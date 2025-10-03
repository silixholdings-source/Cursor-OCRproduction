'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Clock, Crown, X } from 'lucide-react'
import { useAuth } from '@/hooks/use-auth'

export function TrialBanner() {
  const { company, trialDaysLeft, isTrialExpired } = useAuth()
  const [isVisible, setIsVisible] = useState(true)

  if (!company?.is_trial || !isVisible) {
    return null
  }

  const handleUpgrade = () => {
    window.location.href = '/pricing'
  }

  const handleDismiss = () => {
    setIsVisible(false)
  }

  if (isTrialExpired) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Clock className="h-5 w-5 text-red-600" />
            <div>
              <h3 className="font-semibold text-red-900">Trial Expired</h3>
              <p className="text-sm text-red-700">Your trial has ended. Upgrade to continue using all features.</p>
            </div>
          </div>
          <Button onClick={handleUpgrade} className="bg-red-600 hover:bg-red-700">
            <Crown className="w-4 h-4 mr-2" />
            Upgrade Now
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="h-5 w-5 text-blue-600" />
          <div>
            <h3 className="font-semibold text-blue-900">Free Trial Active</h3>
            <p className="text-sm text-blue-700">
              {trialDaysLeft} days remaining in your free trial
            </p>
          </div>
          <Badge variant="secondary" className="bg-blue-100 text-blue-800">
            {trialDaysLeft} days left
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={handleUpgrade} variant="outline" size="sm">
            <Crown className="w-4 h-4 mr-2" />
            Upgrade
          </Button>
          <Button onClick={handleDismiss} variant="ghost" size="sm">
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}