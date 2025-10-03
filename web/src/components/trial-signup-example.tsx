'use client'

import { TrialSignupSection } from '@/components/trial-signup-section'

// Example: Add this to any page where you want the trial signup section
export function ExamplePageWithTrial() {
  return (
    <div className="min-h-screen">
      {/* Your existing page content */}
      <div className="max-w-6xl mx-auto px-4 py-20">
        <h1 className="text-4xl font-bold text-center mb-12">
          AI ERP Features
        </h1>
        
        {/* Your features content */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-4">AI Invoice Processing</h3>
            <p className="text-gray-600">
              Automatically extract data from any invoice format with 99%+ accuracy
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-4">Smart Approvals</h3>
            <p className="text-gray-600">
              Streamline approval workflows with intelligent routing and notifications
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-4">ERP Integration</h3>
            <p className="text-gray-600">
              Seamlessly connect with SAP, Oracle, QuickBooks, and more
            </p>
          </div>
        </div>
        
        {/* Trial Signup Section - This is what you add */}
        <TrialSignupSection />
      </div>
    </div>
  )
}

// Example: Add to homepage
export function HomePageWithTrial() {
  return (
    <div>
      {/* Hero section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            Transform Your Business with AI ERP
          </h1>
          <p className="text-xl mb-8">
            Automate invoice processing, streamline approvals, and integrate with your existing systems
          </p>
        </div>
      </section>
      
      {/* Features section */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
          {/* Your features content */}
        </div>
      </section>
      
      {/* Trial Signup Section */}
      <TrialSignupSection className="bg-gray-50" />
    </div>
  )
}





































