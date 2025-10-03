"""
Test utilities and helper functions
"""
import uuid
import tempfile
import os
from datetime import date, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from src.models.user import User, UserRole, UserStatus
from src.models.company import Company, CompanyStatus, CompanyTier
from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
from src.models.invoice_line import InvoiceLine

def create_test_company(db_session: Session, **kwargs) -> Company:
    """Create a test company with default values."""
    defaults = {
        "id": uuid.uuid4(),
        "name": "Test Company",
        "email": "test@company.com",
        "status": CompanyStatus.ACTIVE,
        "max_users": 10,
        "max_invoices_per_month": 1000
    }
    defaults.update(kwargs)
    
    company = Company(**defaults)
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

def create_test_user(db_session: Session, company_id: uuid.UUID, **kwargs) -> User:
    """Create a test user with default values."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    defaults = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "hashed_password": pwd_context.hash("testpassword123"),
        "first_name": "Test",
        "last_name": "User",
        "company_id": company_id,
        "role": UserRole.ADMIN,
        "is_active": True,
        "is_email_verified": True
    }
    defaults.update(kwargs)
    
    user = User(**defaults)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def create_test_invoice(db_session: Session, company_id: uuid.UUID, created_by_id: uuid.UUID, **kwargs) -> Invoice:
    """Create a test invoice with default values."""
    defaults = {
        "id": uuid.uuid4(),
        "invoice_number": "TEST-001",
        "supplier_name": "Test Supplier",
        "invoice_date": date.today(),
        "total_amount": 1000.00,
        "currency": "USD",
        "status": InvoiceStatus.DRAFT,
        "company_id": company_id,
        "created_by_id": created_by_id,
        "ocr_data": {}
    }
    defaults.update(kwargs)
    
    invoice = Invoice(**defaults)
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice

def create_test_invoice_with_lines(db_session: Session, company_id: uuid.UUID, created_by_id: uuid.UUID, **kwargs) -> Invoice:
    """Create a test invoice with line items."""
    invoice = create_test_invoice(db_session, company_id, created_by_id, **kwargs)
    
    # Add line items
    line_items_data = [
        {
            "id": uuid.uuid4(),
            "invoice_id": invoice.id,
            "description": "Test Item 1",
            "quantity": 1,
            "unit_price": 500.00,
            "total": 500.00,
            "gl_account": "6000"
        },
        {
            "id": uuid.uuid4(),
            "invoice_id": invoice.id,
            "description": "Test Item 2",
            "quantity": 2,
            "unit_price": 250.00,
            "total": 500.00,
            "gl_account": "6500"
        }
    ]
    
    for item_data in line_items_data:
        line_item = InvoiceLine(**item_data)
        db_session.add(line_item)
    
    db_session.commit()
    return invoice

def create_test_file(content: bytes = None, extension: str = ".pdf") -> str:
    """Create a temporary test file."""
    if content is None:
        content = b"Mock file content for testing"
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
    temp_file.write(content)
    temp_file.close()
    return temp_file.name

def cleanup_test_file(file_path: str):
    """Clean up a test file."""
    if os.path.exists(file_path):
        os.unlink(file_path)

def create_mock_ocr_response(**kwargs) -> Dict[str, Any]:
    """Create a mock OCR response with default values."""
    defaults = {
        "supplier_name": "Mock Supplier Inc",
        "invoice_number": "MOCK-001",
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
            "invoice_date": 0.92,
            "due_date": 0.90,
            "total_amount": 0.99,
            "line_items": 0.94,
            "overall_confidence": 0.95
        },
        "processing_metadata": {
            "provider": "mock",
            "processing_time_ms": 150,
            "file_size_bytes": 1024,
            "extraction_method": "mock_testing",
            "timestamp": "2024-01-15T10:00:00Z"
        }
    }
    defaults.update(kwargs)
    return defaults

def create_multiple_test_invoices(db_session: Session, company_id: uuid.UUID, created_by_id: uuid.UUID, count: int = 5) -> List[Invoice]:
    """Create multiple test invoices."""
    invoices = []
    for i in range(count):
        invoice = create_test_invoice(
            db_session,
            company_id,
            created_by_id,
            invoice_number=f"TEST-{i+1:03d}",
            supplier_name=f"Supplier {i+1}",
            total_amount=1000.00 + (i * 100),
            status=InvoiceStatus.DRAFT if i % 2 == 0 else InvoiceStatus.APPROVED
        )
        invoices.append(invoice)
    return invoices

def assert_invoice_data(invoice_data: Dict[str, Any], expected_data: Dict[str, Any]):
    """Assert that invoice data matches expected values."""
    for key, expected_value in expected_data.items():
        assert key in invoice_data, f"Missing key: {key}"
        assert invoice_data[key] == expected_value, f"Mismatch for {key}: expected {expected_value}, got {invoice_data[key]}"

def assert_line_items_data(line_items: List[Dict[str, Any]], expected_items: List[Dict[str, Any]]):
    """Assert that line items data matches expected values."""
    assert len(line_items) == len(expected_items), f"Expected {len(expected_items)} line items, got {len(line_items)}"
    
    for i, (actual_item, expected_item) in enumerate(zip(line_items, expected_items)):
        for key, expected_value in expected_item.items():
            assert key in actual_item, f"Missing key in line item {i}: {key}"
            assert actual_item[key] == expected_value, f"Mismatch in line item {i} for {key}: expected {expected_value}, got {actual_item[key]}"

def create_test_environment():
    """Create a test environment with all necessary services."""
    # This would typically start Docker containers or test services
    # For now, just return a mock environment
    return {
        "database_url": "sqlite:///./test.db",
        "redis_url": "redis://localhost:6379",
        "ocr_service_url": "http://localhost:8001",
        "secret_key": "test_secret_key"
    }

def cleanup_test_environment():
    """Clean up test environment."""
    # This would typically stop Docker containers or clean up test services
    pass

class MockOCRService:
    """Mock OCR service for testing."""
    
    def __init__(self, response_data: Dict[str, Any] = None):
        self.response_data = response_data or create_mock_ocr_response()
    
    async def extract_invoice(self, file_path: str, company_id: str) -> Dict[str, Any]:
        """Mock invoice extraction."""
        return self.response_data.copy()
    
    def set_response(self, response_data: Dict[str, Any]):
        """Set the response data for the mock."""
        self.response_data = response_data

class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self):
        self.data = {}
    
    def get(self, key: str):
        """Get data by key."""
        return self.data.get(key)
    
    def set(self, key: str, value: Any):
        """Set data by key."""
        self.data[key] = value
    
    def delete(self, key: str):
        """Delete data by key."""
        if key in self.data:
            del self.data[key]
    
    def clear(self):
        """Clear all data."""
        self.data.clear()

def generate_test_data(size: int = 100) -> List[Dict[str, Any]]:
    """Generate test data for performance testing."""
    data = []
    for i in range(size):
        data.append({
            "id": str(uuid.uuid4()),
            "invoice_number": f"PERF-{i:03d}",
            "supplier_name": f"Supplier {i}",
            "total_amount": 1000.00 + i,
            "created_at": (date.today() - timedelta(days=i)).isoformat()
        })
    return data
