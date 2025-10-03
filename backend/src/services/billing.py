"""
Billing Service with Stripe integration for subscription management
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import stripe
from sqlalchemy.orm import Session

from core.config import settings
from src.models.company import Company, CompanyStatus, CompanyTier
from src.models.user import User
from src.models.audit import AuditLog, AuditAction, AuditResourceType

logger = logging.getLogger(__name__)

class StripeService:
    """Stripe billing service for subscription management"""
    
    def __init__(self):
        if not settings.STRIPE_SECRET_KEY:
            logger.warning("Stripe secret key not configured")
            self.stripe = None
        else:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            self.stripe = stripe
        
        # Competitive subscription tier pricing (in cents) - Aggressive pricing to undercut competitors
        self.tier_pricing = {
            "starter": {
                "monthly": 1900,      # $19/month (vs Bill.com $39, Tipalti $45)
                "yearly": 19000,      # $190/year (2 months free = 17% discount)
                "features": {
                    "max_users": 3,
                    "max_storage_gb": 5,
                    "max_invoices_per_month": 50,
                    "ocr_included": True,
                    "basic_workflows": True,
                    "email_support": True,
                    "mobile_app": True,
                    "basic_analytics": True,
                    "trial_days": 14
                }
            },
            "professional": {
                "monthly": 4900,      # $49/month (vs Bill.com $99, Tipalti $120)
                "yearly": 49000,      # $490/year (2 months free = 17% discount)
                "features": {
                    "max_users": 15,
                    "max_storage_gb": 50,
                    "max_invoices_per_month": 500,
                    "ocr_included": True,
                    "advanced_workflows": True,
                    "priority_support": True,
                    "api_access": True,
                    "advanced_analytics": True,
                    "mobile_app": True,
                    "fraud_detection": True,
                    "three_way_matching": True,
                    "trial_days": 21
                }
            },
            "business": {
                "monthly": 9900,      # $99/month (vs Bill.com $199, Tipalti $250)
                "yearly": 99000,      # $990/year (2 months free = 17% discount)
                "features": {
                    "max_users": 50,
                    "max_storage_gb": 200,
                    "max_invoices_per_month": 2000,
                    "ocr_included": True,
                    "advanced_workflows": True,
                    "priority_support": True,
                    "api_access": True,
                    "advanced_analytics": True,
                    "mobile_app": True,
                    "fraud_detection": True,
                    "three_way_matching": True,
                    "sso_integration": True,
                    "custom_fields": True,
                    "trial_days": 30
                }
            },
            "enterprise": {
                "monthly": 19900,     # $199/month (vs Bill.com $399, Tipalti $500+)
                "yearly": 199000,     # $1990/year (2 months free = 17% discount)
                "features": {
                    "max_users": 200,
                    "max_storage_gb": 1000,
                    "max_invoices_per_month": 10000,
                    "ocr_included": True,
                    "custom_workflows": True,
                    "dedicated_support": True,
                    "api_access": True,
                    "advanced_analytics": True,
                    "mobile_app": True,
                    "fraud_detection": True,
                    "three_way_matching": True,
                    "sso_integration": True,
                    "custom_integrations": True,
                    "white_labeling": True,
                    "dedicated_account_manager": True,
                    "trial_days": 45
                }
            },
            "unlimited": {
                "monthly": 29900,     # $299/month (vs competitors $600+)
                "yearly": 299000,     # $2990/year (2 months free = 17% discount)
                "features": {
                    "max_users": -1,  # Unlimited
                    "max_storage_gb": -1,  # Unlimited
                    "max_invoices_per_month": -1,  # Unlimited
                    "ocr_included": True,
                    "custom_workflows": True,
                    "dedicated_support": True,
                    "api_access": True,
                    "advanced_analytics": True,
                    "mobile_app": True,
                    "fraud_detection": True,
                    "three_way_matching": True,
                    "sso_integration": True,
                    "custom_integrations": True,
                    "white_labeling": True,
                    "dedicated_account_manager": True,
                    "on_premise_deployment": True,
                    "trial_days": 60
                }
            }
        }
        
        # Add-on pricing for additional features
        self.addon_pricing = {
            "additional_users": {
                "price_per_user_monthly": 500,  # $5/user/month
                "price_per_user_yearly": 5000,  # $50/user/year
            },
            "additional_storage": {
                "price_per_gb_monthly": 50,     # $0.50/GB/month
                "price_per_gb_yearly": 500,     # $5/GB/year
            },
            "additional_invoices": {
                "price_per_invoice": 10,        # $0.10/invoice over limit
            },
            "premium_support": {
                "monthly": 2900,                # $29/month
                "yearly": 29000,                # $290/year
            },
            "custom_integrations": {
                "setup_fee": 50000,             # $500 setup fee
                "monthly": 9900,                # $99/month
            },
            "white_labeling": {
                "setup_fee": 100000,            # $1000 setup fee
                "monthly": 19900,               # $199/month
            }
        }
    
    async def create_customer(self, company: Company, user: User) -> Dict[str, Any]:
        """Create Stripe customer for company"""
        if not self.stripe:
            return self._mock_customer_response(company)
        
        try:
            customer = stripe.Customer.create(
                email=company.email,
                name=company.name,
                metadata={
                    "company_id": str(company.id),
                    "company_tier": company.tier.value,
                    "created_by": str(user.id)
                }
            )
            
            # Update company with Stripe customer ID
            company.subscription_id = customer.id
            
            return {
                "customer_id": customer.id,
                "status": "created",
                "created_at": datetime.fromtimestamp(customer.created).isoformat()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {e}")
            raise
    
    async def create_subscription(self, company: Company, tier: str, 
                                billing_cycle: str = "monthly") -> Dict[str, Any]:
        """Create subscription for company"""
        if not self.stripe:
            return self._mock_subscription_response(company, tier)
        
        try:
            # Get price ID for tier and billing cycle
            price_id = self._get_price_id(tier, billing_cycle)
            if not price_id:
                raise ValueError(f"Invalid tier or billing cycle: {tier}, {billing_cycle}")
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=company.subscription_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "company_id": str(company.id),
                    "tier": tier,
                    "billing_cycle": billing_cycle
                }
            )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "tier": tier,
                "billing_cycle": billing_cycle,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                "latest_invoice": subscription.latest_invoice.id if subscription.latest_invoice else None
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription creation failed: {e}")
            raise
    
    async def update_subscription(self, company: Company, new_tier: str, 
                                billing_cycle: str = None) -> Dict[str, Any]:
        """Update company subscription"""
        if not self.stripe:
            return self._mock_update_response(company, new_tier)
        
        try:
            # Get current subscription
            subscription = stripe.Subscription.retrieve(company.subscription_id)
            
            # Get new price ID
            new_price_id = self._get_price_id(new_tier, billing_cycle or "monthly")
            
            # Update subscription
            updated_subscription = stripe.Subscription.modify(
                subscription.id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id,
                }],
                proration_behavior="create_prorations",
                metadata={
                    "company_id": str(company.id),
                    "tier": new_tier,
                    "billing_cycle": billing_cycle or "monthly",
                    "updated_at": datetime.now(UTC).isoformat()
                }
            )
            
            return {
                "subscription_id": updated_subscription.id,
                "status": updated_subscription.status,
                "tier": new_tier,
                "billing_cycle": billing_cycle or "monthly",
                "updated_at": datetime.now(UTC).isoformat()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription update failed: {e}")
            raise
    
    async def cancel_subscription(self, company: Company, 
                                cancel_at_period_end: bool = True) -> Dict[str, Any]:
        """Cancel company subscription"""
        if not self.stripe:
            return self._mock_cancel_response(company)
        
        try:
            subscription = stripe.Subscription.retrieve(company.subscription_id)
            
            if cancel_at_period_end:
                # Cancel at period end
                updated_subscription = stripe.Subscription.modify(
                    subscription.id,
                    cancel_at_period_end=True
                )
                message = "Subscription will be cancelled at the end of the current period"
            else:
                # Cancel immediately
                updated_subscription = stripe.Subscription.cancel(subscription.id)
                message = "Subscription cancelled immediately"
            
            return {
                "subscription_id": updated_subscription.id,
                "status": updated_subscription.status,
                "cancelled_at": datetime.fromtimestamp(updated_subscription.canceled_at).isoformat() if updated_subscription.canceled_at else None,
                "cancel_at_period_end": updated_subscription.cancel_at_period_end,
                "message": message
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription cancellation failed: {e}")
            raise
    
    async def get_subscription_status(self, company: Company) -> Dict[str, Any]:
        """Get current subscription status"""
        if not self.stripe:
            return self._mock_status_response(company)
        
        try:
            subscription = stripe.Subscription.retrieve(company.subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "cancelled_at": datetime.fromtimestamp(subscription.canceled_at).isoformat() if subscription.canceled_at else None,
                "items": [
                    {
                        "price_id": item.price.id,
                        "quantity": item.quantity,
                        "metadata": item.price.metadata
                    }
                    for item in subscription.items.data
                ]
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription status check failed: {e}")
            raise
    
    async def create_usage_record(self, company: Company, quantity: int, 
                                timestamp: datetime = None) -> Dict[str, Any]:
        """Create usage record for metered billing"""
        if not self.stripe:
            return self._mock_usage_response(company, quantity)
        
        try:
            # Get subscription item ID
            subscription = stripe.Subscription.retrieve(company.subscription_id)
            subscription_item_id = subscription.items.data[0].id
            
            # Create usage record
            usage_record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp or int(datetime.now(UTC).timestamp()),
                action="increment"
            )
            
            return {
                "usage_record_id": usage_record.id,
                "quantity": usage_record.quantity,
                "timestamp": datetime.fromtimestamp(usage_record.timestamp).isoformat(),
                "action": usage_record.action
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe usage record creation failed: {e}")
            raise
    
    async def process_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Process Stripe webhook"""
        if not self.stripe or not settings.STRIPE_WEBHOOK_SECRET:
            return {"status": "webhook_processing_disabled"}
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # Handle different event types
            if event.type == "customer.subscription.created":
                return await self._handle_subscription_created(event.data.object)
            elif event.type == "customer.subscription.updated":
                return await self._handle_subscription_updated(event.data.object)
            elif event.type == "customer.subscription.deleted":
                return await self._handle_subscription_deleted(event.data.object)
            elif event.type == "invoice.payment_succeeded":
                return await self._handle_payment_succeeded(event.data.object)
            elif event.type == "invoice.payment_failed":
                return await self._handle_payment_failed(event.data.object)
            else:
                return {"status": "event_ignored", "event_type": event.type}
                
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            raise
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            raise
    
    def _get_price_id(self, tier: str, billing_cycle: str) -> Optional[str]:
        """Get Stripe price ID for tier and billing cycle"""
        # This would typically be configured in Stripe dashboard
        # For now, return None to indicate mock mode
        return None
    
    def _mock_customer_response(self, company: Company) -> Dict[str, Any]:
        """Mock customer creation response"""
        return {
            "customer_id": f"cus_mock_{company.id}",
            "status": "created",
            "created_at": datetime.now(UTC).isoformat()
        }
    
    def _mock_subscription_response(self, company: Company, tier: str) -> Dict[str, Any]:
        """Mock subscription creation response"""
        return {
            "subscription_id": f"sub_mock_{company.id}",
            "status": "active",
            "tier": tier,
            "billing_cycle": "monthly",
            "current_period_start": datetime.now(UTC).isoformat(),
            "current_period_end": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
            "latest_invoice": f"in_mock_{company.id}"
        }
    
    def _mock_update_response(self, company: Company, new_tier: str) -> Dict[str, Any]:
        """Mock subscription update response"""
        return {
            "subscription_id": f"sub_mock_{company.id}",
            "status": "active",
            "tier": new_tier,
            "billing_cycle": "monthly",
            "updated_at": datetime.now(UTC).isoformat()
        }
    
    def _mock_cancel_response(self, company: Company) -> Dict[str, Any]:
        """Mock subscription cancellation response"""
        return {
            "subscription_id": f"sub_mock_{company.id}",
            "status": "canceled",
            "cancelled_at": datetime.now(UTC).isoformat(),
            "cancel_at_period_end": True,
            "message": "Subscription will be cancelled at the end of the current period"
        }
    
    def _mock_status_response(self, company: Company) -> Dict[str, Any]:
        """Mock subscription status response"""
        return {
            "subscription_id": f"sub_mock_{company.id}",
            "status": "active",
            "current_period_start": datetime.now(UTC).isoformat(),
            "current_period_end": (datetime.now(UTC) + timedelta(days=30)).isoformat(),
            "cancel_at_period_end": False,
            "cancelled_at": None,
            "items": [
                {
                    "price_id": "price_mock",
                    "quantity": 1,
                    "metadata": {"tier": company.tier.value}
                }
            ]
        }
    
    def _mock_usage_response(self, company: Company, quantity: int) -> Dict[str, Any]:
        """Mock usage record response"""
        return {
            "usage_record_id": f"ur_mock_{company.id}",
            "quantity": quantity,
            "timestamp": datetime.now(UTC).isoformat(),
            "action": "increment"
        }
    
    async def _handle_subscription_created(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription created webhook"""
        logger.info(f"Subscription created: {subscription_data['id']}")
        return {"status": "handled", "event": "subscription_created"}
    
    async def _handle_subscription_updated(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updated webhook"""
        logger.info(f"Subscription updated: {subscription_data['id']}")
        return {"status": "handled", "event": "subscription_updated"}
    
    async def _handle_subscription_deleted(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deleted webhook"""
        logger.info(f"Subscription deleted: {subscription_data['id']}")
        return {"status": "handled", "event": "subscription_deleted"}
    
    async def _handle_payment_succeeded(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment succeeded webhook"""
        logger.info(f"Payment succeeded: {invoice_data['id']}")
        return {"status": "handled", "event": "payment_succeeded"}
    
    async def _handle_payment_failed(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failed webhook"""
        logger.info(f"Payment failed: {invoice_data['id']}")
        return {"status": "handled", "event": "payment_failed"}
