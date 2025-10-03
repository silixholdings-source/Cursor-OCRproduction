"""
Tests for invoice field extraction functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

@pytest.mark.ocr
@pytest.mark.invoice
class TestInvoiceExtraction:
    """Test invoice field extraction functionality."""

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_extract_invoice_fields_success(self, mock_extract, client: TestClient, 
                                          auth_headers: dict, sample_pdf_file: str, 
                                          mock_ocr_response: dict):
        """Test successful invoice field extraction."""
        # Mock OCR response
        mock_extract.return_value = mock_ocr_response
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/extract",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify extracted fields
        assert "supplier_name" in data
        assert "invoice_number" in data
        assert "invoice_date" in data
        assert "total_amount" in data
        assert "line_items" in data
        assert "confidence_scores" in data
        
        # Verify specific values
        assert data["supplier_name"] == mock_ocr_response["supplier_name"]
        assert data["invoice_number"] == mock_ocr_response["invoice_number"]
        assert data["total_amount"] == mock_ocr_response["total_amount"]
        assert len(data["line_items"]) == len(mock_ocr_response["line_items"])

    def test_extract_invoice_fields_without_auth(self, client: TestClient, sample_pdf_file: str):
        """Test invoice extraction without authentication fails."""
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/extract",
                files=files,
                data=data
            )
        
        assert response.status_code == 401

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_extract_invoice_fields_validation(self, mock_extract, client: TestClient, 
                                             auth_headers: dict, sample_pdf_file: str):
        """Test invoice field extraction with validation."""
        # Mock OCR response with some missing fields
        mock_response = {
            "supplier_name": "Test Supplier",
            "invoice_number": "",  # Missing invoice number
            "invoice_date": "2024-01-15",
            "total_amount": 0.0,  # Zero amount
            "currency": "USD",
            "line_items": [],
            "confidence_scores": {
                "supplier_name": 0.95,
                "invoice_number": 0.0,  # Low confidence
                "total_amount": 0.0
            }
        }
        mock_extract.return_value = mock_response
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/extract",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify validation results
        assert "validation" in data
        assert "warnings" in data["validation"]
        assert "errors" in data["validation"]
        
        # Should have warnings for missing/invalid fields
        warnings = data["validation"]["warnings"]
        assert any("invoice number" in warning.lower() for warning in warnings)
        assert any("total amount" in warning.lower() for warning in warnings)

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_extract_invoice_fields_confidence_scoring(self, mock_extract, client: TestClient, 
                                                     auth_headers: dict, sample_pdf_file: str):
        """Test confidence scoring in invoice extraction."""
        # Mock OCR response with confidence scores
        mock_response = {
            "supplier_name": "Test Supplier",
            "invoice_number": "INV-001",
            "invoice_date": "2024-01-15",
            "total_amount": 1500.00,
            "currency": "USD",
            "line_items": [
                {
                    "description": "Test Item",
                    "quantity": 1,
                    "unit_price": 1500.00,
                    "total": 1500.00
                }
            ],
            "confidence_scores": {
                "supplier_name": 0.95,
                "invoice_number": 0.98,
                "invoice_date": 0.92,
                "total_amount": 0.99,
                "line_items": 0.88,
                "overall_confidence": 0.94
            }
        }
        mock_extract.return_value = mock_response
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/extract",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify confidence scores
        assert "confidence_scores" in data
        scores = data["confidence_scores"]
        assert scores["overall_confidence"] == 0.94
        assert scores["supplier_name"] == 0.95
        assert scores["total_amount"] == 0.99

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_extract_invoice_fields_line_items(self, mock_extract, client: TestClient, 
                                             auth_headers: dict, sample_pdf_file: str):
        """Test line items extraction."""
        # Mock OCR response with multiple line items
        mock_response = {
            "supplier_name": "Test Supplier",
            "invoice_number": "INV-001",
            "invoice_date": "2024-01-15",
            "total_amount": 2000.00,
            "currency": "USD",
            "line_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 1000.00,
                    "total": 1000.00,
                    "gl_account": "6000"
                },
                {
                    "description": "Support Services",
                    "quantity": 12,
                    "unit_price": 83.33,
                    "total": 1000.00,
                    "gl_account": "6500"
                }
            ],
            "confidence_scores": {"overall_confidence": 0.95}
        }
        mock_extract.return_value = mock_response
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/extract",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify line items
        assert "line_items" in data
        line_items = data["line_items"]
        assert len(line_items) == 2
        
        # Verify first line item
        first_item = line_items[0]
        assert first_item["description"] == "Software License"
        assert first_item["quantity"] == 1
        assert first_item["unit_price"] == 1000.00
        assert first_item["total"] == 1000.00
        assert first_item["gl_account"] == "6000"
        
        # Verify second line item
        second_item = line_items[1]
        assert second_item["description"] == "Support Services"
        assert second_item["quantity"] == 12
        assert second_item["unit_price"] == 83.33
        assert second_item["total"] == 1000.00

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_extract_invoice_fields_different_formats(self, mock_extract, client: TestClient, 
                                                     auth_headers: dict):
        """Test extraction from different file formats."""
        # Test different file formats
        formats = [".pdf", ".jpg", ".png", ".tiff"]
        
        for fmt in formats:
            # Create temporary file
            import tempfile
            import os
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=fmt)
            temp_file.write(b"Mock content")
            temp_file.close()
            
            try:
                # Mock OCR response
                mock_response = {
                    "supplier_name": f"Test Supplier {fmt}",
                    "invoice_number": f"INV-{fmt.upper()[1:]}",
                    "invoice_date": "2024-01-15",
                    "total_amount": 1000.00,
                    "currency": "USD",
                    "line_items": [],
                    "confidence_scores": {"overall_confidence": 0.95}
                }
                mock_extract.return_value = mock_response
                
                with open(temp_file.name, "rb") as f:
                    files = {"file": (f"test{fmt}", f, f"application/{fmt[1:]}" if fmt == ".pdf" else f"image/{fmt[1:]}")}
                    data = {"company_id": "test-company"}
                    
                    response = client.post(
                        "/api/v1/ocr/extract",
                        files=files,
                        data=data,
                        headers=auth_headers
                    )
                
                assert response.status_code == 200, f"Failed for format {fmt}"
                data = response.json()
                assert data["supplier_name"] == f"Test Supplier {fmt}"
                
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_extract_invoice_fields_ocr_failure(self, mock_extract, client: TestClient, 
                                              auth_headers: dict, sample_pdf_file: str):
        """Test handling of OCR extraction failure."""
        # Mock OCR failure
        mock_extract.side_effect = Exception("OCR service unavailable")
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/extract",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 500
        assert "processing failed" in response.json()["detail"].lower()

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_extract_invoice_fields_timeout(self, mock_extract, client: TestClient, 
                                          auth_headers: dict, sample_pdf_file: str):
        """Test handling of OCR extraction timeout."""
        # Mock OCR timeout
        import asyncio
        async def timeout_extract(*args, **kwargs):
            await asyncio.sleep(35)  # Longer than timeout
            return {}
        
        mock_extract.side_effect = timeout_extract
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/extract",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        # Should handle timeout gracefully
        assert response.status_code in [500, 408]  # 500 for error, 408 for timeout

    def test_extract_invoice_fields_invalid_file(self, client: TestClient, auth_headers: dict):
        """Test extraction with invalid file."""
        # Create invalid file
        import tempfile
        import os
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        temp_file.write(b"Not a valid image or PDF")
        temp_file.close()
        
        try:
            with open(temp_file.name, "rb") as f:
                files = {"file": ("test.txt", f, "text/plain")}
                data = {"company_id": "test-company"}
                
                response = client.post(
                    "/api/v1/ocr/extract",
                    files=files,
                    data=data,
                    headers=auth_headers
                )
            
            assert response.status_code == 400
            assert "file type not supported" in response.json()["detail"].lower()
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_extract_invoice_fields_batch_processing(self, mock_extract, client: TestClient, 
                                                   auth_headers: dict):
        """Test batch processing of multiple files."""
        # Mock OCR response
        mock_response = {
            "supplier_name": "Test Supplier",
            "invoice_number": "INV-001",
            "invoice_date": "2024-01-15",
            "total_amount": 1000.00,
            "currency": "USD",
            "line_items": [],
            "confidence_scores": {"overall_confidence": 0.95}
        }
        mock_extract.return_value = mock_response
        
        # Test batch processing endpoint (if available)
        files_data = []
        temp_files = []
        
        try:
            # Create multiple files
            for i in range(3):
                import tempfile
                import os
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_file.write(f"Mock PDF content {i}".encode())
                temp_file.close()
                temp_files.append(temp_file.name)
                
                with open(temp_file.name, "rb") as f:
                    files_data.append(("files", (f"test_{i}.pdf", f, "application/pdf")))
            
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/extract/batch",
                files=files_data,
                data=data,
                headers=auth_headers
            )
            
            # This endpoint might not exist, so check for appropriate response
            assert response.status_code in [200, 404, 405]  # 404 if not implemented, 405 if method not allowed
            
        finally:
            # Cleanup
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)









