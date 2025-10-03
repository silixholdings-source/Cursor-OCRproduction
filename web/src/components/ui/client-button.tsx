'use client'

import React from 'react'
import { Button, ButtonProps } from './button'

export interface ClientButtonProps extends ButtonProps {
  onClick?: () => void
}

export function ClientButton({ onClick, ...props }: ClientButtonProps) {
  return <Button onClick={onClick} {...props} />
}































