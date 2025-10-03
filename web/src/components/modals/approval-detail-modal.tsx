'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { 
  FileText, 
  Building2, 
  DollarSign, 
  Calendar, 
  Edit,
  Trash2,
  X,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  User,
  MessageSquare
} from 'lucide-react'

interface ApprovalDetailModalProps {
  approval: any
  isOpen: boolean
  onClose: () => void
  onApprove?: (approvalId: string, comment?: string) => void
  onReject?: (approvalId: string, reason?: string) => void
  onEdit?: (approval: any) => void
  onDelete?: (approvalId: string) => void
}

export function ApprovalDetailModal({ 
  approval, 
  isOpen, 
  onClose, 
  onApprove,
  onReject,
  onEdit,
  onDelete
}: ApprovalDetailModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [comment, setComment] = useState('')
  const [rejectionReason, setRejectionReason] = useState('')
  const [showCommentForm, setShowCommentForm] = useState(false)
  const [showRejectionForm, setShowRejectionForm] = useState(false)

  if (!approval) return null

  const handleApprove = () => {
    if (onApprove) {
      onApprove(approval.id, comment)
    }
    setComment('')
    setShowCommentForm(false)
    onClose()
  }

  const handleReject = () => {
    if (onReject) {
      onReject(approval.id, rejectionReason)
    }
    setRejectionReason('')
    setShowRejectionForm(false)
    onClose()
  }

  const handleEdit = () => {
    if (onEdit) {
      onEdit(approval)
    }
    onClose()
  }

  const handleDelete = () => {
    if (onDelete) {
      onDelete(approval.id)
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-gray-900">
            Approval Request Details
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Approval Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center">
                <FileText className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{approval.id}</h2>
                <p className="text-lg text-gray-600">{approval.vendor}</p>
                <div className="flex items-center mt-2 space-x-2">
                  <Badge className={getStatusColor(approval.status)}>
                    {getStatusText(approval.status)}
                  </Badge>
                  <Badge className={getPriorityColor(approval.priority)}>
                    {approval.priority.toUpperCase()}
                  </Badge>
                </div>
              </div>
            </div>
            <div className="flex space-x-2">
              {approval.status === 'pending' && (
                <>
                  <Button
                    variant="outline"
                    onClick={() => setShowCommentForm(true)}
                    className="flex items-center gap-2 text-green-600 hover:text-green-700"
                  >
                    <CheckCircle className="h-4 w-4" />
                    Approve
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowRejectionForm(true)}
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

          {/* Approval Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Request Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-900">Invoice ID</p>
                  <p className="text-sm text-gray-600">{approval.invoiceId}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Description</p>
                  <p className="text-sm text-gray-600">{approval.description}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Submitted By</p>
                  <p className="text-sm text-gray-600">{approval.submittedBy}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Submitted At</p>
                  <p className="text-sm text-gray-600">
                    {new Date(approval.submittedAt).toLocaleString()}
                  </p>
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
                    {approval.amount.toLocaleString('en-US', { 
                      style: 'currency', 
                      currency: 'USD' 
                    })}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Due Date</p>
                  <p className="text-sm text-gray-600">
                    {approval.dueDate ? new Date(approval.dueDate + 'T00:00:00').toLocaleDateString() : 'Not specified'}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Approval Status */}
          {approval.status !== 'pending' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {approval.status === 'approved' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  Approval Decision
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {approval.status === 'approved' ? 'Approved By' : 'Rejected By'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {approval.status === 'approved' ? approval.approvedBy : approval.rejectedBy}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {approval.status === 'approved' ? 'Approved At' : 'Rejected At'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {approval.status === 'approved' 
                        ? (approval.approvedAt ? new Date(approval.approvedAt).toLocaleString() : 'Recently')
                        : (approval.rejectedAt ? new Date(approval.rejectedAt).toLocaleString() : 'Recently')
                      }
                    </p>
                  </div>
                </div>
                {approval.rejectionReason && (
                  <div>
                    <p className="text-sm font-medium text-gray-900">Rejection Reason</p>
                    <p className="text-sm text-gray-600">{approval.rejectionReason}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Comment/Rejection Forms */}
          {showCommentForm && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Add Approval Comment
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Add a comment for this approval..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  rows={3}
                />
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setShowCommentForm(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleApprove}>
                    Approve with Comment
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {showRejectionForm && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <XCircle className="h-5 w-5" />
                  Rejection Reason
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Please provide a reason for rejection..."
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  rows={3}
                  required
                />
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setShowRejectionForm(false)}>
                    Cancel
                  </Button>
                  <Button 
                    onClick={handleReject}
                    disabled={!rejectionReason.trim()}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    Reject
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            {approval.status === 'pending' && (
              <Button 
                onClick={() => setShowCommentForm(true)}
                className="flex items-center gap-2"
              >
                <MessageSquare className="h-4 w-4" />
                Add Comment
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
