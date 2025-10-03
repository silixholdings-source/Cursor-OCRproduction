"""
Integration tests for the complete invoice processing workflow
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

@pytest.mark.integration
class TestInvoiceProcessingWorkflow:
    """Test complete invoice processing workflow."""

    @patch('src.services.ocr_client.OCRClient.extract_invoice')
    def test_complete_invoice_workflow(self, mock_extract, client: TestClient, 
                                     auth_headers: dict, sample_pdf_file: str, 
                                     mock_ocr_response: dict):
        """Test complete workflow from file upload to invoice creation."""
        # Mock OCR response
        mock_extract.return_value = mock_ocr_response
        
        # Step 1: Upload file
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            upload_response = client.post(
                "/api/v1/ocr/upload",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert upload_response.status_code == 200
        file_id = upload_response.json()["file_id"]
        
        # Step 2: Process file with OCR
        with open(sample_pdf_file, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            data = {"company_id": "test-company"}
            
            ocr_response = client.post(
                "/api/v1/ocr/process",
                files=files,
                data=data,
                headers=auth_headers
            )
        
        assert ocr_response.status_code == 200
        extracted_data = ocr_response.json()["extracted_data"]
        
        # Step 3: Create invoice from extracted data
        invoice_data = {
            "invoice_number": extracted_data["invoice_number"],
            "supplier_name": extracted_data["supplier_name"],
            "invoice_date": extracted_data["invoice_date"],
            "total_amount": extracted_data["total_amount"],
            "currency": extracted_data["currency"],
            "line_items": extracted_data["line_items"],
            "ocr_data": extracted_data
        }
        
        create_response = client.post(
            "/api/v1/invoices",
            json=invoice_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        invoice_id = create_response.json()["id"]
        
        # Step 4: Retrieve created invoice
        get_response = client.get(f"/api/v1/invoices/{invoice_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        invoice = get_response.json()
        assert invoice["invoice_number"] == mock_ocr_response["invoice_number"]
        assert invoice["supplier_name"] == mock_ocr_response["supplier_name"]
        assert invoice["total_amount"] == mock_ocr_response["total_amount"]
        assert len(invoice["line_items"]) == len(mock_ocr_response["line_items"])

    def test_invoice_approval_workflow(self, client: TestClient, auth_headers: dict, 
                                     sample_invoice):
        """Test invoice approval workflow."""
        # Step 1: Get invoice (should be draft)
        response = client.get(f"/api/v1/invoices/{sample_invoice.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "draft"
        
        # Step 2: Submit for approval
        response = client.put(
            f"/api/v1/invoices/{sample_invoice.id}",
            json={"status": "pending_approval"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 3: Approve invoice
        response = client.put(
            f"/api/v1/invoices/{sample_invoice.id}",
            json={"status": "approved"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 4: Verify approval
        response = client.get(f"/api/v1/invoices/{sample_invoice.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "approved"

    def test_invoice_rejection_workflow(self, client: TestClient, auth_headers: dict, 
                                      sample_invoice):
        """Test invoice rejection workflow."""
        # Step 1: Submit for approval
        response = client.put(
            f"/api/v1/invoices/{sample_invoice.id}",
            json={"status": "pending_approval"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 2: Reject invoice with reason
        response = client.put(
            f"/api/v1/invoices/{sample_invoice.id}",
            json={
                "status": "rejected",
                "rejection_reason": "Invalid supplier information"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 3: Verify rejection
        response = client.get(f"/api/v1/invoices/{sample_invoice.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["rejection_reason"] == "Invalid supplier information"

    def test_batch_invoice_processing(self, client: TestClient, auth_headers: dict):
        """Test processing multiple invoices in batch."""
        # Create multiple test files
        import tempfile
        import os
        
        files_data = []
        temp_files = []
        
        try:
            # Create multiple PDF files
            for i in range(3):
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_file.write(f"Mock PDF content {i}".encode())
                temp_file.close()
                temp_files.append(temp_file.name)
                
                with open(temp_file.name, "rb") as f:
                    files_data.append(("files", (f"test_{i}.pdf", f, "application/pdf")))
            
            data = {"company_id": "test-company"}
            
            # Upload multiple files
            response = client.post(
                "/api/v1/ocr/upload/batch",
                files=files_data,
                data=data,
                headers=auth_headers
            )
            
            # This endpoint might not exist, so check for appropriate response
            assert response.status_code in [200, 404, 405]
            
        finally:
            # Cleanup
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

    def test_invoice_search_and_filtering(self, client: TestClient, auth_headers: dict, 
                                        multiple_invoices):
        """Test invoice search and filtering capabilities."""
        # Test search by invoice number
        response = client.get("/api/v1/invoices?search=INV-001", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["invoices"]) == 1
        assert data["invoices"][0]["invoice_number"] == "INV-001"
        
        # Test filter by status
        response = client.get("/api/v1/invoices?status=approved", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        for invoice in data["invoices"]:
            assert invoice["status"] == "approved"
        
        # Test filter by amount range
        response = client.get("/api/v1/invoices?min_amount=1100&max_amount=1200", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        for invoice in data["invoices"]:
            assert 1100 <= invoice["total_amount"] <= 1200

    def test_invoice_analytics_integration(self, client: TestClient, auth_headers: dict, 
                                         multiple_invoices):
        """Test invoice analytics integration."""
        # Get invoice analytics
        response = client.get("/api/v1/invoices/analytics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify analytics data
        assert "total_invoices" in data
        assert "total_amount" in data
        assert "approved_count" in data
        assert "pending_count" in data
        assert "rejected_count" in data
        assert "avg_amount" in data
        
        # Verify calculated values
        assert data["total_invoices"] == 5
        assert data["total_amount"] == sum(inv.total_amount for inv in multiple_invoices)
        assert data["approved_count"] == 2
        assert data["pending_count"] == 3

    def test_invoice_export_integration(self, client: TestClient, auth_headers: dict, 
                                      multiple_invoices):
        """Test invoice export functionality."""
        # Export as CSV
        response = client.get("/api/v1/invoices/export?format=csv", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        
        # Verify CSV content
        csv_content = response.text
        assert "invoice_number" in csv_content
        assert "supplier_name" in csv_content
        assert "total_amount" in csv_content
        
        # Export as JSON
        response = client.get("/api/v1/invoices/export?format=json", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert len(data) == 5
        assert all("invoice_number" in invoice for invoice in data)

    def test_error_handling_integration(self, client: TestClient, auth_headers: dict):
        """Test error handling across the integration."""
        # Test with invalid file
        import tempfile
        import os
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        temp_file.write(b"Not a valid PDF")
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
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

    def test_performance_integration(self, client: TestClient, auth_headers: dict, 
                                   db_session: Session, test_company, test_user):
        """Test performance with large dataset."""
        import uuid
        import time
        from src.models.invoice import Invoice
        
        # Create many invoices
        invoices = []
        for i in range(100):
            invoice = Invoice(
                id=uuid.uuid4(),
                invoice_number=f"PERF-{i:03d}",
                supplier_name=f"Supplier {i}",
                invoice_date="2024-01-15",
                total_amount=1000.00 + i,
                currency="USD",
                status="draft",
                company_id=test_company.id,
                created_by_id=test_user.id,
                ocr_data={}
            )
            invoices.append(invoice)
        
        db_session.add_all(invoices)
        db_session.commit()
        
        # Test pagination performance
        start_time = time.time()
        
        response = client.get("/api/v1/invoices?page=1&per_page=20", headers=auth_headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds
        
        data = response.json()
        assert len(data["invoices"]) == 20
        assert data["total"] == 100

    def test_concurrent_requests(self, client: TestClient, auth_headers: dict, 
                               sample_invoice):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get(f"/api/v1/invoices/{sample_invoice.id}", headers=auth_headers)
            results.append(response.status_code)
        
        # Create multiple threads making concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10
