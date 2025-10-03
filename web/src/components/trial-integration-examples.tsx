'use client'

import { TrialSignupSection, TrialSignupCompact, TrialSignupHero } from '@/components/trial-signup-section'
import { useRouter } from 'next/navigation'

// Example 1: Standard section for features page
export function FeaturesPageWithTrial() {
  const router = useRouter()

  const handleTrialStart = () => {
    // Custom trial start logic
    console.log('Starting trial from features page')
    router.push('/auth/register?trial=true&source=features')
  }

  return (
    <div className="py-20">
      {/* Your features content */}
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-center mb-12">Our Features</h1>
        
        {/* Features grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {/* Feature cards */}
        </div>
        
        {/* Trial signup section */}
        <TrialSignupSection onTrialStart={handleTrialStart} />
      </div>
    </div>
  )
}

// Example 2: Hero section with trial signup
export function HomePageHero() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="max-w-6xl mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Transform Your Business with AI ERP
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Automate invoice processing, streamline approvals, and integrate with your existing ERP systems 
            using our intelligent AI-powered platform.
          </p>
        </div>
        
        {/* Trial signup hero version */}
        <TrialSignupHero />
      </div>
    </div>
  )
}

// Example 3: Pricing page with trial signup
export function PricingPageWithTrial() {
  return (
    <div className="py-20">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
          <p className="text-xl text-gray-600">
            Start with a free trial and upgrade when you're ready
          </p>
        </div>
        
        {/* Pricing cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {/* Pricing cards content */}
        </div>
        
        {/* Trial signup section */}
        <TrialSignupSection className="bg-gray-50 rounded-2xl" />
      </div>
    </div>
  )
}

// Example 4: Compact version for smaller sections
export function SidebarTrialSection() {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Try AI ERP Free</h3>
      <p className="text-gray-600 mb-4">
        See how our platform can transform your business operations.
      </p>
      <TrialSignupCompact />
    </div>
  )
}

// Example 5: Modal integration
export function TrialModalExample() {
  const [showModal, setShowModal] = useState(false)

  return (
    <div>
      <button 
        onClick={() => setShowModal(true)}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
      >
        Start Free Trial
      </button>
      
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md mx-4">
            <h2 className="text-2xl font-bold mb-4">Start Your Free Trial</h2>
            <TrialSignupCompact onTrialStart={() => setShowModal(false)} />
            <button 
              onClick={() => setShowModal(false)}
              className="mt-4 text-gray-500 hover:text-gray-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Example 6: Different styling variants
export function StyledTrialSections() {
  return (
    <div className="space-y-16">
      {/* Default styling */}
      <TrialSignupSection />
      
      {/* Custom background */}
      <TrialSignupSection className="bg-blue-50 rounded-2xl" />
      
      {/* Custom text color */}
      <TrialSignupSection className="text-white bg-gray-900 rounded-2xl" />
      
      {/* Compact version */}
      <TrialSignupCompact />
    </div>
  )
}





































