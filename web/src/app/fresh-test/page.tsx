'use client'

import { useState } from 'react'

export default function FreshTestPage() {
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const testAPI = async () => {
    setLoading(true)
    setResult('Testing fresh API connection...\n')
    
    try {
      // Use the exact same URL as the backend
      const apiUrl = 'http://127.0.0.1:8001'
      setResult(prev => prev + `Testing API URL: ${apiUrl}\n`)
      
      // Test health endpoint
      setResult(prev => prev + `Testing health endpoint...\n`)
      const healthResponse = await fetch(`${apiUrl}/health`)
      setResult(prev => prev + `Health response status: ${healthResponse.status}\n`)
      
      if (!healthResponse.ok) {
        throw new Error(`Health check failed: ${healthResponse.status}`)
      }
      
      const healthData = await healthResponse.json()
      setResult(prev => prev + `Health data: ${JSON.stringify(healthData)}\n`)
      
      // Test OCR endpoint
      setResult(prev => prev + `Testing OCR endpoint...\n`)
      const formData = new FormData()
      formData.append('file', new Blob(['test content'], { type: 'application/pdf' }), 'test.pdf')
      
      const ocrResponse = await fetch(`${apiUrl}/api/v1/ocr/upload`, {
        method: 'POST',
        body: formData,
      })
      
      setResult(prev => prev + `OCR response status: ${ocrResponse.status}\n`)
      
      if (!ocrResponse.ok) {
        const errorText = await ocrResponse.text()
        throw new Error(`OCR request failed: ${ocrResponse.status} - ${errorText}`)
      }
      
      const ocrData = await ocrResponse.json()
      setResult(prev => prev + `OCR data: ${JSON.stringify(ocrData, null, 2)}\n`)
      
      setResult(prev => prev + `\n✅ SUCCESS: All tests passed!\n`)
      
    } catch (error) {
      setResult(prev => prev + `\n❌ ERROR: ${error}\n`)
      console.error('API test error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Fresh API Test (No Cache)</h1>
      <button 
        onClick={testAPI} 
        disabled={loading}
        style={{ 
          padding: '10px 20px', 
          fontSize: '16px',
          backgroundColor: loading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Testing...' : 'Test Fresh API Connection'}
      </button>
      
      <pre style={{ 
        marginTop: '20px', 
        padding: '10px', 
        backgroundColor: '#f5f5f5', 
        border: '1px solid #ddd',
        borderRadius: '4px',
        whiteSpace: 'pre-wrap',
        fontSize: '14px'
      }}>
        {result}
      </pre>
    </div>
  )
}









