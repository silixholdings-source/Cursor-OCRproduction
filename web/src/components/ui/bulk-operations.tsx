'use client'

import React, { useState, useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { 
  CheckSquare, 
  Square, 
  Trash2, 
  Download, 
  Send, 
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2
} from 'lucide-react'
import { notifications } from '@/lib/notifications'

export interface BulkAction {
  id: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  variant?: 'default' | 'destructive' | 'outline'
  requiresConfirmation?: boolean
  confirmationTitle?: string
  confirmationMessage?: string
}

export interface BulkOperationsProps<T> {
  items: T[]
  selectedItems: string[]
  onSelectionChange: (selectedIds: string[]) => void
  getItemId: (item: T) => string
  actions: BulkAction[]
  onAction: (actionId: string, selectedIds: string[]) => Promise<void>
  className?: string
}

export function BulkOperations<T>({
  items,
  selectedItems,
  onSelectionChange,
  getItemId,
  actions,
  onAction,
  className
}: BulkOperationsProps<T>) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [confirmAction, setConfirmAction] = useState<BulkAction | null>(null)

  const isAllSelected = useMemo(() => {
    return items.length > 0 && selectedItems.length === items.length
  }, [items.length, selectedItems.length])

  const isIndeterminate = useMemo(() => {
    return selectedItems.length > 0 && selectedItems.length < items.length
  }, [selectedItems.length, items.length])

  const handleSelectAll = () => {
    if (isAllSelected) {
      onSelectionChange([])
    } else {
      onSelectionChange(items.map(getItemId))
    }
  }

  const handleActionClick = (action: BulkAction) => {
    if (selectedItems.length === 0) {
      notifications.warning('Please select items to perform this action')
      return
    }

    if (action.requiresConfirmation) {
      setConfirmAction(action)
    } else {
      executeAction(action)
    }
  }

  const executeAction = async (action: BulkAction) => {
    setIsProcessing(true)
    setConfirmAction(null)

    try {
      await onAction(action.id, selectedItems)
      notifications.success(
        `${action.label} completed for ${selectedItems.length} items`,
        'Bulk Operation Complete'
      )
      onSelectionChange([]) // Clear selection after successful action
    } catch (error) {
      notifications.error(
        `Failed to ${action.label.toLowerCase()}. Please try again.`,
        'Bulk Operation Failed'
      )
    } finally {
      setIsProcessing(false)
    }
  }

  if (selectedItems.length === 0) {
    return null
  }

  return (
    <>
      <div className={`flex items-center justify-between p-4 bg-muted/50 border rounded-lg ${className}`}>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              checked={isAllSelected}
              ref={(el) => {
                if (el) el.indeterminate = isIndeterminate
              }}
              onCheckedChange={handleSelectAll}
              aria-label="Select all items"
            />
            <span className="text-sm font-medium">
              {selectedItems.length} of {items.length} selected
            </span>
          </div>
          
          <Badge variant="secondary">
            {selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''}
          </Badge>
        </div>

        <div className="flex items-center space-x-2">
          {actions.map((action) => {
            const Icon = action.icon
            return (
              <Button
                key={action.id}
                variant={action.variant || 'outline'}
                size="sm"
                onClick={() => handleActionClick(action)}
                disabled={isProcessing}
                className="flex items-center space-x-1"
              >
                {isProcessing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Icon className="h-4 w-4" />
                )}
                <span>{action.label}</span>
              </Button>
            )
          })}
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onSelectionChange([])}
            disabled={isProcessing}
          >
            Clear
          </Button>
        </div>
      </div>

      {/* Confirmation Dialog */}
      <Dialog open={!!confirmAction} onOpenChange={() => setConfirmAction(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {confirmAction?.confirmationTitle || `Confirm ${confirmAction?.label}`}
            </DialogTitle>
            <DialogDescription>
              {confirmAction?.confirmationMessage || 
                `Are you sure you want to ${confirmAction?.label.toLowerCase()} ${selectedItems.length} selected items? This action cannot be undone.`
              }
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setConfirmAction(null)}
              disabled={isProcessing}
            >
              Cancel
            </Button>
            <Button
              variant={confirmAction?.variant === 'destructive' ? 'destructive' : 'default'}
              onClick={() => confirmAction && executeAction(confirmAction)}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  {confirmAction && <confirmAction.icon className="h-4 w-4 mr-2" />}
                  {confirmAction?.label}
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// Predefined bulk actions for common use cases
export const commonBulkActions = {
  approve: {
    id: 'approve',
    label: 'Approve',
    icon: CheckCircle,
    variant: 'default' as const,
    requiresConfirmation: true,
    confirmationTitle: 'Approve Selected Items',
    confirmationMessage: 'Are you sure you want to approve all selected items?'
  },
  reject: {
    id: 'reject',
    label: 'Reject',
    icon: XCircle,
    variant: 'destructive' as const,
    requiresConfirmation: true,
    confirmationTitle: 'Reject Selected Items',
    confirmationMessage: 'Are you sure you want to reject all selected items?'
  },
  delete: {
    id: 'delete',
    label: 'Delete',
    icon: Trash2,
    variant: 'destructive' as const,
    requiresConfirmation: true,
    confirmationTitle: 'Delete Selected Items',
    confirmationMessage: 'Are you sure you want to delete all selected items? This action cannot be undone.'
  },
  export: {
    id: 'export',
    label: 'Export',
    icon: Download,
    variant: 'outline' as const
  },
  send: {
    id: 'send',
    label: 'Send',
    icon: Send,
    variant: 'default' as const
  }
}


