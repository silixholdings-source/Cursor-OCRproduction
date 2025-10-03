'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

interface EditInvoiceModalProps {
  invoice: any
  isOpen: boolean
  onClose: () => void
  onSave: (updatedInvoice: any) => void
}

export function EditInvoiceModal({ 
  invoice, 
  isOpen, 
  onClose, 
  onSave 
}: EditInvoiceModalProps) {
  const [formData, setFormData] = useState({
    id: invoice?.id || '',
    vendor: invoice?.vendor || '',
    amount: invoice?.amount || 0,
    status: invoice?.status || 'pending',
    date: invoice?.date || '',
    dueDate: invoice?.dueDate || '',
    description: invoice?.description || ''
  })
  const [isLoading, setIsLoading] = useState(false)

  // Update form data when invoice prop changes
  useEffect(() => {
    if (invoice) {
      setFormData({
        id: invoice.id || '',
        vendor: invoice.vendor || '',
        amount: invoice.amount || 0,
        status: invoice.status || 'pending',
        date: invoice.date || '',
        dueDate: invoice.dueDate || '',
        description: invoice.description || ''
      })
    }
  }, [invoice])

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      onSave(formData)
      setIsLoading(false)
      onClose()
    }, 1000)
  }

  const handleClose = () => {
    setFormData({
      id: invoice?.id || '',
      vendor: invoice?.vendor || '',
      amount: invoice?.amount || 0,
      status: invoice?.status || 'pending',
      date: invoice?.date || '',
      dueDate: invoice?.dueDate || '',
      description: invoice?.description || ''
    })
    onClose()
  }

  if (!invoice) return null

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">
            Edit Invoice
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="invoiceId">Invoice ID</Label>
              <Input
                id="invoiceId"
                value={formData.id}
                onChange={(e) => handleInputChange('id', e.target.value)}
                placeholder="Enter invoice ID"
                required
              />
            </div>
            <div>
              <Label htmlFor="vendor">Vendor</Label>
              <Input
                id="vendor"
                value={formData.vendor}
                onChange={(e) => handleInputChange('vendor', e.target.value)}
                placeholder="Enter vendor name"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="amount">Amount</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                value={formData.amount}
                onChange={(e) => handleInputChange('amount', parseFloat(e.target.value) || 0)}
                placeholder="Enter amount"
                required
              />
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <Select 
                value={formData.status} 
                onValueChange={(value) => handleInputChange('status', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="date">Invoice Date</Label>
              <Input
                id="date"
                type="date"
                value={formData.date}
                onChange={(e) => handleInputChange('date', e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="dueDate">Due Date</Label>
              <Input
                id="dueDate"
                type="date"
                value={formData.dueDate}
                onChange={(e) => handleInputChange('dueDate', e.target.value)}
                required
              />
            </div>
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Enter invoice description"
              rows={3}
              required
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
