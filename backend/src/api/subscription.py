"""
Subscription API Endpoints for Paystack Integration
Handles subscription management, trials, and billing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from core.auth import get_current_user, get_current_company
from core.permissions import require_permission
from src.models.user import User, UserRole
from src.models.company import Company
from src.models.subscription import Subscription, SubscriptionPlan, SLA, PaymentMethod, BillingHistory
from services.subscription_manager import SubscriptionManager
from services.paystack_service import PaystackService
from services.popia_compliance import POPIAComplianceService
from schemas.subscription import (
    SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate,
    TrialCreate, TrialResponse, SLARequest, SLAResponse,
    PaymentMethodCreate, PaymentMethodResponse, BillingHistoryResponse,
    SubscriptionAnalyticsResponse, POPIAConsentRequest, POPIAConsentResponse
)

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])
security = HTTPBearer()

# Service instances
subscription_manager = SubscriptionManager()
paystack_service = PaystackService()
popia_service = POPIAComplianceService()

@router.post("/plans", response_model=List[SubscriptionPlan])
async def create_subscription_plans(
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company)
):
    """Create subscription plans in Paystack"""
    try:
        plans = []
        
        # Create basic plan
        basic_plan = await paystack_service.create_plan(
            paystack_service.subscription_plans["basic"]
        )
        if basic_plan["status"] == "created":
            plans.append(basic_plan)
        
        # Create professional plan
        professional_plan = await paystack_service.create_plan(
            paystack_service.subscription_plans["professional"]
        )
        if professional_plan["status"] == "created":
            plans.append(professional_plan)
        
        # Create enterprise plan
        enterprise_plan = await paystack_service.create_plan(
            paystack_service.subscription_plans["enterprise"]
        )
        if enterprise_plan["status"] == "created":
            plans.append(enterprise_plan)
        
        return plans
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription plans: {str(e)}"
        )

@router.post("/trials", response_model=TrialResponse)
async def create_trial_subscription(
    trial_data: TrialCreate,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company)
):
    """Create a trial subscription with configurable duration"""
    try:
        # Validate trial duration
        if trial_data.trial_days not in [7, 14, 30, 60, 90]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid trial duration. Allowed: 7, 14, 30, 60, 90 days"
            )
        
        # Create trial subscription
        result = await subscription_manager.create_trial_subscription(
            current_company.id,
            trial_data.trial_days,
            trial_data.tier
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return TrialResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trial subscription: {str(e)}"
        )

@router.post("/trials/custom", response_model=TrialResponse)
async def create_custom_trial(
    trial_data: TrialCreate,
    current_user: User = Depends(require_permission("subscription.manage")),
    current_company: Company = Depends(get_current_company)
):
    """Create a custom trial period for enterprise negotiations"""
    try:
        # Validate enterprise tier requirement
        if trial_data.tier != "enterprise":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom trials are only available for enterprise tier"
            )
        
        # Create custom trial
        result = await subscription_manager.create_custom_trial(
            current_company.id,
            trial_data.trial_days,
            trial_data.tier,
            trial_data.custom_terms or "Extended trial for enterprise evaluation"
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return TrialResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom trial: {str(e)}"
        )

@router.post("/trials/{trial_id}/cancel")
async def cancel_trial(
    trial_id: str,
    reason: str,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company)
):
    """Cancel trial before auto-conversion"""
    try:
        result = await subscription_manager.cancel_trial(
            current_company.id,
            reason
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel trial: {str(e)}"
        )

@router.post("/trials/{trial_id}/convert")
async def convert_trial_to_subscription(
    trial_id: str,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company)
):
    """Convert trial to paid subscription"""
    try:
        result = await subscription_manager.process_trial_conversion(
            current_company.id
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert trial: {str(e)}"
        )

@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company)
):
    """Get current subscription details"""
    try:
        # In real implementation, query database for current subscription
        # For now, return mock data
        subscription_data = {
            "id": str(uuid.uuid4()),
            "company_id": current_company.id,
            "subscription_type": "trial",
            "status": "active",
            "plan_tier": "basic",
            "trial_end_date": (datetime.now(UTC) + timedelta(days=14)).isoformat(),
            "auto_convert": True,
            "created_at": datetime.now(UTC).isoformat()
        }
        
        return SubscriptionResponse(**subscription_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription: {str(e)}"
        )

@router.put("/{subscription_id}/plan", response_model=SubscriptionResponse)
async def change_subscription_plan(
    subscription_id: str,
    new_plan: str,
    change_type: str,
    current_user: User = Depends(require_permission("subscription.manage")),
    current_company: Company = Depends(get_current_company)
):
    """Change subscription plan (upgrade/downgrade)"""
    try:
        result = await subscription_manager.change_subscription_plan(
            subscription_id,
            new_plan,
            change_type
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change subscription plan: {str(e)}"
        )

@router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    reason: str,
    current_user: User = Depends(require_permission("subscription.manage")),
    current_company: Company = Depends(get_current_company)
):
    """Cancel subscription with retention strategies"""
    try:
        result = await subscription_manager.cancel_subscription(
            subscription_id,
            reason
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

@router.post("/slas", response_model=SLAResponse)
async def create_sla_agreement(
    sla_data: SLARequest,
    current_user: User = Depends(require_permission("subscription.manage")),
    current_company: Company = Depends(get_current_company)
):
    """Create SLA agreement for enterprise clients"""
    try:
        # Validate enterprise tier requirement
        if current_company.tier.value != "enterprise":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SLA agreements are only available for enterprise tier"
            )
        
        sla_request_data = {
            "company_id": current_company.id,
            "sla_type": sla_data.sla_type,
            "uptime_guarantee": sla_data.uptime_guarantee,
            "response_time_sla": sla_data.response_time_sla,
            "support_level": sla_data.support_level,
            "custom_terms": sla_data.custom_terms,
            "penalty_clauses": sla_data.penalty_clauses
        }
        
        result = await subscription_manager.create_sla_agreement(sla_request_data)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return SLAResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create SLA agreement: {str(e)}"
        )

@router.get("/analytics", response_model=SubscriptionAnalyticsResponse)
async def get_subscription_analytics(
    current_user: User = Depends(require_permission("subscription.view")),
    current_company: Company = Depends(get_current_company)
):
    """Get subscription analytics and metrics"""
    try:
        result = await subscription_manager.get_subscription_analytics(
            current_company.id
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return SubscriptionAnalyticsResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription analytics: {str(e)}"
        )

@router.post("/popia/consent", response_model=POPIAConsentResponse)
async def record_popia_consent(
    consent_data: POPIAConsentRequest,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company)
):
    """Record POPIA-compliant consent for data processing"""
    try:
        consent_request_data = {
            "company_id": current_company.id,
            "consent_type": consent_data.consent_type,
            "consent_given": consent_data.consent_given,
            "consent_date": datetime.now(UTC),
            "legal_basis": consent_data.legal_basis,
            "data_categories": consent_data.data_categories,
            "retention_period": consent_data.retention_period,
            "third_party_sharing": consent_data.third_party_sharing
        }
        
        result = await popia_service.record_consent(consent_request_data)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return POPIAConsentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record POPIA consent: {str(e)}"
        )

@router.get("/popia/data-request/{request_type}")
async def handle_data_request(
    request_type: str,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company)
):
    """Handle POPIA data subject rights requests"""
    try:
        result = await popia_service.handle_data_access_request(
            current_user.id,
            request_type
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle data request: {str(e)}"
        )

@router.post("/popia/data-deletion")
async def handle_data_deletion_request(
    deletion_type: str,
    current_user: User = Depends(get_current_user),
    current_company: Company = Depends(get_current_company)
):
    """Handle POPIA data deletion request (right to be forgotten)"""
    try:
        result = await popia_service.handle_data_deletion_request(
            current_user.id,
            deletion_type
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle data deletion request: {str(e)}"
        )

@router.get("/popia/compliance-report")
async def generate_popia_report(
    report_type: str = "compliance_summary",
    current_user: User = Depends(require_permission("compliance.view")),
    current_company: Company = Depends(get_current_company)
):
    """Generate POPIA compliance report"""
    try:
        result = await popia_service.generate_popia_report(
            current_company.id,
            report_type
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate POPIA report: {str(e)}"
        )

@router.post("/webhooks/paystack")
async def paystack_webhook(
    payload: Dict[str, Any],
    signature: str = None
):
    """Handle Paystack webhook events"""
    try:
        # Validate webhook signature
        if not paystack_service.validate_webhook(str(payload), signature or ""):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Process webhook
        result = paystack_service.process_webhook(payload)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )








