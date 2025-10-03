'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { DashboardHeader } from '@/components/dashboard/dashboard-header'
import { DashboardSidebar } from '@/components/dashboard/dashboard-sidebar'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { 
  Key, 
  Plus, 
  Copy, 
  Eye, 
  EyeOff,
  Trash2,
  Edit,
  Calendar,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'
import { DeleteConfirmationDialog } from '@/components/modals/delete-confirmation-dialog'

export default function APIKeysPage() {
  const { user, company, isLoading, isAuthenticated } = useAuth()
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showKeys, setShowKeys] = useState<{ [key: string]: boolean }>({})
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false)
  const [deleteConfirmationData, setDeleteConfirmationData] = useState<{
    title: string
    description: string
    itemName: string
    itemType: string
    onConfirm: () => void
  } | null>(null)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isLoading, isAuthenticated, router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  // Mock API keys data
  const apiKeys = [
    {
      id: 'key001',
      name: 'Production API Key',
      key: 'ak_live_1234567890abcdef1234567890abcdef',
      environment: 'production',
      status: 'active',
      permissions: ['read', 'write', 'admin'],
      lastUsed: '2024-01-15T10:30:00Z',
      createdAt: '2023-12-01T09:00:00Z',
      expiresAt: null,
      usage: {
        requests: 15420,
        limit: 100000
      }
    },
    {
      id: 'key002',
      name: 'Development API Key',
      key: 'ak_test_abcdef1234567890abcdef1234567890',
      environment: 'development',
      status: 'active',
      permissions: ['read', 'write'],
      lastUsed: '2024-01-14T16:45:00Z',
      createdAt: '2023-11-15T14:30:00Z',
      expiresAt: '2024-02-15T00:00:00Z',
      usage: {
        requests: 8920,
        limit: 50000
      }
    },
    {
      id: 'key003',
      name: 'Webhook Integration',
      key: 'ak_webhook_9876543210fedcba9876543210fedcba',
      environment: 'production',
      status: 'inactive',
      permissions: ['read'],
      lastUsed: '2024-01-10T08:20:00Z',
      createdAt: '2023-10-20T11:15:00Z',
      expiresAt: null,
      usage: {
        requests: 2340,
        limit: 10000
      }
    }
  ]

  const getEnvironmentColor = (environment: string) => {
    switch (environment) {
      case 'production': return 'bg-red-100 text-red-800'
      case 'development': return 'bg-yellow-100 text-yellow-800'
      case 'staging': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'inactive': return 'bg-red-100 text-red-800'
      case 'expired': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4" />
      case 'inactive': return <AlertTriangle className="h-4 w-4" />
      case 'expired': return <Clock className="h-4 w-4" />
      default: return null
    }
  }

  const toggleKeyVisibility = (keyId: string) => {
    setShowKeys(prev => ({
      ...prev,
      [keyId]: !prev[keyId]
    }))
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    // In a real app, you'd show a toast notification
    console.log('Copied to clipboard:', text)
  }

  const handleCreateKey = () => {
    setShowCreateModal(true)
    // In a real app, this would open a modal
  }

  const handleDeleteKey = (keyId: string) => {
    const apiKey = mockApiKeys.find(key => key.id === keyId)
    if (apiKey) {
      setDeleteConfirmationData({
        title: 'Delete API Key',
        description: 'Are you sure you want to delete this API key?',
        itemName: apiKey.name,
        itemType: 'API key',
        onConfirm: () => {
          console.log('Deleting key:', keyId)
          // In a real app, this would make an API call to delete the key
          setShowDeleteConfirmation(false)
          setDeleteConfirmationData(null)
        }
      })
      setShowDeleteConfirmation(true)
    }
  }

  const handleRegenerateKey = (keyId: string) => {
    console.log('Regenerating key:', keyId)
    // In a real app, this would show a confirmation dialog
  }

  const formatKey = (key: string, show: boolean) => {
    if (show) return key
    return key.substring(0, 8) + '•'.repeat(key.length - 16) + key.substring(key.length - 8)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader 
        user={user} 
        company={company}
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
      />
      
      <div className="flex">
        <DashboardSidebar 
          isOpen={sidebarOpen} 
          onClose={() => setSidebarOpen(false)}
          user={user}
          company={company}
        />
        
        <div className="flex-1 px-4 sm:px-6 lg:px-8 py-8">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
                  <p className="mt-2 text-gray-600">
                    Manage your API keys and access tokens
                  </p>
                </div>
                <Button onClick={handleCreateKey} className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Create API Key
                </Button>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Key className="h-6 w-6 text-blue-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Total Keys
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {apiKeys.length}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Active Keys
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {apiKeys.filter(k => k.status === 'active').length}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Activity className="h-6 w-6 text-purple-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Total Requests
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {apiKeys.reduce((sum, k) => sum + k.usage.requests, 0).toLocaleString()}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <AlertTriangle className="h-6 w-6 text-yellow-600" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          Expiring Soon
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {apiKeys.filter(k => k.expiresAt && new Date(k.expiresAt) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)).length}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* API Keys List */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Your API Keys</h2>
              </div>
              <div className="divide-y divide-gray-200">
                {apiKeys.map((apiKey) => (
                  <div key={apiKey.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-sm font-medium text-gray-900">{apiKey.name}</h3>
                          <Badge className={getEnvironmentColor(apiKey.environment)}>
                            {apiKey.environment.charAt(0).toUpperCase() + apiKey.environment.slice(1)}
                          </Badge>
                          <Badge className={getStatusColor(apiKey.status)}>
                            <div className="flex items-center">
                              {getStatusIcon(apiKey.status)}
                              <span className="ml-1">{apiKey.status.charAt(0).toUpperCase() + apiKey.status.slice(1)}</span>
                            </div>
                          </Badge>
                        </div>
                        
                        <div className="flex items-center gap-4 mb-3">
                          <div className="flex items-center">
                            <Key className="h-4 w-4 text-gray-400 mr-2" />
                            <code className="text-sm font-mono text-gray-600 bg-gray-100 px-2 py-1 rounded">
                              {formatKey(apiKey.key, showKeys[apiKey.id] || false)}
                            </code>
                            <button
                              onClick={() => toggleKeyVisibility(apiKey.id)}
                              className="ml-2 text-gray-400 hover:text-gray-600"
                            >
                              {showKeys[apiKey.id] ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                            <button
                              onClick={() => copyToClipboard(apiKey.key)}
                              className="ml-2 text-gray-400 hover:text-gray-600"
                              aria-label="Copy API key"
                            >
                              <Copy className="h-4 w-4" />
                            </button>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-500">
                          <div>
                            <span className="font-medium">Permissions:</span>
                            <div className="flex gap-1 mt-1">
                              {apiKey.permissions.map((permission) => (
                                <Badge key={permission} className="bg-gray-100 text-gray-800 text-xs">
                                  {permission}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          <div>
                            <span className="font-medium">Last Used:</span>
                            <div className="mt-1">
                              {new Date(apiKey.lastUsed).toLocaleDateString()}
                            </div>
                          </div>
                          <div>
                            <span className="font-medium">Usage:</span>
                            <div className="mt-1">
                              {apiKey.usage.requests.toLocaleString()} / {apiKey.usage.limit.toLocaleString()}
                            </div>
                          </div>
                        </div>

                        {apiKey.expiresAt && (
                          <div className="mt-2 text-sm text-yellow-600">
                            <AlertTriangle className="h-4 w-4 inline mr-1" />
                            Expires on {new Date(apiKey.expiresAt).toLocaleDateString()}
                          </div>
                        )}
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleRegenerateKey(apiKey.id)}
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Regenerate
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="text-red-600 hover:text-red-700"
                          onClick={() => handleDeleteKey(apiKey.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Empty State */}
            {apiKeys.length === 0 && (
              <div className="text-center py-12">
                <Key className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No API keys found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Get started by creating your first API key.
                </p>
                <div className="mt-6">
                  <Button onClick={handleCreateKey} className="flex items-center gap-2">
                    <Plus className="h-4 w-4" />
                    Create API Key
                  </Button>
                </div>
              </div>
            )}

            {/* Create Modal Placeholder */}
            {showCreateModal && (
              <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
                <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                  <div className="mt-3">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Create New API Key</h3>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="keyName">Key Name</Label>
                        <Input
                          id="keyName"
                          placeholder="e.g., Production API Key"
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="environment">Environment</Label>
                        <select
                          id="environment"
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          aria-label="Select environment"
                        >
                          <option value="development">Development</option>
                          <option value="staging">Staging</option>
                          <option value="production">Production</option>
                        </select>
                      </div>
                      <div>
                        <Label htmlFor="permissions">Permissions</Label>
                        <div className="mt-2 space-y-2">
                          <label className="flex items-center">
                            <input type="checkbox" className="h-4 w-4 text-blue-600" defaultChecked />
                            <span className="ml-2 text-sm text-gray-700">Read</span>
                          </label>
                          <label className="flex items-center">
                            <input type="checkbox" className="h-4 w-4 text-blue-600" defaultChecked />
                            <span className="ml-2 text-sm text-gray-700">Write</span>
                          </label>
                          <label className="flex items-center">
                            <input type="checkbox" className="h-4 w-4 text-blue-600" />
                            <span className="ml-2 text-sm text-gray-700">Admin</span>
                          </label>
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 mt-6">
                      <Button 
                        variant="outline" 
                        onClick={() => setShowCreateModal(false)}
                      >
                        Cancel
                      </Button>
                      <Button onClick={() => setShowCreateModal(false)}>
                        Create Key
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {deleteConfirmationData && (
        <DeleteConfirmationDialog
          isOpen={showDeleteConfirmation}
          onClose={() => {
            setShowDeleteConfirmation(false)
            setDeleteConfirmationData(null)
          }}
          onConfirm={deleteConfirmationData.onConfirm}
          title={deleteConfirmationData.title}
          description={deleteConfirmationData.description}
          itemName={deleteConfirmationData.itemName}
          itemType={deleteConfirmationData.itemType}
        />
      )}
    </div>
  )
}

