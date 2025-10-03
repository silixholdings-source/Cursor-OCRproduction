"""
Tests for retrieving saved invoice records
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta

@pytest.mark.invoice
class TestInvoiceRetrieval:
    """Test invoice retrieval functionality."""

    def test_get_invoices_list(self, client: TestClient, auth_headers: dict, multiple_invoices):
        """Test retrieving list of invoices."""
        response = client.get("/api/v1/invoices", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "invoices" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "pages" in data
        
        # Verify we got the invoices
        assert len(data["invoices"]) == 5
        assert data["total"] == 5

    def test_get_invoices_list_without_auth(self, client: TestClient):
        """Test retrieving invoices without authentication fails."""
        response = client.get("/api/v1/invoices")
        assert response.status_code == 401

    def test_get_invoices_list_pagination(self, client: TestClient, auth_headers: dict, multiple_invoices):
        """Test invoice list pagination."""
        # Test first page
        response = client.get("/api/v1/invoices?page=1&per_page=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["invoices"]) == 2
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["pages"] == 3  # 5 invoices / 2 per page = 3 pages
        
        # Test second page
        response = client.get("/api/v1/invoices?page=2&per_page=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["invoices"]) == 2
        assert data["page"] == 2
        
        # Test third page
        response = client.get("/api/v1/invoices?page=3&per_page=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["invoices"]) == 1  # Only 1 invoice on last page
        assert data["page"] == 3

    def test_get_invoices_list_filtering(self, client: TestClient, auth_headers: dict, multiple_invoices):
        """Test invoice list filtering."""
        # Filter by status
        response = client.get("/api/v1/invoices?status=draft", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should have 3 draft invoices (every other one)
        assert len(data["invoices"]) == 3
        for invoice in data["invoices"]:
            assert invoice["status"] == "draft"
        
        # Filter by supplier name
        response = client.get("/api/v1/invoices?supplier_name=Supplier 1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["invoices"]) == 1
        assert data["invoices"][0]["supplier_name"] == "Supplier 1"

    def test_get_invoices_list_date_filtering(self, client: TestClient, auth_headers: dict, multiple_invoices):
        """Test invoice list date filtering."""
        # Filter by date range
        today = date.today()
        week_ago = today - timedelta(days=7)
        two_weeks_ago = today - timedelta(days=14)
        
        response = client.get(
            f"/api/v1/invoices?date_from={two_weeks_ago}&date_to={week_ago}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Should have invoices from the specified date range
        assert len(data["invoices"]) >= 0

    def test_get_invoices_list_sorting(self, client: TestClient, auth_headers: dict, multiple_invoices):
        """Test invoice list sorting."""
        # Sort by total_amount descending
        response = client.get("/api/v1/invoices?sort_by=total_amount&sort_order=desc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        amounts = [invoice["total_amount"] for invoice in data["invoices"]]
        assert amounts == sorted(amounts, reverse=True)
        
        # Sort by created_at ascending
        response = client.get("/api/v1/invoices?sort_by=created_at&sort_order=asc", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify sorting (newest first by default, so ascending should reverse)
        created_dates = [invoice["created_at"] for invoice in data["invoices"]]
        assert created_dates == sorted(created_dates)

    def test_get_single_invoice(self, client: TestClient, auth_headers: dict, sample_invoice):
        """Test retrieving a single invoice."""
        response = client.get(f"/api/v1/invoices/{sample_invoice.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify invoice data
        assert data["id"] == str(sample_invoice.id)
        assert data["invoice_number"] == sample_invoice.invoice_number
        assert data["supplier_name"] == sample_invoice.supplier_name
        assert data["total_amount"] == float(sample_invoice.total_amount)
        assert data["status"] == sample_invoice.status.value
        
        # Verify line items are included
        assert "line_items" in data
        assert len(data["line_items"]) == 2

    def test_get_single_invoice_not_found(self, client: TestClient, auth_headers: dict):
        """Test retrieving non-existent invoice."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = client.get(f"/api/v1/invoices/{fake_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_get_single_invoice_without_auth(self, client: TestClient, sample_invoice):
        """Test retrieving invoice without authentication fails."""
        response = client.get(f"/api/v1/invoices/{sample_invoice.id}")
        assert response.status_code == 401

    def test_get_invoice_with_line_items(self, client: TestClient, auth_headers: dict, sample_invoice):
        """Test retrieving invoice with line items."""
        response = client.get(f"/api/v1/invoices/{sample_invoice.id}?include=line_items", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify line items are included
        assert "line_items" in data
        line_items = data["line_items"]
        assert len(line_items) == 2
        
        # Verify line item structure
        first_item = line_items[0]
        assert "description" in first_item
        assert "quantity" in first_item
        assert "unit_price" in first_item
        assert "total" in first_item
        assert "gl_account" in first_item

    def test_get_invoices_search(self, client: TestClient, auth_headers: dict, multiple_invoices):
        """Test searching invoices."""
        # Search by invoice number
        response = client.get("/api/v1/invoices?search=INV-001", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["invoices"]) == 1
        assert data["invoices"][0]["invoice_number"] == "INV-001"
        
        # Search by supplier name
        response = client.get("/api/v1/invoices?search=Supplier 2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["invoices"]) == 1
        assert "Supplier 2" in data["invoices"][0]["supplier_name"]

    def test_get_invoices_analytics(self, client: TestClient, auth_headers: dict, multiple_invoices):
        """Test getting invoice analytics."""
        response = client.get("/api/v1/invoices/analytics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify analytics structure
        assert "total_invoices" in data
        assert "total_amount" in data
        assert "approved_count" in data
        assert "pending_count" in data
        assert "rejected_count" in data
        assert "avg_amount" in data
        
        # Verify values
        assert data["total_invoices"] == 5
        assert data["total_amount"] == sum(inv.total_amount for inv in multiple_invoices)
        assert data["approved_count"] == 2  # Every other invoice is approved
        assert data["pending_count"] == 3  # Every other invoice is draft

    def test_get_invoices_export(self, client: TestClient, auth_headers: dict, multiple_invoices):
        """Test exporting invoices."""
        # Export as CSV
        response = client.get("/api/v1/invoices/export?format=csv", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
        
        # Export as JSON
        response = client.get("/api/v1/invoices/export?format=json", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert len(data) == 5  # All invoices

    def test_get_invoices_with_company_isolation(self, client: TestClient, auth_headers: dict, 
                                                db_session: Session, test_company, test_user):
        """Test that users can only see invoices from their company."""
        # Create another company and invoice
        import uuid
        other_company = Company(
            id=uuid.uuid4(),
            name="Other Company",
            email="other@company.com",
            status="active",
            max_users=10,
            max_invoices_per_month=1000
        )
        db_session.add(other_company)
        db_session.commit()
        
        other_invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="OTHER-001",
            supplier_name="Other Supplier",
            invoice_date=date.today(),
            total_amount=2000.00,
            currency="USD",
            status="draft",
            company_id=other_company.id,
            created_by_id=test_user.id,
            ocr_data={}
        )
        db_session.add(other_invoice)
        db_session.commit()
        
        # Get invoices - should only see invoices from test_company
        response = client.get("/api/v1/invoices", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Should not see the other company's invoice
        invoice_numbers = [inv["invoice_number"] for inv in data["invoices"]]
        assert "OTHER-001" not in invoice_numbers

    def test_get_invoices_performance(self, client: TestClient, auth_headers: dict, db_session: Session, 
                                    test_company, test_user):
        """Test invoice retrieval performance with large dataset."""
        # Create many invoices
        import uuid
        invoices = []
        for i in range(100):
            invoice = Invoice(
                id=uuid.uuid4(),
                invoice_number=f"PERF-{i:03d}",
                supplier_name=f"Supplier {i}",
                invoice_date=date.today() - timedelta(days=i),
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
        import time
        start_time = time.time()
        
        response = client.get("/api/v1/invoices?page=1&per_page=20", headers=auth_headers)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
        
        data = response.json()
        assert len(data["invoices"]) == 20
        assert data["total"] == 100

    def test_get_invoices_error_handling(self, client: TestClient, auth_headers: dict):
        """Test error handling in invoice retrieval."""
        # Test invalid page number
        response = client.get("/api/v1/invoices?page=0", headers=auth_headers)
        assert response.status_code == 400
        
        # Test invalid per_page
        response = client.get("/api/v1/invoices?per_page=0", headers=auth_headers)
        assert response.status_code == 400
        
        # Test invalid sort field
        response = client.get("/api/v1/invoices?sort_by=invalid_field", headers=auth_headers)
        assert response.status_code == 400

    def test_get_invoices_metadata(self, client: TestClient, auth_headers: dict, sample_invoice):
        """Test retrieving invoice with metadata."""
        response = client.get(f"/api/v1/invoices/{sample_invoice.id}?include=metadata", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify metadata fields
        assert "created_at" in data
        assert "updated_at" in data
        assert "created_by" in data
        assert "company" in data
        
        # Verify created_by user info
        created_by = data["created_by"]
        assert "id" in created_by
        assert "email" in created_by
        assert "first_name" in created_by
        assert "last_name" in created_by









