"""
Billing and Subscription Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    UNPAID = "unpaid"

class BillingTierResponse(BaseModel):
    """Response model for billing tier information"""
    name: str = Field(..., description="Tier name")
    monthly_price: float = Field(..., description="Monthly price in USD")
    yearly_price: float = Field(..., description="Yearly price in USD")
    features: List[str] = Field(..., description="List of features included in this tier")
    max_users: int = Field(..., description="Maximum number of users")
    max_storage_gb: int = Field(..., description="Maximum storage in GB")
    max_invoices_per_month: int = Field(..., description="Maximum invoices per month")
    trial_days: int = Field(..., description="Free trial days")
    popular: bool = Field(default=False, description="Whether this is the most popular tier")
    savings_percentage: float = Field(default=0.0, description="Savings percentage for yearly billing")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Professional",
                "monthly_price": 49.00,
                "yearly_price": 490.00,
                "features": ["Unlimited invoices", "Advanced analytics", "API access"],
                "max_users": 10,
                "max_storage_gb": 100,
                "max_invoices_per_month": 1000,
                "trial_days": 14,
                "popular": True,
                "savings_percentage": 16.67
            }
        }
    )

class SubscriptionResponse(BaseModel):
    """Response model for subscription information"""
    id: str = Field(..., description="Subscription ID")
    company_id: str = Field(..., description="Company ID")
    tier: str = Field(..., description="Subscription tier")
    status: SubscriptionStatus = Field(..., description="Subscription status")
    billing_cycle: BillingCycle = Field(..., description="Billing cycle")
    current_period_start: datetime = Field(..., description="Current period start")
    current_period_end: datetime = Field(..., description="Current period end")
    cancel_at_period_end: bool = Field(..., description="Cancel at period end")
    trial_end: Optional[datetime] = Field(None, description="Trial end date")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "sub_1234567890",
                "company_id": "comp_abc123",
                "tier": "professional",
                "status": "active",
                "billing_cycle": "monthly",
                "current_period_start": "2024-01-01T00:00:00Z",
                "current_period_end": "2024-02-01T00:00:00Z",
                "cancel_at_period_end": False,
                "trial_end": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )

class CreateSubscriptionRequest(BaseModel):
    """Request model for creating a subscription"""
    tier: str = Field(..., description="Subscription tier")
    billing_cycle: BillingCycle = Field(..., description="Billing cycle")
    payment_method_id: str = Field(..., description="Payment method ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tier": "professional",
                "billing_cycle": "monthly",
                "payment_method_id": "pm_1234567890"
            }
        }
    )

class UpdateSubscriptionRequest(BaseModel):
    """Request model for updating a subscription"""
    tier: Optional[str] = Field(None, description="New subscription tier")
    billing_cycle: Optional[BillingCycle] = Field(None, description="New billing cycle")
    payment_method_id: Optional[str] = Field(None, description="New payment method ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tier": "enterprise",
                "billing_cycle": "yearly",
                "payment_method_id": "pm_0987654321"
            }
        }
    )

class BillingUsageResponse(BaseModel):
    """Response model for billing usage information"""
    company_id: str = Field(..., description="Company ID")
    current_period_start: datetime = Field(..., description="Current period start")
    current_period_end: datetime = Field(..., description="Current period end")
    usage: Dict[str, int] = Field(..., description="Current usage statistics")
    limits: Dict[str, int] = Field(..., description="Usage limits")
    overages: Dict[str, int] = Field(..., description="Overage charges")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": "comp_abc123",
                "current_period_start": "2024-01-01T00:00:00Z",
                "current_period_end": "2024-02-01T00:00:00Z",
                "usage": {
                    "users": 8,
                    "storage_gb": 45,
                    "invoices": 750
                },
                "limits": {
                    "users": 10,
                    "storage_gb": 100,
                    "invoices": 1000
                },
                "overages": {
                    "users": 0,
                    "storage_gb": 0,
                    "invoices": 0
                }
            }
        }
    )

class PaymentMethodResponse(BaseModel):
    """Response model for payment method information"""
    id: str = Field(..., description="Payment method ID")
    type: str = Field(..., description="Payment method type")
    last_four: str = Field(..., description="Last four digits")
    brand: str = Field(..., description="Card brand")
    expiry_month: int = Field(..., description="Expiry month")
    expiry_year: int = Field(..., description="Expiry year")
    is_default: bool = Field(..., description="Is default payment method")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "pm_1234567890",
                "type": "card",
                "last_four": "4242",
                "brand": "visa",
                "expiry_month": 12,
                "expiry_year": 2025,
                "is_default": True
            }
        }
    )

class InvoiceResponse(BaseModel):
    """Response model for billing invoice information"""
    id: str = Field(..., description="Invoice ID")
    number: str = Field(..., description="Invoice number")
    status: str = Field(..., description="Invoice status")
    amount: float = Field(..., description="Invoice amount")
    currency: str = Field(..., description="Currency")
    created_at: datetime = Field(..., description="Created at")
    paid_at: Optional[datetime] = Field(None, description="Paid at")
    due_date: Optional[datetime] = Field(None, description="Due date")
    download_url: Optional[str] = Field(None, description="Download URL")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "in_1234567890",
                "number": "INV-2024-001",
                "status": "paid",
                "amount": 49.00,
                "currency": "usd",
                "created_at": "2024-01-01T00:00:00Z",
                "paid_at": "2024-01-01T00:05:00Z",
                "due_date": "2024-01-15T00:00:00Z",
                "download_url": "https://example.com/invoices/in_1234567890.pdf"
            }
        }
    )

class BillingDashboardResponse(BaseModel):
    """Response model for billing dashboard information"""
    subscription: SubscriptionResponse = Field(..., description="Current subscription")
    usage: BillingUsageResponse = Field(..., description="Current usage")
    payment_methods: List[PaymentMethodResponse] = Field(..., description="Payment methods")
    recent_invoices: List[InvoiceResponse] = Field(..., description="Recent invoices")
    upcoming_invoice: Optional[InvoiceResponse] = Field(None, description="Upcoming invoice")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "subscription": {
                    "id": "sub_1234567890",
                    "company_id": "comp_abc123",
                    "tier": "professional",
                    "status": "active",
                    "billing_cycle": "monthly",
                    "current_period_start": "2024-01-01T00:00:00Z",
                    "current_period_end": "2024-02-01T00:00:00Z",
                    "cancel_at_period_end": False,
                    "trial_end": None,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                },
                "usage": {
                    "company_id": "comp_abc123",
                    "current_period_start": "2024-01-01T00:00:00Z",
                    "current_period_end": "2024-02-01T00:00:00Z",
                    "usage": {
                        "users": 8,
                        "storage_gb": 45,
                        "invoices": 750
                    },
                    "limits": {
                        "users": 10,
                        "storage_gb": 100,
                        "invoices": 1000
                    },
                    "overages": {
                        "users": 0,
                        "storage_gb": 0,
                        "invoices": 0
                    }
                },
                "payment_methods": [],
                "recent_invoices": [],
                "upcoming_invoice": None
            }
        }
    )

class CancelSubscriptionRequest(BaseModel):
    """Request model for canceling a subscription"""
    cancel_at_period_end: bool = Field(default=True, description="Cancel at period end")
    feedback: Optional[str] = Field(None, description="Cancellation feedback")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cancel_at_period_end": True,
                "feedback": "Switching to a different solution"
            }
        }
    )

class ResumeSubscriptionRequest(BaseModel):
    """Request model for resuming a subscription"""
    payment_method_id: Optional[str] = Field(None, description="Payment method ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payment_method_id": "pm_1234567890"
            }
        }
    )

class CreatePaymentMethodRequest(BaseModel):
    """Request model for creating a payment method"""
    payment_method_id: str = Field(..., description="Payment method ID")
    set_as_default: bool = Field(default=False, description="Set as default payment method")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payment_method_id": "pm_1234567890",
                "set_as_default": True
            }
        }
    )

class WebhookEvent(BaseModel):
    """Webhook event model"""
    id: str = Field(..., description="Event ID")
    type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    created_at: datetime = Field(..., description="Created at")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "evt_1234567890",
                "type": "invoice.payment_succeeded",
                "data": {
                    "object": {
                        "id": "in_1234567890",
                        "amount_paid": 4900,
                        "currency": "usd"
                    }
                },
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    )

class SubscriptionCreateRequest(BaseModel):
    """Request model for creating a subscription"""
    tier: str = Field(..., description="Subscription tier")
    billing_cycle: BillingCycle = Field(..., description="Billing cycle")
    payment_method_id: str = Field(..., description="Payment method ID")

class SubscriptionUpdateRequest(BaseModel):
    """Request model for updating a subscription"""
    tier: Optional[str] = Field(None, description="New subscription tier")
    billing_cycle: Optional[BillingCycle] = Field(None, description="New billing cycle")
    payment_method_id: Optional[str] = Field(None, description="New payment method ID")

class SubscriptionStatusResponse(BaseModel):
    """Response model for subscription status"""
    status: SubscriptionStatus = Field(..., description="Subscription status")
    tier: str = Field(..., description="Subscription tier")
    billing_cycle: BillingCycle = Field(..., description="Billing cycle")
    current_period_end: datetime = Field(..., description="Current period end")

class UsageRecordRequest(BaseModel):
    """Request model for usage record"""
    metric: str = Field(..., description="Usage metric")
    quantity: int = Field(..., description="Usage quantity")
    timestamp: datetime = Field(..., description="Usage timestamp")

class UsageRecordResponse(BaseModel):
    """Response model for usage record"""
    id: str = Field(..., description="Usage record ID")
    metric: str = Field(..., description="Usage metric")
    quantity: int = Field(..., description="Usage quantity")
    timestamp: datetime = Field(..., description="Usage timestamp")

class WebhookResponse(BaseModel):
    """Response model for webhook"""
    received: bool = Field(..., description="Webhook received")
    event_type: str = Field(..., description="Event type")
    processed: bool = Field(..., description="Event processed")

class BillingInvoiceResponse(BaseModel):
    """Response model for billing invoice"""
    id: str = Field(..., description="Invoice ID")
    number: str = Field(..., description="Invoice number")
    status: str = Field(..., description="Invoice status")
    amount: float = Field(..., description="Invoice amount")
    currency: str = Field(..., description="Currency")
    created_at: datetime = Field(..., description="Created at")
    paid_at: Optional[datetime] = Field(None, description="Paid at")
    due_date: Optional[datetime] = Field(None, description="Due date")
    download_url: Optional[str] = Field(None, description="Download URL")