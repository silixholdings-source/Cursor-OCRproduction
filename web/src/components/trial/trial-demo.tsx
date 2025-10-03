'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { TrialBanner } from './trial-banner'
import { Clock, Calendar, Mail, AlertTriangle, CheckCircle } from 'lucide-react'

// Mock different trial states for demonstration
const trialStates = {
  day1: {
    name: 'Day 1 - Fresh Trial',
    company: {
      id: '1',
      name: 'Demo Company',
      max_users: 10,
      max_storage_gb: 100,
      plan: 'trial',
      is_trial: true,
      trial_ends_at: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString() // 2 days from now
    },
    user: {
      id: '1',
      email: 'demo@example.com',
      name: 'Demo User',
      role: 'admin'
    }
  },
  day2: {
    name: 'Day 2 - Warning Phase',
    company: {
      id: '1',
      name: 'Demo Company',
      max_users: 10,
      max_storage_gb: 100,
      plan: 'trial',
      is_trial: true,
      trial_ends_at: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString() // 1 day from now
    },
    user: {
      id: '1',
      email: 'demo@example.com',
      name: 'Demo User',
      role: 'admin'
    }
  },
  day3: {
    name: 'Day 3 - Last Day (Urgent)',
    company: {
      id: '1',
      name: 'Demo Company',
      max_users: 10,
      max_storage_gb: 100,
      plan: 'trial',
      is_trial: true,
      trial_ends_at: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString() // 2 hours from now
    },
    user: {
      id: '1',
      email: 'demo@example.com',
      name: 'Demo User',
      role: 'admin'
    }
  },
  expired: {
    name: 'Day 4+ - Expired Trial',
    company: {
      id: '1',
      name: 'Demo Company',
      max_users: 10,
      max_storage_gb: 100,
      plan: 'trial',
      is_trial: true,
      trial_ends_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() // 1 day ago
    },
    user: {
      id: '1',
      email: 'demo@example.com',
      name: 'Demo User',
      role: 'admin'
    }
  }
}

export function TrialDemo() {
  const [currentState, setCurrentState] = useState<keyof typeof trialStates>('day1')
  const [showEmailPreview, setShowEmailPreview] = useState(false)

  const mockAuthContext = (state: keyof typeof trialStates) => {
    const data = trialStates[state]
    const now = new Date()
    const trialEndDate = new Date(data.company.trial_ends_at)
    const isTrialExpired = now > trialEndDate
    const trialDaysLeft = Math.max(0, Math.ceil((trialEndDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)))

    return {
      user: data.user,
      company: data.company,
      isTrialExpired,
      trialDaysLeft,
      isAuthenticated: true,
      isLoading: false
    }
  }

  const currentMockData = mockAuthContext(currentState)

  const getEmailContent = (state: keyof typeof trialStates) => {
    const data = trialStates[state]
    const daysLeft = mockAuthContext(state).trialDaysLeft
    
    if (state === 'expired') {
      return {
        subject: 'Your AI ERP SaaS trial has expired - Upgrade to continue',
        preview: `Hi ${data.user.name}, Your 3-day free trial expired on ${new Date(data.company.trial_ends_at).toLocaleDateString()}. Your account is now in read-only mode. Upgrade to restore full functionality. Special offer: Upgrade within 7 days and get 20% off your first 3 months!`
      }
    } else {
      return {
        subject: `${daysLeft} day${daysLeft === 1 ? '' : 's'} left in your AI ERP SaaS trial`,
        preview: `Hi ${data.user.name}, Your 3-day free trial will expire in ${daysLeft} day${daysLeft === 1 ? '' : 's'} on ${new Date(data.company.trial_ends_at).toLocaleDateString()}. Don't lose access to AI-powered invoice automation!`
      }
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">3-Day Trial System Demo</h1>
        <p className="text-gray-600 mb-6">
          See how the trial system behaves at different stages
        </p>
        
        {/* State Selector */}
        <div className="flex flex-wrap justify-center gap-2 mb-6">
          {Object.entries(trialStates).map(([key, state]) => (
            <Button
              key={key}
              variant={currentState === key ? 'default' : 'outline'}
              onClick={() => setCurrentState(key as keyof typeof trialStates)}
              size="sm"
            >
              {state.name}
            </Button>
          ))}
        </div>
      </div>

      {/* Current State Info */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="w-5 h-5 mr-2" />
            Current Demo State: {trialStates[currentState].name}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-600">Trial Status</label>
              <div className="flex items-center mt-1">
                {currentMockData.isTrialExpired ? (
                  <Badge variant="destructive">Expired</Badge>
                ) : (
                  <Badge className="bg-blue-600">Active</Badge>
                )}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Days Left</label>
              <div className="text-lg font-bold mt-1">
                {currentMockData.trialDaysLeft} day{currentMockData.trialDaysLeft === 1 ? '' : 's'}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Expires On</label>
              <div className="text-sm mt-1">
                {new Date(currentMockData.company.trial_ends_at!).toLocaleDateString()}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Trial Banner Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            Dashboard Banner Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 p-4 rounded-lg">
            {/* Mock the TrialBanner with current state */}
            <MockTrialBanner mockData={currentMockData} />
          </div>
        </CardContent>
      </Card>

      {/* Email Notification Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center">
              <Mail className="w-5 h-5 mr-2" />
              Email Notification Preview
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowEmailPreview(!showEmailPreview)}
            >
              {showEmailPreview ? 'Hide' : 'Show'} Email
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {showEmailPreview && (
            <div className="border rounded-lg p-4 bg-white">
              <div className="border-b pb-4 mb-4">
                <div className="text-sm text-gray-600 mb-2">
                  <strong>To:</strong> {currentMockData.user.email}
                </div>
                <div className="text-sm text-gray-600 mb-2">
                  <strong>From:</strong> AI ERP SaaS &lt;noreply@ai-erp-saas.com&gt;
                </div>
                <div className="text-sm font-medium">
                  <strong>Subject:</strong> {getEmailContent(currentState).subject}
                </div>
              </div>
              <div className="prose prose-sm max-w-none">
                <p>{getEmailContent(currentState).preview}</p>
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                  <p className="text-sm text-blue-800 mb-2">
                    <strong>Email would include:</strong>
                  </p>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Professional HTML template with SILIX Holdings branding</li>
                    <li>• Clear upgrade call-to-action buttons</li>
                    <li>• Feature highlights and benefits</li>
                    <li>• Special offers for quick upgrades</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* System Behavior Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" />
            System Behavior at This Stage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {currentState === 'day1' && (
              <div className="space-y-2">
                <div className="flex items-center text-green-600">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Full access to all features
                </div>
                <div className="flex items-center text-green-600">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Blue informational banner in dashboard
                </div>
                <div className="flex items-center text-green-600">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  No email notifications yet
                </div>
              </div>
            )}
            
            {currentState === 'day2' && (
              <div className="space-y-2">
                <div className="flex items-center text-yellow-600">
                  <Clock className="w-4 h-4 mr-2" />
                  Yellow warning banner appears
                </div>
                <div className="flex items-center text-green-600">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Still full access to features
                </div>
                <div className="flex items-center text-blue-600">
                  <Mail className="w-4 h-4 mr-2" />
                  First warning email sent
                </div>
              </div>
            )}
            
            {currentState === 'day3' && (
              <div className="space-y-2">
                <div className="flex items-center text-red-600">
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  Red urgent banner - "Trial expires today!"
                </div>
                <div className="flex items-center text-green-600">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Still full access (last chance)
                </div>
                <div className="flex items-center text-red-600">
                  <Mail className="w-4 h-4 mr-2" />
                  Final warning email sent
                </div>
              </div>
            )}
            
            {currentState === 'expired' && (
              <div className="space-y-2">
                <div className="flex items-center text-red-600">
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  Account in read-only mode
                </div>
                <div className="flex items-center text-red-600">
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  No new invoice processing
                </div>
                <div className="flex items-center text-red-600">
                  <Mail className="w-4 h-4 mr-2" />
                  Trial expired email with 20% discount offer
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Mock Trial Banner Component for Demo
function MockTrialBanner({ mockData }: { mockData: any }) {
  if (!mockData.company?.is_trial) {
    return null
  }

  if (mockData.isTrialExpired) {
    return (
      <div className="border-red-200 bg-red-50 border rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <AlertTriangle className="h-4 w-4 text-red-600 mr-2" />
            <div>
              <span className="font-semibold text-red-800">Trial Expired</span>
              <p className="text-red-700 text-sm mt-1">
                Your 3-day trial has ended. Upgrade to continue using all features.
              </p>
            </div>
          </div>
          <Button className="bg-red-600 hover:bg-red-700 text-white ml-4">
            Upgrade Now
          </Button>
        </div>
      </div>
    )
  }

  const getBannerStyle = () => {
    if (mockData.trialDaysLeft <= 0) {
      return "border-red-200 bg-red-50"
    } else if (mockData.trialDaysLeft <= 1) {
      return "border-yellow-200 bg-yellow-50"
    } else {
      return "border-blue-200 bg-blue-50"
    }
  }

  const getTextColor = () => {
    if (mockData.trialDaysLeft <= 0) {
      return "text-red-800"
    } else if (mockData.trialDaysLeft <= 1) {
      return "text-yellow-800"
    } else {
      return "text-blue-800"
    }
  }

  const getIconColor = () => {
    if (mockData.trialDaysLeft <= 0) {
      return "text-red-600"
    } else if (mockData.trialDaysLeft <= 1) {
      return "text-yellow-600"
    } else {
      return "text-blue-600"
    }
  }

  return (
    <div className={`${getBannerStyle()} border rounded-lg p-4`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Clock className={`h-4 w-4 ${getIconColor()} mr-2`} />
          <div>
            <span className={`font-semibold ${getTextColor()}`}>
              {mockData.trialDaysLeft === 0 
                ? 'Trial expires today!' 
                : `${mockData.trialDaysLeft} day${mockData.trialDaysLeft === 1 ? '' : 's'} left in trial`
              }
            </span>
            <p className={`${getTextColor()} text-sm mt-1`}>
              {mockData.trialDaysLeft === 0 
                ? 'Upgrade today to continue using all features without interruption.'
                : 'Enjoying AI ERP SaaS? Upgrade to continue beyond your trial period.'
              }
            </p>
          </div>
        </div>
        <Button variant="outline" className="ml-4">
          View Plans
        </Button>
      </div>
    </div>
  )
}


