"""
Unit tests for workflow engine service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta, UTC
import uuid

from src.services.workflow import WorkflowEngine, WorkflowStepType, WorkflowStepStatus
from src.models.invoice import Invoice, InvoiceStatus
from src.models.user import User, UserRole, UserStatus
from src.models.company import Company, CompanyTier

class TestWorkflowEngine:
    """Test workflow engine functionality"""
    
    def test_workflow_engine_initialization(self):
        """Test workflow engine initializes correctly"""
        engine = WorkflowEngine()
        
        # Check default thresholds
        assert engine.default_approval_thresholds["basic"] == 1000.0
        assert engine.default_approval_thresholds["professional"] == 5000.0
        assert engine.default_approval_thresholds["enterprise"] == 25000.0
    
    def test_create_approval_workflow_basic_tier_below_threshold(self, db_session):
        """Test workflow creation for basic tier below threshold"""
        engine = WorkflowEngine()
        
        # Create test company and invoice
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com",
            tier=CompanyTier.GROWTH
        )
        db_session.add(company)
        db_session.commit()
        
        # Create a test user as the invoice creator
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        
        # Create a manager user for approval
        manager = User(
            id=uuid.uuid4(),
            email="manager@example.com",
            username="manager",
            hashed_password="hash",
            first_name="Test",
            last_name="Manager",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(manager)
        db_session.commit()
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=500.00,  # Below basic threshold
            subtotal=500.00,
            total_with_tax=500.00,
            company_id=company.id,
            created_by_id=user.id
        )
        db_session.add(invoice)
        db_session.commit()
        
        # Create workflow
        workflow_data = engine.create_approval_workflow(invoice, "basic", db_session)
        
        # Check workflow structure
        assert workflow_data["status"] == "active"
        assert workflow_data["current_step"] == 1
        assert workflow_data["threshold"] == 1000.0
        
        # Should have single approval step
        steps = workflow_data["steps"]
        assert len(steps) == 1
        assert steps[0]["type"] == WorkflowStepType.APPROVAL
        assert steps[0]["order"] == 1
        assert steps[0]["approver_role"] == UserRole.MANAGER
        assert steps[0]["status"] == WorkflowStepStatus.PENDING
        
        # Check invoice status
        assert invoice.status == InvoiceStatus.PENDING_APPROVAL
        assert invoice.current_approver_id is not None
    
    def test_create_approval_workflow_professional_tier_above_threshold(self, db_session):
        """Test workflow creation for professional tier above threshold"""
        engine = WorkflowEngine()
        
        # Create test company and invoice
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com",
            tier=CompanyTier.PROFESSIONAL
        )
        db_session.add(company)
        db_session.commit()
        
        # Create a test user as the invoice creator
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        
        # Create manager and admin users for approval
        manager = User(
            id=uuid.uuid4(),
            email="manager@example.com",
            username="manager",
            hashed_password="hash",
            first_name="Test",
            last_name="Manager",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(manager)
        
        admin = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            username="admin",
            hashed_password="hash",
            first_name="Test",
            last_name="Admin",
            company_id=company.id,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        db_session.add(admin)
        db_session.commit()
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=7500.00,  # Above professional threshold
            subtotal=7500.00,
            total_with_tax=7500.00,
            company_id=company.id,
            created_by_id=user.id
        )
        db_session.add(invoice)
        db_session.commit()
        
        # Create workflow
        workflow_data = engine.create_approval_workflow(invoice, "professional", db_session)
        
        # Check workflow structure
        assert workflow_data["status"] == "active"
        assert workflow_data["current_step"] == 1
        assert workflow_data["threshold"] == 5000.0
        
        # Should have two approval steps
        steps = workflow_data["steps"]
        assert len(steps) == 2
        
        # First step: Manager approval
        assert steps[0]["type"] == WorkflowStepType.APPROVAL
        assert steps[0]["order"] == 1
        assert steps[0]["approver_role"] == UserRole.MANAGER
        assert steps[0]["threshold"] == 5000.0
        
        # Second step: Admin approval
        assert steps[1]["type"] == WorkflowStepType.APPROVAL
        assert steps[1]["order"] == 2
        assert steps[1]["approver_role"] == UserRole.ADMIN
        assert steps[1]["threshold"] is None
    
    def test_find_approver_success(self, db_session):
        """Test finding approver with specified role"""
        engine = WorkflowEngine()
        
        # Create test company
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        # Create test user with manager role
        user = User(
            id=uuid.uuid4(),
            email="manager@test.com",
            username="manager",
            hashed_password="hash",
            first_name="Test",
            last_name="Manager",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        # Find approver
        approver_id = engine._find_approver(company.id, UserRole.MANAGER, db_session)
        
        assert approver_id == user.id
    
    def test_find_approver_not_found(self, db_session):
        """Test finding approver when none exists"""
        engine = WorkflowEngine()
        
        # Create test company
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        # Try to find approver (none exists)
        approver_id = engine._find_approver(company.id, UserRole.MANAGER, db_session)
        
        assert approver_id is None
    
    def test_get_next_approver_single_step_workflow(self, db_session):
        """Test getting next approver for single step workflow"""
        engine = WorkflowEngine()
        
        # Create test company and users
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        manager = User(
            id=uuid.uuid4(),
            email="manager@test.com",
            username="manager",
            hashed_password="hash",
            first_name="Test",
            last_name="Manager",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(manager)
        db_session.commit()
        
        # Create invoice with single step workflow
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=500.00,
            subtotal=500.00,
            total_with_tax=500.00,
            company_id=company.id,
            created_by_id=manager.id,
            current_approver_id=manager.id,
            workflow_data={
                "workflow_id": str(uuid.uuid4()),
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 1,
                        "approver_role": UserRole.MANAGER,
                        "status": WorkflowStepStatus.COMPLETED,
                        "completed_at": datetime.now(UTC).isoformat()
                    }
                ],
                "current_step": 1,
                "status": "active"
            }
        )
        db_session.add(invoice)
        db_session.commit()
        
        # Get next approver (should be None for single step)
        next_approver = engine.get_next_approver(invoice, db_session)
        
        assert next_approver is None
        assert invoice.workflow_data["status"] == "completed"
    
    def test_get_next_approver_multi_step_workflow(self, db_session):
        """Test getting next approver for multi-step workflow"""
        engine = WorkflowEngine()
        
        # Create test company and users
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        manager = User(
            id=uuid.uuid4(),
            email="manager@test.com",
            username="manager",
            hashed_password="hash",
            first_name="Test",
            last_name="Manager",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(manager)
        
        admin = User(
            id=uuid.uuid4(),
            email="admin@test.com",
            username="admin",
            hashed_password="hash",
            first_name="Test",
            last_name="Admin",
            company_id=company.id,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        db_session.add(admin)
        db_session.commit()
        
        # Create a test user as the invoice creator
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        # Create invoice with multi-step workflow
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=7500.00,
            subtotal=7500.00,
            total_with_tax=7500.00,
            company_id=company.id,
            created_by_id=user.id,
            current_approver_id=manager.id,
            workflow_data={
                "workflow_id": str(uuid.uuid4()),
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 1,
                        "approver_role": UserRole.MANAGER,
                        "status": WorkflowStepStatus.COMPLETED,
                        "completed_at": datetime.now(UTC).isoformat()
                    },
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 2,
                        "approver_role": UserRole.ADMIN,
                        "status": WorkflowStepStatus.PENDING
                    }
                ],
                "current_step": 1,
                "status": "active"
            }
        )
        db_session.add(invoice)
        db_session.commit()
        
        # Get next approver (should be admin)
        next_approver = engine.get_next_approver(invoice, db_session)
        
        assert next_approver is not None
        assert next_approver.id == admin.id
        assert invoice.workflow_data["current_step"] == 2
        assert invoice.current_approver_id == admin.id
    
    def test_process_approval_approve_single_step(self, db_session):
        """Test processing approval for single step workflow"""
        engine = WorkflowEngine()
        
        # Create test company and user
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        approver = User(
            id=uuid.uuid4(),
            email="approver@test.com",
            username="approver",
            hashed_password="hash",
            first_name="Test",
            last_name="Approver",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(approver)
        db_session.commit()
        
        # Create a test user as the invoice creator
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        # Create invoice with workflow
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=500.00,
            subtotal=500.00,
            total_with_tax=500.00,
            company_id=company.id,
            created_by_id=user.id,
            current_approver_id=approver.id,
            workflow_data={
                "workflow_id": str(uuid.uuid4()),
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 1,
                        "approver_role": UserRole.MANAGER,
                        "status": WorkflowStepStatus.PENDING
                    }
                ],
                "current_step": 1,
                "status": "active"
            }
        )
        db_session.add(invoice)
        db_session.commit()
        
        # Process approval
        result = engine.process_approval_sync(invoice, approver, True, db_session)
        
        # Check result
        assert result["status"] == "approved"
        assert result["workflow_status"] == "completed"
        
        # Refresh invoice from database to get updated values
        db_session.refresh(invoice)
        
        # Check invoice status
        assert invoice.status == InvoiceStatus.APPROVED
        assert invoice.approved_by_id == approver.id
        assert invoice.approved_at is not None
        
        # Check workflow status
        assert invoice.workflow_data["status"] == "completed"
        assert invoice.workflow_data["steps"][0]["status"] == WorkflowStepStatus.COMPLETED
    
    def test_process_approval_reject(self, db_session):
        """Test processing rejection"""
        engine = WorkflowEngine()
        
        # Create test company and user
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        approver = User(
            id=uuid.uuid4(),
            email="approver@test.com",
            username="approver",
            hashed_password="hash",
            first_name="Test",
            last_name="Approver",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(approver)
        db_session.commit()
        
        # Create a test user as the invoice creator
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        # Create invoice with workflow
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=500.00,
            subtotal=500.00,
            total_with_tax=500.00,
            company_id=company.id,
            created_by_id=user.id,
            current_approver_id=approver.id,
            workflow_data={
                "workflow_id": str(uuid.uuid4()),
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 1,
                        "approver_role": UserRole.MANAGER,
                        "status": WorkflowStepStatus.PENDING
                    }
                ],
                "current_step": 1,
                "status": "active"
            }
        )
        db_session.add(invoice)
        db_session.commit()
        
        # Process rejection
        result = engine.process_approval_sync(invoice, approver, False, db_session, "Invalid invoice")
        
        # Check result
        assert result["status"] == "rejected"
        assert result["workflow_status"] == "rejected"
        
        # Refresh invoice from database to get updated values
        db_session.refresh(invoice)
        
        # Check invoice status
        assert invoice.status == InvoiceStatus.REJECTED
        assert invoice.rejection_reason == "Invalid invoice"
        
        # Check workflow status
        assert invoice.workflow_data["status"] == "rejected"
        assert invoice.workflow_data["steps"][0]["status"] == WorkflowStepStatus.FAILED
    
    def test_delegate_approval_success(self, db_session):
        """Test successful approval delegation"""
        engine = WorkflowEngine()
        
        # Create test company and users
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        from_user = User(
            id=uuid.uuid4(),
            email="from@test.com",
            username="from",
            hashed_password="hash",
            first_name="Test",
            last_name="From",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(from_user)
        
        to_user = User(
            id=uuid.uuid4(),
            email="to@test.com",
            username="to",
            hashed_password="hash",
            first_name="Test",
            last_name="To",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(to_user)
        db_session.commit()
        
        # Create a test user as the invoice creator
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        # Create invoice with workflow
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=500.00,
            subtotal=500.00,
            total_with_tax=500.00,
            company_id=company.id,
            created_by_id=user.id,
            current_approver_id=from_user.id,
            workflow_data={
                "workflow_id": str(uuid.uuid4()),
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 1,
                        "approver_role": UserRole.MANAGER,
                        "status": WorkflowStepStatus.PENDING
                    }
                ],
                "current_step": 1,
                "status": "active"
            }
        )
        db_session.add(invoice)
        db_session.commit()
        
        # Delegate approval
        result = engine.delegate_approval(invoice, from_user, to_user, "Out of office", db_session)
        
        # Check result
        assert result["status"] == "delegated"
        assert result["delegation_reason"] == "Out of office"
        
        # Check invoice current approver
        assert invoice.current_approver_id == to_user.id
        
        # Check workflow step status
        assert invoice.workflow_data["steps"][0]["status"] == WorkflowStepStatus.DELEGATED
        
        # Check delegation step was added
        assert len(invoice.workflow_data["steps"]) == 2
        delegation_step = invoice.workflow_data["steps"][1]
        assert delegation_step["type"] == WorkflowStepType.DELEGATION
        assert delegation_step["delegated_from"] == str(from_user.id)
        assert delegation_step["delegated_to"] == str(to_user.id)
    
    def test_delegate_approval_wrong_step_type(self, db_session):
        """Test delegation fails for wrong step type"""
        engine = WorkflowEngine()
        
        # Create test company and users
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        from_user = User(
            id=uuid.uuid4(),
            email="from@test.com",
            username="from",
            hashed_password="hash",
            first_name="Test",
            last_name="From",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(from_user)
        
        to_user = User(
            id=uuid.uuid4(),
            email="to@test.com",
            username="to",
            hashed_password="hash",
            first_name="Test",
            last_name="To",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(to_user)
        db_session.commit()
        
        # Create a test user as the invoice creator
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        # Create invoice with non-approval workflow step
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=500.00,
            subtotal=500.00,
            total_with_tax=500.00,
            company_id=company.id,
            created_by_id=user.id,
            current_approver_id=from_user.id,
            workflow_data={
                "workflow_id": str(uuid.uuid4()),
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.NOTIFICATION,  # Not approval
                        "order": 1,
                        "status": WorkflowStepStatus.PENDING
                    }
                ],
                "current_step": 1,
                "status": "active"
            }
        )
        db_session.add(invoice)
        db_session.commit()
        
        # Try to delegate (should fail)
        with pytest.raises(ValueError, match="Only approval steps can be delegated"):
            engine.delegate_approval(invoice, from_user, to_user, "Out of office", db_session)
    
    def test_get_workflow_summary(self):
        """Test getting workflow summary"""
        engine = WorkflowEngine()
        
        # Create invoice with workflow
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
                        invoice_date=datetime.now().date(),
            total_amount=500.00,
            workflow_data={
                "workflow_id": str(uuid.uuid4()),
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 1,
                        "status": WorkflowStepStatus.COMPLETED
                    },
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 2,
                        "status": WorkflowStepStatus.PENDING
                    }
                ],
                "current_step": 2,
                "status": "active",
                "threshold": 1000.0,
                "created_at": datetime.now(UTC).isoformat()
            }
        )
        
        # Get summary
        summary = engine.get_workflow_summary(invoice)
        
        # Check summary structure
        assert summary["workflow_id"] is not None
        assert summary["status"] == "active"
        assert summary["current_step"] == 2
        assert summary["total_steps"] == 2
        assert summary["completed_steps"] == 1
        assert summary["pending_steps"] == 1
        assert summary["failed_steps"] == 0
        assert summary["threshold"] == 1000.0
        assert "created_at" in summary
        assert "steps" in summary
    
    def test_get_workflow_summary_no_workflow(self):
        """Test getting workflow summary when no workflow exists"""
        engine = WorkflowEngine()
        
        # Create invoice without workflow
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
                        invoice_date=datetime.now().date(),
            total_amount=500.00
        )
        
        # Get summary
        summary = engine.get_workflow_summary(invoice)
        
        assert summary["status"] == "no_workflow"
    
    def test_can_user_approve_success(self):
        """Test user can approve when conditions are met"""
        engine = WorkflowEngine()
        
        # Create test user and invoice
        user = User(
            id=uuid.uuid4(),
            email="approver@test.com",
            username="approver",
            hashed_password="hash",
            first_name="Test",
            last_name="Approver",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
                        invoice_date=datetime.now().date(),
            total_amount=500.00,
            current_approver_id=user.id,
            workflow_data={
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 1,
                        "approver_role": UserRole.MANAGER,
                        "status": WorkflowStepStatus.PENDING
                    }
                ],
                "current_step": 1
            }
        )
        
        # Check if user can approve
        can_approve = engine.can_user_approve(invoice, user)
        
        assert can_approve is True
    
    def test_can_user_approve_wrong_user(self):
        """Test user cannot approve when not current approver"""
        engine = WorkflowEngine()
        
        # Create test users and invoice
        current_approver = User(
            id=uuid.uuid4(),
            email="current@test.com",
            username="current",
            hashed_password="hash",
            first_name="Test",
            last_name="Current",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        
        other_user = User(
            id=uuid.uuid4(),
            email="other@test.com",
            username="other",
            hashed_password="hash",
            first_name="Test",
            last_name="Other",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
                        invoice_date=datetime.now().date(),
            total_amount=500.00,
            current_approver_id=current_approver.id,
            workflow_data={
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 1,
                        "approver_role": UserRole.MANAGER,
                        "status": WorkflowStepStatus.PENDING
                    }
                ],
                "current_step": 1
            }
        )
        
        # Check if other user can approve
        can_approve = engine.can_user_approve(invoice, other_user)
        
        assert can_approve is False
    
    def test_can_user_approve_wrong_role(self):
        """Test user cannot approve when role doesn't match"""
        engine = WorkflowEngine()
        
        # Create test user and invoice
        user = User(
            id=uuid.uuid4(),
            email="approver@test.com",
            username="approver",
            hashed_password="hash",
            first_name="Test",
            last_name="Approver",
            role=UserRole.USER,  # Wrong role
            status=UserStatus.ACTIVE
        )
        
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
                        invoice_date=datetime.now().date(),
            total_amount=500.00,
            current_approver_id=user.id,
            workflow_data={
                "steps": [
                    {
                        "step_id": str(uuid.uuid4()),
                        "type": WorkflowStepType.APPROVAL,
                        "order": 1,
                        "approver_role": UserRole.MANAGER,  # Required role
                        "status": WorkflowStepStatus.PENDING
                    }
                ],
                "current_step": 1
            }
        )
        
        # Check if user can approve
        can_approve = engine.can_user_approve(invoice, user)
        
        assert can_approve is False
    
    def test_get_pending_approvals(self, db_session):
        """Test getting pending approvals for user"""
        engine = WorkflowEngine()
        
        # Create test company and users
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        approver = User(
            id=uuid.uuid4(),
            email="approver@test.com",
            username="approver",
            hashed_password="hash",
            first_name="Test",
            last_name="Approver",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(approver)
        db_session.commit()
        
        # Create a test user as the invoice creator
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        # Create pending invoice
        pending_invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=500.00,
            subtotal=500.00,
            total_with_tax=500.00,
            company_id=company.id,
            created_by_id=user.id,
            current_approver_id=approver.id,
            status=InvoiceStatus.PENDING_APPROVAL
        )
        db_session.add(pending_invoice)
        
        # Create approved invoice
        approved_invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-002",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=600.00,
            subtotal=600.00,
            total_with_tax=600.00,
            company_id=company.id,
            created_by_id=user.id,
            current_approver_id=approver.id,
            status=InvoiceStatus.APPROVED
        )
        db_session.add(approved_invoice)
        db_session.commit()
        
        # Get pending approvals
        pending_approvals = engine.get_pending_approvals(approver, db_session)
        
        # Should only return pending invoice
        assert len(pending_approvals) == 1
        assert pending_approvals[0].id == pending_invoice.id
        assert pending_approvals[0].status == InvoiceStatus.PENDING_APPROVAL
    
    def test_get_overdue_approvals(self, db_session):
        """Test getting overdue approvals"""
        engine = WorkflowEngine()
        
        # Create test company and user
        company = Company(
            id=uuid.uuid4(),
            name="Test Company",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        approver = User(
            id=uuid.uuid4(),
            email="approver@test.com",
            username="approver",
            hashed_password="hash",
            first_name="Test",
            last_name="Approver",
            company_id=company.id,
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
        db_session.add(approver)
        db_session.commit()
        
        # Create a test user as the invoice creator
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        # Create overdue invoice (created 5 days ago)
        overdue_invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=500.00,
            subtotal=500.00,
            total_with_tax=500.00,
            company_id=company.id,
            created_by_id=user.id,
            current_approver_id=approver.id,
            status=InvoiceStatus.PENDING_APPROVAL,
            created_at=datetime.now(UTC) - timedelta(days=5)
        )
        db_session.add(overdue_invoice)
        
        # Create recent invoice (created 1 day ago)
        recent_invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number="INV-002",
            supplier_name="Test Supplier",
            invoice_date=datetime.now().date(),
            total_amount=600.00,
            subtotal=600.00,
            total_with_tax=600.00,
            company_id=company.id,
            created_by_id=user.id,
            current_approver_id=approver.id,
            status=InvoiceStatus.PENDING_APPROVAL,
            created_at=datetime.now(UTC) - timedelta(days=1)
        )
        db_session.add(recent_invoice)
        db_session.commit()
        
        # Get overdue approvals (default 3 days)
        overdue_approvals = engine.get_overdue_approvals(approver, db_session)
        
        # Should only return overdue invoice
        assert len(overdue_approvals) == 1
        assert overdue_approvals[0].id == overdue_invoice.id
        
        # Test with custom days
        overdue_approvals = engine.get_overdue_approvals(approver, db_session, days_overdue=1)
        
        # Should return both invoices
        assert len(overdue_approvals) == 2
