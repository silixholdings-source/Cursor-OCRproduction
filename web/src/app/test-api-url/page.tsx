'use client'

import { useEffect, useState } from 'react'

export default function TestAPIURLPage() {
  const [apiUrl, setApiUrl] = useState<string>('')
  const [envVar, setEnvVar] = useState<string>('')

  useEffect(() => {
    // Get the API URL from the function
    const { getApiBaseUrl } = require('@/lib/api')
    const url = getApiBaseUrl()
    setApiUrl(url)
    
    // Get the raw environment variable
    setEnvVar(process.env.NEXT_PUBLIC_API_URL || 'not set')
  }, [])

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">API URL Test</h1>
      <div className="space-y-4">
        <div>
          <strong>Environment Variable (NEXT_PUBLIC_API_URL):</strong> {envVar}
        </div>
        <div>
          <strong>getApiBaseUrl() result:</strong> {apiUrl}
        </div>
        <div>
          <strong>Expected:</strong> http://127.0.0.1:8001
        </div>
      </div>
    </div>
  )
}









