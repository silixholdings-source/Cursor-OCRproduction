"""
Phase 1 Test Suite for Microsoft Dynamics GP Integration
Tests the core POP Invoice Entry + Payables fallback functionality
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
import uuid

from services.erp import MicrosoftDynamicsGPAdapter
from src.models.invoice import Invoice, InvoiceStatus
from src.models.invoice_line import InvoiceLine


class TestPhase1DynamicsGPIntegration:
    """Test suite for Phase 1 Dynamics GP integration requirements"""
    
    @pytest.fixture
    def gp_adapter(self):
        """Create Dynamics GP adapter instance"""
        config = {
            "base_url": "https://gp-server.example.com",
            "api_key": "test-api-key",
            "company_id": "TWO",
            "timeout": 30
        }
        return MicrosoftDynamicsGPAdapter(config)
    
    @pytest.fixture
    def sample_invoice_with_po(self):
        """Sample invoice with PO number"""
        invoice = Invoice(
            id=str(uuid.uuid4()),
            invoice_number="INV-2024-001",
            supplier_name="Contoso Ltd",
            total_amount=Decimal("1250.00"),
            currency="USD",
            invoice_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            status=InvoiceStatus.PENDING,
            po_number="PO-2024-001",
            company_id=str(uuid.uuid4())
        )
        
        # Add line items
        invoice.line_items = [
            InvoiceLine(
                id=str(uuid.uuid4()),
                description="Office Supplies",
                quantity=Decimal("100"),
                unit_price=Decimal("10.00"),
                total=Decimal("1000.00"),
                invoice_id=invoice.id
            ),
            InvoiceLine(
                id=str(uuid.uuid4()),
                description="Shipping",
                quantity=Decimal("1"),
                unit_price=Decimal("250.00"),
                total=Decimal("250.00"),
                invoice_id=invoice.id
            )
        ]
        
        return invoice
    
    @pytest.fixture
    def sample_invoice_without_po(self):
        """Sample invoice without PO number (direct payables)"""
        invoice = Invoice(
            id=str(uuid.uuid4()),
            invoice_number="INV-2024-002",
            supplier_name="Direct Vendor Inc",
            total_amount=Decimal("500.00"),
            currency="USD",
            invoice_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            status=InvoiceStatus.PENDING,
            po_number=None,  # No PO number
            company_id=str(uuid.uuid4())
        )
        
        # Add line items
        invoice.line_items = [
            InvoiceLine(
                id=str(uuid.uuid4()),
                description="Consulting Services",
                quantity=Decimal("1"),
                unit_price=Decimal("500.00"),
                total=Decimal("500.00"),
                invoice_id=invoice.id
            )
        ]
        
        return invoice
    
    @pytest.fixture
    def company_settings(self):
        """Company-specific settings for GP posting"""
        return {
            "accounts_payable_account": "2000-00",
            "default_expense_account": "5000-00",
            "tax_account": "2100-00",
            "company_database": "TWO",
            "posting_method": "econnect"
        }

    @pytest.mark.asyncio
    async def test_health_check(self, gp_adapter):
        """Test Dynamics GP health check"""
        
        with patch.object(gp_adapter.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "healthy",
                "version": "18.4",
                "database": "TWO"
            }
            mock_get.return_value = mock_response
            
            result = await gp_adapter.health_check()
            
            assert result["status"] == "healthy"
            assert result["erp_name"] == "Microsoft Dynamics GP"
            assert "version" in result
    
    @pytest.mark.asyncio
    async def test_validate_connection(self, gp_adapter):
        """Test connection validation"""
        
        with patch.object(gp_adapter.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "authenticated": True,
                "company_access": ["TWO"],
                "permissions": ["read", "write"]
            }
            mock_get.return_value = mock_response
            
            result = await gp_adapter.validate_connection()
            
            assert result["status"] == "connected"
            assert result["erp_name"] == "Microsoft Dynamics GP"
            assert result["connection_type"] == "api"
    
    @pytest.mark.asyncio
    async def test_post_invoice_with_po_pop_entry(self, gp_adapter, sample_invoice_with_po, company_settings):
        """Test posting invoice with PO using POP Invoice Entry"""
        
        # Mock the GP API responses
        with patch.object(gp_adapter.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "status": "success",
                "method": "pop_invoice_entry",
                "gp_document_number": "INV20240115001",
                "posted_amount": 1250.00,
                "po_number": "PO-2024-001",
                "posting_date": datetime.utcnow().isoformat()
            }
            mock_post.return_value = mock_response
            
            result = await gp_adapter.post_invoice(sample_invoice_with_po, company_settings)
            
            assert result["status"] == "success"
            assert result["method"] == "pop_invoice_entry"
            assert result["gp_document_number"] == "INV20240115001"
            assert result["posted_amount"] == 1250.00
            assert result["po_number"] == "PO-2024-001"
    
    @pytest.mark.asyncio
    async def test_post_invoice_without_po_payables_fallback(self, gp_adapter, sample_invoice_without_po, company_settings):
        """Test posting invoice without PO using Payables Management fallback"""
        
        # Mock the GP API responses
        with patch.object(gp_adapter.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "status": "success",
                "method": "payables_management",
                "gp_document_number": "INV20240115002",
                "posted_amount": 500.00,
                "processing_type": "DIRECT_PAYABLES",
                "posting_date": datetime.utcnow().isoformat()
            }
            mock_post.return_value = mock_response
            
            result = await gp_adapter.post_invoice(sample_invoice_without_po, company_settings)
            
            assert result["status"] == "success"
            assert result["method"] == "payables_management"
            assert result["gp_document_number"] == "INV20240115002"
            assert result["posted_amount"] == 500.00
            assert result["processing_type"] == "DIRECT_PAYABLES"
    
    @pytest.mark.asyncio
    async def test_get_invoice_status(self, gp_adapter):
        """Test retrieving invoice status from GP"""
        
        with patch.object(gp_adapter.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "posted",
                "gp_document_number": "INV20240115001",
                "posted_amount": 1250.00,
                "posting_date": datetime.utcnow().isoformat(),
                "approval_status": "approved"
            }
            mock_get.return_value = mock_response
            
            result = await gp_adapter.get_invoice_status("INV20240115001")
            
            assert result["status"] == "posted"
            assert result["erp_doc_id"] == "INV20240115001"
            assert result["posted_amount"] == 1250.00
            assert result["erp_name"] == "Microsoft Dynamics GP"
    
    def test_transform_to_gp_pop_format(self, gp_adapter, sample_invoice_with_po, company_settings):
        """Test transformation to GP POP format"""
        
        result = gp_adapter._transform_to_gp_pop_format(sample_invoice_with_po, company_settings)
        
        assert result["vendor_id"] is not None
        assert result["invoice_number"] == "INV-2024-001"
        assert result["po_number"] == "PO-2024-001"
        assert result["total_amount"] == 1250.00
        assert result["processing_type"] == "POP_INVOICE_ENTRY"
        assert len(result["line_items"]) == 2
    
    def test_transform_to_gp_payables_format(self, gp_adapter, sample_invoice_without_po, company_settings):
        """Test transformation to GP Payables format"""
        
        result = gp_adapter._transform_to_gp_payables_format(sample_invoice_without_po, company_settings)
        
        assert result["vendor_id"] is not None
        assert result["invoice_number"] == "INV-2024-002"
        assert result["total_amount"] == 500.00
        assert result["processing_type"] == "DIRECT_PAYABLES"
        assert len(result["line_items"]) == 1
        assert len(result["gl_distributions"]) > 0
    
    def test_generate_gl_distributions(self, gp_adapter, sample_invoice_without_po, company_settings):
        """Test GL distribution generation"""
        
        result = gp_adapter._generate_gl_distributions(sample_invoice_without_po, company_settings)
        
        # Should have AP credit and expense debit
        ap_distribution = next((d for d in result if d["account"] == "2000-00"), None)
        expense_distribution = next((d for d in result if d["account"] == "5000-00"), None)
        
        assert ap_distribution is not None
        assert ap_distribution["credit_amount"] == 500.00
        assert ap_distribution["debit_amount"] == 0.0
        
        assert expense_distribution is not None
        assert expense_distribution["debit_amount"] == 500.00
        assert expense_distribution["credit_amount"] == 0.0
    
    def test_determine_gl_account(self, gp_adapter, company_settings):
        """Test GL account determination logic"""
        
        # Test with description-based mapping
        line_item = Mock()
        line_item.description = "Office Supplies"
        line_item.gl_account = None
        
        result = gp_adapter._determine_gl_account(line_item, company_settings)
        
        assert result == "5000-00"  # Default expense account
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_connection(self):
        """Test error handling for invalid connection configuration"""
        
        with pytest.raises(ValueError) as exc_info:
            MicrosoftDynamicsGPAdapter({
                "base_url": "https://gp-server.example.com",
                # Missing api_key and company_id
            })
        
        assert "Missing required Dynamics GP connection configuration" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_error_handling_api_failure(self, gp_adapter, sample_invoice_with_po, company_settings):
        """Test error handling for API failures"""
        
        with patch.object(gp_adapter.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {
                "error": "Internal server error",
                "message": "Database connection failed"
            }
            mock_post.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                await gp_adapter.post_invoice(sample_invoice_with_po, company_settings)
            
            assert "Failed to post invoice" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, gp_adapter, sample_invoice_with_po, company_settings):
        """Test timeout handling"""
        
        with patch.object(gp_adapter.client, 'post') as mock_post:
            mock_post.side_effect = asyncio.TimeoutError("Request timeout")
            
            with pytest.raises(Exception) as exc_info:
                await gp_adapter.post_invoice(sample_invoice_with_po, company_settings)
            
            assert "Request timeout" in str(exc_info.value)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
