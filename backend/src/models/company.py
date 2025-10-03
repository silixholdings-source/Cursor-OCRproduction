from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from src.core.database import Base

class CompanyStatus(str, enum.Enum):
    """Company subscription status"""
    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PENDING_ACTIVATION = "pending_activation"

class CompanyTier(str, enum.Enum):
    """Company subscription tiers - Premium South African Pricing"""
    GROWTH = "growth"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class Company(Base):
    """Company model for multi-tenant SaaS application"""
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Company information
    name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Contact information
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Business information
    tax_id = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    
    # Subscription and billing
    status = Column(Enum(CompanyStatus), default=CompanyStatus.PENDING_ACTIVATION, nullable=False)
    tier = Column(Enum(CompanyTier), default=CompanyTier.GROWTH, nullable=False)
    subscription_id = Column(String(255), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Company settings and configuration
    settings = Column(JSON, default=dict, nullable=False)
    features = Column(JSON, default=dict, nullable=False)
    
    # SSO and Enterprise Authentication
    auth_provider = Column(String(50), default="local", nullable=False)  # local, azure_ad, office365, active_directory, saml
    azure_tenant_id = Column(String(255), nullable=True)  # Azure AD tenant ID
    azure_domain = Column(String(255), nullable=True)  # Verified Azure domain
    ldap_domain = Column(String(255), nullable=True)  # LDAP domain
    saml_entity_id = Column(String(255), nullable=True)  # SAML entity ID
    sso_enabled = Column(Boolean, default=False, nullable=False)
    auto_provision_users = Column(Boolean, default=True, nullable=False)
    
    # Limits and quotas
    max_users = Column(Integer, default=5, nullable=False)
    max_storage_gb = Column(Integer, default=10, nullable=False)
    max_invoices_per_month = Column(Integer, default=100, nullable=False)
    
    # POPIA Compliance (South African Data Protection)
    data_processing_consent = Column(Boolean, default=False, nullable=False)
    popia_consent_date = Column(DateTime(timezone=True), nullable=True)
    privacy_policy_accepted = Column(Boolean, default=False, nullable=False)
    privacy_policy_version = Column(String(10), nullable=True)
    data_retention_period = Column(Integer, default=7, nullable=False)  # Years
    popia_compliance_officer = Column(String(255), nullable=True)
    popia_compliance_email = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("src.models.user.User", back_populates="company", cascade="all, delete-orphan")
    invoices = relationship("src.models.invoice.Invoice", back_populates="company", cascade="all, delete-orphan")
    audit_logs = relationship("src.models.audit.AuditLog", back_populates="company")
    subscriptions = relationship("src.models.subscription.Subscription", back_populates="company", cascade="all, delete-orphan")
    slas = relationship("src.models.subscription.SLA", back_populates="company", cascade="all, delete-orphan")
    payment_methods = relationship("src.models.subscription.PaymentMethod", back_populates="company", cascade="all, delete-orphan")
    billing_history = relationship("src.models.subscription.BillingHistory", back_populates="company", cascade="all, delete-orphan")
    # purchase_orders = relationship("PurchaseOrder", back_populates="company", cascade="all, delete-orphan")
    # receipts = relationship("Receipt", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if company is active"""
        return self.status in [CompanyStatus.ACTIVE, CompanyStatus.TRIAL]
    
    @property
    def is_trial(self) -> bool:
        """Check if company is in trial period"""
        return self.status == CompanyStatus.TRIAL
    
    @property
    def has_expired_trial(self) -> bool:
        """Check if company's trial has expired"""
        if not self.trial_ends_at:
            return False
        return self.trial_ends_at < func.now()
    
    def can_add_user(self) -> bool:
        """Check if company can add more users"""
        if not self.is_active:
            return False
        current_user_count = len(self.users)
        return current_user_count < self.max_users
    
    def get_feature(self, feature_name: str, default=None):
        """Get a specific feature setting"""
        return self.features.get(feature_name, default)
    
    def set_feature(self, feature_name: str, value):
        """Set a specific feature setting"""
        if not self.features:
            self.features = {}
        self.features[feature_name] = value
