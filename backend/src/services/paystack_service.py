"""
Paystack Integration Service for South African Payment Processing
Handles subscriptions, trials, and compliance with PCI-DSS standards
"""
import logging
import httpx
import hashlib
import hmac
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class SubscriptionPlan:
    """Paystack subscription plan configuration"""
    name: str
    amount: int  # Amount in kobo (cents)
    interval: str  # monthly, yearly
    currency: str = "ZAR"  # South African Rand
    tier: str = "basic"
    features: List[str] = None
    trial_period_days: int = 0
    
    def __post_init__(self):
        if self.features is None:
            self.features = []

@dataclass
class TrialPeriod:
    """Trial period configuration"""
    days: int
    name: str
    is_custom: bool = False
    requires_approval: bool = False
    custom_terms: Optional[str] = None

class PaystackService:
    """Paystack payment service integration for South Africa"""
    
    def __init__(self, secret_key: str = None, public_key: str = None):
        self.secret_key = secret_key or settings.PAYSTACK_SECRET_KEY
        self.public_key = public_key or settings.PAYSTACK_PUBLIC_KEY
        
        if not self.secret_key or not self.public_key:
            raise ValueError("Paystack credentials not configured")
        
        self.base_url = "https://api.paystack.co"
        self.webhook_secret = settings.PAYSTACK_WEBHOOK_SECRET
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.secret_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        logger.info("Paystack service initialized for South African market")
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate Paystack API connection"""
        try:
            response = await self.client.get("/transaction/verify/verification")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "connected",
                    "provider": "paystack",
                    "integration_id": data.get("data", {}).get("integration"),
                    "domain": data.get("data", {}).get("domain"),
                    "verified_at": datetime.now(UTC).isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Connection failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Paystack connection validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }
    
    async def create_plan(self, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Create a subscription plan in Paystack"""
        try:
            payload = {
                "name": plan.name,
                "amount": plan.amount,
                "interval": plan.interval,
                "currency": plan.currency,
                "description": f"{plan.tier.title()} plan with {', '.join(plan.features)}"
            }
            
            response = await self.client.post("/plan", json=payload)
            
            if response.status_code == 201:
                data = response.json()
                plan_data = data.get("data", {})
                
                return {
                    "status": "created",
                    "plan_id": plan_data.get("plan_code"),
                    "amount": plan_data.get("amount"),
                    "currency": plan_data.get("currency"),
                    "interval": plan_data.get("interval"),
                    "created_at": plan_data.get("createdAt")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Plan creation failed: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Failed to create Paystack plan: {str(e)}")
            return {
                "status": "error",
                "message": f"Plan creation failed: {str(e)}"
            }
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a customer in Paystack"""
        try:
            payload = {
                "email": customer_data["email"],
                "first_name": customer_data.get("first_name", ""),
                "last_name": customer_data.get("last_name", ""),
                "phone": customer_data.get("phone", ""),
                "metadata": {
                    "company_id": customer_data.get("company_id"),
                    "company_name": customer_data.get("company_name"),
                    "country": customer_data.get("country", "ZA"),
                    "tier": customer_data.get("tier", "basic")
                }
            }
            
            response = await self.client.post("/customer", json=payload)
            
            if response.status_code == 201:
                data = response.json()
                customer = data.get("data", {})
                
                return {
                    "status": "created",
                    "customer_id": customer.get("customer_code"),
                    "email": customer.get("email"),
                    "created_at": customer.get("createdAt")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Customer creation failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to create Paystack customer: {str(e)}")
            return {
                "status": "error",
                "message": f"Customer creation failed: {str(e)}"
            }
    
    async def initialize_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize payment with Paystack (PCI-DSS compliant)"""
        try:
            payload = {
                "amount": payment_data["amount"],
                "currency": payment_data.get("currency", "ZAR"),
                "email": payment_data["customer_email"],
                "reference": payment_data["reference"],
                "callback_url": payment_data.get("callback_url"),
                "metadata": payment_data.get("metadata", {})
            }
            
            response = await self.client.post("/transaction/initialize", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                transaction = data.get("data", {})
                
                return {
                    "status": "authorization_created",
                    "authorization_url": transaction.get("authorization_url"),
                    "access_code": transaction.get("access_code"),
                    "reference": transaction.get("reference"),
                    "amount": transaction.get("amount"),
                    "currency": transaction.get("currency")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Payment initialization failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to initialize Paystack payment: {str(e)}")
            return {
                "status": "error",
                "message": f"Payment initialization failed: {str(e)}"
            }
    
    async def create_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a subscription in Paystack"""
        try:
            payload = {
                "customer": subscription_data["customer_id"],
                "plan": subscription_data["plan_id"],
                "authorization": subscription_data.get("authorization_code"),
                "start_date": subscription_data.get("start_date")
            }
            
            response = await self.client.post("/subscription", json=payload)
            
            if response.status_code == 201:
                data = response.json()
                subscription = data.get("data", {})
                
                return {
                    "status": "subscription_created",
                    "subscription_id": subscription.get("subscription_code"),
                    "customer_id": subscription.get("customer"),
                    "plan_id": subscription.get("plan"),
                    "status": subscription.get("status"),
                    "start_date": subscription.get("start"),
                    "next_payment_date": subscription.get("next_payment_date"),
                    "amount": subscription.get("amount"),
                    "currency": subscription.get("currency")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Subscription creation failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to create Paystack subscription: {str(e)}")
            return {
                "status": "error",
                "message": f"Subscription creation failed: {str(e)}"
            }
    
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details from Paystack"""
        try:
            response = await self.client.get(f"/subscription/{subscription_id}")
            
            if response.status_code == 200:
                data = response.json()
                subscription = data.get("data", {})
                
                return {
                    "status": "retrieved",
                    "subscription_id": subscription.get("subscription_code"),
                    "customer_id": subscription.get("customer"),
                    "plan_id": subscription.get("plan"),
                    "status": subscription.get("status"),
                    "start_date": subscription.get("start"),
                    "next_payment_date": subscription.get("next_payment_date"),
                    "amount": subscription.get("amount"),
                    "currency": subscription.get("currency"),
                    "created_at": subscription.get("createdAt")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Subscription retrieval failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to get Paystack subscription: {str(e)}")
            return {
                "status": "error",
                "message": f"Subscription retrieval failed: {str(e)}"
            }
    
    async def update_subscription(self, subscription_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update subscription in Paystack"""
        try:
            response = await self.client.put(f"/subscription/{subscription_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                subscription = data.get("data", {})
                
                return {
                    "status": "subscription_updated",
                    "subscription_id": subscription.get("subscription_code"),
                    "status": subscription.get("status"),
                    "plan_id": subscription.get("plan"),
                    "updated_at": subscription.get("updatedAt")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Subscription update failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to update Paystack subscription: {str(e)}")
            return {
                "status": "error",
                "message": f"Subscription update failed: {str(e)}"
            }
    
    def validate_webhook(self, payload: str, signature: str) -> bool:
        """Validate Paystack webhook signature"""
        try:
            if not self.webhook_secret:
                logger.warning("Webhook secret not configured")
                return False
            
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Webhook validation failed: {str(e)}")
            return False
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Paystack webhook events"""
        try:
            event_type = webhook_data.get("event")
            data = webhook_data.get("data", {})
            
            logger.info(f"Processing Paystack webhook: {event_type}")
            
            if event_type == "subscription.create":
                return self._handle_subscription_create(data)
            elif event_type == "subscription.disable":
                return self._handle_subscription_disable(data)
            elif event_type == "subscription.enable":
                return self._handle_subscription_enable(data)
            elif event_type == "charge.success":
                return self._handle_charge_success(data)
            elif event_type == "charge.failed":
                return self._handle_charge_failed(data)
            else:
                return {
                    "status": "webhook_processed",
                    "event_type": event_type,
                    "message": "Event logged but not processed"
                }
                
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Webhook processing failed: {str(e)}"
            }
    
    def _handle_subscription_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription creation webhook"""
        return {
            "status": "webhook_processed",
            "event_type": "subscription.create",
            "subscription_id": data.get("subscription_code"),
            "customer_id": data.get("customer"),
            "plan_id": data.get("plan"),
            "processed_at": datetime.now(UTC).isoformat()
        }
    
    def _handle_subscription_disable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription disable webhook"""
        return {
            "status": "webhook_processed",
            "event_type": "subscription.disable",
            "subscription_id": data.get("subscription_code"),
            "processed_at": datetime.now(UTC).isoformat()
        }
    
    def _handle_subscription_enable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription enable webhook"""
        return {
            "status": "webhook_processed",
            "event_type": "subscription.enable",
            "subscription_id": data.get("subscription_code"),
            "processed_at": datetime.now(UTC).isoformat()
        }
    
    def _handle_charge_success(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful charge webhook"""
        return {
            "status": "webhook_processed",
            "event_type": "charge.success",
            "transaction_id": data.get("reference"),
            "amount": data.get("amount"),
            "customer_email": data.get("customer", {}).get("email"),
            "processed_at": datetime.now(UTC).isoformat()
        }
    
    def _handle_charge_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed charge webhook"""
        return {
            "status": "webhook_processed",
            "event_type": "charge.failed",
            "transaction_id": data.get("reference"),
            "amount": data.get("amount"),
            "customer_email": data.get("customer", {}).get("email"),
            "failure_reason": data.get("gateway_response"),
            "processed_at": datetime.now(UTC).isoformat()
        }
    
    async def get_transaction(self, reference: str) -> Dict[str, Any]:
        """Get transaction details from Paystack"""
        try:
            response = await self.client.get(f"/transaction/verify/{reference}")
            
            if response.status_code == 200:
                data = response.json()
                transaction = data.get("data", {})
                
                return {
                    "status": "retrieved",
                    "transaction_id": transaction.get("reference"),
                    "amount": transaction.get("amount"),
                    "currency": transaction.get("currency"),
                    "status": transaction.get("status"),
                    "customer_email": transaction.get("customer", {}).get("email"),
                    "paid_at": transaction.get("paid_at"),
                    "created_at": transaction.get("createdAt")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Transaction retrieval failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to get Paystack transaction: {str(e)}")
            return {
                "status": "error",
                "message": f"Transaction retrieval failed: {str(e)}"
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()








