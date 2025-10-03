'use client'

import React from 'react'
import { useAuth } from '@/hooks/use-auth'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { AlertTriangle, CreditCard, Clock, X } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface TrialExpiredModalProps {
  isOpen: boolean
  onClose: () => void
}

export function TrialExpiredModal({ isOpen, onClose }: TrialExpiredModalProps) {
  const { company } = useAuth()
  const router = useRouter()

  const handleUpgrade = () => {
    router.push('/pricing?utm_source=trial_expired_modal')
    onClose()
  }

  const trialEndDate = company?.trial_ends_at ? new Date(company.trial_ends_at) : null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center text-red-600">
            <AlertTriangle className="w-5 h-5 mr-2" />
            Trial Expired
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Clock className="w-8 h-8 text-red-600" />
            </div>
            
            <h3 className="text-lg font-semibold mb-2">Your 3-day trial has ended</h3>
            <p className="text-gray-600 text-sm mb-4">
              Trial expired on {trialEndDate?.toLocaleDateString()}
            </p>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-semibold text-red-800 mb-2">Limited Access</h4>
            <ul className="text-sm text-red-700 space-y-1">
              <li>• Read-only access to your data</li>
              <li>• Cannot process new invoices</li>
              <li>• No AI features available</li>
              <li>• Limited dashboard functionality</li>
            </ul>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-2">🚀 Upgrade Benefits</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Unlimited invoice processing</li>
              <li>• Full AI-powered automation</li>
              <li>• Advanced analytics & reporting</li>
              <li>• Priority customer support</li>
            </ul>
          </div>

          <div className="space-y-3">
            <Button 
              onClick={handleUpgrade}
              className="w-full bg-red-600 hover:bg-red-700 text-white"
              size="lg"
            >
              <CreditCard className="w-4 h-4 mr-2" />
              Upgrade Now - Restore Full Access
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => router.push('/pricing')}
              className="w-full"
            >
              View All Plans
            </Button>
          </div>

          <div className="text-center">
            <p className="text-xs text-gray-500">
              Special offer: Upgrade within 7 days and save 20%
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export function TrialExpiredPage() {
  const { company, user } = useAuth()
  const router = useRouter()

  const trialEndDate = company?.trial_ends_at ? new Date(company.trial_ends_at) : null

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          {/* Header */}
          <div className="mb-8">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-10 h-10 text-red-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Trial Expired</h1>
            <p className="text-gray-600">
              Your 3-day free trial ended on {trialEndDate?.toLocaleDateString()}
            </p>
          </div>

          {/* Current Status */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
            <h2 className="text-lg font-semibold text-red-800 mb-3">Account Status: Limited Access</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex items-center text-red-700">
                  <X className="w-4 h-4 mr-2" />
                  No new invoice processing
                </div>
                <div className="flex items-center text-red-700">
                  <X className="w-4 h-4 mr-2" />
                  AI features disabled
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center text-red-700">
                  <X className="w-4 h-4 mr-2" />
                  Limited dashboard access
                </div>
                <div className="flex items-center text-red-700">
                  <X className="w-4 h-4 mr-2" />
                  No new integrations
                </div>
              </div>
            </div>
          </div>

          {/* Upgrade Options */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Restore Full Access</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold mb-2">Starter</h3>
                <div className="text-2xl font-bold text-blue-600 mb-2">$29/mo</div>
                <p className="text-sm text-gray-600">Perfect for small businesses</p>
              </div>
              <div className="border-2 border-blue-500 rounded-lg p-4 relative">
                <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded">Popular</span>
                </div>
                <h3 className="font-semibold mb-2">Professional</h3>
                <div className="text-2xl font-bold text-blue-600 mb-2">$79/mo</div>
                <p className="text-sm text-gray-600">For growing companies</p>
              </div>
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold mb-2">Business</h3>
                <div className="text-2xl font-bold text-blue-600 mb-2">$199/mo</div>
                <p className="text-sm text-gray-600">For large enterprises</p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-4">
            <Button 
              onClick={() => router.push('/pricing?utm_source=trial_expired_page')}
              className="w-full bg-red-600 hover:bg-red-700 text-white"
              size="lg"
            >
              <CreditCard className="w-5 h-5 mr-2" />
              Choose Your Plan - Restore Access Now
            </Button>
            
            <div className="flex space-x-4">
              <Button 
                variant="outline"
                onClick={() => router.push('/contact')}
                className="flex-1"
              >
                Contact Sales
              </Button>
              <Button 
                variant="outline"
                onClick={() => router.push('/')}
                className="flex-1"
              >
                Back to Home
              </Button>
            </div>
          </div>

          {/* Special Offer */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-800 mb-2">🎉 Limited Time Offer</h3>
            <p className="text-sm text-blue-700">
              Upgrade within 7 days of trial expiration and get <strong>20% off</strong> your first 3 months!
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}


