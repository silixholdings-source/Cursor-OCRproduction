from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, JSON, Numeric, Date, and_
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from src.core.database import Base

class InvoiceStatus(str, enum.Enum):
    """Invoice processing status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    POSTED_TO_ERP = "posted_to_erp"
    ERROR = "error"
    CANCELLED = "cancelled"
    DELETED = "deleted"

class InvoiceType(str, enum.Enum):
    """Invoice type"""
    INVOICE = "invoice"
    CREDIT_MEMO = "credit_memo"
    DEBIT_MEMO = "debit_memo"
    RECURRING = "recurring"

class Invoice(Base):
    """Invoice model for multi-tenant SaaS application"""
    __tablename__ = "invoices"
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Invoice identification
    invoice_number = Column(String(255), nullable=False, index=True)
    supplier_name = Column(String(255), nullable=False, index=True)
    supplier_email = Column(String(255), nullable=True)
    supplier_phone = Column(String(20), nullable=True)
    supplier_address = Column(Text, nullable=True)
    supplier_tax_id = Column(String(100), nullable=True)
    
    # Invoice details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    total_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0, nullable=False)
    tax_rate = Column(Numeric(5, 4), default=0, nullable=False)
    subtotal = Column(Numeric(15, 2), nullable=False)
    total_with_tax = Column(Numeric(15, 2), nullable=False)
    
    # Processing status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    type = Column(Enum(InvoiceType), default=InvoiceType.INVOICE, nullable=False)
    
    # Approval workflow
    current_approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approval_chain = Column(JSON, default=list, nullable=False)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # ERP integration
    posted_to_erp = Column(Boolean, default=False, nullable=False)
    erp_document_id = Column(String(255), nullable=True)
    erp_posting_date = Column(DateTime(timezone=True), nullable=True)
    erp_error_message = Column(Text, nullable=True)
    
    # OCR and AI data
    ocr_data = Column(JSON, default=dict, nullable=False)
    ai_gl_coding = Column(JSON, default=dict, nullable=False)
    fraud_score = Column(Numeric(3, 2), nullable=True)
    confidence_score = Column(Numeric(3, 2), nullable=True)
    
    # Workflow and processing
    workflow_data = Column(JSON, default=dict, nullable=False)
    processing_priority = Column(Integer, default=5, nullable=False)
    estimated_processing_time = Column(Integer, nullable=True)  # in minutes
    
    # File attachments
    original_file_path = Column(String(500), nullable=True)
    processed_file_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)
    
    # Business logic
    po_number = Column(String(255), nullable=True)
    receipt_number = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    cost_center = Column(String(100), nullable=True)
    project_code = Column(String(100), nullable=True)
    
    # Notes and metadata
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list, nullable=False)
    
    # Company relationship (multi-tenant)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # User relationships
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("models.company.Company", back_populates="invoices")
    created_by = relationship("models.user.User", foreign_keys=[created_by_id], back_populates="invoices")
    current_approver = relationship("models.user.User", foreign_keys=[current_approver_id])
    approved_by = relationship("models.user.User", foreign_keys=[approved_by_id])
    line_items = relationship("models.invoice_line.InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    # audit_logs relationship removed due to complex join conditions - can be added back later if needed
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', status='{self.status}')>"
    
    @property
    def is_approved(self) -> bool:
        """Check if invoice is approved"""
        return self.status == InvoiceStatus.APPROVED
    
    @property
    def is_posted(self) -> bool:
        """Check if invoice is posted to ERP"""
        return self.status == InvoiceStatus.POSTED_TO_ERP
    
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        if not self.due_date:
            return False
        from datetime import date
        return self.due_date < date.today()
    
    @property
    def days_overdue(self) -> int:
        """Get number of days overdue"""
        if not self.is_overdue:
            return 0
        from datetime import date
        return (date.today() - self.due_date).days
    
    def can_be_approved_by(self, user_id: uuid.UUID) -> bool:
        """Check if user can approve this invoice"""
        if self.status != InvoiceStatus.PENDING_APPROVAL:
            return False
        
        # Check if user is in approval chain
        for approver in self.approval_chain:
            if approver.get("user_id") == str(user_id):
                return approver.get("status") == "pending"
        return False
    
    def add_approval_step(self, user_id: uuid.UUID, order: int, threshold: float = None):
        """Add an approval step to the chain"""
        step = {
            "user_id": str(user_id),
            "order": order,
            "status": "pending",
            "threshold": threshold,
            "created_at": func.now().isoformat()
        }
        self.approval_chain.append(step)
    
    def mark_approved(self, user_id: uuid.UUID):
        """Mark invoice as approved by user"""
        self.status = InvoiceStatus.APPROVED
        self.approved_by_id = user_id
        self.approved_at = func.now()
        
        # Update approval chain
        for step in self.approval_chain:
            if step.get("user_id") == str(user_id):
                step["status"] = "approved"
                step["approved_at"] = func.now().isoformat()
                break
    
    def mark_rejected(self, user_id: uuid.UUID, reason: str):
        """Mark invoice as rejected by user"""
        self.status = InvoiceStatus.REJECTED
        self.rejection_reason = reason
        
        # Update approval chain
        for step in self.approval_chain:
            if step.get("user_id") == str(user_id):
                step["status"] = "rejected"
                step["rejected_at"] = func.now().isoformat()
                step["rejection_reason"] = reason
                break
