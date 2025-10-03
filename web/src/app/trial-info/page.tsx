'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  Lock, 
  Clock, 
  CheckCircle, 
  ArrowRight, 
  Star,
  Users,
  Zap,
  Globe
} from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function TrialInfoPage() {
  const [isStartingTrial, setIsStartingTrial] = useState(false)
  const router = useRouter()

  const handleStartTrial = async () => {
    setIsStartingTrial(true)
    try {
      // Track trial start
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'trial_start', {
          event_category: 'conversion',
          event_label: 'trial_info_page'
        })
      }

      // Navigate to signup
      router.push('/auth/register?trial=true')
    } catch (error) {
      console.error('Error starting trial:', error)
    } finally {
      setIsStartingTrial(false)
    }
  }

  const features = [
    {
      icon: <Shield className="w-6 h-6 text-green-600" />,
      title: "No Credit Card Required",
      description: "Start your trial instantly without providing any payment information"
    },
    {
      icon: <Clock className="w-6 h-6 text-blue-600" />,
      title: "3 Days Full Access",
      description: "Experience all premium features with no limitations or restrictions"
    },
    {
      icon: <Lock className="w-6 h-6 text-purple-600" />,
      title: "Secure & Private",
      description: "Your data is encrypted and protected with enterprise-grade security"
    },
    {
      icon: <Zap className="w-6 h-6 text-yellow-600" />,
      title: "Instant Setup",
      description: "Get started in under 5 minutes with our guided onboarding process"
    }
  ]

  const benefits = [
    "Process unlimited invoices during trial",
    "Access to all AI-powered features",
    "Full ERP integration capabilities",
    "Priority customer support",
    "Export your data anytime",
    "Cancel with one click"
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">AI</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">AI ERP</h1>
            </div>
            <Button 
              variant="outline" 
              onClick={() => router.push('/')}
            >
              Back to Home
            </Button>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center mb-6">
            <Shield className="w-12 h-12 mr-4" />
            <h1 className="text-4xl font-bold">No Credit Card Required</h1>
          </div>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Start your free 3-day trial today and experience the full power of AI ERP 
            without any commitment or payment information required.
          </p>
          
          <Button
            onClick={handleStartTrial}
            disabled={isStartingTrial}
            size="lg"
            className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold transition-all duration-200 hover:scale-105 shadow-lg"
          >
            {isStartingTrial ? (
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                Starting Your Trial...
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Lock className="w-5 h-5" />
                Start Free Trial Now
                <ArrowRight className="w-5 h-5" />
              </div>
            )}
          </Button>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              What You Get During Your Trial
            </h2>
            <p className="text-lg text-gray-600">
              Full access to all features with no limitations
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="text-center p-6 hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex justify-center mb-4">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-gray-600 text-sm">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="bg-white py-16">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Trial Benefits
            </h2>
            <p className="text-lg text-gray-600">
              Everything you need to evaluate AI ERP for your business
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-xl font-semibold mb-6 text-gray-900">
                What's Included
              </h3>
              <ul className="space-y-4">
                {benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-900">
                Why No Credit Card?
              </h3>
              <div className="space-y-4 text-gray-700">
                <p>
                  We believe you should be able to fully evaluate our platform 
                  without any barriers or commitments.
                </p>
                <p>
                  This approach builds trust and allows you to make an informed 
                  decision based on actual experience, not just marketing promises.
                </p>
                <p>
                  You can cancel anytime during the trial with just one click, 
                  and we'll never ask for payment information.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Social Proof */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">
            Trusted by Thousands of Businesses
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">10,000+</div>
              <div className="text-gray-600">Active Users</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">99.9%</div>
              <div className="text-gray-600">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-600 mb-2">4.9/5</div>
              <div className="text-gray-600">Customer Rating</div>
            </div>
          </div>

          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600">
            <div className="flex items-center">
              <Star className="w-4 h-4 text-yellow-500 mr-1" />
              <span>Rated 4.9/5 by users</span>
            </div>
            <div className="flex items-center">
              <Shield className="w-4 h-4 text-green-500 mr-1" />
              <span>SOC 2 Type II Certified</span>
            </div>
            <div className="flex items-center">
              <Globe className="w-4 h-4 text-blue-500 mr-1" />
              <span>Available in 50+ countries</span>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Join thousands of businesses already using AI ERP to streamline their operations
          </p>
          
          <Button
            onClick={handleStartTrial}
            disabled={isStartingTrial}
            size="lg"
            className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold transition-all duration-200 hover:scale-105 shadow-lg"
          >
            {isStartingTrial ? (
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                Starting Your Trial...
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Lock className="w-5 h-5" />
                Start Your Free Trial
                <ArrowRight className="w-5 h-5" />
              </div>
            )}
          </Button>
          
          <p className="text-sm mt-6 opacity-75">
            No credit card required • 3-day free trial • Cancel anytime
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-900 text-white py-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <p className="text-gray-400">
            © 2024 AI ERP. All rights reserved. | 
            <a href="/privacy" className="hover:text-white ml-2">Privacy Policy</a> | 
            <a href="/terms" className="hover:text-white ml-2">Terms of Service</a>
          </p>
        </div>
      </div>
    </div>
  )
}











