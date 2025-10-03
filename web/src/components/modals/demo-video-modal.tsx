'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Play, X, ExternalLink } from 'lucide-react'

interface DemoVideoModalProps {
  isOpen: boolean
  onClose: () => void
  onTryInteractiveDemo: () => void
}

export function DemoVideoModal({ isOpen, onClose, onTryInteractiveDemo }: DemoVideoModalProps) {
  const [isPlaying, setIsPlaying] = useState(false)

  // Demo video - using a real example video for demonstration
  const videoUrl = "https://www.youtube.com/embed/dQw4w9WgXcQ" // Sample video - replace with actual demo

  const handlePlay = () => {
    setIsPlaying(true)
  }

  const handleClose = () => {
    setIsPlaying(false)
    onClose()
  }

  const handleTryInteractiveDemo = () => {
    onTryInteractiveDemo()
    handleClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[800px] p-0 overflow-hidden">
        <DialogHeader className="p-6 pb-0">
          <DialogTitle className="text-2xl font-bold text-gray-900">
            AI ERP Demo Video
          </DialogTitle>
        </DialogHeader>

        <div className="p-6 pt-4">
          {!isPlaying ? (
            <div className="text-center">
              {/* Video Placeholder */}
              <div className="relative w-full aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg mb-6 flex items-center justify-center">
                <button
                  onClick={handlePlay}
                  className="w-24 h-24 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-lg hover:bg-blue-700 transition-all duration-200 transform hover:scale-105"
                  aria-label="Play Demo Video"
                >
                  <Play className="h-12 w-12 fill-current ml-1" />
                </button>
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 mb-2">Demo Video</h3>
              <p className="text-gray-600 mb-6">
                This would be your actual demo video showcasing the AI ERP platform
              </p>
              
              {/* Feature List */}
              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">What you'll see in this demo:</h4>
                <ul className="space-y-3 text-left max-w-md mx-auto">
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">3-minute walkthrough of invoice processing</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">Real-time AI-powered data extraction</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">Approval workflow demonstration</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">ERP integration examples</span>
                  </li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="relative w-full aspect-video bg-black rounded-lg mb-6">
              <iframe
                className="absolute top-0 left-0 w-full h-full rounded-lg"
                src={`${videoUrl}?autoplay=1&rel=0&modestbranding=1`}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                title="AI ERP Demo Video"
              />
            </div>
          )}
        </div>

        <DialogFooter className="bg-gray-50 px-6 py-4 flex justify-between">
          <Button 
            variant="outline" 
            onClick={handleClose}
          >
            Close
          </Button>
          <Button 
            onClick={handleTryInteractiveDemo}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
          >
            <ExternalLink className="h-4 w-4" />
            Try Interactive Demo
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
