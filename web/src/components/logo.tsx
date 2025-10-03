import Link from 'next/link'
import { cn } from '@/lib/utils'

interface LogoProps {
  className?: string
  showText?: boolean
}

export function Logo({ className, showText = true }: LogoProps) {
  return (
    <Link href="/" className={cn('flex items-center space-x-2', className)}>
      {/* Icon */}
      <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-600 rounded-lg">
        <svg
          className="w-5 h-5 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      
      {/* Text */}
      {showText && (
        <div className="flex flex-col">
          <span className="text-xl font-bold text-foreground">AI ERP</span>
          <span className="text-xs font-medium text-muted-foreground -mt-1">SaaS</span>
        </div>
      )}
    </Link>
  )
}
