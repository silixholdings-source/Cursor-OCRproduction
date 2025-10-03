from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, JSON, Index, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from src.core.database import Base

class AuditAction(str, enum.Enum):
    """Audit action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    POST = "post"
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    ROLE_CHANGE = "role_change"
    SUBSCRIPTION_CHANGE = "subscription_change"
    FILE_UPLOAD = "file_upload"
    OCR_PROCESS = "ocr_process"
    ERP_SYNC = "erp_sync"

class AuditResourceType(str, enum.Enum):
    """Audit resource types"""
    USER = "User"
    COMPANY = "Company"
    INVOICE = "Invoice"
    INVOICE_LINE = "InvoiceLine"
    APPROVAL = "Approval"
    SUBSCRIPTION = "Subscription"
    FILE = "File"
    WORKFLOW = "Workflow"
    ERP_CONNECTION = "ERPConnection"

class AuditLog(Base):
    """Audit log model for compliance and security tracking"""
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Audit event details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    resource_type = Column(Enum(AuditResourceType), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # User and company context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    
    # Timestamp and session
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    session_id = Column(String(255), nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_id = Column(String(255), nullable=True)
    
    # Change details
    details = Column(JSON, default=dict, nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Security and compliance
    risk_level = Column(String(20), nullable=True)  # low, medium, high, critical
    compliance_tags = Column(JSON, default=list, nullable=False)
    data_classification = Column(String(20), nullable=True)  # public, internal, confidential, restricted
    
    # Relationships
    user = relationship("models.user.User", back_populates="audit_logs")
    company = relationship("models.company.Company", back_populates="audit_logs")
    # invoice relationship removed due to complex join conditions - can be added back later if needed
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_timestamp_company', 'timestamp', 'company_id'),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}:{self.resource_id}')>"
    
    @property
    def is_high_risk(self) -> bool:
        """Check if this audit event is high risk"""
        return self.risk_level in ["high", "critical"]
    
    @property
    def is_compliance_related(self) -> bool:
        """Check if this audit event is compliance-related"""
        return len(self.compliance_tags) > 0
    
    def add_compliance_tag(self, tag: str):
        """Add a compliance tag to the audit log"""
        if tag not in self.compliance_tags:
            self.compliance_tags.append(tag)
    
    def set_risk_level(self, level: str):
        """Set the risk level for this audit event"""
        valid_levels = ["low", "medium", "high", "critical"]
        if level.lower() in valid_levels:
            self.risk_level = level.lower()
    
    def add_change_detail(self, field: str, old_value, new_value):
        """Add a change detail to track field modifications"""
        if not self.old_values:
            self.old_values = {}
        if not self.new_values:
            self.new_values = {}
        
        self.old_values[field] = old_value
        self.new_values[field] = new_value
        
        # Update the details with change summary
        if "changes" not in self.details:
            self.details["changes"] = []
        
        self.details["changes"].append({
            "field": field,
            "old_value": str(old_value) if old_value is not None else None,
            "new_value": str(new_value) if new_value is not None else None,
            "timestamp": func.now().isoformat()
        })
    
    def add_security_context(self, ip_address: str = None, user_agent: str = None, session_id: str = None):
        """Add security context information"""
        if ip_address:
            self.ip_address = ip_address
        if user_agent:
            self.user_agent = user_agent
        if session_id:
            self.session_id = session_id
    
    def add_request_context(self, method: str = None, path: str = None, request_id: str = None):
        """Add request context information"""
        if method:
            self.request_method = method
        if path:
            self.request_path = path
        if request_id:
            self.request_id = request_id
