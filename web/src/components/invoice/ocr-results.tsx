'use client'

import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { SafeComponentWrapper, safeMap } from '@/components/safe-component-wrapper'
import { 
  CheckCircle, 
  AlertTriangle, 
  Edit3, 
  Save, 
  X,
  FileText,
  DollarSign,
  Calendar,
  Building2,
  Hash
} from 'lucide-react'

interface ExtractedData {
  vendor: string
  invoiceNumber: string
  date: string
  dueDate: string
  amount: number
  currency: string
  lineItems: Array<{
    description: string
    quantity: number
    unitPrice: number
    total: number
  }>
  confidence: number
  rawText: string
}

interface OCRResultsProps {
  extractedData: ExtractedData
  onSave: (data: ExtractedData) => void
  onReject: () => void
  isProcessing?: boolean
}

export function OCRResults({ 
  extractedData, 
  onSave, 
  onReject, 
  isProcessing = false 
}: OCRResultsProps) {
  // Safe fallback for extractedData
  const safeExtractedData = useMemo(() => extractedData || {
    vendor: 'Unknown Vendor',
    amount: 0,
    currency: 'USD',
    date: new Date().toISOString().split('T')[0],
    invoiceNumber: 'N/A',
    confidence: 0,
    items: [],
    lineItems: [],
    extractionTime: '0 seconds',
    ocrProvider: 'AI ERP OCR Engine'
  }, [extractedData])
  
  const [isEditing, setIsEditing] = useState(false)
  const [editedData, setEditedData] = useState(safeExtractedData)
  
  // Update editedData when safeExtractedData changes
  React.useEffect(() => {
    setEditedData(safeExtractedData)
  }, [safeExtractedData])

  const handleSave = () => {
    onSave(editedData)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditedData(safeExtractedData)
    setIsEditing(false)
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'bg-green-100 text-green-800'
    if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.9) return 'High Confidence'
    if (confidence >= 0.7) return 'Medium Confidence'
    return 'Low Confidence'
  }

  return (
    <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">OCR Results</h3>
          <p className="text-sm text-gray-600">
            Review and edit the extracted invoice data
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge className={getConfidenceColor(safeExtractedData.confidence)}>
            {getConfidenceText(safeExtractedData.confidence)}
          </Badge>
          <Badge variant="outline">
            {(safeExtractedData.confidence * 100).toFixed(1)}% Accuracy
          </Badge>
        </div>
      </div>

      {/* Main Data Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Invoice Details
            </CardTitle>
            {!isEditing ? (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(true)}
              >
                <Edit3 className="h-4 w-4 mr-2" />
                Edit
              </Button>
            ) : (
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCancel}
                >
                  <X className="h-4 w-4 mr-2" />
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSave}
                >
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="vendor" className="flex items-center">
                  <Building2 className="h-4 w-4 mr-2" />
                  Vendor
                </Label>
                {isEditing ? (
                  <Input
                    id="vendor"
                    value={editedData.vendor}
                    onChange={(e) => setEditedData(prev => ({ ...prev, vendor: e.target.value }))}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1">{safeExtractedData.vendor}</p>
                )}
              </div>

              <div>
                <Label htmlFor="invoiceNumber" className="flex items-center">
                  <Hash className="h-4 w-4 mr-2" />
                  Invoice Number
                </Label>
                {isEditing ? (
                  <Input
                    id="invoiceNumber"
                    value={editedData.invoiceNumber}
                    onChange={(e) => setEditedData(prev => ({ ...prev, invoiceNumber: e.target.value }))}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1">{safeExtractedData.invoiceNumber}</p>
                )}
              </div>

              <div>
                <Label htmlFor="amount" className="flex items-center">
                  <DollarSign className="h-4 w-4 mr-2" />
                  Amount
                </Label>
                {isEditing ? (
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={editedData.amount}
                    onChange={(e) => setEditedData(prev => ({ ...prev, amount: parseFloat(e.target.value) }))}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1">
                    {safeExtractedData.currency} {safeExtractedData.amount.toFixed(2)}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="date" className="flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  Invoice Date
                </Label>
                {isEditing ? (
                  <Input
                    id="date"
                    type="date"
                    value={editedData.date}
                    onChange={(e) => setEditedData(prev => ({ ...prev, date: e.target.value }))}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1">
                    {new Date(safeExtractedData.date).toLocaleDateString()}
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="dueDate" className="flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  Due Date
                </Label>
                {isEditing ? (
                  <Input
                    id="dueDate"
                    type="date"
                    value={editedData.dueDate}
                    onChange={(e) => setEditedData(prev => ({ ...prev, dueDate: e.target.value }))}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1">
                    {new Date(safeExtractedData.dueDate).toLocaleDateString()}
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="currency" className="flex items-center">
                  <DollarSign className="h-4 w-4 mr-2" />
                  Currency
                </Label>
                {isEditing ? (
                  <Input
                    id="currency"
                    value={editedData.currency}
                    onChange={(e) => setEditedData(prev => ({ ...prev, currency: e.target.value }))}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1">{safeExtractedData.currency}</p>
                )}
              </div>
            </div>
          </div>

          {/* Line Items */}
          <div>
            <Label className="text-base font-medium">Line Items</Label>
            <div className="mt-2 space-y-2">
              {safeMap(
                safeExtractedData.lineItems,
                (item, index) => (
                  <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{item?.description || 'Unknown Item'}</p>
                      <p className="text-sm text-gray-600">
                        Qty: {item?.quantity || 0} × {item?.currency || safeExtractedData.currency} {(item?.unitPrice || 0).toFixed(2)}
                      </p>
                    </div>
                    <div className="text-sm font-medium text-gray-900">
                      {item?.currency || safeExtractedData.currency} {(item?.total || 0).toFixed(2)}
                    </div>
                  </div>
                ),
                [
                  <div key="no-items" className="text-center py-4 text-gray-500">
                    No line items available
                  </div>
                ]
              )}
            </div>
          </div>

          {/* Raw Text */}
          <div>
            <Label htmlFor="rawText" className="text-base font-medium">
              Extracted Text
            </Label>
            <Textarea
              id="rawText"
              value={safeExtractedData.rawText}
              readOnly
              className="mt-2 h-32"
              placeholder="Raw extracted text will appear here..."
            />
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-4">
        <Button
          variant="outline"
          onClick={onReject}
          className="text-red-600 hover:text-red-700"
        >
          <X className="h-4 w-4 mr-2" />
          Reject
        </Button>
        <Button
          onClick={() => onSave(editedData)}
          disabled={isProcessing}
          className="bg-green-600 hover:bg-green-700"
        >
          <CheckCircle className="h-4 w-4 mr-2" />
          {isProcessing ? 'Processing...' : 'Approve & Save'}
        </Button>
      </div>
    </div>
  )
}















