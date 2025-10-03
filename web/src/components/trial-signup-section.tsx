'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Lock, Shield, ArrowRight } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface TrialSignupSectionProps {
  className?: string
  onTrialStart?: () => void
}

export function TrialSignupSection({ className = '', onTrialStart }: TrialSignupSectionProps) {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleFreeTrial = async () => {
    setIsLoading(true)
    try {
      // Track trial signup event
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'trial_signup', {
          event_category: 'conversion',
          event_label: 'free_trial_button'
        })
      }

      // Call custom handler if provided
      if (onTrialStart) {
        onTrialStart()
      } else {
        // Default behavior: navigate to signup page
        router.push('/auth/register?trial=true')
      }
    } catch (error) {
      console.error('Error starting trial:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleNoCreditCard = () => {
    // Track no credit card info click
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'trial_info', {
        event_category: 'engagement',
        event_label: 'no_credit_card_info'
      })
    }

    // Navigate to trial information page or show modal
    router.push('/trial-info')
  }

  return (
    <div className={`text-center py-12 ${className}`}>
      <h2 className="text-2xl font-semibold text-gray-900 mb-8">
        Ready to see these features in action?
      </h2>
      
      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-2xl mx-auto">
        {/* Free 3-day trial button */}
        <Button
          onClick={handleFreeTrial}
          disabled={isLoading}
          className="flex items-center gap-3 px-8 py-4 h-auto bg-white border-2 border-gray-300 text-gray-900 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 rounded-xl font-semibold text-lg min-w-[200px]"
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
          ) : (
            <Lock className="w-5 h-5 text-gray-600" />
          )}
          <span>Free 3-day trial</span>
          <ArrowRight className="w-4 h-4" />
        </Button>

        {/* No credit card required button */}
        <Button
          onClick={handleNoCreditCard}
          variant="outline"
          className="flex items-center gap-3 px-8 py-4 h-auto bg-white border-2 border-gray-300 text-gray-900 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 rounded-xl font-semibold text-lg min-w-[200px]"
        >
          <Shield className="w-5 h-5 text-gray-600" />
          <span>No credit card required</span>
        </Button>
      </div>

      {/* Additional trust signals */}
      <div className="mt-6 text-sm text-gray-500">
        <p>✓ Cancel anytime • ✓ Full access to all features • ✓ Setup in under 5 minutes</p>
      </div>
    </div>
  )
}

// Alternative compact version for smaller spaces
export function TrialSignupCompact({ className = '', onTrialStart }: TrialSignupSectionProps) {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleFreeTrial = async () => {
    setIsLoading(true)
    try {
      if (onTrialStart) {
        onTrialStart()
      } else {
        router.push('/auth/register?trial=true')
      }
    } catch (error) {
      console.error('Error starting trial:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={`text-center py-8 ${className}`}>
      <h3 className="text-xl font-semibold text-gray-900 mb-6">
        Ready to see these features in action?
      </h3>
      
      <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
        <Button
          onClick={handleFreeTrial}
          disabled={isLoading}
          className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Lock className="w-4 h-4" />
          )}
          <span>Start Free Trial</span>
        </Button>

        <Button
          onClick={() => router.push('/trial-info')}
          variant="outline"
          className="flex items-center gap-2 px-6 py-3 border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg font-semibold"
        >
          <Shield className="w-4 h-4" />
          <span>No Credit Card</span>
        </Button>
      </div>
    </div>
  )
}

// Hero section version with enhanced styling
export function TrialSignupHero({ className = '', onTrialStart }: TrialSignupSectionProps) {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleFreeTrial = async () => {
    setIsLoading(true)
    try {
      if (onTrialStart) {
        onTrialStart()
      } else {
        router.push('/auth/register?trial=true')
      }
    } catch (error) {
      console.error('Error starting trial:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={`bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16 ${className}`}>
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h2 className="text-4xl font-bold mb-4">
          Ready to see these features in action?
        </h2>
        <p className="text-xl mb-8 opacity-90">
          Join thousands of businesses already using AI ERP to streamline their operations
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button
            onClick={handleFreeTrial}
            disabled={isLoading}
            className="flex items-center gap-3 px-8 py-4 h-auto bg-white text-blue-600 hover:bg-gray-100 transition-all duration-200 rounded-xl font-semibold text-lg min-w-[200px] shadow-lg"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Lock className="w-5 h-5" />
            )}
            <span>Free 3-day trial</span>
            <ArrowRight className="w-4 h-4" />
          </Button>

          <Button
            onClick={() => router.push('/trial-info')}
            variant="outline"
            className="flex items-center gap-3 px-8 py-4 h-auto bg-transparent border-2 border-white text-white hover:bg-white hover:text-blue-600 transition-all duration-200 rounded-xl font-semibold text-lg min-w-[200px]"
          >
            <Shield className="w-5 h-5" />
            <span>No credit card required</span>
          </Button>
        </div>

        <div className="mt-6 text-sm opacity-80">
          <p>✓ Cancel anytime • ✓ Full access to all features • ✓ Setup in under 5 minutes</p>
        </div>
      </div>
    </div>
  )
}











