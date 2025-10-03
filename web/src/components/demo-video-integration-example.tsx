'use client'

import { DemoVideoButton, DemoVideoIconButton } from '@/components/demo-video-button'
import { Play, Video, ArrowRight } from 'lucide-react'

// Example 1: Hero Section Integration
export function HeroSectionWithDemo() {
  return (
    <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-5xl font-bold mb-6">
          Transform Your Business with AI ERP
        </h1>
        <p className="text-xl mb-8 max-w-2xl mx-auto">
          See how our intelligent platform can revolutionize your invoice processing 
          and approval workflows in just 3 minutes.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <DemoVideoButton 
            size="lg"
            className="bg-white text-blue-600 hover:bg-gray-100 transition-all duration-200 hover:scale-105 shadow-lg"
          >
            <Play className="h-5 w-5" />
            Watch Demo Video
          </DemoVideoButton>
          <DemoVideoButton 
            variant="outline"
            size="lg"
            className="border-white text-white hover:bg-white hover:text-blue-600"
          >
            Try Interactive Demo
            <ArrowRight className="h-5 w-5" />
          </DemoVideoButton>
        </div>
      </div>
    </section>
  )
}

// Example 2: Features Section Integration
export function FeaturesSectionWithDemo() {
  const features = [
    {
      title: "AI-Powered Invoice Processing",
      description: "Automatically extract data from any invoice format with 99%+ accuracy",
      demo: <DemoVideoButton variant="ghost" size="sm">See in Action</DemoVideoButton>
    },
    {
      title: "Smart Approval Workflows",
      description: "Streamline approvals with intelligent routing and notifications",
      demo: <DemoVideoButton variant="ghost" size="sm">Watch Demo</DemoVideoButton>
    },
    {
      title: "ERP Integration",
      description: "Seamlessly connect with SAP, Oracle, QuickBooks, and more",
      demo: <DemoVideoButton variant="ghost" size="sm">View Integration</DemoVideoButton>
    }
  ]

  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Discover how our AI ERP platform can transform your business operations
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white rounded-lg p-8 shadow-lg">
              <h3 className="text-2xl font-semibold mb-4">{feature.title}</h3>
              <p className="text-gray-600 mb-6">{feature.description}</p>
              {feature.demo}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// Example 3: Navigation Integration
export function NavigationWithDemo() {
  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-blue-600">AI ERP</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <a href="/features" className="text-gray-600 hover:text-gray-900">Features</a>
            <a href="/pricing" className="text-gray-600 hover:text-gray-900">Pricing</a>
            <a href="/contact" className="text-gray-600 hover:text-gray-900">Contact</a>
            
            {/* Demo Video Icon Button */}
            <DemoVideoIconButton className="text-blue-600 hover:text-blue-700" />
            
            <DemoVideoButton variant="outline" size="sm">
              Watch Demo
            </DemoVideoButton>
          </div>
        </div>
      </div>
    </nav>
  )
}

// Example 4: Pricing Page Integration
export function PricingCardWithDemo({ 
  title, 
  price, 
  features, 
  isPopular = false 
}: {
  title: string
  price: string
  features: string[]
  isPopular?: boolean
}) {
  return (
    <div className={`bg-white rounded-lg p-8 shadow-lg ${isPopular ? 'ring-2 ring-blue-600' : ''}`}>
      {isPopular && (
        <div className="bg-blue-600 text-white text-sm font-semibold px-3 py-1 rounded-full inline-block mb-4">
          Most Popular
        </div>
      )}
      
      <h3 className="text-2xl font-bold mb-2">{title}</h3>
      <div className="text-4xl font-bold mb-6">{price}</div>
      
      <ul className="space-y-3 mb-8">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
            {feature}
          </li>
        ))}
      </ul>
      
      <div className="space-y-3">
        <DemoVideoButton 
          variant={isPopular ? "default" : "outline"} 
          className="w-full"
        >
          <Play className="h-4 w-4" />
          Watch Demo
        </DemoVideoButton>
        
        <button className={`w-full py-2 px-4 rounded-lg font-semibold ${
          isPopular 
            ? 'bg-blue-600 text-white hover:bg-blue-700' 
            : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
        }`}>
          Start Free Trial
        </button>
      </div>
    </div>
  )
}

// Example 5: Footer Integration
export function FooterWithDemo() {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">AI ERP</h3>
            <p className="text-gray-400 mb-4">
              Transform your business with intelligent automation
            </p>
            <DemoVideoButton variant="outline" size="sm" className="border-gray-600 text-gray-300 hover:bg-gray-800">
              <Video className="h-4 w-4" />
              Watch Demo
            </DemoVideoButton>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/features" className="hover:text-white">Features</a></li>
              <li><a href="/demo" className="hover:text-white">Demo</a></li>
              <li><a href="/pricing" className="hover:text-white">Pricing</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/about" className="hover:text-white">About</a></li>
              <li><a href="/contact" className="hover:text-white">Contact</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/docs" className="hover:text-white">Documentation</a></li>
              <li><a href="/support" className="hover:text-white">Support</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2024 AI ERP. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}











