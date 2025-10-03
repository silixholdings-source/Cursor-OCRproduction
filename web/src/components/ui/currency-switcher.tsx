'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { DollarSign } from 'lucide-react'
import { SUPPORTED_CURRENCIES, currencyService } from '@/lib/currency'

interface CurrencySwitcherProps {
  currentCurrency: string
  onCurrencyChange: (currency: string) => void
  className?: string
}

export function CurrencySwitcher({ 
  currentCurrency, 
  onCurrencyChange, 
  className 
}: CurrencySwitcherProps) {
  const [isOpen, setIsOpen] = useState(false)
  
  const currentCurrencyInfo = SUPPORTED_CURRENCIES[currentCurrency]
  const supportedCurrencies = currencyService.getSupportedCurrencies()

  const handleCurrencyChange = (currencyCode: string) => {
    onCurrencyChange(currencyCode)
    setIsOpen(false)
    
    // Store preference in localStorage
    localStorage.setItem('preferred_currency', currencyCode)
  }

  // Load saved currency preference on mount
  useEffect(() => {
    const savedCurrency = localStorage.getItem('preferred_currency')
    if (savedCurrency && SUPPORTED_CURRENCIES[savedCurrency]) {
      onCurrencyChange(savedCurrency)
    }
  }, [onCurrencyChange])

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className={`flex items-center gap-2 ${className}`}
        >
          <DollarSign className="h-4 w-4" />
          <span className="hidden sm:inline">
            {currentCurrencyInfo?.symbol} {currentCurrency}
          </span>
          <span className="sm:hidden">
            {currentCurrencyInfo?.symbol}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        {supportedCurrencies.map((currency) => (
          <DropdownMenuItem
            key={currency.code}
            onClick={() => handleCurrencyChange(currency.code)}
            className={`flex items-center justify-between ${
              currency.code === currentCurrency ? 'bg-accent' : ''
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="font-medium">{currency.symbol}</span>
              <span>{currency.code}</span>
            </div>
            <span className="text-xs text-muted-foreground">
              {currency.name}
            </span>
            {currency.code === currentCurrency && (
              <span className="ml-2 text-xs text-muted-foreground">✓</span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}


