#!/usr/bin/env python3
"""
Test Enterprise trial period update
"""
import sys
sys.path.append('src')

from config.subscription_config import SubscriptionConfig, SubscriptionTier

def test_enterprise_trial():
    """Test that Enterprise trial maximum is 60 days"""
    config = SubscriptionConfig()
    
    print("Testing Enterprise Trial Period Update")
    print("=" * 50)
    
    # Get Enterprise trial periods
    enterprise_periods = config.TRIAL_PERIODS[SubscriptionTier.ENTERPRISE]
    
    print("Enterprise trial periods:")
    print(f"  Standard: {enterprise_periods['standard_days']} days")
    print(f"  Extended: {enterprise_periods['extended_days']} days")
    print(f"  Enterprise negotiation: {enterprise_periods['enterprise_negotiation']} days")
    
    # Verify the maximum is 60 days
    max_trial = enterprise_periods['enterprise_negotiation']
    if max_trial == 60:
        print(f"\nSUCCESS: Enterprise trial maximum is correctly set to {max_trial} days")
    else:
        print(f"\nERROR: Enterprise trial maximum is {max_trial} days, expected 60 days")
    
    # Test all tiers
    print(f"\nAll tier trial periods:")
    for tier in [SubscriptionTier.GROWTH, SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
        periods = config.TRIAL_PERIODS[tier]
        max_period = periods['enterprise_negotiation']
        print(f"  {tier.value.title()}: {max_period} days maximum")
    
    print(f"\nTrial period validation:")
    print(f"  Valid trial days: 14, 21, 30, 45, 60")
    print(f"  Maximum custom trial: 60 days")

if __name__ == "__main__":
    test_enterprise_trial()
