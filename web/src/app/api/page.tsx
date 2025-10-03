'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Code, 
  Key, 
  BookOpen, 
  Zap,
  Shield,
  Globe,
  Terminal,
  Copy,
  ExternalLink
} from 'lucide-react'

export default function APIPage() {
  const endpoints = [
    {
      method: 'POST',
      path: '/api/v1/invoices/process',
      description: 'Process and extract data from invoice documents',
      parameters: ['file', 'options'],
      response: 'InvoiceData'
    },
    {
      method: 'GET',
      path: '/api/v1/invoices/{id}',
      description: 'Retrieve invoice data by ID',
      parameters: ['id'],
      response: 'InvoiceData'
    },
    {
      method: 'POST',
      path: '/api/v1/invoices/{id}/approve',
      description: 'Approve a pending invoice',
      parameters: ['id', 'approver_id'],
      response: 'ApprovalResult'
    },
    {
      method: 'GET',
      path: '/api/v1/analytics/summary',
      description: 'Get processing analytics and statistics',
      parameters: ['date_range', 'filters'],
      response: 'AnalyticsData'
    },
    {
      method: 'POST',
      path: '/api/v1/integrations/erp/sync',
      description: 'Sync data with external ERP system',
      parameters: ['erp_type', 'credentials'],
      response: 'SyncResult'
    }
  ]

  const codeExamples = [
    {
      language: 'JavaScript',
      title: 'Process Invoice',
      code: `const response = await fetch('https://api.aierpsaas.com/v1/invoices/process', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    file: 'base64_encoded_file',
    options: {
      extract_tables: true,
      validate_amounts: true
    }
  })
});

const result = await response.json();
console.log(result);`
    },
    {
      language: 'Python',
      title: 'Get Invoice Data',
      code: `import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.aierpsaas.com/v1/invoices/12345',
    headers=headers
)

invoice_data = response.json()
print(invoice_data)`
    },
    {
      language: 'cURL',
      title: 'Approve Invoice',
      code: `curl -X POST \\
  'https://api.aierpsaas.com/v1/invoices/12345/approve' \\
  -H 'Authorization: Bearer YOUR_API_KEY' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "approver_id": "user_123",
    "comments": "Approved for payment"
  }'`
    }
  ]

  const sdkLanguages = [
    { name: 'JavaScript/Node.js', version: '2.1.0', status: 'stable' },
    { name: 'Python', version: '1.8.2', status: 'stable' },
    { name: 'PHP', version: '1.5.1', status: 'stable' },
    { name: 'Java', version: '1.3.0', status: 'beta' },
    { name: 'C#/.NET', version: '1.2.0', status: 'beta' },
    { name: 'Go', version: '1.0.5', status: 'stable' }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">API Documentation</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Integrate AI-powered invoice processing into your applications with our comprehensive REST API. 
            Built for developers, by developers.
          </p>
        </div>

        {/* Quick Start */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Quick Start</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Key className="h-6 w-6 mr-2 text-blue-600" />
                  Get API Key
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Sign up for a free account and generate your API key from the dashboard.
                </p>
                <Button className="w-full">
                  Get Started
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Code className="h-6 w-6 mr-2 text-green-600" />
                  Choose SDK
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Use our official SDKs for faster integration with your preferred language.
                </p>
                <Button variant="outline" className="w-full">
                  View SDKs
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="h-6 w-6 mr-2 text-purple-600" />
                  Start Building
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Process your first invoice in under 5 minutes with our quick start guide.
                </p>
                <Button variant="outline" className="w-full">
                  Quick Start Guide
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* API Endpoints */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">API Endpoints</h2>
          <div className="space-y-4">
            {endpoints.map((endpoint, index) => (
              <Card key={index}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      <Badge className={`mr-3 ${
                        endpoint.method === 'GET' ? 'bg-green-100 text-green-800' :
                        endpoint.method === 'POST' ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {endpoint.method}
                      </Badge>
                      <code className="text-lg font-mono">{endpoint.path}</code>
                    </div>
                    <Button variant="ghost" size="sm">
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  <p className="text-gray-600 mb-3">{endpoint.description}</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="text-sm text-gray-500">Parameters:</span>
                    {endpoint.parameters.map((param, paramIndex) => (
                      <Badge key={paramIndex} variant="outline" className="text-xs">
                        {param}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Code Examples */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Code Examples</h2>
          <div className="space-y-8">
            {codeExamples.map((example, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Terminal className="h-5 w-5 mr-2" />
                    {example.title} - {example.language}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                    <code>{example.code}</code>
                  </pre>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* SDKs */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Official SDKs</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sdkLanguages.map((sdk, index) => (
              <Card key={index}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">{sdk.name}</h3>
                    <Badge className={
                      sdk.status === 'stable' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }>
                      {sdk.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">Version {sdk.version}</p>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline">
                      <ExternalLink className="h-4 w-4 mr-1" />
                      Docs
                    </Button>
                    <Button size="sm" variant="outline">
                      <Code className="h-4 w-4 mr-1" />
                      GitHub
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Authentication */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Authentication</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="h-6 w-6 mr-2 text-blue-600" />
                  API Keys
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  All API requests require authentication using your API key. Include it in the 
                  Authorization header of your requests.
                </p>
                <div className="bg-gray-100 p-3 rounded">
                  <code className="text-sm">Authorization: Bearer YOUR_API_KEY</code>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Globe className="h-6 w-6 mr-2 text-green-600" />
                  Rate Limits
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Free Plan:</span>
                    <span className="text-sm font-medium">100 requests/hour</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Pro Plan:</span>
                    <span className="text-sm font-medium">1,000 requests/hour</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Enterprise:</span>
                    <span className="text-sm font-medium">Unlimited</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Support */}
        <div className="text-center bg-blue-50 rounded-lg p-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Need Help?</h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Our developer support team is here to help you integrate our API successfully.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="flex items-center">
              <BookOpen className="h-5 w-5 mr-2" />
              View Full Documentation
            </Button>
            <Button variant="outline" size="lg" className="flex items-center">
              <ExternalLink className="h-5 w-5 mr-2" />
              Contact Support
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
