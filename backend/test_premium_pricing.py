#!/usr/bin/env python3
"""
Test script for premium pricing configuration
"""
import sys
sys.path.append('src')

from config.subscription_config import SubscriptionConfig, SubscriptionTier

def test_premium_pricing():
    """Test the premium pricing configuration"""
    config = SubscriptionConfig()
    
    print("Premium Pricing Model (South Africa, Monthly)")
    print("=" * 60)
    
    print("\nPricing Tiers:")
    for tier in [SubscriptionTier.GROWTH, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
        pricing = config.get_tier_pricing(tier)
        limits = config.get_tier_limits(tier)
        features = config.get_tier_features(tier)
        
        monthly_price = pricing['monthly_price_zar'] / 100
        annual_price = pricing['annual_price_zar'] / 100
        annual_savings = pricing['annual_savings_zar'] / 100
        discount = pricing['annual_discount_percent']
        
        print(f"\n{tier.value.upper()} Plan:")
        print(f"  Price: R{monthly_price:,.0f}/month")
        print(f"  Annual: R{annual_price:,.0f}/year (save R{annual_savings:,.0f})")
        print(f"  Users: {limits.max_users}")
        print(f"  Invoices/month: {limits.max_invoices_per_month:,}")
        print(f"  Storage: {limits.max_storage_gb}GB")
        print(f"  ERP Connectors: {limits.max_erp_connectors}")
        print(f"  Support: {features.support_level}")
        print(f"  SLA: {features.sla_uptime}% uptime")
        print(f"  Response: {features.response_time_hours}h")
    
    print("\nFeature Comparison:")
    feature_comparison = config.get_feature_comparison()
    all_features = set()
    for features in feature_comparison.values():
        all_features.update(features)
    
    print(f"Total features available: {len(all_features)}")
    print("Key features by tier:")
    for tier, features in feature_comparison.items():
        print(f"  {tier.title()}: {len(features)} features")
    
    print("\nTrial Options:")
    for tier in [SubscriptionTier.GROWTH, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
        standard = config.get_trial_period(tier, "standard")
        extended = config.get_trial_period(tier, "extended")
        enterprise = config.get_trial_period(tier, "enterprise_negotiation")
        print(f"  {tier.value.title()}: {standard}d standard, {extended}d extended, {enterprise}d enterprise")
    
    print("\nPremium pricing configuration loaded successfully!")

if __name__ == "__main__":
    test_premium_pricing()
