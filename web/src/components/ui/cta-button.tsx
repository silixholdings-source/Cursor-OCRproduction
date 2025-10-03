'use client'

import Link from 'next/link'
import { ButtonProps, buttonVariants } from './button'
import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface CTAButtonProps extends Omit<ButtonProps, 'asChild'> {
  href: string
  children: ReactNode
  variant?: 'primary' | 'secondary'
  backgroundType?: 'blue' | 'white' // Add background type to determine button style
}

export function CTAButton({ href, children, className, variant = 'primary', backgroundType = 'white', size = 'lg', ...props }: CTAButtonProps) {
  const baseClasses = "px-8 py-4 rounded-lg font-semibold transition-all duration-200 text-lg shadow-lg"
  
  // Both buttons use the same style based on background
  const getButtonStyle = () => {
    if (backgroundType === 'blue') {
      // On blue background, both buttons are white with blue text - IDENTICAL STYLING
      return "bg-white text-blue-600 hover:bg-gray-100 border border-blue-600"
    } else {
      // On white background, both buttons are blue with white text - IDENTICAL STYLING
      return "bg-blue-600 hover:bg-blue-700 text-white"
    }
  }
  
  return (
    <Link
      href={href}
      className={cn(
        buttonVariants({ size }),
        baseClasses,
        getButtonStyle(),
        className
      )}
      {...props}
    >
      {children}
    </Link>
  )
}
