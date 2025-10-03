import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models first before importing the app
from src.models.user import User, UserRole, UserStatus
from src.models.company import Company, CompanyStatus, CompanyTier
from src.core.auth import AuthManager
from src.core.database import Base, get_db

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """Create test client"""
    # Import app after models are registered
    from src.main import app
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def db_session():
    """Create database session and tables"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_company(db_session):
    """Create test company"""
    company = Company(
        name="Test Company Inc",
        email="admin@testcompany.com",
        status=CompanyStatus.ACTIVE,
        tier=CompanyTier.PROFESSIONAL  # Updated to match new enum values
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture
def test_user(db_session, test_company):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=AuthManager.get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        company_id=test_company.id,
        role=UserRole.OWNER,
        status=UserStatus.ACTIVE,
        is_email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_company_registration(self, client, db_session):
        """Test company and user registration"""
        register_data = {
            "company_name": "New Company Inc",
            "company_email": "admin@newcompany.com",
            "industry": "Technology",
            "company_size": "11-50",
            "owner_email": "owner@newcompany.com",
            "owner_username": "owner",
            "owner_password": "securepassword123",
            "owner_first_name": "Owner",
            "owner_last_name": "User"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "company" in data
        assert "user" in data
        assert data["company"]["name"] == "New Company Inc"
        assert data["user"]["email"] == "owner@newcompany.com"
    
    def test_user_login(self, client, test_user):
        """Test user login"""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "user" in data
        assert "company" in data
        assert data["user"]["email"] == "test@example.com"
    
    def test_invalid_login(self, client):
        """Test invalid login credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_refresh_token(self, client, test_user):
        """Test token refresh"""
        # First login to get tokens
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token to get new access token
        refresh_data = {
            "refresh_token": refresh_token
        }
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
    
    def test_forgot_password(self, client):
        """Test forgot password functionality"""
        forgot_data = {
            "email": "test@example.com"
        }
        
        response = client.post("/api/v1/auth/forgot-password", json=forgot_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
    
    def test_change_password(self, client, test_user):
        """Test password change"""
        # First login to get access token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Change password
        change_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        
        # Verify new password works
        new_login_data = {
            "email": "test@example.com",
            "password": "newpassword123"
        }
        
        new_login_response = client.post("/api/v1/auth/login", json=new_login_data)
        assert new_login_response.status_code == 200
    
    def test_update_profile(self, client, test_user):
        """Test profile update"""
        # First login to get access token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Update profile
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+1234567890"
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.put("/api/v1/auth/profile", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "user" in data
        assert data["user"]["first_name"] == "Updated"
        assert data["user"]["last_name"] == "Name"
        assert data["user"]["phone"] == "+1234567890"
