"""
Performance tests for the FastAPI backend
"""
import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor
import statistics

@pytest.mark.slow
@pytest.mark.performance
class TestPerformance:
    """Performance tests for the API."""

    def test_invoice_list_performance(self, client: TestClient, auth_headers: dict, 
                                    db_session: Session, test_company, test_user):
        """Test invoice list retrieval performance with large dataset."""
        from tests.utils import create_multiple_test_invoices
        
        # Create 1000 invoices
        invoices = create_multiple_test_invoices(db_session, test_company.id, test_user.id, 1000)
        
        # Test pagination performance
        start_time = time.time()
        response = client.get("/api/v1/invoices?page=1&per_page=20", headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0, f"Response time {response_time}s exceeds 1s limit"
        
        data = response.json()
        assert len(data["invoices"]) == 20
        assert data["total"] == 1000

    def test_concurrent_requests_performance(self, client: TestClient, auth_headers: dict, 
                                           sample_invoice):
        """Test performance under concurrent load."""
        def make_request():
            response = client.get(f"/api/v1/invoices/{sample_invoice.id}", headers=auth_headers)
            return response.status_code, time.time()
        
        # Make 100 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        assert all(status == 200 for status in status_codes)
        
        # Calculate response time statistics
        response_times = [result[1] for result in results]
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 0.5, f"Average response time {avg_response_time}s exceeds 0.5s limit"
        assert max_response_time < 2.0, f"Max response time {max_response_time}s exceeds 2s limit"

    def test_database_query_performance(self, client: TestClient, auth_headers: dict, 
                                      db_session: Session, test_company, test_user):
        """Test database query performance."""
        from tests.utils import create_multiple_test_invoices
        
        # Create test data
        invoices = create_multiple_test_invoices(db_session, test_company.id, test_user.id, 500)
        
        # Test different query patterns
        queries = [
            "/api/v1/invoices",
            "/api/v1/invoices?status=draft",
            "/api/v1/invoices?supplier_name=Supplier 1",
            "/api/v1/invoices?sort_by=total_amount&sort_order=desc",
            "/api/v1/invoices/analytics"
        ]
        
        for query in queries:
            start_time = time.time()
            response = client.get(query, headers=auth_headers)
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 2.0, f"Query {query} took {response_time}s, exceeds 2s limit"

    def test_file_upload_performance(self, client: TestClient, auth_headers: dict):
        """Test file upload performance."""
        from tests.utils import create_test_file, cleanup_test_file
        
        # Create test file
        test_file = create_test_file(b"x" * (1024 * 1024))  # 1MB file
        
        try:
            start_time = time.time()
            
            with open(test_file, "rb") as f:
                files = {"file": ("test.pdf", f, "application/pdf")}
                data = {"company_id": "test-company"}
                
                response = client.post(
                    "/api/v1/ocr/upload",
                    files=files,
                    data=data,
                    headers=auth_headers
                )
            
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 5.0, f"File upload took {response_time}s, exceeds 5s limit"
            
        finally:
            cleanup_test_file(test_file)

    def test_memory_usage(self, client: TestClient, auth_headers: dict, 
                         db_session: Session, test_company, test_user):
        """Test memory usage with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        from tests.utils import create_multiple_test_invoices
        invoices = create_multiple_test_invoices(db_session, test_company.id, test_user.id, 1000)
        
        # Perform operations
        for i in range(10):
            response = client.get("/api/v1/invoices", headers=auth_headers)
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100, f"Memory usage increased by {memory_increase}MB, exceeds 100MB limit"

    def test_api_response_times(self, client: TestClient, auth_headers: dict, sample_invoice):
        """Test API response times for different endpoints."""
        endpoints = [
            ("/api/v1/health", "GET"),
            ("/api/v1/auth/me", "GET"),
            (f"/api/v1/invoices/{sample_invoice.id}", "GET"),
            ("/api/v1/invoices", "GET"),
            ("/api/v1/invoices/analytics", "GET")
        ]
        
        for endpoint, method in endpoints:
            start_time = time.time()
            
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers)
            else:
                response = client.post(endpoint, headers=auth_headers)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code in [200, 201], f"Endpoint {endpoint} returned {response.status_code}"
            assert response_time < 1.0, f"Endpoint {endpoint} took {response_time}s, exceeds 1s limit"

    def test_bulk_operations_performance(self, client: TestClient, auth_headers: dict, 
                                       db_session: Session, test_company, test_user):
        """Test performance of bulk operations."""
        from tests.utils import create_test_invoice
        
        # Test bulk invoice creation
        start_time = time.time()
        
        invoices_data = []
        for i in range(100):
            invoice_data = {
                "invoice_number": f"BULK-{i:03d}",
                "supplier_name": f"Bulk Supplier {i}",
                "invoice_date": "2024-01-15",
                "total_amount": 1000.00 + i,
                "currency": "USD",
                "line_items": [
                    {
                        "description": f"Bulk Item {i}",
                        "quantity": 1,
                        "unit_price": 1000.00 + i,
                        "total": 1000.00 + i
                    }
                ]
            }
            invoices_data.append(invoice_data)
        
        # Create invoices one by one (simulating API calls)
        for invoice_data in invoices_data:
            response = client.post("/api/v1/invoices", json=invoice_data, headers=auth_headers)
            assert response.status_code == 201
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should create 100 invoices in less than 30 seconds
        assert total_time < 30.0, f"Bulk creation took {total_time}s, exceeds 30s limit"

    def test_search_performance(self, client: TestClient, auth_headers: dict, 
                              db_session: Session, test_company, test_user):
        """Test search performance with large dataset."""
        from tests.utils import create_multiple_test_invoices
        
        # Create test data
        invoices = create_multiple_test_invoices(db_session, test_company.id, test_user.id, 1000)
        
        # Test different search patterns
        search_queries = [
            "TEST-001",
            "Supplier 1",
            "1000",
            "TEST"
        ]
        
        for query in search_queries:
            start_time = time.time()
            response = client.get(f"/api/v1/invoices?search={query}", headers=auth_headers)
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            assert response_time < 2.0, f"Search for '{query}' took {response_time}s, exceeds 2s limit"

    def test_export_performance(self, client: TestClient, auth_headers: dict, 
                              db_session: Session, test_company, test_user):
        """Test export performance with large dataset."""
        from tests.utils import create_multiple_test_invoices
        
        # Create test data
        invoices = create_multiple_test_invoices(db_session, test_company.id, test_user.id, 500)
        
        # Test CSV export
        start_time = time.time()
        response = client.get("/api/v1/invoices/export?format=csv", headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        csv_time = end_time - start_time
        assert csv_time < 5.0, f"CSV export took {csv_time}s, exceeds 5s limit"
        
        # Test JSON export
        start_time = time.time()
        response = client.get("/api/v1/invoices/export?format=json", headers=auth_headers)
        end_time = time.time()
        
        assert response.status_code == 200
        json_time = end_time - start_time
        assert json_time < 3.0, f"JSON export took {json_time}s, exceeds 3s limit"

    def test_error_handling_performance(self, client: TestClient, auth_headers: dict):
        """Test that error handling doesn't significantly impact performance."""
        # Test with invalid requests
        invalid_requests = [
            ("/api/v1/invoices/invalid-id", "GET"),
            ("/api/v1/invoices?page=0", "GET"),
            ("/api/v1/invoices?per_page=0", "GET"),
            ("/api/v1/invoices?sort_by=invalid_field", "GET")
        ]
        
        for endpoint, method in invalid_requests:
            start_time = time.time()
            
            if method == "GET":
                response = client.get(endpoint, headers=auth_headers)
            else:
                response = client.post(endpoint, headers=auth_headers)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Error responses should still be fast
            assert response.status_code in [400, 404, 422], f"Expected error status for {endpoint}"
            assert response_time < 0.5, f"Error handling for {endpoint} took {response_time}s, exceeds 0.5s limit"









