'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { 
  Building2, 
  Save, 
  Edit, 
  Users, 
  Shield, 
  Settings,
  Globe,
  Phone,
  Mail,
  MapPin,
  Calendar,
  CheckCircle
} from 'lucide-react'

export default function CompanyPage() {
  const [isEditing, setIsEditing] = useState(false)
  const [activeTab, setActiveTab] = useState('general')

  const tabs = [
    { id: 'general', name: 'General', icon: Building2 },
    { id: 'team', name: 'Team', icon: Users },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'integrations', name: 'Integrations', icon: Settings },
  ]

  // Mock company data
  const companyData = {
    name: 'Demo Company',
    industry: 'Technology',
    size: '50-100 employees',
    website: 'https://democompany.com',
    email: 'contact@democompany.com',
    phone: '+1 (555) 123-4567',
    address: '123 Business St, City, State 12345',
    founded: '2020',
    description: 'A leading technology company specializing in AI-powered solutions.',
    team: [
      { name: 'John Doe', role: 'CEO', email: 'john@democompany.com', status: 'active' },
      { name: 'Jane Smith', role: 'CTO', email: 'jane@democompany.com', status: 'active' },
      { name: 'Mike Johnson', role: 'CFO', email: 'mike@democompany.com', status: 'active' },
      { name: 'Sarah Wilson', role: 'COO', email: 'sarah@democompany.com', status: 'inactive' }
    ],
    integrations: [
      { name: 'SAP ERP', status: 'connected', lastSync: '2024-01-15T10:30:00Z' },
      { name: 'Salesforce CRM', status: 'connected', lastSync: '2024-01-15T09:15:00Z' },
      { name: 'QuickBooks', status: 'error', lastSync: '2024-01-14T16:45:00Z' }
    ]
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'inactive': return 'bg-gray-100 text-gray-800'
      case 'connected': return 'bg-green-100 text-green-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Active'
      case 'inactive': return 'Inactive'
      case 'connected': return 'Connected'
      case 'error': return 'Error'
      default: return status
    }
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
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
                  defaultValue={companyData.name}
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="industry">Industry</Label>
                <Input
                  id="industry"
                  defaultValue={companyData.industry}
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="size">Company Size</Label>
                <Input
                  id="size"
                  defaultValue={companyData.size}
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="website">Website</Label>
                <Input
                  id="website"
                  defaultValue={companyData.website}
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="founded">Founded</Label>
                <Input
                  id="founded"
                  defaultValue={companyData.founded}
                  disabled={!isEditing}
                  className="mt-1"
                />
              </div>
              <div className="md:col-span-2">
                <Label htmlFor="description">Description</Label>
                <textarea
                  id="description"
                  name="description"
                  defaultValue={companyData.description}
                  disabled={!isEditing}
                  rows={3}
                  placeholder="Enter company description"
                  aria-label="Company description"
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
                />
              </div>
            </div>
            {isEditing && (
              <div className="flex justify-end">
                <Button className="flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  Save Changes
                </Button>
              </div>
            )}
          </div>
        )

      case 'team':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Team Members</h3>
              <Button className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                Add Member
              </Button>
            </div>
            <div className="space-y-4">
              {companyData.team.map((member, index) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <Users className="h-5 w-5 text-gray-600" />
                      </div>
                      <div className="ml-4">
                        <h4 className="text-sm font-medium text-gray-900">{member.name}</h4>
                        <p className="text-sm text-gray-500">{member.role}</p>
                        <p className="text-sm text-gray-500 flex items-center">
                          <Mail className="h-3 w-3 mr-1" />
                          {member.email}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(member.status)}>
                        {getStatusText(member.status)}
                      </Badge>
                      <Button variant="ghost" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
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
                    <h4 className="text-sm font-medium text-gray-900">Two-Factor Authentication</h4>
                    <p className="text-sm text-gray-500">Require 2FA for all team members</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Configure
                  </Button>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Session Timeout</h4>
                    <p className="text-sm text-gray-500">Automatically log out inactive users</p>
                  </div>
                  <select 
                    id="session-timeout"
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                    aria-label="Session timeout duration"
                  >
                    <option value="30">30 minutes</option>
                    <option value="60">1 hour</option>
                    <option value="120">2 hours</option>
                    <option value="480">8 hours</option>
                  </select>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">API Access</h4>
                    <p className="text-sm text-gray-500">Manage API keys and access controls</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Manage
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )

      case 'integrations':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Active Integrations</h3>
            <div className="space-y-4">
              {companyData.integrations.map((integration, index) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <Settings className="h-5 w-5 text-blue-600" />
                      </div>
                      <div className="ml-4">
                        <h4 className="text-sm font-medium text-gray-900">{integration.name}</h4>
                        <p className="text-sm text-gray-500">
                          Last sync: {new Date(integration.lastSync).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(integration.status)}>
                        {getStatusText(integration.status)}
                      </Badge>
                      <Button variant="outline" size="sm">
                        Configure
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
        <h1 className="text-3xl font-bold text-gray-900">Company Settings</h1>
        <p className="mt-2 text-gray-600">
          Manage your company information, team, and integrations
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
          <div className="bg-white shadow rounded-lg p-6">
            {renderTabContent()}
          </div>
        </div>
      </div>
    </>
  )
}