'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function DebugOCRPage() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const testAPI = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      console.log('Testing API connection...')
      
      // Test health endpoint first
      const healthResponse = await fetch('http://127.0.0.1:8001/health')
      console.log('Health response:', healthResponse.status)
      
      if (!healthResponse.ok) {
        throw new Error(`Health check failed: ${healthResponse.status}`)
      }
      
      const healthData = await healthResponse.json()
      console.log('Health data:', healthData)
      
      // Test OCR endpoint
      const formData = new FormData()
      formData.append('file', new Blob(['fake pdf content'], { type: 'application/pdf' }), 'test.pdf')
      
      console.log('Making OCR request...')
      const ocrResponse = await fetch('http://127.0.0.1:8001/api/v1/ocr/upload', {
        method: 'POST',
        body: formData,
      })
      
      console.log('OCR response status:', ocrResponse.status)
      
      if (!ocrResponse.ok) {
        const errorText = await ocrResponse.text()
        throw new Error(`OCR request failed: ${ocrResponse.status} - ${errorText}`)
      }
      
      const ocrData = await ocrResponse.json()
      console.log('OCR data:', ocrData)
      
      setResult({
        health: healthData,
        ocr: ocrData
      })
      
    } catch (err) {
      console.error('Test failed:', err)
      setError(err instanceof Error ? err.message : 'Test failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-8">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>OCR Debug Page</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button onClick={testAPI} disabled={loading} className="w-full">
            {loading ? 'Testing...' : 'Test API Connection'}
          </Button>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800"><strong>Error:</strong> {error}</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">Health Check Result:</h3>
                <pre className="text-sm text-green-700 whitespace-pre-wrap">
                  {JSON.stringify(result.health, null, 2)}
                </pre>
              </div>
              
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">OCR Test Result:</h3>
                <pre className="text-sm text-blue-700 whitespace-pre-wrap">
                  {JSON.stringify(result.ocr, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}









