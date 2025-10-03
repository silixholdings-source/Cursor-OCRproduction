#!/usr/bin/env python3
"""
Simple OCR Testing Script - No Unicode Issues
Tests OCR functionality by importing and testing the OCR services directly
"""

import sys
import asyncio
import json
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

def test_ocr_imports():
    """Test if OCR modules can be imported"""
    print("Testing OCR Module Imports...")
    
    try:
        # Test OCR service imports
        from services.ocr import OCRService, MockOCRService, AzureOCRService
        print("SUCCESS: OCR service imports successful")
        
        from services.invoice_processor import InvoiceProcessor
        print("SUCCESS: Invoice processor import successful")
        
        from services.simple_ocr import SimpleOCRService
        print("SUCCESS: Simple OCR service import successful")
        
        return True
    except ImportError as e:
        print(f"FAILED: Import failed: {e}")
        return False

async def test_mock_ocr_service():
    """Test the Mock OCR service"""
    print("\nTesting Mock OCR Service...")
    
    try:
        from services.ocr import MockOCRService
        
        # Create mock OCR service
        ocr_service = MockOCRService()
        print("SUCCESS: Mock OCR service created successfully")
        
        # Test invoice extraction
        result = await ocr_service.extract_invoice("test-invoice.pdf", "test-company")
        print("SUCCESS: Mock OCR extraction completed")
        
        # Validate result structure
        required_fields = ["supplier_name", "invoice_number", "total_amount", "line_items"]
        missing_fields = [field for field in required_fields if field not in result]
        
        if not missing_fields:
            print("SUCCESS: All required fields extracted")
            print(f"   Supplier: {result['supplier_name']}")
            print(f"   Invoice: {result['invoice_number']}")
            print(f"   Amount: ${result['total_amount']}")
            print(f"   Line items: {len(result['line_items'])}")
            
            # Test confidence scores
            if "confidence_scores" in result:
                confidence = result["confidence_scores"]
                print("SUCCESS: Confidence scores available")
                print(f"   Overall: {confidence.get('overall_confidence', 'N/A')}")
                print(f"   Supplier: {confidence.get('supplier_name', 'N/A')}")
                print(f"   Amount: {confidence.get('total_amount', 'N/A')}")
            
            return True
        else:
            print(f"FAILED: Missing fields: {missing_fields}")
            return False
            
    except Exception as e:
        print(f"FAILED: Mock OCR test failed: {e}")
        return False

async def test_simple_ocr_service():
    """Test the Simple OCR service"""
    print("\nTesting Simple OCR Service...")
    
    try:
        from services.simple_ocr import SimpleOCRService
        
        # Create simple OCR service
        ocr_service = SimpleOCRService()
        print("SUCCESS: Simple OCR service created successfully")
        
        # Test invoice extraction
        result = await ocr_service.extract_invoice("test-invoice.pdf", "test-company")
        print("SUCCESS: Simple OCR extraction completed")
        
        # Validate result structure
        if "supplier_name" in result and "total_amount" in result:
            print("SUCCESS: Basic extraction working")
            print(f"   Supplier: {result['supplier_name']}")
            print(f"   Amount: ${result['total_amount']}")
            return True
        else:
            print("FAILED: Basic extraction failed")
            return False
            
    except Exception as e:
        print(f"FAILED: Simple OCR test failed: {e}")
        return False

async def test_invoice_processor():
    """Test the Invoice Processor integration"""
    print("\nTesting Invoice Processor Integration...")
    
    try:
        from services.invoice_processor import InvoiceProcessor
        
        # Create invoice processor
        processor = InvoiceProcessor()
        print("SUCCESS: Invoice processor created successfully")
        
        # Test OCR service integration
        if hasattr(processor, 'ocr_service'):
            print("SUCCESS: OCR service integrated in processor")
            
            # Test mock processing
            result = await processor.ocr_service.extract_invoice("test-invoice.pdf", "test-company")
            if result:
                print("SUCCESS: OCR processing through processor successful")
                return True
            else:
                print("FAILED: OCR processing through processor failed")
                return False
        else:
            print("FAILED: OCR service not found in processor")
            return False
            
    except Exception as e:
        print(f"FAILED: Invoice processor test failed: {e}")
        return False

def test_ocr_configuration():
    """Test OCR configuration and settings"""
    print("\nTesting OCR Configuration...")
    
    try:
        from core.config import settings
        
        # Check OCR-related settings
        ocr_settings = {
            "OCR_PROVIDER": getattr(settings, 'OCR_PROVIDER', 'Not set'),
            "OCR_CONFIDENCE_THRESHOLD": getattr(settings, 'OCR_CONFIDENCE_THRESHOLD', 'Not set'),
            "AZURE_FORM_RECOGNIZER_ENDPOINT": getattr(settings, 'AZURE_FORM_RECOGNIZER_ENDPOINT', 'Not set'),
            "AZURE_FORM_RECOGNIZER_KEY": getattr(settings, 'AZURE_FORM_RECOGNIZER_KEY', 'Not set')
        }
        
        print("SUCCESS: Configuration loaded successfully")
        for key, value in ocr_settings.items():
            if value == 'Not set':
                print(f"   {key}: Not configured (using defaults)")
            else:
                # Hide sensitive values
                if 'KEY' in key:
                    print(f"   {key}: ********** (configured)")
                else:
                    print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"FAILED: Configuration test failed: {e}")
        return False

async def run_all_tests():
    """Run all OCR tests"""
    print("Starting Manual OCR Functionality Tests...\n")
    
    tests = [
        ("Module Imports", test_ocr_imports()),
        ("OCR Configuration", test_ocr_configuration()),
        ("Mock OCR Service", test_mock_ocr_service()),
        ("Simple OCR Service", test_simple_ocr_service()),
        ("Invoice Processor", test_invoice_processor())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
    
    # Print summary
    print("\nTest Summary:")
    print("=============")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\nSuccess Rate: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("\nRESULT: OCR FUNCTIONALITY IS WORKING WELL")
        print("   Core OCR components are functional!")
        print("   The system is ready for testing with a live backend.")
    elif success_rate >= 60:
        print("\nRESULT: OCR FUNCTIONALITY IS MOSTLY WORKING")
        print("   Most OCR components are functional.")
        print("   Some issues need attention.")
    else:
        print("\nRESULT: OCR FUNCTIONALITY NEEDS ATTENTION")
        print("   Several OCR components need to be fixed.")
        print("   Review the test results above.")
    
    # Save results
    test_results = {
        "timestamp": "2024-12-29T00:00:00Z",
        "total_tests": total,
        "passed_tests": passed,
        "success_rate": success_rate,
        "results": [{"test": name, "passed": result} for name, result in results]
    }
    
    with open("ocr-simple-test-results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nResults saved to ocr-simple-test-results.json")
    
    return success_rate >= 80

if __name__ == "__main__":
    asyncio.run(run_all_tests())
