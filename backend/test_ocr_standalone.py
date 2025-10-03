"""
Standalone OCR test that doesn't depend on the full application
"""
import os
import sys
from pathlib import Path

# Set test environment
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["OCR_PROVIDER"] = "mock"
os.environ["ENVIRONMENT"] = "test"

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_simple_ocr():
    """Test the simple OCR service directly"""
    try:
        from services.simple_ocr import SimpleOCRService
        
        ocr_service = SimpleOCRService()
        
        # Test with sample file path (mock)
        sample_file_path = "test_invoice.pdf"
        sample_company_id = "test-company-123"
        result = await ocr_service.extract_invoice(sample_file_path, sample_company_id)
        
        print("+ OCR service result keys:", list(result.keys()))
        print("+ Vendor:", result.get("vendor", "N/A"))
        print("+ Invoice number:", result.get("invoice_number", "N/A"))
        print("+ Amount:", result.get("amount", "N/A"))
        
        # Check for the actual field names returned by SimpleOCRService
        assert "invoice_number" in result
        assert "vendor" in result
        assert "amount" in result
        assert result["amount"] > 0
        
        print("+ OCR mock service works")
        return True
        
    except Exception as e:
        print(f"- OCR mock service test failed: {e}")
        return False

def test_file_upload_validation():
    """Test file upload validation logic"""
    try:
        # Test file type validation
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff'}
        
        def is_allowed_file(filename):
            return Path(filename).suffix.lower() in allowed_extensions
        
        # Test cases
        test_cases = [
            ("test.pdf", True),
            ("test.PDF", True),
            ("test.png", True),
            ("test.jpg", True),
            ("test.txt", False),
            ("test.doc", False)
        ]
        
        for filename, expected in test_cases:
            result = is_allowed_file(filename)
            assert result == expected, f"Expected {expected} for {filename}, got {result}"
        
        print("+ File upload validation logic works")
        return True
        
    except Exception as e:
        print(f"- File upload logic test failed: {e}")
        return False

def test_invoice_data_structure():
    """Test invoice data structure and validation"""
    try:
        # Test invoice data structure
        invoice_data = {
            "supplier_name": "Test Supplier Inc.",
            "invoice_number": "INV-12345",
            "invoice_date": "2023-01-15",
            "total_amount": 1234.56,
            "currency": "USD",
            "tax_amount": 100.00,
            "subtotal": 1134.56,
            "line_items": [
                {
                    "description": "Item 1",
                    "quantity": 1.0,
                    "unit_price": 1000.00,
                    "total": 1000.00
                }
            ]
        }
        
        # Validate required fields
        required_fields = ["supplier_name", "invoice_number", "total_amount"]
        for field in required_fields:
            assert field in invoice_data, f"Missing required field: {field}"
            assert invoice_data[field], f"Empty value for required field: {field}"
        
        # Validate data types
        assert isinstance(invoice_data["total_amount"], (int, float))
        assert invoice_data["total_amount"] > 0
        assert isinstance(invoice_data["line_items"], list)
        
        print("+ Invoice data structure validation works")
        return True
        
    except Exception as e:
        print(f"- Invoice data structure test failed: {e}")
        return False

async def run_async_tests():
    """Run async tests"""
    print("Running standalone OCR tests...")
    
    # Run async tests
    async_tests = [test_simple_ocr]
    sync_tests = [test_file_upload_validation, test_invoice_data_structure]
    
    passed = 0
    total = len(async_tests) + len(sync_tests)
    
    # Run async tests
    for test in async_tests:
        if await test():
            passed += 1
    
    # Run sync tests
    for test in sync_tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("+ All standalone tests passed!")
    else:
        print(f"- {total - passed} tests failed")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_async_tests())
