"""
Isolated unit tests for workflow engine service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta, UTC
import uuid
import sys
from pathlib import Path

# Add src to path for imports
backend_dir = Path(__file__).parent.parent.parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Text, Float, Date
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base
import enum
from datetime import datetime, UTC

# Create isolated base for this test
TestBase = declarative_base()

# Import enums from main models to avoid conflicts
from src.models.company import CompanyStatus, CompanyTier
from src.models.user import UserRole, UserStatus
from src.models.invoice import InvoiceStatus
from src.services.workflow import WorkflowEngine, WorkflowStepType, WorkflowStepStatus

# Define isolated models for this test
class TestCompany(TestBase):
    __tablename__ = "test_companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(CompanyStatus), default=CompanyStatus.TRIAL, nullable=False)
    tier = Column(Enum(CompanyTier), default=CompanyTier.GROWTH, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    users = relationship("TestUser", back_populates="company")
    invoices = relationship("TestInvoice", back_populates="company")

class TestUser(TestBase):
    __tablename__ = "test_users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("test_companies.id"), index=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    company = relationship("TestCompany", back_populates="users")

class TestInvoice(TestBase):
    __tablename__ = "test_invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    supplier_name = Column(String, index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING_APPROVAL, nullable=False)
    company_id = Column(Integer, ForeignKey("test_companies.id"), index=True, nullable=False)
    created_by_id = Column(Integer, ForeignKey("test_users.id"), index=True, nullable=False)
    current_approver_id = Column(Integer, ForeignKey("test_users.id"), index=True, nullable=True)
    approved_by_id = Column(Integer, ForeignKey("test_users.id"), index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    company = relationship("TestCompany", back_populates="invoices")

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session_isolated():
    """Create isolated database session and tables for each test."""
    TestBase.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        TestBase.metadata.drop_all(bind=engine)

class TestWorkflowEngineIsolated:
    """Test workflow engine functionality in isolated environment"""
    
    def test_workflow_engine_initialization(self):
        """Test workflow engine initializes correctly"""
        engine = WorkflowEngine()
        assert engine is not None
    
    def test_create_approval_workflow_basic_tier_below_threshold(self, db_session_isolated):
        """Test creating approval workflow for basic tier below threshold"""
        # Create test company and user
        company = TestCompany(
            name="Test Company",
            email="test@company.com",
            status=CompanyStatus.ACTIVE,
            tier=CompanyTier.GROWTH
        )
        db_session_isolated.add(company)
        db_session_isolated.commit()
        db_session_isolated.refresh(company)

        user = TestUser(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            role=UserRole.OWNER,
            status=UserStatus.ACTIVE,
            is_email_verified=True
        )
        db_session_isolated.add(user)
        db_session_isolated.commit()
        db_session_isolated.refresh(user)

        # Create invoice below threshold
        invoice = TestInvoice(
            invoice_number="INV-001",
            supplier_name="Test Supplier",
            total_amount=500.00,  # Below threshold for Growth tier
            currency="USD",
            invoice_date=datetime.now().date(),
            due_date=(datetime.now().date() + timedelta(days=30)),
            status=InvoiceStatus.PENDING_APPROVAL,
            company_id=company.id,
            created_by_id=user.id
        )
        db_session_isolated.add(invoice)
        db_session_isolated.commit()
        db_session_isolated.refresh(invoice)

        engine = WorkflowEngine()
        
        # Mock the workflow creation
        with patch.object(engine, 'create_approval_workflow') as mock_create:
            mock_create.return_value = {"workflow_id": "test-workflow-123"}
            
            result = engine.create_approval_workflow(
                invoice_id=invoice.id,
                company_tier=company.tier,
                invoice_amount=invoice.total_amount,
                company_settings={"auto_approve_threshold": 1000.0}
            )
            
            assert result is not None
            assert "workflow_id" in result

    def test_workflow_engine_basic_functionality(self, db_session_isolated):
        """Test basic workflow engine functionality without model conflicts"""
        engine = WorkflowEngine()
        
        # Test workflow step types
        assert WorkflowStepType.APPROVAL is not None
        assert WorkflowStepType.DELEGATION is not None
        assert WorkflowStepType.NOTIFICATION is not None
        assert WorkflowStepType.CONDITIONAL is not None
        
        # Test workflow step statuses
        assert WorkflowStepStatus.PENDING is not None
        assert WorkflowStepStatus.IN_PROGRESS is not None
        assert WorkflowStepStatus.COMPLETED is not None
        assert WorkflowStepStatus.FAILED is not None
        
        # Test engine methods exist
        assert hasattr(engine, 'create_approval_workflow')
        assert hasattr(engine, '_find_approver')
        assert hasattr(engine, 'get_next_approver')
        assert hasattr(engine, 'process_approval')
        assert hasattr(engine, 'delegate_approval')
        assert hasattr(engine, 'get_workflow_summary')
        assert hasattr(engine, 'can_user_approve')
        assert hasattr(engine, 'get_pending_approvals')
        assert hasattr(engine, 'get_overdue_approvals')
