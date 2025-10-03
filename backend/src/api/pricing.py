"""
Pricing API Endpoints for Premium South African Subscription Plans
Shows pricing tiers, features, and limits
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime

from config.subscription_config import SubscriptionConfig, SubscriptionTier
from schemas.pricing import (
    PricingResponse, TierPricing, TierFeatures, TierLimits,
    FeatureComparisonResponse, SupportLevelResponse, SLAComparisonResponse
)

router = APIRouter(prefix="/api/v1/pricing", tags=["pricing"])

# Initialize configuration
config = SubscriptionConfig()

@router.get("/tiers", response_model=List[PricingResponse])
async def get_pricing_tiers():
    """Get all available pricing tiers with full details"""
    try:
        pricing_tiers = []
        
        for tier in SubscriptionTier:
            tier_pricing = config.get_tier_pricing(tier)
            tier_limits = config.get_tier_limits(tier)
            tier_features = config.get_tier_features(tier)
            sla_terms = config.get_sla_terms(tier)
            
            # Calculate annual pricing with discount
            monthly_price = tier_pricing["monthly_price_zar"]
            annual_price = config.calculate_annual_price(tier, monthly_price)
            discount_percent = tier_pricing.get("annual_discount_percent", 0)
            
            pricing_response = PricingResponse(
                tier=tier.value,
                name=tier.value.title() + " Plan",
                monthly_price_zar=monthly_price,
                annual_price_zar=annual_price,
                annual_discount_percent=discount_percent,
                currency="ZAR",
                billing_cycle="monthly",
                custom_pricing=tier_pricing.get("custom_pricing", False),
                limits=TierLimits(
                    max_users=tier_limits.max_users,
                    max_invoices_per_month=tier_limits.max_invoices_per_month,
                    max_storage_gb=tier_limits.max_storage_gb,
                    max_erp_connectors=tier_limits.max_erp_connectors,
                    max_api_calls_per_month=tier_limits.max_api_calls_per_month,
                    max_custom_workflows=tier_limits.max_custom_workflows,
                    max_entities=tier_limits.max_entities
                ),
                features=TierFeatures(
                    features=tier_features.features,
                    support_level=tier_features.support_level,
                    sla_uptime=tier_features.sla_uptime,
                    response_time_hours=tier_features.response_time_hours,
                    onboarding_type=tier_features.onboarding_type
                ),
                sla_terms=sla_terms,
                trial_days=config.get_trial_period(tier, "standard"),
                extended_trial_days=config.get_trial_period(tier, "extended"),
                enterprise_trial_days=config.get_trial_period(tier, "enterprise_negotiation")
            )
            
            pricing_tiers.append(pricing_response)
        
        return pricing_tiers
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pricing tiers: {str(e)}"
        )

@router.get("/tier/{tier_name}", response_model=PricingResponse)
async def get_tier_details(tier_name: str):
    """Get detailed pricing information for a specific tier"""
    try:
        # Validate tier name
        try:
            tier = SubscriptionTier(tier_name.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {tier_name}. Available tiers: {[t.value for t in SubscriptionTier]}"
            )
        
        tier_pricing = config.get_tier_pricing(tier)
        tier_limits = config.get_tier_limits(tier)
        tier_features = config.get_tier_features(tier)
        sla_terms = config.get_sla_terms(tier)
        
        # Calculate annual pricing with discount
        monthly_price = tier_pricing["monthly_price_zar"]
        annual_price = config.calculate_annual_price(tier, monthly_price)
        discount_percent = tier_pricing.get("annual_discount_percent", 0)
        
        return PricingResponse(
            tier=tier.value,
            name=tier.value.title() + " Plan",
            monthly_price_zar=monthly_price,
            annual_price_zar=annual_price,
            annual_discount_percent=discount_percent,
            currency="ZAR",
            billing_cycle="monthly",
            custom_pricing=tier_pricing.get("custom_pricing", False),
            limits=TierLimits(
                max_users=tier_limits.max_users,
                max_invoices_per_month=tier_limits.max_invoices_per_month,
                max_storage_gb=tier_limits.max_storage_gb,
                max_erp_connectors=tier_limits.max_erp_connectors,
                max_api_calls_per_month=tier_limits.max_api_calls_per_month,
                max_custom_workflows=tier_limits.max_custom_workflows,
                max_entities=tier_limits.max_entities
            ),
            features=TierFeatures(
                features=tier_features.features,
                support_level=tier_features.support_level,
                sla_uptime=tier_features.sla_uptime,
                response_time_hours=tier_features.response_time_hours,
                onboarding_type=tier_features.onboarding_type
            ),
            sla_terms=sla_terms,
            trial_days=config.get_trial_period(tier, "standard"),
            extended_trial_days=config.get_trial_period(tier, "extended"),
            enterprise_trial_days=config.get_trial_period(tier, "enterprise_negotiation")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tier details: {str(e)}"
        )

@router.get("/features/comparison", response_model=FeatureComparisonResponse)
async def get_feature_comparison():
    """Get feature comparison across all tiers"""
    try:
        feature_comparison = config.get_feature_comparison()
        
        return FeatureComparisonResponse(
            tiers=list(feature_comparison.keys()),
            features_by_tier=feature_comparison,
            all_features=list(set([
                feature for features in feature_comparison.values() 
                for feature in features
            ]))
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feature comparison: {str(e)}"
        )

@router.get("/support-levels", response_model=List[SupportLevelResponse])
async def get_support_levels():
    """Get all support levels and their details"""
    try:
        support_levels = []
        
        for support_type, details in config.SUPPORT_LEVELS.items():
            support_response = SupportLevelResponse(
                support_type=support_type,
                name=details["name"],
                response_time=details["response_time"],
                availability=details["availability"],
                channels=details["channels"]
            )
            support_levels.append(support_response)
        
        return support_levels
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get support levels: {str(e)}"
        )

@router.get("/sla-comparison", response_model=SLAComparisonResponse)
async def get_sla_comparison():
    """Get SLA comparison across all tiers"""
    try:
        sla_comparison = {}
        
        for tier in SubscriptionTier:
            sla_terms = config.get_sla_terms(tier)
            sla_comparison[tier.value] = sla_terms
        
        return SLAComparisonResponse(
            tiers=list(sla_comparison.keys()),
            sla_by_tier=sla_comparison
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get SLA comparison: {str(e)}"
        )

@router.get("/calculator")
async def calculate_pricing(
    tier: str,
    billing_cycle: str = "monthly",
    user_count: int = None,
    invoice_count: int = None
):
    """Calculate pricing based on tier and usage"""
    try:
        # Validate tier
        try:
            tier_enum = SubscriptionTier(tier.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {tier}. Available tiers: {[t.value for t in SubscriptionTier]}"
            )
        
        # Get base pricing
        tier_pricing = config.get_tier_pricing(tier_enum)
        tier_limits = config.get_tier_limits(tier_enum)
        
        base_price = tier_pricing["monthly_price_zar"]
        
        # Calculate pricing based on billing cycle
        if billing_cycle == "annual":
            price = config.calculate_annual_price(tier_enum, base_price)
            discount_percent = tier_pricing.get("annual_discount_percent", 0)
        else:
            price = base_price
            discount_percent = 0
        
        # Calculate overage charges (if applicable)
        overage_charges = {}
        
        if user_count and user_count > tier_limits.max_users:
            excess_users = user_count - tier_limits.max_users
            overage_charges["users"] = {
                "excess_count": excess_users,
                "rate_per_user": 50000,  # R500 per additional user
                "total_charge": excess_users * 50000
            }
        
        if invoice_count and invoice_count > tier_limits.max_invoices_per_month:
            excess_invoices = invoice_count - tier_limits.max_invoices_per_month
            overage_charges["invoices"] = {
                "excess_count": excess_invoices,
                "rate_per_invoice": 50,  # R0.50 per additional invoice
                "total_charge": excess_invoices * 50
            }
        
        total_overage = sum(charge["total_charge"] for charge in overage_charges.values())
        total_price = price + total_overage
        
        return {
            "tier": tier,
            "billing_cycle": billing_cycle,
            "base_price_zar": price,
            "discount_percent": discount_percent,
            "overage_charges": overage_charges,
            "total_overage_zar": total_overage,
            "total_price_zar": total_price,
            "currency": "ZAR",
            "calculated_at": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate pricing: {str(e)}"
        )

@router.get("/trial-options")
async def get_trial_options():
    """Get available trial options for each tier"""
    try:
        trial_options = {}
        
        for tier in SubscriptionTier:
            trial_options[tier.value] = {
                "standard_trial": config.get_trial_period(tier, "standard"),
                "extended_trial": config.get_trial_period(tier, "extended"),
                "enterprise_negotiation": config.get_trial_period(tier, "enterprise_negotiation"),
                "max_custom_trial": 90,  # Maximum custom trial period
                "auto_convert": True,
                "requires_approval": tier == SubscriptionTier.ENTERPRISE
            }
        
        return trial_options
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trial options: {str(e)}"
        )








