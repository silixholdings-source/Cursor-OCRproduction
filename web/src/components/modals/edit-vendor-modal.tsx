'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

interface EditVendorModalProps {
  vendor: any
  isOpen: boolean
  onClose: () => void
  onSave: (vendor: any) => void
}

export function EditVendorModal({ 
  vendor, 
  isOpen, 
  onClose, 
  onSave 
}: EditVendorModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    category: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    country: '',
    website: '',
    contactPerson: '',
    notes: '',
    status: 'active'
  })
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (vendor) {
      // Parse address if it's a single string
      let address = vendor.address || ''
      let city = vendor.city || ''
      let state = vendor.state || ''
      let zipCode = vendor.zipCode || ''
      
      // If address is a single string, try to parse it
      if (address && !city && !state && !zipCode) {
        const addressParts = address.split(', ')
        if (addressParts.length >= 3) {
          address = addressParts[0] || ''
          city = addressParts[1] || ''
          const stateZip = addressParts[2] || ''
          const stateZipParts = stateZip.split(' ')
          state = stateZipParts[0] || ''
          zipCode = stateZipParts[1] || ''
        }
      }
      
      const newFormData = {
        name: vendor.name || '',
        email: vendor.email || '',
        phone: vendor.phone || '',
        category: vendor.category || '',
        address: address,
        city: city,
        state: state,
        zipCode: zipCode,
        country: vendor.country || 'United States',
        website: vendor.website || '',
        contactPerson: vendor.contactPerson || '',
        notes: vendor.notes || '',
        status: vendor.status || 'active'
      }
      
      setFormData(newFormData)
    }
  }, [vendor])

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate required fields
    if (!formData.name || !formData.email || !formData.category) {
      alert('Please fill in all required fields (Name, Email, and Category)')
      return
    }
    
    setIsLoading(true)
    
    // Simulate API call with realistic delay
    setTimeout(() => {
      try {
        // Reconstruct full address if individual fields are provided
        let fullAddress = formData.address
        if (formData.city || formData.state || formData.zipCode) {
          const addressParts = [formData.address, formData.city, `${formData.state} ${formData.zipCode}`].filter(Boolean)
          fullAddress = addressParts.join(', ')
        }
        
        const updatedVendor = {
          ...vendor,
          ...formData,
          address: fullAddress,
          totalAmount: vendor.totalAmount || 0,
          totalInvoices: vendor.totalInvoices || 0,
          rating: vendor.rating || 5,
          lastInvoice: vendor.lastInvoice || new Date().toISOString().split('T')[0],
          updatedAt: new Date().toISOString()
        }
        
        // Call the save function
        onSave(updatedVendor)
        
        // Reset loading state
        setIsLoading(false)
        
        // Close the modal
        onClose()
        
      } catch (error) {
        console.error('Error saving vendor:', error)
        alert('Failed to save vendor. Please try again.')
        setIsLoading(false)
      }
    }, 1500) // Slightly longer delay to show loading state
  }

  const handleClose = () => {
    onClose()
  }

  if (!vendor) return null

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">
            Edit Vendor: {vendor.name}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="edit-name">Vendor Name *</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter vendor name"
                required
              />
            </div>
            <div>
              <Label htmlFor="edit-email">Email *</Label>
              <Input
                id="edit-email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="Enter email address"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="edit-phone">Phone</Label>
              <Input
                id="edit-phone"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                placeholder="Enter phone number"
              />
            </div>
            <div>
              <Label htmlFor="edit-category">Category *</Label>
              <Select 
                key={`category-${vendor?.id}-${formData.category}`}
                value={formData.category} 
                onValueChange={(value) => handleInputChange('category', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category">
                    {formData.category ? (
                      <span className="text-foreground">{formData.category}</span>
                    ) : (
                      <span className="text-muted-foreground">Select category</span>
                    )}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Office Supplies">Office Supplies</SelectItem>
                  <SelectItem value="Technology">Technology</SelectItem>
                  <SelectItem value="Consulting">Consulting</SelectItem>
                  <SelectItem value="Manufacturing">Manufacturing</SelectItem>
                  <SelectItem value="Healthcare">Healthcare</SelectItem>
                  <SelectItem value="Finance">Finance</SelectItem>
                  <SelectItem value="Retail">Retail</SelectItem>
                  <SelectItem value="supplier">Supplier</SelectItem>
                  <SelectItem value="service">Service Provider</SelectItem>
                  <SelectItem value="contractor">Contractor</SelectItem>
                  <SelectItem value="consultant">Consultant</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="edit-status">Status</Label>
              <Select 
                key={`status-${vendor?.id}-${formData.status}`}
                value={formData.status} 
                onValueChange={(value) => handleInputChange('status', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status">
                    {formData.status ? (
                      <span className="text-foreground">{formData.status}</span>
                    ) : (
                      <span className="text-muted-foreground">Select status</span>
                    )}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edit-website">Website</Label>
              <Input
                id="edit-website"
                value={formData.website}
                onChange={(e) => handleInputChange('website', e.target.value)}
                placeholder="Enter website URL"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="edit-address">Address</Label>
            <Input
              id="edit-address"
              value={formData.address}
              onChange={(e) => handleInputChange('address', e.target.value)}
              placeholder="Enter street address"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="edit-city">City</Label>
              <Input
                id="edit-city"
                value={formData.city}
                onChange={(e) => handleInputChange('city', e.target.value)}
                placeholder="Enter city"
              />
            </div>
            <div>
              <Label htmlFor="edit-state">State</Label>
              <Input
                id="edit-state"
                value={formData.state}
                onChange={(e) => handleInputChange('state', e.target.value)}
                placeholder="Enter state"
              />
            </div>
            <div>
              <Label htmlFor="edit-zipCode">ZIP Code</Label>
              <Input
                id="edit-zipCode"
                value={formData.zipCode}
                onChange={(e) => handleInputChange('zipCode', e.target.value)}
                placeholder="Enter ZIP code"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="edit-country">Country</Label>
              <Input
                id="edit-country"
                value={formData.country}
                onChange={(e) => handleInputChange('country', e.target.value)}
                placeholder="Enter country"
              />
            </div>
            <div>
              <Label htmlFor="edit-contactPerson">Contact Person</Label>
              <Input
                id="edit-contactPerson"
                value={formData.contactPerson}
                onChange={(e) => handleInputChange('contactPerson', e.target.value)}
                placeholder="Enter contact person name"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="edit-notes">Notes</Label>
            <Textarea
              id="edit-notes"
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              placeholder="Enter any additional notes"
              rows={3}
            />
          </div>

          <div className="flex justify-end space-x-3">
            <Button 
              type="button" 
              variant="outline" 
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
