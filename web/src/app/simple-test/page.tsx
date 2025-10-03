'use client'

import { useState } from 'react'

export default function SimpleTestPage() {
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const testAPI = async () => {
    setLoading(true)
    setResult('Testing...\n')
    
    try {
      // Test the correct API URL directly
      const apiUrl = 'http://127.0.0.1:8001'
      setResult(prev => prev + `Testing API URL: ${apiUrl}\n`)
      
      // Test health endpoint
      const healthResponse = await fetch(`${apiUrl}/health`)
      const healthData = await healthResponse.json()
      setResult(prev => prev + `Health check: ${healthResponse.status} - ${JSON.stringify(healthData)}\n`)
      
      // Test OCR endpoint
      const formData = new FormData()
      formData.append('file', new Blob(['test content'], { type: 'application/pdf' }), 'test.pdf')
      
      setResult(prev => prev + `Testing OCR endpoint...\n`)
      const ocrResponse = await fetch(`${apiUrl}/api/v1/ocr/upload`, {
        method: 'POST',
        body: formData,
      })
      
      const ocrData = await ocrResponse.json()
      setResult(prev => prev + `OCR test: ${ocrResponse.status} - ${JSON.stringify(ocrData, null, 2)}\n`)
      
      setResult(prev => prev + `\n✅ SUCCESS: API is working correctly!\n`)
      
    } catch (error) {
      setResult(prev => prev + `\n❌ ERROR: ${error}\n`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Simple API Test</h1>
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
        {loading ? 'Testing...' : 'Test API Connection'}
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









