'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { LinkButton } from '@/components/ui/link-button'
import { CTAButton } from '@/components/ui/cta-button'
import { Badge } from '@/components/ui/badge'
import { 
  ArrowRight, 
  CheckCircle, 
  Star, 
  Users, 
  Zap, 
  Shield,
  Smartphone,
  BarChart3,
  Clock,
  DollarSign
} from 'lucide-react'

export default function HomePage() {
  const router = useRouter()

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative container mx-auto px-4 py-24">
          <div className="max-w-4xl mx-auto text-center">
            <Badge variant="secondary" className="mb-6 bg-white/20 text-white border-white/30">
              <Star className="w-4 h-4 mr-1" />
              #1 AI-Powered Invoice Automation
            </Badge>
            
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
              Automate Invoice Processing with{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-400">
                AI Power
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl mb-8 text-blue-100 max-w-3xl mx-auto">
              Save 80% time and 60% costs with our AI-powered invoice automation. 
              Process invoices 10x faster than traditional methods.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <CTAButton href="/auth/register" backgroundType="blue" className="hover:scale-105 transition-all duration-200 shadow-lg">
                Start Free Trial
                <ArrowRight className="w-5 h-5 ml-2" />
              </CTAButton>
              <CTAButton href="/demo" backgroundType="blue" className="hover:scale-105 transition-all duration-200">
                Watch Demo
              </CTAButton>
              <CTAButton href="/test" backgroundType="blue" className="hover:scale-105 transition-all duration-200">
                Test API
              </CTAButton>
            </div>
            
            <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-blue-200">
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-2" />
                No credit card required
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-2" />
                3-day free trial
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-2" />
                Setup in 5 minutes
              </div>
            </div>
          </div>
        </div>
        
        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-white/10 rounded-full animate-pulse"></div>
        <div className="absolute top-40 right-20 w-16 h-16 bg-yellow-400/20 rounded-full animate-bounce"></div>
        <div className="absolute bottom-20 left-20 w-12 h-12 bg-white/10 rounded-full animate-pulse"></div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">10,000+</div>
              <div className="text-gray-600">Active Users</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">$50M+</div>
              <div className="text-gray-600">Invoices Processed</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">95%</div>
              <div className="text-gray-600">Accuracy Rate</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">80%</div>
              <div className="text-gray-600">Time Saved</div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Benefits */}
      <section id="competitive-advantages" className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why Choose AI ERP SaaS?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We're not just another invoice tool. We're the future of AP automation, 
              built with cutting-edge AI and designed for modern businesses.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
                <DollarSign className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Up to 60% Cost Savings</h3>
              <p className="text-gray-600 mb-4">
                Our aggressive pricing undercuts major competitors while providing superior features. 
                Save thousands annually compared to Bill.com, Tipalti, and Stampli.
              </p>
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                Save $1,000s annually
              </Badge>
            </div>
            
            <div className="bg-white rounded-lg p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-purple-100 rounded-lg flex items-center justify-center mb-6">
                <Zap className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">AI-Powered Automation</h3>
              <p className="text-gray-600 mb-4">
                Advanced OCR and machine learning that learns from your data to improve accuracy over time. 
                Process invoices with 95%+ accuracy.
              </p>
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                95%+ accuracy rate
              </Badge>
            </div>
            
            <div className="bg-white rounded-lg p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center mb-6">
                <Clock className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Lightning Fast Setup</h3>
              <p className="text-gray-600 mb-4">
                Get up and running in minutes, not weeks. Our intuitive interface requires minimal training 
                and works with your existing systems.
              </p>
              <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                5-minute setup
              </Badge>
            </div>
            
            <div className="bg-white rounded-lg p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-red-100 rounded-lg flex items-center justify-center mb-6">
                <Shield className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Enterprise Security</h3>
              <p className="text-gray-600 mb-4">
                SOC 2 compliant with end-to-end encryption, audit trails, and advanced fraud detection. 
                Your data is protected at the highest level.
              </p>
              <Badge variant="secondary" className="bg-red-100 text-red-800">
                SOC 2 Type II
              </Badge>
            </div>
            
            <div className="bg-white rounded-lg p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-indigo-100 rounded-lg flex items-center justify-center mb-6">
                <Smartphone className="w-8 h-8 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Mobile-First Design</h3>
              <p className="text-gray-600 mb-4">
                Native mobile apps for iOS and Android with offline capabilities, camera integration, 
                and push notifications for instant approvals.
              </p>
              <Badge variant="secondary" className="bg-indigo-100 text-indigo-800">
                Offline approvals
              </Badge>
            </div>
            
            <div className="bg-white rounded-lg p-8 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-orange-100 rounded-lg flex items-center justify-center mb-6">
                <BarChart3 className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Advanced Analytics</h3>
              <p className="text-gray-600 mb-4">
                Real-time dashboards, predictive analytics, and comprehensive reporting to help you 
                make better business decisions.
              </p>
              <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                Real-time insights
              </Badge>
            </div>
          </div>
        </div>
      </section>

      {/* Competitive Advantages */}
      <section className="py-20 bg-white hover:bg-gray-50 transition-colors cursor-pointer" onClick={() => router.push('/#competitive-advantages')}>
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Competitive Advantages
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We outperform major competitors in every key metric.
            </p>
          </div>
        </div>
      </section>

      {/* Advanced Features */}
      <section className="py-20 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer" onClick={() => router.push('/features')}>
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Advanced Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Cutting-edge AI technology for enterprise automation.
            </p>
          </div>
        </div>
      </section>

      {/* ROI Calculator */}
      <section className="py-20 bg-white hover:bg-gray-50 transition-colors cursor-pointer" onClick={() => router.push('/roi-calculator')}>
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              ROI Calculator
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Calculate your potential savings with our platform.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer" onClick={() => router.push('/pricing')}>
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Pricing Plans
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Choose the plan that fits your business needs.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Transform Your Invoice Processing?
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Join thousands of businesses already saving time and money with AI ERP SaaS. 
            Start your free trial today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <CTAButton href="/auth/register" backgroundType="blue" className="hover:scale-105 transition-all duration-200 shadow-lg">
              Start Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </CTAButton>
            <CTAButton href="/contact" backgroundType="blue" className="hover:scale-105 transition-all duration-200 shadow-lg">
              Schedule Demo
            </CTAButton>
          </div>
          <p className="text-sm mt-6 opacity-75">
            No credit card required • 3-day free trial • Setup in 5 minutes
          </p>
        </div>
      </section>
    </div>
  )
}