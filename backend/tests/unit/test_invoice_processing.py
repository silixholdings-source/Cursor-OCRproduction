"""
Unit tests for invoice processing functionality
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from src.services.invoice_processor import InvoiceProcessor
from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
from src.models.user import User, UserRole
from src.models.audit import AuditLog, AuditAction, AuditResourceType


class TestInvoiceProcessor:
    """Test invoice processor functionality"""
    
    @pytest.fixture
    def processor(self):
        return InvoiceProcessor()
    
    @pytest.fixture
    def sample_ocr_data(self):
        from datetime import datetime, timedelta
        recent_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return {
            "supplier_name": "Test Supplier Corp",
            "invoice_number": "INV-001",
            "invoice_date": recent_date,
            "due_date": due_date,
            "total_amount": 1500.00,
            "currency": "USD",
            "tax_amount": 120.00,
            "tax_rate": 0.08,
            "subtotal": 1500.00,
            "total_with_tax": 1620.00,
            "line_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 1000.00,
                    "total": 1000.00,
                    "gl_account": "6000"
                },
                {
                    "description": "Implementation Services",
                    "quantity": 10,
                    "unit_price": 50.00,
                    "total": 500.00,
                    "gl_account": "6500"
                }
            ],
            "confidence_scores": {
                "supplier_name": 0.95,
                "invoice_number": 0.98,
                "total_amount": 0.99,
                "line_items": 0.92
            },
            "processing_metadata": {
                "provider": "mock",
                "processing_time_ms": 100,
                "file_size_bytes": 1024,
                "extraction_method": "mock"
            }
        }
    
    @pytest.fixture
    def mock_db_session(self):
        session = Mock()
        
        def mock_add(obj):
            # Simulate setting an ID when an object is added
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = "generated-id-123"
        
        def mock_refresh(obj):
            # Simulate refresh by ensuring the object has an ID
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = "generated-id-123"
        
        session.add = mock_add
        session.commit = Mock()
        session.refresh = mock_refresh
        session.query = Mock()
        return session
    
    @pytest.fixture
    def mock_user(self):
        user = Mock()
        user.id = "user-123"
        user.company_id = "company-123"
        user.role = UserRole.MANAGER
        return user
    
    def test_business_rules_configuration(self, processor):
        """Test business rules are properly configured"""
        rules = processor.business_rules
        
        assert rules["duplicate_threshold"] == 0.95
        assert rules["fraud_threshold"] == 0.8
        assert rules["auto_approval_limit"] == 1000.0
        assert rules["max_processing_time"] == 48
        assert rules["retry_attempts"] == 3
        assert rules["batch_size"] == 100
    
    def test_validate_invoice_data_valid(self, processor, sample_ocr_data):
        """Test validation of valid invoice data"""
        result = processor._validate_invoice_data(sample_ocr_data)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_invoice_data_missing_fields(self, processor):
        """Test validation with missing required fields"""
        incomplete_data = {
            "supplier_name": "Test Supplier",
            # Missing invoice_number, total_amount, invoice_date
        }
        
        result = processor._validate_invoice_data(incomplete_data)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) == 3
        assert "Missing required field: invoice_number" in result["errors"]
        assert "Missing required field: total_amount" in result["errors"]
        assert "Missing required field: invoice_date" in result["errors"]
    
    def test_validate_invoice_data_invalid_amount(self, processor, sample_ocr_data):
        """Test validation with invalid amount"""
        sample_ocr_data["total_amount"] = -100  # Negative amount
        
        result = processor._validate_invoice_data(sample_ocr_data)
        
        assert result["is_valid"] is False
        assert "Total amount must be greater than 0" in result["errors"]
    
    def test_validate_invoice_data_amount_too_high(self, processor, sample_ocr_data):
        """Test validation with amount exceeding limit"""
        sample_ocr_data["total_amount"] = 2000000  # Over $1M limit
        
        result = processor._validate_invoice_data(sample_ocr_data)
        
        assert result["is_valid"] is False
        assert "Total amount exceeds maximum limit" in result["errors"]
    
    def test_validate_invoice_data_future_date(self, processor, sample_ocr_data):
        """Test validation with future invoice date"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        sample_ocr_data["invoice_date"] = tomorrow
        
        result = processor._validate_invoice_data(sample_ocr_data)
        
        assert result["is_valid"] is False
        assert "Invoice date cannot be in the future" in result["errors"]
    
    def test_validate_invoice_data_old_date(self, processor, sample_ocr_data):
        """Test validation with very old invoice date"""
        old_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        sample_ocr_data["invoice_date"] = old_date
        
        result = processor._validate_invoice_data(sample_ocr_data)
        
        assert result["is_valid"] is False
        assert "Invoice date is too old (more than 1 year)" in result["errors"]
    
    def test_validate_invoice_data_invalid_line_items(self, processor, sample_ocr_data):
        """Test validation with invalid line items"""
        sample_ocr_data["line_items"][0]["description"] = ""  # Empty description
        sample_ocr_data["line_items"][1]["total"] = 0  # Zero total
        
        result = processor._validate_invoice_data(sample_ocr_data)
        
        assert result["is_valid"] is False
        assert "Line item 1 missing description" in result["errors"]
        assert "Line item 2 has invalid total amount" in result["errors"]
    
    def test_create_invoice_from_ocr(self, processor, sample_ocr_data, mock_user):
        """Test creating invoice from OCR data"""
        invoice = processor._create_invoice_from_ocr(
            sample_ocr_data, 
            str(mock_user.company_id), 
            str(mock_user.id), 
            "/path/to/file.pdf"
        )
        
        assert invoice.invoice_number == "INV-001"
        assert invoice.supplier_name == "Test Supplier Corp"
        assert invoice.total_amount == Decimal("1500.00")
        assert invoice.currency == "USD"
        assert invoice.tax_amount == Decimal("120.00")
        assert invoice.tax_rate == Decimal("0.08")
        assert invoice.company_id == str(mock_user.company_id)
        assert invoice.created_by_id == str(mock_user.id)
        assert invoice.original_file_path == "/path/to/file.pdf"
    
    @pytest.mark.asyncio
    async def test_check_for_duplicates_exact_match(self, processor, mock_db_session):
        """Test duplicate detection with exact match"""
        # Mock existing invoice
        existing_invoice = Mock()
        existing_invoice.id = "existing-123"
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = existing_invoice
        mock_db_session.query.return_value = mock_query
        
        invoice = Mock()
        invoice.invoice_number = "INV-001"
        invoice.supplier_name = "Test Supplier"
        invoice.id = "new-123"
        
        result = await processor._check_for_duplicates(
            invoice, "company-123", mock_db_session
        )
        
        assert result["is_duplicate"] is True
        assert result["duplicate_id"] == "existing-123"
        assert result["confidence"] == 1.0
        assert "Exact invoice number and supplier match" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_check_for_duplicates_similar_match(self, processor, mock_db_session):
        """Test duplicate detection with similar match"""
        # Mock no exact match
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        
        # Mock similar invoices
        similar_invoice = Mock()
        similar_invoice.id = "similar-123"
        similar_invoice.invoice_number = "INV-002"
        similar_invoice.supplier_name = "Test Supplier"
        similar_invoice.total_amount = Decimal("1000.00")
        
        # Set up the mock to return different results for first() and all() calls
        mock_query.filter.return_value.all.return_value = [similar_invoice]
        mock_db_session.query.return_value = mock_query
        
        invoice = Mock()
        invoice.invoice_number = "INV-002"
        invoice.supplier_name = "Test Supplier"
        invoice.total_amount = Decimal("1000.00")
        invoice.invoice_date = datetime.now().date()
        invoice.id = "new-123"
        
        result = await processor._check_for_duplicates(
            invoice, "company-123", mock_db_session
        )
        
        assert result["is_duplicate"] is True
        assert result["duplicate_id"] == "similar-123"
        assert result["confidence"] == 0.9
        assert "Similar invoice with same amount, supplier, and date" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_check_for_duplicates_no_match(self, processor, mock_db_session):
        """Test duplicate detection with no matches"""
        # Mock no matches
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_query.filter.return_value.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        invoice = Mock()
        invoice.invoice_number = "INV-003"
        invoice.supplier_name = "Test Supplier"
        invoice.total_amount = Decimal("1000.00")
        invoice.invoice_date = datetime.now().date()
        invoice.id = "new-123"
        
        result = await processor._check_for_duplicates(
            invoice, "company-123", mock_db_session
        )
        
        assert result["is_duplicate"] is False
        assert result["confidence"] == 0.0
    
    @pytest.mark.asyncio
    async def test_detect_fraud_low_risk(self, processor, sample_ocr_data):
        """Test fraud detection for low-risk invoice"""
        invoice = Mock()
        invoice.total_amount = Decimal("500.00")
        invoice.invoice_date = datetime.now().date()
        invoice.supplier_name = "Legitimate Supplier"
        invoice.tax_amount = Decimal("40.00")
        
        result = await processor._detect_fraud(invoice, sample_ocr_data)
        
        assert result["fraud_score"] <= 0.3
        assert result["risk_level"] in ["low", "medium"]
        assert len(result["fraud_indicators"]) <= 1
    
    @pytest.mark.asyncio
    async def test_detect_fraud_high_risk(self, processor, sample_ocr_data):
        """Test fraud detection for high-risk invoice"""
        invoice = Mock()
        invoice.total_amount = Decimal("100000.00")  # High value
        invoice.invoice_date = datetime.now().date()
        invoice.supplier_name = "test"  # Test supplier
        invoice.tax_amount = Decimal("0.00")  # No tax on high value
        
        result = await processor._detect_fraud(invoice, sample_ocr_data)
        
        assert result["fraud_score"] > 0.6
        assert result["risk_level"] == "high"
        assert len(result["fraud_indicators"]) >= 3
    
    @pytest.mark.asyncio
    async def test_ai_gl_coding(self, processor):
        """Test AI GL coding functionality"""
        invoice = Mock()
        line1 = Mock()
        line1.description = "Software License"
        line1.id = "line-1"
        
        line2 = Mock()
        line2.description = "Consulting Services"
        line2.id = "line-2"
        
        invoice.line_items = [line1, line2]
        
        result = await processor._ai_gl_coding(invoice, "company-123")
        
        assert result["confidence"] == 0.85
        assert result["ai_model"] == "mock-gl-coder-v1"
        assert len(result["line_items"]) == 2
        
        # Check GL account suggestions
        software_line = next(l for l in result["line_items"] if "Software" in l["description"])
        assert software_line["suggested_gl_account"] == "6000"  # Software expenses
        
        service_line = next(l for l in result["line_items"] if "Services" in l["description"])
        assert service_line["suggested_gl_account"] == "6500"  # Professional services
    
    def test_should_auto_approve_below_threshold(self, processor):
        """Test auto-approval for invoices below threshold"""
        invoice = Mock()
        invoice.total_amount = Decimal("500.00")  # Below $1000 threshold
        
        result = processor._should_auto_approve(invoice)
        
        assert result is True
    
    def test_should_auto_approve_above_threshold(self, processor):
        """Test auto-approval for invoices above threshold"""
        invoice = Mock()
        invoice.total_amount = Decimal("1500.00")  # Above $1000 threshold
        invoice.type = None  # Not a recurring invoice
        invoice.po_number = None  # Not PO-backed
        
        result = processor._should_auto_approve(invoice)
        
        assert result is False
    
    def test_should_auto_approve_recurring(self, processor):
        """Test auto-approval for recurring invoices"""
        invoice = Mock()
        invoice.total_amount = Decimal("2000.00")  # Above threshold
        invoice.type = InvoiceType.RECURRING
        
        result = processor._should_auto_approve(invoice)
        
        assert result is True
    
    def test_should_auto_approve_po_backed(self, processor):
        """Test auto-approval for PO-backed invoices"""
        invoice = Mock()
        invoice.total_amount = Decimal("2000.00")  # Above threshold
        invoice.po_number = "PO-001"
        
        result = processor._should_auto_approve(invoice)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_batch_process_invoices(self, processor, mock_db_session, mock_user):
        """Test batch processing of invoices"""
        file_paths = [
            "/path/to/invoice1.pdf",
            "/path/to/invoice2.jpg",
            "/path/to/invoice3.pdf"
        ]
        
        # Mock database query to return no duplicates
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_query.filter.return_value.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        # Mock OCR service to return sample data
        with patch.object(processor.ocr_service, 'extract_invoice') as mock_ocr:
            mock_ocr.return_value = {
                "supplier_name": "Test Supplier",
                "invoice_number": "INV-001",
                "invoice_date": "2025-01-15",
                "total_amount": 1000.00,
                "currency": "USD",
                "subtotal": 1000.00,
                "total_with_tax": 1000.00,
                "confidence_scores": {"supplier_name": 0.95}
            }
            
            # Mock workflow engine
            with patch('services.workflow_engine.workflow_engine.create_workflow') as mock_workflow:
                mock_workflow.return_value = {"workflow_id": "workflow-123"}
                
                result = await processor.batch_process_invoices(
                    file_paths, str(mock_user.company_id), str(mock_user.id), mock_db_session
                )
                
                
                assert result["status"] == "completed"
                assert result["total"] == 3
                assert result["successful"] == 3
                assert result["failed"] == 0
                assert len(result["results"]) == 3
    
    @pytest.mark.asyncio
    async def test_reprocess_invoice(self, processor, mock_db_session, mock_user):
        """Test reprocessing an existing invoice"""
        # Mock existing invoice
        existing_invoice = Mock()
        existing_invoice.id = "invoice-123"
        existing_invoice.original_file_path = "/path/to/original.pdf"
        existing_invoice.status = InvoiceStatus.ERROR
        existing_invoice.erp_error_message = "Previous error"
        
        # Mock database query to handle multiple queries
        query_count = [0]  # Use list to make it mutable in nested function
        
        def mock_query_side_effect(model):
            query_count[0] += 1
            mock_query = Mock()
            
            if query_count[0] == 1:
                # First query: find existing invoice for reprocess
                mock_query.filter.return_value.first.return_value = existing_invoice
            else:
                # Subsequent queries: duplicate checks should return None
                mock_query.filter.return_value.first.return_value = None
                mock_query.filter.return_value.all.return_value = []
            
            return mock_query
        
        mock_db_session.query.side_effect = mock_query_side_effect
        
        # Mock OCR service
        with patch.object(processor.ocr_service, 'extract_invoice') as mock_ocr:
            mock_ocr.return_value = {
                "supplier_name": "Test Supplier",
                "invoice_number": "INV-001",
                "invoice_date": "2025-01-15",
                "total_amount": 1000.00,
                "currency": "USD",
                "subtotal": 1000.00,
                "total_with_tax": 1000.00,
                "confidence_scores": {"supplier_name": 0.95}
            }
            
            # Mock workflow engine
            with patch('services.workflow_engine.workflow_engine.create_workflow') as mock_workflow:
                mock_workflow.return_value = {"workflow_id": "workflow-123"}
                
                result = await processor.reprocess_invoice(
                    "invoice-123", str(mock_user.company_id), str(mock_user.id), mock_db_session
                )
                
                
                assert result["status"] == "success"
                assert "reprocessed" in result["message"].lower()
                
                # Check that invoice was reset
                assert existing_invoice.status == InvoiceStatus.DRAFT
                assert existing_invoice.erp_error_message is None


if __name__ == "__main__":
    pytest.main([__file__])



















