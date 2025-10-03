"""
Subscription Schemas for Paystack Integration
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid

class SubscriptionType(str, Enum):
    """Subscription type enumeration"""
    TRIAL = "trial"
    PAID = "paid"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"

class BillingCycle(str, Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class TrialCreate(BaseModel):
    """Schema for creating a trial subscription"""
    trial_days: int = Field(..., description="Trial duration in days")
    tier: str = Field(..., description="Subscription tier")
    custom_terms: Optional[str] = Field(None, description="Custom trial terms")
    
    @validator('trial_days')
    def validate_trial_days(cls, v):
        if v not in [14, 21, 30, 45, 60]:
            raise ValueError('Trial days must be one of: 14, 21, 30, 45, 60')
        return v
    
    @validator('tier')
    def validate_tier(cls, v):
        if v not in ['growth', 'professional', 'enterprise']:
            raise ValueError('Tier must be one of: growth, professional, enterprise')
        return v

class TrialResponse(BaseModel):
    """Schema for trial subscription response"""
    status: str
    trial_id: str
    trial_end_date: str
    auto_convert: bool
    trial_duration_days: int
    plan_tier: str
    requires_approval: Optional[bool] = None
    custom_terms: Optional[str] = None
    approval_workflow: Optional[str] = None

class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription"""
    plan_tier: str = Field(..., description="Subscription tier")
    billing_cycle: BillingCycle = Field(default=BillingCycle.MONTHLY, description="Billing cycle")
    payment_method_id: Optional[str] = Field(None, description="Payment method ID")

class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription"""
    plan_tier: Optional[str] = None
    billing_cycle: Optional[BillingCycle] = None
    status: Optional[SubscriptionStatus] = None

class SubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: str
    company_id: str
    subscription_type: SubscriptionType
    status: SubscriptionStatus
    plan_tier: str
    paystack_subscription_id: Optional[str] = None
    paystack_plan_id: Optional[str] = None
    paystack_customer_id: Optional[str] = None
    billing_cycle: BillingCycle
    amount: int
    currency: str
    is_trial: bool
    trial_start_date: Optional[str] = None
    trial_end_date: Optional[str] = None
    auto_convert: bool
    custom_terms: Optional[str] = None
    requires_approval: bool
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    next_billing_date: Optional[str] = None
    last_billing_date: Optional[str] = None
    cancelled_at: Optional[str] = None
    cancellation_reason: Optional[str] = None
    sla_agreement_id: Optional[str] = None
    contract_terms: Optional[Dict[str, Any]] = None
    subscription_metadata: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str

class SLARequest(BaseModel):
    """Schema for SLA agreement request"""
    sla_type: str = Field(default="enterprise", description="SLA type")
    uptime_guarantee: int = Field(default=99, description="Uptime guarantee percentage")
    response_time_sla: str = Field(default="24_hours", description="Response time SLA")
    support_level: str = Field(default="dedicated", description="Support level")
    custom_terms: Optional[List[str]] = Field(None, description="Custom terms")
    penalty_clauses: Optional[Dict[str, str]] = Field(None, description="Penalty clauses")

class SLAResponse(BaseModel):
    """Schema for SLA agreement response"""
    status: str
    sla_id: str
    company_id: str
    sla_type: str
    effective_date: str
    expiry_date: str
    uptime_guarantee: int
    support_level: str

class PaymentMethodCreate(BaseModel):
    """Schema for creating a payment method"""
    method_type: str = Field(..., description="Payment method type")
    card_last_four: Optional[str] = Field(None, description="Last four digits of card")
    card_brand: Optional[str] = Field(None, description="Card brand")
    is_default: bool = Field(default=False, description="Is default payment method")

class PaymentMethodResponse(BaseModel):
    """Schema for payment method response"""
    id: str
    company_id: str
    method_type: str
    provider: str
    paystack_authorization_code: Optional[str] = None
    paystack_customer_code: Optional[str] = None
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    bank_name: Optional[str] = None
    account_last_four: Optional[str] = None
    account_type: Optional[str] = None
    is_default: bool
    is_active: bool
    created_at: str
    updated_at: str

class BillingHistoryResponse(BaseModel):
    """Schema for billing history response"""
    id: str
    company_id: str
    subscription_id: Optional[str] = None
    transaction_type: str
    amount: int
    currency: str
    paystack_transaction_id: Optional[str] = None
    paystack_reference: Optional[str] = None
    billing_period_start: Optional[str] = None
    billing_period_end: Optional[str] = None
    status: str
    payment_method_id: Optional[str] = None
    paid_at: Optional[str] = None
    description: Optional[str] = None
    transaction_metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

class SubscriptionAnalyticsResponse(BaseModel):
    """Schema for subscription analytics response"""
    status: str
    analytics: Dict[str, Any]
    generated_at: str

class POPIAConsentRequest(BaseModel):
    """Schema for POPIA consent request"""
    consent_type: str = Field(..., description="Type of consent")
    consent_given: bool = Field(..., description="Whether consent is given")
    legal_basis: str = Field(default="consent", description="Legal basis for processing")
    data_categories: List[str] = Field(..., description="Categories of data being processed")
    retention_period: str = Field(default="7_years", description="Data retention period")
    third_party_sharing: bool = Field(default=False, description="Whether data is shared with third parties")
    withdrawal_method: str = Field(default="email_request", description="Method for withdrawing consent")

class POPIAConsentResponse(BaseModel):
    """Schema for POPIA consent response"""
    status: str
    consent_id: str
    compliance_status: str
    popia_reference: str
    data_categories: List[str]
    retention_period: str
    legal_basis: str

class DataAccessRequest(BaseModel):
    """Schema for data access request"""
    request_type: str = Field(..., description="Type of data request")
    user_id: str = Field(..., description="User ID making the request")
    description: Optional[str] = Field(None, description="Description of the request")

class DataDeletionRequest(BaseModel):
    """Schema for data deletion request"""
    deletion_type: str = Field(..., description="Type of deletion requested")
    user_id: str = Field(..., description="User ID making the request")
    reason: Optional[str] = Field(None, description="Reason for deletion request")

class POPIAReportRequest(BaseModel):
    """Schema for POPIA report request"""
    report_type: str = Field(default="compliance_summary", description="Type of report")
    company_id: str = Field(..., description="Company ID")
    period_start: Optional[str] = Field(None, description="Report period start")
    period_end: Optional[str] = Field(None, description="Report period end")

class POPIAReportResponse(BaseModel):
    """Schema for POPIA report response"""
    status: str
    report_id: str
    company_id: str
    report_type: str
    generated_date: str
    compliance_data: Dict[str, Any]
    recommendations: List[str]

class PaystackWebhookPayload(BaseModel):
    """Schema for Paystack webhook payload"""
    event: str = Field(..., description="Webhook event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    created_at: Optional[str] = Field(None, description="Event creation timestamp")

class SubscriptionPlanResponse(BaseModel):
    """Schema for subscription plan response"""
    id: str
    name: str
    description: Optional[str] = None
    tier: str
    amount: int
    currency: str
    billing_cycle: BillingCycle
    features: Optional[List[str]] = None
    limits: Optional[Dict[str, Any]] = None
    paystack_plan_id: Optional[str] = None
    is_active: bool
    is_default: bool
    trial_days: int
    created_at: str
    updated_at: str

class SubscriptionMetrics(BaseModel):
    """Schema for subscription metrics"""
    total_subscriptions: int
    active_subscriptions: int
    trial_conversions: int
    churn_rate: float
    mrr: int  # Monthly recurring revenue in cents
    arr: int  # Annual recurring revenue in cents
    average_revenue_per_user: int
    trial_conversion_rate: float
    customer_lifetime_value: int

class ComplianceMetrics(BaseModel):
    """Schema for compliance metrics"""
    popia_compliance_score: float
    consent_records_count: int
    data_requests_count: int
    deletion_requests_count: int
    last_audit_date: Optional[str] = None
    next_audit_due: Optional[str] = None
    compliance_status: str

class RetentionOffer(BaseModel):
    """Schema for retention offer"""
    offer_type: str = Field(..., description="Type of retention offer")
    discount_percentage: Optional[int] = Field(None, description="Discount percentage")
    duration_months: Optional[int] = Field(None, description="Offer duration in months")
    description: str = Field(..., description="Offer description")
    terms: Optional[Dict[str, Any]] = Field(None, description="Offer terms and conditions")

class CancellationResponse(BaseModel):
    """Schema for subscription cancellation response"""
    status: str
    subscription_id: str
    cancellation_date: str
    retention_offers: List[RetentionOffer]
    final_billing_date: str
    feedback_requested: bool = True
