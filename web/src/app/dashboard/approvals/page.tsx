'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ApprovalWorkflow } from '@/components/approval/approval-workflow'
import { BulkApproval } from '@/components/approval/bulk-approval'
import { ApprovalDetailModal } from '@/components/modals/approval-detail-modal'
import { exportApprovalsToCSV } from '@/lib/csv-export'
import { MoreOptionsModal } from '@/components/modals/more-options-modal'
import { DeleteConfirmationDialog } from '@/components/modals/delete-confirmation-dialog'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Eye, 
  FileText,
  Calendar,
  DollarSign,
  Building2,
  Settings,
  Users,
  AlertTriangle,
  Download,
  RefreshCw,
  MoreVertical,
  Filter,
  Search
} from 'lucide-react'

interface EditApprovalFormProps {
  approval: any
  onSave: (updatedApproval: any) => void
  onCancel: () => void
}

function EditApprovalForm({ approval, onSave, onCancel }: EditApprovalFormProps) {
  const [formData, setFormData] = useState({
    vendor: approval?.vendor || '',
    amount: approval?.amount || 0,
    description: approval?.description || '',
    priority: approval?.priority || 'medium'
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const updatedApproval = {
      ...approval,
      ...formData
    }
    onSave(updatedApproval)
  }

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="vendor" className="block text-sm font-medium mb-2">Vendor</label>
          <input
            id="vendor"
            type="text"
            value={formData.vendor}
            onChange={(e) => handleChange('vendor', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
        <div>
          <label htmlFor="amount" className="block text-sm font-medium mb-2">Amount</label>
          <input
            id="amount"
            type="number"
            step="0.01"
            value={formData.amount}
            onChange={(e) => handleChange('amount', parseFloat(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>
      </div>
      
      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-2">Description</label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <div>
        <label htmlFor="priority" className="block text-sm font-medium mb-2">Priority</label>
        <select
          id="priority"
          value={formData.priority}
          onChange={(e) => handleChange('priority', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          Save Changes
        </Button>
      </div>
    </form>
  )
}

export default function ApprovalsPage() {
  const [filterStatus, setFilterStatus] = useState('pending')
  const [selectedApproval, setSelectedApproval] = useState<any>(null)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [selectedItems, setSelectedItems] = useState<string[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('list') // 'list', 'workflow', 'bulk'
  const [showMoreOptions, setShowMoreOptions] = useState(false)
  const [selectedItem, setSelectedItem] = useState<{id: string, name: string} | null>(null)
  const [editingApproval, setEditingApproval] = useState<any>(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false)
  const [deleteConfirmationData, setDeleteConfirmationData] = useState<{
    title: string
    description: string
    itemName: string
    itemType: string
    onConfirm: () => void
  } | null>(null)

  // Approvals data state
  const [approvals, setApprovals] = useState([
    {
      id: 'APP-001',
      invoiceId: 'INV-001',
      vendor: 'Acme Corp',
      amount: 1250.00,
      status: 'pending',
      submittedBy: 'John Doe',
      submittedAt: '2024-01-15T10:30:00Z',
      dueDate: '2024-01-20T17:00:00Z',
      description: 'Office supplies and equipment',
      priority: 'high'
    },
    {
      id: 'APP-002',
      invoiceId: 'INV-002',
      vendor: 'Tech Solutions Inc',
      amount: 3200.50,
      status: 'approved',
      submittedBy: 'Jane Smith',
      submittedAt: '2024-01-14T14:20:00Z',
      approvedBy: 'Admin User',
      approvedAt: '2024-01-15T09:15:00Z',
      description: 'Software licensing and support',
      priority: 'medium'
    },
    {
      id: 'APP-003',
      invoiceId: 'INV-003',
      vendor: 'Global Services Ltd',
      amount: 875.25,
      status: 'rejected',
      submittedBy: 'Mike Johnson',
      submittedAt: '2024-01-13T16:45:00Z',
      rejectedBy: 'Admin User',
      rejectedAt: '2024-01-14T11:30:00Z',
      rejectionReason: 'Insufficient documentation',
      description: 'Consulting services',
      priority: 'low'
    },
    {
      id: 'APP-004',
      invoiceId: 'INV-004',
      vendor: 'Office Depot',
      amount: 450.00,
      status: 'pending',
      submittedBy: 'Sarah Wilson',
      submittedAt: '2024-01-12T08:15:00Z',
      dueDate: '2024-01-17T17:00:00Z',
      description: 'Office furniture',
      priority: 'medium'
    }
  ])

  const filteredApprovals = approvals.filter(approval => {
    const matchesSearch = approval.vendor.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         approval.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         approval.invoiceId.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || approval.status === filterStatus
    return matchesSearch && matchesStatus
  })

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

  const handleApprove = (approvalId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsProcessing(true)
    
    setTimeout(() => {
      setApprovals(prev => prev.map(approval => 
        approval.id === approvalId 
          ? { 
              ...approval, 
              status: 'approved',
              approvedBy: 'Current User',
              approvedAt: new Date().toISOString()
            }
          : approval
      ))
      setIsProcessing(false)
      console.log('✅ Approval approved successfully:', approvalId)
    }, 1000)
  }

  const handleReject = (approvalId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsProcessing(true)
    
    setTimeout(() => {
      setApprovals(prev => prev.map(approval => 
        approval.id === approvalId 
          ? { 
              ...approval, 
              status: 'rejected',
              rejectedBy: 'Current User',
              rejectedAt: new Date().toISOString(),
              rejectionReason: 'Rejected by approver'
            }
          : approval
      ))
      setIsProcessing(false)
      console.log('✅ Approval rejected successfully:', approvalId)
    }, 1000)
  }

  const handleViewApproval = (approval: any, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setSelectedApproval(approval)
    setShowDetailModal(true)
    console.log('✅ View approval clicked:', approval.id)
  }

  const handleExport = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsLoading(true)
    
    try {
      exportApprovalsToCSV(filteredApprovals, 'approvals-export.csv')
      console.log('✅ Approvals exported successfully')
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefresh = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsLoading(true)
    
    setTimeout(() => {
      setIsLoading(false)
      console.log('✅ Approvals data refreshed')
    }, 1000)
  }

  const handleFilterApply = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('✅ Filters applied')
  }

  const handleFilterClear = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setSearchTerm('')
    setFilterStatus('all')
    setSelectedItems([])
    console.log('✅ All filters cleared')
  }

  const handleMoreOptions = (approval: any, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setSelectedItem({ id: approval.id, name: approval.title || approval.id })
    setShowMoreOptions(true)
    console.log('✅ More options for approval:', approval.id)
  }

  const handleEditApproval = (approval: any) => {
    setEditingApproval(approval)
    setShowEditModal(true)
    console.log('✅ Edit approval clicked:', approval.id)
  }

  const handleSaveEdit = (updatedApproval: any) => {
    setApprovals(prev => prev.map(approval => 
      approval.id === updatedApproval.id ? updatedApproval : approval
    ))
    setEditingApproval(null)
    setShowEditModal(false)
    console.log('✅ Approval updated successfully:', updatedApproval.id)
  }

  const handleCancelEdit = () => {
    setEditingApproval(null)
    setShowEditModal(false)
  }

  const handleApproveWithComment = (id: string, comment?: string) => {
    setIsProcessing(true)
    console.log('Approving with comment:', id, comment)
    // Simulate API call
    setTimeout(() => {
      setIsProcessing(false)
      setShowDetailModal(false)
    }, 1000)
  }

  const handleRejectWithReason = (id: string, reason: string) => {
    setIsProcessing(true)
    console.log('Rejecting with reason:', id, reason)
    // Simulate API call
    setTimeout(() => {
      setIsProcessing(false)
      setShowDetailModal(false)
    }, 1000)
  }

  const handleAddComment = (id: string, comment: string) => {
    console.log('Adding comment:', id, comment)
    // In a real app, this would make an API call
  }

  const handleBulkApprove = async (ids: string[], comment?: string) => {
    setIsProcessing(true)
    try {
      const response = await fetch('/api/v1/approvals/bulk/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          approval_ids: ids,
          comment: comment || ''
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ Bulk approval successful:', result)
        
        // Update local state
        setApprovals(prev => prev.map(approval => 
          ids.includes(approval.id) 
            ? { 
                ...approval, 
                status: 'approved',
                approvedBy: 'Current User',
                approvedAt: new Date().toISOString()
              }
            : approval
        ))
        
        // Show success notification
        alert(`Successfully approved ${result.approved_count} invoices`)
      } else {
        throw new Error('Failed to bulk approve')
      }
    } catch (error) {
      console.error('Bulk approval failed:', error)
      alert('Failed to approve invoices. Please try again.')
    } finally {
      setIsProcessing(false)
      setSelectedItems([])
    }
  }

  const handleBulkReject = async (ids: string[], reason: string) => {
    setIsProcessing(true)
    try {
      const response = await fetch('/api/v1/approvals/bulk/reject', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          approval_ids: ids,
          reason: reason
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('✅ Bulk rejection successful:', result)
        
        // Update local state
        setApprovals(prev => prev.map(approval => 
          ids.includes(approval.id) 
            ? { 
                ...approval, 
                status: 'rejected',
                rejectedBy: 'Current User',
                rejectedAt: new Date().toISOString(),
                rejectionReason: reason
              }
            : approval
        ))
        
        // Show success notification
        alert(`Successfully rejected ${result.rejected_count} invoices`)
      } else {
        throw new Error('Failed to bulk reject')
      }
    } catch (error) {
      console.error('Bulk rejection failed:', error)
      alert('Failed to reject invoices. Please try again.')
    } finally {
      setIsProcessing(false)
      setSelectedItems([])
    }
  }

  const handleSelectAll = (selected: boolean) => {
    if (selected) {
      setSelectedItems(filteredApprovals.map(a => a.id))
    } else {
      setSelectedItems([])
    }
  }

  const handleSelectItem = (id: string, selected: boolean) => {
    if (selected) {
      setSelectedItems(prev => [...prev, id])
    } else {
      setSelectedItems(prev => prev.filter(item => item !== id))
    }
  }

  return (
    <>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Approvals</h1>
            <p className="mt-2 text-gray-600">
              Review and approve pending requests with workflow management
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button 
              variant="outline" 
              onClick={handleRefresh}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button 
              variant="outline" 
              onClick={handleExport}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Export
            </Button>
            <div className="flex gap-2">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
                aria-label="Filter by status"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <Button 
                variant={activeTab === 'list' ? 'default' : 'outline'}
                onClick={() => setActiveTab('list')}
                size="sm"
              >
                <FileText className="h-4 w-4 mr-1" />
                List View
              </Button>
              <Button 
                variant={activeTab === 'workflow' ? 'default' : 'outline'}
                onClick={() => setActiveTab('workflow')}
                size="sm"
              >
                <Settings className="h-4 w-4 mr-1" />
                Workflow
              </Button>
              <Button 
                variant={activeTab === 'bulk' ? 'default' : 'outline'}
                onClick={() => setActiveTab('bulk')}
                size="sm"
              >
                <Users className="h-4 w-4 mr-1" />
                Bulk Actions
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Pending
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {approvals.filter(a => a.status === 'pending').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Approved
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {approvals.filter(a => a.status === 'approved').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Rejected
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {approvals.filter(a => a.status === 'rejected').length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Value
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${approvals.reduce((sum, a) => sum + a.amount, 0).toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'bulk' && (
        <BulkApproval
          items={filteredApprovals}
          onBulkApprove={handleBulkApprove}
          onBulkReject={handleBulkReject}
          onSelectAll={handleSelectAll}
          onSelectItem={handleSelectItem}
          selectedItems={selectedItems}
          isProcessing={isProcessing}
        />
      )}

      {activeTab === 'workflow' && (
        <ApprovalWorkflow
          workflowId="default-workflow"
          steps={[
            {
              id: 'step-1',
              name: 'Manager Approval',
              type: 'approval',
              approver: 'John Manager',
              status: 'completed',
              completedAt: '2024-01-15T10:30:00Z',
              completedBy: 'John Manager',
              order: 1
            },
            {
              id: 'step-2',
              name: 'Finance Review',
              type: 'approval',
              approver: 'Jane Finance',
              status: 'pending',
              order: 2
            },
            {
              id: 'step-3',
              name: 'Final Approval',
              type: 'approval',
              approver: 'Admin User',
              status: 'pending',
              order: 3
            }
          ]}
          currentStep={1}
          onStepComplete={(stepId, action, comment) => {
            console.log('Step completed:', stepId, action, comment)
          }}
          onStepSkip={(stepId) => {
            console.log('Step skipped:', stepId)
          }}
          canApprove={true}
        />
      )}

      {activeTab === 'list' && (
        <>
          {/* Search and Filters */}
          <div className="mb-6 flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search approvals..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={handleFilterApply}
                className="flex items-center gap-2"
              >
                <Filter className="h-4 w-4" />
                Apply Filters
              </Button>
              <Button 
                variant="outline" 
                onClick={handleFilterClear}
                className="flex items-center gap-2"
              >
                <XCircle className="h-4 w-4" />
                Clear
              </Button>
            </div>
          </div>

          {/* Approvals List */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Request
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Submitted
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredApprovals.map((approval) => (
                <tr key={approval.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {approval.id}
                        </div>
                        <div className="text-sm text-gray-500">
                          {approval.invoiceId}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Building2 className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-sm text-gray-900">{approval.vendor}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 text-gray-400 mr-1" />
                      {approval.amount.toLocaleString('en-US', { 
                        style: 'currency', 
                        currency: 'USD' 
                      })}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge className={getStatusColor(approval.status)}>
                      {getStatusText(approval.status)}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge className={getPriorityColor(approval.priority)}>
                      {approval.priority.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                      {new Date(approval.submittedAt).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleViewApproval(approval, e)}
                        title="View approval details"
                        className="hover:bg-blue-50 hover:text-blue-600"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {approval.status === 'pending' && (
                        <>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="text-green-600 hover:text-green-700 hover:bg-green-50"
                            onClick={(e) => handleApprove(approval.id, e)}
                            title="Approve this request"
                          >
                            <CheckCircle className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={(e) => handleReject(approval.id, e)}
                            title="Reject this request"
                          >
                            <XCircle className="h-4 w-4" />
                          </Button>
                        </>
                      )}
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleMoreOptions(approval, e)}
                        title="More options"
                        className="hover:bg-gray-50"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

          {/* Empty State */}
          {filteredApprovals.length === 0 && (
            <div className="text-center py-12">
              <Clock className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No approvals found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {filterStatus !== 'all' 
                  ? `No ${filterStatus} approvals at the moment.`
                  : 'No approval requests have been submitted yet.'
                }
              </p>
            </div>
          )}
        </>
      )}

      {/* Approval Detail Modal */}
      <ApprovalDetailModal
        approval={selectedApproval}
        isOpen={showDetailModal}
        onClose={() => setShowDetailModal(false)}
        onApprove={handleApproveWithComment}
        onReject={handleRejectWithReason}
        onEdit={handleEditApproval}
        onDelete={(approvalId) => {
          setApprovals(prev => prev.filter(approval => approval.id !== approvalId))
          setShowDetailModal(false)
        }}
      />

      {/* More Options Modal */}
      <MoreOptionsModal
        isOpen={showMoreOptions}
        onClose={() => setShowMoreOptions(false)}
        type="approval"
        itemId={selectedItem?.id || ''}
        itemName={selectedItem?.name}
      />

      {/* Edit Approval Modal */}
      {editingApproval && (
        <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Edit Approval Request</DialogTitle>
            </DialogHeader>
            <EditApprovalForm
              approval={editingApproval}
              onSave={handleSaveEdit}
              onCancel={handleCancelEdit}
            />
          </DialogContent>
        </Dialog>
      )}
    </>
  )
}