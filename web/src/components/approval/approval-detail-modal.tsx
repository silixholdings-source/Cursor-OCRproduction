'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { 
  X, 
  CheckCircle, 
  XCircle, 
  Clock, 
  FileText, 
  Building2, 
  DollarSign, 
  Calendar,
  User,
  MessageCircle,
  AlertTriangle,
  History
} from 'lucide-react'

interface ApprovalDetail {
  id: string
  invoiceId: string
  vendor: string
  amount: number
  status: 'pending' | 'approved' | 'rejected'
  submittedBy: string
  submittedAt: string
  dueDate?: string
  description: string
  priority: 'high' | 'medium' | 'low'
  category?: string
  lineItems?: Array<{
    description: string
    quantity: number
    unitPrice: number
    total: number
  }>
  attachments?: Array<{
    name: string
    type: string
    size: number
    url: string
  }>
  comments?: Array<{
    id: string
    author: string
    message: string
    timestamp: string
  }>
  approvalHistory?: Array<{
    action: string
    user: string
    timestamp: string
    comment?: string
  }>
}

interface ApprovalDetailModalProps {
  approval: ApprovalDetail | null
  isOpen: boolean
  onClose: () => void
  onApprove: (id: string, comment?: string) => void
  onReject: (id: string, reason: string) => void
  onComment: (id: string, comment: string) => void
}

export function ApprovalDetailModal({
  approval,
  isOpen,
  onClose,
  onApprove,
  onReject,
  onComment
}: ApprovalDetailModalProps) {
  const [comment, setComment] = useState('')
  const [rejectionReason, setRejectionReason] = useState('')
  const [showRejectForm, setShowRejectForm] = useState(false)

  if (!isOpen || !approval) return null

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleApprove = () => {
    onApprove(approval.id, comment)
    setComment('')
    onClose()
  }

  const handleReject = () => {
    if (rejectionReason.trim()) {
      onReject(approval.id, rejectionReason)
      setRejectionReason('')
      setShowRejectForm(false)
      onClose()
    }
  }

  const handleComment = () => {
    if (comment.trim()) {
      onComment(approval.id, comment)
      setComment('')
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Approval Request {approval.id}
            </h2>
            <p className="text-sm text-gray-600">
              Invoice {approval.invoiceId} • {approval.vendor}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Badge className={getPriorityColor(approval.priority)}>
              {approval.priority.toUpperCase()}
            </Badge>
            <Badge className={getStatusColor(approval.status)}>
              {approval.status.toUpperCase()}
            </Badge>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Request Details
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-500">Amount</Label>
                <p className="text-lg font-semibold text-gray-900 flex items-center">
                  <DollarSign className="h-4 w-4 mr-1" />
                  {approval.amount.toLocaleString('en-US', { 
                    style: 'currency', 
                    currency: 'USD' 
                  })}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-500">Vendor</Label>
                <p className="text-sm text-gray-900 flex items-center">
                  <Building2 className="h-4 w-4 mr-1" />
                  {approval.vendor}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-500">Submitted By</Label>
                <p className="text-sm text-gray-900 flex items-center">
                  <User className="h-4 w-4 mr-1" />
                  {approval.submittedBy}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-500">Submitted At</Label>
                <p className="text-sm text-gray-900 flex items-center">
                  <Calendar className="h-4 w-4 mr-1" />
                  {new Date(approval.submittedAt).toLocaleString()}
                </p>
              </div>
              {approval.dueDate && (
                <div>
                  <Label className="text-sm font-medium text-gray-500">Due Date</Label>
                  <p className="text-sm text-gray-900 flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    {new Date(approval.dueDate).toLocaleString()}
                  </p>
                </div>
              )}
              <div>
                <Label className="text-sm font-medium text-gray-500">Description</Label>
                <p className="text-sm text-gray-900">{approval.description}</p>
              </div>
            </CardContent>
          </Card>

          {/* Line Items */}
          {approval.lineItems && approval.lineItems.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Line Items</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {approval.lineItems.map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{item.description}</p>
                        <p className="text-sm text-gray-600">
                          Qty: {item.quantity} × ${item.unitPrice.toFixed(2)}
                        </p>
                      </div>
                      <p className="text-sm font-medium text-gray-900">
                        ${item.total.toFixed(2)}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Attachments */}
          {approval.attachments && approval.attachments.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Attachments</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {approval.attachments.map((attachment, index) => (
                    <div key={index} className="flex items-center justify-between p-2 border rounded-lg">
                      <div className="flex items-center">
                        <FileText className="h-4 w-4 mr-2 text-gray-400" />
                        <span className="text-sm text-gray-900">{attachment.name}</span>
                      </div>
                      <Button variant="ghost" size="sm">
                        Download
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Comments */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MessageCircle className="h-5 w-5 mr-2" />
                Comments
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {approval.comments && approval.comments.length > 0 ? (
                <div className="space-y-3">
                  {approval.comments.map((comment, index) => (
                    <div key={index} className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex justify-between items-start">
                        <p className="text-sm text-gray-900">{comment.message}</p>
                        <div className="text-xs text-gray-500">
                          {comment.author} • {new Date(comment.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No comments yet</p>
              )}
              
              <div className="flex space-x-2">
                <Textarea
                  placeholder="Add a comment..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  className="flex-1"
                />
                <Button onClick={handleComment} disabled={!comment.trim()}>
                  Add Comment
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Approval History */}
          {approval.approvalHistory && approval.approvalHistory.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <History className="h-5 w-5 mr-2" />
                  Approval History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {approval.approvalHistory.map((entry, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        {entry.action === 'approved' ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : entry.action === 'rejected' ? (
                          <XCircle className="h-5 w-5 text-red-600" />
                        ) : (
                          <Clock className="h-5 w-5 text-yellow-600" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-900">
                          {entry.action.charAt(0).toUpperCase() + entry.action.slice(1)} by {entry.user}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(entry.timestamp).toLocaleString()}
                        </p>
                        {entry.comment && (
                          <p className="text-sm text-gray-600 mt-1">{entry.comment}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          {approval.status === 'pending' && (
            <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
              {!showRejectForm ? (
                <>
                  <Button
                    variant="outline"
                    onClick={() => setShowRejectForm(true)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    Reject
                  </Button>
                  <Button
                    onClick={handleApprove}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Approve
                  </Button>
                </>
              ) : (
                <div className="flex-1 space-y-4">
                  <div>
                    <Label htmlFor="rejection-reason">Rejection Reason</Label>
                    <Textarea
                      id="rejection-reason"
                      placeholder="Please provide a reason for rejection..."
                      value={rejectionReason}
                      onChange={(e) => setRejectionReason(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => setShowRejectForm(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleReject}
                      disabled={!rejectionReason.trim()}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Reject Request
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}





































