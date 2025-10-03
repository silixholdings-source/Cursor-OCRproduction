"""
Unit tests for ERP integration functionality
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from decimal import Decimal

from src.services.erp import (
    ERPAdapter, 
    MockERPAdapter, 
    MicrosoftDynamicsGPAdapter,
    ERPIntegrationService
)
from src.models.invoice import Invoice, InvoiceStatus
from src.models.user import User, UserRole


class TestERPAdapter:
    """Test base ERP adapter functionality"""
    
    def test_erp_adapter_abstract_methods(self):
        """Test that ERPAdapter is abstract and cannot be instantiated"""
        with pytest.raises(TypeError):
            ERPAdapter()


class TestMockERPAdapter:
    """Test mock ERP adapter"""
    
    @pytest.fixture
    def mock_adapter(self):
        return MockERPAdapter("TestERP")
    
    @pytest.fixture
    def sample_invoice(self):
        return Invoice(
            id="test-id-123",
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=Decimal("1000.00"),
            currency="USD"
        )
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_adapter):
        """Test mock health check"""
        result = await mock_adapter.health_check()
        
        assert result["status"] == "healthy"
        assert result["erp_name"] == "TestERP"
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_post_invoice(self, mock_adapter, sample_invoice):
        """Test mock invoice posting"""
        company_settings = {"company_id": "COMPANY001"}
        
        result = await mock_adapter.post_invoice(sample_invoice, company_settings)
        
        assert result["status"] == "success"
        assert "erp_doc_id" in result
        assert result["erp_doc_id"].startswith("TestERP")
        assert result["message"] == "Invoice successfully posted to TestERP"
    
    @pytest.mark.asyncio
    async def test_get_invoice_status(self, mock_adapter, sample_invoice):
        """Test mock invoice status retrieval"""
        company_settings = {"company_id": "COMPANY001"}
        
        # First post an invoice
        post_result = await mock_adapter.post_invoice(sample_invoice, company_settings)
        erp_doc_id = post_result["erp_doc_id"]
        
        # Then get its status
        status_result = await mock_adapter.get_invoice_status(erp_doc_id)
        
        assert status_result["status"] == "posted"
        assert status_result["erp_doc_id"] == erp_doc_id
        assert status_result["erp_name"] == "TestERP"
    
    @pytest.mark.asyncio
    async def test_get_invoice_status_not_found(self, mock_adapter):
        """Test getting status for non-existent invoice"""
        result = await mock_adapter.get_invoice_status("non-existent-id")
        
        assert result["status"] == "not_found"
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_validate_connection(self, mock_adapter):
        """Test mock connection validation"""
        result = await mock_adapter.validate_connection()
        
        assert result["status"] == "success"
        assert "message" in result


class TestMicrosoftDynamicsGPAdapter:
    """Test Microsoft Dynamics GP adapter"""
    
    @pytest.fixture
    def connection_config(self):
        return {
            "base_url": "https://api.dynamicsgp.test.com",
            "api_key": "test-api-key",
            "company_id": "COMPANY001",
            "timeout": 30
        }
    
    @pytest.fixture
    def sample_invoice(self):
        return Invoice(
            id="test-id-123",
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=Decimal("1000.00"),
            currency="USD",
            invoice_date=datetime.now().date(),
            subtotal=Decimal("1000.00"),
            total_with_tax=Decimal("1000.00")
        )
    
    def test_init_valid_config(self, connection_config):
        """Test adapter initialization with valid config"""
        adapter = MicrosoftDynamicsGPAdapter(connection_config)
        
        assert adapter.base_url == connection_config["base_url"]
        assert adapter.api_key == connection_config["api_key"]
        assert adapter.company_id == connection_config["company_id"]
        assert adapter.timeout == connection_config["timeout"]
    
    def test_init_missing_config(self):
        """Test adapter initialization with missing config"""
        incomplete_config = {"base_url": "https://test.com"}
        
        with pytest.raises(ValueError, match="Missing required Dynamics GP connection configuration"):
            MicrosoftDynamicsGPAdapter(incomplete_config)
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, connection_config):
        """Test successful health check"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"version": "18.3.1234.0"}
            mock_get.return_value = mock_response
            
            adapter = MicrosoftDynamicsGPAdapter(connection_config)
            result = await adapter.health_check()
            
            assert result["status"] == "healthy"
            assert result["erp_name"] == "Microsoft Dynamics GP"
            assert result["company_id"] == "COMPANY001"
            assert result["version"] == "18.3.1234.0"
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, connection_config):
        """Test failed health check"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")
            
            adapter = MicrosoftDynamicsGPAdapter(connection_config)
            result = await adapter.health_check()
            
            assert result["status"] == "unhealthy"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_post_invoice_success(self, connection_config, sample_invoice):
        """Test successful invoice posting"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"document_id": "GP-001-123"}
            mock_post.return_value = mock_response
            
            adapter = MicrosoftDynamicsGPAdapter(connection_config)
            company_settings = {
                "gp_company_id": "COMPANY001",
                "gp_vendor_id": "VENDOR001"
            }
            
            result = await adapter.post_invoice(sample_invoice, company_settings)
            
            assert result["status"] == "success"
            assert result["erp_doc_id"] == "GP-001-123"
            assert "GP" in result["message"]
    
    @pytest.mark.asyncio
    async def test_post_invoice_failure(self, connection_config, sample_invoice):
        """Test failed invoice posting"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = Exception("Posting failed")
            
            adapter = MicrosoftDynamicsGPAdapter(connection_config)
            company_settings = {"company_id": "COMPANY001"}
            
            result = await adapter.post_invoice(sample_invoice, company_settings)
            
            assert result["status"] == "error"
            assert "error" in result
    
    def test_transform_to_gp_format(self, connection_config, sample_invoice):
        """Test invoice transformation to GP format"""
        adapter = MicrosoftDynamicsGPAdapter(connection_config)
        company_settings = {"company_id": "COMPANY001"}
        
        gp_format = adapter._transform_to_gp_format(sample_invoice, company_settings)
        
        assert gp_format["invoice_number"] == "INV-001"
        assert gp_format["total_amount"] == 1000.0
        assert gp_format["currency_id"] == "USD"
        assert "vendor_id" in gp_format
    
    def test_get_or_create_vendor_id(self, connection_config):
        """Test vendor ID generation"""
        adapter = MicrosoftDynamicsGPAdapter(connection_config)
        
        vendor_id = adapter._get_or_create_vendor_id("Test Supplier Corp")
        
        assert vendor_id.startswith("VENDOR-")
        assert "TEST" in vendor_id


class TestERPIntegrationService:
    """Test ERP adapter factory"""
    
    def test_create_dynamics_gp_adapter(self):
        """Test creating Dynamics GP adapter"""
        config = {"base_url": "https://test.com", "api_key": "key", "company_id": "COMPANY001"}
        
        adapter = ERPIntegrationService.create_adapter("dynamics_gp", config)
        
        assert isinstance(adapter, MicrosoftDynamicsGPAdapter)
        assert adapter.base_url == "https://test.com"
    
    def test_create_mock_adapter(self):
        """Test creating mock adapter"""
        config = {}
        
        adapter = ERPIntegrationService.create_adapter("mock", config)
        
        assert isinstance(adapter, MockERPAdapter)
    
    def test_create_unsupported_adapter(self):
        """Test creating unsupported adapter type"""
        config = {}
        
        with pytest.raises(ValueError, match="Unsupported ERP type: unsupported"):
            ERPIntegrationService.create_adapter("unsupported", config)


class TestERPIntegrationService:
    """Test ERP manager"""
    
    @pytest.fixture
    def erp_manager(self):
        return ERPIntegrationService()
    
    @pytest.fixture
    def sample_invoice(self):
        return Invoice(
            id="test-id-123",
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=Decimal("1000.00"),
            currency="USD"
        )
    
    @pytest.mark.asyncio
    async def test_register_erp_success(self, erp_manager):
        """Test successful ERP registration"""
        company_id = "COMPANY001"
        erp_type = "mock"
        connection_config = {}
        
        result = await erp_manager.register_erp(company_id, erp_type, connection_config)
        
        assert result["status"] == "success"
        assert result["erp_type"] == erp_type
        assert result["company_id"] == company_id
        
        # Check that adapter was stored
        assert company_id in erp_manager.connection_cache
        assert erp_manager.connection_cache[company_id]["erp_type"] == erp_type
    
    @pytest.mark.asyncio
    async def test_register_erp_validation_failure(self, erp_manager):
        """Test ERP registration with validation failure"""
        company_id = "COMPANY001"
        erp_type = "dynamics_gp"
        connection_config = {"base_url": "https://test.com"}  # Missing required fields
        
        result = await erp_manager.register_erp(company_id, erp_type, connection_config)
        
        assert result["status"] == "error"
        assert "Missing required" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_adapter(self, erp_manager):
        """Test getting ERP adapter"""
        company_id = "COMPANY001"
        erp_type = "mock"
        connection_config = {}
        
        # Register ERP first
        await erp_manager.register_erp(company_id, erp_type, connection_config)
        
        # Get adapter
        adapter = erp_manager.get_adapter_by_company(company_id)
        
        assert adapter is not None
        assert isinstance(adapter, MockERPAdapter)
    
    @pytest.mark.asyncio
    async def test_get_adapter_not_found(self, erp_manager):
        """Test getting non-existent adapter"""
        adapter = erp_manager.get_adapter_by_company("NON_EXISTENT")
        
        assert adapter is None
    
    @pytest.mark.asyncio
    async def test_post_invoice_to_erp_success(self, erp_manager, sample_invoice):
        """Test successful invoice posting to ERP"""
        company_id = "COMPANY001"
        erp_type = "mock"
        connection_config = {}
        
        # Register ERP first
        await erp_manager.register_erp(company_id, erp_type, connection_config)
        
        # Post invoice
        company_settings = {"company_id": company_id}
        result = await erp_manager.post_invoice_to_erp(company_id, sample_invoice, company_settings)
        
        assert result["status"] == "success"
        assert "erp_doc_id" in result
    
    @pytest.mark.asyncio
    async def test_post_invoice_to_erp_no_adapter(self, erp_manager, sample_invoice):
        """Test invoice posting without ERP adapter"""
        company_id = "COMPANY001"
        company_settings = {"company_id": company_id}
        
        result = await erp_manager.post_invoice_to_erp(company_id, sample_invoice, company_settings)
        
        assert result["status"] == "error"
        assert "No ERP integration found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_health_check_all(self, erp_manager):
        """Test health check for all registered ERPs"""
        company_id = "COMPANY001"
        erp_type = "mock"
        connection_config = {}
        
        # Register ERP first
        await erp_manager.register_erp(company_id, erp_type, connection_config)
        
        # Check health
        results = await erp_manager.health_check_all()
        
        assert company_id in results
        assert results[company_id]["erp_type"] == erp_type
        assert "health" in results[company_id]
    
    def test_get_connection_status(self, erp_manager):
        """Test getting connection status"""
        company_id = "COMPANY001"
        
        # No connection registered
        status = erp_manager.get_connection_status(company_id)
        assert status is None
        
        # Register connection
        erp_manager.connection_cache[company_id] = {
            "erp_type": "mock",
            "status": "connected"
        }
        
        status = erp_manager.get_connection_status(company_id)
        assert status["erp_type"] == "mock"
        assert status["status"] == "connected"
    
    def test_list_registered_erps(self, erp_manager):
        """Test listing registered ERPs"""
        company_id = "COMPANY001"
        erp_type = "mock"
        
        # Register ERP
        erp_manager.connection_cache[company_id] = {
            "erp_type": erp_type,
            "status": "connected",
            "registered_at": "2024-01-15T10:00:00Z"
        }
        
        # List ERPs
        erps = erp_manager.list_registered_erps()
        
        assert len(erps) == 1
        assert erps[0]["company_id"] == company_id
        assert erps[0]["erp_type"] == erp_type
        assert erps[0]["status"] == "connected"


if __name__ == "__main__":
    pytest.main([__file__])



















