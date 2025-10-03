"""
Comprehensive Test Suite for Dynamics GP Integration
Tests multi-company databases, 2-way and 3-way matching with multiple shipments
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
import uuid

from services.dynamics_gp_integration import (
    DynamicsGPIntegration,
    GPCompanyDatabase,
    GPPurchaseOrder,
    GPShipment,
    GPMatchResult,
    GPMatchingType,
    GPModule
)
from services.enhanced_three_way_match import MatchStatus, VarianceDetail, VarianceType
from src.models.invoice import Invoice
from src.models.purchase_order import PurchaseOrder, POLine
from src.models.receipt import Receipt, ReceiptLine

class TestDynamicsGPIntegration:
    """Test suite for Dynamics GP integration"""
    
    @pytest.fixture
    def gp_integration(self):
        """Create GP integration instance"""
        return DynamicsGPIntegration()
    
    @pytest.fixture
    def sample_companies(self):
        """Sample GP company databases"""
        return [
            GPCompanyDatabase(
                company_id="TWO",
                company_name="Fabrikam, Inc.",
                database_name="TWO",
                server_name="GP-SERVER",
                is_active=True,
                fiscal_year=2024,
                base_currency="USD",
                functional_currency="USD",
                reporting_currency="USD",
                multi_currency_enabled=True
            ),
            GPCompanyDatabase(
                company_id="DYNAMICS",
                company_name="Sample Company",
                database_name="DYNAMICS",
                server_name="GP-SERVER",
                is_active=True,
                fiscal_year=2024,
                base_currency="CAD",
                functional_currency="CAD",
                reporting_currency="USD",
                multi_currency_enabled=True
            )
        ]
    
    @pytest.fixture
    def sample_invoice_data(self):
        """Sample invoice data for testing"""
        return {
            "id": str(uuid.uuid4()),
            "invoice_number": "INV-2024-001",
            "vendor_name": "Contoso Ltd",
            "vendor_id": "CONTOSO001",
            "total_amount": Decimal("1250.00"),
            "currency": "USD",
            "invoice_date": datetime.now(),
            "due_date": datetime.now() + timedelta(days=30),
            "po_number": "PO-2024-001",
            "line_items": [
                {
                    "id": str(uuid.uuid4()),
                    "description": "Office Supplies - Pens and Paper",
                    "quantity": Decimal("100"),
                    "unit_price": Decimal("10.00"),
                    "total": Decimal("1000.00"),
                    "item_number": "OFFICE-001"
                },
                {
                    "id": str(uuid.uuid4()),
                    "description": "Shipping and Handling",
                    "quantity": Decimal("1"),
                    "unit_price": Decimal("250.00"),
                    "total": Decimal("250.00"),
                    "item_number": "SHIPPING"
                }
            ]
        }
    
    @pytest.fixture
    def sample_po_data(self):
        """Sample PO data from GP"""
        return GPPurchaseOrder(
            po_number="PO-2024-001",
            vendor_id="CONTOSO001",
            po_date=datetime.now() - timedelta(days=5),
            required_date=datetime.now() + timedelta(days=10),
            total_amount=Decimal("1250.00"),
            currency_code="USD",
            status="Released",
            type_id=1,
            company_db="TWO",
            line_items=[
                {
                    "line_number": 1,
                    "item_number": "OFFICE-001",
                    "description": "Office Supplies - Pens and Paper",
                    "quantity_ordered": Decimal("100"),
                    "quantity_received": Decimal("80"),
                    "unit_cost": Decimal("10.00"),
                    "extended_cost": Decimal("1000.00")
                },
                {
                    "line_number": 2,
                    "item_number": "SHIPPING",
                    "description": "Shipping and Handling",
                    "quantity_ordered": Decimal("1"),
                    "quantity_received": Decimal("0"),
                    "unit_cost": Decimal("250.00"),
                    "extended_cost": Decimal("250.00")
                }
            ],
            shipments=[
                {
                    "shipment_number": "SHIP-001",
                    "receipt_date": datetime.now() - timedelta(days=2),
                    "total_amount": Decimal("800.00")
                },
                {
                    "shipment_number": "SHIP-002", 
                    "receipt_date": datetime.now() - timedelta(days=1),
                    "total_amount": Decimal("200.00")
                }
            ]
        )
    
    @pytest.fixture
    def sample_shipments(self):
        """Sample shipments with multiple deliveries"""
        return [
            GPShipment(
                shipment_number="SHIP-001",
                po_number="PO-2024-001",
                receipt_date=datetime.now() - timedelta(days=2),
                vendor_id="CONTOSO001",
                total_amount=Decimal("800.00"),
                currency_code="USD",
                status="Received",
                line_items=[
                    {
                        "line_number": 1,
                        "item_number": "OFFICE-001",
                        "description": "Office Supplies - Pens and Paper",
                        "quantity_received": Decimal("80"),
                        "unit_cost": Decimal("10.00"),
                        "extended_cost": Decimal("800.00")
                    }
                ]
            ),
            GPShipment(
                shipment_number="SHIP-002",
                po_number="PO-2024-001", 
                receipt_date=datetime.now() - timedelta(days=1),
                vendor_id="CONTOSO001",
                total_amount=Decimal("200.00"),
                currency_code="USD",
                status="Received",
                line_items=[
                    {
                        "line_number": 1,
                        "item_number": "OFFICE-001",
                        "description": "Office Supplies - Pens and Paper",
                        "quantity_received": Decimal("20"),
                        "unit_cost": Decimal("10.00"),
                        "extended_cost": Decimal("200.00")
                    }
                ]
            ),
            GPShipment(
                shipment_number="SHIP-003",
                po_number="PO-2024-001",
                receipt_date=datetime.now(),
                vendor_id="CONTOSO001", 
                total_amount=Decimal("250.00"),
                currency_code="USD",
                status="Received",
                line_items=[
                    {
                        "line_number": 2,
                        "item_number": "SHIPPING",
                        "description": "Shipping and Handling",
                        "quantity_received": Decimal("1"),
                        "unit_cost": Decimal("250.00"),
                        "extended_cost": Decimal("250.00")
                    }
                ]
            )
        ]

class TestMultiCompanySupport:
    """Test multi-company database support"""
    
    @pytest.mark.asyncio
    async def test_get_company_databases(self, gp_integration, sample_companies):
        """Test retrieving all GP company databases"""
        
        with patch.object(gp_integration, 'get_company_databases', return_value=sample_companies):
            companies = await gp_integration.get_company_databases()
            
            assert len(companies) == 2
            assert companies[0].company_id == "TWO"
            assert companies[0].database_name == "TWO"
            assert companies[1].company_id == "DYNAMICS"
            assert companies[1].multi_currency_enabled == True
    
    @pytest.mark.asyncio
    async def test_initialize_connections(self, gp_integration, sample_companies):
        """Test initializing connections to multiple company databases"""
        
        with patch.object(gp_integration, 'get_company_databases', return_value=sample_companies):
            with patch.object(gp_integration, '_create_connection_pool', return_value=None):
                with patch.object(gp_integration, '_initialize_web_services', return_value=Mock()):
                    result = await gp_integration.initialize_connections()
                    
                    assert result["status"] == "success"
                    assert result["companies_connected"] == 2
                    assert result["web_services_available"] == True
    
    @pytest.mark.asyncio
    async def test_connection_pooling(self, gp_integration, sample_companies):
        """Test connection pooling for multiple companies"""
        
        for company in sample_companies:
            await gp_integration._create_connection_pool(company)
            
        assert len(gp_integration.connection_pools) == 2
        assert "TWO" in gp_integration.connection_pools
        assert "DYNAMICS" in gp_integration.connection_pools

class TestTwoWayMatching:
    """Test 2-way matching (Invoice vs PO) for Payables Management"""
    
    @pytest.mark.asyncio
    async def test_perfect_two_way_match(self, gp_integration, sample_invoice_data, sample_po_data):
        """Test perfect 2-way match scenario"""
        
        with patch.object(gp_integration, '_get_invoice_data', return_value=sample_invoice_data):
            with patch.object(gp_integration, '_find_gp_purchase_order', return_value=sample_po_data):
                with patch.object(gp_integration, '_analyze_invoice_po_match') as mock_analyze:
                    mock_analyze.return_value = {
                        "status": MatchStatus.PERFECT_MATCH,
                        "confidence_score": 0.98,
                        "variances": [],
                        "total_variance": Decimal("0"),
                        "auto_approval_eligible": True
                    }
                    
                    with patch.object(gp_integration, '_determine_gp_posting_requirements') as mock_posting:
                        mock_posting.return_value = {
                            "posting_required": True,
                            "gl_accounts": {"expense": "5000-000"}
                        }
                        
                        with patch.object(gp_integration, '_create_match_audit_trail', return_value=[]):
                            result = await gp_integration.perform_two_way_match(
                                sample_invoice_data["id"], "TWO", "PO-2024-001"
                            )
                            
                            assert result.match_type == GPMatchingType.TWO_WAY
                            assert result.status == MatchStatus.PERFECT_MATCH
                            assert result.confidence_score == 0.98
                            assert result.auto_approval_eligible == True
                            assert result.po_data.po_number == "PO-2024-001"
    
    @pytest.mark.asyncio
    async def test_price_variance_two_way_match(self, gp_integration, sample_invoice_data, sample_po_data):
        """Test 2-way match with price variance"""
        
        # Modify PO to have different price
        sample_po_data.total_amount = Decimal("1200.00")  # $50 difference
        
        price_variance = VarianceDetail(
            type=VarianceType.PRICE_VARIANCE,
            line_item_id="line-1",
            invoice_value=Decimal("1250.00"),
            po_value=Decimal("1200.00"),
            receipt_value=None,
            variance_amount=Decimal("50.00"),
            variance_percentage=4.17,  # 50/1200 * 100
            within_tolerance=False,  # Exceeds 2% tolerance
            requires_approval=True,
            explanation="Invoice amount $1,250.00 exceeds PO amount $1,200.00",
            suggested_action="Contact vendor for price clarification"
        )
        
        with patch.object(gp_integration, '_get_invoice_data', return_value=sample_invoice_data):
            with patch.object(gp_integration, '_find_gp_purchase_order', return_value=sample_po_data):
                with patch.object(gp_integration, '_analyze_invoice_po_match') as mock_analyze:
                    mock_analyze.return_value = {
                        "status": MatchStatus.PRICE_VARIANCE,
                        "confidence_score": 0.75,
                        "variances": [price_variance],
                        "total_variance": Decimal("50.00"),
                        "auto_approval_eligible": False
                    }
                    
                    with patch.object(gp_integration, '_determine_gp_posting_requirements') as mock_posting:
                        mock_posting.return_value = {
                            "posting_required": True,
                            "gl_accounts": {"expense": "5000-000"}
                        }
                        
                        with patch.object(gp_integration, '_create_match_audit_trail', return_value=[]):
                            result = await gp_integration.perform_two_way_match(
                                sample_invoice_data["id"], "TWO", "PO-2024-001"
                            )
                            
                            assert result.status == MatchStatus.PRICE_VARIANCE
                            assert result.confidence_score == 0.75
                            assert len(result.variances) == 1
                            assert result.variances[0].type == VarianceType.PRICE_VARIANCE
                            assert result.auto_approval_eligible == False
    
    @pytest.mark.asyncio
    async def test_no_po_found_scenario(self, gp_integration, sample_invoice_data):
        """Test scenario where no matching PO is found"""
        
        with patch.object(gp_integration, '_get_invoice_data', return_value=sample_invoice_data):
            with patch.object(gp_integration, '_find_gp_purchase_order', return_value=None):
                result = await gp_integration.perform_two_way_match(
                    sample_invoice_data["id"], "TWO", "NONEXISTENT-PO"
                )
                
                assert result.status == MatchStatus.PO_NOT_FOUND
                assert result.confidence_score == 0.0
                assert result.po_data is None
                assert result.auto_approval_eligible == False

class TestThreeWayMatching:
    """Test 3-way matching (Invoice vs PO vs Receipt) for Purchase Order Processing"""
    
    @pytest.mark.asyncio
    async def test_perfect_three_way_match_single_shipment(self, gp_integration, sample_invoice_data, 
                                                          sample_po_data, sample_shipments):
        """Test perfect 3-way match with single shipment"""
        
        # Use only first shipment that matches invoice amount
        single_shipment = [sample_shipments[0]]
        single_shipment[0].total_amount = Decimal("1250.00")  # Match invoice exactly
        
        with patch.object(gp_integration, '_get_invoice_data', return_value=sample_invoice_data):
            with patch.object(gp_integration, '_find_gp_purchase_order', return_value=sample_po_data):
                with patch.object(gp_integration, '_find_gp_shipments_for_po', return_value=single_shipment):
                    with patch.object(gp_integration, '_analyze_three_way_match') as mock_analyze:
                        mock_analyze.return_value = {
                            "status": MatchStatus.PERFECT_MATCH,
                            "confidence_score": 0.99,
                            "variances": [],
                            "total_variance": Decimal("0"),
                            "auto_approval_eligible": True,
                            "confidence_breakdown": {
                                "po_match": 0.98,
                                "shipment_match": 1.0,
                                "consistency": 0.99
                            }
                        }
                        
                        with patch.object(gp_integration, '_analyze_multiple_shipments') as mock_multi:
                            mock_multi.return_value = {"status": "single_shipment", "complexity": "low"}
                            
                            with patch.object(gp_integration, '_determine_gp_posting_requirements') as mock_posting:
                                mock_posting.return_value = {
                                    "posting_required": True,
                                    "gl_accounts": {"expense": "5000-000"}
                                }
                                
                                with patch.object(gp_integration, '_create_match_audit_trail', return_value=[]):
                                    with patch.object(gp_integration, '_log_multiple_shipments_analysis', return_value=None):
                                        result = await gp_integration.perform_three_way_match(
                                            sample_invoice_data["id"], "TWO", "PO-2024-001"
                                        )
                                        
                                        assert result.match_type == GPMatchingType.THREE_WAY
                                        assert result.status == MatchStatus.PERFECT_MATCH
                                        assert result.confidence_score == 0.99
                                        assert len(result.shipment_data) == 1
                                        assert result.auto_approval_eligible == True
    
    @pytest.mark.asyncio
    async def test_three_way_match_multiple_shipments(self, gp_integration, sample_invoice_data,
                                                     sample_po_data, sample_shipments):
        """Test 3-way match with multiple shipments (complex scenario)"""
        
        with patch.object(gp_integration, '_get_invoice_data', return_value=sample_invoice_data):
            with patch.object(gp_integration, '_find_gp_purchase_order', return_value=sample_po_data):
                with patch.object(gp_integration, '_find_gp_shipments_for_po', return_value=sample_shipments):
                    with patch.object(gp_integration, '_analyze_three_way_match') as mock_analyze:
                        mock_analyze.return_value = {
                            "status": MatchStatus.GOOD_MATCH,
                            "confidence_score": 0.87,
                            "variances": [],
                            "total_variance": Decimal("0"),
                            "auto_approval_eligible": False,  # Multiple shipments require review
                            "confidence_breakdown": {
                                "po_match": 0.95,
                                "shipment_match": 0.85,
                                "consistency": 0.90,
                                "multi_shipment": 0.75
                            }
                        }
                        
                        with patch.object(gp_integration, '_analyze_multiple_shipments') as mock_multi:
                            mock_multi.return_value = {
                                "strategy": "cumulative_match",
                                "total_shipments": 3,
                                "total_received_amount": 1250.0,
                                "invoice_amount": 1250.0,
                                "cumulative_variance": 0.0,
                                "date_span_days": 2,
                                "recommendation": "Approve - cumulative receipts match invoice"
                            }
                            
                            with patch.object(gp_integration, '_determine_gp_posting_requirements') as mock_posting:
                                mock_posting.return_value = {
                                    "posting_required": True,
                                    "gl_accounts": {"expense": "5000-000"}
                                }
                                
                                with patch.object(gp_integration, '_create_match_audit_trail', return_value=[]):
                                    with patch.object(gp_integration, '_log_multiple_shipments_analysis', return_value=None):
                                        result = await gp_integration.perform_three_way_match(
                                            sample_invoice_data["id"], "TWO", "PO-2024-001", True
                                        )
                                        
                                        assert result.match_type == GPMatchingType.THREE_WAY
                                        assert result.status == MatchStatus.GOOD_MATCH
                                        assert result.confidence_score == 0.87
                                        assert len(result.shipment_data) == 3
                                        assert result.auto_approval_eligible == False  # Requires manual review
    
    @pytest.mark.asyncio
    async def test_partial_shipments_scenario(self, gp_integration, sample_invoice_data,
                                            sample_po_data, sample_shipments):
        """Test scenario with partial shipments and progressive delivery"""
        
        # Modify shipments to simulate partial deliveries
        partial_shipments = sample_shipments[:2]  # Only first two shipments
        total_received = sum(s.total_amount for s in partial_shipments)  # $1000 received, $1250 invoiced
        
        quantity_variance = VarianceDetail(
            type=VarianceType.QUANTITY_VARIANCE,
            line_item_id="line-1",
            invoice_value=Decimal("100"),  # Invoice quantity
            po_value=Decimal("100"),       # PO quantity
            receipt_value=Decimal("80"),   # Only 80 received so far
            variance_amount=Decimal("20"), # 20 units short
            variance_percentage=20.0,
            within_tolerance=False,        # Exceeds 5% tolerance
            requires_approval=True,
            explanation="Invoice quantity 100 exceeds received quantity 80",
            suggested_action="Verify remaining delivery or adjust invoice"
        )
        
        with patch.object(gp_integration, '_get_invoice_data', return_value=sample_invoice_data):
            with patch.object(gp_integration, '_find_gp_purchase_order', return_value=sample_po_data):
                with patch.object(gp_integration, '_find_gp_shipments_for_po', return_value=partial_shipments):
                    with patch.object(gp_integration, '_analyze_three_way_match') as mock_analyze:
                        mock_analyze.return_value = {
                            "status": MatchStatus.QUANTITY_VARIANCE,
                            "confidence_score": 0.65,
                            "variances": [quantity_variance],
                            "total_variance": Decimal("250.00"),  # $250 over-invoiced
                            "auto_approval_eligible": False,
                            "confidence_breakdown": {
                                "po_match": 0.95,
                                "shipment_match": 0.60,  # Lower due to quantity variance
                                "consistency": 0.85,
                                "multi_shipment": 0.70
                            }
                        }
                        
                        with patch.object(gp_integration, '_analyze_multiple_shipments') as mock_multi:
                            mock_multi.return_value = {
                                "strategy": "partial_billing",
                                "total_shipments": 2,
                                "total_received_amount": float(total_received),
                                "invoice_amount": 1250.0,
                                "cumulative_variance": 250.0,
                                "date_span_days": 1,
                                "recommendation": "Hold for additional delivery or adjust invoice amount"
                            }
                            
                            with patch.object(gp_integration, '_determine_gp_posting_requirements') as mock_posting:
                                mock_posting.return_value = {
                                    "posting_required": False,  # Don't post until resolved
                                    "gl_accounts": {"expense": "5000-000"}
                                }
                                
                                with patch.object(gp_integration, '_create_match_audit_trail', return_value=[]):
                                    with patch.object(gp_integration, '_log_multiple_shipments_analysis', return_value=None):
                                        result = await gp_integration.perform_three_way_match(
                                            sample_invoice_data["id"], "TWO", "PO-2024-001", True
                                        )
                                        
                                        assert result.status == MatchStatus.QUANTITY_VARIANCE
                                        assert result.confidence_score == 0.65
                                        assert len(result.variances) == 1
                                        assert result.variances[0].type == VarianceType.QUANTITY_VARIANCE
                                        assert result.gp_posting_required == False
    
    @pytest.mark.asyncio
    async def test_no_receipts_found_scenario(self, gp_integration, sample_invoice_data, sample_po_data):
        """Test scenario where PO exists but no receipts found"""
        
        with patch.object(gp_integration, '_get_invoice_data', return_value=sample_invoice_data):
            with patch.object(gp_integration, '_find_gp_purchase_order', return_value=sample_po_data):
                with patch.object(gp_integration, '_find_gp_shipments_for_po', return_value=[]):
                    with patch.object(gp_integration, '_create_no_receipt_result') as mock_no_receipt:
                        mock_no_receipt.return_value = GPMatchResult(
                            match_id=str(uuid.uuid4()),
                            match_type=GPMatchingType.THREE_WAY,
                            status=MatchStatus.RECEIPT_NOT_FOUND,
                            confidence_score=0.0,
                            invoice_data=sample_invoice_data,
                            po_data=sample_po_data,
                            shipment_data=[],
                            variances=[],
                            total_variance=Decimal("0"),
                            auto_approval_eligible=False,
                            gp_posting_required=False,
                            suggested_gl_accounts={},
                            audit_trail=[]
                        )
                        
                        result = await gp_integration.perform_three_way_match(
                            sample_invoice_data["id"], "TWO", "PO-2024-001"
                        )
                        
                        assert result.status == MatchStatus.RECEIPT_NOT_FOUND
                        assert result.confidence_score == 0.0
                        assert len(result.shipment_data) == 0
                        assert result.auto_approval_eligible == False

class TestGPPosting:
    """Test posting to GP Payables Management module"""
    
    @pytest.mark.asyncio
    async def test_econnect_posting(self, gp_integration, sample_invoice_data, sample_po_data):
        """Test posting invoice via eConnect"""
        
        match_result = GPMatchResult(
            match_id=str(uuid.uuid4()),
            match_type=GPMatchingType.THREE_WAY,
            status=MatchStatus.PERFECT_MATCH,
            confidence_score=0.98,
            invoice_data=sample_invoice_data,
            po_data=sample_po_data,
            shipment_data=[],
            variances=[],
            total_variance=Decimal("0"),
            auto_approval_eligible=True,
            gp_posting_required=True,
            suggested_gl_accounts={"expense": "5000-000"},
            audit_trail=[]
        )
        
        with patch.object(gp_integration, '_post_via_econnect') as mock_econnect:
            mock_econnect.return_value = {
                "status": "success",
                "method": "econnect",
                "gp_document_number": "INV20240115001",
                "posted_amount": 1250.00,
                "posting_date": datetime.utcnow().isoformat(),
                "company_database": "TWO"
            }
            
            result = await gp_integration.post_invoice_to_gp(
                match_result, "TWO", "econnect"
            )
            
            assert result["status"] == "success"
            assert result["method"] == "econnect"
            assert result["posted_amount"] == 1250.00
            assert result["company_database"] == "TWO"
    
    def test_build_econnect_xml(self, gp_integration, sample_invoice_data, sample_po_data):
        """Test building eConnect XML document"""
        
        match_result = GPMatchResult(
            match_id=str(uuid.uuid4()),
            match_type=GPMatchingType.TWO_WAY,
            status=MatchStatus.PERFECT_MATCH,
            confidence_score=0.98,
            invoice_data=sample_invoice_data,
            po_data=sample_po_data,
            shipment_data=[],
            variances=[],
            total_variance=Decimal("0"),
            auto_approval_eligible=True,
            gp_posting_required=True,
            suggested_gl_accounts={},
            audit_trail=[]
        )
        
        xml_result = gp_integration._build_econnect_invoice_xml(match_result, "TWO")
        
        assert "eConnect" in xml_result
        assert "PMTransactionType" in xml_result
        assert "CONTOSO001" in xml_result  # Vendor ID
        assert "INV-2024-001" in xml_result  # Invoice number
        assert "TWO" in xml_result  # Company database

class TestErrorHandling:
    """Test error handling and recovery scenarios"""
    
    @pytest.mark.asyncio
    async def test_database_connection_failure(self, gp_integration):
        """Test handling of database connection failures"""
        
        with patch.object(gp_integration, '_get_connection', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception) as exc_info:
                await gp_integration._find_gp_purchase_order({}, "TWO", "PO-001")
            
            assert "Connection failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_company_database(self, gp_integration, sample_invoice_data):
        """Test handling of invalid company database"""
        
        with pytest.raises(ValueError) as exc_info:
            await gp_integration.perform_two_way_match(
                sample_invoice_data["id"], "INVALID_DB", "PO-001"
            )
        
        assert "No connection pool" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_malformed_data_handling(self, gp_integration):
        """Test handling of malformed invoice data"""
        
        malformed_data = {
            "id": "invalid-uuid",
            "total_amount": "not-a-number",  # Invalid amount
            "invoice_date": "invalid-date"   # Invalid date
        }
        
        with patch.object(gp_integration, '_get_invoice_data', return_value=malformed_data):
            with patch.object(gp_integration, '_find_gp_purchase_order', return_value=None):
                result = await gp_integration.perform_two_way_match(
                    malformed_data["id"], "TWO", "PO-001"
                )
                
                # Should handle gracefully and return no match
                assert result.status == MatchStatus.PO_NOT_FOUND

class TestPerformanceAndScalability:
    """Test performance and scalability aspects"""
    
    @pytest.mark.asyncio
    async def test_concurrent_matching_operations(self, gp_integration, sample_invoice_data, sample_po_data):
        """Test concurrent matching operations"""
        
        async def perform_match():
            with patch.object(gp_integration, '_get_invoice_data', return_value=sample_invoice_data):
                with patch.object(gp_integration, '_find_gp_purchase_order', return_value=sample_po_data):
                    with patch.object(gp_integration, '_analyze_invoice_po_match') as mock_analyze:
                        mock_analyze.return_value = {
                            "status": MatchStatus.PERFECT_MATCH,
                            "confidence_score": 0.98,
                            "variances": [],
                            "total_variance": Decimal("0"),
                            "auto_approval_eligible": True
                        }
                        
                        with patch.object(gp_integration, '_determine_gp_posting_requirements') as mock_posting:
                            mock_posting.return_value = {"posting_required": True, "gl_accounts": {}}
                            
                            with patch.object(gp_integration, '_create_match_audit_trail', return_value=[]):
                                return await gp_integration.perform_two_way_match(
                                    str(uuid.uuid4()), "TWO", f"PO-{uuid.uuid4()}"
                                )
        
        # Run 10 concurrent matching operations
        tasks = [perform_match() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 10
        assert all(result.status == MatchStatus.PERFECT_MATCH for result in results)
    
    @pytest.mark.asyncio
    async def test_large_shipment_volume_handling(self, gp_integration, sample_invoice_data, sample_po_data):
        """Test handling of large numbers of shipments"""
        
        # Create 50 shipments for a single PO
        large_shipments = []
        for i in range(50):
            shipment = GPShipment(
                shipment_number=f"SHIP-{i:03d}",
                po_number="PO-2024-001",
                receipt_date=datetime.now() - timedelta(days=i),
                vendor_id="CONTOSO001",
                total_amount=Decimal("25.00"),  # Small amounts that add up to invoice
                currency_code="USD",
                status="Received",
                line_items=[{
                    "line_number": 1,
                    "item_number": "OFFICE-001",
                    "description": "Office Supplies",
                    "quantity_received": Decimal("2"),
                    "unit_cost": Decimal("12.50"),
                    "extended_cost": Decimal("25.00")
                }]
            )
            large_shipments.append(shipment)
        
        with patch.object(gp_integration, '_get_invoice_data', return_value=sample_invoice_data):
            with patch.object(gp_integration, '_find_gp_purchase_order', return_value=sample_po_data):
                with patch.object(gp_integration, '_find_gp_shipments_for_po', return_value=large_shipments):
                    with patch.object(gp_integration, '_analyze_three_way_match') as mock_analyze:
                        mock_analyze.return_value = {
                            "status": MatchStatus.GOOD_MATCH,
                            "confidence_score": 0.85,
                            "variances": [],
                            "total_variance": Decimal("0"),
                            "auto_approval_eligible": False,  # Too complex for auto-approval
                            "confidence_breakdown": {"multi_shipment": 0.60}  # Lower confidence due to complexity
                        }
                        
                        with patch.object(gp_integration, '_analyze_multiple_shipments') as mock_multi:
                            mock_multi.return_value = {
                                "strategy": "progressive_delivery",
                                "total_shipments": 50,
                                "complexity": "very_high"
                            }
                            
                            with patch.object(gp_integration, '_determine_gp_posting_requirements') as mock_posting:
                                mock_posting.return_value = {"posting_required": True, "gl_accounts": {}}
                                
                                with patch.object(gp_integration, '_create_match_audit_trail', return_value=[]):
                                    with patch.object(gp_integration, '_log_multiple_shipments_analysis', return_value=None):
                                        result = await gp_integration.perform_three_way_match(
                                            sample_invoice_data["id"], "TWO", "PO-2024-001", True
                                        )
                                        
                                        assert result.status == MatchStatus.GOOD_MATCH
                                        assert len(result.shipment_data) == 50
                                        assert result.auto_approval_eligible == False  # Complex scenario

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])


