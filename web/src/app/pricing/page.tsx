'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import PricingPage from '@/components/pricing/PricingPage'
import ROICalculator from '@/components/pricing/ROICalculator'

export default function Pricing() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            Choose the perfect plan for your business. All plans include our core AI features 
            with no hidden fees. Save up to 60% compared to competitors.
          </p>
          <div className="flex justify-center items-center space-x-8 text-sm">
            <div className="flex items-center">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
              No setup fees
            </div>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
              Cancel anytime
            </div>
            <div className="flex items-center">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
              3-day free trial
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Tiers */}
      <PricingPage />

      {/* ROI Calculator */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Calculate Your Savings
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See how much you can save by switching to AI ERP SaaS compared to 
              traditional invoice processing methods.
            </p>
          </div>
          <ROICalculator />
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
          </div>
          
          <div className="max-w-3xl mx-auto">
            <div className="space-y-8">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  How does the free trial work?
                </h3>
                <p className="text-gray-600">
                  Start with a 3-day free trial for all plans. No credit card required. 
                  Full access to all features during the trial period.
                </p>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Can I change plans anytime?
                </h3>
                <p className="text-gray-600">
                  Yes! You can upgrade or downgrade your plan at any time. Changes take effect 
                  immediately, and we'll prorate any billing differences.
                </p>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  What happens if I exceed my plan limits?
                </h3>
                <p className="text-gray-600">
                  We'll notify you when you're approaching your limits. You can either upgrade 
                  your plan or purchase additional capacity as add-ons. We never cut off service 
                  without warning.
                </p>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Do you offer custom pricing for large enterprises?
                </h3>
                <p className="text-gray-600">
                  Yes! Our Unlimited plan is designed for large enterprises, but we also offer 
                  custom pricing for organizations with unique requirements. Contact our sales 
                  team for a personalized quote.
                </p>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  What payment methods do you accept?
                </h3>
                <p className="text-gray-600">
                  We accept all major credit cards (Visa, MasterCard, American Express), 
                  bank transfers, and ACH payments. Enterprise customers can also pay via 
                  purchase orders.
                </p>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Is there a setup fee or implementation cost?
                </h3>
                <p className="text-gray-600">
                  No setup fees! We provide free onboarding and implementation support for all plans. 
                  Our team will help you get started and ensure a smooth transition from your 
                  current system.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Join thousands of businesses already saving time and money with AI ERP SaaS.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              onClick={() => router.push('/auth/register?plan=professional&trial=true')}
              size="lg"
              className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-8 py-4 rounded-lg font-semibold transition-all duration-200 hover:scale-105 shadow-lg"
            >
              Start Free Trial
            </Button>
            <Button 
              onClick={() => router.push('/contact?inquiry=sales')}
              size="lg"
              className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-8 py-4 rounded-lg font-semibold transition-all duration-200 hover:scale-105 shadow-lg"
            >
              Contact Sales
            </Button>
          </div>
          <p className="text-sm mt-6 opacity-75">
            No credit card required • Setup in 5 minutes • 24/7 support
          </p>
        </div>
      </section>
    </div>
  )
}
