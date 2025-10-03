'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  User, 
  Building2, 
  Shield, 
  Bell, 
  Key,
  Save,
  Edit
} from 'lucide-react'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile')
  const [isEditing, setIsEditing] = useState(false)
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [show2FAModal, setShow2FAModal] = useState(false)
  const [showAPIKeysModal, setShowAPIKeysModal] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  
  const handleChangePassword = () => {
    setShowPasswordModal(true)
  }
  
  const handleEnable2FA = () => {
    setShow2FAModal(true)
  }
  
  const handleManageAPIKeys = () => {
    setShowAPIKeysModal(true)
  }
  
  const handleSaveProfile = async () => {
    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      setSuccessMessage('Profile updated successfully!')
      setIsEditing(false)
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (error) {
      console.error('Failed to save profile:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleSaveCompany = async () => {
    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      setSuccessMessage('Company information updated successfully!')
      setIsEditing(false)
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (error) {
      console.error('Failed to save company info:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'company', name: 'Company', icon: Building2 },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'notifications', name: 'Notifications', icon: Bell },
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Personal Information</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                <Edit className="h-4 w-4 mr-1" />
                {isEditing ? 'Cancel' : 'Edit'}
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  defaultValue="John"
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  defaultValue="Doe"
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  defaultValue="john.doe@company.com"
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  defaultValue="+1 (555) 123-4567"
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
            </div>
            {isEditing && (
              <div className="flex justify-end">
                <Button 
                  className="flex items-center gap-2"
                  onClick={handleSaveProfile}
                  disabled={isLoading}
                >
                  <Save className="h-4 w-4" />
                  {isLoading ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            )}
          </div>
        )

      case 'company':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Company Information</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                <Edit className="h-4 w-4 mr-1" />
                {isEditing ? 'Cancel' : 'Edit'}
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <Label htmlFor="companyName">Company Name</Label>
                <Input
                  id="companyName"
                  defaultValue="Demo Company"
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="industry">Industry</Label>
                <Input
                  id="industry"
                  defaultValue="Technology"
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="size">Company Size</Label>
                <Input
                  id="size"
                  defaultValue="50-100 employees"
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div className="md:col-span-2">
                <Label htmlFor="address">Address</Label>
                <Input
                  id="address"
                  defaultValue="123 Business St, City, State 12345"
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
            </div>
            {isEditing && (
              <div className="flex justify-end">
                <Button 
                  className="flex items-center gap-2"
                  onClick={handleSaveCompany}
                  disabled={isLoading}
                >
                  <Save className="h-4 w-4" />
                  {isLoading ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            )}
          </div>
        )

      case 'security':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Security Settings</h3>
            <div className="space-y-4">
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Password</h4>
                    <p className="text-sm text-gray-500">Last changed 30 days ago</p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={handleChangePassword}
                  >
                    Change Password
                  </Button>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Two-Factor Authentication</h4>
                    <p className="text-sm text-gray-500">Add an extra layer of security</p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={handleEnable2FA}
                  >
                    Enable 2FA
                  </Button>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">API Keys</h4>
                    <p className="text-sm text-gray-500">Manage your API access keys</p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={handleManageAPIKeys}
                  >
                    Manage Keys
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )

      case 'notifications':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Notification Preferences</h3>
            <div className="space-y-4">
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Email Notifications</h4>
                    <p className="text-sm text-gray-500">Receive updates via email</p>
                  </div>
                  <input
                    type="checkbox"
                    defaultChecked
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    aria-label="Enable email notifications"
                  />
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Invoice Approvals</h4>
                    <p className="text-sm text-gray-500">Get notified when invoices need approval</p>
                  </div>
                  <input
                    type="checkbox"
                    defaultChecked
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    aria-label="Enable invoice approval notifications"
                  />
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Weekly Reports</h4>
                    <p className="text-sm text-gray-500">Receive weekly summary reports</p>
                  </div>
                  <input
                    type="checkbox"
                    defaultChecked
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    aria-label="Enable weekly reports"
                  />
                </div>
              </div>
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
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Manage your account settings and preferences
        </p>
        
        {/* Success Message */}
        {successMessage && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800">{successMessage}</p>
          </div>
        )}
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
          <div className="bg-white shadow rounded-lg p-6">
            {renderTabContent()}
          </div>
        </div>
      </div>

      {/* Simple Modal Implementations */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Change Password</h3>
            <div className="space-y-4">
              <div>
                <Label htmlFor="currentPassword">Current Password</Label>
                <Input id="currentPassword" type="password" className="mt-1" />
              </div>
              <div>
                <Label htmlFor="newPassword">New Password</Label>
                <Input id="newPassword" type="password" className="mt-1" />
              </div>
              <div>
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <Input id="confirmPassword" type="password" className="mt-1" />
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <Button variant="outline" onClick={() => setShowPasswordModal(false)}>
                Cancel
              </Button>
              <Button onClick={() => {
                setSuccessMessage('Password changed successfully!')
                setShowPasswordModal(false)
              }}>
                Change Password
              </Button>
            </div>
          </div>
        </div>
      )}

      {show2FAModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Enable Two-Factor Authentication</h3>
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Two-factor authentication adds an extra layer of security to your account.
              </p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium">Setup Steps:</p>
                <ol className="text-sm text-gray-600 mt-2 space-y-1">
                  <li>1. Download an authenticator app</li>
                  <li>2. Scan the QR code</li>
                  <li>3. Enter the verification code</li>
                </ol>
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <Button variant="outline" onClick={() => setShow2FAModal(false)}>
                Cancel
              </Button>
              <Button onClick={() => {
                setSuccessMessage('2FA setup initiated! Check your email for instructions.')
                setShow2FAModal(false)
              }}>
                Continue Setup
              </Button>
            </div>
          </div>
        </div>
      )}

      {showAPIKeysModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">API Keys Management</h3>
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Manage your API access keys for integrations and third-party applications.
              </p>
              <div className="border rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-medium">Production API Key</p>
                    <p className="text-sm text-gray-500">Created 15 days ago</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Regenerate
                  </Button>
                </div>
              </div>
              <div className="border rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-medium">Development API Key</p>
                    <p className="text-sm text-gray-500">Created 30 days ago</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Regenerate
                  </Button>
                </div>
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <Button variant="outline" onClick={() => setShowAPIKeysModal(false)}>
                Close
              </Button>
              <Button onClick={() => {
                setSuccessMessage('New API key generated successfully!')
                setShowAPIKeysModal(false)
              }}>
                Generate New Key
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}