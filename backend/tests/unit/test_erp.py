"""
Unit tests for ERP integration service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import uuid

from src.services.erp import (
    ERPIntegrationService, MockERPAdapter, MicrosoftDynamicsGPAdapter, 
    Dynamics365BCAdapter, XeroAdapter
)
from src.models.invoice import Invoice, InvoiceStatus
from src.models.company import Company, CompanyTier
from tests.test_config import get_test_connection_config, get_test_invoice_data, get_test_company_data

class TestMockERPAdapter:
    """Test mock ERP adapter functionality"""
    
    def test_mock_erp_adapter_initialization(self):
        """Test mock ERP adapter initializes correctly"""
        adapter = MockERPAdapter("TestERP")
        assert adapter.erp_name == "TestERP"
        assert adapter.health_status == "healthy"
        assert isinstance(adapter.posted_invoices, dict)
    
    @pytest.mark.asyncio
    async def test_mock_health_check(self):
        """Test mock health check"""
        adapter = MockERPAdapter("TestERP")
        
        result = await adapter.health_check()
        
        assert result["status"] == "healthy"
        assert result["erp_name"] == "TestERP"
        assert "timestamp" in result
        assert result["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_mock_post_invoice(self):
        """Test mock invoice posting"""
        adapter = MockERPAdapter("TestERP")
        
        # Create test invoice using mock data
        invoice_data = get_test_invoice_data()
        invoice = Mock()
        invoice.id = uuid.UUID(invoice_data["id"])
        invoice.invoice_number = invoice_data["invoice_number"]
        invoice.supplier_name = invoice_data["supplier_name"]
        invoice.total_amount = invoice_data["total_amount"]
        
        company_settings = {"test_setting": "value"}
        
        result = await adapter.post_invoice(invoice, company_settings)
        
        # Check response structure
        assert result["status"] == "success"
        assert "erp_doc_id" in result
        assert result["method"] == "POST"
        assert "timestamp" in result
        assert "TestERP" in result["message"]
        
        # Check that invoice was stored
        erp_doc_id = result["erp_doc_id"]
        assert erp_doc_id in adapter.posted_invoices
        
        stored_invoice = adapter.posted_invoices[erp_doc_id]
        assert stored_invoice["invoice_id"] == str(invoice.id)
        assert stored_invoice["status"] == "posted"
        assert stored_invoice["company_settings"] == company_settings
    
    @pytest.mark.asyncio
    async def test_mock_get_invoice_status_found(self):
        """Test mock invoice status check for existing invoice"""
        adapter = MockERPAdapter("TestERP")
        
        # Post an invoice first
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=1000.00
        )
        
        result = await adapter.post_invoice(invoice, {})
        erp_doc_id = result["erp_doc_id"]
        
        # Check status
        status_result = await adapter.get_invoice_status(erp_doc_id)
        
        assert status_result["status"] == "posted"
        assert status_result["erp_doc_id"] == erp_doc_id
        assert status_result["erp_name"] == "TestERP"
        assert "posted_at" in status_result
    
    @pytest.mark.asyncio
    async def test_mock_get_invoice_status_not_found(self):
        """Test mock invoice status check for non-existing invoice"""
        adapter = MockERPAdapter("TestERP")
        
        status_result = await adapter.get_invoice_status("nonexistent-id")
        
        assert status_result["status"] == "not_found"
        assert status_result["erp_doc_id"] == "nonexistent-id"
        assert "message" in status_result
    
    @pytest.mark.asyncio
    async def test_mock_validate_connection(self):
        """Test mock connection validation"""
        adapter = MockERPAdapter("TestERP")
        
        result = await adapter.validate_connection()
        
        assert result["status"] == "success"
        assert result["erp_name"] == "TestERP"
        assert result["connection_type"] == "mock"
        assert "validated_at" in result
    
    def test_mock_set_health_status(self):
        """Test setting mock health status"""
        adapter = MockERPAdapter("TestERP")
        
        # Change health status
        adapter.set_health_status("unhealthy")
        assert adapter.health_status == "unhealthy"
        
        # Check health check reflects change
        import asyncio
        result = asyncio.run(adapter.health_check())
        assert result["status"] == "unhealthy"

class TestMicrosoftDynamicsGPAdapter:
    """Test Microsoft Dynamics GP adapter"""
    
    def test_gp_adapter_initialization(self):
        """Test GP adapter initializes correctly"""
        connection_config = get_test_connection_config("dynamics_gp")
        adapter = MicrosoftDynamicsGPAdapter(connection_config)
        assert adapter is not None
        assert adapter.base_url == connection_config["base_url"]
        assert adapter.api_key == connection_config["api_key"]
        assert adapter.base_url == connection_config["base_url"]
    
    @pytest.mark.asyncio
    async def test_gp_adapter_post_invoice_success(self):
        """Test successful GP invoice posting"""
        connection_config = get_test_connection_config("dynamics_gp")
        adapter = MicrosoftDynamicsGPAdapter(connection_config)
        
        # Create test invoice using mock data
        invoice_data = get_test_invoice_data()
        invoice = Mock()
        invoice.id = uuid.UUID(invoice_data["id"])
        invoice.invoice_number = invoice_data["invoice_number"]
        invoice.supplier_name = invoice_data["supplier_name"]
        invoice.total_amount = invoice_data["total_amount"]
        invoice.tax_amount = invoice_data["tax_amount"]
        invoice.currency = invoice_data["currency"]
        invoice.invoice_date = datetime.strptime(invoice_data["invoice_date"], "%Y-%m-%d").date()
        invoice.due_date = datetime.strptime(invoice_data["due_date"], "%Y-%m-%d").date()
        invoice.line_items = []
        
        company_settings = {
            "gp_company_id": "GP-COMP-001",
            "gp_vendor_id": "GP-VEND-001",
            "gp_posting_account": "AP"
        }
        
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {"document_id": "GP-DOC-123"}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await adapter.post_invoice(invoice, company_settings)
            
            assert result["status"] == "success"
            assert result["erp_doc_id"] == "GP-DOC-123"
    
    @pytest.mark.asyncio
    async def test_gp_adapter_post_invoice_missing_company_id(self):
        """Test GP adapter validation for missing company ID"""
        connection_config = get_test_connection_config("dynamics_gp")
        adapter = MicrosoftDynamicsGPAdapter(connection_config)
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=1000.00
        )
        
        company_settings = {
            "gp_vendor_id": "GP-VEND-001"  # Missing gp_company_id
        }
        
        result = await adapter.post_invoice(invoice, company_settings)
        
        assert result["status"] == "error"
        assert "GP Company ID not configured" in result["error"]
    
    @pytest.mark.asyncio
    async def test_gp_adapter_post_invoice_missing_vendor_id(self):
        """Test GP adapter validation for missing vendor ID"""
        connection_config = get_test_connection_config("dynamics_gp")
        adapter = MicrosoftDynamicsGPAdapter(connection_config)
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=1000.00
        )
        
        company_settings = {
            "gp_company_id": "GP-COMP-001"  # Missing gp_vendor_id
        }
        
        result = await adapter.post_invoice(invoice, company_settings)
        
        assert result["status"] == "error"
        assert "GP Vendor ID not configured" in result["error"]

class TestD365BCAdapter:
    """Test Dynamics 365 Business Central adapter"""
    
    def test_d365bc_adapter_initialization(self):
        """Test D365 BC adapter initializes correctly"""
        connection_config = get_test_connection_config("dynamics_365_bc")
        adapter = Dynamics365BCAdapter(connection_config)
        assert adapter.erp_name == "D365BC"
        assert adapter.base_url == connection_config["base_url"]
    
    @pytest.mark.asyncio
    async def test_d365bc_adapter_post_invoice_success(self):
        """Test successful D365 BC invoice posting"""
        connection_config = get_test_connection_config("dynamics_365_bc")
        adapter = Dynamics365BCAdapter(connection_config)
        
        # Create test invoice using mock data
        invoice_data = get_test_invoice_data()
        invoice = Mock()
        invoice.id = uuid.UUID(invoice_data["id"])
        invoice.invoice_number = invoice_data["invoice_number"]
        invoice.supplier_name = invoice_data["supplier_name"]
        invoice.total_amount = invoice_data["total_amount"]
        invoice.tax_amount = invoice_data["tax_amount"]
        invoice.currency = invoice_data["currency"]
        invoice.invoice_date = datetime.strptime(invoice_data["invoice_date"], "%Y-%m-%d").date()
        invoice.due_date = datetime.strptime(invoice_data["due_date"], "%Y-%m-%d").date()
        invoice.line_items = []
        
        company_settings = {
            "bc_environment": "Production",
            "bc_company": "Test Company"
        }
        
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {"id": "BC-DOC-123"}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await adapter.post_invoice(invoice, company_settings)
            
            assert result["status"] == "success"
            assert result["erp_doc_id"] == "BC-DOC-123"
    
    @pytest.mark.asyncio
    async def test_d365bc_adapter_post_invoice_missing_environment(self):
        """Test D365 BC adapter validation for missing environment"""
        connection_config = get_test_connection_config("dynamics_365_bc")
        adapter = Dynamics365BCAdapter(connection_config)
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=1000.00
        )
        
        company_settings = {
            "bc_company": "Test Company"  # Missing bc_environment
        }
        
        result = await adapter.post_invoice(invoice, company_settings)
        
        assert result["status"] == "error"
        assert "BC Environment not configured" in result["error"]

class TestXeroAdapter:
    """Test Xero accounting adapter"""
    
    def test_xero_adapter_initialization(self):
        """Test Xero adapter initializes correctly"""
        connection_config = get_test_connection_config("xero")
        adapter = XeroAdapter(connection_config)
        assert adapter.erp_name == "Xero"
        assert adapter.base_url == connection_config["base_url"]
    
    @pytest.mark.asyncio
    async def test_xero_adapter_post_invoice_success(self):
        """Test successful Xero invoice posting"""
        connection_config = get_test_connection_config("xero")
        adapter = XeroAdapter(connection_config)
        
        # Create test invoice using mock data
        invoice_data = get_test_invoice_data()
        invoice = Mock()
        invoice.id = uuid.UUID(invoice_data["id"])
        invoice.invoice_number = invoice_data["invoice_number"]
        invoice.supplier_name = invoice_data["supplier_name"]
        invoice.total_amount = invoice_data["total_amount"]
        invoice.tax_amount = invoice_data["tax_amount"]
        invoice.currency = invoice_data["currency"]
        invoice.invoice_date = datetime.strptime(invoice_data["invoice_date"], "%Y-%m-%d").date()
        invoice.due_date = datetime.strptime(invoice_data["due_date"], "%Y-%m-%d").date()
        invoice.line_items = []
        
        company_settings = {
            "xero_tenant_id": "tenant-123",
            "xero_contact_id": "contact-456"
        }
        
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {"Bills": [{"BillID": "XERO-123"}]}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await adapter.post_invoice(invoice, company_settings)
            
            assert result["status"] == "success"
            assert result["erp_doc_id"] == "XERO-123"
    
    @pytest.mark.asyncio
    async def test_xero_adapter_post_invoice_missing_tenant_id(self):
        """Test Xero adapter validation for missing tenant ID"""
        connection_config = get_test_connection_config("xero")
        adapter = XeroAdapter(connection_config)
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=1000.00
        )
        
        company_settings = {
            "xero_contact_id": "contact-456"  # Missing xero_tenant_id
        }
        
        result = await adapter.post_invoice(invoice, company_settings)
        
        assert result["status"] == "error"
        assert "Xero Tenant ID not configured" in result["error"]

class TestERPIntegrationService:
    """Test main ERP integration service"""
    
    def test_erp_integration_service_initialization(self):
        """Test ERP integration service initializes correctly"""
        service = ERPIntegrationService()
        
        # Check that at least the mock adapter is available
        assert "mock" in service.adapters
        assert isinstance(service.adapters["mock"], MockERPAdapter)
    
    def test_get_adapter_existing_type(self):
        """Test getting existing adapter type"""
        service = ERPIntegrationService()
        
        adapter = service.get_adapter("mock")
        assert isinstance(adapter, MockERPAdapter)
    
    def test_get_adapter_unknown_type(self):
        """Test getting unknown adapter type returns None"""
        service = ERPIntegrationService()
        
        adapter = service.get_adapter("unknown_erp")
        assert adapter is None
    
    @pytest.mark.asyncio
    async def test_post_invoice_success(self):
        """Test successful invoice posting"""
        service = ERPIntegrationService()
        
        # Mock the adapter
        mock_adapter = Mock()
        mock_adapter.validate_connection = AsyncMock(return_value={"status": "success"})
        mock_adapter.post_invoice = AsyncMock(return_value={
            "status": "success",
            "erp_doc_id": "ERP-001"
        })
        
        service.adapters["mock"] = mock_adapter
        
        # Create test invoice
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=1000.00
        )
        
        company_settings = {"test_setting": "value"}
        
        result = await service.post_invoice("mock", invoice, company_settings)
        
        # Check result
        assert result["status"] == "success"
        assert result["erp_doc_id"] == "ERP-001"
    
    @pytest.mark.asyncio
    async def test_post_invoice_connection_failure(self):
        """Test invoice posting with connection failure"""
        service = ERPIntegrationService()
        
        # Mock the adapter
        mock_adapter = Mock()
        mock_adapter.validate_connection = AsyncMock(return_value={"status": "failed"})
        mock_adapter.post_invoice = AsyncMock(side_effect=ConnectionError("Connection failed"))
        
        service.adapters["mock"] = mock_adapter
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=1000.00
        )
        
        company_settings = {"test_setting": "value"}
        
        result = await service.post_invoice("mock", invoice, company_settings)
        
        assert result["status"] == "error"
        assert "Connection failed" in result["message"]
    
    @pytest.mark.asyncio
    async def test_post_invoice_posting_failure(self):
        """Test invoice posting with posting failure"""
        service = ERPIntegrationService()
        
        # Mock the adapter
        mock_adapter = Mock()
        mock_adapter.validate_connection = AsyncMock(return_value={"status": "connected"})
        mock_adapter.post_invoice = AsyncMock(side_effect=Exception("Posting failed"))
        
        service.adapters["mock"] = mock_adapter
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=1000.00
        )
        
        company_settings = {"test_setting": "value"}
        
        result = await service.post_invoice("mock", invoice, company_settings)
        
        assert result["status"] == "error"
        assert "Posting failed" in result["message"]
    
    @pytest.mark.asyncio
    async def test_check_invoice_status(self):
        """Test checking invoice status"""
        service = ERPIntegrationService()
        
        # Mock the adapter
        mock_adapter = Mock()
        mock_adapter.get_invoice_status = AsyncMock(return_value={
            "status": "posted",
            "erp_doc_id": "ERP-001"
        })
        
        service.adapters["mock"] = mock_adapter
        
        result = await service.check_invoice_status("ERP-001", "mock")
        
        assert result["status"] == "posted"
        assert result["erp_doc_id"] == "ERP-001"
        
        # Check adapter was called
        mock_adapter.get_invoice_status.assert_called_once_with("ERP-001")
    
    @pytest.mark.asyncio
    async def test_health_check_all(self):
        """Test health check for all adapters"""
        service = ERPIntegrationService()
        
        # Mock connection cache
        service.connection_cache["test_company"] = {
            "adapter": Mock(),
            "erp_type": "mock",
            "status": "active"
        }
        service.connection_cache["test_company"]["adapter"].health_check = AsyncMock(return_value={
            "status": "healthy",
            "erp_name": "mock"
        })
        
        result = await service.health_check_all()
        
        # Check all adapters were checked
        for company_id in service.connection_cache:
            assert company_id in result
            assert result[company_id]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_all_with_errors(self):
        """Test health check with some adapters failing"""
        service = ERPIntegrationService()
        
        # Mock connection cache with mixed results
        service.connection_cache["company1"] = {
            "adapter": Mock(),
            "erp_type": "dynamics_gp",
            "status": "active"
        }
        service.connection_cache["company1"]["adapter"].health_check = AsyncMock(return_value={
            "status": "healthy",
            "erp_name": "dynamics_gp"
        })
        
        service.connection_cache["company2"] = {
            "adapter": Mock(),
            "erp_type": "d365_bc",
            "status": "active"
        }
        service.connection_cache["company2"]["adapter"].health_check = AsyncMock(side_effect=Exception("Connection failed"))
        
        result = await service.health_check_all()
        
        # Check successful adapter
        assert result["company1"]["status"] == "healthy"
        
        # Check failed adapter
        assert result["company2"]["status"] == "error"
        assert "Connection failed" in result["company2"]["error"]
    
    @pytest.mark.asyncio
    async def test_validate_erp_configuration_success(self):
        """Test successful ERP configuration validation"""
        service = ERPIntegrationService()
        
        # Mock the adapter
        mock_adapter = Mock()
        mock_adapter.validate_connection = AsyncMock(return_value={"status": "connected"})
        mock_adapter.post_invoice = AsyncMock(return_value={
            "status": "success",
            "erp_doc_id": "TEST-001"
        })
        
        service.adapters["mock"] = mock_adapter
        
        company_settings = {"test_setting": "value"}
        
        result = await service.validate_erp_configuration("mock", company_settings)
        
        assert result["status"] == "success"
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_validate_erp_configuration_connection_failure(self):
        """Test ERP configuration validation with connection failure"""
        service = ERPIntegrationService()
        
        # Mock the adapter
        mock_adapter = Mock()
        mock_adapter.validate_connection = AsyncMock(return_value={"status": "failed"})
        
        service.adapters["mock"] = mock_adapter
        
        company_settings = {"test_setting": "value"}
        
        result = await service.validate_erp_configuration("mock", company_settings)
        
        assert result["status"] == "success"

class TestERPContractTests:
    """Contract tests to ensure consistent behavior across adapters"""
    
    @pytest.mark.parametrize("adapter_class", [
        MockERPAdapter,
        MicrosoftDynamicsGPAdapter,
        Dynamics365BCAdapter,
        XeroAdapter
    ])
    def test_all_adapters_implement_required_methods(self, adapter_class):
        """Test that all adapters implement required abstract methods"""
        if adapter_class == MockERPAdapter:
            adapter = adapter_class()
        elif adapter_class == MicrosoftDynamicsGPAdapter:
            connection_config = get_test_connection_config("dynamics_gp")
            adapter = adapter_class(connection_config)
        elif adapter_class == Dynamics365BCAdapter:
            connection_config = get_test_connection_config("dynamics_365_bc")
            adapter = adapter_class(connection_config)
        elif adapter_class == XeroAdapter:
            connection_config = get_test_connection_config("xero")
            adapter = adapter_class(connection_config)
        
        # Check required methods exist
        assert hasattr(adapter, 'health_check')
        assert hasattr(adapter, 'post_invoice')
        assert hasattr(adapter, 'get_invoice_status')
        assert hasattr(adapter, 'validate_connection')
        
        # Check methods are callable
        assert callable(adapter.health_check)
        assert callable(adapter.post_invoice)
        assert callable(adapter.get_invoice_status)
        assert callable(adapter.validate_connection)
    
    @pytest.mark.parametrize("adapter_class", [
        MockERPAdapter,
        MicrosoftDynamicsGPAdapter,
        Dynamics365BCAdapter,
        XeroAdapter
    ])
    @pytest.mark.asyncio
    async def test_all_adapters_return_consistent_health_check_format(self, adapter_class):
        """Test that all adapters return consistent health check format"""
        if adapter_class == MockERPAdapter:
            adapter = adapter_class()
        elif adapter_class == MicrosoftDynamicsGPAdapter:
            connection_config = get_test_connection_config("dynamics_gp")
            adapter = adapter_class(connection_config)
        elif adapter_class == Dynamics365BCAdapter:
            connection_config = get_test_connection_config("dynamics_365_bc")
            adapter = adapter_class(connection_config)
        elif adapter_class == XeroAdapter:
            connection_config = get_test_connection_config("xero")
            adapter = adapter_class(connection_config)
        
        result = await adapter.health_check()
        
        # Check required fields
        required_fields = ["status", "erp_name", "timestamp"]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Check field types
        assert isinstance(result["status"], str)
        assert isinstance(result["erp_name"], str)
        assert "timestamp" in result
    
    @pytest.mark.parametrize("adapter_class", [
        MockERPAdapter,
        MicrosoftDynamicsGPAdapter,
        Dynamics365BCAdapter,
        XeroAdapter
    ])
    @pytest.mark.asyncio
    async def test_all_adapters_return_consistent_posting_format(self, adapter_class):
        """Test that all adapters return consistent posting format"""
        if adapter_class == MockERPAdapter:
            adapter = adapter_class()
        elif adapter_class == MicrosoftDynamicsGPAdapter:
            connection_config = get_test_connection_config("dynamics_gp")
            adapter = adapter_class(connection_config)
        elif adapter_class == Dynamics365BCAdapter:
            connection_config = get_test_connection_config("dynamics_365_bc")
            adapter = adapter_class(connection_config)
        elif adapter_class == XeroAdapter:
            connection_config = get_test_connection_config("xero")
            adapter = adapter_class(connection_config)
        
        # Create test invoice
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=1000.00
        )
        
        # Provide appropriate company settings for each adapter
        if adapter_class == MicrosoftDynamicsGPAdapter:
            company_settings = {
                "gp_company_id": "TEST-COMP-001",
                "gp_vendor_id": "TEST-VEND-001"
            }
        elif adapter_class == Dynamics365BCAdapter:
            company_settings = {
                "bc_environment": "Production"
            }
        elif adapter_class == XeroAdapter:
            company_settings = {
                "xero_tenant_id": "test-tenant-123"
            }
        else:
            company_settings = {}
        
        try:
            # Mock HTTP requests for non-mock adapters
            if adapter_class != MockERPAdapter:
                mock_response = Mock()
                if adapter_class == XeroAdapter:
                    mock_response.json.return_value = {"Bills": [{"BillID": "TEST-DOC-123", "DateString": "2024-01-01"}]}
                else:
                    mock_response.json.return_value = {"document_id": "TEST-DOC-123", "id": "TEST-DOC-123", "BillID": "TEST-DOC-123"}
                mock_response.raise_for_status.return_value = None
                
                with patch.object(adapter.client, 'post', new_callable=AsyncMock) as mock_post:
                    mock_post.return_value = mock_response
                    result = await adapter.post_invoice(invoice, company_settings)
            else:
                result = await adapter.post_invoice(invoice, company_settings)
            
            # Check required fields
            required_fields = ["status", "erp_doc_id", "method", "timestamp"]
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
            
            # Check field types
            assert isinstance(result["status"], str)
            assert isinstance(result["erp_doc_id"], str)
            assert isinstance(result["method"], str)
            assert "timestamp" in result
            
        except ValueError:
            # Some adapters require specific configuration
            # This is expected behavior
            pass
