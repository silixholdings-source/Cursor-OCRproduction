'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { DemoVideoModal } from '@/components/modals/demo-video-modal'
import { Play, Video } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface DemoVideoButtonProps {
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link' | 'destructive'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  className?: string
  children?: React.ReactNode
}

export function DemoVideoButton({ 
  variant = 'default', 
  size = 'default',
  className = '',
  children
}: DemoVideoButtonProps) {
  const [showDemoModal, setShowDemoModal] = useState(false)
  const router = useRouter()

  const handleOpenDemo = () => {
    setShowDemoModal(true)
  }

  const handleCloseDemo = () => {
    setShowDemoModal(false)
  }

  const handleTryInteractiveDemo = () => {
    // Navigate to the interactive demo page
    router.push('/demo/interactive')
  }

  return (
    <>
      <Button
        variant={variant}
        size={size}
        className={`flex items-center gap-2 ${className}`}
        onClick={handleOpenDemo}
      >
        {children || (
          <>
            <Play className="h-4 w-4" />
            Watch Demo Video
          </>
        )}
      </Button>

      <DemoVideoModal
        isOpen={showDemoModal}
        onClose={handleCloseDemo}
        onTryInteractiveDemo={handleTryInteractiveDemo}
      />
    </>
  )
}

// Alternative button with video icon
export function DemoVideoIconButton({ className = '' }: { className?: string }) {
  return (
    <DemoVideoButton
      variant="ghost"
      size="icon"
      className={`text-gray-600 hover:text-gray-900 hover:bg-gray-100 ${className}`}
    >
      <Video className="h-5 w-5" />
    </DemoVideoButton>
  )
}





































