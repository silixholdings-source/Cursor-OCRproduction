'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { InvoiceUpload } from '@/components/invoice/invoice-upload'
import { OCRResults } from '@/components/invoice/ocr-results'
import { ArrowLeft, Upload, Brain, CheckCircle, ArrowRight } from 'lucide-react'
import Link from 'next/link'

export default function InteractiveDemoPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([])
  const [selectedFile, setSelectedFile] = useState<any>(null)

  const handleFilesProcessed = (files: any[]) => {
    setUploadedFiles(files)
    if (files.length > 0) {
      setSelectedFile(files[0])
      setCurrentStep(2)
    }
  }

  const handleStartTrial = () => {
    router.push('/auth/register?trial=true&plan=professional&source=interactive-demo')
  }

  const steps = [
    {
      number: 1,
      title: 'Upload Invoice',
      description: 'Try uploading a sample invoice or use our demo files',
      active: currentStep === 1,
      completed: currentStep > 1
    },
    {
      number: 2,
      title: 'AI Processing',
      description: 'Watch our AI extract data with high accuracy',
      active: currentStep === 2,
      completed: currentStep > 2
    },
    {
      number: 3,
      title: 'Review Results',
      description: 'See the extracted data and approve for processing',
      active: currentStep === 3,
      completed: currentStep > 3
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button variant="ghost" asChild className="mb-4">
            <Link href="/demo">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Demo
            </Link>
          </Button>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Interactive Demo
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl">
            Experience our AI-powered invoice processing firsthand. Upload a sample invoice 
            and see how our technology extracts data with incredible accuracy.
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between max-w-2xl mx-auto">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center">
                <div className={`
                  flex items-center justify-center w-10 h-10 rounded-full border-2 
                  ${step.completed 
                    ? 'bg-green-500 border-green-500 text-white' 
                    : step.active 
                      ? 'bg-blue-500 border-blue-500 text-white' 
                      : 'bg-white border-gray-300 text-gray-500'
                  }
                `}>
                  {step.completed ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <span className="text-sm font-semibold">{step.number}</span>
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`
                    w-16 h-0.5 mx-4 
                    ${step.completed ? 'bg-green-500' : 'bg-gray-300'}
                  `} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between max-w-2xl mx-auto mt-4">
            {steps.map((step) => (
              <div key={step.number} className="text-center flex-1">
                <h3 className={`text-sm font-medium ${
                  step.active ? 'text-blue-600' : step.completed ? 'text-green-600' : 'text-gray-500'
                }`}>
                  {step.title}
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Demo Content */}
        <div className="max-w-4xl mx-auto">
          {currentStep === 1 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Upload className="w-6 h-6 mr-3" />
                  Step 1: Upload Your Invoice
                </CardTitle>
              </CardHeader>
              <CardContent>
                <InvoiceUpload onFilesProcessed={handleFilesProcessed} maxFiles={1} />
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-blue-900 mb-2">Demo Tips:</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Upload any PDF or image file to see our AI in action</li>
                    <li>• Supported formats: PDF, JPG, PNG, TIFF</li>
                    <li>• Processing typically takes 2-5 seconds</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          )}

          {currentStep === 2 && selectedFile && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Brain className="w-6 h-6 mr-3" />
                  Step 2: AI Processing Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                <OCRResults 
                  file={selectedFile} 
                  onApprove={() => setCurrentStep(3)}
                  onReject={() => setCurrentStep(1)}
                />
              </CardContent>
            </Card>
          )}

          {currentStep === 3 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CheckCircle className="w-6 h-6 mr-3 text-green-600" />
                  Demo Complete!
                </CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <div className="py-8">
                  <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    Amazing Results!
                  </h3>
                  <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
                    You've just experienced how our AI can process invoices in seconds with 
                    incredible accuracy. Ready to transform your business?
                  </p>
                  
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Button size="lg" onClick={handleStartTrial} className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg">
                      Start Your Free Trial
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Button>
                    <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 border border-blue-600 transition-all duration-200 hover:scale-105 shadow-lg" asChild>
                      <Link href="/contact?inquiry=demo">
                        Schedule Live Demo
                      </Link>
                    </Button>
                  </div>
                  
                  <p className="text-sm text-gray-500 mt-4">
                    No credit card required • 3-day free trial • Full feature access
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-xl opacity-90 mb-6">
              Join thousands of businesses saving time and money with AI ERP SaaS.
            </p>
            <Button size="lg" onClick={handleStartTrial} className="bg-white text-blue-600 hover:bg-gray-100 transition-all duration-200 hover:scale-105 shadow-lg">
              Start Free Trial Now
            </Button>
            <p className="text-sm mt-4 opacity-75">
              No credit card required • Setup in 5 minutes • 24/7 support
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}