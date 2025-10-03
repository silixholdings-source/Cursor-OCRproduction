"""
Pytest configuration and fixtures for FastAPI backend tests
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
from pathlib import Path
import uuid
from datetime import datetime, date, timedelta
import json

# Set test environment before importing anything else
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENVIRONMENT"] = "test"

from src.main import app
from src.core.database import Base, get_db
from src.models.user import User, UserRole, UserStatus
from src.models.company import Company, CompanyStatus, CompanyTier
from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
from src.models.invoice_line import InvoiceLine
from src.core.config import settings
from passlib.context import CryptContext

# Test database URL - use PostgreSQL for testing to support UUID
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/ai_erp_test"

# Create test engine with proper test configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False  # Disable SQL echo in tests
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_company(db_session):
    """Create a test company."""
    company = Company(
        id=uuid.uuid4(),
        name="Test Company",
        email="test@company.com",
        status=CompanyStatus.ACTIVE,
        max_users=10,
        max_invoices_per_month=1000
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture
def test_user(db_session, test_company):
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=pwd_context.hash("testpassword123"),
        first_name="Test",
        last_name="User",
        company_id=test_company.id,
        role=UserRole.ADMIN,
        is_active=True,
        is_email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_invoice_data():
    """Sample invoice data for testing."""
    return {
        "invoice_number": "INV-001",
        "supplier_name": "Test Supplier Inc",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "total_amount": 1500.00,
        "currency": "USD",
        "tax_amount": 120.00,
        "tax_rate": 0.08,
        "subtotal": 1380.00,
        "total_with_tax": 1500.00,
        "line_items": [
            {
                "description": "Software License",
                "quantity": 1,
                "unit_price": 1000.00,
                "total": 1000.00,
                "gl_account": "6000"
            },
            {
                "description": "Implementation Services",
                "quantity": 10,
                "unit_price": 38.00,
                "total": 380.00,
                "gl_account": "6500"
            }
        ]
    }

@pytest.fixture
def sample_invoice(db_session, test_company, test_user, sample_invoice_data):
    """Create a sample invoice in the database."""
    invoice = Invoice(
        id=uuid.uuid4(),
        invoice_number=sample_invoice_data["invoice_number"],
        supplier_name=sample_invoice_data["supplier_name"],
        invoice_date=date.fromisoformat(sample_invoice_data["invoice_date"]),
        due_date=date.fromisoformat(sample_invoice_data["due_date"]),
        total_amount=sample_invoice_data["total_amount"],
        currency=sample_invoice_data["currency"],
        tax_amount=sample_invoice_data["tax_amount"],
        tax_rate=sample_invoice_data["tax_rate"],
        subtotal=sample_invoice_data["subtotal"],
        total_with_tax=sample_invoice_data["total_with_tax"],
        status=InvoiceStatus.DRAFT,
        company_id=test_company.id,
        created_by_id=test_user.id,
        ocr_data=sample_invoice_data
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    
    # Add line items
    for item_data in sample_invoice_data["line_items"]:
        line_item = InvoiceLine(
            id=uuid.uuid4(),
            invoice_id=invoice.id,
            description=item_data["description"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            total=item_data["total"],
            gl_account=item_data["gl_account"]
        )
        db_session.add(line_item)
    
    db_session.commit()
    return invoice

@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    # Create a temporary PDF file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(b"Mock PDF content for testing")
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    os.unlink(temp_file.name)

@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing."""
    # Create a temporary image file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(b"Mock image content for testing")
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    os.unlink(temp_file.name)

@pytest.fixture
def mock_ocr_response():
    """Mock OCR response data."""
    return {
        "supplier_name": "Test Supplier Inc",
        "invoice_number": "INV-001",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "total_amount": 1500.00,
        "currency": "USD",
        "tax_amount": 120.00,
        "tax_rate": 0.08,
        "subtotal": 1380.00,
        "total_with_tax": 1500.00,
        "line_items": [
            {
                "description": "Software License",
                "quantity": 1,
                "unit_price": 1000.00,
                "total": 1000.00,
                "gl_account": "6000"
            },
            {
                "description": "Implementation Services",
                "quantity": 10,
                "unit_price": 38.00,
                "total": 380.00,
                "gl_account": "6500"
            }
        ],
        "confidence_scores": {
            "supplier_name": 0.95,
            "invoice_number": 0.98,
            "total_amount": 0.99,
            "line_items": 0.92,
            "overall_confidence": 0.96
        },
        "processing_metadata": {
            "provider": "mock",
            "processing_time_ms": 150,
            "file_size_bytes": 1024,
            "extraction_method": "mock_testing"
        }
    }

@pytest.fixture
def multiple_invoices(db_session, test_company, test_user):
    """Create multiple test invoices."""
    invoices = []
    for i in range(5):
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number=f"INV-{i+1:03d}",
            supplier_name=f"Supplier {i+1}",
            invoice_date=date.today() - timedelta(days=i*7),
            total_amount=1000.00 + (i * 100),
            currency="USD",
            status=InvoiceStatus.DRAFT if i % 2 == 0 else InvoiceStatus.APPROVED,
            company_id=test_company.id,
            created_by_id=test_user.id,
            ocr_data={"test": f"data_{i}"}
        )
        db_session.add(invoice)
        invoices.append(invoice)
    
    db_session.commit()
    for invoice in invoices:
        db_session.refresh(invoice)
    
    return invoices

@pytest.fixture
def mock_ocr_service():
    """Mock OCR service for testing."""
    class MockOCRService:
        async def extract_invoice(self, file_path: str, company_id: str):
            return {
                "supplier_name": "Mock Supplier",
                "invoice_number": "MOCK-001",
                "invoice_date": "2024-01-15",
                "total_amount": 1000.00,
                "currency": "USD",
                "line_items": [],
                "confidence_scores": {"overall_confidence": 0.95},
                "processing_metadata": {"provider": "mock"}
            }
    
    return MockOCRService()

# Test data for different invoice types
@pytest.fixture
def credit_memo_data():
    """Sample credit memo data."""
    return {
        "invoice_number": "CM-001",
        "supplier_name": "Test Supplier Inc",
        "invoice_date": "2024-01-15",
        "total_amount": -500.00,  # Negative amount for credit memo
        "currency": "USD",
        "line_items": [
            {
                "description": "Returned Item",
                "quantity": 1,
                "unit_price": -500.00,
                "total": -500.00
            }
        ]
    }

@pytest.fixture
def large_invoice_data():
    """Sample large invoice with many line items."""
    line_items = []
    for i in range(20):
        line_items.append({
            "description": f"Item {i+1}",
            "quantity": 1,
            "unit_price": 50.00,
            "total": 50.00,
            "gl_account": f"600{i%10}"
        })
    
    return {
        "invoice_number": "INV-LARGE-001",
        "supplier_name": "Large Supplier Inc",
        "invoice_date": "2024-01-15",
        "total_amount": 1000.00,
        "currency": "USD",
        "line_items": line_items
    }
