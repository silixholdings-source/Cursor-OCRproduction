'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { exportVendorsToCSV } from '@/lib/csv-export'
import { VendorDetailModal } from '@/components/modals/vendor-detail-modal'
import { AddVendorModal } from '@/components/modals/add-vendor-modal'
import { EditVendorModal } from '@/components/modals/edit-vendor-modal'
import { MoreOptionsModal } from '@/components/modals/more-options-modal'
import { DeleteConfirmationDialog } from '@/components/modals/delete-confirmation-dialog'
import { loadVendors, updateVendor, addVendor, deleteVendor, searchVendors, getVendorStats, type Vendor } from '@/lib/database/vendors'
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2,
  Building2,
  Mail,
  Phone,
  MapPin,
  DollarSign,
  FileText,
  Star,
  Download,
  RefreshCw,
  MoreVertical,
  CheckCircle,
  XCircle,
  Eye,
  AlertTriangle
} from 'lucide-react'

export default function VendorsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedVendors, setSelectedVendors] = useState<string[]>([])
  const [editingVendor, setEditingVendor] = useState<any>(null)
  const [deletingVendor, setDeletingVendor] = useState<any>(null)
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false)
  const [deleteConfirmationData, setDeleteConfirmationData] = useState<{
    title: string
    description: string
    itemName: string
    itemType: string
    onConfirm: () => void
  } | null>(null)
  const [viewingVendor, setViewingVendor] = useState<any>(null)
  const [showAddVendor, setShowAddVendor] = useState(false)
  const [showMoreOptions, setShowMoreOptions] = useState(false)
  const [selectedItem, setSelectedItem] = useState<{id: string, name: string} | null>(null)
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'list'
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  // Vendors data state
  const [vendors, setVendors] = useState<Vendor[]>([])
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    inactive: 0,
    pending: 0,
    totalValue: 0,
    averageRating: 0
  })

  // Load vendors from database on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const vendorsData = loadVendors()
        const statsData = getVendorStats()
        setVendors(vendorsData)
        setStats(statsData)
      } catch (error) {
        console.error('Error loading vendors:', error)
      }
    }
    
    loadData()
  }, [])

  // Filter vendors based on search term and status
  const filteredVendors = vendors.filter(vendor => {
    const matchesSearch = vendor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vendor.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         vendor.category.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = filterStatus === 'all' || vendor.status === filterStatus
    return matchesSearch && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'inactive': return 'bg-gray-100 text-gray-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Active'
      case 'inactive': return 'Inactive'
      case 'pending': return 'Pending'
      default: return status
    }
  }

  // Vendor management functions
  const handleAddVendor = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setShowAddVendor(true)
    console.log('✅ Add vendor clicked')
  }

  const handleVendorAdded = (newVendor: any) => {
    try {
      // Add vendor to database
      const savedVendor = addVendor(newVendor)
      
      // Update local state
      setVendors(prev => [savedVendor, ...prev])
      
      // Update stats
      const newStats = getVendorStats()
      setStats(newStats)
      
      // Close the add modal
      setShowAddVendor(false)
      
      // Show success feedback
      console.log('✅ Vendor added successfully:', savedVendor.name)
      
      // Show success message
      setSuccessMessage(`Vendor "${savedVendor.name}" has been added successfully!`)
      setShowSuccessMessage(true)
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setShowSuccessMessage(false)
      }, 3000)
      
    } catch (error) {
      console.error('Error adding vendor:', error)
      alert('Failed to add vendor. Please try again.')
    }
  }

  const handleEdit = (vendorId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const vendor = vendors.find(v => v.id === vendorId)
    if (vendor) {
      setEditingVendor(vendor)
      console.log('✅ Edit vendor clicked:', vendorId)
    }
  }

  const handleVendorUpdated = (updatedVendor: any) => {
    try {
      // Update vendor in database
      const savedVendor = updateVendor(updatedVendor)
      
      // Update local state
      setVendors(prev => prev.map(vendor => 
        vendor.id === savedVendor.id ? savedVendor : vendor
      ))
      
      // Update stats
      const newStats = getVendorStats()
      setStats(newStats)
      
      // Close the edit modal
      setEditingVendor(null)
      
      // Show success feedback
      console.log('✅ Vendor updated successfully:', savedVendor.name)
      
      // Show success message
      setSuccessMessage(`Vendor "${savedVendor.name}" has been updated successfully!`)
      setShowSuccessMessage(true)
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setShowSuccessMessage(false)
      }, 3000)
      
    } catch (error) {
      console.error('Error updating vendor:', error)
      alert('Failed to update vendor. Please try again.')
    }
  }

  const handleDelete = (vendorId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const vendor = vendors.find(v => v.id === vendorId)
    if (vendor) {
      setDeleteConfirmationData({
        title: 'Delete Vendor',
        description: 'Are you sure you want to delete this vendor?',
        itemName: vendor.name,
        itemType: 'vendor',
        onConfirm: () => handleVendorDeleted(vendorId)
      })
      setShowDeleteConfirmation(true)
      console.log('✅ Delete vendor clicked:', vendorId)
    }
  }

  const handleVendorDeleted = (vendorId: string) => {
    try {
      // Delete vendor from database
      deleteVendor(vendorId)
      
      // Update local state
      setVendors(prev => prev.filter(vendor => vendor.id !== vendorId))
      
      // Update stats
      const newStats = getVendorStats()
      setStats(newStats)
      
      // Close delete modal
      setDeletingVendor(null)
      
      // Show success feedback
      console.log('✅ Vendor deleted successfully:', vendorId)
      
      // Show success message
      setSuccessMessage('Vendor has been deleted successfully!')
      setShowSuccessMessage(true)
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setShowSuccessMessage(false)
      }, 3000)
      
    } catch (error) {
      console.error('Error deleting vendor:', error)
      alert('Failed to delete vendor. Please try again.')
    }
  }

  const handleViewVendor = (vendorId: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const vendor = vendors.find(v => v.id === vendorId)
    if (vendor) {
      setViewingVendor(vendor)
      console.log('✅ View vendor clicked:', vendorId)
    }
  }

  const handleExport = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsLoading(true)
    
    try {
      exportVendorsToCSV(filteredVendors, 'vendors-export.csv')
      console.log('✅ Vendors exported successfully')
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
      console.log('✅ Vendors data refreshed')
    }, 1000)
  }

  const handleBulkAction = (action: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (selectedVendors.length === 0) {
      console.log('Please select vendors first')
      return
    }

    setIsLoading(true)
    
    setTimeout(() => {
      switch (action) {
        case 'activate':
          setVendors(prev => prev.map(vendor => 
            selectedVendors.includes(vendor.id) 
              ? { ...vendor, status: 'active' }
              : vendor
          ))
          break
        case 'deactivate':
          setVendors(prev => prev.map(vendor => 
            selectedVendors.includes(vendor.id) 
              ? { ...vendor, status: 'inactive' }
              : vendor
          ))
          break
        case 'export':
          const selectedVendorsData = vendors.filter(vendor => selectedVendors.includes(vendor.id))
          exportVendorsToCSV(selectedVendorsData, 'selected-vendors.csv')
          break
        case 'delete':
          setDeleteConfirmationData({
            title: 'Delete Selected Vendors',
            description: `Are you sure you want to delete ${selectedVendors.length} selected vendor${selectedVendors.length > 1 ? 's' : ''}?`,
            itemName: `${selectedVendors.length} vendor${selectedVendors.length > 1 ? 's' : ''}`,
            itemType: 'vendors',
            onConfirm: () => {
              // Delete vendors from database
              selectedVendors.forEach(vendorId => {
                try {
                  deleteVendor(vendorId)
                } catch (error) {
                  console.error(`Error deleting vendor ${vendorId}:`, error)
                }
              })
              
              // Update local state
              setVendors(prev => prev.filter(vendor => !selectedVendors.includes(vendor.id)))
              setSelectedVendors([])
              
              // Update stats
              const newStats = getVendorStats()
              setStats(newStats)
              
              // Show success message
              setSuccessMessage(`${selectedVendors.length} vendor${selectedVendors.length > 1 ? 's' : ''} deleted successfully!`)
              setShowSuccessMessage(true)
              setTimeout(() => setShowSuccessMessage(false), 3000)
            }
          })
          setShowDeleteConfirmation(true)
          setIsLoading(false)
          return
      }
      setIsLoading(false)
      console.log(`✅ Bulk action "${action}" completed for ${selectedVendors.length} vendors`)
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
    setSelectedVendors([])
    console.log('✅ All filters cleared')
  }

  const handleMoreOptions = (vendor: any, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setSelectedItem({ id: vendor.id, name: vendor.name })
    setShowMoreOptions(true)
    console.log('✅ More options for vendor:', vendor.id)
  }

  const handleVendorSelect = (vendorId: string, checked: boolean) => {
    if (checked) {
      setSelectedVendors(prev => [...prev, vendorId])
    } else {
      setSelectedVendors(prev => prev.filter(id => id !== vendorId))
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedVendors(filteredVendors.map(vendor => vendor.id))
    } else {
      setSelectedVendors([])
    }
  }

  const handleViewModeChange = (mode: 'grid' | 'list') => {
    setViewMode(mode)
    console.log(`✅ View mode changed to: ${mode}`)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Vendors</h1>
            <p className="mt-2 text-gray-600">
              Manage your vendor relationships and information with comprehensive tracking
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
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              onClick={() => handleViewModeChange('grid')}
              className="flex items-center gap-2"
            >
              <Building2 className="h-4 w-4" />
              Grid
            </Button>
            <Button 
              variant={viewMode === 'list' ? 'default' : 'outline'}
              onClick={() => handleViewModeChange('list')}
              className="flex items-center gap-2"
            >
              <FileText className="h-4 w-4" />
              List
            </Button>
            <Button 
              onClick={handleAddVendor}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Vendor
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Vendors</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.active}
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
                  {stats.pending}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Building2 className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Vendors</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <DollarSign className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Value</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${stats.totalValue.toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bulk Actions */}
      {filteredVendors.length > 0 && (
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">
              {selectedVendors.length} vendor{selectedVendors.length !== 1 ? 's' : ''} selected
            </span>
            <Button 
              variant="outline" 
              size="sm"
              onClick={(e) => handleBulkAction('activate', e)}
              className="flex items-center gap-2"
            >
              <CheckCircle className="h-4 w-4" />
              Activate
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={(e) => handleBulkAction('deactivate', e)}
              className="flex items-center gap-2"
            >
              <XCircle className="h-4 w-4" />
              Deactivate
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
              placeholder="Search vendors..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            aria-label="Filter by status"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="pending">Pending</option>
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

      {/* Vendors Display */}
      {viewMode === 'grid' ? (
        /* Grid View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredVendors.map((vendor) => (
            <div key={vendor.id} className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <input
                    id={`vendor-checkbox-grid-${vendor.id}`}
                    type="checkbox"
                    checked={selectedVendors.includes(vendor.id)}
                    onChange={(e) => handleVendorSelect(vendor.id, e.target.checked)}
                    className="rounded border-gray-300 mr-3"
                    aria-label={`Select vendor ${vendor.name}`}
                  />
                  <div className="flex-shrink-0 h-12 w-12">
                    <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                      <Building2 className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-gray-900">{vendor.name}</h3>
                    <p className="text-sm text-gray-500">{vendor.category}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={getStatusColor(vendor.status)}>
                    {getStatusText(vendor.status)}
                  </Badge>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={(e) => handleMoreOptions(vendor, e)}
                    title="More options"
                    className="hover:bg-gray-50"
                  >
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                  <Mail className="h-4 w-4 mr-2" />
                  {vendor.email}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Phone className="h-4 w-4 mr-2" />
                  {vendor.phone}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <MapPin className="h-4 w-4 mr-2" />
                  {vendor.address}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{vendor.totalInvoices}</div>
                  <div className="text-sm text-gray-500">Invoices</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    ${vendor.totalAmount.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500">Total Value</div>
                </div>
              </div>

              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Star className="h-4 w-4 text-yellow-400 mr-1" />
                  <span className="text-sm font-medium text-gray-900">{vendor.rating}</span>
                </div>
                <div className="text-sm text-gray-500">
                  Last invoice: {new Date(vendor.lastInvoice).toLocaleDateString()}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={(e) => handleViewVendor(vendor.id, e)}
                  title="View vendor details"
                  className="hover:bg-blue-50 hover:text-blue-600"
                >
                  <Eye className="h-4 w-4" />
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={(e) => handleEdit(vendor.id, e)}
                  title="Edit vendor"
                  className="hover:bg-green-50 hover:text-green-600"
                >
                  <Edit className="h-4 w-4" />
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  onClick={(e) => handleDelete(vendor.id, e)}
                  title="Delete vendor"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* List View */
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center">
              <input
                id="select-all-vendors-list"
                type="checkbox"
                checked={selectedVendors.length === filteredVendors.length && filteredVendors.length > 0}
                onChange={(e) => handleSelectAll(e.target.checked)}
                className="rounded border-gray-300 mr-3"
                aria-label="Select all vendors"
              />
              <div className="flex-1 grid grid-cols-6 gap-4 text-sm font-medium text-gray-500 uppercase tracking-wider">
                <div>Vendor</div>
                <div>Contact</div>
                <div>Status</div>
                <div>Invoices</div>
                <div>Total Value</div>
                <div>Actions</div>
              </div>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {filteredVendors.map((vendor) => (
              <div key={vendor.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center">
                  <input
                    id={`vendor-checkbox-list-${vendor.id}`}
                    type="checkbox"
                    checked={selectedVendors.includes(vendor.id)}
                    onChange={(e) => handleVendorSelect(vendor.id, e.target.checked)}
                    className="rounded border-gray-300 mr-3"
                    aria-label={`Select vendor ${vendor.name}`}
                  />
                  <div className="flex-1 grid grid-cols-6 gap-4 items-center">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                        <Building2 className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{vendor.name}</div>
                        <div className="text-sm text-gray-500">{vendor.category}</div>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-900">{vendor.email}</div>
                      <div className="text-sm text-gray-500">{vendor.phone}</div>
                    </div>
                    <div>
                      <Badge className={getStatusColor(vendor.status)}>
                        {getStatusText(vendor.status)}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-900">{vendor.totalInvoices}</div>
                    <div className="text-sm text-gray-900">${vendor.totalAmount.toLocaleString()}</div>
                    <div className="flex items-center gap-2">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleViewVendor(vendor.id, e)}
                        title="View vendor details"
                        className="hover:bg-blue-50 hover:text-blue-600"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleEdit(vendor.id, e)}
                        title="Edit vendor"
                        className="hover:bg-green-50 hover:text-green-600"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={(e) => handleDelete(vendor.id, e)}
                        title="Delete vendor"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredVendors.length === 0 && (
        <div className="text-center py-12">
          <Building2 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No vendors found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || filterStatus !== 'all' 
              ? 'Try adjusting your search or filter criteria.'
              : 'Get started by adding a new vendor.'
            }
          </p>
          {(!searchTerm && filterStatus === 'all') && (
            <div className="mt-6">
              <Button 
                onClick={handleAddVendor}
                className="flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Add Vendor
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Vendor Detail Modal */}
      <VendorDetailModal
        vendor={viewingVendor}
        isOpen={!!viewingVendor}
        onClose={() => setViewingVendor(null)}
        onEdit={setEditingVendor}
        onDelete={handleVendorDeleted}
      />

      {/* Add Vendor Modal */}
      <AddVendorModal
        isOpen={showAddVendor}
        onClose={() => setShowAddVendor(false)}
        onSave={handleVendorAdded}
      />

      {/* Edit Vendor Modal */}
      <EditVendorModal
        vendor={editingVendor}
        isOpen={!!editingVendor}
        onClose={() => setEditingVendor(null)}
        onSave={handleVendorUpdated}
      />

      {/* More Options Modal */}
      <MoreOptionsModal
        isOpen={showMoreOptions}
        onClose={() => setShowMoreOptions(false)}
        type="vendor"
        itemId={selectedItem?.id || ''}
        itemName={selectedItem?.name || ''}
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

      {/* Success Message */}
      {showSuccessMessage && (
        <div className="fixed top-4 right-4 z-50 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2">
          <CheckCircle className="h-5 w-5" />
          <span>{successMessage}</span>
        </div>
      )}
    </div>
  )
}