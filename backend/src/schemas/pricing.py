"""
Pricing Schemas for Premium South African Subscription Plans
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class TierLimits(BaseModel):
    """Subscription tier limits and quotas"""
    max_users: int = Field(..., description="Maximum number of users")
    max_invoices_per_month: int = Field(..., description="Maximum invoices per month")
    max_storage_gb: int = Field(..., description="Maximum storage in GB")
    max_erp_connectors: int = Field(..., description="Maximum ERP connectors")
    max_api_calls_per_month: int = Field(..., description="Maximum API calls per month")
    max_custom_workflows: int = Field(..., description="Maximum custom workflows")
    max_entities: int = Field(..., description="Maximum entities/companies")

class TierFeatures(BaseModel):
    """Subscription tier features"""
    features: List[str] = Field(..., description="List of features included")
    support_level: str = Field(..., description="Support level provided")
    sla_uptime: float = Field(..., description="SLA uptime guarantee percentage")
    response_time_hours: int = Field(..., description="Response time in hours")
    onboarding_type: str = Field(..., description="Type of onboarding provided")

class PricingResponse(BaseModel):
    """Complete pricing information for a tier"""
    tier: str = Field(..., description="Tier name")
    name: str = Field(..., description="Display name")
    monthly_price_zar: int = Field(..., description="Monthly price in cents (ZAR)")
    annual_price_zar: int = Field(..., description="Annual price in cents (ZAR)")
    annual_discount_percent: int = Field(..., description="Annual discount percentage")
    currency: str = Field(default="ZAR", description="Currency code")
    billing_cycle: str = Field(default="monthly", description="Billing cycle")
    custom_pricing: bool = Field(default=False, description="Whether custom pricing is available")
    limits: TierLimits = Field(..., description="Tier limits and quotas")
    features: TierFeatures = Field(..., description="Tier features")
    sla_terms: Dict[str, Any] = Field(..., description="SLA terms and conditions")
    trial_days: int = Field(..., description="Standard trial period in days")
    extended_trial_days: int = Field(..., description="Extended trial period in days")
    enterprise_trial_days: int = Field(..., description="Enterprise negotiation trial period in days")

class FeatureComparisonResponse(BaseModel):
    """Feature comparison across all tiers"""
    tiers: List[str] = Field(..., description="List of available tiers")
    features_by_tier: Dict[str, List[str]] = Field(..., description="Features by tier")
    all_features: List[str] = Field(..., description="All available features")

class SupportLevelResponse(BaseModel):
    """Support level details"""
    support_type: str = Field(..., description="Type of support")
    name: str = Field(..., description="Support level name")
    response_time: str = Field(..., description="Response time commitment")
    availability: str = Field(..., description="Support availability")
    channels: List[str] = Field(..., description="Support channels available")

class SLAComparisonResponse(BaseModel):
    """SLA comparison across all tiers"""
    tiers: List[str] = Field(..., description="List of available tiers")
    sla_by_tier: Dict[str, Dict[str, Any]] = Field(..., description="SLA terms by tier")

class PricingCalculatorRequest(BaseModel):
    """Request for pricing calculation"""
    tier: str = Field(..., description="Subscription tier")
    billing_cycle: str = Field(default="monthly", description="Billing cycle (monthly/annual)")
    user_count: Optional[int] = Field(None, description="Number of users")
    invoice_count: Optional[int] = Field(None, description="Number of invoices per month")
    custom_features: Optional[List[str]] = Field(None, description="Custom features requested")

class PricingCalculatorResponse(BaseModel):
    """Response from pricing calculation"""
    tier: str = Field(..., description="Subscription tier")
    billing_cycle: str = Field(..., description="Billing cycle")
    base_price_zar: int = Field(..., description="Base price in cents (ZAR)")
    discount_percent: int = Field(..., description="Discount percentage applied")
    overage_charges: Dict[str, Any] = Field(default={}, description="Overage charges")
    total_overage_zar: int = Field(default=0, description="Total overage charges in cents")
    total_price_zar: int = Field(..., description="Total price in cents (ZAR)")
    currency: str = Field(default="ZAR", description="Currency code")
    calculated_at: str = Field(..., description="Calculation timestamp")

class TrialOptionsResponse(BaseModel):
    """Available trial options for each tier"""
    standard_trial: int = Field(..., description="Standard trial period in days")
    extended_trial: int = Field(..., description="Extended trial period in days")
    enterprise_negotiation: int = Field(..., description="Enterprise negotiation trial period in days")
    max_custom_trial: int = Field(..., description="Maximum custom trial period in days")
    auto_convert: bool = Field(..., description="Whether trial auto-converts to paid")
    requires_approval: bool = Field(..., description="Whether trial requires approval")

class PricingTableResponse(BaseModel):
    """Complete pricing table response"""
    tiers: List[PricingResponse] = Field(..., description="All pricing tiers")
    feature_comparison: FeatureComparisonResponse = Field(..., description="Feature comparison")
    support_levels: List[SupportLevelResponse] = Field(..., description="Support levels")
    sla_comparison: SLAComparisonResponse = Field(..., description="SLA comparison")
    trial_options: Dict[str, TrialOptionsResponse] = Field(..., description="Trial options by tier")

class EnterpriseQuoteRequest(BaseModel):
    """Request for enterprise custom quote"""
    company_name: str = Field(..., description="Company name")
    contact_email: str = Field(..., description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    company_size: str = Field(..., description="Company size category")
    industry: str = Field(..., description="Industry")
    estimated_users: int = Field(..., description="Estimated number of users")
    estimated_invoices: int = Field(..., description="Estimated invoices per month")
    required_features: List[str] = Field(..., description="Required features")
    custom_integrations: Optional[List[str]] = Field(None, description="Custom integrations needed")
    compliance_requirements: Optional[List[str]] = Field(None, description="Compliance requirements")
    preferred_trial_period: Optional[int] = Field(None, description="Preferred trial period in days")
    additional_requirements: Optional[str] = Field(None, description="Additional requirements")

class EnterpriseQuoteResponse(BaseModel):
    """Response for enterprise custom quote"""
    quote_id: str = Field(..., description="Quote ID")
    company_name: str = Field(..., description="Company name")
    contact_email: str = Field(..., description="Contact email")
    estimated_monthly_price_zar: int = Field(..., description="Estimated monthly price in cents")
    estimated_annual_price_zar: int = Field(..., description="Estimated annual price in cents")
    recommended_tier: str = Field(..., description="Recommended tier")
    included_features: List[str] = Field(..., description="Included features")
    custom_additions: List[str] = Field(default=[], description="Custom additions")
    trial_period_days: int = Field(..., description="Recommended trial period")
    next_steps: List[str] = Field(..., description="Next steps for the customer")
    quote_valid_until: str = Field(..., description="Quote validity date")
    created_at: str = Field(..., description="Quote creation timestamp")








