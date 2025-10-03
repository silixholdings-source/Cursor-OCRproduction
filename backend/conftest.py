"""
Pytest configuration and fixtures for AI ERP SaaS application
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# from src.main import app  # Avoid importing main app to prevent model conflicts
from src.core.database import Base, get_db
from src.core.config import settings
from tests.utils.factories import UserFactory, CompanyFactory

# Test database configuration - Use PostgreSQL for testing to support UUID
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/ai_erp_test"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with a fresh database."""
    from fastapi import FastAPI
    
    # Create a minimal test app to avoid model conflicts
    test_app = FastAPI(title="Test App")
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app) as test_client:
        yield test_client
    test_app.dependency_overrides.clear()

@pytest.fixture
def test_company(db_session: Session):
    """Create a test company for testing."""
    from src.models.company import Company
    company = CompanyFactory()
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture
def test_user(db_session: Session, test_company):
    """Create a test user for testing."""
    from src.models.user import User
    user = UserFactory(company_id=test_company.id)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session: Session, test_company):
    """Create an admin user for testing."""
    from src.models.user import User, UserRole, UserStatus
    user = UserFactory(
        company_id=test_company.id,
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def mock_ocr_service():
    """Mock OCR service for testing."""
    with patch("src.services.ocr.OCRService") as mock:
        mock_instance = Mock()
        mock_instance.extract_invoice.return_value = {
            "supplier_name": "Test Supplier",
            "invoice_number": "INV-001",
            "total_amount": 100.00,
            "currency": "USD",
            "invoice_date": "2024-01-01",
            "line_items": [
                {
                    "description": "Test Item",
                    "quantity": 1,
                    "unit_price": 100.00,
                    "total": 100.00
                }
            ]
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_erp_adapter():
    """Mock ERP adapter for testing."""
    with patch("src.services.erp.ERPAdapter") as mock:
        mock_instance = Mock()
        mock_instance.post_invoice.return_value = {
            "status": "success",
            "erp_doc_id": "ERP-001",
            "method": "POST"
        }
        mock_instance.health_check.return_value = {"status": "healthy"}
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_stripe_service():
    """Mock Stripe service for testing."""
    with patch("src.services.billing.StripeService") as mock:
        mock_instance = Mock()
        mock_instance.create_customer.return_value = {"id": "cus_test123"}
        mock_instance.create_subscription.return_value = {"id": "sub_test123"}
        mock_instance.create_webhook.return_value = {"id": "evt_test123"}
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_redis():
    """Mock Redis for testing."""
    with patch("src.core.cache.redis") as mock:
        mock_instance = Mock()
        mock_instance.get.return_value = None
        mock_instance.set.return_value = True
        mock_instance.delete.return_value = True
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_celery():
    """Mock Celery for testing."""
    with patch("src.core.celery.celery_app") as mock:
        mock_instance = Mock()
        mock_instance.send_task.return_value = Mock(id="task_123")
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def golden_invoice_data():
    """Golden invoice data for OCR regression testing."""
    return {
        "invoice_number": "GOLDEN-001",
        "supplier_name": "Golden Supplier Corp",
        "total_amount": 1500.00,
        "currency": "USD",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "line_items": [
            {
                "description": "Premium Software License",
                "quantity": 1,
                "unit_price": 1000.00,
                "total": 1000.00,
                "gl_account": "6000"
            },
            {
                "description": "Implementation Services",
                "quantity": 10,
                "unit_price": 50.00,
                "total": 500.00,
                "gl_account": "6500"
            }
        ],
        "tax_amount": 120.00,
        "tax_rate": 0.08,
        "subtotal": 1500.00,
        "total_with_tax": 1620.00
    }

@pytest.fixture
def mock_telemetry():
    """Mock telemetry for testing."""
    with patch("src.core.telemetry.setup_telemetry") as mock:
        yield mock

@pytest.fixture
def mock_sentry():
    """Mock Sentry for testing."""
    with patch("sentry_sdk.init") as mock:
        yield mock
