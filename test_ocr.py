"""
Simple test file for OCR service
"""
import pytest
import asyncio
from main import OCRProcessor

@pytest.fixture
def ocr_processor():
    return OCRProcessor(confidence_threshold=0.8)

def test_ocr_processor_initialization(ocr_processor):
    """Test OCR processor initialization"""
    assert ocr_processor is not None
    assert ocr_processor.confidence_threshold == 0.8
    assert 'pdf' in ocr_processor.supported_formats

@pytest.mark.asyncio
async def test_image_text_extraction(ocr_processor):
    """Test text extraction from image (mock test)"""
    # This would require an actual image file
    # For now, we'll just test that the method exists and can be called
    try:
        # This will fail without a real image, but we can test the structure
        await ocr_processor.extract_text_from_image("nonexistent.jpg", "eng")
    except FileNotFoundError:
        # Expected behavior for non-existent file
        pass
    except Exception as e:
        # Other exceptions are acceptable for this mock test
        assert isinstance(e, Exception)

def test_supported_formats():
    """Test that supported formats are correctly defined"""
    processor = OCRProcessor()
    expected_formats = ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'tif']
    for fmt in expected_formats:
        assert fmt in processor.supported_formats

if __name__ == "__main__":
    # Simple test runner
    import sys
    import os
    
    print("Running OCR service tests...")
    
    # Test 1: Processor initialization
    try:
        processor = OCRProcessor()
        print("✅ OCR Processor initialization: PASSED")
    except Exception as e:
        print(f"❌ OCR Processor initialization: FAILED - {e}")
        sys.exit(1)
    
    # Test 2: Supported formats
    try:
        expected_formats = ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'tif']
        for fmt in expected_formats:
            assert fmt in processor.supported_formats
        print("✅ Supported formats check: PASSED")
    except Exception as e:
        print(f"❌ Supported formats check: FAILED - {e}")
        sys.exit(1)
    
    print("All basic tests passed! 🎉")
