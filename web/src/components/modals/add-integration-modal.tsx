'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  Database, 
  CheckCircle, 
  AlertTriangle, 
  ExternalLink,
  Info,
  Zap,
  Shield,
  Clock
} from 'lucide-react'

interface AddIntegrationModalProps {
  isOpen: boolean
  onClose: () => void
  onIntegrationAdded?: (integration: any) => void
}

const erpSystems = [
  {
    id: 'sap',
    name: 'SAP ERP',
    description: 'Enterprise resource planning software by SAP',
    logo: 'SAP',
    color: 'bg-blue-100 text-blue-600',
    features: ['Real-time sync', 'Multi-currency', 'Advanced reporting', 'API integration'],
    setupTime: '15-30 minutes',
    difficulty: 'Advanced'
  },
  {
    id: 'oracle',
    name: 'Oracle NetSuite',
    description: 'Cloud-based business management suite',
    logo: 'Oracle',
    color: 'bg-red-100 text-red-600',
    features: ['Cloud-based', 'Scalable', 'Custom fields', 'Workflow automation'],
    setupTime: '10-20 minutes',
    difficulty: 'Intermediate'
  },
  {
    id: 'salesforce',
    name: 'Salesforce CRM',
    description: 'Customer relationship management platform',
    logo: 'SF',
    color: 'bg-blue-100 text-blue-600',
    features: ['CRM integration', 'Lead management', 'Sales tracking', 'Custom objects'],
    setupTime: '5-15 minutes',
    difficulty: 'Easy'
  },
  {
    id: 'quickbooks',
    name: 'QuickBooks Online',
    description: 'Accounting and financial management software',
    logo: 'QB',
    color: 'bg-green-100 text-green-600',
    features: ['Accounting sync', 'Invoice management', 'Tax reporting', 'Bank integration'],
    setupTime: '5-10 minutes',
    difficulty: 'Easy'
  },
  {
    id: 'microsoft',
    name: 'Microsoft Dynamics 365',
    description: 'Microsoft\'s cloud-based business applications',
    logo: 'MS',
    color: 'bg-blue-100 text-blue-600',
    features: ['Microsoft ecosystem', 'Power BI integration', 'Azure integration', 'Custom workflows'],
    setupTime: '20-40 minutes',
    difficulty: 'Advanced'
  },
  {
    id: 'workday',
    name: 'Workday',
    description: 'Human capital management and financial management',
    logo: 'WD',
    color: 'bg-orange-100 text-orange-600',
    features: ['HCM integration', 'Financial management', 'Analytics', 'Mobile access'],
    setupTime: '25-45 minutes',
    difficulty: 'Advanced'
  }
]

export function AddIntegrationModal({ isOpen, onClose, onIntegrationAdded }: AddIntegrationModalProps) {
  const [selectedSystem, setSelectedSystem] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    apiUrl: '',
    apiKey: '',
    username: '',
    password: '',
    syncFrequency: 'hourly',
    description: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [currentStep, setCurrentStep] = useState(1)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    setError('')
  }

  const handleSystemSelect = (systemId: string) => {
    setSelectedSystem(systemId)
    const system = erpSystems.find(s => s.id === systemId)
    if (system) {
      setFormData(prev => ({ 
        ...prev, 
        name: system.name,
        description: system.description
      }))
    }
    setError('')
  }

  const validateForm = () => {
    if (!selectedSystem) {
      setError('Please select an ERP system')
      return false
    }
    if (!formData.apiUrl.trim()) {
      setError('API URL is required')
      return false
    }
    if (!formData.apiKey.trim()) {
      setError('API Key is required')
      return false
    }
    return true
  }

  const handleNext = () => {
    if (currentStep === 1) {
      if (!selectedSystem) {
        setError('Please select an ERP system')
        return
      }
      setCurrentStep(2)
    }
  }

  const handleBack = () => {
    if (currentStep === 2) {
      setCurrentStep(1)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setIsLoading(true)
    setError('')

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const newIntegration = {
        id: `${selectedSystem.toUpperCase()}${Date.now()}`,
        name: formData.name,
        status: 'connected',
        lastSync: new Date().toISOString(),
        syncFrequency: formData.syncFrequency,
        recordsSynced: 0,
        lastError: null,
        version: 'Latest',
        apiUrl: formData.apiUrl,
        apiKey: formData.apiKey
      }
      
      if (onIntegrationAdded) {
        onIntegrationAdded(newIntegration)
      }
      
      // Reset form
      setSelectedSystem('')
      setFormData({
        name: '',
        apiUrl: '',
        apiKey: '',
        username: '',
        password: '',
        syncFrequency: 'hourly',
        description: ''
      })
      setCurrentStep(1)
      onClose()
    } catch (err) {
      setError('Failed to add integration. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const selectedSystemData = erpSystems.find(s => s.id === selectedSystem)

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Database className="h-6 w-6" />
            Add ERP Integration
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Step Indicator */}
          <div className="flex items-center justify-center space-x-4">
            <div className={`flex items-center ${currentStep >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                1
              </div>
              <span className="ml-2 text-sm font-medium">Select System</span>
            </div>
            <div className="w-8 h-0.5 bg-gray-200"></div>
            <div className={`flex items-center ${currentStep >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                2
              </div>
              <span className="ml-2 text-sm font-medium">Configure</span>
            </div>
          </div>

          {/* Step 1: Select ERP System */}
          {currentStep === 1 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Choose Your ERP System</h3>
              <div className="grid md:grid-cols-2 gap-4">
                {erpSystems.map((system) => (
                  <Card 
                    key={system.id}
                    className={`cursor-pointer transition-all ${
                      selectedSystem === system.id 
                        ? 'ring-2 ring-blue-500 border-blue-500' 
                        : 'hover:shadow-md'
                    }`}
                    onClick={() => handleSystemSelect(system.id)}
                  >
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className={`w-12 h-12 rounded-lg ${system.color} flex items-center justify-center font-bold`}>
                          {system.logo}
                        </div>
                        <Badge className={system.difficulty === 'Easy' ? 'bg-green-100 text-green-800' : 
                                         system.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' : 
                                         'bg-red-100 text-red-800'}>
                          {system.difficulty}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg">{system.name}</CardTitle>
                      <p className="text-sm text-gray-600">{system.description}</p>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex items-center text-sm text-gray-600">
                          <Clock className="h-4 w-4 mr-2" />
                          Setup time: {system.setupTime}
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {system.features.map((feature, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {feature}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Configuration */}
          {currentStep === 2 && selectedSystemData && (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Configure {selectedSystemData.name}</h3>
                
                {/* Selected System Info */}
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg ${selectedSystemData.color} flex items-center justify-center font-bold`}>
                      {selectedSystemData.logo}
                    </div>
                    <div>
                      <h4 className="font-semibold">{selectedSystemData.name}</h4>
                      <p className="text-sm text-gray-600">{selectedSystemData.description}</p>
                    </div>
                  </div>
                </div>

                {/* Configuration Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Integration Name</Label>
                    <Input
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      className="mt-1"
                      required
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
                    placeholder="https://api.example.com"
                    value={formData.apiUrl}
                    onChange={handleInputChange}
                    className="mt-1"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="apiKey">API Key</Label>
                    <Input
                      id="apiKey"
                      name="apiKey"
                      type="password"
                      placeholder="Enter your API key"
                      value={formData.apiKey}
                      onChange={handleInputChange}
                      className="mt-1"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="username">Username (Optional)</Label>
                    <Input
                      id="username"
                      name="username"
                      placeholder="Enter username"
                      value={formData.username}
                      onChange={handleInputChange}
                      className="mt-1"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="description">Description (Optional)</Label>
                  <textarea
                    id="description"
                    name="description"
                    rows={3}
                    placeholder="Enter a description for this integration"
                    value={formData.description}
                    onChange={handleInputChange}
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Security Notice */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-medium text-blue-900">Security Notice</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      Your API credentials are encrypted and stored securely. We never store your passwords in plain text.
                    </p>
                  </div>
                </div>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </form>
          )}
        </div>

        <DialogFooter className="flex gap-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          {currentStep === 1 ? (
            <Button onClick={handleNext} disabled={!selectedSystem}>
              Next
            </Button>
          ) : (
            <>
              <Button type="button" variant="outline" onClick={handleBack}>
                Back
              </Button>
              <Button 
                type="submit" 
                onClick={handleSubmit}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg"
              >
                {isLoading ? 'Adding...' : 'Add Integration'}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}




