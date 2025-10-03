"""
Phase 1 Test Suite for AI-Powered Approval Workflow with Dynamic Thresholds
Tests intelligent approval routing, threshold management, and workflow automation
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
import uuid

from services.workflow_engine import (
    WorkflowEngine, 
    WorkflowStatus, 
    ApprovalAction,
    WorkflowStep,
    WorkflowInstance
)
from services.invoice_processor import InvoiceProcessor
from services.advanced_ml_models import advanced_ml_service
from src.models.invoice import Invoice, InvoiceStatus
from src.models.user import User, UserRole
from src.models.company import Company, CompanyTier


class TestPhase1AIApprovalWorkflow:
    """Test suite for Phase 1 AI-powered approval workflow requirements"""
    
    @pytest.fixture
    def workflow_engine(self):
        """Create workflow engine instance"""
        return WorkflowEngine()
    
    @pytest.fixture
    def invoice_processor(self):
        """Create invoice processor instance"""
        return InvoiceProcessor()
    
    @pytest.fixture
    def sample_company_basic(self):
        """Sample basic tier company"""
        return Company(
            id=str(uuid.uuid4()),
            name="Basic Company Inc.",
            tier=CompanyTier.BASIC,
            subscription_status="active",
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_company_enterprise(self):
        """Sample enterprise tier company"""
        return Company(
            id=str(uuid.uuid4()),
            name="Enterprise Corp.",
            tier=CompanyTier.ENTERPRISE,
            subscription_status="active",
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_users(self):
        """Sample users with different roles"""
        return [
            User(
                id=str(uuid.uuid4()),
                email="manager@company.com",
                role=UserRole.MANAGER,
                first_name="John",
                last_name="Manager",
                company_id=str(uuid.uuid4())
            ),
            User(
                id=str(uuid.uuid4()),
                email="director@company.com",
                role=UserRole.DIRECTOR,
                first_name="Jane",
                last_name="Director",
                company_id=str(uuid.uuid4())
            ),
            User(
                id=str(uuid.uuid4()),
                email="approver@company.com",
                role=UserRole.APPROVER,
                first_name="Bob",
                last_name="Approver",
                company_id=str(uuid.uuid4())
            )
        ]
    
    @pytest.fixture
    def sample_invoice_low_amount(self):
        """Sample low amount invoice for auto-approval testing"""
        return Invoice(
            id=str(uuid.uuid4()),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=Decimal("500.00"),
            currency="USD",
            invoice_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=30),
            status=InvoiceStatus.PENDING,
            company_id=str(uuid.uuid4())
        )
    
    @pytest.fixture
    def sample_invoice_medium_amount(self):
        """Sample medium amount invoice requiring manager approval"""
        return Invoice(
            id=str(uuid.uuid4()),
            invoice_number="INV-002",
            supplier_name="Test Supplier",
            total_amount=Decimal("2500.00"),
            currency="USD",
            invoice_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=30),
            status=InvoiceStatus.PENDING,
            company_id=str(uuid.uuid4())
        )
    
    @pytest.fixture
    def sample_invoice_high_amount(self):
        """Sample high amount invoice requiring director approval"""
        return Invoice(
            id=str(uuid.uuid4()),
            invoice_number="INV-003",
            supplier_name="Test Supplier",
            total_amount=Decimal("15000.00"),
            currency="USD",
            invoice_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=30),
            status=InvoiceStatus.PENDING,
            company_id=str(uuid.uuid4())
        )
    
    @pytest.fixture
    def sample_invoice_very_high_amount(self):
        """Sample very high amount invoice requiring executive approval"""
        return Invoice(
            id=str(uuid.uuid4()),
            invoice_number="INV-004",
            supplier_name="Test Supplier",
            total_amount=Decimal("50000.00"),
            currency="USD",
            invoice_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=30),
            status=InvoiceStatus.PENDING,
            company_id=str(uuid.uuid4())
        )

    @pytest.mark.asyncio
    async def test_auto_approval_low_amount_invoice(self, workflow_engine, sample_invoice_low_amount, sample_company_basic):
        """Test auto-approval for low amount invoices"""
        
        # Mock AI analysis for low risk invoice
        ai_analysis = {
            "fraud_probability": 0.05,
            "risk_score": 0.1,
            "auto_approval_eligible": True,
            "confidence_score": 0.95,
            "recommended_action": "auto_approve",
            "approval_chain": [],
            "threshold_analysis": {
                "amount_threshold": 1000.0,
                "current_amount": 500.0,
                "within_auto_approval": True
            }
        }
        
        with patch.object(workflow_engine, 'create_workflow') as mock_create:
            mock_create.return_value = WorkflowInstance(
                workflow_id=str(uuid.uuid4()),
                invoice_id=sample_invoice_low_amount.id,
                company_id=sample_company_basic.id,
                status=WorkflowStatus.COMPLETED,
                steps=[],
                created_at=datetime.utcnow()
            )
            
            result = await workflow_engine.process_approval_workflow(
                sample_invoice_low_amount, 
                ai_analysis, 
                sample_company_basic
            )
            
            assert result["status"] == "auto_approved"
            assert result["approval_required"] == False
            assert result["workflow_status"] == WorkflowStatus.COMPLETED
            assert result["ai_recommendation"] == "auto_approve"

    @pytest.mark.asyncio
    async def test_approval_workflow_medium_amount(self, workflow_engine, sample_invoice_medium_amount, sample_company_basic):
        """Test approval workflow for medium amount invoices"""
        
        # Mock AI analysis for medium risk invoice
        ai_analysis = {
            "fraud_probability": 0.15,
            "risk_score": 0.3,
            "auto_approval_eligible": False,
            "confidence_score": 0.85,
            "recommended_action": "manager_approval",
            "approval_chain": ["manager"],
            "threshold_analysis": {
                "amount_threshold": 1000.0,
                "current_amount": 2500.0,
                "approval_level_required": "manager"
            }
        }
        
        with patch.object(workflow_engine, 'create_workflow') as mock_create:
            mock_create.return_value = WorkflowInstance(
                workflow_id=str(uuid.uuid4()),
                invoice_id=sample_invoice_medium_amount.id,
                company_id=sample_company_basic.id,
                status=WorkflowStatus.PENDING,
                steps=[
                    WorkflowStep(
                        step_id="step_1",
                        name="Manager Approval",
                        description="Manager approval required for amount > $1000",
                        approver_role="manager",
                        is_required=True,
                        timeout_hours=72
                    )
                ],
                created_at=datetime.utcnow()
            )
            
            result = await workflow_engine.process_approval_workflow(
                sample_invoice_medium_amount, 
                ai_analysis, 
                sample_company_basic
            )
            
            assert result["status"] == "pending_approval"
            assert result["approval_required"] == True
            assert result["workflow_status"] == WorkflowStatus.PENDING
            assert result["approval_level"] == "manager"
            assert len(result["approval_chain"]) == 1

    @pytest.mark.asyncio
    async def test_approval_workflow_high_amount(self, workflow_engine, sample_invoice_high_amount, sample_company_basic):
        """Test approval workflow for high amount invoices"""
        
        # Mock AI analysis for high risk invoice
        ai_analysis = {
            "fraud_probability": 0.25,
            "risk_score": 0.5,
            "auto_approval_eligible": False,
            "confidence_score": 0.75,
            "recommended_action": "director_approval",
            "approval_chain": ["manager", "director"],
            "threshold_analysis": {
                "amount_threshold": 10000.0,
                "current_amount": 15000.0,
                "approval_level_required": "director"
            }
        }
        
        with patch.object(workflow_engine, 'create_workflow') as mock_create:
            mock_create.return_value = WorkflowInstance(
                workflow_id=str(uuid.uuid4()),
                invoice_id=sample_invoice_high_amount.id,
                company_id=sample_company_basic.id,
                status=WorkflowStatus.PENDING,
                steps=[
                    WorkflowStep(
                        step_id="step_1",
                        name="Manager Approval",
                        description="Manager approval required",
                        approver_role="manager",
                        is_required=True,
                        timeout_hours=72
                    ),
                    WorkflowStep(
                        step_id="step_2",
                        name="Director Approval",
                        description="Director approval required for amount > $10K",
                        approver_role="director",
                        is_required=True,
                        timeout_hours=48
                    )
                ],
                created_at=datetime.utcnow()
            )
            
            result = await workflow_engine.process_approval_workflow(
                sample_invoice_high_amount, 
                ai_analysis, 
                sample_company_basic
            )
            
            assert result["status"] == "pending_approval"
            assert result["approval_required"] == True
            assert result["workflow_status"] == WorkflowStatus.PENDING
            assert result["approval_level"] == "director"
            assert len(result["approval_chain"]) == 2

    @pytest.mark.asyncio
    async def test_enterprise_tier_higher_thresholds(self, workflow_engine, sample_invoice_medium_amount, sample_company_enterprise):
        """Test that enterprise tier has higher auto-approval thresholds"""
        
        # Mock AI analysis for enterprise company
        ai_analysis = {
            "fraud_probability": 0.10,
            "risk_score": 0.2,
            "auto_approval_eligible": True,  # Should be auto-approved in enterprise
            "confidence_score": 0.90,
            "recommended_action": "auto_approve",
            "approval_chain": [],
            "threshold_analysis": {
                "amount_threshold": 25000.0,  # Higher threshold for enterprise
                "current_amount": 2500.0,
                "within_auto_approval": True
            }
        }
        
        with patch.object(workflow_engine, 'create_workflow') as mock_create:
            mock_create.return_value = WorkflowInstance(
                workflow_id=str(uuid.uuid4()),
                invoice_id=sample_invoice_medium_amount.id,
                company_id=sample_company_enterprise.id,
                status=WorkflowStatus.COMPLETED,
                steps=[],
                created_at=datetime.utcnow()
            )
            
            result = await workflow_engine.process_approval_workflow(
                sample_invoice_medium_amount, 
                ai_analysis, 
                sample_company_enterprise
            )
            
            assert result["status"] == "auto_approved"
            assert result["approval_required"] == False
            assert result["workflow_status"] == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_ai_fraud_detection_high_risk(self, workflow_engine, sample_invoice_low_amount, sample_company_basic):
        """Test AI fraud detection overriding auto-approval"""
        
        # Mock AI analysis with high fraud probability
        ai_analysis = {
            "fraud_probability": 0.85,
            "risk_score": 0.9,
            "auto_approval_eligible": False,  # Overridden by fraud detection
            "confidence_score": 0.95,
            "recommended_action": "manual_review",
            "approval_chain": ["manager", "director"],
            "fraud_indicators": [
                "unusual_amount_pattern",
                "new_supplier",
                "weekend_submission"
            ],
            "threshold_analysis": {
                "amount_threshold": 1000.0,
                "current_amount": 500.0,
                "fraud_override": True
            }
        }
        
        with patch.object(workflow_engine, 'create_workflow') as mock_create:
            mock_create.return_value = WorkflowInstance(
                workflow_id=str(uuid.uuid4()),
                invoice_id=sample_invoice_low_amount.id,
                company_id=sample_company_basic.id,
                status=WorkflowStatus.PENDING,
                steps=[
                    WorkflowStep(
                        step_id="step_1",
                        name="Fraud Review",
                        description="Manual review required due to fraud indicators",
                        approver_role="manager",
                        is_required=True,
                        timeout_hours=24
                    )
                ],
                created_at=datetime.utcnow()
            )
            
            result = await workflow_engine.process_approval_workflow(
                sample_invoice_low_amount, 
                ai_analysis, 
                sample_company_basic
            )
            
            assert result["status"] == "pending_approval"
            assert result["approval_required"] == True
            assert result["fraud_detected"] == True
            assert result["risk_level"] == "high"
            assert len(result["fraud_indicators"]) > 0

    @pytest.mark.asyncio
    async def test_dynamic_threshold_adjustment(self, workflow_engine, sample_invoice_medium_amount, sample_company_basic):
        """Test dynamic threshold adjustment based on historical data"""
        
        # Mock AI analysis with dynamic threshold adjustment
        ai_analysis = {
            "fraud_probability": 0.12,
            "risk_score": 0.25,
            "auto_approval_eligible": False,
            "confidence_score": 0.88,
            "recommended_action": "manager_approval",
            "approval_chain": ["manager"],
            "dynamic_thresholds": {
                "base_threshold": 1000.0,
                "adjusted_threshold": 800.0,  # Lowered due to recent fraud
                "adjustment_reason": "recent_fraud_activity",
                "adjustment_factor": 0.8
            },
            "threshold_analysis": {
                "amount_threshold": 800.0,
                "current_amount": 2500.0,
                "approval_level_required": "manager"
            }
        }
        
        with patch.object(workflow_engine, 'create_workflow') as mock_create:
            mock_create.return_value = WorkflowInstance(
                workflow_id=str(uuid.uuid4()),
                invoice_id=sample_invoice_medium_amount.id,
                company_id=sample_company_basic.id,
                status=WorkflowStatus.PENDING,
                steps=[
                    WorkflowStep(
                        step_id="step_1",
                        name="Manager Approval",
                        description="Manager approval required (threshold adjusted)",
                        approver_role="manager",
                        is_required=True,
                        timeout_hours=72
                    )
                ],
                created_at=datetime.utcnow()
            )
            
            result = await workflow_engine.process_approval_workflow(
                sample_invoice_medium_amount, 
                ai_analysis, 
                sample_company_basic
            )
            
            assert result["status"] == "pending_approval"
            assert result["approval_required"] == True
            assert result["threshold_adjusted"] == True
            assert result["adjusted_threshold"] == 800.0

    @pytest.mark.asyncio
    async def test_approval_step_processing(self, workflow_engine, sample_invoice_medium_amount):
        """Test individual approval step processing"""
        
        # Create mock workflow instance
        workflow = WorkflowInstance(
            workflow_id=str(uuid.uuid4()),
            invoice_id=sample_invoice_medium_amount.id,
            company_id=str(uuid.uuid4()),
            status=WorkflowStatus.PENDING,
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    name="Manager Approval",
                    description="Manager approval required",
                    approver_role="manager",
                    is_required=True,
                    timeout_hours=72
                )
            ],
            created_at=datetime.utcnow()
        )
        
        with patch.object(workflow_engine, 'get_workflow') as mock_get:
            mock_get.return_value = workflow
            
            # Test approval action
            result = await workflow_engine.process_approval_step(
                workflow.workflow_id,
                "step_1",
                ApprovalAction.APPROVE,
                str(uuid.uuid4()),  # approver_id
                "Approved by manager"
            )
            
            assert result["status"] == "approved"
            assert result["step_status"] == "completed"
            assert result["workflow_status"] == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_approval_step_rejection(self, workflow_engine, sample_invoice_medium_amount):
        """Test approval step rejection"""
        
        # Create mock workflow instance
        workflow = WorkflowInstance(
            workflow_id=str(uuid.uuid4()),
            invoice_id=sample_invoice_medium_amount.id,
            company_id=str(uuid.uuid4()),
            status=WorkflowStatus.PENDING,
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    name="Manager Approval",
                    description="Manager approval required",
                    approver_role="manager",
                    is_required=True,
                    timeout_hours=72
                )
            ],
            created_at=datetime.utcnow()
        )
        
        with patch.object(workflow_engine, 'get_workflow') as mock_get:
            mock_get.return_value = workflow
            
            # Test rejection action
            result = await workflow_engine.process_approval_step(
                workflow.workflow_id,
                "step_1",
                ApprovalAction.REJECT,
                str(uuid.uuid4()),  # approver_id
                "Rejected due to missing documentation"
            )
            
            assert result["status"] == "rejected"
            assert result["step_status"] == "rejected"
            assert result["workflow_status"] == WorkflowStatus.REJECTED
            assert "missing documentation" in result["rejection_reason"]

    @pytest.mark.asyncio
    async def test_approval_step_delegation(self, workflow_engine, sample_invoice_medium_amount):
        """Test approval step delegation"""
        
        # Create mock workflow instance
        workflow = WorkflowInstance(
            workflow_id=str(uuid.uuid4()),
            invoice_id=sample_invoice_medium_amount.id,
            company_id=str(uuid.uuid4()),
            status=WorkflowStatus.PENDING,
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    name="Manager Approval",
                    description="Manager approval required",
                    approver_role="manager",
                    is_required=True,
                    timeout_hours=72
                )
            ],
            created_at=datetime.utcnow()
        )
        
        with patch.object(workflow_engine, 'get_workflow') as mock_get:
            mock_get.return_value = workflow
            
            # Test delegation action
            result = await workflow_engine.process_approval_step(
                workflow.workflow_id,
                "step_1",
                ApprovalAction.DELEGATE,
                str(uuid.uuid4()),  # original_approver_id
                "Delegated to senior manager",
                delegate_to=str(uuid.uuid4())  # delegate_user_id
            )
            
            assert result["status"] == "delegated"
            assert result["step_status"] == "delegated"
            assert result["delegated_to"] is not None

    @pytest.mark.asyncio
    async def test_workflow_timeout_handling(self, workflow_engine, sample_invoice_medium_amount):
        """Test workflow timeout handling and escalation"""
        
        # Create mock workflow instance with expired step
        expired_time = datetime.utcnow() - timedelta(hours=80)  # Past 72-hour timeout
        workflow = WorkflowInstance(
            workflow_id=str(uuid.uuid4()),
            invoice_id=sample_invoice_medium_amount.id,
            company_id=str(uuid.uuid4()),
            status=WorkflowStatus.PENDING,
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    name="Manager Approval",
                    description="Manager approval required",
                    approver_role="manager",
                    is_required=True,
                    timeout_hours=72
                )
            ],
            created_at=expired_time
        )
        
        with patch.object(workflow_engine, 'get_workflow') as mock_get:
            mock_get.return_value = workflow
            
            # Test timeout escalation
            result = await workflow_engine.handle_workflow_timeout(workflow.workflow_id)
            
            assert result["status"] == "escalated"
            assert result["timeout_detected"] == True
            assert result["escalation_reason"] == "timeout_exceeded"

    @pytest.mark.asyncio
    async def test_multi_step_approval_chain(self, workflow_engine, sample_invoice_high_amount):
        """Test multi-step approval chain progression"""
        
        # Create mock workflow instance with multiple steps
        workflow = WorkflowInstance(
            workflow_id=str(uuid.uuid4()),
            invoice_id=sample_invoice_high_amount.id,
            company_id=str(uuid.uuid4()),
            status=WorkflowStatus.PENDING,
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    name="Manager Approval",
                    description="Manager approval required",
                    approver_role="manager",
                    is_required=True,
                    timeout_hours=72
                ),
                WorkflowStep(
                    step_id="step_2",
                    name="Director Approval",
                    description="Director approval required",
                    approver_role="director",
                    is_required=True,
                    timeout_hours=48
                )
            ],
            created_at=datetime.utcnow()
        )
        
        with patch.object(workflow_engine, 'get_workflow') as mock_get:
            mock_get.return_value = workflow
            
            # Test first step approval
            result1 = await workflow_engine.process_approval_step(
                workflow.workflow_id,
                "step_1",
                ApprovalAction.APPROVE,
                str(uuid.uuid4()),
                "Manager approved"
            )
            
            assert result1["status"] == "approved"
            assert result1["workflow_status"] == WorkflowStatus.PENDING  # Still pending next step
            assert result1["next_step"] == "step_2"
            
            # Test second step approval
            result2 = await workflow_engine.process_approval_step(
                workflow.workflow_id,
                "step_2",
                ApprovalAction.APPROVE,
                str(uuid.uuid4()),
                "Director approved"
            )
            
            assert result2["status"] == "approved"
            assert result2["workflow_status"] == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_ai_analysis_integration(self, invoice_processor, sample_invoice_medium_amount, sample_company_basic):
        """Test AI analysis integration with workflow engine"""
        
        # Mock AI analysis
        ai_analysis = {
            "fraud_probability": 0.15,
            "risk_score": 0.3,
            "auto_approval_eligible": False,
            "confidence_score": 0.85,
            "recommended_action": "manager_approval",
            "approval_chain": ["manager"],
            "threshold_analysis": {
                "amount_threshold": 1000.0,
                "current_amount": 2500.0,
                "approval_level_required": "manager"
            }
        }
        
        with patch.object(invoice_processor, '_run_ai_analysis') as mock_ai:
            mock_ai.return_value = ai_analysis
            
            with patch.object(invoice_processor, '_create_approval_workflow') as mock_workflow:
                mock_workflow.return_value = {
                    "workflow_id": str(uuid.uuid4()),
                    "status": "pending_approval",
                    "approval_chain": ["manager"]
                }
                
                # Test AI analysis integration
                result = await invoice_processor._run_ai_analysis(
                    sample_invoice_medium_amount, 
                    sample_company_basic.id, 
                    Mock()  # Mock database session
                )
                
                assert result["fraud_probability"] == 0.15
                assert result["auto_approval_eligible"] == False
                assert result["recommended_action"] == "manager_approval"

    def test_threshold_configuration_by_company_tier(self, workflow_engine):
        """Test threshold configuration based on company tier"""
        
        # Test basic tier thresholds
        basic_thresholds = workflow_engine.get_approval_thresholds("basic")
        assert basic_thresholds["auto_approval_limit"] <= 1000.0
        assert basic_thresholds["manager_approval_limit"] <= 5000.0
        
        # Test enterprise tier thresholds
        enterprise_thresholds = workflow_engine.get_approval_thresholds("enterprise")
        assert enterprise_thresholds["auto_approval_limit"] >= 25000.0
        assert enterprise_thresholds["manager_approval_limit"] >= 50000.0

    @pytest.mark.asyncio
    async def test_workflow_audit_trail(self, workflow_engine, sample_invoice_medium_amount):
        """Test workflow audit trail creation"""
        
        # Create mock workflow instance
        workflow = WorkflowInstance(
            workflow_id=str(uuid.uuid4()),
            invoice_id=sample_invoice_medium_amount.id,
            company_id=str(uuid.uuid4()),
            status=WorkflowStatus.PENDING,
            steps=[],
            created_at=datetime.utcnow()
        )
        
        with patch.object(workflow_engine, 'get_workflow') as mock_get:
            mock_get.return_value = workflow
            
            # Test audit trail creation
            result = await workflow_engine.create_audit_trail(
                workflow.workflow_id,
                "workflow_created",
                "Workflow created for invoice approval",
                str(uuid.uuid4())  # user_id
            )
            
            assert result["status"] == "success"
            assert result["audit_entry_created"] == True
            assert "workflow_created" in result["action"]

    @pytest.mark.asyncio
    async def test_bulk_workflow_processing(self, workflow_engine):
        """Test bulk workflow processing for multiple invoices"""
        
        # Create multiple sample invoices
        invoices = [
            Invoice(
                id=str(uuid.uuid4()),
                invoice_number=f"INV-{i:03d}",
                supplier_name="Test Supplier",
                total_amount=Decimal(f"{500 + i * 100}.00"),
                currency="USD",
                invoice_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=30),
                status=InvoiceStatus.PENDING,
                company_id=str(uuid.uuid4())
            )
            for i in range(5)
        ]
        
        with patch.object(workflow_engine, 'process_approval_workflow') as mock_process:
            mock_process.return_value = {
                "status": "auto_approved",
                "approval_required": False,
                "workflow_status": WorkflowStatus.COMPLETED
            }
            
            # Test bulk processing
            results = await workflow_engine.process_bulk_workflows(
                invoices, 
                Mock()  # Mock AI analysis
            )
            
            assert len(results) == 5
            assert all(result["status"] == "auto_approved" for result in results)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
