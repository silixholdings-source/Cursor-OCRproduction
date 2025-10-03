'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Play, CheckCircle, ArrowRight, Zap, Shield, BarChart3, ExternalLink } from 'lucide-react'

export function Demo() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)
  const [showVideoModal, setShowVideoModal] = useState(false)

  const handleWatchDemo = () => {
    // Open demo video in a modal or redirect to demo page
    setShowVideoModal(true)
    setIsVideoPlaying(true)
  }

  const handleTryInteractiveDemo = () => {
    // Redirect to interactive demo page or open demo in new tab
    window.open('/demo/interactive', '_blank')
  }

  const handleCloseVideo = () => {
    setShowVideoModal(false)
    setIsVideoPlaying(false)
  }
  return (
    <section id="demo" className="py-20 bg-muted/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4 px-4 py-2 text-sm">
            <Play className="mr-2 h-4 w-4" />
            Live Demo
          </Badge>
          <h2 className="text-4xl font-bold mb-6">
            See AI ERP in Action
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Watch how our AI-powered platform transforms your invoice processing workflow 
            from hours to minutes with intelligent automation.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Demo Video Placeholder */}
          <div className="relative">
            <div 
              className="aspect-video bg-gradient-to-br from-brand-500/20 to-brand-600/20 rounded-2xl border border-border/50 flex items-center justify-center cursor-pointer hover:from-brand-500/30 hover:to-brand-600/30 transition-all duration-300 group"
              onClick={handleWatchDemo}
            >
              <div className="text-center">
                <div className="w-20 h-20 bg-brand-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Play className="h-8 w-8 text-white ml-1" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Interactive Demo</h3>
                <p className="text-muted-foreground">
                  Click to watch a 3-minute walkthrough
                </p>
              </div>
            </div>
            <div className="absolute -top-4 -right-4">
              <Badge className="bg-green-500 text-white">
                <Zap className="mr-1 h-3 w-3" />
                Live
              </Badge>
            </div>
          </div>

          {/* Demo Features */}
          <div className="space-y-8">
            <div>
              <h3 className="text-2xl font-bold mb-4">
                Experience the Power of AI
              </h3>
              <p className="text-muted-foreground mb-6">
                Our platform processes invoices with 99.5% accuracy, reducing manual work 
                by 90% and cutting processing time from days to minutes.
              </p>
            </div>

            <div className="space-y-4">
              {[
                {
                  icon: Zap,
                  title: 'Instant Processing',
                  description: 'Upload invoices and watch them process in real-time'
                },
                {
                  icon: Shield,
                  title: 'Smart Validation',
                  description: 'AI automatically validates data and flags discrepancies'
                },
                {
                  icon: BarChart3,
                  title: 'Real-time Analytics',
                  description: 'Track processing metrics and approval workflows live'
                }
              ].map((feature, index) => (
                <div key={index} className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-brand-500/10 rounded-lg flex items-center justify-center">
                    <feature.icon className="h-5 w-5 text-brand-500" />
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">{feature.title}</h4>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="group" onClick={handleWatchDemo}>
                <Play className="mr-2 h-5 w-5" />
                Watch Demo
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
              <Button variant="outline" size="lg" onClick={handleTryInteractiveDemo}>
                <ExternalLink className="mr-2 h-5 w-5" />
                Try Interactive Demo
              </Button>
            </div>
          </div>
        </div>

        {/* Demo Stats */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              number: '99.5%',
              label: 'Accuracy Rate',
              description: 'AI-powered data extraction'
            },
            {
              number: '90%',
              label: 'Time Saved',
              description: 'Reduced processing time'
            },
            {
              number: '500+',
              label: 'Companies',
              description: 'Trust our platform'
            }
          ].map((stat, index) => (
            <Card key={index} className="text-center">
              <CardHeader>
                <div className="text-4xl font-bold text-brand-500 mb-2">
                  {stat.number}
                </div>
                <CardTitle className="text-lg">{stat.label}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{stat.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Video Modal */}
      {showVideoModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">AI ERP Demo Video</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCloseVideo}
                className="h-8 w-8 p-0"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </Button>
            </div>
            <div className="aspect-video bg-gray-100 flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 bg-brand-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Play className="h-6 w-6 text-white ml-1" />
                </div>
                <h4 className="text-lg font-semibold mb-2">Demo Video</h4>
                <p className="text-gray-600 mb-4">
                  This would be your actual demo video showcasing the AI ERP platform
                </p>
                <div className="space-y-2 text-sm text-gray-500">
                  <p>• 3-minute walkthrough of invoice processing</p>
                  <p>• Real-time AI-powered data extraction</p>
                  <p>• Approval workflow demonstration</p>
                  <p>• ERP integration examples</p>
                </div>
                <div className="mt-6 flex gap-4 justify-center">
                  <Button onClick={handleCloseVideo} variant="outline">
                    Close
                  </Button>
                  <Button onClick={handleTryInteractiveDemo}>
                    Try Interactive Demo
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
