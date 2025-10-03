import pytest
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base

# Create a separate base for testing
TestBase = declarative_base()

# Create a simple test model
class TestCompany(TestBase):
    __tablename__ = "test_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)

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

def test_simple_company_creation(db_session):
    """Test that we can create a simple company without conflicts"""
    company = TestCompany(
        name="Test Company Inc",
        email="admin@testcompany.com"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    assert company.id is not None
    assert company.name == "Test Company Inc"
    assert company.email == "admin@testcompany.com"

def test_simple_company_query(db_session):
    """Test that we can query companies without conflicts"""
    # Create a company
    company = TestCompany(
        name="Query Test Company",
        email="query@testcompany.com"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    
    # Query the company
    found_company = db_session.query(TestCompany).filter(TestCompany.email == "query@testcompany.com").first()
    assert found_company is not None
    assert found_company.name == "Query Test Company"
