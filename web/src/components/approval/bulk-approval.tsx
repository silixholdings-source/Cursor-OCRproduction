'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { EnhancedButton } from '@/components/ui/enhanced-button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { useAsyncAction } from '@/hooks/use-async-action'
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  DollarSign,
  Users,
  FileText,
  Loader2
} from 'lucide-react'

interface ApprovalItem {
  id: string
  invoiceId: string
  vendor: string
  amount: number
  priority: 'high' | 'medium' | 'low'
  submittedBy: string
  submittedAt: string
  description: string
}

interface BulkApprovalProps {
  items: ApprovalItem[]
  onBulkApprove: (ids: string[], comment?: string) => void
  onBulkReject: (ids: string[], reason: string) => void
  onSelectAll: (selected: boolean) => void
  onSelectItem: (id: string, selected: boolean) => void
  selectedItems: string[]
  isProcessing: boolean
}

export function BulkApproval({
  items,
  onBulkApprove,
  onBulkReject,
  onSelectAll,
  onSelectItem,
  selectedItems,
  isProcessing
}: BulkApprovalProps) {
  const [showBulkActions, setShowBulkActions] = useState(false)
  const [bulkComment, setBulkComment] = useState('')
  const [bulkReason, setBulkReason] = useState('')
  const [showRejectForm, setShowRejectForm] = useState(false)

  const totalAmount = selectedItems.reduce((sum, id) => {
    const item = items.find(i => i.id === id)
    return sum + (item?.amount || 0)
  }, 0)

  // Enhanced bulk actions with proper UX
  const bulkApproveAction = useAsyncAction(
    async () => {
      await onBulkApprove(selectedItems, bulkComment)
      setBulkComment('')
      setShowBulkActions(false)
    },
    {
      successMessage: `Successfully approved ${selectedItems.length} invoices`,
      errorMessage: 'Failed to approve invoices',
      confirmAction: true,
      confirmMessage: `Are you sure you want to approve ${selectedItems.length} invoices with a total value of $${totalAmount.toLocaleString()}?`
    }
  )

  const bulkRejectAction = useAsyncAction(
    async () => {
      if (!bulkReason.trim()) {
        throw new Error('Rejection reason is required')
      }
      await onBulkReject(selectedItems, bulkReason)
      setBulkReason('')
      setShowRejectForm(false)
      setShowBulkActions(false)
    },
    {
      successMessage: `Successfully rejected ${selectedItems.length} invoices`,
      errorMessage: 'Failed to reject invoices',
      confirmAction: true,
      confirmMessage: `Are you sure you want to reject ${selectedItems.length} invoices? This action cannot be undone.`
    }
  )

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-4">
      {/* Bulk Selection Header */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Checkbox
                checked={selectedItems.length === items.length && items.length > 0}
                onCheckedChange={(checked) => onSelectAll(checked as boolean)}
                className="h-4 w-4"
              />
              <span className="text-sm font-medium text-gray-700">
                Select All ({items.length} items)
              </span>
              {selectedItems.length > 0 && (
                <Badge variant="outline">
                  {selectedItems.length} selected
                </Badge>
              )}
            </div>
            
            {selectedItems.length > 0 && (
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowBulkActions(true)}
                  disabled={isProcessing}
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Bulk Actions
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    onSelectAll(false)
                    setShowBulkActions(false)
                  }}
                >
                  Clear Selection
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Bulk Actions Summary */}
      {selectedItems.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">
                    {selectedItems.length} items selected
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-900">
                    Total: ${totalAmount.toLocaleString('en-US', { 
                      style: 'currency', 
                      currency: 'USD' 
                    })}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600">
                    {new Set(selectedItems.map(id => 
                      items.find(i => i.id === id)?.submittedBy
                    )).size} submitters
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bulk Actions Modal */}
      {showBulkActions && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Bulk Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                You are about to perform bulk actions on {selectedItems.length} items 
                with a total value of ${totalAmount.toLocaleString('en-US', { 
                  style: 'currency', 
                  currency: 'USD' 
                })}.
              </p>
            </div>

            {!showRejectForm ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Comment (Optional)
                  </label>
                  <textarea
                    value={bulkComment}
                    onChange={(e) => setBulkComment(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    rows={3}
                    placeholder="Add a comment for all selected items..."
                  />
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowBulkActions(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowRejectForm(true)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <XCircle className="h-4 w-4 mr-1" />
                    Reject All
                  </Button>
                  <EnhancedButton
                    onClick={bulkApproveAction.execute}
                    loading={bulkApproveAction.isLoading}
                    loadingText="Approving..."
                    success={bulkApproveAction.success}
                    successText="Approved!"
                    variant="success"
                    icon={<CheckCircle className="h-4 w-4" />}
                  >
                    Approve All
                  </EnhancedButton>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rejection Reason *
                  </label>
                  <textarea
                    value={bulkReason}
                    onChange={(e) => setBulkReason(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    rows={3}
                    placeholder="Please provide a reason for rejecting all selected items..."
                    required
                  />
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowRejectForm(false)}
                  >
                    Back
                  </Button>
                  <EnhancedButton
                    onClick={bulkRejectAction.execute}
                    loading={bulkRejectAction.isLoading}
                    loadingText="Rejecting..."
                    success={bulkRejectAction.success}
                    successText="Rejected!"
                    variant="destructive"
                    disabled={!bulkReason.trim()}
                    icon={<XCircle className="h-4 w-4" />}
                  >
                    Reject All
                  </EnhancedButton>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Selected Items List */}
      {selectedItems.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Selected Items</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {selectedItems.map(id => {
                const item = items.find(i => i.id === id)
                if (!item) return null
                
                return (
                  <div key={id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Checkbox
                        checked={true}
                        onCheckedChange={(checked) => onSelectItem(id, checked as boolean)}
                        className="h-4 w-4"
                      />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {item.id} • {item.vendor}
                        </p>
                        <p className="text-xs text-gray-500">
                          {item.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getPriorityColor(item.priority)}>
                        {item.priority.toUpperCase()}
                      </Badge>
                      <span className="text-sm font-medium text-gray-900">
                        ${item.amount.toLocaleString('en-US', { 
                          style: 'currency', 
                          currency: 'USD' 
                        })}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}















