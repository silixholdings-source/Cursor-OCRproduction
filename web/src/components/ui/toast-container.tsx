'use client'

import React, { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { X, CheckCircle, AlertTriangle, AlertCircle, Info } from 'lucide-react'
import { toast, ToastNotification } from '@/lib/toast-notifications'
import { cn } from '@/lib/utils'

const ToastIcon = ({ type }: { type: ToastNotification['type'] }) => {
  switch (type) {
    case 'success':
      return <CheckCircle className="h-5 w-5 text-green-600" />
    case 'error':
      return <AlertCircle className="h-5 w-5 text-red-600" />
    case 'warning':
      return <AlertTriangle className="h-5 w-5 text-yellow-600" />
    case 'info':
      return <Info className="h-5 w-5 text-blue-600" />
    default:
      return <Info className="h-5 w-5 text-gray-600" />
  }
}

const ToastItem = ({ notification, onRemove }: { 
  notification: ToastNotification
  onRemove: (id: string) => void 
}) => {
  const [isVisible, setIsVisible] = useState(false)
  const [isExiting, setIsExiting] = useState(false)

  useEffect(() => {
    // Trigger entrance animation
    const timer = setTimeout(() => setIsVisible(true), 50)
    return () => clearTimeout(timer)
  }, [])

  const handleRemove = () => {
    setIsExiting(true)
    setTimeout(() => onRemove(notification.id), 300)
  }

  const getToastStyles = (type: ToastNotification['type']) => {
    switch (type) {
      case 'success':
        return 'bg-white border-green-200 shadow-lg'
      case 'error':
        return 'bg-white border-red-200 shadow-lg'
      case 'warning':
        return 'bg-white border-yellow-200 shadow-lg'
      case 'info':
        return 'bg-white border-blue-200 shadow-lg'
      default:
        return 'bg-white border-gray-200 shadow-lg'
    }
  }

  return (
    <div
      className={cn(
        "flex items-start space-x-3 p-4 rounded-lg border transition-all duration-300 transform",
        getToastStyles(notification.type),
        isVisible && !isExiting ? "translate-x-0 opacity-100" : "translate-x-full opacity-0",
        isExiting && "translate-x-full opacity-0"
      )}
    >
      <ToastIcon type={notification.type} />
      
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-semibold text-gray-900">{notification.title}</h4>
        <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
        
        {notification.action && (
          <button
            onClick={notification.action.onClick}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium mt-2 underline"
          >
            {notification.action.label}
          </button>
        )}
      </div>
      
      <button
        onClick={handleRemove}
        className="flex-shrink-0 p-1 rounded-md hover:bg-gray-100 transition-colors"
        aria-label="Dismiss notification"
      >
        <X className="h-4 w-4 text-gray-400" />
      </button>
    </div>
  )
}

export function ToastContainer() {
  const [notifications, setNotifications] = useState<ToastNotification[]>([])
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const unsubscribe = toast.subscribe(setNotifications)
    return unsubscribe
  }, [])

  if (!mounted) return null

  if (notifications.length === 0) return null

  return createPortal(
    <div className="fixed top-4 right-4 z-50 space-y-3 max-w-sm w-full">
      {notifications.map((notification) => (
        <ToastItem
          key={notification.id}
          notification={notification}
          onRemove={toast.remove.bind(toast)}
        />
      ))}
    </div>,
    document.body
  )
}

