'use client'

import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { UserNav } from '@/components/user-nav'
import { 
  Menu
} from 'lucide-react'

interface DashboardHeaderProps {
  user: any
  company: any
  onMenuClick: () => void
}

export function DashboardHeader({ user, company, onMenuClick }: DashboardHeaderProps) {
  const { logout } = useAuth()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left side - Menu button */}
          <div className="flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={onMenuClick}
              className="lg:hidden mr-2"
              aria-label="Open navigation menu"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </div>

          {/* Right side - User menu */}
          <div className="flex items-center space-x-4">
            {/* User navigation */}
            <UserNav user={user} onLogout={logout} />
          </div>
        </div>
      </div>
    </header>
  )
}












