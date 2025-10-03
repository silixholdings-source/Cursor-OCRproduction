'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { InvoiceUpload } from '@/components/invoice/invoice-upload'
import { OCRResults } from '@/components/invoice/ocr-results'
import { exportInvoicesToCSV } from '@/lib/csv-export'
import { InvoiceDetailModal } from '@/components/modals/invoice-detail-modal'
import { EditInvoiceModal } from '@/components/modals/edit-invoice-modal'
import { MoreOptionsModal } from '@/components/modals/more-options-modal'
import { DeleteConfirmationDialog } from '@/components/modals/delete-confirmation-dialog'
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Edit, 
  Trash2,
  FileText,
  Calendar,
  DollarSign,
  Upload,
  Brain,
  CheckCircle,
  XCircle,
  MoreVertical,
  RefreshCw,
  AlertTriangle
} from 'lucide-react'

export default function InvoicesPage() {
  const searchParams = useSearchParams()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [activeTab, setActiveTab] = useState('list') // 'list' or 'upload'
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([])
  const [selectedFile, setSelectedFile] = useState<any>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedInvoices, setSelectedInvoices] = useState<string[]>([])
  const [editingInvoice, setEditingInvoice] = useState(null)
  const [deletingInvoice, setDeletingInvoice] = useState(null)
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false)
  const [deleteConfirmationData, setDeleteConfirmationData] = useState<{
    title: string
    description: string
    itemName: string
    itemType: string
    onConfirm: () => void
  } | null>(null)
  const [viewingInvoice, setViewingInvoice] = useState(null)
  const [showMoreOptions, setShowMoreOptions] = useState(false)
  const [selectedItem, setSelectedItem] = useState<{id: string, name: string} | null>(null)

  // Invoices data state
  const [invoices, setInvoices] = useState([
    {
      id: 'INV-001',
      vendor: 'Acme Corp',
      amount: 1250.00,
      status: 'pending',
      date: '2024-01-15',
      dueDate: '2024-02-15',
      description: 'Office supplies and equipment'
    },
    {
      id: 'INV-002',
      vendor: 'Tech Solutions Inc',
      amount: 3200.50,
      status: 'approved',
      date: '2024-01-14',
      dueDate: '2024-02-14',
      description: 'Software licensing and support'
    },
    {
      id: 'INV-003',
      vendor: 'Global Services Ltd',
      amount: 875.25,
      status: 'rejected',
      date: '2024-01-13',
      dueDate: '2024-02-13',
      description: 'Consulting services'
    },
    {
      id: 'INV-004',
      vendor: 'Office Depot',
      amount: 450.00,
      status: 'pending',
      date: '2024-01-12',
      dueDate: '2024-02-12',
      description: 'Office furniture'
    },
    {
      id: 'INV-005',
      vendor: 'Cloud Hosting Co',
      amount: 1200.00,
      status: 'approved',
      date: '2024-01-11',
      dueDate: '2024-02-11',
      description: 'Monthly hosting services'
    }
  ])

  // Handle vendor filter from URL parameter
  useEffect(() => {
    const vendorParam = searchParams.get('vendor')
    if (vendorParam) {
      setSearchTerm(vendorParam)
    }
  }, [searchParams])

  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch = invoice.vendor.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         invoice.id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || invoice.status === filterStatus
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

  const handleFilesProcessed = (files: any[]) => {
    setUploadedFiles(files)
    if (files.length > 0) {
      setSelectedFile(files[0])
    }
  }

  // Invoice management functions
  const handleSaveInvoice = (data: any) => {
    setIsProcessing(true)
    
    setTimeout(() => {
      const newInvoice = {
        id: `INV-${Date.now()}`,
        vendor: data.vendor,
        amount: data.amount,
        status: 'pending',
        date: data.date,
        dueDate: data.dueDate,
        description: data.lineItems[0]?.description || 'Invoice',
        createdAt: new Date().toISOString()
      }
      
      setInvoices(prev => [...prev, newInvoice])
      setIsProcessing(false)
      setActiveTab('list')
      console.log('✅ Invoice saved successfully:', newInvoice.id)
    }, 1000)
  }

  const handleRejectInvoice = () => {
    setSelectedFile(null)
    setActiveTab('upload')
    console.log('✅ Invoice rejected')
  }

  const handleViewInvoice = (invoiceId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const invoice = invoices.find(inv => inv.id === invoiceId)
    setViewingInvoice(invoice)
    console.log('✅ View invoice clicked:', invoiceId)
  }

  const handleEditInvoice = (invoiceId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const invoice = invoices.find(inv => inv.id === invoiceId)
    console.log('🔍 Looking for invoice:', invoiceId)
    console.log('🔍 Found invoice:', invoice)
    console.log('🔍 All invoices:', invoices.map(inv => ({ id: inv.id, vendor: inv.vendor })))
    setEditingInvoice(invoice)
    console.log('✅ Edit invoice clicked:', invoiceId)
  }

  const handleInvoiceUpdated = (updatedInvoice: any) => {
    setInvoices(prev => prev.map(invoice => 
      invoice.id === updatedInvoice.id ? updatedInvoice : invoice
    ))
    setEditingInvoice(null)
    console.log('✅ Invoice updated successfully:', updatedInvoice.id)
  }

  const handleDeleteInvoice = (invoiceId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const invoice = invoices.find(inv => inv.id === invoiceId)
    if (invoice) {
      setDeleteConfirmationData({
        title: 'Delete Invoice',
        description: 'Are you sure you want to delete this invoice?',
        itemName: invoice.invoiceNumber || `Invoice #${invoice.id}`,
        itemType: 'invoice',
        onConfirm: () => handleInvoiceDeleted(invoiceId)
      })
      setShowDeleteConfirmation(true)
      console.log('✅ Delete invoice clicked:', invoiceId)
    }
  }

  const handleInvoiceDeleted = (invoiceId: string) => {
    setInvoices(prev => prev.filter(invoice => invoice.id !== invoiceId))
    setDeletingInvoice(null)
    console.log('✅ Invoice deleted successfully:', invoiceId)
  }

  const handleExport = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (filteredInvoices.length === 0) {
      alert('No invoices to export')
      return
    }
    
    setIsLoading(true)
    
    try {
      exportInvoicesToCSV(filteredInvoices, 'invoices-export.csv')
      console.log('✅ Invoices exported successfully')
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export failed. Please try again.')
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
      console.log('✅ Invoices data refreshed')
    }, 1000)
  }

  const handleBulkAction = (action: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (selectedInvoices.length === 0) {
      console.log('Please select invoices first')
      return
    }

    setIsLoading(true)
    
    setTimeout(() => {
      switch (action) {
        case 'approve':
          setInvoices(prev => prev.map(invoice => 
            selectedInvoices.includes(invoice.id) 
              ? { ...invoice, status: 'approved' }
              : invoice
          ))
          break
        case 'reject':
          setInvoices(prev => prev.map(invoice => 
            selectedInvoices.includes(invoice.id) 
              ? { ...invoice, status: 'rejected' }
              : invoice
          ))
          break
        case 'export':
          const selectedInvoicesData = invoices.filter(invoice => selectedInvoices.includes(invoice.id))
          exportInvoicesToCSV(selectedInvoicesData, 'selected-invoices.csv')
          break
        case 'delete':
          setDeleteConfirmationData({
            title: 'Delete Selected Invoices',
            description: `Are you sure you want to delete ${selectedInvoices.length} selected invoice${selectedInvoices.length > 1 ? 's' : ''}?`,
            itemName: `${selectedInvoices.length} invoice${selectedInvoices.length > 1 ? 's' : ''}`,
            itemType: 'invoices',
            onConfirm: () => {
              setInvoices(prev => prev.filter(invoice => !selectedInvoices.includes(invoice.id)))
              setSelectedInvoices([])
            }
          })
          setShowDeleteConfirmation(true)
          setIsLoading(false)
          return
      }
      setIsLoading(false)
      console.log(`✅ Bulk action "${action}" completed for ${selectedInvoices.length} invoices`)
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
    setSelectedInvoices([])
    console.log('✅ All filters cleared')
  }

  const handleMoreOptions = (invoice: any, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setSelectedItem({ id: invoice.id, name: invoice.id })
    setShowMoreOptions(true)
    console.log('✅ More options for invoice:', invoice.id)
  }

  const handleInvoiceSelect = (invoiceId: string, checked: boolean) => {
    if (checked) {
      setSelectedInvoices(prev => [...prev, invoiceId])
    } else {
      setSelectedInvoices(prev => prev.filter(id => id !== invoiceId))
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedInvoices(filteredInvoices.map(invoice => invoice.id))
    } else {
      setSelectedInvoices([])
    }
  }

  return (
    <>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Invoices</h1>
            <p className="mt-2 text-gray-600">
              Manage and track all your invoices with OCR processing
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
            <Button 
              variant={activeTab === 'upload' ? 'default' : 'outline'}
              onClick={() => setActiveTab('upload')}
              className="flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              Upload & Process
            </Button>
            <Button 
              variant={activeTab === 'list' ? 'default' : 'outline'}
              onClick={() => setActiveTab('list')}
              className="flex items-center gap-2"
            >
              <FileText className="h-4 w-4" />
              View All
            </Button>
          </div>
        </div>
      </div>

      {/* Upload & OCR Section */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          {!selectedFile ? (
            <InvoiceUpload onFilesProcessed={handleFilesProcessed} />
          ) : (
            <OCRResults
              extractedData={selectedFile.extractedData}
              onSave={handleSaveInvoice}
              onReject={handleRejectInvoice}
              isProcessing={isProcessing}
            />
          )}
        </div>
      )}

      {/* Invoice List Section */}
      {activeTab === 'list' && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Approved</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {invoices.filter(inv => inv.status === 'approved').length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <AlertTriangle className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Pending</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {invoices.filter(inv => inv.status === 'pending').length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <XCircle className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Rejected</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {invoices.filter(inv => inv.status === 'rejected').length}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <DollarSign className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Value</p>
                    <p className="text-2xl font-bold text-gray-900">
                      ${invoices.reduce((sum, inv) => sum + inv.amount, 0).toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Bulk Actions */}
          {filteredInvoices.length > 0 && (
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">
                  {selectedInvoices.length} invoice{selectedInvoices.length !== 1 ? 's' : ''} selected
                </span>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={(e) => handleBulkAction('approve', e)}
                  className="flex items-center gap-2"
                >
                  <CheckCircle className="h-4 w-4" />
                  Approve
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={(e) => handleBulkAction('reject', e)}
                  className="flex items-center gap-2"
                >
                  <XCircle className="h-4 w-4" />
                  Reject
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={(e) => handleBulkAction('export', e)}
                  className="flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Export Selected
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={(e) => handleBulkAction('delete', e)}
                  className="flex items-center gap-2 text-red-600 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete
                </Button>
              </div>
            </div>
          )}

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search invoices..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          {searchParams.get('vendor') && (
            <div className="mt-2 text-sm text-blue-600 flex items-center gap-1">
              <Filter className="h-3 w-3" />
              <span>Filtered by vendor: {searchParams.get('vendor')}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearchTerm('')
                  window.history.replaceState({}, '', '/dashboard/invoices')
                }}
                className="text-blue-600 hover:text-blue-800 h-auto p-0 ml-1"
              >
                Clear filter
              </Button>
            </div>
          )}
        </div>
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

      {/* Invoices Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    id="select-all-invoices"
                    type="checkbox"
                    checked={selectedInvoices.length === filteredInvoices.length && filteredInvoices.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300"
                    aria-label="Select all invoices"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice
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
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Due Date
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInvoices.map((invoice) => (
                <tr key={invoice.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      id={`invoice-checkbox-${invoice.id}`}
                      type="checkbox"
                      checked={selectedInvoices.includes(invoice.id)}
                      onChange={(e) => handleInvoiceSelect(invoice.id, e.target.checked)}
                      className="rounded border-gray-300"
                      aria-label={`Select invoice ${invoice.id}`}
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {invoice.id}
                        </div>
                        <div className="text-sm text-gray-500">
                          {invoice.description}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {invoice.vendor}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 text-gray-400 mr-1" />
                      {invoice.amount.toLocaleString('en-US', { 
                        style: 'currency', 
                        currency: 'USD' 
                      })}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge className={getStatusColor(invoice.status)}>
                      {getStatusText(invoice.status)}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                      {new Date(invoice.date + 'T00:00:00').toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                      {new Date(invoice.dueDate + 'T00:00:00').toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleViewInvoice(invoice.id, e)}
                        title="View invoice details"
                        className="hover:bg-blue-50 hover:text-blue-600"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleEditInvoice(invoice.id, e)}
                        title="Edit invoice"
                        className="hover:bg-green-50 hover:text-green-600"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleDeleteInvoice(invoice.id, e)}
                        title="Delete invoice"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleMoreOptions(invoice, e)}
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
      {filteredInvoices.length === 0 && (
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No invoices found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || filterStatus !== 'all' 
              ? 'Try adjusting your search or filter criteria.'
              : 'Get started by creating a new invoice.'
            }
          </p>
          {(!searchTerm && filterStatus === 'all') && (
            <div className="mt-6">
              <Button className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                New Invoice
              </Button>
            </div>
          )}
        </div>
      )}
        </>
      )}

      {/* Invoice Detail Modal */}
      <InvoiceDetailModal
        invoice={viewingInvoice}
        isOpen={!!viewingInvoice}
        onClose={() => setViewingInvoice(null)}
        onEdit={setEditingInvoice}
        onDelete={handleInvoiceDeleted}
        onApprove={(invoiceId) => {
          setInvoices(prev => prev.map(inv => 
            inv.id === invoiceId 
              ? { ...inv, status: 'approved', approvedAt: new Date().toISOString() }
              : inv
          ))
        }}
        onReject={(invoiceId) => {
          setInvoices(prev => prev.map(inv => 
            inv.id === invoiceId 
              ? { ...inv, status: 'rejected', rejectedAt: new Date().toISOString() }
              : inv
          ))
        }}
      />

      {/* Edit Invoice Modal */}
      <EditInvoiceModal
        invoice={editingInvoice}
        isOpen={!!editingInvoice}
        onClose={() => setEditingInvoice(null)}
        onSave={handleInvoiceUpdated}
      />

      {/* More Options Modal */}
      <MoreOptionsModal
        isOpen={showMoreOptions}
        onClose={() => setShowMoreOptions(false)}
        type="invoice"
        itemId={selectedItem?.id || ''}
        itemName={selectedItem?.name}
      />

      {/* Delete Confirmation Dialog */}
      {deleteConfirmationData && (
        <DeleteConfirmationDialog
          isOpen={showDeleteConfirmation}
          onClose={() => {
            setShowDeleteConfirmation(false)
            setDeleteConfirmationData(null)
          }}
          onConfirm={deleteConfirmationData.onConfirm}
          title={deleteConfirmationData.title}
          description={deleteConfirmationData.description}
          itemName={deleteConfirmationData.itemName}
          itemType={deleteConfirmationData.itemType}
        />
      )}
    </>
  )
}