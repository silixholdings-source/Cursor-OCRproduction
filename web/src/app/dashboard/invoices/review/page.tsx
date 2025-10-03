'use client'

import React, { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Brain,
  CheckCircle,
  AlertTriangle,
  FileText,
  Target,
  Eye,
  Download,
  Save,
  X,
  RefreshCw,
  Zap,
  Shield,
  TrendingUp,
  Users,
  Clock
} from 'lucide-react'
import { EnhancedOCRResults } from '@/components/invoice/enhanced-ocr-results'
import { ThreeWayMatchViewer } from '@/components/invoice/three-way-match-viewer'
import { useKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts'
import { notifications } from '@/lib/notifications'
import { apiClient } from '@/lib/api-client'

interface ReviewInvoice {
  id: string
  filename: string
  status: 'pending_review' | 'approved' | 'rejected' | 'processing'
  extractedData: any
  confidenceScore: number
  processingTime: number
  threeWayMatch?: any
  assignedReviewer?: string
  priority: 'high' | 'medium' | 'low'
  flags: string[]
}

export default function InvoiceReviewPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [invoices, setInvoices] = useState<ReviewInvoice[]>([])
  const [currentInvoiceIndex, setCurrentInvoiceIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [batchMode, setBatchMode] = useState(false)
  const [selectedInvoices, setSelectedInvoices] = useState<string[]>([])

  // Keyboard shortcuts for efficient review
  useKeyboardShortcuts([
    {
      key: 'ArrowRight',
      description: 'Next invoice',
      action: () => {
        if (currentInvoiceIndex < invoices.length - 1) {
          setCurrentInvoiceIndex(prev => prev + 1)
        }
      }
    },
    {
      key: 'ArrowLeft', 
      description: 'Previous invoice',
      action: () => {
        if (currentInvoiceIndex > 0) {
          setCurrentInvoiceIndex(prev => prev - 1)
        }
      }
    },
    {
      key: 'a',
      description: 'Approve current invoice',
      action: () => handleApprove(invoices[currentInvoiceIndex]?.id)
    },
    {
      key: 'r',
      description: 'Reject current invoice', 
      action: () => handleReject(invoices[currentInvoiceIndex]?.id)
    },
    {
      key: 'e',
      description: 'Edit current invoice',
      action: () => {/* Open edit mode */}
    },
    {
      key: '3',
      description: 'Run 3-way match',
      action: () => {/* Trigger 3-way match */}
    }
  ])

  useEffect(() => {
    loadPendingInvoices()
  }, [])

  const loadPendingInvoices = async () => {
    setIsLoading(true)
    try {
      const response = await apiClient.get('/api/v1/invoices/pending-review')
      setInvoices(response.data || [])
      
      if (response.data?.length > 0) {
        notifications.info(
          `${response.data.length} invoices ready for review`,
          'Review Queue',
          {
            label: 'Start Review',
            onClick: () => setCurrentInvoiceIndex(0)
          }
        )
      }
    } catch (error) {
      notifications.error('Failed to load pending invoices')
    } finally {
      setIsLoading(false)
    }
  }

  const handleApprove = async (invoiceId: string) => {
    try {
      await apiClient.post(`/api/v1/invoices/${invoiceId}/approve`)
      
      notifications.success('Invoice approved successfully')
      
      // Move to next invoice
      if (currentInvoiceIndex < invoices.length - 1) {
        setCurrentInvoiceIndex(prev => prev + 1)
      } else {
        router.push('/dashboard/invoices')
      }
      
      // Update local state
      setInvoices(prev => prev.filter(inv => inv.id !== invoiceId))
      
    } catch (error) {
      notifications.error('Failed to approve invoice')
    }
  }

  const handleReject = async (invoiceId: string) => {
    const reason = prompt('Please provide a reason for rejection:')
    if (!reason) return

    try {
      await apiClient.post(`/api/v1/invoices/${invoiceId}/reject`, { reason })
      
      notifications.warning('Invoice rejected')
      
      // Move to next invoice
      if (currentInvoiceIndex < invoices.length - 1) {
        setCurrentInvoiceIndex(prev => prev + 1)
      } else {
        router.push('/dashboard/invoices')
      }
      
      // Update local state
      setInvoices(prev => prev.filter(inv => inv.id !== invoiceId))
      
    } catch (error) {
      notifications.error('Failed to reject invoice')
    }
  }

  const handleBatchApprove = async () => {
    if (selectedInvoices.length === 0) {
      notifications.warning('Please select invoices to approve')
      return
    }

    try {
      await apiClient.post('/api/v1/invoices/batch-approve', {
        invoice_ids: selectedInvoices
      })
      
      notifications.success(`${selectedInvoices.length} invoices approved`)
      setSelectedInvoices([])
      loadPendingInvoices()
      
    } catch (error) {
      notifications.error('Batch approval failed')
    }
  }

  const currentInvoice = invoices[currentInvoiceIndex]
  const completionPercentage = invoices.length > 0 ? ((invoices.length - (currentInvoiceIndex + 1)) / invoices.length) * 100 : 0

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Brain className="h-12 w-12 mx-auto text-blue-600 mb-4 animate-pulse" />
          <h2 className="text-lg font-medium mb-2">Loading Invoice Review Queue</h2>
          <p className="text-gray-600">Preparing your invoices for review...</p>
        </div>
      </div>
    )
  }

  if (invoices.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <CheckCircle className="h-12 w-12 mx-auto text-green-600 mb-4" />
          <h2 className="text-lg font-medium mb-2">All Caught Up!</h2>
          <p className="text-gray-600 mb-4">No invoices pending review</p>
          <Button onClick={() => router.push('/dashboard/invoices')}>
            <FileText className="h-4 w-4 mr-2" />
            Back to Invoices
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header with Progress */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Brain className="h-6 w-6 mr-2 text-blue-600" />
              Invoice Review Dashboard
            </h1>
            <p className="text-gray-600">
              Review AI-processed invoices for accuracy and approval
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <Badge variant="outline" className="flex items-center">
              <Clock className="h-3 w-3 mr-1" />
              {invoices.length} pending
            </Badge>
            <Button
              variant="outline"
              onClick={() => setBatchMode(!batchMode)}
            >
              {batchMode ? 'Single Review' : 'Batch Review'}
            </Button>
            <Button variant="outline" onClick={loadPendingInvoices}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Review Progress</span>
            <span>{Math.round(completionPercentage)}% Complete</span>
          </div>
          <Progress value={completionPercentage} className="h-2" />
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        {batchMode ? (
          /* Batch Review Mode */
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Batch Review Mode
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {invoices.map((invoice, index) => (
                  <div key={invoice.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                    <input
                      type="checkbox"
                      checked={selectedInvoices.includes(invoice.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedInvoices(prev => [...prev, invoice.id])
                        } else {
                          setSelectedInvoices(prev => prev.filter(id => id !== invoice.id))
                        }
                      }}
                      className="h-4 w-4"
                      aria-label={`Select invoice ${invoice.filename}`}
                    />
                    <div className="flex-1">
                      <p className="font-medium">{invoice.filename}</p>
                      <p className="text-sm text-gray-600">
                        {invoice.extractedData?.vendor} • ${invoice.extractedData?.amount?.toFixed(2)}
                      </p>
                    </div>
                    <Badge className={
                      invoice.confidenceScore >= 0.95 ? 'bg-green-100 text-green-800' :
                      invoice.confidenceScore >= 0.85 ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }>
                      {(invoice.confidenceScore * 100).toFixed(1)}%
                    </Badge>
                  </div>
                ))}
                
                {selectedInvoices.length > 0 && (
                  <div className="flex justify-end space-x-2 pt-4 border-t">
                    <Button variant="outline" onClick={() => setSelectedInvoices([])}>
                      Clear Selection
                    </Button>
                    <Button onClick={handleBatchApprove}>
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Approve {selectedInvoices.length} Invoices
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          /* Single Review Mode */
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Invoice Queue Sidebar */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Review Queue</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {invoices.map((invoice, index) => (
                      <div
                        key={invoice.id}
                        className={`p-3 rounded-lg cursor-pointer transition-colors ${
                          index === currentInvoiceIndex 
                            ? 'bg-blue-100 border-blue-200' 
                            : 'hover:bg-gray-100'
                        }`}
                        onClick={() => setCurrentInvoiceIndex(index)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{invoice.filename}</p>
                            <p className="text-xs text-gray-600 truncate">
                              {invoice.extractedData?.vendor}
                            </p>
                          </div>
                          <Badge size="sm" className={
                            invoice.confidenceScore >= 0.95 ? 'bg-green-100 text-green-800' :
                            invoice.confidenceScore >= 0.85 ? 'bg-blue-100 text-blue-800' :
                            'bg-yellow-100 text-yellow-800'
                          }>
                            {(invoice.confidenceScore * 100).toFixed(0)}%
                          </Badge>
                        </div>
                        
                        {invoice.flags.length > 0 && (
                          <div className="mt-1 flex flex-wrap gap-1">
                            {invoice.flags.slice(0, 2).map((flag, i) => (
                              <Badge key={i} size="sm" variant="outline" className="text-xs">
                                {flag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Review Area */}
            <div className="lg:col-span-3">
              {currentInvoice && (
                <div className="space-y-6">
                  {/* Review Header */}
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="flex items-center">
                            <FileText className="h-5 w-5 mr-2" />
                            {currentInvoice.filename}
                          </CardTitle>
                          <p className="text-sm text-gray-600 mt-1">
                            Invoice {currentInvoiceIndex + 1} of {invoices.length} • 
                            Processed in {currentInvoice.processingTime}ms
                          </p>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Badge className={
                            currentInvoice.priority === 'high' ? 'bg-red-100 text-red-800' :
                            currentInvoice.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }>
                            {currentInvoice.priority.toUpperCase()} PRIORITY
                          </Badge>
                          
                          {currentInvoice.flags.map((flag, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {flag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <p className="text-sm text-gray-600">Vendor</p>
                          <p className="font-medium">{currentInvoice.extractedData?.vendor}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-600">Amount</p>
                          <p className="font-medium text-green-600">
                            ${currentInvoice.extractedData?.amount?.toFixed(2)}
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-600">Confidence</p>
                          <Badge className={
                            currentInvoice.confidenceScore >= 0.95 ? 'bg-green-100 text-green-800' :
                            currentInvoice.confidenceScore >= 0.85 ? 'bg-blue-100 text-blue-800' :
                            'bg-yellow-100 text-yellow-800'
                          }>
                            {(currentInvoice.confidenceScore * 100).toFixed(1)}%
                          </Badge>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-600">Status</p>
                          <Badge variant="outline">
                            {currentInvoice.status.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Review Tabs */}
                  <Tabs defaultValue="ocr-results" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="ocr-results" className="flex items-center">
                        <Brain className="h-4 w-4 mr-2" />
                        OCR Results
                      </TabsTrigger>
                      <TabsTrigger value="three-way-match" className="flex items-center">
                        <Target className="h-4 w-4 mr-2" />
                        3-Way Match
                      </TabsTrigger>
                      <TabsTrigger value="document-view" className="flex items-center">
                        <Eye className="h-4 w-4 mr-2" />
                        Original Document
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="ocr-results" className="space-y-4">
                      <EnhancedOCRResults
                        extractedData={currentInvoice.extractedData}
                        onSave={(data) => {
                          // Update invoice data
                          setInvoices(prev => 
                            prev.map(inv => 
                              inv.id === currentInvoice.id 
                                ? { ...inv, extractedData: data }
                                : inv
                            )
                          )
                          notifications.success('Invoice data updated')
                        }}
                        onReject={() => handleReject(currentInvoice.id)}
                        onReprocess={async () => {
                          try {
                            notifications.loading('Reprocessing invoice with enhanced AI...')
                            await apiClient.post(`/api/v1/invoices/${currentInvoice.id}/reprocess`)
                            loadPendingInvoices()
                          } catch (error) {
                            notifications.error('Reprocessing failed')
                          }
                        }}
                        showThreeWayMatch={true}
                      />
                    </TabsContent>

                    <TabsContent value="three-way-match" className="space-y-4">
                      <ThreeWayMatchViewer
                        invoiceId={currentInvoice.id}
                        poNumber={currentInvoice.extractedData?.poNumber}
                        onMatchComplete={(result) => {
                          setInvoices(prev => 
                            prev.map(inv => 
                              inv.id === currentInvoice.id 
                                ? { ...inv, threeWayMatch: result }
                                : inv
                            )
                          )
                        }}
                      />
                    </TabsContent>

                    <TabsContent value="document-view" className="space-y-4">
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center">
                            <Eye className="h-5 w-5 mr-2" />
                            Original Document
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="aspect-[8.5/11] bg-gray-100 rounded-lg flex items-center justify-center">
                            <div className="text-center">
                              <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                              <p className="text-gray-600">Document viewer would be displayed here</p>
                              <p className="text-sm text-gray-500 mt-2">
                                In production: PDF viewer, image viewer, annotation tools
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </TabsContent>
                  </Tabs>

                  {/* Navigation and Actions */}
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            onClick={() => setCurrentInvoiceIndex(prev => Math.max(0, prev - 1))}
                            disabled={currentInvoiceIndex === 0}
                          >
                            ← Previous
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => setCurrentInvoiceIndex(prev => Math.min(invoices.length - 1, prev + 1))}
                            disabled={currentInvoiceIndex === invoices.length - 1}
                          >
                            Next →
                          </Button>
                        </div>

                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            onClick={() => handleReject(currentInvoice.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <X className="h-4 w-4 mr-2" />
                            Reject
                          </Button>
                          <Button
                            onClick={() => handleApprove(currentInvoice.id)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Approve
                          </Button>
                        </div>
                      </div>
                      
                      {/* Keyboard Shortcuts Help */}
                      <div className="mt-4 pt-4 border-t text-xs text-gray-500">
                        <p>Keyboard shortcuts: ← → (navigate) • A (approve) • R (reject) • E (edit) • 3 (3-way match)</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
