'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  Key, 
  Lock, 
  Eye, 
  EyeOff,
  CheckCircle,
  AlertTriangle,
  Clock,
  Smartphone,
  Monitor,
  Globe
} from 'lucide-react'

export default function SecurityPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const tabs = [
    { id: 'overview', name: 'Overview', icon: Shield },
    { id: 'password', name: 'Password', icon: Lock },
    { id: '2fa', name: 'Two-Factor Auth', icon: Key },
    { id: 'sessions', name: 'Active Sessions', icon: Monitor },
  ]

  // Mock security data
  const securityData = {
    score: 85,
    recommendations: [
      { id: 1, title: 'Enable Two-Factor Authentication', priority: 'high', completed: false },
      { id: 2, title: 'Update Password', priority: 'medium', completed: true },
      { id: 3, title: 'Review Active Sessions', priority: 'low', completed: false },
      { id: 4, title: 'Enable Login Notifications', priority: 'medium', completed: true }
    ],
    recentActivity: [
      { action: 'Password changed', time: '2024-01-15T10:30:00Z', ip: '192.168.1.100', device: 'Chrome on Windows' },
      { action: 'Login from new device', time: '2024-01-14T14:20:00Z', ip: '192.168.1.101', device: 'Safari on iPhone' },
      { action: 'Two-factor authentication enabled', time: '2024-01-13T09:15:00Z', ip: '192.168.1.100', device: 'Chrome on Windows' },
      { action: 'API key generated', time: '2024-01-12T16:45:00Z', ip: '192.168.1.100', device: 'Chrome on Windows' }
    ],
    activeSessions: [
      { id: '1', device: 'Chrome on Windows', location: 'New York, NY', lastActive: '2024-01-15T10:30:00Z', current: true },
      { id: '2', device: 'Safari on iPhone', location: 'New York, NY', lastActive: '2024-01-14T14:20:00Z', current: false },
      { id: '3', device: 'Firefox on Mac', location: 'San Francisco, CA', lastActive: '2024-01-13T09:15:00Z', current: false }
    ]
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            {/* Security Score */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Security Score</h3>
                <span className={`text-2xl font-bold ${getScoreColor(securityData.score)}`}>
                  {securityData.score}/100
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${securityData.score}%` }}
                  role="progressbar"
                  aria-valuenow={securityData.score}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`Security score: ${securityData.score} out of 100`}
                ></div>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Your account security is {securityData.score >= 80 ? 'strong' : securityData.score >= 60 ? 'moderate' : 'weak'}
              </p>
            </div>

            {/* Recommendations */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Security Recommendations</h3>
              <div className="space-y-3">
                {securityData.recommendations.map((rec) => (
                  <div key={rec.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        {rec.completed ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : (
                          <AlertTriangle className="h-5 w-5 text-yellow-500" />
                        )}
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">{rec.title}</p>
                        <Badge className={`mt-1 ${getPriorityColor(rec.priority)}`}>
                          {rec.priority}
                        </Badge>
                      </div>
                    </div>
                    {!rec.completed && (
                      <Button variant="outline" size="sm">
                        Fix
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {securityData.recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                      <p className="text-sm text-gray-500">
                        {activity.device} • {activity.ip}
                      </p>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(activity.time).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )

      case 'password':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Change Password</h3>
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="currentPassword">Current Password</Label>
                  <div className="relative mt-1">
                    <Input
                      id="currentPassword"
                      type={showCurrentPassword ? 'text' : 'password'}
                      className="pr-10"
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    >
                      {showCurrentPassword ? (
                        <EyeOff className="h-4 w-4 text-gray-400" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>
                <div>
                  <Label htmlFor="newPassword">New Password</Label>
                  <div className="relative mt-1">
                    <Input
                      id="newPassword"
                      type={showNewPassword ? 'text' : 'password'}
                      className="pr-10"
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                    >
                      {showNewPassword ? (
                        <EyeOff className="h-4 w-4 text-gray-400" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>
                <div>
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <div className="relative mt-1">
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      className="pr-10"
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4 text-gray-400" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button className="flex items-center gap-2">
                    <Lock className="h-4 w-4" />
                    Update Password
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )

      case '2fa':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Two-Factor Authentication</h3>
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Authenticator App</h4>
                  <p className="text-sm text-gray-500">Use an authenticator app to generate codes</p>
                </div>
                <Button variant="outline" size="sm">
                  Enable
                </Button>
              </div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">SMS</h4>
                  <p className="text-sm text-gray-500">Receive codes via text message</p>
                </div>
                <Button variant="outline" size="sm">
                  Enable
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Backup Codes</h4>
                  <p className="text-sm text-gray-500">Generate backup codes for account recovery</p>
                </div>
                <Button variant="outline" size="sm">
                  Generate
                </Button>
              </div>
            </div>
          </div>
        )

      case 'sessions':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Active Sessions</h3>
            <div className="space-y-4">
              {securityData.activeSessions.map((session) => (
                <div key={session.id} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        {session.device.includes('iPhone') || session.device.includes('Android') ? (
                          <Smartphone className="h-5 w-5 text-gray-400" />
                        ) : (
                          <Monitor className="h-5 w-5 text-gray-400" />
                        )}
                      </div>
                      <div className="ml-4">
                        <h4 className="text-sm font-medium text-gray-900">{session.device}</h4>
                        <p className="text-sm text-gray-500">
                          <Globe className="h-3 w-3 inline mr-1" />
                          {session.location}
                        </p>
                        <p className="text-sm text-gray-500">
                          <Clock className="h-3 w-3 inline mr-1" />
                          Last active: {new Date(session.lastActive).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {session.current && (
                        <Badge className="bg-green-100 text-green-800">Current</Badge>
                      )}
                      <Button variant="outline" size="sm">
                        Revoke
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Security</h1>
        <p className="mt-2 text-gray-600">
          Manage your account security settings and monitor activity
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <tab.icon className="h-4 w-4 mr-3" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          {renderTabContent()}
        </div>
      </div>
    </>
  )
}