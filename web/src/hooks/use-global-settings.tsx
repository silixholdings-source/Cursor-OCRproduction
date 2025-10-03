'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { currencyService } from '@/lib/currency'

interface GlobalSettings {
  currency: string
  locale: string
  timezone: string
  dateFormat: string
  numberFormat: string
}

interface GlobalSettingsContextType {
  settings: GlobalSettings
  updateCurrency: (currency: string) => void
  updateLocale: (locale: string) => void
  updateTimezone: (timezone: string) => void
  formatCurrency: (amount: number, currencyCode?: string) => string
  convertCurrency: (amount: number, from: string, to?: string) => Promise<number>
}

const defaultSettings: GlobalSettings = {
  currency: 'USD',
  locale: 'en',
  timezone: 'UTC',
  dateFormat: 'MM/dd/yyyy',
  numberFormat: 'en-US'
}

const GlobalSettingsContext = createContext<GlobalSettingsContextType | undefined>(undefined)

export function GlobalSettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<GlobalSettings>(defaultSettings)

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('global_settings')
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings)
        setSettings({ ...defaultSettings, ...parsed })
      } catch (error) {
        // Failed to parse saved settings, using defaults
      }
    }
  }, [])

  // Save settings to localStorage when they change
  useEffect(() => {
    localStorage.setItem('global_settings', JSON.stringify(settings))
  }, [settings])

  const updateCurrency = (currency: string) => {
    setSettings(prev => ({ ...prev, currency }))
  }

  const updateLocale = (locale: string) => {
    setSettings(prev => ({ ...prev, locale }))
  }

  const updateTimezone = (timezone: string) => {
    setSettings(prev => ({ ...prev, timezone }))
  }

  const formatCurrency = (amount: number, currencyCode?: string): string => {
    const currency = currencyCode || settings.currency
    return currencyService.formatAmount(amount, currency, settings.locale)
  }

  const convertCurrency = async (amount: number, from: string, to?: string): Promise<number> => {
    const targetCurrency = to || settings.currency
    return await currencyService.convertAmount(amount, from, targetCurrency)
  }

  const value: GlobalSettingsContextType = {
    settings,
    updateCurrency,
    updateLocale,
    updateTimezone,
    formatCurrency,
    convertCurrency
  }

  return (
    <GlobalSettingsContext.Provider value={value}>
      {children}
    </GlobalSettingsContext.Provider>
  )
}

export function useGlobalSettings() {
  const context = useContext(GlobalSettingsContext)
  if (context === undefined) {
    throw new Error('useGlobalSettings must be used within a GlobalSettingsProvider')
  }
  return context
}
