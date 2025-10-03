'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Eye,
  Download
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Loader2 } from 'lucide-react'
import { useGlobalSettings } from '@/hooks/use-global-settings'
import { formatCurrency } from '@/lib/currency'
import { logger } from '@/lib/logger'
import { useTranslations } from 'next-intl'
import { useToast } from '@/hooks/use-toast'

// Mock data with multi-currency support - in production this would come from API
const mockInvoices = [
  {
    id: 'INV-001',
    vendor: 'Tech Supplies Inc',
    amount: 1250.00,
    currency: 'USD',
    date: '2024-01-15',
    status: 'pending_approval',
    dueDate: '2024-02-15',
    invoiceNumber: 'TSI-2024-001',
    category: 'Office Supplies'
  },
  {
    id: 'INV-002',
    vendor: 'Cloud Services Ltd',
    amount: 255.99,
    currency: 'EUR',
    date: '2024-01-14',
    status: 'approved',
    dueDate: '2024-02-14',
    invoiceNumber: 'CSL-2024-002',
    category: 'Software'
  },
  {
    id: 'INV-003',
    vendor: 'Marketing Solutions',
    amount: 3800.00,
    currency: 'GBP',
    date: '2024-01-13',
    status: 'rejected',
    dueDate: '2024-02-13',
    invoiceNumber: 'MS-2024-003',
    category: 'Marketing'
  },
  {
    id: 'INV-004',
    vendor: 'Office Furniture Co',
    amount: 875.50,
    currency: 'CAD',
    date: '2024-01-12',
    status: 'pending_approval',
    dueDate: '2024-02-12',
    invoiceNumber: 'OFC-2024-004',
    category: 'Furniture'
  },
  {
    id: 'INV-005',
    vendor: 'Internet Provider',
    amount: 22500,
    currency: 'JPY',
    date: '2024-01-11',
    status: 'approved',
    dueDate: '2024-02-11',
    invoiceNumber: 'IP-2024-005',
    category: 'Utilities'
  }
]

const statusConfig = {
  pending_approval: {
    label: 'Pending Approval',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    icon: Clock
  },
  approved: {
    label: 'Approved',
    color: 'bg-green-100 text-green-800 border-green-200',
    icon: CheckCircle
  },
  rejected: {
    label: 'Rejected',
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: XCircle
  },
  processing: {
    label: 'Processing',
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    icon: AlertTriangle
  }
}

export function RecentInvoices() {
  const router = useRouter()
  const t = useTranslations()
  const { toast } = useToast()
  const [selectedInvoice, setSelectedInvoice] = useState<string | null>(null)
  const [invoices, setInvoices] = useState(mockInvoices)
  const [isLoading, setIsLoading] = useState(false)
  const [downloadingInvoice, setDownloadingInvoice] = useState<string | null>(null)
  const { formatCurrency: formatCurrencyGlobal } = useGlobalSettings()

  // Load real invoice data from API
  useEffect(() => {
    const loadInvoices = async () => {
      setIsLoading(true)
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'}/invoices/recent`)
        if (response.ok) {
          const data = await response.json()
          setInvoices(data.invoices || mockInvoices)
        }
      } catch (error) {
        logger.error('Failed to load invoices:', error instanceof Error ? error : new Error(String(error)))
        // Keep using mock data as fallback
      } finally {
        setIsLoading(false)
      }
    }
    
    loadInvoices()
  }, [])

  const handleViewInvoice = (invoiceId: string) => {
    setSelectedInvoice(invoiceId)
    // Navigate to invoice detail page
    router.push(`/dashboard/invoices/${invoiceId}`)
  }

  const handleDownloadInvoice = async (invoiceId: string) => {
    setDownloadingInvoice(invoiceId)
    
    try {
      // Use the backend API to download the invoice
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const downloadUrl = `${apiUrl}/api/v1/invoices/${invoiceId}/download`
      
      // Create a temporary link to trigger download
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `invoice-${invoiceId}.pdf`
      link.target = '_blank'
      
      // Add to DOM temporarily and click
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      // Show success notification
      toast({
        title: "Download Started",
        description: `Invoice ${invoiceId} download has started.`,
      })
    } catch (error) {
      logger.error('Failed to download invoice:', error)
      
      // Show error notification
      toast({
        title: "Download Failed",
        description: "Failed to download invoice. Please try again.",
        variant: "destructive",
      })
      
      // Fallback: open in new tab
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      window.open(`${apiUrl}/api/v1/invoices/${invoiceId}/download`, '_blank')
    } finally {
      setDownloadingInvoice(null)
    }
  }

  return (
    <div className="bg-white shadow rounded-lg border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-gray-400" />
            <h3 className="text-lg font-medium text-gray-900">{t('dashboard.recentInvoices')}</h3>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => router.push('/dashboard/invoices')}
          >
            {t('dashboard.viewAll')}
          </Button>
        </div>
      </div>
      
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-500">Loading invoices...</span>
        </div>
      ) : (
        <>
          <div className="divide-y divide-gray-200">
            {invoices.map((invoice) => {
          const status = statusConfig[invoice.status as keyof typeof statusConfig]
          const StatusIcon = status.icon
          
          return (
            <div key={invoice.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <Badge className={`${status.color} border`}>
                        <StatusIcon className="h-3 w-3 mr-1" />
                        {status.label}
                      </Badge>
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {invoice.vendor}
                      </p>
                      <p className="text-sm text-gray-500">
                        {invoice.invoiceNumber} • {invoice.category}
                      </p>
                    </div>
                  </div>
                  
                  <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                    <span>Due: {new Date(invoice.dueDate).toLocaleDateString()}</span>
                    <span>Date: {new Date(invoice.date).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <div className="text-right">
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrencyGlobal(invoice.amount, invoice.currency || 'USD')}
                    </p>
                  </div>
                  
                  <div className="flex space-x-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewInvoice(invoice.id)}
                      className="h-8 w-8 p-0"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownloadInvoice(invoice.id)}
                      disabled={downloadingInvoice === invoice.id}
                      className="h-8 w-8 p-0"
                    >
                      {downloadingInvoice === invoice.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Download className="h-4 w-4" />
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
            <div className="text-sm text-gray-600">
              <span className="font-medium">{mockInvoices.length}</span> invoices processed this month
            </div>
          </div>
        </>
      )}
    </div>
  )
}












