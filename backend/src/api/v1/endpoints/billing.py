"""
Billing and Subscription API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.database import get_db
from core.auth import AuthManager
from src.models.user import User
from src.models.company import Company
from services.billing import StripeService
from schemas.billing import (
    SubscriptionCreateRequest,
    SubscriptionUpdateRequest,
    SubscriptionResponse,
    SubscriptionStatusResponse,
    UsageRecordRequest,
    UsageRecordResponse,
    WebhookResponse,
    BillingTierResponse,
    PaymentMethodResponse,
    BillingInvoiceResponse
)

router = APIRouter()

# Initialize Stripe service
stripe_service = StripeService()

@router.get("/tiers", response_model=Dict[str, BillingTierResponse])
async def get_billing_tiers():
    """Get available billing tiers and competitive pricing"""
    return {
        "starter": BillingTierResponse(
            name="Starter",
            monthly_price=19.00,
            yearly_price=190.00,
            features=[
                "Up to 3 users",
                "5GB storage",
                "50 invoices/month",
                "AI-powered OCR",
                "Email support",
                "Mobile app access",
                "Basic analytics",
                "14-day free trial"
            ],
            max_users=3,
            max_storage_gb=5,
            max_invoices_per_month=50,
            trial_days=14,
            popular=False,
            savings_percentage=17.0
        ),
        "professional": BillingTierResponse(
            name="Professional", 
            monthly_price=49.00,
            yearly_price=490.00,
            features=[
                "Up to 15 users",
                "50GB storage", 
                "500 invoices/month",
                "AI-powered OCR",
                "Priority support",
                "API access",
                "Advanced analytics",
                "Mobile app access",
                "Fraud detection",
                "Three-way matching",
                "21-day free trial"
            ],
            max_users=15,
            max_storage_gb=50,
            max_invoices_per_month=500,
            trial_days=21,
            popular=True,
            savings_percentage=17.0
        ),
        "business": BillingTierResponse(
            name="Business",
            monthly_price=99.00,
            yearly_price=990.00,
            features=[
                "Up to 50 users",
                "200GB storage", 
                "2,000 invoices/month",
                "AI-powered OCR",
                "Priority support",
                "API access",
                "Advanced analytics",
                "Mobile app access",
                "Fraud detection",
                "Three-way matching",
                "SSO integration",
                "Custom fields",
                "30-day free trial"
            ],
            max_users=50,
            max_storage_gb=200,
            max_invoices_per_month=2000,
            trial_days=30,
            popular=False,
            savings_percentage=17.0
        ),
        "enterprise": BillingTierResponse(
            name="Enterprise",
            monthly_price=199.00,
            yearly_price=1990.00,
            features=[
                "Up to 200 users",
                "1TB storage",
                "10,000 invoices/month",
                "AI-powered OCR",
                "Custom workflows",
                "Dedicated support",
                "API access",
                "Advanced analytics",
                "Mobile app access",
                "Fraud detection",
                "Three-way matching",
                "SSO integration",
                "Custom integrations",
                "White labeling",
                "Dedicated account manager",
                "45-day free trial"
            ],
            max_users=200,
            max_storage_gb=1000,
            max_invoices_per_month=10000,
            trial_days=45,
            popular=False,
            savings_percentage=17.0
        ),
        "unlimited": BillingTierResponse(
            name="Unlimited",
            monthly_price=299.00,
            yearly_price=2990.00,
            features=[
                "Unlimited users",
                "Unlimited storage",
                "Unlimited invoices",
                "AI-powered OCR",
                "Custom workflows",
                "Dedicated support",
                "API access",
                "Advanced analytics",
                "Mobile app access",
                "Fraud detection",
                "Three-way matching",
                "SSO integration",
                "Custom integrations",
                "White labeling",
                "Dedicated account manager",
                "On-premise deployment",
                "60-day free trial"
            ],
            max_users=-1,
            max_storage_gb=-1,
            max_invoices_per_month=-1,
            trial_days=60,
            popular=False,
            savings_percentage=17.0
        )
    }

@router.get("/addons", response_model=Dict[str, Any])
async def get_addon_pricing():
    """Get add-on pricing for additional features"""
    return {
        "additional_users": {
            "name": "Additional Users",
            "price_per_user_monthly": 5.00,
            "price_per_user_yearly": 50.00,
            "description": "Add more users to your plan",
            "savings_yearly": 17.0
        },
        "additional_storage": {
            "name": "Additional Storage",
            "price_per_gb_monthly": 0.50,
            "price_per_gb_yearly": 5.00,
            "description": "Add more storage space",
            "savings_yearly": 17.0
        },
        "additional_invoices": {
            "name": "Additional Invoices",
            "price_per_invoice": 0.10,
            "description": "Pay per invoice over your monthly limit",
            "billing": "per_invoice"
        },
        "premium_support": {
            "name": "Premium Support",
            "monthly": 29.00,
            "yearly": 290.00,
            "description": "24/7 phone support, dedicated account manager",
            "savings_yearly": 17.0
        },
        "custom_integrations": {
            "name": "Custom Integrations",
            "setup_fee": 500.00,
            "monthly": 99.00,
            "description": "Custom ERP integrations and API development",
            "savings_yearly": 17.0
        },
        "white_labeling": {
            "name": "White Labeling",
            "setup_fee": 1000.00,
            "monthly": 199.00,
            "description": "Rebrand the platform with your company's branding",
            "savings_yearly": 17.0
        }
    }

@router.get("/comparison", response_model=Dict[str, Any])
async def get_competitor_comparison():
    """Get pricing comparison with competitors"""
    return {
        "our_pricing": {
            "starter": {"monthly": 19, "yearly": 190},
            "professional": {"monthly": 49, "yearly": 490},
            "business": {"monthly": 99, "yearly": 990},
            "enterprise": {"monthly": 199, "yearly": 1990}
        },
        "competitors": {
            "bill_com": {
                "name": "Bill.com",
                "starter": {"monthly": 39, "yearly": 390},
                "professional": {"monthly": 99, "yearly": 990},
                "business": {"monthly": 199, "yearly": 1990},
                "enterprise": {"monthly": 399, "yearly": 3990}
            },
            "tipalti": {
                "name": "Tipalti",
                "starter": {"monthly": 45, "yearly": 450},
                "professional": {"monthly": 120, "yearly": 1200},
                "business": {"monthly": 250, "yearly": 2500},
                "enterprise": {"monthly": 500, "yearly": 5000}
            },
            "stampli": {
                "name": "Stampli",
                "starter": {"monthly": 35, "yearly": 350},
                "professional": {"monthly": 89, "yearly": 890},
                "business": {"monthly": 179, "yearly": 1790},
                "enterprise": {"monthly": 350, "yearly": 3500}
            }
        },
        "savings": {
            "vs_bill_com": "Up to 50% savings",
            "vs_tipalti": "Up to 60% savings", 
            "vs_stampli": "Up to 43% savings"
        }
    }

@router.post("/customers", response_model=Dict[str, Any])
async def create_customer(
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe customer for company"""
    try:
        # Get company for current user
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        result = await stripe_service.create_customer(company, current_user)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer: {str(e)}"
        )

@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionCreateRequest,
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Create subscription for company"""
    try:
        # Get company for current user
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Validate tier
        if request.tier not in ["basic", "professional", "enterprise"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tier. Must be basic, professional, or enterprise"
            )
        
        result = await stripe_service.create_subscription(
            company, 
            request.tier, 
            request.billing_cycle
        )
        
        # Update company tier in database
        company.tier = request.tier
        db.commit()
        
        return SubscriptionResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    request: SubscriptionUpdateRequest,
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Update subscription"""
    try:
        # Get company for current user
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        result = await stripe_service.update_subscription(
            company, 
            request.tier, 
            request.billing_cycle
        )
        
        # Update company tier in database
        if request.tier:
            company.tier = request.tier
            db.commit()
        
        return SubscriptionResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscription: {str(e)}"
        )

@router.delete("/subscriptions/{subscription_id}", response_model=Dict[str, Any])
async def cancel_subscription(
    subscription_id: str,
    cancel_immediately: bool = False,
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription"""
    try:
        # Get company for current user
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        result = await stripe_service.cancel_subscription(
            company, 
            cancel_immediately
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

@router.get("/subscriptions/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get current subscription status"""
    try:
        # Get company for current user
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        result = await stripe_service.get_subscription_status(company)
        return SubscriptionStatusResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription status: {str(e)}"
        )

@router.post("/usage", response_model=UsageRecordResponse)
async def create_usage_record(
    request: UsageRecordRequest,
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Create usage record for metered billing"""
    try:
        # Get company for current user
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        result = await stripe_service.create_usage_record(
            company, 
            request.quantity,
            request.timestamp
        )
        
        return UsageRecordResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create usage record: {str(e)}"
        )

@router.get("/invoices", response_model=List[BillingInvoiceResponse])
async def get_billing_invoices(
    limit: int = 10,
    starting_after: Optional[str] = None,
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing invoices for company"""
    try:
        # Get company for current user
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # This would typically fetch from Stripe
        # For now, return mock data
        return [
            BillingInvoiceResponse(
                id="in_mock_1",
                amount_paid=2900,
                currency="usd",
                status="paid",
                created=datetime.now(UTC).timestamp(),
                invoice_pdf="https://example.com/invoice.pdf"
            )
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoices: {str(e)}"
        )

@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment methods for company"""
    try:
        # Get company for current user
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # This would typically fetch from Stripe
        # For now, return mock data
        return [
            PaymentMethodResponse(
                id="pm_mock_1",
                type="card",
                card_last4="4242",
                card_brand="visa",
                is_default=True
            )
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment methods: {str(e)}"
        )

@router.post("/webhooks/stripe", response_model=WebhookResponse)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhooks"""
    try:
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing stripe-signature header"
            )
        
        # Process webhook
        result = await stripe_service.process_webhook(body, signature)
        
        return WebhookResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook processing failed: {str(e)}"
        )
