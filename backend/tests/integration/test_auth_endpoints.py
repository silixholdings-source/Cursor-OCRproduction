import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.core.database import Base, get_db
from src.models.user import User, UserRole, UserStatus
from src.models.company import Company, CompanyStatus, CompanyTier
from src.core.auth import AuthManager

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

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create test client"""
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
        tier=CompanyTier.PRO
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
            "company_size": "10-50",
            "owner_email": "owner@newcompany.com",
            "owner_username": "newowner",
            "owner_password": "newpassword123",
            "owner_first_name": "Jane",
            "owner_last_name": "Doe"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "company" in data
        assert "user" in data
        assert "tokens" in data
        
        # Verify company was created
        assert data["company"]["name"] == "New Company Inc"
        assert data["company"]["email"] == "admin@newcompany.com"
        
        # Verify user was created
        assert data["user"]["email"] == "owner@newcompany.com"
        assert data["user"]["first_name"] == "Jane"
        assert data["user"]["last_name"] == "Doe"
        assert data["user"]["role"] == UserRole.OWNER.value
        
        # Verify tokens were generated
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
    
    def test_user_login_success(self, client, test_user):
        """Test successful user login"""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "remember_me": False
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "user" in data
        assert "company" in data
        assert "tokens" in data
        
        # Verify user info
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["first_name"] == "Test"
        assert data["user"]["last_name"] == "User"
        
        # Verify company info
        assert data["company"]["name"] == "Test Company Inc"
        
        # Verify tokens
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
    
    def test_user_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword",
            "remember_me": False
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_user_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "testpassword123",
            "remember_me": False
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_get_current_user(self, client, test_user):
        """Test getting current user info"""
        # First login to get token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "remember_me": False
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        access_token = login_response.json()["tokens"]["access_token"]
        
        # Use token to get current user
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["role"] == UserRole.OWNER.value
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_refresh_token(self, client, test_user):
        """Test token refresh"""
        # First login to get tokens
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "remember_me": False
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        refresh_token = login_response.json()["tokens"]["refresh_token"]
        
        # Use refresh token to get new access token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid token"""
        refresh_data = {"refresh_token": "invalid.refresh.token"}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 401
    
    def test_change_password(self, client, test_user):
        """Test password change"""
        # First login to get token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "remember_me": False
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        access_token = login_response.json()["tokens"]["access_token"]
        
        # Change password
        change_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 200
        
        # Verify password was changed by trying to login with new password
        new_login_data = {
            "email": "test@example.com",
            "password": "newpassword123",
            "remember_me": False
        }
        
        new_login_response = client.post("/api/v1/auth/login", json=new_login_data)
        assert new_login_response.status_code == 200
    
    def test_change_password_wrong_current(self, client, test_user):
        """Test password change with wrong current password"""
        # First login to get token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "remember_me": False
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        access_token = login_response.json()["tokens"]["access_token"]
        
        # Try to change password with wrong current password
        change_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/auth/change-password", json=change_data, headers=headers)
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]
    
    def test_update_profile(self, client, test_user):
        """Test profile update"""
        # First login to get token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "remember_me": False
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        access_token = login_response.json()["tokens"]["access_token"]
        
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
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["phone"] == "+1234567890"
    
    def test_logout(self, client, test_user):
        """Test user logout"""
        # First login to get token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "remember_me": False
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        access_token = login_response.json()["tokens"]["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/api/v1/auth/logout", headers=headers)
        assert response.status_code == 200
        
        # Verify token is no longer valid
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 401












