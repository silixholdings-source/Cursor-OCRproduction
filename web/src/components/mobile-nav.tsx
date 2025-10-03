'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Menu, X } from 'lucide-react'
import { useAuth } from '@/hooks/use-auth'
import { cn } from '@/lib/utils'

interface NavigationItem {
  name: string
  href: string
}

interface MobileNavProps {
  navigation: NavigationItem[]
}

export function MobileNav({ navigation }: MobileNavProps) {
  const [open, setOpen] = useState(false)
  const { user, isAuthenticated, logout } = useAuth()
  const router = useRouter()

  const handleSignOut = () => {
    logout()
    router.push('/')
    setOpen(false)
  }

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[300px] sm:w-[400px]">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center pb-4 border-b">
            <h2 className="text-lg font-semibold">Menu</h2>
          </div>

          {/* Navigation */}
          <nav className="flex-1 py-6">
            <ul className="space-y-4">
              {navigation.map((item) => (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className={cn(
                      'block px-3 py-2 text-base font-medium rounded-md transition-colors',
                      'text-muted-foreground hover:text-foreground hover:bg-muted'
                    )}
                    onClick={() => setOpen(false)}
                  >
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          {/* Auth Buttons */}
          <div className="border-t pt-6 space-y-3">
            {isAuthenticated ? (
              <>
                <Button 
                  variant="ghost" 
                  className="w-full justify-start" 
                  onClick={() => {
                    router.push('/dashboard')
                    setOpen(false)
                  }}
                >
                  Dashboard
                </Button>
                <Button variant="ghost" className="w-full justify-start" onClick={handleSignOut}>
                  Sign Out
                </Button>
              </>
            ) : (
              <>
                <Button 
                  variant="ghost" 
                  className="w-full justify-start" 
                  onClick={() => {
                    router.push('/auth/login')
                    setOpen(false)
                  }}
                >
                  Sign In
                </Button>
                <Button 
                  className="w-full" 
                  onClick={() => {
                    router.push('/auth/register')
                    setOpen(false)
                  }}
                >
                  Get Started
                </Button>
              </>
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
