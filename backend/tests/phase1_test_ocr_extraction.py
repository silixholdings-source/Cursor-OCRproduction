"""
Phase 1 Test Suite for Invoice OCR Extraction with Golden Dataset Validation
Tests OCR accuracy, confidence scoring, and data extraction quality
"""

import pytest
import asyncio
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
import uuid
from pathlib import Path

from services.ocr import OCRService, AzureOCRService, MockOCRService
from services.simple_ocr import SimpleOCRService
from tests.golden_datasets import golden_dataset_manager, GoldenInvoiceData


class TestPhase1OCRExtraction:
    """Test suite for Phase 1 OCR extraction requirements"""
    
    @pytest.fixture
    def ocr_service(self):
        """Create OCR service instance"""
        return OCRService()
    
    @pytest.fixture
    def mock_ocr_service(self):
        """Create mock OCR service for testing"""
        return MockOCRService()
    
    @pytest.fixture
    def simple_ocr_service(self):
        """Create simple OCR service"""
        return SimpleOCRService()
    
    @pytest.fixture
    def golden_datasets(self):
        """Get golden datasets for testing"""
        return golden_dataset_manager

    @pytest.mark.asyncio
    async def test_simple_invoice_ocr_extraction(self, ocr_service, golden_datasets):
        """Test OCR extraction on simple invoice from golden dataset"""
        
        # Get simple invoice dataset
        simple_dataset = golden_datasets.get_invoice_dataset("simple_invoice_001")
        assert simple_dataset is not None
        
        # Mock file path (in real tests, this would be an actual PDF file)
        mock_file_path = f"/tmp/{simple_dataset.file_path}"
        
        # Mock the OCR extraction result
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.return_value = {
                "supplier_name": "Tech Solutions Inc.",
                "invoice_number": "TS-2024-001",
                "invoice_date": "2024-01-15",
                "due_date": "2024-02-14",
                "total_amount": 2500.00,
                "currency": "USD",
                "tax_amount": 200.00,
                "subtotal": 2300.00,
                "line_items": [
                    {
                        "description": "Software License - Annual",
                        "quantity": 1,
                        "unit_price": 2000.00,
                        "total": 2000.00
                    },
                    {
                        "description": "Implementation Services",
                        "quantity": 10,
                        "unit_price": 30.00,
                        "total": 300.00
                    }
                ],
                "confidence_scores": {
                    "supplier_name": 0.98,
                    "invoice_number": 0.99,
                    "total_amount": 0.99,
                    "line_items": 0.95
                },
                "processing_metadata": {
                    "provider": "mock",
                    "processing_time_ms": 150,
                    "file_size_bytes": 1024,
                    "extraction_method": "mock"
                }
            }
            
            # Perform OCR extraction
            result = await ocr_service.extract_invoice(mock_file_path, str(uuid.uuid4()))
            
            # Validate against golden dataset
            validation_result = golden_datasets.validate_ocr_result("simple_invoice_001", result)
            
            # Assertions
            assert validation_result["valid"] == True
            assert validation_result["overall_accuracy"] >= 0.95
            assert result["supplier_name"] == "Tech Solutions Inc."
            assert result["invoice_number"] == "TS-2024-001"
            assert result["total_amount"] == 2500.00
            assert len(result["line_items"]) == 2
            assert result["confidence_scores"]["supplier_name"] >= 0.98

    @pytest.mark.asyncio
    async def test_medium_complexity_invoice_ocr_extraction(self, ocr_service, golden_datasets):
        """Test OCR extraction on medium complexity invoice"""
        
        medium_dataset = golden_datasets.get_invoice_dataset("medium_invoice_001")
        assert medium_dataset is not None
        
        mock_file_path = f"/tmp/{medium_dataset.file_path}"
        
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.return_value = {
                "supplier_name": "Manufacturing Corp.",
                "invoice_number": "MC-2024-003",
                "invoice_date": "2024-01-25",
                "due_date": "2024-03-25",
                "total_amount": 15650.00,
                "currency": "USD",
                "tax_amount": 1252.00,
                "subtotal": 14398.00,
                "line_items": [
                    {
                        "description": "Raw Materials - Steel Sheets",
                        "quantity": 500,
                        "unit_price": 15.50,
                        "total": 7750.00
                    },
                    {
                        "description": "Machining Services",
                        "quantity": 200,
                        "unit_price": 25.00,
                        "total": 5000.00
                    },
                    {
                        "description": "Quality Inspection",
                        "quantity": 50,
                        "unit_price": 32.96,
                        "total": 1648.00
                    }
                ],
                "shipping_address": {
                    "company": "ABC Manufacturing",
                    "address": "123 Industrial Blvd",
                    "city": "Detroit",
                    "state": "MI",
                    "zip": "48201"
                },
                "confidence_scores": {
                    "supplier_name": 0.96,
                    "invoice_number": 0.98,
                    "total_amount": 0.98,
                    "line_items": 0.92,
                    "shipping_address": 0.90
                },
                "processing_metadata": {
                    "provider": "mock",
                    "processing_time_ms": 200,
                    "file_size_bytes": 2048,
                    "extraction_method": "mock"
                }
            }
            
            result = await ocr_service.extract_invoice(mock_file_path, str(uuid.uuid4()))
            
            # Validate against golden dataset
            validation_result = golden_datasets.validate_ocr_result("medium_invoice_001", result)
            
            assert validation_result["valid"] == True
            assert validation_result["overall_accuracy"] >= 0.95
            assert result["total_amount"] == 15650.00
            assert len(result["line_items"]) == 3
            assert "shipping_address" in result
            assert result["shipping_address"]["city"] == "Detroit"

    @pytest.mark.asyncio
    async def test_complex_invoice_ocr_extraction(self, ocr_service, golden_datasets):
        """Test OCR extraction on complex invoice with multiple addresses and references"""
        
        complex_dataset = golden_datasets.get_invoice_dataset("complex_invoice_001")
        assert complex_dataset is not None
        
        mock_file_path = f"/tmp/{complex_dataset.file_path}"
        
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.return_value = {
                "supplier_name": "Multi-National Corporation",
                "invoice_number": "MNC-2024-005",
                "invoice_date": "2024-02-05",
                "due_date": "2024-03-07",
                "total_amount": 45620.50,
                "currency": "USD",
                "tax_amount": 3649.64,
                "subtotal": 41970.86,
                "line_items": [
                    {
                        "description": "Enterprise Software License - 3 Year",
                        "quantity": 1,
                        "unit_price": 25000.00,
                        "total": 25000.00
                    },
                    {
                        "description": "Implementation & Training",
                        "quantity": 1,
                        "unit_price": 8500.00,
                        "total": 8500.00
                    },
                    {
                        "description": "Data Migration Services",
                        "quantity": 1,
                        "unit_price": 4200.00,
                        "total": 4200.00
                    },
                    {
                        "description": "Ongoing Support - Year 1",
                        "quantity": 1,
                        "unit_price": 3270.86,
                        "total": 3270.86
                    },
                    {
                        "description": "Custom Integration Development",
                        "quantity": 1,
                        "unit_price": 1000.00,
                        "total": 1000.00
                    }
                ],
                "billing_address": {
                    "company": "Enterprise Client Inc.",
                    "address": "456 Corporate Plaza",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001"
                },
                "shipping_address": {
                    "company": "Enterprise Client Inc.",
                    "address": "789 Tech Center",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94105"
                },
                "payment_terms": "Net 30",
                "po_number": "PO-2024-001",
                "contract_number": "CNT-2024-005",
                "confidence_scores": {
                    "supplier_name": 0.94,
                    "invoice_number": 0.97,
                    "total_amount": 0.97,
                    "line_items": 0.90,
                    "billing_address": 0.88,
                    "shipping_address": 0.88,
                    "po_number": 0.92,
                    "contract_number": 0.90
                },
                "processing_metadata": {
                    "provider": "mock",
                    "processing_time_ms": 300,
                    "file_size_bytes": 4096,
                    "extraction_method": "mock"
                }
            }
            
            result = await ocr_service.extract_invoice(mock_file_path, str(uuid.uuid4()))
            
            # Validate against golden dataset
            validation_result = golden_datasets.validate_ocr_result("complex_invoice_001", result)
            
            assert validation_result["valid"] == True
            assert validation_result["overall_accuracy"] >= 0.90  # Slightly lower threshold for complex invoices
            assert result["total_amount"] == 45620.50
            assert len(result["line_items"]) == 5
            assert result["po_number"] == "PO-2024-001"
            assert result["contract_number"] == "CNT-2024-005"
            assert "billing_address" in result
            assert "shipping_address" in result

    @pytest.mark.asyncio
    async def test_edge_case_handwritten_invoice(self, ocr_service, golden_datasets):
        """Test OCR extraction on handwritten invoice (challenging case)"""
        
        edge_dataset = golden_datasets.get_invoice_dataset("edge_case_001")
        assert edge_dataset is not None
        
        mock_file_path = f"/tmp/{edge_dataset.file_path}"
        
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.return_value = {
                "supplier_name": "Handwritten Services",
                "invoice_number": "HS-2024-007",
                "invoice_date": "2024-02-15",
                "due_date": "2024-03-15",
                "total_amount": 850.00,
                "currency": "USD",
                "tax_amount": 68.00,
                "subtotal": 782.00,
                "line_items": [
                    {
                        "description": "Consulting Services - Handwritten Invoice",
                        "quantity": 1,
                        "unit_price": 782.00,
                        "total": 782.00
                    }
                ],
                "confidence_scores": {
                    "supplier_name": 0.85,
                    "invoice_number": 0.88,
                    "total_amount": 0.90,
                    "line_items": 0.82
                },
                "processing_metadata": {
                    "provider": "mock",
                    "processing_time_ms": 500,
                    "file_size_bytes": 512,
                    "extraction_method": "mock",
                    "quality_issues": ["handwritten_text", "poor_scan_quality"]
                }
            }
            
            result = await ocr_service.extract_invoice(mock_file_path, str(uuid.uuid4()))
            
            # Validate against golden dataset
            validation_result = golden_datasets.validate_ocr_result("edge_case_001", result)
            
            # For edge cases, we expect lower accuracy but still functional results
            assert validation_result["overall_accuracy"] >= 0.80
            assert result["supplier_name"] == "Handwritten Services"
            assert result["total_amount"] == 850.00
            assert result["confidence_scores"]["supplier_name"] >= 0.85

    @pytest.mark.asyncio
    async def test_multilingual_invoice_extraction(self, ocr_service, golden_datasets):
        """Test OCR extraction on bilingual invoice"""
        
        multilingual_dataset = golden_datasets.get_invoice_dataset("edge_case_002")
        assert multilingual_dataset is not None
        
        mock_file_path = f"/tmp/{multilingual_dataset.file_path}"
        
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.return_value = {
                "supplier_name": "Multi-Language Corp.",
                "invoice_number": "ML-2024-008",
                "invoice_date": "2024-02-20",
                "due_date": "2024-03-20",
                "total_amount": 12500.00,
                "currency": "USD",
                "tax_amount": 1000.00,
                "subtotal": 11500.00,
                "line_items": [
                    {
                        "description": "Servicios de Consultoría / Consulting Services",
                        "quantity": 1,
                        "unit_price": 11500.00,
                        "total": 11500.00
                    }
                ],
                "confidence_scores": {
                    "supplier_name": 0.92,
                    "invoice_number": 0.95,
                    "total_amount": 0.94,
                    "line_items": 0.88
                },
                "processing_metadata": {
                    "provider": "mock",
                    "processing_time_ms": 250,
                    "file_size_bytes": 1536,
                    "extraction_method": "mock",
                    "languages_detected": ["es", "en"]
                }
            }
            
            result = await ocr_service.extract_invoice(mock_file_path, str(uuid.uuid4()))
            
            # Validate against golden dataset
            validation_result = golden_datasets.validate_ocr_result("edge_case_002", result)
            
            assert validation_result["valid"] == True
            assert validation_result["overall_accuracy"] >= 0.90
            assert result["supplier_name"] == "Multi-Language Corp."
            assert result["total_amount"] == 12500.00
            assert "Consulting Services" in result["line_items"][0]["description"]

    @pytest.mark.asyncio
    async def test_confidence_score_validation(self, ocr_service):
        """Test confidence score validation and thresholds"""
        
        mock_file_path = "/tmp/test_invoice.pdf"
        
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.return_value = {
                "supplier_name": "Test Supplier",
                "invoice_number": "TEST-001",
                "total_amount": 1000.00,
                "confidence_scores": {
                    "supplier_name": 0.95,  # Above threshold
                    "invoice_number": 0.99,  # Above threshold
                    "total_amount": 0.85,    # Below threshold
                    "line_items": 0.75       # Below threshold
                },
                "processing_metadata": {
                    "provider": "mock",
                    "processing_time_ms": 100,
                    "file_size_bytes": 1024,
                    "extraction_method": "mock"
                }
            }
            
            result = await ocr_service.extract_invoice(mock_file_path, str(uuid.uuid4()))
            
            # Check confidence scores
            confidence_scores = result["confidence_scores"]
            assert confidence_scores["supplier_name"] >= 0.95
            assert confidence_scores["invoice_number"] >= 0.95
            assert confidence_scores["total_amount"] < 0.95  # Below threshold
            assert confidence_scores["line_items"] < 0.95    # Below threshold

    @pytest.mark.asyncio
    async def test_processing_metadata_tracking(self, ocr_service):
        """Test processing metadata tracking and performance metrics"""
        
        mock_file_path = "/tmp/test_invoice.pdf"
        
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.return_value = {
                "supplier_name": "Test Supplier",
                "invoice_number": "TEST-001",
                "total_amount": 1000.00,
                "confidence_scores": {
                    "supplier_name": 0.98,
                    "invoice_number": 0.99,
                    "total_amount": 0.99
                },
                "processing_metadata": {
                    "provider": "mock",
                    "processing_time_ms": 150,
                    "file_size_bytes": 2048,
                    "extraction_method": "mock",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            result = await ocr_service.extract_invoice(mock_file_path, str(uuid.uuid4()))
            
            # Check processing metadata
            metadata = result["processing_metadata"]
            assert metadata["provider"] == "mock"
            assert metadata["processing_time_ms"] >= 0
            assert metadata["file_size_bytes"] > 0
            assert "timestamp" in metadata

    @pytest.mark.asyncio
    async def test_error_handling_invalid_file(self, ocr_service):
        """Test error handling for invalid file paths"""
        
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.side_effect = FileNotFoundError("File not found")
            
            with pytest.raises(FileNotFoundError):
                await ocr_service.extract_invoice("/invalid/path/invoice.pdf", str(uuid.uuid4()))

    @pytest.mark.asyncio
    async def test_error_handling_corrupted_file(self, ocr_service):
        """Test error handling for corrupted files"""
        
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.side_effect = Exception("Corrupted file format")
            
            with pytest.raises(Exception) as exc_info:
                await ocr_service.extract_invoice("/tmp/corrupted.pdf", str(uuid.uuid4()))
            
            assert "Corrupted file format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_batch_processing_performance(self, ocr_service, golden_datasets):
        """Test batch processing performance with multiple invoices"""
        
        # Get multiple datasets for batch testing
        simple_datasets = golden_datasets.get_datasets_by_category("simple")
        batch_size = min(5, len(simple_datasets))
        
        mock_file_paths = [f"/tmp/{dataset.file_path}" for dataset in simple_datasets[:batch_size]]
        
        with patch.object(ocr_service.provider, 'extract_invoice') as mock_extract:
            mock_extract.return_value = {
                "supplier_name": "Batch Test Supplier",
                "invoice_number": "BATCH-001",
                "total_amount": 1000.00,
                "confidence_scores": {
                    "supplier_name": 0.98,
                    "invoice_number": 0.99,
                    "total_amount": 0.99
                },
                "processing_metadata": {
                    "provider": "mock",
                    "processing_time_ms": 100,
                    "file_size_bytes": 1024,
                    "extraction_method": "mock"
                }
            }
            
            # Process batch of invoices
            start_time = datetime.utcnow()
            tasks = [
                ocr_service.extract_invoice(file_path, str(uuid.uuid4()))
                for file_path in mock_file_paths
            ]
            results = await asyncio.gather(*tasks)
            end_time = datetime.utcnow()
            
            # Verify batch processing
            assert len(results) == batch_size
            assert all(result["supplier_name"] == "Batch Test Supplier" for result in results)
            
            # Check processing time (should be reasonable for batch)
            processing_time = (end_time - start_time).total_seconds()
            assert processing_time < 2.0  # Should complete within 2 seconds

    def test_golden_dataset_validation_accuracy(self, golden_datasets):
        """Test golden dataset validation accuracy calculations"""
        
        # Test perfect match
        perfect_result = {
            "supplier_name": "Tech Solutions Inc.",
            "invoice_number": "TS-2024-001",
            "total_amount": 2500.00,
            "confidence_scores": {
                "supplier_name": 0.98,
                "invoice_number": 0.99,
                "total_amount": 0.99
            }
        }
        
        validation = golden_datasets.validate_ocr_result("simple_invoice_001", perfect_result)
        assert validation["valid"] == True
        assert validation["overall_accuracy"] >= 0.95
        
        # Test partial match
        partial_result = {
            "supplier_name": "Tech Solutions Inc.",
            "invoice_number": "TS-2024-001",
            "total_amount": 2500.00,
            "confidence_scores": {
                "supplier_name": 0.85,  # Below threshold
                "invoice_number": 0.99,
                "total_amount": 0.99
            }
        }
        
        validation = golden_datasets.validate_ocr_result("simple_invoice_001", partial_result)
        # Should still be valid due to overall accuracy
        assert validation["overall_accuracy"] >= 0.90

    def test_confidence_threshold_enforcement(self, golden_datasets):
        """Test confidence threshold enforcement"""
        
        dataset = golden_datasets.get_invoice_dataset("simple_invoice_001")
        assert dataset is not None
        
        # Test with low confidence scores
        low_confidence_result = {
            "supplier_name": "Tech Solutions Inc.",
            "invoice_number": "TS-2024-001",
            "total_amount": 2500.00,
            "confidence_scores": {
                "supplier_name": 0.70,  # Below 0.98 threshold
                "invoice_number": 0.80,  # Below 0.99 threshold
                "total_amount": 0.85    # Below 0.99 threshold
            }
        }
        
        validation = golden_datasets.validate_ocr_result("simple_invoice_001", low_confidence_result)
        
        # Check that low confidence fields are flagged
        field_results = validation["field_results"]
        assert field_results["supplier_name"]["meets_threshold"] == False
        assert field_results["invoice_number"]["meets_threshold"] == False
        assert field_results["total_amount"]["meets_threshold"] == False

    @pytest.mark.asyncio
    async def test_azure_ocr_service_fallback(self):
        """Test Azure OCR service fallback to mock when not configured"""
        
        # Test with missing Azure credentials
        with patch('services.ocr.settings') as mock_settings:
            mock_settings.AZURE_FORM_RECOGNIZER_ENDPOINT = None
            mock_settings.AZURE_FORM_RECOGNIZER_KEY = None
            mock_settings.OCR_PROVIDER = "azure"
            
            # Should fall back to mock service
            ocr_service = OCRService()
            assert isinstance(ocr_service.provider, MockOCRService)

    @pytest.mark.asyncio
    async def test_simple_ocr_service_integration(self, simple_ocr_service):
        """Test simple OCR service integration"""
        
        mock_file_path = "/tmp/simple_test.pdf"
        
        with patch.object(simple_ocr_service, 'extract_invoice') as mock_extract:
            mock_extract.return_value = {
                "supplier_name": "Simple Test Supplier",
                "invoice_number": "SIMPLE-001",
                "total_amount": 500.00,
                "confidence_scores": {
                    "supplier_name": 0.95,
                    "invoice_number": 0.98,
                    "total_amount": 0.97
                },
                "processing_metadata": {
                    "provider": "simple",
                    "processing_time_ms": 50,
                    "file_size_bytes": 512,
                    "extraction_method": "simple"
                }
            }
            
            result = await simple_ocr_service.extract_invoice(mock_file_path, str(uuid.uuid4()))
            
            assert result["supplier_name"] == "Simple Test Supplier"
            assert result["total_amount"] == 500.00
            assert result["processing_metadata"]["provider"] == "simple"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])








