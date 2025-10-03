'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Building2, 
  Mail, 
  Phone, 
  MapPin, 
  DollarSign, 
  FileText, 
  Star, 
  Calendar,
  Edit,
  Trash2,
  X,
  ExternalLink,
  TrendingUp,
  Users,
  Clock
} from 'lucide-react'
import { DeleteConfirmationDialog } from './delete-confirmation-dialog'

interface VendorDetailModalProps {
  vendor: any
  isOpen: boolean
  onClose: () => void
  onEdit?: (vendor: any) => void
  onDelete?: (vendorId: string) => void
}

export function VendorDetailModal({ 
  vendor, 
  isOpen, 
  onClose, 
  onEdit, 
  onDelete 
}: VendorDetailModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false)

  if (!vendor) return null

  const handleEdit = () => {
    if (onEdit) {
      onEdit(vendor)
    }
    onClose()
  }

  const handleDelete = () => {
    setShowDeleteConfirmation(true)
  }

  const handleConfirmDelete = () => {
    if (onDelete) {
      onDelete(vendor.id)
    }
    setShowDeleteConfirmation(false)
    onClose()
  }

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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-gray-900">
            Vendor Details
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Vendor Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center">
                <Building2 className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{vendor.name}</h2>
                <p className="text-lg text-gray-600">{vendor.category}</p>
                <div className="flex items-center mt-2">
                  <Badge className={getStatusColor(vendor.status)}>
                    {getStatusText(vendor.status)}
                  </Badge>
                  <div className="flex items-center ml-4">
                    <Star className="h-4 w-4 text-yellow-400 mr-1" />
                    <span className="text-sm font-medium text-gray-900">{vendor.rating}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex space-x-2">
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

          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Contact Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-3">
                  <Mail className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Email</p>
                    <p className="text-sm text-gray-600">{vendor.email}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Phone className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Phone</p>
                    <p className="text-sm text-gray-600">{vendor.phone}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 md:col-span-2">
                  <MapPin className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Address</p>
                    <p className="text-sm text-gray-600">{vendor.address}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Business Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <FileText className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Invoices</p>
                    <p className="text-2xl font-bold text-gray-900">{vendor.totalInvoices}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <DollarSign className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Value</p>
                    <p className="text-2xl font-bold text-gray-900">
                      ${vendor.totalAmount.toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <Star className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Rating</p>
                    <p className="text-2xl font-bold text-gray-900">{vendor.rating}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <div className="flex items-center space-x-3">
                    <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Last Invoice</p>
                      <p className="text-sm text-gray-600">
                        {new Date(vendor.lastInvoice).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800">Completed</Badge>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <div className="flex items-center space-x-3">
                    <div className="h-2 w-2 bg-blue-500 rounded-full"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Vendor Added</p>
                      <p className="text-sm text-gray-600">
                        {vendor.createdAt ? new Date(vendor.createdAt).toLocaleDateString() : 'Unknown'}
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button 
              onClick={handleEdit}
              className="flex items-center gap-2"
            >
              <Edit className="h-4 w-4" />
              Edit Vendor
            </Button>
          </div>
        </div>
      </DialogContent>

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmationDialog
        isOpen={showDeleteConfirmation}
        onClose={() => setShowDeleteConfirmation(false)}
        onConfirm={handleConfirmDelete}
        title="Delete Vendor"
        description="Are you sure you want to delete this vendor?"
        itemName={vendor.name}
        itemType="vendor"
      />
    </Dialog>
  )
}
