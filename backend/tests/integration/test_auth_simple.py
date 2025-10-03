import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import core database first
from src.core.database import Base

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

def test_company_creation(db_session):
    """Test that we can create a company without conflicts"""
    # Import models inside the test to avoid circular imports
    from src.models.company import Company, CompanyStatus, CompanyTier
    
    company = Company(
        name="Test Company Inc",
        email="admin@testcompany.com",
        status=CompanyStatus.ACTIVE,
        tier=CompanyTier.PROFESSIONAL
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    assert company.id is not None
    assert company.name == "Test Company Inc"
    assert company.email == "admin@testcompany.com"
    assert company.status == CompanyStatus.ACTIVE
    assert company.tier == CompanyTier.PROFESSIONAL

def test_user_creation(db_session):
    """Test that we can create a user without conflicts"""
    # Import models inside the test to avoid circular imports
    from src.models.company import Company, CompanyStatus, CompanyTier
    from src.models.user import User, UserRole, UserStatus
    from src.core.auth import AuthManager
    
    # First create a company
    company = Company(
        name="Test Company Inc",
        email="admin@testcompany.com",
        status=CompanyStatus.ACTIVE,
        tier=CompanyTier.PROFESSIONAL
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    # Then create a user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=AuthManager.get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        company_id=company.id,
        role=UserRole.OWNER,
        status=UserStatus.ACTIVE,
        is_email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.company_id == company.id

def test_company_query(db_session):
    """Test that we can query companies without conflicts"""
    # Import models inside the test to avoid circular imports
    from src.models.company import Company, CompanyStatus, CompanyTier
    
    # Create a company
    company = Company(
        name="Query Test Company",
        email="query@testcompany.com",
        status=CompanyStatus.ACTIVE,
        tier=CompanyTier.PROFESSIONAL
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    # Query the company
    found_company = db_session.query(Company).filter(Company.email == "query@testcompany.com").first()
    assert found_company is not None
    assert found_company.name == "Query Test Company"
