'use client'

import { useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'

interface KeyboardShortcut {
  key: string
  ctrlKey?: boolean
  shiftKey?: boolean
  altKey?: boolean
  action: () => void
  description: string
}

export function useKeyboardShortcuts() {
  const router = useRouter()

  const shortcuts: KeyboardShortcut[] = [
    {
      key: 'd',
      ctrlKey: true,
      action: () => router.push('/dashboard'),
      description: 'Go to Dashboard'
    },
    {
      key: 'i',
      ctrlKey: true,
      action: () => router.push('/dashboard/invoices'),
      description: 'Go to Invoices'
    },
    {
      key: 'a',
      ctrlKey: true,
      action: () => router.push('/dashboard/approvals'),
      description: 'Go to Approvals'
    },
    {
      key: 'n',
      ctrlKey: true,
      action: () => {
        // Trigger new invoice upload
        const uploadButton = document.querySelector('[data-upload-trigger]') as HTMLElement
        uploadButton?.click()
      },
      description: 'New Invoice Upload'
    },
    {
      key: 's',
      ctrlKey: true,
      action: () => router.push('/dashboard/settings'),
      description: 'Go to Settings'
    },
    {
      key: 'h',
      ctrlKey: true,
      action: () => router.push('/help'),
      description: 'Help & Support'
    },
    {
      key: '/',
      ctrlKey: true,
      action: () => {
        // Focus search input
        const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement
        searchInput?.focus()
      },
      description: 'Focus Search'
    },
    {
      key: 'Escape',
      action: () => {
        // Close any open modals or clear selections
        const closeButtons = document.querySelectorAll('[data-close-modal]')
        closeButtons.forEach(btn => (btn as HTMLElement).click())
      },
      description: 'Close Modals'
    }
  ]

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Don't trigger shortcuts when typing in input fields
    if (
      event.target instanceof HTMLInputElement ||
      event.target instanceof HTMLTextAreaElement ||
      event.target instanceof HTMLSelectElement
    ) {
      return
    }

    const matchingShortcut = shortcuts.find(shortcut => 
      shortcut.key.toLowerCase() === event.key.toLowerCase() &&
      !!shortcut.ctrlKey === event.ctrlKey &&
      !!shortcut.shiftKey === event.shiftKey &&
      !!shortcut.altKey === event.altKey
    )

    if (matchingShortcut) {
      event.preventDefault()
      matchingShortcut.action()
    }
  }, [shortcuts])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])

  return {
    shortcuts: shortcuts.map(({ action, ...shortcut }) => shortcut)
  }
}

