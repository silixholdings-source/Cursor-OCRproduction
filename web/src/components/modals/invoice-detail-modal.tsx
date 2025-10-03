'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  FileText, 
  Building2, 
  DollarSign, 
  Calendar, 
  Edit,
  Trash2,
  X,
  Download,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle
} from 'lucide-react'

interface InvoiceDetailModalProps {
  invoice: any
  isOpen: boolean
  onClose: () => void
  onEdit?: (invoice: any) => void
  onDelete?: (invoiceId: string) => void
  onApprove?: (invoiceId: string) => void
  onReject?: (invoiceId: string) => void
}

export function InvoiceDetailModal({ 
  invoice, 
  isOpen, 
  onClose, 
  onEdit, 
  onDelete,
  onApprove,
  onReject
}: InvoiceDetailModalProps) {
  const [isLoading, setIsLoading] = useState(false)

  if (!invoice) return null

  const handleEdit = () => {
    if (onEdit) {
      onEdit(invoice)
    }
    onClose()
  }

  const handleDelete = () => {
    if (onDelete) {
      onDelete(invoice.id)
    }
    onClose()
  }

  const handleApprove = () => {
    if (onApprove) {
      onApprove(invoice.id)
    }
    onClose()
  }

  const handleReject = () => {
    if (onReject) {
      onReject(invoice.id)
    }
    onClose()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'approved': return 'Approved'
      case 'pending': return 'Pending'
      case 'rejected': return 'Rejected'
      default: return status
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircle className="h-4 w-4" />
      case 'pending': return <Clock className="h-4 w-4" />
      case 'rejected': return <XCircle className="h-4 w-4" />
      default: return <AlertTriangle className="h-4 w-4" />
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-gray-900">
            Invoice Details
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Invoice Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center">
                <FileText className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{invoice.id}</h2>
                <p className="text-lg text-gray-600">{invoice.vendor}</p>
                <div className="flex items-center mt-2">
                  <Badge className={getStatusColor(invoice.status)}>
                    <div className="flex items-center gap-1">
                      {getStatusIcon(invoice.status)}
                      {getStatusText(invoice.status)}
                    </div>
                  </Badge>
                </div>
              </div>
            </div>
            <div className="flex space-x-2">
              {invoice.status === 'pending' && (
                <>
                  <Button
                    variant="outline"
                    onClick={handleApprove}
                    className="flex items-center gap-2 text-green-600 hover:text-green-700"
                  >
                    <CheckCircle className="h-4 w-4" />
                    Approve
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleReject}
                    className="flex items-center gap-2 text-red-600 hover:text-red-700"
                  >
                    <XCircle className="h-4 w-4" />
                    Reject
                  </Button>
                </>
              )}
              <Button
                variant="outline"
                onClick={handleEdit}
                className="flex items-center gap-2"
              >
                <Edit className="h-4 w-4" />
                Edit
              </Button>
              <Button
                variant="outline"
                onClick={handleDelete}
                className="flex items-center gap-2 text-red-600 hover:text-red-700"
              >
                <Trash2 className="h-4 w-4" />
                Delete
              </Button>
            </div>
          </div>

          {/* Invoice Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Vendor Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-900">Vendor Name</p>
                  <p className="text-sm text-gray-600">{invoice.vendor}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Description</p>
                  <p className="text-sm text-gray-600">{invoice.description}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Financial Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-900">Amount</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {invoice.amount.toLocaleString('en-US', { 
                      style: 'currency', 
                      currency: 'USD' 
                    })}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Invoice Date</p>
                    <p className="text-sm text-gray-600">
                      {new Date(invoice.date + 'T00:00:00').toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Due Date</p>
                    <p className="text-sm text-gray-600">
                      {new Date(invoice.dueDate + 'T00:00:00').toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Status Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Status Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <div className="flex items-center space-x-3">
                    <div className="h-2 w-2 bg-blue-500 rounded-full"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Invoice Created</p>
                      <p className="text-sm text-gray-600">
                        {new Date(invoice.date).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-blue-100 text-blue-800">Completed</Badge>
                </div>
                
                {invoice.status === 'approved' && (
                  <div className="flex items-center justify-between py-3 border-b border-gray-200">
                    <div className="flex items-center space-x-3">
                      <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">Approved</p>
                        <p className="text-sm text-gray-600">
                          {invoice.approvedAt ? new Date(invoice.approvedAt).toLocaleString() : 'Recently'}
                        </p>
                      </div>
                    </div>
                    <Badge className="bg-green-100 text-green-800">Completed</Badge>
                  </div>
                )}

                {invoice.status === 'rejected' && (
                  <div className="flex items-center justify-between py-3 border-b border-gray-200">
                    <div className="flex items-center space-x-3">
                      <div className="h-2 w-2 bg-red-500 rounded-full"></div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">Rejected</p>
                        <p className="text-sm text-gray-600">
                          {invoice.rejectedAt ? new Date(invoice.rejectedAt).toLocaleString() : 'Recently'}
                        </p>
                      </div>
                    </div>
                    <Badge className="bg-red-100 text-red-800">Completed</Badge>
                  </div>
                )}

                {invoice.status === 'pending' && (
                  <div className="flex items-center justify-between py-3">
                    <div className="flex items-center space-x-3">
                      <div className="h-2 w-2 bg-yellow-500 rounded-full"></div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">Pending Approval</p>
                        <p className="text-sm text-gray-600">Awaiting review</p>
                      </div>
                    </div>
                    <Badge className="bg-yellow-100 text-yellow-800">In Progress</Badge>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button 
              variant="outline"
              onClick={() => {
                // Download invoice functionality
                const downloadUrl = `/api/invoices/${invoice.id}/download`
                const link = document.createElement('a')
                link.href = downloadUrl
                link.download = `${invoice.invoiceNumber}.pdf`
                document.body.appendChild(link)
                link.click()
                document.body.removeChild(link)
              }}
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Download
            </Button>
            <Button 
              onClick={handleEdit}
              className="flex items-center gap-2"
            >
              <Edit className="h-4 w-4" />
              Edit Invoice
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
