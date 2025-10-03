'use client'

import React from 'react'
import { Button } from '@/components/ui/button'

export default function HomePage() {
  const handleClick = () => {
    alert('Button clicked!')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI ERP SaaS - Test Page
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            This is a simplified test page to verify the app is working.
          </p>
          <Button onClick={handleClick} size="lg">
            Test Button
          </Button>
        </div>
      </div>
    </div>
  )
}

