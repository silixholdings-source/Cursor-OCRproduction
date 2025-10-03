"""
Premium Subscription Configuration for South African Market
Defines pricing, limits, and features for each tier
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class SubscriptionTier(str, Enum):
    """Subscription tier enumeration"""
    GROWTH = "growth"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

@dataclass
class TierLimits:
    """Subscription tier limits and quotas"""
    max_users: int
    max_invoices_per_month: int
    max_storage_gb: int
    max_erp_connectors: int
    max_api_calls_per_month: int
    max_custom_workflows: int
    max_entities: int

@dataclass
class TierFeatures:
    """Subscription tier features"""
    features: List[str]
    support_level: str
    sla_uptime: float
    response_time_hours: int
    onboarding_type: str

class SubscriptionConfig:
    """Configuration for premium subscription tiers"""
    
    # Premium Pricing (South African Rand) - Per Tenant
    PRICING = {
        SubscriptionTier.GROWTH: {
            "monthly_price_zar": 600000,  # R6,000.00 in cents
            "annual_price_zar": 6120000,  # R61,200.00 in cents (15% off)
            "annual_savings_zar": 1080000, # R10,800.00 savings
            "annual_discount_percent": 15,  # 15% discount for annual billing
            "currency": "ZAR",
            "billing_cycle": "monthly"
        },
        SubscriptionTier.PROFESSIONAL: {
            "monthly_price_zar": 1200000,  # R12,000.00 in cents
            "annual_price_zar": 12240000,  # R122,400.00 in cents (15% off)
            "annual_savings_zar": 2160000, # R21,600.00 savings
            "annual_discount_percent": 15,  # 15% discount for annual billing
            "currency": "ZAR",
            "billing_cycle": "monthly"
        },
        SubscriptionTier.ENTERPRISE: {
            "monthly_price_zar": 2500000,  # R25,000.00 in cents
            "annual_price_zar": 25500000,  # R255,000.00 in cents (15% off)
            "annual_savings_zar": 4500000, # R45,000.00 savings
            "annual_discount_percent": 15,  # 15% discount for annual billing
            "currency": "ZAR",
            "billing_cycle": "monthly",
            "custom_pricing": True  # Custom pricing for enterprise
        }
    }
    
    # User and Usage Limits - Per Tenant
    LIMITS = {
        SubscriptionTier.GROWTH: TierLimits(
            max_users=5,  # 5 users included
            max_invoices_per_month=2000,  # 2,000 invoices/month
            max_storage_gb=100,
            max_erp_connectors=5,  # Full ERP connectors (GP, D365 BC, Sage, Xero, QuickBooks)
            max_api_calls_per_month=50000,
            max_custom_workflows=5,
            max_entities=1
        ),
        SubscriptionTier.PROFESSIONAL: TierLimits(
            max_users=15,  # 15 users included
            max_invoices_per_month=10000,  # 10,000 invoices/month
            max_storage_gb=500,
            max_erp_connectors=5,  # Full ERP connectors
            max_api_calls_per_month=150000,
            max_custom_workflows=15,
            max_entities=5
        ),
        SubscriptionTier.ENTERPRISE: TierLimits(
            max_users=999,  # Unlimited users
            max_invoices_per_month=50000,  # 50,000+ invoices/month (scalable)
            max_storage_gb=2000,  # 2TB
            max_erp_connectors=999,  # Unlimited ERP connectors
            max_api_calls_per_month=999999,  # Unlimited API calls
            max_custom_workflows=999,  # Unlimited custom workflows
            max_entities=999  # Unlimited entities
        )
    }
    
    # Features by Tier - Per Tenant
    FEATURES = {
        SubscriptionTier.GROWTH: TierFeatures(
            features=[
                "full_erp_connectors",  # GP, D365 BC, Sage, Xero, QuickBooks
                "csv_export",
                "advanced_ocr",
                "email_support",
                "invoice_processing",
                "basic_analytics",
                "audit_trails",
                "mobile_app",
                "multi_language_support",
                "standard_workflows"
            ],
            support_level="email",
            sla_uptime=99.5,
            response_time_hours=24,
            onboarding_type="self_service"
        ),
        SubscriptionTier.PROFESSIONAL: TierFeatures(
            features=[
                "full_erp_connectors",  # All Growth ERP connectors
                "csv_export",
                "advanced_ocr",
                "email_support",
                "invoice_processing",
                "api_access",  # New for Professional
                "advanced_analytics",  # New for Professional
                "role_based_access",  # New for Professional
                "priority_support",  # New for Professional
                "audit_trails",
                "mobile_app",
                "multi_language_support",
                "custom_workflows",
                "advanced_security",
                "backup_restore"
            ],
            support_level="priority",
            sla_uptime=99.7,
            response_time_hours=12,
            onboarding_type="dedicated"
        ),
        SubscriptionTier.ENTERPRISE: TierFeatures(
            features=[
                "full_erp_connectors",  # All Professional ERP connectors
                "csv_export",
                "advanced_ocr",
                "email_support",
                "invoice_processing",
                "api_access",
                "advanced_analytics",
                "role_based_access",
                "priority_support",
                "custom_integrations",  # New for Enterprise
                "sla_backed_uptime",  # New for Enterprise
                "dedicated_support_manager",  # New for Enterprise
                "private_cloud_option",  # New for Enterprise
                "unlimited_erp_connectors",
                "unlimited_users",
                "unlimited_invoices",
                "dedicated_account_manager",
                "custom_development",
                "white_labeling",
                "sso_integration",
                "advanced_security",
                "compliance_reporting",
                "custom_analytics",
                "unlimited_workflows"
            ],
            support_level="dedicated",
            sla_uptime=99.9,
            response_time_hours=4,
            onboarding_type="dedicated_plus"
        )
    }
    
    # Trial Periods
    TRIAL_PERIODS = {
        SubscriptionTier.GROWTH: {
            "standard_days": 14,
            "extended_days": 21,
            "enterprise_negotiation": 30
        },
        SubscriptionTier.PROFESSIONAL: {
            "standard_days": 21,
            "extended_days": 30,
            "enterprise_negotiation": 45
        },
        SubscriptionTier.ENTERPRISE: {
            "standard_days": 30,
            "extended_days": 45,
            "enterprise_negotiation": 60
        }
    }
    
    # Support Levels
    SUPPORT_LEVELS = {
        "email_chat": {
            "name": "Email & Chat Support",
            "response_time": "24 hours",
            "availability": "Business hours (SAST)",
            "channels": ["email", "chat", "help_center"]
        },
        "priority": {
            "name": "Priority Support",
            "response_time": "12 hours",
            "availability": "Extended hours",
            "channels": ["email", "chat", "phone", "help_center"]
        },
        "dedicated": {
            "name": "Dedicated Account Manager",
            "response_time": "4 hours",
            "availability": "24/7 for critical issues",
            "channels": ["phone", "email", "chat", "video_call", "on_site"]
        }
    }
    
    # SLA Terms
    SLA_TERMS = {
        SubscriptionTier.GROWTH: {
            "uptime_guarantee": 99.5,
            "response_time": "24 hours",
            "resolution_time": "72 hours",
            "penalty_type": "service_credit",
            "penalty_percent": 5
        },
        SubscriptionTier.PROFESSIONAL: {
            "uptime_guarantee": 99.7,
            "response_time": "12 hours",
            "resolution_time": "48 hours",
            "penalty_type": "service_credit",
            "penalty_percent": 10
        },
        SubscriptionTier.ENTERPRISE: {
            "uptime_guarantee": 99.9,
            "response_time": "4 hours",
            "resolution_time": "24 hours",
            "penalty_type": "service_credit",
            "penalty_percent": 25
        }
    }
    
    @classmethod
    def get_tier_pricing(cls, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get pricing information for a specific tier"""
        return cls.PRICING.get(tier, {})
    
    @classmethod
    def get_tier_limits(cls, tier: SubscriptionTier) -> TierLimits:
        """Get limits for a specific tier"""
        return cls.LIMITS.get(tier)
    
    @classmethod
    def get_tier_features(cls, tier: SubscriptionTier) -> TierFeatures:
        """Get features for a specific tier"""
        return cls.FEATURES.get(tier)
    
    @classmethod
    def get_trial_period(cls, tier: SubscriptionTier, trial_type: str = "standard") -> int:
        """Get trial period for a specific tier and type"""
        tier_trials = cls.TRIAL_PERIODS.get(tier, {})
        return tier_trials.get(trial_type, 14)
    
    @classmethod
    def get_sla_terms(cls, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get SLA terms for a specific tier"""
        return cls.SLA_TERMS.get(tier, {})
    
    @classmethod
    def get_support_level(cls, support_type: str) -> Dict[str, Any]:
        """Get support level details"""
        return cls.SUPPORT_LEVELS.get(support_type, {})
    
    @classmethod
    def calculate_annual_price(cls, tier: SubscriptionTier, monthly_price: int) -> int:
        """Calculate annual price with discount"""
        discount_percent = cls.PRICING.get(tier, {}).get("annual_discount_percent", 0)
        annual_price = monthly_price * 12
        discount_amount = annual_price * (discount_percent / 100)
        return int(annual_price - discount_amount)
    
    @classmethod
    def validate_tier_upgrade(cls, current_tier: SubscriptionTier, target_tier: SubscriptionTier) -> bool:
        """Validate if tier upgrade is allowed"""
        tier_order = [SubscriptionTier.GROWTH, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]
        current_index = tier_order.index(current_tier)
        target_index = tier_order.index(target_tier)
        return target_index > current_index
    
    @classmethod
    def get_feature_comparison(cls) -> Dict[str, List[str]]:
        """Get feature comparison across all tiers"""
        comparison = {}
        for tier in SubscriptionTier:
            features = cls.FEATURES.get(tier, TierFeatures(features=[], support_level="", sla_uptime=0, response_time_hours=0, onboarding_type=""))
            comparison[tier.value] = features.features
        return comparison
