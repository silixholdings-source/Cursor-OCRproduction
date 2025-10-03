#!/usr/bin/env python3
"""
Premium Pricing Table Generator
Shows the exact pricing structure as specified
"""
import sys
sys.path.append('src')

from config.subscription_config import SubscriptionConfig, SubscriptionTier

def generate_pricing_table():
    """Generate the exact pricing table as specified"""
    config = SubscriptionConfig()
    
    print("Subscription Tiers & Pricing (Per Tenant)")
    print("=" * 80)
    print(f"{'Tier':<12} {'Monthly Price (ZAR)':<18} {'Yearly Price (ZAR, 15% off)':<30} {'Users Included':<15} {'Invoice Processing / Month':<25}")
    print("-" * 80)
    
    # Growth Plan
    growth_pricing = config.get_tier_pricing(SubscriptionTier.GROWTH)
    growth_limits = config.get_tier_limits(SubscriptionTier.GROWTH)
    growth_monthly = growth_pricing['monthly_price_zar'] / 100
    growth_annual = growth_pricing['annual_price_zar'] / 100
    growth_savings = growth_pricing['annual_savings_zar'] / 100
    
    print(f"{'Growth':<12} R{growth_monthly:,.0f} {'':<8} R{growth_annual:,.0f} (save R{growth_savings:,.0f}) {'':<6} {growth_limits.max_users} {'':<5} {growth_limits.max_invoices_per_month:,}")
    
    # Professional Plan
    prof_pricing = config.get_tier_pricing(SubscriptionTier.PROFESSIONAL)
    prof_limits = config.get_tier_limits(SubscriptionTier.PROFESSIONAL)
    prof_monthly = prof_pricing['monthly_price_zar'] / 100
    prof_annual = prof_pricing['annual_price_zar'] / 100
    prof_savings = prof_pricing['annual_savings_zar'] / 100
    
    print(f"{'Professional':<12} R{prof_monthly:,.0f} {'':<8} R{prof_annual:,.0f} (save R{prof_savings:,.0f}) {'':<6} {prof_limits.max_users} {'':<6} {prof_limits.max_invoices_per_month:,}")
    
    # Enterprise Plan
    ent_pricing = config.get_tier_pricing(SubscriptionTier.ENTERPRISE)
    ent_limits = config.get_tier_limits(SubscriptionTier.ENTERPRISE)
    ent_monthly = ent_pricing['monthly_price_zar'] / 100
    ent_annual = ent_pricing['annual_price_zar'] / 100
    ent_savings = ent_pricing['annual_savings_zar'] / 100
    
    print(f"{'Enterprise':<12} R{ent_monthly:,.0f} {'':<8} R{ent_annual:,.0f} (save R{ent_savings:,.0f}) {'':<6} Unlimited {'':<2} {ent_limits.max_invoices_per_month:,}+")
    
    print("\n" + "=" * 80)
    print("FEATURES BREAKDOWN")
    print("=" * 80)
    
    # Growth Features
    growth_features = config.get_tier_features(SubscriptionTier.GROWTH)
    print(f"\nGROWTH PLAN FEATURES:")
    print("• Full ERP connectors (GP, D365 BC, Sage, Xero, QuickBooks)")
    print("• CSV export")
    print("• Advanced OCR")
    print("• Email support")
    print("• Invoice processing")
    print("• Basic analytics")
    print("• Audit trails")
    print("• Mobile app")
    print("• Multi-language support")
    print("• Standard workflows")
    
    # Professional Features
    prof_features = config.get_tier_features(SubscriptionTier.PROFESSIONAL)
    print(f"\nPROFESSIONAL PLAN FEATURES:")
    print("All Growth features +")
    print("• API access")
    print("• Advanced analytics")
    print("• Role-based access")
    print("• Priority support")
    print("• Custom workflows")
    print("• Advanced security")
    print("• Backup & restore")
    
    # Enterprise Features
    ent_features = config.get_tier_features(SubscriptionTier.ENTERPRISE)
    print(f"\nENTERPRISE PLAN FEATURES:")
    print("All Professional features +")
    print("• Custom integrations")
    print("• SLA-backed uptime")
    print("• Dedicated support manager")
    print("• Private cloud option")
    print("• Unlimited ERP connectors")
    print("• Unlimited users")
    print("• Unlimited invoices")
    print("• Dedicated account manager")
    print("• Custom development")
    print("• White labeling")
    print("• SSO integration")
    print("• Compliance reporting")
    print("• Custom analytics")
    print("• Unlimited workflows")
    
    print("\n" + "=" * 80)
    print("SUPPORT & SLA LEVELS")
    print("=" * 80)
    
    print(f"\nGROWTH:")
    print("• Support: Email support")
    print("• SLA: 99.5% uptime guarantee")
    print("• Response time: 24 hours")
    print("• Resolution time: 72 hours")
    
    print(f"\nPROFESSIONAL:")
    print("• Support: Priority support")
    print("• SLA: 99.7% uptime guarantee")
    print("• Response time: 12 hours")
    print("• Resolution time: 48 hours")
    
    print(f"\nENTERPRISE:")
    print("• Support: Dedicated support manager")
    print("• SLA: 99.9% uptime guarantee")
    print("• Response time: 4 hours")
    print("• Resolution time: 24 hours")
    
    print("\n" + "=" * 80)
    print("TRIAL OPTIONS")
    print("=" * 80)
    
    print(f"\nGROWTH: 14-day standard trial")
    print(f"PROFESSIONAL: 21-day standard trial")
    print(f"ENTERPRISE: 30-day standard trial")
    print(f"\nExtended trials available for enterprise negotiations:")
    print(f"• Growth: Up to 30 days")
    print(f"• Professional: Up to 45 days")
    print(f"• Enterprise: Up to 60 days")
    
    print("\n" + "=" * 80)
    print("Premium pricing structure implemented successfully!")
    print("=" * 80)

if __name__ == "__main__":
    generate_pricing_table()
