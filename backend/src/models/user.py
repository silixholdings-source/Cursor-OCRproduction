from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from src.core.database import Base

class UserRole(str, enum.Enum):
    """User roles within a company"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

class UserStatus(str, enum.Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class User(Base):
    """User model for multi-tenant SaaS application"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile fields
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Company relationship (multi-tenant)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Role and status
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    
    # Security fields
    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_2fa_enabled = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # SSO and Enterprise Authentication
    auth_provider = Column(String(50), default="local", nullable=False)  # local, azure_ad, office365, active_directory, saml
    azure_ad_id = Column(String(255), nullable=True)  # Azure AD object ID
    azure_tenant_id = Column(String(255), nullable=True)  # Azure tenant ID
    ldap_dn = Column(String(500), nullable=True)  # LDAP distinguished name
    saml_name_id = Column(String(255), nullable=True)  # SAML NameID
    sso_session_id = Column(String(255), nullable=True)  # SSO session identifier
    
    # Extended profile from SSO
    job_title = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)
    office_location = Column(String(200), nullable=True)
    manager_email = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("models.company.Company", back_populates="users")
    invoices = relationship("models.invoice.Invoice", foreign_keys="models.invoice.Invoice.created_by_id", back_populates="created_by")
    audit_logs = relationship("models.audit.AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', company_id={self.company_id})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        from datetime import datetime, UTC
        if self.locked_until is None:
            return False
        # Make sure both datetimes are timezone-aware for comparison
        now = datetime.now(UTC)
        locked_until = self.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=UTC)
        return locked_until > now
    
    def can_access_company(self, company_id: UUID) -> bool:
        """Check if user can access a specific company"""
        return self.company_id == company_id and self.is_active
