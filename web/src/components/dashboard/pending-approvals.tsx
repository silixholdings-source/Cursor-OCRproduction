'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api-client'
import { logger } from '@/lib/logger'
import { notifications } from '@/lib/notifications'
import { useToast } from '@/hooks/use-toast'
import { 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Eye,
  DollarSign,
  Calendar,
  Loader2
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'

// Mock data - in production this would come from API
const mockPendingApprovals = [
  {
    id: 'APR-001',
    invoiceId: 'INV-001',
    vendor: 'Tech Supplies Inc',
    amount: 1250.00,
    submittedBy: 'John Doe',
    submittedAt: '2024-01-15T10:30:00Z',
    dueDate: '2024-02-15',
    priority: 'high',
    category: 'Office Supplies',
    description: 'Office equipment and supplies for Q1 2024'
  },
  {
    id: 'APR-002',
    invoiceId: 'INV-004',
    vendor: 'Office Furniture Co',
    amount: 875.50,
    submittedBy: 'Jane Smith',
    submittedAt: '2024-01-12T14:15:00Z',
    dueDate: '2024-02-12',
    priority: 'medium',
    category: 'Furniture',
    description: 'New office chairs for conference room'
  },
  {
    id: 'APR-003',
    invoiceId: 'INV-006',
    vendor: 'Marketing Solutions',
    amount: 2500.00,
    submittedBy: 'Mike Johnson',
    submittedAt: '2024-01-10T09:45:00Z',
    dueDate: '2024-02-10',
    priority: 'low',
    category: 'Marketing',
    description: 'Q1 marketing campaign materials'
  },
  {
    id: 'APR-004',
    invoiceId: 'INV-007',
    vendor: 'Software Licenses Inc',
    amount: 1200.00,
    submittedBy: 'Sarah Wilson',
    submittedAt: '2024-01-08T16:20:00Z',
    dueDate: '2024-02-08',
    priority: 'high',
    category: 'Software',
    description: 'Annual software license renewal'
  }
]

const priorityConfig = {
  high: {
    label: 'High',
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: AlertTriangle
  },
  medium: {
    label: 'Medium',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    icon: Clock
  },
  low: {
    label: 'Low',
    color: 'bg-green-100 text-green-800 border-green-200',
    icon: CheckCircle
  }
}

export function PendingApprovals() {
  const router = useRouter()
  const { toast } = useToast()
  const [selectedApproval, setSelectedApproval] = useState<string | null>(null)
  const [loadingApproval, setLoadingApproval] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [approvals, setApprovals] = useState(mockPendingApprovals)
  const [isLoading, setIsLoading] = useState(false)

  // Load real approval data from API
  useEffect(() => {
    const loadApprovals = async () => {
      setIsLoading(true)
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'}/approvals/pending`)
        if (response.ok) {
          const data = await response.json()
          setApprovals(data.approvals || mockPendingApprovals)
        }
      } catch (error) {
        logger.error('Failed to load approvals:', error)
        // Keep using mock data as fallback
      } finally {
        setIsLoading(false)
      }
    }
    
    loadApprovals()
  }, [])

  const handleViewApproval = (approvalId: string) => {
    setSelectedApproval(approvalId)
    // Navigate to approval detail page
    router.push(`/dashboard/approvals/${approvalId}`)
  }

  const handleApprove = async (approvalId: string) => {
    setLoadingApproval(approvalId)
    setError(null)
    
    try {
      // Call API to approve the request
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/api/v1/invoices/${approvalId}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // Show success notification
      const approval = approvals.find(a => a.id === approvalId)
      if (approval) {
        toast({
          title: "Approval Successful",
          description: `Invoice from ${approval.vendor} for $${approval.amount} has been approved.`,
        })
        
        // Remove the approved item from the list
        setApprovals(prev => prev.filter(a => a.id !== approvalId))
      }
    } catch (error) {
      logger.error('Failed to approve request', error instanceof Error ? error : new Error(String(error)), { approvalId })
      const errorMessage = error instanceof Error ? error.message : 'Failed to approve request. Please try again.'
      setError(errorMessage)
      toast({
        title: "Approval Failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setLoadingApproval(null)
    }
  }

  const handleReject = async (approvalId: string) => {
    const reason = prompt('Please provide a reason for rejection:')
    if (!reason) return
    
    setLoadingApproval(approvalId)
    setError(null)
    
    try {
      // Call API to reject the request
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/api/v1/invoices/${approvalId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // Show success notification
      const approval = approvals.find(a => a.id === approvalId)
      if (approval) {
        toast({
          title: "Request Rejected",
          description: `Invoice from ${approval.vendor} for $${approval.amount} has been rejected.`,
        })
        
        // Remove the rejected item from the list
        setApprovals(prev => prev.filter(a => a.id !== approvalId))
      }
    } catch (error) {
      logger.error('Failed to reject request', error instanceof Error ? error : new Error(String(error)), { approvalId, reason })
      const errorMessage = error instanceof Error ? error.message : 'Failed to reject request. Please try again.'
      setError(errorMessage)
      toast({
        title: "Rejection Failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setLoadingApproval(null)
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Just now'
    if (diffInHours < 24) return `${diffInHours}h ago`
    return `${Math.floor(diffInHours / 24)}d ago`
  }

  return (
    <div className="bg-white shadow rounded-lg border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="h-5 w-5 text-yellow-500" />
            <h3 className="text-lg font-medium text-gray-900">Pending Approvals</h3>
            <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">
              {approvals.length}
            </Badge>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => router.push('/dashboard/approvals')}
          >
            View All
          </Button>
        </div>
      </div>

      {error && (
        <div className="px-6 py-3">
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      )}
      
      <div className="divide-y divide-gray-200">
        {approvals.map((approval) => {
          const priority = priorityConfig[approval.priority as keyof typeof priorityConfig]
          const PriorityIcon = priority.icon
          
          return (
            <div key={approval.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="flex-shrink-0">
                      <Badge className={`${priority.color} border`}>
                        <PriorityIcon className="h-3 w-3 mr-1" />
                        {priority.label}
                      </Badge>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {approval.vendor}
                      </p>
                      <p className="text-sm text-gray-500">
                        {approval.category} • {approval.invoiceId}
                      </p>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                    {approval.description}
                  </p>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-3 w-3" />
                      <span>Due: {new Date(approval.dueDate).toLocaleDateString()}</span>
                    </div>
                    <span>•</span>
                    <span>Submitted by {approval.submittedBy}</span>
                    <span>•</span>
                    <span>{formatTimeAgo(approval.submittedAt)}</span>
                  </div>
                </div>
                
                <div className="flex flex-col items-end space-y-2">
                  <div className="text-right">
                    <p className="text-lg font-semibold text-gray-900">
                      ${approval.amount.toLocaleString()}
                    </p>
                  </div>
                  
                  <div className="flex space-x-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewApproval(approval.id)}
                      className="h-8 w-8 p-0"
                      aria-label={`View approval request for ${approval.vendor}`}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleApprove(approval.id)}
                      disabled={loadingApproval === approval.id}
                      className="h-8 w-8 p-0 text-green-600 hover:text-green-700 hover:bg-green-50"
                      aria-label={`Approve request for ${approval.vendor}`}
                    >
                      {loadingApproval === approval.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                      ) : (
                        <CheckCircle className="h-4 w-4" aria-hidden="true" />
                      )}
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleReject(approval.id)}
                      disabled={loadingApproval === approval.id}
                      className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                      aria-label={`Reject request for ${approval.vendor}`}
                    >
                      {loadingApproval === approval.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                      ) : (
                        <XCircle className="h-4 w-4" aria-hidden="true" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
      
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            <span className="font-medium">{approvals.length}</span> approvals pending
          </span>
          <span className="flex items-center space-x-1">
            <DollarSign className="h-3 w-3" />
            <span>
              Total: ${approvals.reduce((sum, approval) => sum + approval.amount, 0).toLocaleString()}
            </span>
          </span>
        </div>
      </div>
    </div>
  )
}












