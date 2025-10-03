"""
Unit tests for OCR service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import tempfile
import os

from src.services.ocr import OCRService, MockOCRService, AzureOCRService
from src.core.config import settings

class TestMockOCRService:
    """Test mock OCR service functionality"""
    
    def test_mock_ocr_service_initialization(self):
        """Test mock OCR service initializes correctly"""
        service = MockOCRService()
        assert service.confidence_threshold == settings.OCR_CONFIDENCE_THRESHOLD
    
    @pytest.mark.asyncio
    async def test_mock_extract_invoice(self):
        """Test mock invoice extraction"""
        service = MockOCRService()
        file_path = "/test/path/invoice.pdf"
        company_id = "test-company-123"
        
        result = await service.extract_invoice(file_path, company_id)
        
        # Check basic structure
        assert "supplier_name" in result
        assert "invoice_number" in result
        assert "total_amount" in result
        assert "line_items" in result
        assert "confidence_scores" in result
        assert "processing_metadata" in result
        
        # Check specific values (MockOCRService generates random IDs)
        assert result["supplier_name"].startswith("Mock Supplier Corp")
        assert result["invoice_number"].startswith("MOCK-")
        assert result["total_amount"] == 1500.00
        assert result["currency"] == "USD"
        
        # Check line items
        assert len(result["line_items"]) == 2
        assert result["line_items"][0]["description"] == "Software License"
        assert result["line_items"][1]["description"] == "Implementation Services"
        
        # Check confidence scores
        assert result["confidence_scores"]["supplier_name"] == 0.95
        assert result["confidence_scores"]["invoice_number"] == 0.98
        assert result["confidence_scores"]["total_amount"] == 0.99
        
        # Check processing metadata
        assert result["processing_metadata"]["provider"] == "mock"
        assert result["processing_metadata"]["extraction_method"] == "mock"
    
    @pytest.mark.asyncio
    async def test_mock_processing_delay(self):
        """Test that mock service simulates processing delay"""
        service = MockOCRService()
        from datetime import UTC
        start_time = datetime.now(UTC)
        
        await service.extract_invoice("/test/path", "company-123")
        
        end_time = datetime.now(UTC)
        processing_time = (end_time - start_time).total_seconds()
        
        # Should have some delay (at least 0.05 seconds)
        assert processing_time >= 0.05

class TestAzureOCRService:
    """Test Azure OCR service functionality"""
    
    def test_azure_ocr_service_initialization_with_credentials(self):
        """Test Azure OCR service initializes with valid credentials"""
        with patch('src.services.ocr.settings') as mock_settings:
            mock_settings.AZURE_FORM_RECOGNIZER_ENDPOINT = "https://test.cognitiveservices.azure.com/"
            mock_settings.AZURE_FORM_RECOGNIZER_KEY = "test-key"
            mock_settings.OCR_CONFIDENCE_THRESHOLD = 0.8
            
            service = AzureOCRService()
            assert service.confidence_threshold == 0.8
            assert service.client is not None
    
    def test_azure_ocr_service_initialization_without_credentials(self):
        """Test Azure OCR service fails initialization without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Azure Form Recognizer credentials not configured"):
                AzureOCRService()
    
    @pytest.mark.asyncio
    async def test_azure_extract_invoice_success(self):
        """Test successful Azure invoice extraction"""
        # Mock Azure credentials
        with patch('src.services.ocr.settings') as mock_settings:
            mock_settings.AZURE_FORM_RECOGNIZER_ENDPOINT = "https://test.cognitiveservices.azure.com/"
            mock_settings.AZURE_FORM_RECOGNIZER_KEY = "test-key"
            mock_settings.OCR_CONFIDENCE_THRESHOLD = 0.8
            service = AzureOCRService()
            
            # Mock Azure client response
            mock_result = Mock()
            mock_result.fields = [
                Mock(
                    key=Mock(content="Vendor Name"),
                    value=Mock(content="Test Supplier"),
                    confidence=0.95
                ),
                Mock(
                    key=Mock(content="Invoice Number"),
                    value=Mock(content="INV-001"),
                    confidence=0.98
                ),
                Mock(
                    key=Mock(content="Total"),
                    value=Mock(content="$1000.00"),
                    confidence=0.99
                )
            ]
            mock_result.tables = []
            
            # Mock the Azure client
            with patch.object(service.client, 'begin_analyze_document', new_callable=AsyncMock) as mock_analyze:
                mock_poller = Mock()
                mock_poller.result = AsyncMock(return_value=mock_result)
                mock_analyze.return_value = mock_poller
                
                # Create temporary file for testing
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write("Test invoice content")
                    temp_file_path = f.name
                
                try:
                    result = await service.extract_invoice(temp_file_path, "company-123")
                    
                    # Check extracted data
                    assert result["supplier_name"] == "Test Supplier"
                    assert result["invoice_number"] == "INV-001"
                    assert result["total_amount"] == 1000.00
                    
                    # Check confidence scores
                    assert result["confidence_scores"]["supplier_name"] == 0.95
                    assert result["confidence_scores"]["invoice_number"] == 0.98
                    assert result["confidence_scores"]["total_amount"] == 0.99
                    
                    # Check processing metadata
                    assert result["processing_metadata"]["provider"] == "azure"
                    assert result["processing_metadata"]["extraction_method"] == "azure_form_recognizer"
                    
                finally:
                    # Clean up temporary file
                    os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_azure_extract_invoice_with_tables(self):
        """Test Azure invoice extraction with table data"""
        with patch('src.services.ocr.settings') as mock_settings:
            mock_settings.AZURE_FORM_RECOGNIZER_ENDPOINT = "https://test.cognitiveservices.azure.com/"
            mock_settings.AZURE_FORM_RECOGNIZER_KEY = "test-key"
            mock_settings.OCR_CONFIDENCE_THRESHOLD = 0.8
            service = AzureOCRService()
            
            # Mock Azure client response with tables
            mock_result = Mock()
            mock_result.fields = [
                Mock(
                    key=Mock(content="Vendor Name"),
                    value=Mock(content="Test Supplier"),
                    confidence=0.95
                )
            ]
            
            # Mock table with line items
            mock_table = Mock()
            mock_table.row_count = 3  # Header + 2 line items
            mock_table.rows = [
                Mock(cells=[Mock(content="Description"), Mock(content="Qty"), Mock(content="Price")]),  # Header
                Mock(cells=[Mock(content="Item 1"), Mock(content="2"), Mock(content="$50.00")]),       # Line item 1
                Mock(cells=[Mock(content="Item 2"), Mock(content="1"), Mock(content="$100.00")])       # Line item 2
            ]
            mock_result.tables = [mock_table]
            
            with patch.object(service.client, 'begin_analyze_document', new_callable=AsyncMock) as mock_analyze:
                mock_poller = Mock()
                mock_poller.result = AsyncMock(return_value=mock_result)
                mock_analyze.return_value = mock_poller
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write("Test invoice content")
                    temp_file_path = f.name
                
                try:
                    result = await service.extract_invoice(temp_file_path, "company-123")
                    
                    # Check line items were extracted
                    assert len(result["line_items"]) == 2
                    assert result["line_items"][0]["description"] == "Item 1"
                    assert result["line_items"][1]["description"] == "Item 2"
                    
                    # Check confidence for line items
                    assert result["confidence_scores"]["line_items"] == 0.9
                    
                finally:
                    os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_azure_extract_invoice_azure_error(self):
        """Test Azure OCR service handles Azure errors gracefully"""
        with patch('src.services.ocr.settings') as mock_settings:
            mock_settings.AZURE_FORM_RECOGNIZER_ENDPOINT = "https://test.cognitiveservices.azure.com/"
            mock_settings.AZURE_FORM_RECOGNIZER_KEY = "test-key"
            mock_settings.OCR_CONFIDENCE_THRESHOLD = 0.8
            service = AzureOCRService()
            
            with patch.object(service.client, 'begin_analyze_document', new_callable=AsyncMock) as mock_analyze:
                from azure.core.exceptions import AzureError
                mock_analyze.side_effect = AzureError("Test Azure error")
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write("Test invoice content")
                    temp_file_path = f.name
                
                try:
                    with pytest.raises(AzureError, match="Test Azure error"):
                        await service.extract_invoice(temp_file_path, "company-123")
                finally:
                    os.unlink(temp_file_path)
    
    def test_azure_validate_confidence_scores(self):
        """Test confidence score validation"""
        with patch('src.services.ocr.settings') as mock_settings:
            mock_settings.AZURE_FORM_RECOGNIZER_ENDPOINT = "https://test.cognitiveservices.azure.com/"
            mock_settings.AZURE_FORM_RECOGNIZER_KEY = "test-key"
            mock_settings.OCR_CONFIDENCE_THRESHOLD = 0.8
            service = AzureOCRService()
            
            # Test with high confidence scores
            high_confidence = {
                "supplier_name": 0.95,
                "invoice_number": 0.98,
                "total_amount": 0.99
            }
            
            # Should not raise warnings
            with patch('src.services.ocr.logger') as mock_logger:
                service._validate_confidence_scores(high_confidence)
                mock_logger.warning.assert_not_called()
            
            # Test with low confidence scores
            low_confidence = {
                "supplier_name": 0.75,  # Below threshold
                "invoice_number": 0.98,
                "total_amount": 0.99
            }
            
            # Should log warnings for low confidence
            with patch('src.services.ocr.logger') as mock_logger:
                service._validate_confidence_scores(low_confidence)
                mock_logger.warning.assert_called()

class TestOCRService:
    """Test main OCR service that delegates to providers"""
    
    def test_ocr_service_initialization_with_azure(self):
        """Test OCR service initializes with Azure provider"""
        with patch('src.services.ocr.settings') as mock_settings:
            mock_settings.AZURE_FORM_RECOGNIZER_ENDPOINT = "https://test.cognitiveservices.azure.com/"
            mock_settings.AZURE_FORM_RECOGNIZER_KEY = "test-key"
            mock_settings.OCR_CONFIDENCE_THRESHOLD = 0.8
            mock_settings.OCR_PROVIDER = "azure"
            service = OCRService()
            assert isinstance(service.provider, AzureOCRService)
    
    def test_ocr_service_initialization_without_azure(self):
        """Test OCR service falls back to mock provider without Azure"""
        with patch.dict(os.environ, {}, clear=True):
            service = OCRService()
            assert isinstance(service.provider, MockOCRService)
    
    def test_ocr_service_initialization_with_mock_provider(self):
        """Test OCR service uses mock provider when configured"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.services.ocr.settings.OCR_PROVIDER", "mock"):
                service = OCRService()
                assert isinstance(service.provider, MockOCRService)
    
    @pytest.mark.asyncio
    async def test_ocr_service_extract_invoice(self):
        """Test OCR service delegates extraction to provider"""
        service = OCRService()
        
        # Mock the provider
        mock_provider = Mock()
        mock_provider.extract_invoice = AsyncMock(return_value={
            "supplier_name": "Test Supplier",
            "total_amount": 1000.00
        })
        service.provider = mock_provider
        
        result = await service.extract_invoice("/test/path", "company-123")
        
        # Check that provider was called
        mock_provider.extract_invoice.assert_called_once_with("/test/path", "company-123")
        
        # Check result
        assert result["supplier_name"] == "Test Supplier"
        assert result["total_amount"] == 1000.00
    
    @pytest.mark.asyncio
    async def test_ocr_service_validate_extraction(self):
        """Test OCR service validation functionality"""
        service = OCRService()
        
        # Test with valid data
        valid_data = {
            "supplier_name": "Test Supplier",
            "invoice_number": "INV-001",
            "total_amount": 1000.00,
            "confidence_scores": {
                "supplier_name": 0.95,
                "invoice_number": 0.98,
                "total_amount": 0.99
            },
            "line_items": [
                {"description": "Item 1", "quantity": 1, "unit_price": 1000.00, "total": 1000.00}
            ]
        }
        
        validation_result = await service.validate_extraction(valid_data)
        
        assert validation_result["is_valid"] is True
        assert len(validation_result["errors"]) == 0
        assert validation_result["overall_confidence"] > 0.9
        
        # Test with invalid data
        invalid_data = {
            "supplier_name": "",  # Missing required field
            "confidence_scores": {
                "supplier_name": 0.95
            }
        }
        
        validation_result = await service.validate_extraction(invalid_data)
        
        assert validation_result["is_valid"] is False
        assert len(validation_result["errors"]) > 0
        assert "Missing required field: supplier_name" in validation_result["errors"]
    
    @pytest.mark.asyncio
    async def test_ocr_service_processing_metadata(self):
        """Test that OCR service adds processing metadata"""
        service = OCRService()
        
        # Mock the provider
        mock_provider = Mock()
        mock_provider.extract_invoice = AsyncMock(return_value={
            "supplier_name": "Test Supplier",
            "processing_metadata": {
                "provider": "mock",
                "processing_time_ms": 0
            }
        })
        service.provider = mock_provider
        
        result = await service.extract_invoice("/test/path", "company-123")
        
        # Check that processing metadata was added
        assert "processing_metadata" in result
        assert "processing_time_ms" in result["processing_metadata"]
        assert result["processing_metadata"]["processing_time_ms"] > 0

class TestOCRIntegration:
    """Integration tests for OCR service"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_mock_ocr_workflow(self):
        """Test complete mock OCR workflow"""
        service = MockOCRService()
        
        # Simulate invoice processing
        result = await service.extract_invoice("/test/invoice.pdf", "company-123")
        
        # Validate extracted data
        assert result["supplier_name"] is not None
        assert result["invoice_number"] is not None
        assert result["total_amount"] > 0
        assert len(result["line_items"]) > 0
        
        # Validate confidence scores
        confidence_scores = result["confidence_scores"]
        assert confidence_scores["supplier_name"] >= 0.9
        assert confidence_scores["invoice_number"] >= 0.9
        assert confidence_scores["total_amount"] >= 0.9
    
    @pytest.mark.asyncio
    async def test_ocr_service_error_handling(self):
        """Test OCR service handles errors gracefully"""
        service = OCRService()
        
        # Mock provider that raises an exception
        mock_provider = Mock()
        mock_provider.extract_invoice = AsyncMock(side_effect=Exception("OCR processing failed"))
        service.provider = mock_provider
        
        # Should raise the exception
        with pytest.raises(Exception, match="OCR processing failed"):
            await service.extract_invoice("/test/path", "company-123")
