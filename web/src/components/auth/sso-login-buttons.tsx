'use client'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useState } from 'react'
import { Loader2 } from 'lucide-react'

export function SSOLoginButtons() {
  const [loading, setLoading] = useState<string | null>(null)

  const handleSSOLogin = async (provider: string) => {
    setLoading(provider)
    try {
      // In a real implementation, this would redirect to the SSO provider
      // For demo purposes, we'll simulate the process
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Simulate successful login
      console.log(`${provider} SSO login initiated`)
    } catch (error) {
      console.error(`${provider} SSO login failed:`, error)
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3">
        <Button
          variant="outline"
          onClick={() => handleSSOLogin('azure')}
          disabled={loading === 'azure'}
          className="w-full"
        >
          {loading === 'azure' ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
              <path fill="currentColor" d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zM24 11.4H12.6V0H24v11.4z"/>
            </svg>
          )}
          Microsoft Azure AD
          <Badge variant="secondary" className="ml-2 text-xs">Enterprise</Badge>
        </Button>

        <Button
          variant="outline"
          onClick={() => handleSSOLogin('google')}
          disabled={loading === 'google'}
          className="w-full"
        >
          {loading === 'google' ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
          )}
          Google Workspace
        </Button>

        <Button
          variant="outline"
          onClick={() => handleSSOLogin('okta')}
          disabled={loading === 'okta'}
          className="w-full"
        >
          {loading === 'okta' ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
            </svg>
          )}
          Okta
          <Badge variant="secondary" className="ml-2 text-xs">Enterprise</Badge>
        </Button>
      </div>

      <p className="text-xs text-muted-foreground text-center">
        SSO integration requires enterprise plan
      </p>
    </div>
  )
}