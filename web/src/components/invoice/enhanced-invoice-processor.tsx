'use client'

import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Upload, 
  FileText, 
  Brain, 
  CheckCircle, 
  AlertTriangle,
  Zap,
  Search,
  Shield,
  TrendingUp,
  Clock,
  Eye,
  Download,
  Loader2,
  Wifi,
  WifiOff
} from 'lucide-react'
import { useWebSocket } from '@/hooks/use-websocket'
import { logger } from '@/lib/logger'
import { getApiBaseUrl } from '@/lib/api'

interface ProcessingResult {
  invoice_id: string
  ocr_confidence: number
  vendor_match: {
    suggested: string
    confidence: number
    new_vendor: boolean
  }
  fraud_score: number
  duplicate_check: {
    is_duplicate: boolean
    similar_invoices: any[]
  }
  category_suggestion: {
    category: string
    confidence: number
  }
  processing_time: number
  status: string
}

interface EnhancedInvoiceProcessorProps {
  onProcessingComplete?: (result: ProcessingResult) => void
}

export function EnhancedInvoiceProcessor({ onProcessingComplete }: EnhancedInvoiceProcessorProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStage, setProcessingStage] = useState('')
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<ProcessingResult | null>(null)
  const [vendorQuery, setVendorQuery] = useState('')
  const [vendorSuggestions, setVendorSuggestions] = useState<any[]>([])

  // Real-time processing updates
  const { isConnected } = useWebSocket('ws://localhost:8001/ws', {
    onMessage: (message) => {
      if (message.type === 'invoice_processed') {
        setResult(message.data)
        setIsProcessing(false)
        setProgress(100)
        onProcessingComplete?.(message.data)
      }
    }
  })

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setIsProcessing(true)
    setProgress(0)
    setResult(null)

    // Simulate processing stages
    const stages = [
      { name: 'Uploading file...', progress: 20 },
      { name: 'Running OCR analysis...', progress: 40 },
      { name: 'Extracting data...', progress: 60 },
      { name: 'Matching vendors...', progress: 80 },
      { name: 'Fraud detection...', progress: 90 },
      { name: 'Finalizing...', progress: 100 }
    ]

    for (const stage of stages) {
      setProcessingStage(stage.name)
      setProgress(stage.progress)
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    // Call processing API
    try {
      const response = await fetch(`${getApiBaseUrl()}/invoices/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: file.name,
          size: file.size
        })
      })

      if (response.ok) {
        const processingResult = await response.json()
        setResult(processingResult)
        onProcessingComplete?.(processingResult)
      }
    } catch (error) {
      logger.error('Processing failed:', error)
    }

    setIsProcessing(false)
  }, [onProcessingComplete])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff']
    },
    maxFiles: 1
  })

  const searchVendors = async (query: string) => {
    if (query.length < 2) {
      setVendorSuggestions([])
      return
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'}/vendors/suggestions?query=${encodeURIComponent(query)}`)
      if (response.ok) {
        const data = await response.json()
        setVendorSuggestions(data.suggestions)
      }
    } catch (error) {
      logger.error('Vendor search failed:', error)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'bg-green-100 text-green-800'
    if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  const getFraudRiskColor = (score: number) => {
    if (score <= 0.3) return 'bg-green-100 text-green-800'
    if (score <= 0.6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <div className="space-y-6">
      {/* Real-time Connection Status */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Enhanced Invoice Processor</h2>
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <>
              <Wifi className="h-4 w-4 text-green-600" />
              <span className="text-sm text-green-600">Real-time connected</span>
            </>
          ) : (
            <>
              <WifiOff className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-400">Offline mode</span>
            </>
          )}
        </div>
      </div>

      {/* File Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Upload Invoice</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragActive 
                ? 'border-blue-400 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            {isProcessing ? (
              <div className="space-y-4">
                <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto" />
                <div>
                  <p className="text-lg font-medium text-gray-900">{processingStage}</p>
                  <Progress value={progress} className="mt-2" />
                  <p className="text-sm text-gray-600 mt-1">{progress}% complete</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <FileText className="h-12 w-12 text-gray-400 mx-auto" />
                <div>
                  <p className="text-lg font-medium text-gray-900">
                    {isDragActive ? 'Drop the invoice here' : 'Drag & drop an invoice'}
                  </p>
                  <p className="text-gray-600">or click to select files</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Supports PDF, PNG, JPG, JPEG, TIFF (max 10MB)
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Vendor Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Smart Vendor Matching</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Label htmlFor="vendor-search">Search Vendors</Label>
              <Input
                id="vendor-search"
                placeholder="Type vendor name..."
                value={vendorQuery}
                onChange={(e) => {
                  setVendorQuery(e.target.value)
                  searchVendors(e.target.value)
                }}
              />
            </div>
            
            {vendorSuggestions.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">Suggested Vendors:</p>
                {vendorSuggestions.map((vendor) => (
                  <div key={vendor.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                    <div>
                      <p className="font-medium">{vendor.name}</p>
                      <p className="text-sm text-gray-600">{vendor.category}</p>
                    </div>
                    <Badge className={getConfidenceColor(vendor.confidence)}>
                      {Math.round(vendor.confidence * 100)}% match
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Processing Results */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="h-5 w-5" />
              <span>AI Processing Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* OCR Confidence */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <Eye className="h-4 w-4 text-blue-600" />
                  <span className="font-medium">OCR Accuracy</span>
                </div>
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(result.ocr_confidence * 100)}%
                </div>
                <Badge className={getConfidenceColor(result.ocr_confidence)} size="sm">
                  {result.ocr_confidence >= 0.9 ? 'Excellent' : result.ocr_confidence >= 0.7 ? 'Good' : 'Review Needed'}
                </Badge>
              </div>

              {/* Vendor Match */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <Search className="h-4 w-4 text-green-600" />
                  <span className="font-medium">Vendor Match</span>
                </div>
                <div className="text-sm font-medium text-gray-900">
                  {result.vendor_match.suggested}
                </div>
                <Badge className={getConfidenceColor(result.vendor_match.confidence)} size="sm">
                  {Math.round(result.vendor_match.confidence * 100)}% confidence
                </Badge>
              </div>

              {/* Fraud Detection */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <Shield className="h-4 w-4 text-red-600" />
                  <span className="font-medium">Fraud Risk</span>
                </div>
                <div className="text-2xl font-bold">
                  {Math.round(result.fraud_score * 100)}%
                </div>
                <Badge className={getFraudRiskColor(result.fraud_score)} size="sm">
                  {result.fraud_score <= 0.3 ? 'Low Risk' : result.fraud_score <= 0.6 ? 'Medium Risk' : 'High Risk'}
                </Badge>
              </div>

              {/* Category Suggestion */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-purple-600" />
                  <span className="font-medium">Category</span>
                </div>
                <div className="text-sm font-medium text-gray-900">
                  {result.category_suggestion.category}
                </div>
                <Badge className={getConfidenceColor(result.category_suggestion.confidence)} size="sm">
                  {Math.round(result.category_suggestion.confidence * 100)}% confidence
                </Badge>
              </div>

              {/* Processing Time */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <Clock className="h-4 w-4 text-indigo-600" />
                  <span className="font-medium">Processing Time</span>
                </div>
                <div className="text-2xl font-bold text-indigo-600">
                  {result.processing_time}s
                </div>
                <Badge variant="outline" size="sm">
                  Lightning fast
                </Badge>
              </div>

              {/* Duplicate Check */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="font-medium">Duplicate Check</span>
                </div>
                <div className="text-sm font-medium">
                  {result.duplicate_check.is_duplicate ? 'Duplicate Found' : 'No Duplicates'}
                </div>
                <Badge className={result.duplicate_check.is_duplicate ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'} size="sm">
                  {result.duplicate_check.is_duplicate ? 'Attention Required' : 'Verified Unique'}
                </Badge>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4 mt-6">
              <Button className="flex-1 bg-green-600 hover:bg-green-700">
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve & Process
              </Button>
              <Button variant="outline" className="flex-1">
                <Eye className="h-4 w-4 mr-2" />
                Review Details
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

