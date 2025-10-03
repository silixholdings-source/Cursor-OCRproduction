'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export default function AzureCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login } = useAuth()
  
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing')
  const [message, setMessage] = useState('Processing Azure AD authentication...')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleAzureCallback = async () => {
      try {
        const code = searchParams.get('code')
        const state = searchParams.get('state')
        const error = searchParams.get('error')
        const errorDescription = searchParams.get('error_description')

        // Check for OAuth errors
        if (error) {
          throw new Error(errorDescription || error)
        }

        if (!code || !state) {
          throw new Error('Missing authorization code or state parameter')
        }

        setMessage('Authenticating with Azure AD...')

        // Call backend to handle Azure AD callback
        const response = await fetch(`/api/v1/auth/azure/callback?code=${code}&state=${state}`)
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Azure AD authentication failed')
        }

        const authData = await response.json()
        
        setMessage('Authentication successful! Redirecting...')
        setStatus('success')

        // Store tokens and user data
        localStorage.setItem('auth_token', authData.access_token)
        localStorage.setItem('refresh_token', authData.refresh_token)
        
        // Update auth context (if using context-based auth)
        // await login(authData.user.email, '', 'azure_ad')

        // Redirect to dashboard
        setTimeout(() => {
          router.push('/dashboard')
        }, 2000)

      } catch (error) {
        console.error('Azure AD authentication error:', error)
        setStatus('error')
        setError(error instanceof Error ? error.message : 'Authentication failed')
        setMessage('Azure AD authentication failed')
      }
    }

    handleAzureCallback()
  }, [searchParams, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
            {status === 'processing' && <Loader2 className="h-6 w-6 animate-spin text-blue-600" />}
            {status === 'success' && <CheckCircle className="h-6 w-6 text-green-600" />}
            {status === 'error' && <XCircle className="h-6 w-6 text-red-600" />}
          </div>
          
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Azure AD Authentication
          </h2>
          
          <p className="mt-2 text-sm text-gray-600">
            {message}
          </p>
        </div>

        {status === 'error' && error && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>
              {error}
            </AlertDescription>
          </Alert>
        )}

        {status === 'error' && (
          <div className="text-center">
            <Button 
              onClick={() => router.push('/auth/login')}
              variant="outline"
              className="w-full"
            >
              Back to Login
            </Button>
          </div>
        )}

        {status === 'success' && (
          <div className="text-center">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <p className="text-sm text-green-700">
                Successfully authenticated with Azure AD!
              </p>
              <p className="text-xs text-green-600 mt-1">
                Redirecting to your dashboard...
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}


