'use client'

import Link from 'next/link'
import { ButtonProps, buttonVariants } from './button'
import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface LinkButtonProps extends Omit<ButtonProps, 'asChild'> {
  href: string
  children: ReactNode
}

export function LinkButton({ href, children, className, variant, size, ...props }: LinkButtonProps) {
  return (
    <Link 
      href={href}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    >
      {children}
    </Link>
  )
}

