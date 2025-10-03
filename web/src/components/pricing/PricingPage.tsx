'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { EnhancedButton } from '@/components/ui/enhanced-button'
import { Badge } from '@/components/ui/badge'
import { useAsyncAction } from '@/hooks/use-async-action'
import { useToast } from '@/lib/toast-notifications'
import { Check, X, Star, Zap, Shield, Users, Database, FileText, Smartphone, Headphones, Code, Palette, ArrowRight } from 'lucide-react'

interface PricingTier {
  name: string
  monthly_price: number
  yearly_price: number
  features: string[]
  max_users: number
  max_storage_gb: number
  max_invoices_per_month: number
  trial_days: number
  popular: boolean
  savings_percentage: number
}

interface AddonPricing {
  name: string
  price_per_user_monthly?: number
  price_per_user_yearly?: number
  price_per_gb_monthly?: number
  price_per_gb_yearly?: number
  price_per_invoice?: number
  monthly?: number
  yearly?: number
  setup_fee?: number
  description: string
  savings_yearly?: number
  billing?: string
}

const pricingTiers: PricingTier[] = [
  {
    name: "Starter",
    monthly_price: 19,
    yearly_price: 190,
    features: [
      "Up to 3 users",
      "5GB storage",
      "50 invoices/month",
      "AI-powered OCR",
      "Email support",
      "Mobile app access",
      "Basic analytics",
      "3-day free trial"
    ],
    max_users: 3,
    max_storage_gb: 5,
    max_invoices_per_month: 50,
    trial_days: 3,
    popular: false,
    savings_percentage: 17
  },
  {
    name: "Professional",
    monthly_price: 49,
    yearly_price: 490,
    features: [
      "Up to 15 users",
      "50GB storage",
      "500 invoices/month",
      "AI-powered OCR",
      "Priority support",
      "API access",
      "Advanced analytics",
      "Mobile app access",
      "Fraud detection",
      "Three-way matching",
      "3-day free trial"
    ],
    max_users: 15,
    max_storage_gb: 50,
    max_invoices_per_month: 500,
    trial_days: 3,
    popular: true,
    savings_percentage: 17
  },
  {
    name: "Business",
    monthly_price: 99,
    yearly_price: 990,
    features: [
      "Up to 50 users",
      "200GB storage",
      "2,000 invoices/month",
      "AI-powered OCR",
      "Priority support",
      "API access",
      "Advanced analytics",
      "Mobile app access",
      "Fraud detection",
      "Three-way matching",
      "SSO integration",
      "Custom fields",
      "3-day free trial"
    ],
    max_users: 50,
    max_storage_gb: 200,
    max_invoices_per_month: 2000,
    trial_days: 3,
    popular: false,
    savings_percentage: 17
  },
  {
    name: "Enterprise",
    monthly_price: 199,
    yearly_price: 1990,
    features: [
      "Up to 200 users",
      "1TB storage",
      "10,000 invoices/month",
      "AI-powered OCR",
      "Custom workflows",
      "Dedicated support",
      "API access",
      "Advanced analytics",
      "Mobile app access",
      "Fraud detection",
      "Three-way matching",
      "SSO integration",
      "Custom integrations",
      "White labeling",
      "Dedicated account manager",
      "3-day free trial"
    ],
    max_users: 200,
    max_storage_gb: 1000,
    max_invoices_per_month: 10000,
    trial_days: 3,
    popular: false,
    savings_percentage: 17
  },
  {
    name: "Unlimited",
    monthly_price: 299,
    yearly_price: 2990,
    features: [
      "Unlimited users",
      "Unlimited storage",
      "Unlimited invoices",
      "AI-powered OCR",
      "Custom workflows",
      "Dedicated support",
      "API access",
      "Advanced analytics",
      "Mobile app access",
      "Fraud detection",
      "Three-way matching",
      "SSO integration",
      "Custom integrations",
      "White labeling",
      "Dedicated account manager",
      "On-premise deployment",
      "3-day free trial"
    ],
    max_users: -1,
    max_storage_gb: -1,
    max_invoices_per_month: -1,
    trial_days: 3,
    popular: false,
    savings_percentage: 17
  }
]

const addonPricing: AddonPricing[] = [
  {
    name: "Additional Users",
    price_per_user_monthly: 5,
    price_per_user_yearly: 50,
    description: "Add more users to your plan",
    savings_yearly: 17
  },
  {
    name: "Additional Storage",
    price_per_gb_monthly: 0.5,
    price_per_gb_yearly: 5,
    description: "Add more storage space",
    savings_yearly: 17
  },
  {
    name: "Additional Invoices",
    price_per_invoice: 0.1,
    description: "Pay per invoice over your monthly limit",
    billing: "per_invoice"
  },
  {
    name: "Premium Support",
    monthly: 29,
    yearly: 290,
    description: "24/7 phone support, dedicated account manager",
    savings_yearly: 17
  },
  {
    name: "Custom Integrations",
    setup_fee: 500,
    monthly: 99,
    description: "Custom ERP integrations and API development",
    savings_yearly: 17
  },
  {
    name: "White Labeling",
    setup_fee: 1000,
    monthly: 199,
    description: "Rebrand the platform with your company's branding",
    savings_yearly: 17
  }
]

const competitorComparison = {
  our_pricing: {
    starter: { monthly: 19, yearly: 190 },
    professional: { monthly: 49, yearly: 490 },
    business: { monthly: 99, yearly: 990 },
    enterprise: { monthly: 199, yearly: 1990 }
  },
  competitors: {
    bill_com: {
      name: "Bill.com",
      starter: { monthly: 39, yearly: 390 },
      professional: { monthly: 99, yearly: 990 },
      business: { monthly: 199, yearly: 1990 },
      enterprise: { monthly: 399, yearly: 3990 }
    },
    tipalti: {
      name: "Tipalti",
      starter: { monthly: 45, yearly: 450 },
      professional: { monthly: 120, yearly: 1200 },
      business: { monthly: 250, yearly: 2500 },
      enterprise: { monthly: 500, yearly: 5000 }
    },
    stampli: {
      name: "Stampli",
      starter: { monthly: 35, yearly: 350 },
      professional: { monthly: 89, yearly: 890 },
      business: { monthly: 179, yearly: 1790 },
      enterprise: { monthly: 350, yearly: 3500 }
    }
  },
  savings: {
    vs_bill_com: "Up to 50% savings",
    vs_tipalti: "Up to 60% savings",
    vs_stampli: "Up to 43% savings"
  }
}

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('yearly')
  const [selectedTier, setSelectedTier] = useState<string>('professional')
  const { success } = useToast()
  
  const startTrialAction = useAsyncAction(
    async (tierName: string) => {
      // Store the selected tier for the trial
      setSelectedTier(tierName.toLowerCase())
      
      // Show success message
      success(
        'Trial Started!', 
        `Starting your 3-day free trial for ${tierName} plan`,
        {
          label: 'Continue to Registration',
          onClick: () => {
            const planParam = encodeURIComponent(tierName.toLowerCase())
            window.location.href = `/auth/register?plan=${planParam}&trial=true`
          }
        }
      )
      
      // Small delay for better UX
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Redirect to registration
      const planParam = encodeURIComponent(tierName.toLowerCase())
      window.location.href = `/auth/register?plan=${planParam}&trial=true`
    },
    {
      loadingMessage: 'Starting trial...',
      successMessage: 'Trial started successfully!'
    }
  )

  const getPrice = (tier: PricingTier) => {
    return billingCycle === 'yearly' ? tier.yearly_price : tier.monthly_price
  }

  const getSavings = (tier: PricingTier) => {
    if (billingCycle === 'yearly') {
      const monthlyEquivalent = tier.monthly_price * 12
      return monthlyEquivalent - tier.yearly_price
    }
    return 0
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Choose the perfect plan for your business. No hidden fees, no surprises.
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <span className={`text-lg ${billingCycle === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              aria-label={`Switch to ${billingCycle === 'monthly' ? 'yearly' : 'monthly'} billing`}
              title={`Switch to ${billingCycle === 'monthly' ? 'yearly' : 'monthly'} billing`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-lg ${billingCycle === 'yearly' ? 'text-gray-900' : 'text-gray-500'}`}>
              Yearly
            </span>
            {billingCycle === 'yearly' && (
              <Badge variant="secondary" className="ml-2 bg-green-100 text-green-800">
                Save 17%
              </Badge>
            )}
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-16">
          {pricingTiers.map((tier) => (
            <Card 
              key={tier.name}
              className={`relative ${
                tier.popular 
                  ? 'border-blue-500 shadow-lg scale-105' 
                  : 'border-gray-200 hover:shadow-lg transition-shadow'
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-blue-500 text-white px-4 py-1">
                    <Star className="w-3 h-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}
              
              <CardHeader className="text-center pb-4">
                <CardTitle className="text-xl font-semibold">{tier.name}</CardTitle>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-gray-900">
                    ${getPrice(tier)}
                  </span>
                  <span className="text-gray-600 ml-1">
                    /{billingCycle === 'yearly' ? 'year' : 'month'}
                  </span>
                </div>
                {billingCycle === 'yearly' && getSavings(tier) > 0 && (
                  <p className="text-sm text-green-600 font-medium">
                    Save ${getSavings(tier)}/year
                  </p>
                )}
              </CardHeader>
              
              <CardContent className="pt-0">
                <div className="space-y-3 mb-6">
                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="w-4 h-4 mr-2" />
                    {tier.max_users === -1 ? 'Unlimited users' : `Up to ${tier.max_users} users`}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <Database className="w-4 h-4 mr-2" />
                    {tier.max_storage_gb === -1 ? 'Unlimited storage' : `${tier.max_storage_gb}GB storage`}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <FileText className="w-4 h-4 mr-2" />
                    {tier.max_invoices_per_month === -1 ? 'Unlimited invoices' : `${tier.max_invoices_per_month} invoices/month`}
                  </div>
                </div>
                
                <EnhancedButton 
                  className="w-full"
                  variant={tier.popular ? 'default' : 'secondary'}
                  onClick={() => startTrialAction.execute(tier.name)}
                  loading={startTrialAction.isLoading && selectedTier === tier.name.toLowerCase()}
                  loadingText="Starting trial..."
                  success={startTrialAction.success && selectedTier === tier.name.toLowerCase()}
                  successText="Trial started!"
                  icon={<ArrowRight className="h-4 w-4" />}
                  iconPosition="right"
                  aria-label={`Start ${tier.trial_days}-day free trial for ${tier.name} plan`}
                >
                  Start {tier.trial_days}-day free trial
                </EnhancedButton>
                
                <p className="text-xs text-gray-500 text-center mt-2">
                  No credit card required
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Features Comparison */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            Compare Features
          </h2>
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Features</th>
                    {pricingTiers.map((tier) => (
                      <th key={tier.name} className="px-6 py-4 text-center text-sm font-medium text-gray-900">
                        {tier.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {[
                    { name: 'AI-powered OCR', icon: Zap },
                    { name: 'Mobile app access', icon: Smartphone },
                    { name: 'Fraud detection', icon: Shield },
                    { name: 'Three-way matching', icon: FileText },
                    { name: 'API access', icon: Code },
                    { name: 'SSO integration', icon: Users },
                    { name: 'White labeling', icon: Palette },
                    { name: 'Dedicated support', icon: Headphones }
                  ].map((feature) => (
                    <tr key={feature.name}>
                      <td className="px-6 py-4 text-sm text-gray-900 flex items-center">
                        <feature.icon className="w-4 h-4 mr-2" />
                        {feature.name}
                      </td>
                      {pricingTiers.map((tier) => (
                        <td key={tier.name} className="px-6 py-4 text-center">
                          {tier.features.some(f => f.toLowerCase().includes(feature.name.toLowerCase())) ? (
                            <Check className="w-5 h-5 text-green-500 mx-auto" />
                          ) : (
                            <X className="w-5 h-5 text-gray-300 mx-auto" />
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Competitor Comparison */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            How We Compare
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">AI ERP SaaS</h3>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-blue-600">$19</div>
                <div className="text-sm text-gray-600">Starter plan</div>
                <div className="text-2xl font-bold text-blue-600">$49</div>
                <div className="text-sm text-gray-600">Professional plan</div>
              </div>
            </div>
            
            {Object.values(competitorComparison.competitors).map((competitor) => (
              <div key={competitor.name} className="bg-white rounded-lg shadow-lg p-6 text-center">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{competitor.name}</h3>
                <div className="space-y-2">
                  <div className="text-2xl font-bold text-gray-600">${competitor.starter.monthly}</div>
                  <div className="text-sm text-gray-600">Starter plan</div>
                  <div className="text-2xl font-bold text-gray-600">${competitor.professional.monthly}</div>
                  <div className="text-sm text-gray-600">Professional plan</div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-8">
            <div className="inline-flex items-center space-x-8">
              <Badge variant="secondary" className="bg-green-100 text-green-800 text-lg px-4 py-2">
                {competitorComparison.savings.vs_bill_com}
              </Badge>
              <Badge variant="secondary" className="bg-green-100 text-green-800 text-lg px-4 py-2">
                {competitorComparison.savings.vs_tipalti}
              </Badge>
              <Badge variant="secondary" className="bg-green-100 text-green-800 text-lg px-4 py-2">
                {competitorComparison.savings.vs_stampli}
              </Badge>
            </div>
          </div>
        </div>

        {/* Add-on Pricing */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            Add-on Services
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {addonPricing.map((addon) => (
              <Card key={addon.name} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-lg">{addon.name}</CardTitle>
                  <p className="text-sm text-gray-600">{addon.description}</p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {addon.price_per_user_monthly && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Per user/month:</span>
                        <span className="font-semibold">${addon.price_per_user_monthly}</span>
                      </div>
                    )}
                    {addon.price_per_gb_monthly && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Per GB/month:</span>
                        <span className="font-semibold">${addon.price_per_gb_monthly}</span>
                      </div>
                    )}
                    {addon.price_per_invoice && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Per invoice:</span>
                        <span className="font-semibold">${addon.price_per_invoice}</span>
                      </div>
                    )}
                    {addon.monthly && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Monthly:</span>
                        <span className="font-semibold">${addon.monthly}</span>
                      </div>
                    )}
                    {addon.setup_fee && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Setup fee:</span>
                        <span className="font-semibold">${addon.setup_fee}</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-12 text-white">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Join thousands of businesses already using AI ERP SaaS
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100 transition-all duration-200 hover:scale-105 shadow-lg">
              Start Free Trial
            </Button>
            <Button size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100 transition-all duration-200 hover:scale-105 shadow-lg">
              Contact Sales
            </Button>
          </div>
          <p className="text-sm mt-6 opacity-75">
            No credit card required • Setup in 5 minutes • 24/7 support
          </p>
        </div>
      </div>
    </div>
  )
}
