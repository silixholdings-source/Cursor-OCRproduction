'use client'

import { useEffect, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { notifications } from '@/lib/notifications'
import { Button } from '@/components/ui/button'

export interface KeyboardShortcut {
  key: string
  ctrlKey?: boolean
  altKey?: boolean
  shiftKey?: boolean
  metaKey?: boolean
  description: string
  action: () => void
  disabled?: boolean
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[] = []) {
  const router = useRouter()

  // Default global shortcuts
  const globalShortcuts: KeyboardShortcut[] = [
    {
      key: 'k',
      ctrlKey: true,
      description: 'Quick search',
      action: () => {
        // Focus search input or open search modal
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]') as HTMLInputElement
        if (searchInput) {
          searchInput.focus()
          searchInput.select()
        }
      }
    },
    {
      key: 'd',
      ctrlKey: true,
      description: 'Go to dashboard',
      action: () => router.push('/dashboard')
    },
    {
      key: 'i',
      ctrlKey: true,
      description: 'Go to invoices',
      action: () => router.push('/dashboard/invoices')
    },
    {
      key: 'a',
      ctrlKey: true,
      description: 'Go to approvals',
      action: () => router.push('/dashboard/approvals')
    },
    {
      key: 'u',
      ctrlKey: true,
      description: 'Upload invoice',
      action: () => router.push('/dashboard/invoices?action=upload')
    },
    {
      key: 'n',
      ctrlKey: true,
      description: 'New invoice',
      action: () => router.push('/dashboard/invoices?action=new')
    },
    {
      key: 'r',
      ctrlKey: true,
      shiftKey: true,
      description: 'Refresh data',
      action: () => window.location.reload()
    },
    {
      key: 'h',
      ctrlKey: true,
      description: 'Go to homepage',
      action: () => router.push('/')
    },
    {
      key: 's',
      ctrlKey: true,
      description: 'Go to settings',
      action: () => router.push('/dashboard/settings')
    },
    {
      key: '/',
      description: 'Show keyboard shortcuts',
      action: () => {
        notifications.info(
          'Press Ctrl+K for search, Ctrl+D for dashboard, Ctrl+I for invoices, Ctrl+A for approvals',
          'Keyboard Shortcuts'
        )
      }
    }
  ]

  const allShortcuts = useMemo(() => [...globalShortcuts, ...shortcuts], [globalShortcuts, shortcuts])

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Don't trigger shortcuts when user is typing in inputs
    const target = event.target as HTMLElement
    if (
      target.tagName === 'INPUT' ||
      target.tagName === 'TEXTAREA' ||
      target.contentEditable === 'true'
    ) {
      // Allow some shortcuts even in inputs (like Ctrl+A for select all)
      if (!event.ctrlKey || !['a', 'c', 'v', 'x', 'z'].includes(event.key.toLowerCase())) {
        return
      }
    }

    for (const shortcut of allShortcuts) {
      if (
        event.key.toLowerCase() === shortcut.key.toLowerCase() &&
        !!event.ctrlKey === !!shortcut.ctrlKey &&
        !!event.altKey === !!shortcut.altKey &&
        !!event.shiftKey === !!shortcut.shiftKey &&
        !!event.metaKey === !!shortcut.metaKey &&
        !shortcut.disabled
      ) {
        event.preventDefault()
        shortcut.action()
        break
      }
    }
  }, [allShortcuts])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  return {
    shortcuts: allShortcuts,
    showShortcuts: () => {
      notifications.info(
        allShortcuts
          .map(s => {
            const keys = []
            if (s.ctrlKey) keys.push('Ctrl')
            if (s.altKey) keys.push('Alt')
            if (s.shiftKey) keys.push('Shift')
            if (s.metaKey) keys.push('Cmd')
            keys.push(s.key.toUpperCase())
            return `${keys.join('+')} - ${s.description}`
          })
          .join('\n'),
        'Available Keyboard Shortcuts'
      )
    }
  }
}

// Keyboard shortcuts help component
export function KeyboardShortcutsHelp() {
  const { shortcuts, showShortcuts } = useKeyboardShortcuts()

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={showShortcuts}
      className="fixed bottom-4 right-4 z-50 bg-background/80 backdrop-blur-sm border"
    >
      <span className="text-xs">Press / for shortcuts</span>
    </Button>
  )
}


