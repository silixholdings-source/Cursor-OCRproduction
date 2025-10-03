'use client'

import React, { useState, useEffect, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
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
  Hash,
  Eye,
  RefreshCw,
  Zap,
  Brain,
  Target,
  TrendingUp,
  Shield,
  Loader2
} from 'lucide-react'
import { notifications } from '@/lib/notifications'
import { apiClient } from '@/lib/api-client'

interface ConfidenceScore {
  field: string
  confidence: number
  suggestion?: string
  alternatives?: string[]
}

interface ThreeWayMatchResult {
  status: 'perfect_match' | 'partial_match' | 'price_mismatch' | 'quantity_mismatch' | 'no_match'
  confidence: number
  po_number?: string
  receipt_number?: string
  variance_amount: number
  variance_percentage: number
  warnings: string[]
  suggested_actions: string[]
}

interface EnhancedExtractedData {
  vendor: string
  invoiceNumber: string
  date: string
  dueDate: string
  amount: number
  currency: string
  poNumber?: string
  lineItems: Array<{
    description: string
    quantity: number
    unitPrice: number
    total: number
    confidence: number
  }>
  confidence: number
  confidenceScores: ConfidenceScore[]
  rawText: string
  processingTime: number
  threeWayMatch?: ThreeWayMatchResult
  validationErrors: string[]
  suggestions: string[]
}

interface EnhancedOCRResultsProps {
  extractedData: EnhancedExtractedData
  onSave: (data: EnhancedExtractedData) => void
  onReject: () => void
  onReprocess: () => void
  isProcessing?: boolean
  showThreeWayMatch?: boolean
}

export function EnhancedOCRResults({ 
  extractedData, 
  onSave, 
  onReject, 
  onReprocess,
  isProcessing = false,
  showThreeWayMatch = true
}: EnhancedOCRResultsProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedData, setEditedData] = useState(extractedData)
  const [isValidating, setIsValidating] = useState(false)
  const [validationResults, setValidationResults] = useState<any>(null)

  // Real-time validation as user edits
  useEffect(() => {
    if (isEditing) {
      const timer = setTimeout(() => {
        validateData(editedData)
      }, 500) // Debounce validation
      
      return () => clearTimeout(timer)
    }
  }, [editedData, isEditing])

  const validateData = async (data: EnhancedExtractedData) => {
    setIsValidating(true)
    try {
      const response = await apiClient.post('/api/v1/invoices/validate', data)
      setValidationResults(response)
    } catch (error) {
      console.error('Validation failed:', error)
    } finally {
      setIsValidating(false)
    }
  }

  const performThreeWayMatch = async () => {
    if (!editedData.poNumber) {
      notifications.warning('PO Number required for 3-way matching')
      return
    }

    try {
      const matchResult = await apiClient.post('/api/v1/three-way-match/match', {
        invoice_id: extractedData.invoiceNumber,
        po_number: editedData.poNumber
      })

      setEditedData(prev => ({
        ...prev,
        threeWayMatch: matchResult
      }))

      if (matchResult.status === 'perfect_match') {
        notifications.success('Perfect 3-way match found!', '3-Way Match')
      } else {
        notifications.warning(
          `${matchResult.warnings.length} issues found in 3-way match`,
          '3-Way Match',
          {
            label: 'View Details',
            onClick: () => {
              // Open detailed 3-way match analysis
              const detailsElement = document.querySelector('[data-three-way-details]')
              if (detailsElement) {
                detailsElement.scrollIntoView({ behavior: 'smooth' })
              } else {
                // Navigate to dedicated 3-way match page
                window.location.href = `/dashboard/invoices/${extractedData.invoiceNumber}/three-way-match`
              }
            }
          }
        )
      }
    } catch (error) {
      notifications.error('3-way match failed', '3-Way Match Error')
    }
  }

  const handleSave = async () => {
    // Validate before saving
    await validateData(editedData)
    
    if (validationResults?.errors?.length > 0) {
      notifications.error('Please fix validation errors before saving')
      return
    }

    onSave(editedData)
    setIsEditing(false)
    notifications.success('Invoice data saved successfully')
  }

  const handleCancel = () => {
    setEditedData(extractedData)
    setIsEditing(false)
    setValidationResults(null)
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.95) return 'bg-green-100 text-green-800 border-green-200'
    if (confidence >= 0.85) return 'bg-blue-100 text-blue-800 border-blue-200'
    if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-red-100 text-red-800 border-red-200'
  }

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.95) return 'Excellent'
    if (confidence >= 0.85) return 'High'
    if (confidence >= 0.7) return 'Medium'
    return 'Low'
  }

  const overallConfidence = useMemo(() => {
    const confidenceScores = extractedData.confidenceScores || []
    const scores = confidenceScores.map(cs => cs.confidence || 0)
    return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0
  }, [extractedData.confidenceScores])

  return (
    <div className="space-y-6">
      {/* Enhanced Header with Processing Metrics */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <Brain className="h-5 w-5 mr-2 text-blue-600" />
            AI OCR Results
          </h3>
          <p className="text-sm text-gray-600 flex items-center mt-1">
            <Zap className="h-4 w-4 mr-1" />
            Processed in {extractedData.processingTime}ms with advanced AI
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge className={getConfidenceColor(overallConfidence)}>
            <Target className="h-3 w-3 mr-1" />
            {getConfidenceText(overallConfidence)} Confidence
          </Badge>
          <Badge variant="outline">
            {(overallConfidence * 100).toFixed(1)}% Accuracy
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={onReprocess}
            disabled={isProcessing}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Reprocess
          </Button>
        </div>
      </div>

      {/* Confidence Score Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center text-sm">
            <Shield className="h-4 w-4 mr-2" />
            Field Confidence Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(extractedData.confidenceScores || []).map((score, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium capitalize">{score.field.replace('_', ' ')}</span>
                  <Badge size="sm" className={getConfidenceColor(score.confidence)}>
                    {(score.confidence * 100).toFixed(0)}%
                  </Badge>
                </div>
                <Progress value={score.confidence * 100} className="h-2" />
                {score.suggestion && (
                  <p className="text-xs text-gray-500">{score.suggestion}</p>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 3-Way Match Results */}
      {showThreeWayMatch && editedData.poNumber && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center text-sm">
                <TrendingUp className="h-4 w-4 mr-2" />
                3-Way Match Analysis
              </CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={performThreeWayMatch}
                disabled={!editedData.poNumber}
              >
                <Target className="h-4 w-4 mr-2" />
                Run 3-Way Match
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {editedData.threeWayMatch ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Badge 
                    className={
                      editedData.threeWayMatch.status === 'perfect_match' 
                        ? 'bg-green-100 text-green-800' 
                        : editedData.threeWayMatch.status === 'partial_match'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }
                  >
                    {editedData.threeWayMatch.status.replace('_', ' ').toUpperCase()}
                  </Badge>
                  <span className="text-sm text-gray-600">
                    {editedData.threeWayMatch.confidence.toFixed(1)}% Match Confidence
                  </span>
                </div>
                
                {editedData.threeWayMatch.variance_amount !== 0 && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Variance detected: ${Math.abs(editedData.threeWayMatch.variance_amount).toFixed(2)} 
                      ({editedData.threeWayMatch.variance_percentage.toFixed(1)}%)
                    </AlertDescription>
                  </Alert>
                )}

                {editedData.threeWayMatch.warnings.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Warnings:</h4>
                    {editedData.threeWayMatch.warnings.map((warning, index) => (
                      <p key={index} className="text-sm text-yellow-700">{warning}</p>
                    ))}
                  </div>
                )}

                {editedData.threeWayMatch.suggested_actions.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Suggested Actions:</h4>
                    {editedData.threeWayMatch.suggested_actions.map((action, index) => (
                      <p key={index} className="text-sm text-blue-700">{action}</p>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                Enter PO Number and click "Run 3-Way Match" to validate against purchase order and receipt data
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Main Data Card with Enhanced Editing */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Invoice Details
              {isValidating && <Loader2 className="h-4 w-4 ml-2 animate-spin" />}
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
                  disabled={validationResults?.errors?.length > 0}
                >
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Validation Errors */}
          {validationResults?.errors?.length > 0 && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-1">
                  <p className="font-medium">Validation Issues:</p>
                  {validationResults.errors.map((error: string, index: number) => (
                    <p key={index} className="text-sm">• {error}</p>
                  ))}
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Basic Information with Confidence Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="vendor" className="flex items-center justify-between">
                  <span className="flex items-center">
                    <Building2 className="h-4 w-4 mr-2" />
                    Vendor
                  </span>
                  <Badge size="sm" className={getConfidenceColor(
                    (extractedData.confidenceScores || []).find(cs => cs.field === 'vendor')?.confidence || 0
                  )}>
                    {(((extractedData.confidenceScores || []).find(cs => cs.field === 'vendor')?.confidence || 0) * 100).toFixed(0)}%
                  </Badge>
                </Label>
                {isEditing ? (
                  <Input
                    id="vendor"
                    value={editedData.vendor}
                    onChange={(e) => setEditedData(prev => ({ ...prev, vendor: e.target.value }))}
                    className={validationResults?.fieldErrors?.vendor ? 'border-red-500' : ''}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded">{extractedData.vendor}</p>
                )}
              </div>

              <div>
                <Label htmlFor="invoiceNumber" className="flex items-center justify-between">
                  <span className="flex items-center">
                    <Hash className="h-4 w-4 mr-2" />
                    Invoice Number
                  </span>
                  <Badge size="sm" className={getConfidenceColor(
                    (extractedData.confidenceScores || []).find(cs => cs.field === 'invoice_number')?.confidence || 0
                  )}>
                    {(((extractedData.confidenceScores || []).find(cs => cs.field === 'invoice_number')?.confidence || 0) * 100).toFixed(0)}%
                  </Badge>
                </Label>
                {isEditing ? (
                  <Input
                    id="invoiceNumber"
                    value={editedData.invoiceNumber}
                    onChange={(e) => setEditedData(prev => ({ ...prev, invoiceNumber: e.target.value }))}
                    className={validationResults?.fieldErrors?.invoiceNumber ? 'border-red-500' : ''}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded">{extractedData.invoiceNumber}</p>
                )}
              </div>

              <div>
                <Label htmlFor="poNumber" className="flex items-center">
                  <Hash className="h-4 w-4 mr-2" />
                  PO Number (for 3-way matching)
                </Label>
                {isEditing ? (
                  <Input
                    id="poNumber"
                    value={editedData.poNumber || ''}
                    onChange={(e) => setEditedData(prev => ({ ...prev, poNumber: e.target.value }))}
                    placeholder="Enter PO number for matching"
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded">
                    {extractedData.poNumber || 'Not specified'}
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="amount" className="flex items-center justify-between">
                  <span className="flex items-center">
                    <DollarSign className="h-4 w-4 mr-2" />
                    Total Amount
                  </span>
                  <Badge size="sm" className={getConfidenceColor(
                    (extractedData.confidenceScores || []).find(cs => cs.field === 'total_amount')?.confidence || 0
                  )}>
                    {(((extractedData.confidenceScores || []).find(cs => cs.field === 'total_amount')?.confidence || 0) * 100).toFixed(0)}%
                  </Badge>
                </Label>
                {isEditing ? (
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={editedData.amount}
                    onChange={(e) => setEditedData(prev => ({ ...prev, amount: parseFloat(e.target.value) }))}
                    className={validationResults?.fieldErrors?.amount ? 'border-red-500' : ''}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded">
                    {extractedData.currency} {extractedData.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
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
                  <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded">
                    {new Date(extractedData.date).toLocaleDateString()}
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
                  <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded">
                    {new Date(extractedData.dueDate).toLocaleDateString()}
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="currency">Currency</Label>
                {isEditing ? (
                  <Input
                    id="currency"
                    value={editedData.currency}
                    onChange={(e) => setEditedData(prev => ({ ...prev, currency: e.target.value }))}
                  />
                ) : (
                  <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded">{extractedData.currency}</p>
                )}
              </div>
            </div>
          </div>

          {/* Enhanced Line Items with Confidence */}
          <div>
            <Label className="text-base font-medium flex items-center">
              <FileText className="h-4 w-4 mr-2" />
              Line Items ({extractedData.lineItems.length})
            </Label>
            <div className="mt-2 space-y-2">
              {extractedData.lineItems.map((item, index) => (
                <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg border">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{item.description}</p>
                      <Badge size="sm" className={getConfidenceColor(item.confidence || 0)}>
                        {((item.confidence || 0) * 100).toFixed(0)}%
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">
                      Qty: {item.quantity} × {extractedData.currency} {item.unitPrice.toFixed(2)}
                    </p>
                  </div>
                  <div className="text-sm font-medium text-gray-900">
                    {extractedData.currency} {item.total.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Suggestions */}
          {extractedData.suggestions.length > 0 && (
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-sm flex items-center">
                  <Brain className="h-4 w-4 mr-2 text-blue-600" />
                  AI Suggestions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {extractedData.suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                      <p className="text-sm text-blue-800">{suggestion}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>

      {/* Enhanced Action Buttons */}
      <div className="flex justify-between">
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={() => {
              // Open original document in new tab
              const documentUrl = `/api/v1/invoices/${extractedData.invoiceNumber}/original-document`
              window.open(documentUrl, '_blank')
            }}
            className="flex items-center"
          >
            <Eye className="h-4 w-4 mr-2" />
            View Original
          </Button>
          {showThreeWayMatch && editedData.poNumber && (
            <Button
              variant="outline"
              onClick={performThreeWayMatch}
              disabled={!editedData.poNumber}
            >
              <Target className="h-4 w-4 mr-2" />
              3-Way Match
            </Button>
          )}
        </div>
        
        <div className="flex space-x-4">
          <Button
            variant="outline"
            onClick={onReject}
            className="text-red-600 hover:text-red-700"
          >
            <X className="h-4 w-4 mr-2" />
            Reject
          </Button>
          <Button
            onClick={handleSave}
            disabled={isProcessing || validationResults?.errors?.length > 0}
            className="bg-green-600 hover:bg-green-700"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            {isProcessing ? 'Processing...' : 'Approve & Save'}
          </Button>
        </div>
      </div>
    </div>
  )
}
