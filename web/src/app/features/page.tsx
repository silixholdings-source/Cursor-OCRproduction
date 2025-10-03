'use client'

import React from 'react'
import AdvancedFeatures from '@/components/features/AdvancedFeatures'
import CompetitiveAdvantages from '@/components/landing/CompetitiveAdvantages'
import { LinkButton } from '@/components/ui/link-button'
import { CTAButton } from '@/components/ui/cta-button'

export default function Features() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            Powerful Features for Modern Businesses
          </h1>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            Everything you need to automate invoice processing, reduce costs, 
            and scale your business with AI-powered technology.
          </p>
        </div>
      </section>

      {/* Advanced Features */}
      <AdvancedFeatures />

      {/* Competitive Advantages */}
      <CompetitiveAdvantages />

      {/* Integration Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Seamless Integrations
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Connect with your existing tools and workflows. No disruption to your current processes.
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8">
            {[
              'SAP', 'Oracle', 'NetSuite', 'QuickBooks', 'Xero', 'Microsoft Dynamics',
              'Salesforce', 'HubSpot', 'Slack', 'Microsoft Teams', 'Google Workspace', 'Office 365'
            ].map((integration) => (
              <div key={integration} className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow text-center">
                <div className="w-12 h-12 bg-gray-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
                  <span className="text-gray-600 font-semibold text-sm">
                    {integration.substring(0, 2)}
                  </span>
                </div>
                <div className="text-sm font-medium text-gray-900">{integration}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Enterprise-Grade Security
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Your data is protected with industry-leading security measures and compliance standards.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">🔒</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">SOC 2 Type II</h3>
              <p className="text-gray-600">
                Independently audited security controls and processes
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">🛡️</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">End-to-End Encryption</h3>
              <p className="text-gray-600">
                All data encrypted in transit and at rest
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">✅</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">GDPR Compliant</h3>
              <p className="text-gray-600">
                Full compliance with data protection regulations
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">🔍</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Audit Trails</h3>
              <p className="text-gray-600">
                Complete audit logs for all user actions
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">🚨</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Fraud Detection</h3>
              <p className="text-gray-600">
                AI-powered fraud detection and prevention
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">🔐</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">SSO Integration</h3>
              <p className="text-gray-600">
                Single sign-on with your existing identity provider
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Experience These Features?
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Start your free trial today and see how AI ERP SaaS can transform your business.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <CTAButton href="/auth/register" backgroundType="white">
              Start Free Trial
            </CTAButton>
            <CTAButton href="/contact" backgroundType="white">
              Schedule Demo
            </CTAButton>
          </div>
        </div>
      </section>
    </div>
  )
}
