'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { 
  Menu, 
  X, 
  Zap,
  ArrowRight,
  User,
  LogOut
} from 'lucide-react'

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false)
  const router = useRouter()
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">AI ERP SaaS</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {isAuthenticated ? (
              <>
                <Link href="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Dashboard
                </Link>
                <Link href="/dashboard/invoices" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Invoices
                </Link>
                <Link href="/dashboard/approvals" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Approvals
                </Link>
                <Link href="/dashboard/vendors" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Vendors
                </Link>
                <Link href="/dashboard/analytics" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Analytics
                </Link>
                <Link href="/dashboard/settings" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Settings
                </Link>
                <Link href="/support" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Support
                </Link>
              </>
            ) : (
              <>
                <Link href="/features" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Features
                </Link>
                <Link href="/pricing" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Pricing
                </Link>
                <Link href="/integrations" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Integrations
                </Link>
                <Link href="/security" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Security
                </Link>
                <Link href="/support" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Support
                </Link>
                <Link href="/contact" className="text-gray-700 hover:text-blue-600 transition-colors">
                  Contact Us
                </Link>
              </>
            )}
          </div>

          {/* Desktop CTA Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <div className="flex items-center space-x-2">
                  <User className="w-4 h-4 text-gray-600" />
                  <span className="text-sm text-gray-700">{user?.name || user?.email}</span>
                </div>
                <Button
                  variant="ghost"
                  className="text-gray-700 hover:text-red-600 transition-colors"
                  onClick={() => {
                    logout()
                    router.push('/')
                  }}
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  className="text-gray-700 hover:text-blue-600 transition-colors"
                  onClick={() => router.push('/auth/login')}
                >
                  Sign In
                </Button>
                <Button
                  className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg"
                  onClick={() => router.push('/auth/register')}
                >
                  Start Free Trial
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-md hover:bg-gray-100 transition-colors"
            onClick={() => setIsOpen(!isOpen)}
            aria-label={isOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={isOpen ? 'true' : 'false'}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

            {/* Mobile Navigation */}
            {isOpen && (
              <div className="md:hidden border-t bg-white shadow-lg">
                <div className="py-4 space-y-2">
                  {isAuthenticated ? (
                    <>
                      <Link
                        href="/dashboard"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Dashboard
                      </Link>
                      <Link
                        href="/dashboard/invoices"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Invoices
                      </Link>
                      <Link
                        href="/dashboard/approvals"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Approvals
                      </Link>
                      <Link
                        href="/dashboard/vendors"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Vendors
                      </Link>
                      <Link
                        href="/dashboard/analytics"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Analytics
                      </Link>
                      <Link
                        href="/dashboard/settings"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Settings
                      </Link>
                      <Link
                        href="/support"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Support
                      </Link>
                    </>
                  ) : (
                    <>
                      <Link
                        href="/features"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Features
                      </Link>
                      <Link
                        href="/pricing"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Pricing
                      </Link>
                      <Link
                        href="/integrations"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Integrations
                      </Link>
                      <Link
                        href="/security"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Security
                      </Link>
                      <Link
                        href="/support"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Support
                      </Link>
                      <Link
                        href="/contact"
                        className="block px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-md transition-colors font-medium"
                        onClick={() => setIsOpen(false)}
                      >
                        Contact Us
                      </Link>
                    </>
                  )}
              
                  <div className="border-t pt-4 mt-4">
                    {isAuthenticated ? (
                      <>
                        <div className="flex items-center space-x-2 px-4 py-2 text-gray-700 mb-2">
                          <User className="w-4 h-4" />
                          <span className="text-sm">{user?.name || user?.email}</span>
                        </div>
                        <Button
                          variant="ghost"
                          className="w-full justify-start text-gray-700 hover:text-red-600"
                          onClick={() => {
                            logout()
                            setIsOpen(false)
                          }}
                        >
                          <LogOut className="w-4 h-4 mr-2" />
                          Sign Out
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button
                          variant="ghost"
                          className="w-full justify-start text-gray-700 mb-2"
                          onClick={() => {
                            router.push('/auth/login')
                            setIsOpen(false)
                          }}
                        >
                          Sign In
                        </Button>
                        <Button
                          className="w-full bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg"
                          onClick={() => {
                            router.push('/auth/register')
                            setIsOpen(false)
                          }}
                        >
                          Start Free Trial
                          <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                      </>
                    )}
                  </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
