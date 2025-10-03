'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { notifications } from '@/lib/notifications'

export interface RealTimeConfig {
  endpoint: string
  interval?: number
  onUpdate?: (data: any) => void
  onError?: (error: Error) => void
  enabled?: boolean
}

export function useRealTime<T>(config: RealTimeConfig) {
  const [data, setData] = useState<T | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [error, setError] = useState<Error | null>(null)
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const fetchData = useCallback(async () => {
    if (!config.enabled) return

    try {
      // Cancel previous request if still pending
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }

      abortControllerRef.current = new AbortController()

      const response = await fetch(config.endpoint, {
        signal: abortControllerRef.current.signal,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const newData = await response.json()
      setData(newData)
      setLastUpdate(new Date())
      setError(null)
      setIsConnected(true)

      config.onUpdate?.(newData)
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return // Request was cancelled, ignore
      }

      const error = err instanceof Error ? err : new Error('Unknown error')
      setError(error)
      setIsConnected(false)
      config.onError?.(error)
    }
  }, [config])

  const startPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    // Initial fetch
    fetchData()

    // Set up polling
    intervalRef.current = setInterval(fetchData, config.interval || 30000)
  }, [fetchData, config.interval])

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    
    setIsConnected(false)
  }, [])

  const refresh = useCallback(() => {
    fetchData()
  }, [fetchData])

  useEffect(() => {
    if (config.enabled) {
      startPolling()
    } else {
      stopPolling()
    }

    return () => {
      stopPolling()
    }
  }, [config.enabled, startPolling, stopPolling])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling()
    }
  }, [stopPolling])

  return {
    data,
    isConnected,
    lastUpdate,
    error,
    refresh,
    startPolling,
    stopPolling
  }
}

/**
 * Hook for real-time invoice updates
 */
export function useRealTimeInvoices() {
  return useRealTime<any[]>({
    endpoint: '/api/v1/invoices/real-time',
    interval: 15000, // Update every 15 seconds
    enabled: true,
    onUpdate: (invoices) => {
      // Check for new invoices and notify
      const newInvoices = invoices.filter((invoice: any) => {
        const createdAt = new Date(invoice.createdAt)
        const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
        return createdAt > fiveMinutesAgo
      })

      newInvoices.forEach((invoice: any) => {
        notifications.invoiceProcessed(invoice.invoiceNumber, invoice.amount)
      })
    }
  })
}

/**
 * Hook for real-time approval updates
 */
export function useRealTimeApprovals() {
  return useRealTime<any[]>({
    endpoint: '/api/v1/approvals/real-time',
    interval: 10000, // Update every 10 seconds
    enabled: true,
    onUpdate: (approvals) => {
      // Check for status changes and notify
      approvals.forEach((approval: any) => {
        if (approval.statusChanged) {
          notifications.approvalStatusChanged(
            approval.vendor,
            approval.status,
            approval.amount
          )
        }
      })
    }
  })
}

/**
 * Hook for real-time system status
 */
export function useRealTimeSystemStatus() {
  return useRealTime<{
    status: 'healthy' | 'degraded' | 'down'
    services: Record<string, boolean>
    lastHealthCheck: string
  }>({
    endpoint: '/api/v1/health/detailed',
    interval: 60000, // Update every minute
    enabled: true,
    onUpdate: (status) => {
      if (status.status === 'degraded') {
        notifications.warning(
          'Some services are experiencing issues. Functionality may be limited.',
          'System Status'
        )
      } else if (status.status === 'down') {
        notifications.error(
          'System maintenance in progress. Please try again later.',
          'System Unavailable'
        )
      }
    }
  })
}


