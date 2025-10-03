'use client'

import { useState, useCallback } from 'react'
import { useToast } from '@/lib/toast-notifications'

interface AsyncActionOptions {
  successMessage?: string
  errorMessage?: string
  loadingMessage?: string
  onSuccess?: (result: any) => void
  onError?: (error: any) => void
  confirmAction?: boolean
  confirmMessage?: string
}

export function useAsyncAction<T = any>(
  action: (...args: any[]) => Promise<T>,
  options: AsyncActionOptions = {}
) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const { success: showSuccess, error: showError } = useToast()

  const execute = useCallback(async (...args: any[]) => {
    // Confirmation dialog if required
    if (options.confirmAction && options.confirmMessage) {
      if (!window.confirm(options.confirmMessage)) {
        return
      }
    }

    setIsLoading(true)
    setError(null)
    setSuccess(false)

    try {
      const result = await action(...args)
      
      setSuccess(true)
      
      // Show success notification
      if (options.successMessage) {
        showSuccess('Success', options.successMessage)
      }
      
      // Call success callback
      options.onSuccess?.(result)
      
      // Reset success state after delay
      setTimeout(() => setSuccess(false), 2000)
      
      return result
    } catch (err: any) {
      const errorMessage = err.message || options.errorMessage || 'An error occurred'
      setError(errorMessage)
      
      // Show error notification
      showError('Error', errorMessage)
      
      // Call error callback
      options.onError?.(err)
      
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [action, options, showSuccess, showError])

  const reset = useCallback(() => {
    setIsLoading(false)
    setError(null)
    setSuccess(false)
  }, [])

  return {
    execute,
    isLoading,
    error,
    success,
    reset
  }
}

