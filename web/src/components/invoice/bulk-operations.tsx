'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  CheckCircle, 
  XCircle, 
  Download, 
  Trash2, 
  Send, 
  Archive,
  FileText,
  AlertTriangle,
  Zap,
  Clock
} from 'lucide-react'
import { useWebSocket } from '@/hooks/use-websocket'
import { formatCurrency } from '@/lib/currency'

interface Invoice {
  id: string
  vendor: string
  amount: number
  currency: string
  status: string
  date: string
  invoiceNumber: string
}

interface BulkOperationsProps {
  invoices: Invoice[]
  onSelectionChange?: (selectedIds: string[]) => void
  onBulkAction?: (action: string, invoiceIds: string[]) => void
}

export function BulkOperations({ invoices, onSelectionChange, onBulkAction }: BulkOperationsProps) {
  const [selectedInvoices, setSelectedInvoices] = useState<string[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingAction, setProcessingAction] = useState('')

  // Real-time updates for bulk operations
  const { isConnected } = useWebSocket('ws://localhost:8001/ws', {
    onMessage: (message) => {
      if (message.type === 'bulk_operation_complete') {
        setIsProcessing(false)
        setProcessingAction('')
        setSelectedInvoices([])
      }
    }
  })

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const allIds = invoices.map(inv => inv.id)
      setSelectedInvoices(allIds)
      onSelectionChange?.(allIds)
    } else {
      setSelectedInvoices([])
      onSelectionChange?.([])
    }
  }

  const handleSelectInvoice = (invoiceId: string, checked: boolean) => {
    let newSelection: string[]
    if (checked) {
      newSelection = [...selectedInvoices, invoiceId]
    } else {
      newSelection = selectedInvoices.filter(id => id !== invoiceId)
    }
    setSelectedInvoices(newSelection)
    onSelectionChange?.(newSelection)
  }

  const handleBulkAction = async (action: string) => {
    if (selectedInvoices.length === 0) return

    setIsProcessing(true)
    setProcessingAction(action)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/api/v1/invoices/bulk/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          invoice_ids: selectedInvoices
        })
      })

      if (response.ok) {
        onBulkAction?.(action, selectedInvoices)
      }
    } catch (error) {
      console.error('Bulk operation failed:', error)
    }

    // Simulate processing time
    setTimeout(() => {
      setIsProcessing(false)
      setProcessingAction('')
      setSelectedInvoices([])
    }, 2000)
  }

  const getTotalAmount = () => {
    return selectedInvoices.reduce((total, id) => {
      const invoice = invoices.find(inv => inv.id === id)
      return total + (invoice?.amount || 0)
    }, 0)
  }

  const getStatusCounts = () => {
    const counts = { pending: 0, approved: 0, rejected: 0 }
    selectedInvoices.forEach(id => {
      const invoice = invoices.find(inv => inv.id === id)
      if (invoice) {
        if (invoice.status === 'pending_approval') counts.pending++
        else if (invoice.status === 'approved') counts.approved++
        else if (invoice.status === 'rejected') counts.rejected++
      }
    })
    return counts
  }

  const statusCounts = getStatusCounts()

  return (
    <div className="space-y-4">
      {/* Bulk Selection Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-blue-600" />
              <span>Bulk Operations</span>
              {isConnected && (
                <Badge className="bg-green-100 text-green-800" size="sm">
                  Real-time
                </Badge>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="select-all"
                checked={selectedInvoices.length === invoices.length && invoices.length > 0}
                onCheckedChange={handleSelectAll}
              />
              <label htmlFor="select-all" className="text-sm font-medium">
                Select All ({invoices.length})
              </label>
            </div>
          </CardTitle>
        </CardHeader>
        
        {selectedInvoices.length > 0 && (
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <Badge variant="outline" className="px-3 py-1">
                  {selectedInvoices.length} selected
                </Badge>
                <Badge className="bg-blue-100 text-blue-800 px-3 py-1">
                  Total: {formatCurrency(getTotalAmount(), 'USD')}
                </Badge>
                {statusCounts.pending > 0 && (
                  <Badge className="bg-yellow-100 text-yellow-800 px-2 py-1">
                    {statusCounts.pending} pending
                  </Badge>
                )}
                {statusCounts.approved > 0 && (
                  <Badge className="bg-green-100 text-green-800 px-2 py-1">
                    {statusCounts.approved} approved
                  </Badge>
                )}
                {statusCounts.rejected > 0 && (
                  <Badge className="bg-red-100 text-red-800 px-2 py-1">
                    {statusCounts.rejected} rejected
                  </Badge>
                )}
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                className="bg-green-600 hover:bg-green-700"
                onClick={() => handleBulkAction('approve')}
                disabled={isProcessing || statusCounts.pending === 0}
              >
                {isProcessing && processingAction === 'approve' ? (
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <CheckCircle className="h-4 w-4 mr-2" />
                )}
                Approve All ({statusCounts.pending})
              </Button>

              <Button
                size="sm"
                variant="outline"
                className="border-red-600 text-red-600 hover:bg-red-50"
                onClick={() => handleBulkAction('reject')}
                disabled={isProcessing || statusCounts.pending === 0}
              >
                {isProcessing && processingAction === 'reject' ? (
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <XCircle className="h-4 w-4 mr-2" />
                )}
                Reject All
              </Button>

              <Button
                size="sm"
                variant="outline"
                onClick={() => handleBulkAction('download')}
                disabled={isProcessing}
              >
                {isProcessing && processingAction === 'download' ? (
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Download className="h-4 w-4 mr-2" />
                )}
                Download All
              </Button>

              <Button
                size="sm"
                variant="outline"
                onClick={() => handleBulkAction('archive')}
                disabled={isProcessing}
              >
                {isProcessing && processingAction === 'archive' ? (
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Archive className="h-4 w-4 mr-2" />
                )}
                Archive
              </Button>

              <Button
                size="sm"
                variant="outline"
                className="border-red-600 text-red-600 hover:bg-red-50"
                onClick={() => handleBulkAction('delete')}
                disabled={isProcessing}
              >
                {isProcessing && processingAction === 'delete' ? (
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4 mr-2" />
                )}
                Delete
              </Button>
            </div>

            {isProcessing && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-blue-600 animate-spin" />
                  <span className="text-sm text-blue-800">
                    Processing {processingAction} for {selectedInvoices.length} invoices...
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        )}
      </Card>

      {/* Invoice List with Selection */}
      <div className="space-y-2">
        {invoices.map((invoice) => (
          <Card key={invoice.id} className={`transition-all ${selectedInvoices.includes(invoice.id) ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:shadow-md'}`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <Checkbox
                    checked={selectedInvoices.includes(invoice.id)}
                    onCheckedChange={(checked) => handleSelectInvoice(invoice.id, checked as boolean)}
                  />
                  <FileText className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="font-medium">{invoice.vendor}</div>
                    <div className="text-sm text-gray-600">{invoice.invoiceNumber}</div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="font-bold">{formatCurrency(invoice.amount, invoice.currency)}</div>
                    <div className="text-sm text-gray-600">{invoice.date}</div>
                  </div>
                  
                  <Badge 
                    className={
                      invoice.status === 'approved' ? 'bg-green-100 text-green-800' :
                      invoice.status === 'rejected' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }
                  >
                    {invoice.status.replace('_', ' ')}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

