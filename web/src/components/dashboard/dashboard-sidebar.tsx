'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { 
  X,
  Home,
  FileText,
  Users,
  Settings,
  BarChart3,
  CreditCard,
  Building2,
  Workflow,
  Database,
  Zap,
  Shield,
  HelpCircle,
  Menu
} from 'lucide-react'

interface DashboardSidebarProps {
  isOpen: boolean
  onClose: () => void
  user: any
  company: any
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Invoices', href: '/dashboard/invoices', icon: FileText },
  { name: 'Approvals', href: '/dashboard/approvals', icon: Workflow },
  { name: 'Workflows', href: '/dashboard/workflows', icon: Workflow },
  { name: 'Vendors', href: '/dashboard/vendors', icon: Building2 },
  { name: 'Users', href: '/dashboard/users', icon: Users },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { name: 'Audit Trail', href: '/dashboard/audit', icon: Shield },
  { name: 'ERP Integration', href: '/dashboard/erp', icon: Database },
  { name: 'Billing', href: '/dashboard/billing', icon: CreditCard },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  { name: 'Help', href: '/dashboard/help', icon: HelpCircle },
]

const adminNavigation = [
  { name: 'Company Settings', href: '/dashboard/company', icon: Building2 },
  { name: 'User Management', href: '/dashboard/users', icon: Users },
  { name: 'Security', href: '/dashboard/security', icon: Shield },
  { name: 'API Keys', href: '/dashboard/api-keys', icon: Zap },
]

export function DashboardSidebar({ isOpen, onClose, user, company }: DashboardSidebarProps) {
  const pathname = usePathname()
  const isAdmin = user?.role === 'owner' || user?.role === 'admin'

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Mobile Menu Button */}
      <div className="lg:hidden p-4 border-b border-gray-200 flex-shrink-0">
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="w-full justify-start"
        >
          <Menu className="h-5 w-5 mr-2" />
          Close Menu
        </Button>
      </div>
      
      {/* Company Header */}
      <div className="p-4 border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900 truncate">
              {company?.name || 'Company'}
            </h3>
            <p className="text-xs text-gray-500 capitalize">
              {company?.tier || 'Free'} Plan
            </p>
          </div>
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center ml-3">
            <span className="text-white font-semibold text-lg">
              {company?.name?.charAt(0) || 'C'}
            </span>
          </div>
        </div>
        
        {/* Trial status */}
        {company?.trial_ends_at && (
          <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
            <p className="text-xs text-yellow-800">
              Trial ends {new Date(company.trial_ends_at).toLocaleDateString()}
            </p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                  ${isActive
                    ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }
                `}
                onClick={() => onClose()}
              >
                <item.icon
                  className={`
                    mr-3 h-5 w-5 flex-shrink-0
                    ${isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'}
                  `}
                />
                {item.name}
              </Link>
            )
          })}
        </div>

        {/* Admin Section */}
        {isAdmin && (
          <div className="pt-6 border-t border-gray-200">
            <h4 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Administration
            </h4>
            <div className="mt-2 space-y-1">
              {adminNavigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`
                      group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                      ${isActive
                        ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }
                    `}
                    onClick={() => onClose()}
                  >
                    <item.icon
                      className={`
                        mr-3 h-5 w-5 flex-shrink-0
                        ${isActive ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'}
                      `}
                    />
                    {item.name}
                  </Link>
                )
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 flex-shrink-0">
        <div className="space-y-2">
          <Link
            href="/dashboard/help"
            className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
            onClick={() => onClose()}
          >
            <HelpCircle className="mr-3 h-5 w-5 text-gray-400" />
            Help & Support
          </Link>
          
          <div className="px-3 py-2">
            <p className="text-xs text-gray-500">
              © 2024 AI ERP SaaS
            </p>
            <p className="text-xs text-gray-400">
              v1.0.0
            </p>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Mobile sidebar */}
      <Sheet open={isOpen} onOpenChange={onClose}>
        <SheetContent side="left" className="w-80 p-0">
          <SheetHeader className="sr-only">
            <SheetTitle>Navigation</SheetTitle>
          </SheetHeader>
          <SidebarContent />
        </SheetContent>
      </Sheet>

      {/* Desktop sidebar */}
      <div className="hidden lg:block fixed left-0 top-0 w-64 h-screen z-40">
        <div className="flex flex-col h-full bg-white border-r border-gray-200">
          <SidebarContent />
        </div>
      </div>
    </>
  )
}












