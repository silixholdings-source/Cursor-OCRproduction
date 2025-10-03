'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { testApiConnection, checkHealth, uploadFile, getInvoices } from '@/lib/api'
import { Upload, CheckCircle, XCircle, RefreshCw } from 'lucide-react'

export default function TestPage() {
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('loading')
  const [healthData, setHealthData] = useState<any>(null)
  const [testResults, setTestResults] = useState<any[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  useEffect(() => {
    testConnection()
  }, [])

  const testConnection = async () => {
    setApiStatus('loading')
    try {
      const result = await testApiConnection()
      if (result.success) {
        setApiStatus('connected')
        setHealthData(result.health)
      } else {
        setApiStatus('error')
      }
    } catch (error) {
      setApiStatus('error')
      console.error('Connection test failed:', error)
    }
  }

  const runTests = async () => {
    const tests = [
      {
        name: 'Health Check',
        test: async () => {
          const health = await checkHealth()
          return { success: true, data: health }
        }
      },
      {
        name: 'Get Invoices',
        test: async () => {
          const invoices = await getInvoices()
          return { success: true, data: invoices }
        }
      }
    ]

    const results = []
    for (const test of tests) {
      try {
        const result = await test.test()
        results.push({ name: test.name, success: true, data: result.data })
      } catch (error) {
        results.push({ name: test.name, success: false, error: error.message })
      }
    }

    setTestResults(results)
  }

  const handleFileUpload = async () => {
    if (!selectedFile) return

    try {
      const result = await uploadFile(selectedFile)
      setTestResults(prev => [...prev, { 
        name: 'File Upload', 
        success: true, 
        data: result 
      }])
    } catch (error) {
      setTestResults(prev => [...prev, { 
        name: 'File Upload', 
        success: false, 
        error: error.message 
      }])
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">API Connection Test</h1>
        
        {/* API Status */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              API Status
              {apiStatus === 'loading' && <RefreshCw className="w-4 h-4 animate-spin" />}
              {apiStatus === 'connected' && <CheckCircle className="w-4 h-4 text-green-500" />}
              {apiStatus === 'error' && <XCircle className="w-4 h-4 text-red-500" />}
            </CardTitle>
            <CardDescription>
              Backend API connection status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Badge variant={apiStatus === 'connected' ? 'default' : 'destructive'}>
                {apiStatus === 'loading' && 'Testing...'}
                {apiStatus === 'connected' && 'Connected'}
                {apiStatus === 'error' && 'Error'}
              </Badge>
              <Button onClick={testConnection} variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </Button>
            </div>
            
            {healthData && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold mb-2">Health Data:</h4>
                <pre className="text-sm">{JSON.stringify(healthData, null, 2)}</pre>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Test Results */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
            <CardDescription>
              Run tests to verify API functionality
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Button onClick={runTests} className="w-full">
                Run All Tests
              </Button>
              
              {testResults.map((result, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-2">
                    {result.success ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-500" />
                    )}
                    <span className="font-medium">{result.name}</span>
                  </div>
                  <Badge variant={result.success ? 'default' : 'destructive'}>
                    {result.success ? 'Success' : 'Failed'}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* File Upload Test */}
        <Card>
          <CardHeader>
            <CardTitle>File Upload Test</CardTitle>
            <CardDescription>
              Test OCR file processing functionality
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.tiff"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              <Button 
                onClick={handleFileUpload} 
                disabled={!selectedFile}
                className="w-full"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload and Process File
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}