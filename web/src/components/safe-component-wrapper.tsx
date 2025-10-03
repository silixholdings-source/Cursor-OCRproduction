'use client'

import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface SafeComponentWrapperProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  componentName?: string
}

interface SafeComponentState {
  hasError: boolean
  error: Error | null
}

export class SafeComponentWrapper extends React.Component<
  SafeComponentWrapperProps,
  SafeComponentState
> {
  constructor(props: SafeComponentWrapperProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null
    }
  }

  static getDerivedStateFromError(error: Error): SafeComponentState {
    return {
      hasError: true,
      error
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error(`Error in ${this.props.componentName || 'component'}:`, error)
    console.error('Error info:', errorInfo)
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-red-800 mb-2">
            Component Error
          </h3>
          <p className="text-red-600 mb-4">
            {this.props.componentName || 'This component'} encountered an error and couldn't load properly.
          </p>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <div className="bg-red-100 p-3 rounded mb-4 text-left">
              <code className="text-xs text-red-800 break-all">
                {this.state.error.message}
              </code>
            </div>
          )}
          <Button onClick={this.handleRetry} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook version for functional components
export function useSafeData<T>(data: T | undefined | null, fallback: T): T {
  return data ?? fallback
}

// Safe array mapper
export function safeMap<T, R>(
  array: T[] | undefined | null,
  mapper: (item: T, index: number) => R,
  fallback: R[] = []
): R[] {
  if (!Array.isArray(array)) {
    return fallback
  }
  
  try {
    return array.map(mapper)
  } catch (error) {
    console.error('Error in safeMap:', error)
    return fallback
  }
}

// Safe object property access
export function safeGet<T>(
  obj: any,
  path: string,
  fallback: T
): T {
  try {
    const keys = path.split('.')
    let result = obj
    
    for (const key of keys) {
      if (result == null || typeof result !== 'object') {
        return fallback
      }
      result = result[key]
    }
    
    return result ?? fallback
  } catch {
    return fallback
  }
}

