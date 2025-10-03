'use client'

import React from 'react'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { UserNav } from '@/components/user-nav'
import { MobileNav } from '@/components/mobile-nav'
import { Logo } from '@/components/logo'
import { LanguageSwitcher } from '@/components/ui/language-switcher'
import { CurrencySwitcher } from '@/components/ui/currency-switcher'
import { useAuth } from '@/hooks/use-auth'
import { useGlobalSettings } from '@/hooks/use-global-settings'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Features', href: '/features' },
  { name: 'How It Works', href: '/features#how-it-works' },
  { name: 'Pricing', href: '/pricing' },
  { name: 'About', href: '/about' },
  { name: 'Contact', href: '/contact' },
]

export function Header() {
  const [isScrolled, setIsScrolled] = useState(false)
  const { user, isAuthenticated, logout } = useAuth()
  const { settings, updateCurrency } = useGlobalSettings()
  const router = useRouter()

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleSignOut = () => {
    logout()
    router.push('/')
  }

  return (
    <header
      className={cn(
        'sticky top-0 z-50 w-full transition-all duration-200',
        isScrolled
          ? 'bg-background/80 backdrop-blur-md border-b border-border/40'
          : 'bg-background'
      )}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <Logo />
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            
            {/* Global Settings */}
            <div className="hidden md:flex items-center space-x-2 mr-4">
              <LanguageSwitcher />
              <CurrencySwitcher 
                currentCurrency={settings.currency}
                onCurrencyChange={updateCurrency}
              />
            </div>

            {/* Desktop Auth Buttons */}
            <div className="hidden md:flex items-center space-x-2">
              {isAuthenticated ? (
                <>
                  <Button variant="ghost" onClick={() => router.push('/dashboard')}>
                    Dashboard
                  </Button>
                  <Button variant="ghost" onClick={handleSignOut}>
                    Sign Out
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="ghost" onClick={() => router.push('/auth/login')}>
                    Sign In
                  </Button>
                  <Button onClick={() => router.push('/auth/register')}>
                    Get Started
                  </Button>
                </>
              )}
            </div>

            {/* Mobile menu button */}
            <MobileNav navigation={navigation} />
          </div>
        </div>
      </div>
    </header>
  )
}
