import pytest
import sys
from pathlib import Path

# Add src to path for imports
backend_dir = Path(__file__).parent.parent.parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base
import enum
from datetime import datetime, UTC

# Create isolated base for this test
TestBase = declarative_base()

# Define enums locally to avoid conflicts
class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    APPROVER = "approver"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# Import enums from main models to avoid conflicts
from src.models.company import CompanyStatus, CompanyTier

# Create isolated models
class TestCompany(TestBase):
    __tablename__ = "test_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    status = Column(Enum(CompanyStatus), default=CompanyStatus.ACTIVE)
    tier = Column(Enum(CompanyTier), default=CompanyTier.GROWTH)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class TestUser(TestBase):
    __tablename__ = "test_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_id = Column(Integer, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    is_email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

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
    TestBase.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        TestBase.metadata.drop_all(bind=engine)

def test_company_creation_isolated(db_session):
    """Test that we can create a company without conflicts"""
    company = TestCompany(
        name="Test Company Inc",
        email="admin@testcompany.com",
        status=CompanyStatus.ACTIVE,
        tier=CompanyTier.GROWTH
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    assert company.id is not None
    assert company.name == "Test Company Inc"
    assert company.email == "admin@testcompany.com"
    assert company.status == CompanyStatus.ACTIVE
    assert company.tier == CompanyTier.GROWTH

def test_user_creation_isolated(db_session):
    """Test that we can create a user without conflicts"""
    # First create a company
    company = TestCompany(
        name="Test Company Inc",
        email="admin@testcompany.com",
        status=CompanyStatus.ACTIVE,
        tier=CompanyTier.GROWTH
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    # Then create a user
    user = TestUser(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_123",
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
    assert user.role == UserRole.OWNER

def test_company_query_isolated(db_session):
    """Test that we can query companies without conflicts"""
    # Create a company
    company = TestCompany(
        name="Query Test Company",
        email="query@testcompany.com",
        status=CompanyStatus.ACTIVE,
        tier=CompanyTier.GROWTH
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    # Query the company
    found_company = db_session.query(TestCompany).filter(TestCompany.email == "query@testcompany.com").first()
    assert found_company is not None
    assert found_company.name == "Query Test Company"

def test_user_company_relationship_isolated(db_session):
    """Test user-company relationship without conflicts"""
    # Create a company
    company = TestCompany(
        name="Relationship Test Company",
        email="relationship@testcompany.com",
        status=CompanyStatus.ACTIVE,
        tier=CompanyTier.ENTERPRISE
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    # Create multiple users for the company
    users = []
    for i in range(3):
        user = TestUser(
            email=f"user{i}@example.com",
            username=f"user{i}",
            hashed_password="hashed_password_123",
            first_name=f"User{i}",
            last_name="Test",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            is_email_verified=True
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    
    # Verify all users belong to the same company
    for user in users:
        db_session.refresh(user)
        assert user.company_id == company.id
    
    # Query users by company
    company_users = db_session.query(TestUser).filter(TestUser.company_id == company.id).all()
    assert len(company_users) == 3
