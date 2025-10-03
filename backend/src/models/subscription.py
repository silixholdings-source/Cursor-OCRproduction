"""
Subscription Models for Paystack Integration
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import os

from src.core.database import Base
import enum

# Use JSONB for PostgreSQL, JSON for SQLite
if os.getenv("DATABASE_URL", "").startswith("postgresql"):
    JSONType = JSONB
else:
    JSONType = JSON

class SubscriptionType(enum.Enum):
    """Subscription type enumeration"""
    TRIAL = "trial"
    PAID = "paid"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(enum.Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"

class BillingCycle(enum.Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class Subscription(Base):
    """Subscription model for managing company subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Subscription details
    subscription_type = Column(Enum(SubscriptionType), nullable=False, default=SubscriptionType.TRIAL)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    plan_tier = Column(String(50), nullable=False, default="basic")
    
    # Paystack integration
    paystack_subscription_id = Column(String(100), nullable=True)
    paystack_plan_id = Column(String(100), nullable=True)
    paystack_customer_id = Column(String(100), nullable=True)
    
    # Billing details
    billing_cycle = Column(Enum(BillingCycle), nullable=False, default=BillingCycle.MONTHLY)
    amount = Column(Integer, nullable=False, default=0)  # Amount in kobo/cents
    currency = Column(String(3), nullable=False, default="ZAR")
    
    # Trial management
    is_trial = Column(Boolean, nullable=False, default=True)
    trial_start_date = Column(DateTime, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)
    auto_convert = Column(Boolean, nullable=False, default=True)
    custom_terms = Column(Text, nullable=True)
    requires_approval = Column(Boolean, nullable=False, default=False)
    
    # Subscription dates
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    last_billing_date = Column(DateTime, nullable=True)
    
    # Cancellation
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(String(255), nullable=True)
    cancellation_feedback = Column(Text, nullable=True)
    
    # SLA and agreements
    sla_agreement_id = Column(UUID(as_uuid=True), nullable=True)
    contract_terms = Column(JSONType, nullable=True)
    
    # Metadata
    subscription_metadata = Column(JSONType, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("models.company.Company", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, company_id={self.company_id}, type={self.subscription_type.value}, status={self.status.value})>"

class SubscriptionPlan(Base):
    """Subscription plan model for managing available plans"""
    __tablename__ = "subscription_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Plan details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    tier = Column(String(50), nullable=False)
    
    # Pricing
    amount = Column(Integer, nullable=False)  # Amount in kobo/cents
    currency = Column(String(3), nullable=False, default="ZAR")
    billing_cycle = Column(Enum(BillingCycle), nullable=False, default=BillingCycle.MONTHLY)
    
    # Features and limits
    features = Column(JSONType, nullable=True)
    limits = Column(JSONType, nullable=True)
    
    # Paystack integration
    paystack_plan_id = Column(String(100), nullable=True)
    
    # Plan status
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)
    
    # Trial settings
    trial_days = Column(Integer, nullable=False, default=14)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SubscriptionPlan(id={self.id}, name={self.name}, tier={self.tier}, amount={self.amount})>"

class SLA(Base):
    """Service Level Agreement model for enterprise clients"""
    __tablename__ = "slas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    
    # SLA details
    sla_type = Column(String(50), nullable=False, default="enterprise")
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Service levels
    uptime_guarantee = Column(Integer, nullable=False, default=99)  # Percentage
    response_time_sla = Column(String(50), nullable=False, default="24_hours")
    resolution_time_sla = Column(String(50), nullable=False, default="72_hours")
    support_level = Column(String(50), nullable=False, default="standard")
    
    # Terms and conditions
    custom_terms = Column(JSONType, nullable=True)
    penalty_clauses = Column(JSONType, nullable=True)
    escalation_procedures = Column(JSONType, nullable=True)
    
    # Agreement dates
    effective_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    signed_date = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="draft")
    is_active = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("models.company.Company", back_populates="slas")
    subscription = relationship("Subscription")
    
    def __repr__(self):
        return f"<SLA(id={self.id}, company_id={self.company_id}, type={self.sla_type}, uptime={self.uptime_guarantee}%)>"

class PaymentMethod(Base):
    """Payment method model for storing customer payment information"""
    __tablename__ = "payment_methods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Payment method details
    method_type = Column(String(50), nullable=False)  # card, bank_account, etc.
    provider = Column(String(50), nullable=False, default="paystack")
    
    # Paystack integration
    paystack_authorization_code = Column(String(200), nullable=True)
    paystack_customer_code = Column(String(100), nullable=True)
    
    # Card details (encrypted)
    card_last_four = Column(String(4), nullable=True)
    card_brand = Column(String(50), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)
    
    # Bank account details (encrypted)
    bank_name = Column(String(100), nullable=True)
    account_last_four = Column(String(4), nullable=True)
    account_type = Column(String(50), nullable=True)
    
    # Status
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("models.company.Company", back_populates="payment_methods")
    
    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, company_id={self.company_id}, type={self.method_type})>"

class BillingHistory(Base):
    """Billing history model for tracking payments and charges"""
    __tablename__ = "billing_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # subscription, upgrade, downgrade, refund
    amount = Column(Integer, nullable=False)  # Amount in kobo/cents
    currency = Column(String(3), nullable=False, default="ZAR")
    
    # Paystack integration
    paystack_transaction_id = Column(String(100), nullable=True)
    paystack_reference = Column(String(100), nullable=True)
    
    # Billing period
    billing_period_start = Column(DateTime, nullable=True)
    billing_period_end = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="pending")  # pending, paid, failed, refunded
    
    # Payment details
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # Description and metadata
    description = Column(String(255), nullable=True)
    transaction_metadata = Column(JSONType, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("models.company.Company", back_populates="billing_history")
    subscription = relationship("Subscription")
    payment_method = relationship("PaymentMethod")
    
    def __repr__(self):
        return f"<BillingHistory(id={self.id}, company_id={self.company_id}, amount={self.amount}, status={self.status})>"
