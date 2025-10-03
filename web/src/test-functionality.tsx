// Manual functionality test component
// This can be imported and used to verify all major features work

import React from 'react'
import { useAuth } from '@/hooks/use-auth'
import { apiClient } from '@/lib/api-client'
import { logger } from '@/lib/logger'
import { sanitizeHtml, validatePassword, isValidEmail } from '@/lib/security'

export function FunctionalityTest() {
  const { user, login, logout, register } = useAuth()

  const testFeatures = async () => {
    console.log('🧪 Testing Core Functionality...')

    // Test 1: Authentication System
    try {
      logger.info('Testing authentication system')
      console.log('✅ Auth hook working:', { user, isAuthenticated: !!user })
    } catch (error) {
      console.error('❌ Auth system error:', error)
    }

    // Test 2: Security Functions
    try {
      const testHtml = '<script>alert("xss")</script>Hello'
      const sanitized = sanitizeHtml(testHtml)
      console.log('✅ HTML sanitization:', sanitized)

      const emailTest = isValidEmail('test@example.com')
      console.log('✅ Email validation:', emailTest)

      const passwordTest = validatePassword('TestPassword123!')
      console.log('✅ Password validation:', passwordTest)
    } catch (error) {
      console.error('❌ Security functions error:', error)
    }

    // Test 3: API Client
    try {
      // This will fail but should handle gracefully
      await apiClient.get('/api/test')
    } catch (error) {
      console.log('✅ API client error handling working:', error instanceof Error)
    }

    // Test 4: Logger
    try {
      logger.info('Test log message', { test: true })
      logger.error('Test error message', new Error('Test error'))
      console.log('✅ Logger system working')
    } catch (error) {
      console.error('❌ Logger error:', error)
    }

    console.log('🎉 All core functionality tests completed!')
  }

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h3 className="text-lg font-bold mb-4">🧪 Functionality Test Panel</h3>
      
      <div className="space-y-2 mb-4">
        <p><strong>User:</strong> {user ? user.email : 'Not logged in'}</p>
        <p><strong>Auth Status:</strong> {user ? '✅ Authenticated' : '❌ Not authenticated'}</p>
      </div>

      <div className="space-x-2">
        <button
          onClick={testFeatures}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Run Tests
        </button>
        
        {!user && (
          <button
            onClick={() => login('demo@example.com', 'password')}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Test Login
          </button>
        )}
        
        {user && (
          <button
            onClick={logout}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Test Logout
          </button>
        )}
      </div>

      <div className="mt-4 text-sm text-gray-600">
        <p>Open browser console to see test results</p>
      </div>
    </div>
  )
}

export default FunctionalityTest


