'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Plug, 
  Save, 
  X, 
  Trash2, 
  CheckCircle, 
  AlertCircle,
  Loader2
} from 'lucide-react'
import { notifications } from '@/lib/notifications'
import { logger } from '@/lib/logger'

interface ERPIntegration {
  id: string
  name: string
  type: string
  status: 'connected' | 'disconnected' | 'error'
  config: {
    autoSync: boolean
    syncOnStartup: boolean
    retryOnError: boolean
    maxRetries: number
    timeout: number
    batchSize: number
    description: string
  }
}

export default function ERPConfigurationPage() {
  const router = useRouter()
  const [integration, setIntegration] = useState<ERPIntegration>({
    id: 'dynamics-gp-1',
    name: 'Microsoft Dynamics GP',
    type: 'dynamics-gp',
    status: 'connected',
    config: {
      autoSync: true,
      syncOnStartup: false,
      retryOnError: true,
      maxRetries: 3,
      timeout: 30,
      batchSize: 100,
      description: 'Microsoft Dynamics GP integration configuration'
    }
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [isTesting, setIsTesting] = useState(false)
  const [testResult, setTestResult] = useState<{
    success: boolean
    message: string
  } | null>(null)

  const handleConfigChange = (key: keyof ERPIntegration['config'], value: any) => {
    setIntegration(prev => ({
      ...prev,
      config: {
        ...prev.config,
        [key]: value
      }
    }))
  }

  const handleTestConnection = async () => {
    setIsTesting(true)
    setTestResult(null)
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'
      console.log('Testing connection to:', apiUrl)
      
      const response = await fetch(`${apiUrl}/erp/test-connection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          erp_type: integration.type,
          config: integration.config
        })
      })

      const result = await response.json()
      
      if (response.ok && result.status === 'success') {
        setTestResult({
          success: true,
          message: 'Connection test successful!'
        })
        notifications.success('Connection test passed', 'ERP Integration')
      } else {
        setTestResult({
          success: false,
          message: result.message || 'Connection test failed'
        })
        notifications.error('Connection test failed', 'ERP Integration')
      }
    } catch (error) {
      logger.error('Connection test error:', error)
      setTestResult({
        success: false,
        message: 'Failed to test connection'
      })
      notifications.error('Connection test failed', 'ERP Integration')
    } finally {
      setIsTesting(false)
    }
  }

  const handleSaveChanges = async () => {
    setIsLoading(true)
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'
      console.log('Saving to:', apiUrl)
      
      const response = await fetch(`${apiUrl}/erp/integrations/${integration.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(integration)
      })

      const result = await response.json()
      
      if (response.ok) {
        notifications.success('Configuration saved successfully', 'ERP Integration')
        
        // Close form and refresh page
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      } else {
        notifications.error('Failed to save configuration', 'ERP Integration')
      }
    } catch (error) {
      logger.error('Save configuration error:', error)
      notifications.error('Failed to save configuration', 'ERP Integration')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this integration?')) {
      return
    }

    setIsLoading(true)
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'
      const response = await fetch(`${apiUrl}/erp/integrations/${integration.id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        notifications.success('Integration deleted successfully', 'ERP Integration')
        router.push('/dashboard/erp')
      } else {
        notifications.error('Failed to delete integration', 'ERP Integration')
      }
    } catch (error) {
      logger.error('Delete integration error:', error)
      notifications.error('Failed to delete integration', 'ERP Integration')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    router.push('/dashboard/erp')
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">ERP Integration Configuration</h1>
        <p className="text-gray-600 mt-2">Configure your Microsoft Dynamics GP integration settings</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plug className="h-5 w-5" />
            Integration Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Auto Sync */}
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="autoSync" className="text-sm font-medium">Auto Sync</Label>
              <p className="text-sm text-gray-500">Automatically sync data</p>
            </div>
            <Switch
              id="autoSync"
              checked={integration.config.autoSync}
              onCheckedChange={(checked) => handleConfigChange('autoSync', checked)}
            />
          </div>

          {/* Sync on Startup */}
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="syncOnStartup" className="text-sm font-medium">Sync on Startup</Label>
              <p className="text-sm text-gray-500">Sync when system starts</p>
            </div>
            <Switch
              id="syncOnStartup"
              checked={integration.config.syncOnStartup}
              onCheckedChange={(checked) => handleConfigChange('syncOnStartup', checked)}
            />
          </div>

          {/* Retry on Error */}
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="retryOnError" className="text-sm font-medium">Retry on Error</Label>
              <p className="text-sm text-gray-500">Retry failed syncs</p>
            </div>
            <Switch
              id="retryOnError"
              checked={integration.config.retryOnError}
              onCheckedChange={(checked) => handleConfigChange('retryOnError', checked)}
            />
          </div>

          {/* Max Retries */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="maxRetries" className="text-sm font-medium">Max Retries</Label>
              <Input
                id="maxRetries"
                type="number"
                value={integration.config.maxRetries}
                onChange={(e) => handleConfigChange('maxRetries', parseInt(e.target.value))}
                min="1"
                max="10"
              />
            </div>
            <div>
              <Label htmlFor="timeout" className="text-sm font-medium">Timeout (seconds)</Label>
              <Input
                id="timeout"
                type="number"
                value={integration.config.timeout}
                onChange={(e) => handleConfigChange('timeout', parseInt(e.target.value))}
                min="5"
                max="300"
              />
            </div>
          </div>

          {/* Batch Size */}
          <div>
            <Label htmlFor="batchSize" className="text-sm font-medium">Batch Size</Label>
            <Input
              id="batchSize"
              type="number"
              value={integration.config.batchSize}
              onChange={(e) => handleConfigChange('batchSize', parseInt(e.target.value))}
              min="1"
              max="1000"
            />
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="description" className="text-sm font-medium">Description</Label>
            <Textarea
              id="description"
              value={integration.config.description}
              onChange={(e) => handleConfigChange('description', e.target.value)}
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Test Connection */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Test Connection</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 mb-4">
            Test the connection to ensure your API credentials are working correctly.
          </p>
          
          {testResult && (
            <Alert className={`mb-4 ${testResult.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
              {testResult.success ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-600" />
              )}
              <AlertDescription className={testResult.success ? 'text-green-800' : 'text-red-800'}>
                {testResult.message}
              </AlertDescription>
            </Alert>
          )}

          <Button
            onClick={handleTestConnection}
            disabled={isTesting}
            className="w-full sm:w-auto"
          >
            {isTesting ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Plug className="mr-2 h-4 w-4" />
            )}
            Test Connection
          </Button>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 mt-6">
        <Button
          onClick={handleDelete}
          variant="destructive"
          disabled={isLoading}
          className="sm:order-1"
        >
          <Trash2 className="mr-2 h-4 w-4" />
          Delete
        </Button>
        
        <Button
          onClick={handleCancel}
          variant="outline"
          disabled={isLoading}
          className="sm:order-2"
        >
          <X className="mr-2 h-4 w-4" />
          Cancel
        </Button>
        
        <Button
          onClick={handleSaveChanges}
          disabled={isLoading}
          className="sm:order-3 sm:ml-auto"
        >
          {isLoading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          Save Changes
        </Button>
      </div>
    </div>
  )
}