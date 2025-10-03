"""
Subscription Manager Service for Trial and Subscription Management
Handles configurable trials, auto-conversion, and enterprise agreements
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import asyncio

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.company import Company, CompanyTier, CompanyStatus
from src.models.subscription import Subscription, SubscriptionStatus, SubscriptionType
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from services.paystack_service import PaystackService, SubscriptionPlan, TrialPeriod
from config.subscription_config import SubscriptionConfig, SubscriptionTier
from core.config import settings

logger = logging.getLogger(__name__)

class SubscriptionManager:
    """Manages subscriptions, trials, and billing cycles"""
    
    def __init__(self):
        try:
            self.paystack_service = PaystackService()
        except ValueError:
            # Handle missing credentials gracefully for testing
            self.paystack_service = None
        
        # Initialize configuration
        self.config = SubscriptionConfig()
        
        # Standard trial periods for premium plans
        self.standard_trials = {
            "growth": TrialPeriod(days=14, name="14-day growth trial"),
            "professional": TrialPeriod(days=21, name="21-day professional trial"),
            "enterprise": TrialPeriod(days=30, name="30-day enterprise trial")
        }
        
        # Premium Subscription Plans (South African Pricing)
        self.subscription_plans = {
            "growth": SubscriptionPlan(
                name="Growth Plan",
                amount=self.config.PRICING[SubscriptionTier.GROWTH]["monthly_price_zar"],
                interval="monthly",
                currency="ZAR",
                tier="growth",
                features=self.config.FEATURES[SubscriptionTier.GROWTH].features
            ),
            "professional": SubscriptionPlan(
                name="Professional Plan",
                amount=self.config.PRICING[SubscriptionTier.PROFESSIONAL]["monthly_price_zar"],
                interval="monthly",
                currency="ZAR",
                tier="professional",
                features=self.config.FEATURES[SubscriptionTier.PROFESSIONAL].features
            ),
            "enterprise": SubscriptionPlan(
                name="Enterprise Plan",
                amount=self.config.PRICING[SubscriptionTier.ENTERPRISE]["monthly_price_zar"],
                interval="monthly",
                currency="ZAR",
                tier="enterprise",
                features=self.config.FEATURES[SubscriptionTier.ENTERPRISE].features
            )
        }
    
    async def create_trial_subscription(self, company_id: str, trial_days: int, tier: str) -> Dict[str, Any]:
        """Create a trial subscription with configurable duration"""
        try:
            logger.info(f"Creating {trial_days}-day trial for company {company_id}")
            
            # Validate trial period
            if trial_days not in [14, 21, 30, 45, 60]:
                return {
                    "status": "error",
                    "message": f"Invalid trial duration: {trial_days} days. Allowed: 14, 21, 30, 45, 60"
                }
            
            # Create trial subscription
            trial_subscription = Subscription(
                id=str(uuid.uuid4()),
                company_id=company_id,
                subscription_type=SubscriptionType.TRIAL,
                status=SubscriptionStatus.ACTIVE,
                plan_tier=tier,
                trial_start_date=datetime.now(UTC),
                trial_end_date=datetime.now(UTC) + timedelta(days=trial_days),
                auto_convert=True,
                created_at=datetime.now(UTC)
            )
            
            return {
                "status": "trial_created",
                "trial_id": trial_subscription.id,
                "trial_end_date": trial_subscription.trial_end_date.isoformat(),
                "auto_convert": trial_subscription.auto_convert,
                "trial_duration_days": trial_days,
                "plan_tier": tier
            }
            
        except Exception as e:
            logger.error(f"Failed to create trial subscription: {str(e)}")
            return {
                "status": "error",
                "message": f"Trial creation failed: {str(e)}"
            }
    
    async def create_custom_trial(self, company_id: str, trial_days: int, tier: str, custom_terms: str) -> Dict[str, Any]:
        """Create a custom trial period for enterprise negotiations"""
        try:
            logger.info(f"Creating custom {trial_days}-day trial for company {company_id}")
            
            # Validate custom trial requirements
            if trial_days > 60:
                return {
                    "status": "error",
                    "message": "Custom trials cannot exceed 60 days"
                }
            
            if tier not in ["enterprise"]:
                return {
                    "status": "error",
                    "message": "Custom trials are only available for enterprise tier"
                }
            
            # Create custom trial with approval workflow
            custom_trial = TrialPeriod(
                days=trial_days,
                name=f"Custom {trial_days}-day enterprise trial",
                is_custom=True,
                requires_approval=True,
                custom_terms=custom_terms
            )
            
            # Create trial subscription with custom terms
            trial_subscription = Subscription(
                id=str(uuid.uuid4()),
                company_id=company_id,
                subscription_type=SubscriptionType.TRIAL,
                status=SubscriptionStatus.PENDING_APPROVAL,
                plan_tier=tier,
                trial_start_date=datetime.now(UTC),
                trial_end_date=datetime.now(UTC) + timedelta(days=trial_days),
                auto_convert=True,
                custom_terms=custom_terms,
                requires_approval=True,
                created_at=datetime.now(UTC)
            )
            
            return {
                "status": "custom_trial_created",
                "trial_id": trial_subscription.id,
                "trial_end_date": trial_subscription.trial_end_date.isoformat(),
                "requires_approval": trial_subscription.requires_approval,
                "custom_terms": custom_terms,
                "approval_workflow": "manual_review",
                "trial_duration_days": trial_days
            }
            
        except Exception as e:
            logger.error(f"Failed to create custom trial: {str(e)}")
            return {
                "status": "error",
                "message": f"Custom trial creation failed: {str(e)}"
            }
    
    async def cancel_trial(self, company_id: str, reason: str) -> Dict[str, Any]:
        """Cancel trial before auto-conversion"""
        try:
            logger.info(f"Cancelling trial for company {company_id}")
            
            # Find active trial
            # In real implementation, query database
            trial_subscription = Subscription(
                id=str(uuid.uuid4()),
                company_id=company_id,
                subscription_type=SubscriptionType.TRIAL,
                status=SubscriptionStatus.CANCELLED,
                cancelled_at=datetime.now(UTC),
                cancellation_reason=reason
            )
            
            return {
                "status": "cancelled",
                "trial_id": trial_subscription.id,
                "cancellation_date": trial_subscription.cancelled_at.isoformat(),
                "reason": reason,
                "auto_convert": False
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel trial: {str(e)}")
            return {
                "status": "error",
                "message": f"Trial cancellation failed: {str(e)}"
            }
    
    async def process_trial_conversion(self, company_id: str) -> Dict[str, Any]:
        """Process automatic trial to subscription conversion"""
        try:
            logger.info(f"Processing trial conversion for company {company_id}")
            
            # Get trial details
            # In real implementation, query database
            trial_end_date = datetime.now(UTC) - timedelta(hours=1)  # Trial ended
            
            # Create Paystack subscription
            subscription_data = {
                "customer_id": f"CUS_{company_id}",
                "plan_id": "PLN_basic",  # Default to basic plan
                "authorization_code": None  # Will be set when customer provides payment method
            }
            
            paystack_result = await self.paystack_service.create_subscription(subscription_data)
            
            if paystack_result["status"] == "subscription_created":
                # Create local subscription record
                subscription = Subscription(
                    id=str(uuid.uuid4()),
                    company_id=company_id,
                    subscription_type=SubscriptionType.PAID,
                    status=SubscriptionStatus.ACTIVE,
                    plan_tier="basic",
                    paystack_subscription_id=paystack_result["subscription_id"],
                    start_date=datetime.now(UTC),
                    next_billing_date=datetime.now(UTC) + timedelta(days=30),
                    created_at=datetime.now(UTC)
                )
                
                return {
                    "status": "converted",
                    "subscription_id": subscription.id,
                    "paystack_subscription_id": paystack_result["subscription_id"],
                    "conversion_date": datetime.now(UTC).isoformat(),
                    "payment_method": "auto_charge",
                    "plan_tier": "basic"
                }
            else:
                return {
                    "status": "conversion_failed",
                    "message": paystack_result.get("message", "Unknown error"),
                    "paystack_error": paystack_result
                }
                
        except Exception as e:
            logger.error(f"Failed to process trial conversion: {str(e)}")
            return {
                "status": "error",
                "message": f"Trial conversion failed: {str(e)}"
            }
    
    async def change_subscription_plan(self, subscription_id: str, new_plan: str, change_type: str) -> Dict[str, Any]:
        """Change subscription plan (upgrade/downgrade)"""
        try:
            logger.info(f"Changing subscription {subscription_id} to {new_plan} ({change_type})")
            
            # Get current subscription
            current_subscription = await self.paystack_service.get_subscription(subscription_id)
            
            if current_subscription["status"] != "retrieved":
                return {
                    "status": "error",
                    "message": "Subscription not found"
                }
            
            # Calculate prorated amount
            prorated_amount = self._calculate_prorated_amount(
                current_subscription["amount"],
                self.subscription_plans[new_plan].amount,
                change_type
            )
            
            # Update subscription in Paystack
            update_data = {
                "plan": self.subscription_plans[new_plan].name,
                "prorate": True
            }
            
            update_result = await self.paystack_service.update_subscription(subscription_id, update_data)
            
            if update_result["status"] == "subscription_updated":
                return {
                    "status": "plan_changed",
                    "subscription_id": subscription_id,
                    "change_type": change_type,
                    "old_plan": current_subscription.get("plan_id"),
                    "new_plan": new_plan,
                    "effective_date": datetime.now(UTC).isoformat(),
                    "prorated_charge": prorated_amount
                }
            else:
                return {
                    "status": "change_failed",
                    "message": update_result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Failed to change subscription plan: {str(e)}")
            return {
                "status": "error",
                "message": f"Plan change failed: {str(e)}"
            }
    
    async def cancel_subscription(self, subscription_id: str, reason: str) -> Dict[str, Any]:
        """Cancel subscription with retention strategies"""
        try:
            logger.info(f"Cancelling subscription {subscription_id}")
            
            # Generate retention offers
            retention_offers = [
                {
                    "offer_type": "discount",
                    "discount_percentage": 20,
                    "duration_months": 3,
                    "description": "20% off for 3 months"
                },
                {
                    "offer_type": "pause",
                    "duration_months": 2,
                    "description": "Pause subscription for 2 months"
                },
                {
                    "offer_type": "downgrade",
                    "new_plan": "basic",
                    "description": "Downgrade to basic plan at reduced rate"
                }
            ]
            
            # Cancel subscription in Paystack
            cancel_data = {
                "cancel": True,
                "reason": reason
            }
            
            cancel_result = await self.paystack_service.update_subscription(subscription_id, cancel_data)
            
            if cancel_result["status"] == "subscription_updated":
                return {
                    "status": "cancellation_requested",
                    "subscription_id": subscription_id,
                    "cancellation_date": datetime.now(UTC).isoformat(),
                    "retention_offers": retention_offers,
                    "final_billing_date": (datetime.now(UTC) + timedelta(days=30)).isoformat()
                }
            else:
                return {
                    "status": "cancellation_failed",
                    "message": cancel_result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            return {
                "status": "error",
                "message": f"Subscription cancellation failed: {str(e)}"
            }
    
    async def manage_billing_cycle(self, subscription_id: str) -> Dict[str, Any]:
        """Manage subscription billing cycle"""
        try:
            # Get subscription details
            subscription = await self.paystack_service.get_subscription(subscription_id)
            
            if subscription["status"] != "retrieved":
                return {
                    "status": "error",
                    "message": "Subscription not found"
                }
            
            # Calculate next billing date
            next_billing_date = datetime.now(UTC) + timedelta(days=30)
            
            return {
                "status": "cycle_managed",
                "subscription_id": subscription_id,
                "next_billing_date": next_billing_date.isoformat(),
                "amount_due": subscription["amount"],
                "currency": subscription["currency"],
                "billing_cycle": "monthly"
            }
            
        except Exception as e:
            logger.error(f"Failed to manage billing cycle: {str(e)}")
            return {
                "status": "error",
                "message": f"Billing cycle management failed: {str(e)}"
            }
    
    async def create_sla_agreement(self, sla_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create SLA agreement for enterprise clients"""
        try:
            logger.info(f"Creating SLA agreement for company {sla_data['company_id']}")
            
            # Create SLA agreement record
            sla_agreement = {
                "id": str(uuid.uuid4()),
                "company_id": sla_data["company_id"],
                "sla_type": sla_data["sla_type"],
                "uptime_guarantee": sla_data["uptime_guarantee"],
                "response_time_sla": sla_data["response_time_sla"],
                "support_level": sla_data["support_level"],
                "custom_terms": sla_data["custom_terms"],
                "penalty_clauses": sla_data["penalty_clauses"],
                "effective_date": datetime.now(UTC),
                "expiry_date": datetime.now(UTC) + timedelta(days=365),
                "created_at": datetime.now(UTC)
            }
            
            return {
                "status": "sla_created",
                "sla_id": sla_agreement["id"],
                "company_id": sla_data["company_id"],
                "sla_type": sla_data["sla_type"],
                "effective_date": sla_agreement["effective_date"].isoformat(),
                "expiry_date": sla_agreement["expiry_date"].isoformat(),
                "uptime_guarantee": sla_data["uptime_guarantee"],
                "support_level": sla_data["support_level"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create SLA agreement: {str(e)}")
            return {
                "status": "error",
                "message": f"SLA creation failed: {str(e)}"
            }
    
    async def generate_subscription_report(self, report_type: str, period: str) -> Dict[str, Any]:
        """Generate subscription analytics and reporting"""
        try:
            logger.info(f"Generating {report_type} report for {period}")
            
            # Mock analytics data
            metrics = {
                "total_subscriptions": 150,
                "active_subscriptions": 142,
                "trial_conversions": 28,
                "churn_rate": 5.3,
                "mrr": 225000,  # R2,250.00 monthly recurring revenue
                "arr": 2700000,  # R27,000.00 annual recurring revenue
                "average_revenue_per_user": 1500,  # R15.00
                "trial_conversion_rate": 67.5,
                "customer_lifetime_value": 45000  # R450.00
            }
            
            return {
                "status": "report_generated",
                "report_id": str(uuid.uuid4()),
                "report_type": report_type,
                "period": period,
                "metrics": metrics,
                "generated_at": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate subscription report: {str(e)}")
            return {
                "status": "error",
                "message": f"Report generation failed: {str(e)}"
            }
    
    def _calculate_prorated_amount(self, current_amount: int, new_amount: int, change_type: str) -> int:
        """Calculate prorated amount for plan changes"""
        if change_type == "upgrade":
            # Charge difference for remaining days
            return max(0, new_amount - current_amount)
        elif change_type == "downgrade":
            # Credit difference for remaining days
            return min(0, new_amount - current_amount)
        else:
            return 0
    
    async def process_bulk_trial_conversions(self, company_ids: List[str]) -> List[Dict[str, Any]]:
        """Process bulk trial conversions"""
        try:
            tasks = [self.process_trial_conversion(company_id) for company_id in company_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return [
                result if not isinstance(result, Exception) else {
                    "status": "error",
                    "message": str(result)
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Failed to process bulk trial conversions: {str(e)}")
            return [{
                "status": "error",
                "message": f"Bulk conversion failed: {str(e)}"
            }]
    
    async def get_subscription_analytics(self, company_id: str = None) -> Dict[str, Any]:
        """Get subscription analytics for a company or overall"""
        try:
            # Mock analytics data
            analytics = {
                "subscription_count": 150,
                "active_trials": 25,
                "conversion_rate": 67.5,
                "churn_rate": 5.3,
                "mrr_growth": 12.5,
                "average_trial_duration": 18.5,
                "top_converting_tier": "professional",
                "revenue_breakdown": {
                    "basic": 45000,      # R450.00
                    "professional": 135000,  # R1,350.00
                    "enterprise": 45000   # R450.00
                }
            }
            
            return {
                "status": "analytics_retrieved",
                "analytics": analytics,
                "generated_at": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get subscription analytics: {str(e)}")
            return {
                "status": "error",
                "message": f"Analytics retrieval failed: {str(e)}"
            }
