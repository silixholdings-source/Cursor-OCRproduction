'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function TestConnectionPage() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const testConnection = async () => {
    setLoading(true)
    setResult(null)

    try {
      // Test the exact URL that the invoice upload uses
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8001'
      const healthUrl = `${apiUrl}/health`
      const ocrUrl = `${apiUrl}/api/v1/ocr/upload`
      
      console.log('Testing URLs:')
      console.log('Health URL:', healthUrl)
      console.log('OCR URL:', ocrUrl)
      
      // Test health endpoint
      const healthResponse = await fetch(healthUrl)
      const healthData = await healthResponse.json()
      
      // Test OCR endpoint with a simple file
      const formData = new FormData()
      formData.append('file', new Blob(['test content'], { type: 'application/pdf' }), 'test.pdf')
      
      const ocrResponse = await fetch(ocrUrl, {
        method: 'POST',
        body: formData,
      })
      const ocrData = await ocrResponse.json()
      
      setResult({
        health: {
          url: healthUrl,
          status: healthResponse.status,
          data: healthData
        },
        ocr: {
          url: ocrUrl,
          status: ocrResponse.status,
          data: ocrData
        }
      })
      
    } catch (error) {
      setResult({
        error: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-8">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>API Connection Test</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <p><strong>Environment Variable:</strong> {process.env.NEXT_PUBLIC_API_URL || 'not set'}</p>
            <p><strong>Expected URL:</strong> http://127.0.0.1:8001</p>
          </div>
          
          <Button onClick={testConnection} disabled={loading} className="w-full">
            {loading ? 'Testing...' : 'Test API Connection'}
          </Button>

          {result && (
            <div className="space-y-4">
              {result.error ? (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <h3 className="font-semibold text-red-800 mb-2">Error:</h3>
                  <p className="text-red-700">{result.error}</p>
                  {result.stack && (
                    <pre className="text-xs text-red-600 mt-2 whitespace-pre-wrap">
                      {result.stack}
                    </pre>
                  )}
                </div>
              ) : (
                <>
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <h3 className="font-semibold text-green-800 mb-2">Health Check:</h3>
                    <p><strong>URL:</strong> {result.health.url}</p>
                    <p><strong>Status:</strong> {result.health.status}</p>
                    <pre className="text-sm text-green-700 mt-2 whitespace-pre-wrap">
                      {JSON.stringify(result.health.data, null, 2)}
                    </pre>
                  </div>
                  
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h3 className="font-semibold text-blue-800 mb-2">OCR Test:</h3>
                    <p><strong>URL:</strong> {result.ocr.url}</p>
                    <p><strong>Status:</strong> {result.ocr.status}</p>
                    <pre className="text-sm text-blue-700 mt-2 whitespace-pre-wrap">
                      {JSON.stringify(result.ocr.data, null, 2)}
                    </pre>
                  </div>
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}









