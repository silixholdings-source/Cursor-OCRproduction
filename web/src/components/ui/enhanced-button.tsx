'use client'

import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

const enhancedButtonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 relative overflow-hidden",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90 active:scale-95",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 active:scale-95",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground active:scale-95",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80 active:scale-95",
        ghost: "hover:bg-accent hover:text-accent-foreground active:scale-95",
        link: "text-primary underline-offset-4 hover:underline",
        success: "bg-green-600 text-white hover:bg-green-700 active:scale-95",
        warning: "bg-yellow-600 text-white hover:bg-yellow-700 active:scale-95",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
        xl: "h-12 rounded-lg px-10 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface EnhancedButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof enhancedButtonVariants> {
  asChild?: boolean
  loading?: boolean
  loadingText?: string
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
  success?: boolean
  successText?: string
  successDuration?: number
}

const EnhancedButton = React.forwardRef<HTMLButtonElement, EnhancedButtonProps>(
  ({ 
    className, 
    variant, 
    size, 
    asChild = false, 
    loading = false,
    loadingText,
    icon,
    iconPosition = 'left',
    success = false,
    successText,
    successDuration = 2000,
    children,
    disabled,
    onClick,
    ...props 
  }, ref) => {
    const [showSuccess, setShowSuccess] = React.useState(false)
    const [isProcessing, setIsProcessing] = React.useState(false)

    React.useEffect(() => {
      if (success) {
        setShowSuccess(true)
        const timer = setTimeout(() => setShowSuccess(false), successDuration)
        return () => clearTimeout(timer)
      }
    }, [success, successDuration])

    const handleClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
      if (disabled || loading || isProcessing) return
      
      setIsProcessing(true)
      try {
        await onClick?.(e)
      } finally {
        // Small delay to show processing state
        setTimeout(() => setIsProcessing(false), 200)
      }
    }

    const isLoading = loading || isProcessing
    const isDisabled = disabled || isLoading

    if (asChild) {
      return (
        <Slot
          className={cn(enhancedButtonVariants({ variant, size, className }))}
          ref={ref}
          {...props}
        >
          {children}
        </Slot>
      )
    }

    return (
      <button
        className={cn(
          enhancedButtonVariants({ variant, size, className }),
          showSuccess && "bg-green-600 text-white"
        )}
        ref={ref}
        disabled={isDisabled}
        onClick={handleClick}
        {...props}
      >
        {/* Loading state */}
        {isLoading && (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            {loadingText || 'Loading...'}
          </>
        )}
        
        {/* Success state */}
        {showSuccess && !isLoading && (
          <>
            <div className="mr-2 h-4 w-4 rounded-full bg-white/20 flex items-center justify-center">
              <div className="h-2 w-2 rounded-full bg-white" />
            </div>
            {successText || 'Success!'}
          </>
        )}
        
        {/* Normal state */}
        {!isLoading && !showSuccess && (
          <>
            {icon && iconPosition === 'left' && (
              <span className="mr-2">{icon}</span>
            )}
            {children}
            {icon && iconPosition === 'right' && (
              <span className="ml-2">{icon}</span>
            )}
          </>
        )}
      </button>
    )
  }
)
EnhancedButton.displayName = "EnhancedButton"

export { EnhancedButton, enhancedButtonVariants }

