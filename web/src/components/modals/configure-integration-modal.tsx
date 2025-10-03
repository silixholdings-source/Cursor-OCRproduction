'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Switch } from '@/components/ui/switch'
import { 
  Database, 
  CheckCircle, 
  AlertTriangle, 
  Settings,
  RefreshCw,
  Trash2,
  TestTube,
  Shield,
  Clock,
  Zap
} from 'lucide-react'

interface ConfigureIntegrationModalProps {
  isOpen: boolean
  onClose: () => void
  integration: {
    id: string
    name: string
    status: string
    lastSync: string
    syncFrequency: string
    recordsSynced: number
    lastError: string | null
    version: string
  } | null
  onIntegrationUpdated?: (integration: any) => void
  onIntegrationDeleted?: (integrationId: string) => void
}

export function ConfigureIntegrationModal({ 
  isOpen, 
  onClose, 
  integration, 
  onIntegrationUpdated,
  onIntegrationDeleted 
}: ConfigureIntegrationModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    syncFrequency: 'hourly',
    apiUrl: '',
    apiKey: '',
    username: '',
    autoSync: true,
    syncOnStartup: false,
    retryOnError: true,
    maxRetries: 3,
    timeout: 30,
    batchSize: 100,
    description: ''
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [isTesting, setIsTesting] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  useEffect(() => {
    if (integration) {
      setFormData({
        name: integration.name,
        syncFrequency: integration.syncFrequency,
        apiUrl: 'https://api.example.com', // Mock URL
        apiKey: '••••••••••••••••', // Masked key
        username: 'admin@company.com',
        autoSync: true,
        syncOnStartup: false,
        retryOnError: true,
        maxRetries: 3,
        timeout: 30,
        batchSize: 100,
        description: `${integration.name} integration configuration`
      })
    }
  }, [integration])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({ 
      ...prev, 
      [name]: type === 'number' ? parseInt(value) || 0 : value 
    }))
    setError('')
  }

  const handleSwitchChange = (name: string, checked: boolean) => {
    setFormData(prev => ({ ...prev, [name]: checked }))
  }

  const validateForm = () => {
    if (!formData.name.trim()) {
      setError('Integration name is required')
      return false
    }
    if (!formData.apiUrl.trim()) {
      setError('API URL is required')
      return false
    }
    return true
  }

  const handleTestConnection = async () => {
    setIsTesting(true)
    setError('')
    
    try {
      // Simulate API test
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Simulate random success/failure
      if (Math.random() > 0.3) {
        setSuccessMessage('Connection test successful!')
        setTimeout(() => setSuccessMessage(''), 3000)
      } else {
        setError('Connection test failed. Please check your credentials.')
      }
    } catch (err) {
      setError('Connection test failed. Please try again.')
    } finally {
      setIsTesting(false)
    }
  }

  const handleSave = async () => {
    if (!validateForm()) return

    setIsLoading(true)
    setError('')

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      if (onIntegrationUpdated && integration) {
        onIntegrationUpdated({
          ...integration,
          name: formData.name,
          syncFrequency: formData.syncFrequency
        })
      }
      
      setSuccessMessage('Configuration saved successfully!')
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err) {
      setError('Failed to save configuration. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!integration) return

    setIsLoading(true)
    setError('')

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (onIntegrationDeleted) {
        onIntegrationDeleted(integration.id)
      }
      
      setShowDeleteConfirm(false)
      onClose()
    } catch (err) {
      setError('Failed to delete integration. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (!integration) return null

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Settings className="h-6 w-6" />
            Configure {integration.name}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Integration Status */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Database className="h-5 w-5" />
                Integration Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <Label className="text-sm text-gray-500">Status</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <div className={`w-2 h-2 rounded-full ${
                      integration.status === 'connected' ? 'bg-green-500' :
                      integration.status === 'error' ? 'bg-red-500' : 'bg-gray-500'
                    }`} />
                    <span className="text-sm font-medium capitalize">{integration.status}</span>
                  </div>
                </div>
                <div>
                  <Label className="text-sm text-gray-500">Records Synced</Label>
                  <p className="text-sm font-medium mt-1">{integration.recordsSynced.toLocaleString()}</p>
                </div>
                <div>
                  <Label className="text-sm text-gray-500">Last Sync</Label>
                  <p className="text-sm font-medium mt-1">
                    {new Date(integration.lastSync).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <Label className="text-sm text-gray-500">Version</Label>
                  <p className="text-sm font-medium mt-1">{integration.version}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Configuration Form */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Configuration Settings</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Integration Name</Label>
                <Input
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="syncFrequency">Sync Frequency</Label>
                <Select value={formData.syncFrequency} onValueChange={(value) => setFormData(prev => ({ ...prev, syncFrequency: value }))}>
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="realtime">Real-time</SelectItem>
                    <SelectItem value="hourly">Every Hour</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="manual">Manual Only</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="apiUrl">API URL</Label>
              <Input
                id="apiUrl"
                name="apiUrl"
                type="url"
                value={formData.apiUrl}
                onChange={handleInputChange}
                className="mt-1"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="apiKey">API Key</Label>
                <Input
                  id="apiKey"
                  name="apiKey"
                  type="password"
                  value={formData.apiKey}
                  onChange={handleInputChange}
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="mt-1"
                />
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="space-y-4">
              <h4 className="text-md font-semibold">Advanced Settings</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="autoSync">Auto Sync</Label>
                    <p className="text-sm text-gray-500">Automatically sync data</p>
                  </div>
                  <Switch
                    id="autoSync"
                    checked={formData.autoSync}
                    onCheckedChange={(checked) => handleSwitchChange('autoSync', checked)}
                    aria-label="Auto Sync"
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="syncOnStartup">Sync on Startup</Label>
                    <p className="text-sm text-gray-500">Sync when system starts</p>
                  </div>
                  <Switch
                    id="syncOnStartup"
                    checked={formData.syncOnStartup}
                    onCheckedChange={(checked) => handleSwitchChange('syncOnStartup', checked)}
                    aria-label="Sync on Startup"
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="retryOnError">Retry on Error</Label>
                    <p className="text-sm text-gray-500">Retry failed syncs</p>
                  </div>
                  <Switch
                    id="retryOnError"
                    checked={formData.retryOnError}
                    onCheckedChange={(checked) => handleSwitchChange('retryOnError', checked)}
                    aria-label="Retry on Error"
                  />
                </div>
                
                <div>
                  <Label htmlFor="maxRetries">Max Retries</Label>
                  <Input
                    id="maxRetries"
                    name="maxRetries"
                    type="number"
                    min="1"
                    max="10"
                    value={formData.maxRetries}
                    onChange={handleInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="timeout">Timeout (seconds)</Label>
                  <Input
                    id="timeout"
                    name="timeout"
                    type="number"
                    min="5"
                    max="300"
                    value={formData.timeout}
                    onChange={handleInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <Label htmlFor="batchSize">Batch Size</Label>
                  <Input
                    id="batchSize"
                    name="batchSize"
                    type="number"
                    min="1"
                    max="1000"
                    value={formData.batchSize}
                    onChange={handleInputChange}
                    className="mt-1"
                  />
                </div>
              </div>
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <textarea
                id="description"
                name="description"
                rows={3}
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Enter a description for this integration"
                className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Test Connection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TestTube className="h-5 w-5" />
                Test Connection
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Test the connection to ensure your API credentials are working correctly.
              </p>
              <Button
                onClick={handleTestConnection}
                disabled={isTesting}
                variant="outline"
                className="flex items-center gap-2"
              >
                {isTesting ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <TestTube className="h-4 w-4" />
                )}
                {isTesting ? 'Testing...' : 'Test Connection'}
              </Button>
            </CardContent>
          </Card>

          {successMessage && (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{successMessage}</AlertDescription>
            </Alert>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter className="flex gap-2">
          <Button 
            type="button" 
            variant="destructive" 
            onClick={() => setShowDeleteConfirm(true)}
            className="flex items-center gap-2"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </Button>
          <div className="flex-1" />
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleSave}
            disabled={isLoading}
            className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg"
          >
            {isLoading ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogFooter>

        {/* Delete Confirmation Dialog */}
        <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Integration</DialogTitle>
            </DialogHeader>
            <div className="py-4">
              <p className="text-gray-600">
                Are you sure you want to delete the <strong>{integration.name}</strong> integration? 
                This action cannot be undone and will stop all data synchronization.
              </p>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowDeleteConfirm(false)}>
                Cancel
              </Button>
              <Button 
                variant="destructive"
                onClick={handleDelete}
                disabled={isLoading}
              >
                {isLoading ? 'Deleting...' : 'Delete Integration'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </DialogContent>
    </Dialog>
  )
}
