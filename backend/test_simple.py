"""
Simple test to verify basic functionality without full app startup
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Set test environment before importing anything else
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["OCR_PROVIDER"] = "mock"
os.environ["ENVIRONMENT"] = "test"

def test_basic_imports():
    """Test that we can import the main modules without errors"""
    try:
        from src.core.config import settings
        from src.models.user import User, UserRole, UserStatus
        from src.models.company import Company, CompanyStatus, CompanyTier
        from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
        print("+ All imports successful")
        assert True
    except Exception as e:
        print(f"- Import failed: {e}")
        assert False, f"Import failed: {e}"

def test_database_models():
    """Test that database models can be created"""
    try:
        from src.core.database import Base
        from src.models.user import User, UserRole, UserStatus
        from src.models.company import Company, CompanyStatus, CompanyTier
        from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
        
        # Test that we can create model instances
        user = User(
            id="test-id",
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            first_name="Test",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        
        company = Company(
            id="test-company-id",
            name="Test Company",
            email="test@company.com",
            status=CompanyStatus.ACTIVE,
            tier=CompanyTier.ENTERPRISE
        )
        
        invoice = Invoice(
            id="test-invoice-id",
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=100.0,
            company_id="test-company-id",
            created_by_id="test-id",
            status=InvoiceStatus.PENDING_APPROVAL
        )
        
        print("+ Database models created successfully")
        assert user.email == "test@example.com"
        assert company.name == "Test Company"
        assert invoice.invoice_number == "INV-001"
        
    except Exception as e:
        print(f"- Model creation failed: {e}")
        assert False, f"Model creation failed: {e}"

def test_file_upload_logic():
    """Test file upload validation logic"""
    try:
        from src.core.config import settings
        
        # Test file type validation
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff'}
        
        def is_allowed_file(filename):
            return Path(filename).suffix.lower() in allowed_extensions
        
        # Test cases
        assert is_allowed_file("test.pdf") == True
        assert is_allowed_file("test.PDF") == True
        assert is_allowed_file("test.png") == True
        assert is_allowed_file("test.jpg") == True
        assert is_allowed_file("test.txt") == False
        assert is_allowed_file("test.doc") == False
        
        print("+ File upload validation logic works")
        assert True
        
    except Exception as e:
        print(f"- File upload logic test failed: {e}")
        assert False, f"File upload logic test failed: {e}"

def test_ocr_mock_service():
    """Test OCR mock service functionality"""
    try:
        # Import directly to avoid __init__.py issues
        import sys
        sys.path.append('src')
        from services.simple_ocr import MockOCRService
        
        ocr_service = MockOCRService()
        
        # Test with sample text
        sample_text = "Invoice from Test Supplier for $123.45"
        result = ocr_service.extract_invoice_from_text(sample_text)
        
        assert "supplier_name" in result
        assert "invoice_number" in result
        assert "total_amount" in result
        assert result["total_amount"] > 0
        
        print("+ OCR mock service works")
        assert True
        
    except Exception as e:
        print(f"- OCR mock service test failed: {e}")
        assert False, f"OCR mock service test failed: {e}"

def test_invoice_processing():
    """Test invoice processing logic"""
    try:
        from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
        from datetime import date
        
        # Create test invoice
        invoice = Invoice(
            id="test-invoice-id",
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=date.today(),
            total_amount=100.0,
            subtotal=90.0,
            total_with_tax=100.0,
            company_id="test-company-id",
            created_by_id="test-user-id",
            status=InvoiceStatus.PENDING_APPROVAL,
            type=InvoiceType.INVOICE
        )
        
        # Test invoice properties
        assert invoice.invoice_number == "INV-001"
        assert invoice.supplier_name == "Test Supplier"
        assert invoice.total_amount == 100.0
        assert invoice.status == InvoiceStatus.PENDING_APPROVAL
        
        # Test status transitions
        invoice.status = InvoiceStatus.APPROVED
        assert invoice.status == InvoiceStatus.APPROVED
        
        print("+ Invoice processing logic works")
        assert True
        
    except Exception as e:
        print(f"- Invoice processing test failed: {e}")
        assert False, f"Invoice processing test failed: {e}"

if __name__ == "__main__":
    print("Running simple tests...")
    test_basic_imports()
    test_database_models()
    test_file_upload_logic()
    test_ocr_mock_service()
    test_invoice_processing()
    print("All simple tests passed! +")
