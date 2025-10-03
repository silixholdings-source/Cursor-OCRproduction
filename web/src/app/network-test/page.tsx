'use client'

import { useState } from 'react'

export default function NetworkTestPage() {
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const testBothURLs = async () => {
    setLoading(true)
    setResult('Testing both localhost and 127.0.0.1...\n\n')
    
    const urls = [
      'http://localhost:8001',
      'http://127.0.0.1:8001'
    ]
    
    for (const url of urls) {
      try {
        setResult(prev => prev + `Testing ${url}...\n`)
        
        const response = await fetch(`${url}/health`)
        setResult(prev => prev + `  Status: ${response.status}\n`)
        
        if (response.ok) {
          const data = await response.json()
          setResult(prev => prev + `  Data: ${JSON.stringify(data)}\n`)
          setResult(prev => prev + `  ✅ SUCCESS with ${url}\n\n`)
        } else {
          setResult(prev => prev + `  ❌ FAILED with ${url} - Status: ${response.status}\n\n`)
        }
      } catch (error) {
        setResult(prev => prev + `  ❌ ERROR with ${url}: ${error}\n\n`)
      }
    }
    
    setLoading(false)
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Network Test - Both URLs</h1>
      <button 
        onClick={testBothURLs} 
        disabled={loading}
        style={{ 
          padding: '10px 20px', 
          fontSize: '16px',
          backgroundColor: loading ? '#ccc' : '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Testing...' : 'Test Both URLs'}
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









