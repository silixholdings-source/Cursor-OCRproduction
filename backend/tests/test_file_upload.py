"""
Tests for file upload functionality
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

@pytest.mark.file_upload
class TestFileUpload:
    """Test file upload functionality."""

    def test_upload_pdf_file_success(self, client: TestClient, auth_headers: dict, sample_pdf_file: str):
        """Test successful PDF file upload."""
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert "status" in data
        assert data["status"] == "uploaded"

    def test_upload_image_file_success(self, client: TestClient, auth_headers: dict, sample_image_file: str):
        """Test successful image file upload."""
        with open(sample_image_file, "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert "status" in data

    def test_upload_file_without_auth(self, client: TestClient, sample_pdf_file: str):
        """Test file upload without authentication fails."""
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/upload",
                files=files,
                data=data
            )
        
        assert response.status_code == 401

    def test_upload_file_invalid_extension(self, client: TestClient, auth_headers: dict):
        """Test file upload with invalid file extension."""
        # Create a temporary file with invalid extension
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        temp_file.write(b"Mock content")
        temp_file.close()
        
        try:
            with open(temp_file.name, "rb") as f:
                files = {"file": ("test.txt", f, "text/plain")}
                data = {"company_id": "test-company"}
                
                response = client.post(
                    "/api/v1/ocr/upload",
                    files=files,
                    data=data,
                    headers=auth_headers
                )
            
            assert response.status_code == 400
            assert "file type not supported" in response.json()["detail"].lower()
        finally:
            os.unlink(temp_file.name)

    def test_upload_file_too_large(self, client: TestClient, auth_headers: dict):
        """Test file upload with file too large."""
        # Create a large temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        # Write 11MB of data (exceeds 10MB limit)
        temp_file.write(b"x" * (11 * 1024 * 1024))
        temp_file.close()
        
        try:
            with open(temp_file.name, "rb") as f:
                files = {"file": ("large.pdf", f, "application/pdf")}
                data = {"company_id": "test-company"}
                
                response = client.post(
                    "/api/v1/ocr/upload",
                    files=files,
                    data=data,
                    headers=auth_headers
                )
            
            assert response.status_code == 400
            assert "file too large" in response.json()["detail"].lower()
        finally:
            os.unlink(temp_file.name)

    def test_upload_file_missing_file(self, client: TestClient, auth_headers: dict):
        """Test file upload without file parameter."""
        data = {"company_id": "test-company"}
        
        response = client.post(
            "/api/v1/ocr/upload",
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "no file provided" in response.json()["detail"].lower()

    def test_upload_file_missing_company_id(self, client: TestClient, auth_headers: dict, sample_pdf_file: str):
        """Test file upload without company_id."""
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            
            response = client.post(
                "/api/v1/ocr/upload",
                files=files,
                headers=auth_headers
            )
        
        assert response.status_code == 400
        assert "company_id" in response.json()["detail"].lower()

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_upload_and_process_file(self, mock_extract, client: TestClient, auth_headers: dict, 
                                   sample_pdf_file: str, mock_ocr_response: dict):
        """Test file upload and OCR processing."""
        # Mock OCR response
        mock_extract.return_value = mock_ocr_response
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/process",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "extracted_data" in data
        assert data["extracted_data"]["supplier_name"] == mock_ocr_response["supplier_name"]
        assert data["extracted_data"]["invoice_number"] == mock_ocr_response["invoice_number"]

    def test_upload_multiple_files(self, client: TestClient, auth_headers: dict):
        """Test uploading multiple files."""
        files = []
        temp_files = []
        
        try:
            # Create multiple temporary files
            for i in range(3):
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_file.write(f"Mock PDF content {i}".encode())
                temp_file.close()
                temp_files.append(temp_file.name)
                
                with open(temp_file.name, "rb") as f:
                    files.append(("file", (f"test_{i}.pdf", f, "application/pdf")))
            
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
            
            # Note: This endpoint might not support multiple files
            # Adjust based on your actual implementation
            assert response.status_code in [200, 400]  # 400 if not supported
            
        finally:
            # Cleanup
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

    def test_upload_file_with_metadata(self, client: TestClient, auth_headers: dict, sample_pdf_file: str):
        """Test file upload with additional metadata."""
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {
                "company_id": "test-company",
                "invoice_type": "invoice",
                "department": "IT",
                "cost_center": "CC001"
            }
            
            response = client.post(
                "/api/v1/ocr/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_upload_file_ocr_failure(self, mock_extract, client: TestClient, auth_headers: dict, 
                                   sample_pdf_file: str):
        """Test file upload when OCR processing fails."""
        # Mock OCR failure
        mock_extract.side_effect = Exception("OCR processing failed")
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/process",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 500
        assert "processing failed" in response.json()["detail"].lower()

    def test_upload_file_different_formats(self, client: TestClient, auth_headers: dict):
        """Test uploading files in different supported formats."""
        supported_formats = [
            (".pdf", "application/pdf"),
            (".jpg", "image/jpeg"),
            (".jpeg", "image/jpeg"),
            (".png", "image/png"),
            (".tiff", "image/tiff")
        ]
        
        for ext, mime_type in supported_formats:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            temp_file.write(b"Mock content")
            temp_file.close()
            
            try:
                with open(temp_file.name, "rb") as f:
                    files = {"file": (f"test{ext}", f, mime_type)}
                    data = {"company_id": "test-company"}
                    
                    response = client.post(
                        "/api/v1/ocr/upload",
                        files=files,
                        data=data,
                        headers=auth_headers
                    )
                
                assert response.status_code == 200, f"Failed for format {ext}"
                
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)

    def test_upload_file_storage_verification(self, client: TestClient, auth_headers: dict, 
                                            sample_pdf_file: str):
        """Test that uploaded file is properly stored."""
        with open(sample_pdf_file, "rb") as f:
            original_content = f.read()
        
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            response = client.post(
                "/api/v1/ocr/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify file was stored (implementation depends on your storage solution)
        assert "file_id" in data
        assert "file_path" in data or "file_url" in data
        
        # If file path is returned, verify file exists and content matches
        if "file_path" in data:
            stored_file_path = data["file_path"]
            assert os.path.exists(stored_file_path)
            
            with open(stored_file_path, "rb") as f:
                stored_content = f.read()
            assert stored_content == original_content









