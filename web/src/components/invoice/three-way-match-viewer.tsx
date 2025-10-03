'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Target,
  FileText,
  Package,
  Receipt,
  DollarSign,
  Hash,
  Calendar,
  Building2,
  TrendingUp,
  TrendingDown,
  Minus,
  Plus,
  Eye,
  Download,
  RefreshCw
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { notifications } from '@/lib/notifications'

interface MatchLineItem {
  invoice_line: {
    description: string
    quantity: number
    unit_price: number
    total: number
  }
  po_line?: {
    description: string
    quantity: number
    unit_price: number
    total: number
  }
  receipt_line?: {
    description: string
    quantity: number
    unit_price: number
    total: number
  }
  match_status: 'perfect' | 'partial' | 'price_variance' | 'quantity_variance' | 'missing'
  variance_amount: number
  variance_percentage: number
  confidence: number
}

interface ThreeWayMatchData {
  invoice_id: string
  po_number: string
  receipt_number?: string
  match_status: 'perfect_match' | 'partial_match' | 'price_mismatch' | 'quantity_mismatch' | 'no_match'
  confidence_level: 'high' | 'medium' | 'low' | 'very_low'
  confidence_score: number
  total_invoice_amount: number
  total_po_amount: number
  total_receipt_amount: number
  variance_amount: number
  variance_percentage: number
  line_items: MatchLineItem[]
  warnings: string[]
  suggested_actions: string[]
  processing_time_ms: number
}

interface ThreeWayMatchViewerProps {
  invoiceId: string
  poNumber?: string
  receiptNumber?: string
  onMatchComplete?: (result: ThreeWayMatchData) => void
}

export function ThreeWayMatchViewer({ 
  invoiceId, 
  poNumber, 
  receiptNumber, 
  onMatchComplete 
}: ThreeWayMatchViewerProps) {
  const [matchData, setMatchData] = useState<ThreeWayMatchData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const performMatch = async () => {
    if (!poNumber) {
      notifications.warning('PO Number is required for 3-way matching')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await apiClient.post('/api/v1/three-way-match/match', {
        invoice_id: invoiceId,
        po_number: poNumber,
        receipt_number: receiptNumber
      })

      setMatchData(result)
      onMatchComplete?.(result)

      // Show appropriate notification
      if (result.match_status === 'perfect_match') {
        notifications.success(
          `Perfect 3-way match completed in ${result.processing_time_ms}ms`,
          '3-Way Match Success'
        )
      } else {
        notifications.warning(
          `Match completed with ${result.warnings.length} warnings`,
          '3-Way Match Completed',
          {
            label: 'View Details',
            onClick: () => {
              // Scroll to warnings section
              const warningsElement = document.querySelector('[data-warnings-section]')
              if (warningsElement) {
                warningsElement.scrollIntoView({ behavior: 'smooth' })
              }
            }
          }
        )
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Match failed'
      setError(errorMessage)
      notifications.error(errorMessage, '3-Way Match Error')
    } finally {
      setIsLoading(false)
    }
  }

  const getMatchStatusColor = (status: string) => {
    switch (status) {
      case 'perfect_match': return 'bg-green-100 text-green-800 border-green-200'
      case 'partial_match': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'price_mismatch': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'quantity_mismatch': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'no_match': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getMatchStatusIcon = (status: string) => {
    switch (status) {
      case 'perfect_match': return CheckCircle
      case 'partial_match': return Target
      case 'price_mismatch': 
      case 'quantity_mismatch': return AlertTriangle
      case 'no_match': return XCircle
      default: return Minus
    }
  }

  const getLineItemStatusIcon = (status: string) => {
    switch (status) {
      case 'perfect': return CheckCircle
      case 'partial': return Target
      case 'price_variance': return TrendingDown
      case 'quantity_variance': return TrendingUp
      case 'missing': return XCircle
      default: return Minus
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <Target className="h-5 w-5 mr-2 text-blue-600" />
            3-Way Match Analysis
          </h3>
          <p className="text-sm text-gray-600">
            Compare invoice against purchase order and receipt data
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={performMatch}
            disabled={isLoading || !poNumber}
          >
            {isLoading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Matching...
              </>
            ) : (
              <>
                <Target className="h-4 w-4 mr-2" />
                Run Match
              </>
            )}
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {matchData && (
        <>
          {/* Match Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center">
                  <Target className="h-5 w-5 mr-2" />
                  Match Summary
                </span>
                <div className="flex items-center space-x-2">
                  <Badge className={getMatchStatusColor(matchData.match_status)}>
                    {React.createElement(getMatchStatusIcon(matchData.match_status), { className: "h-3 w-3 mr-1" })}
                    {matchData.match_status.replace('_', ' ').toUpperCase()}
                  </Badge>
                  <Badge variant="outline">
                    {matchData.confidence_score.toFixed(1)}% Confidence
                  </Badge>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Invoice Amount */}
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <FileText className="h-8 w-8 mx-auto text-blue-600 mb-2" />
                  <p className="text-sm font-medium text-gray-900">Invoice Amount</p>
                  <p className="text-lg font-bold text-blue-600">
                    ${matchData.total_invoice_amount.toLocaleString()}
                  </p>
                </div>

                {/* PO Amount */}
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <Package className="h-8 w-8 mx-auto text-green-600 mb-2" />
                  <p className="text-sm font-medium text-gray-900">PO Amount</p>
                  <p className="text-lg font-bold text-green-600">
                    ${matchData.total_po_amount.toLocaleString()}
                  </p>
                </div>

                {/* Variance */}
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  {matchData.variance_amount > 0 ? (
                    <Plus className="h-8 w-8 mx-auto text-red-600 mb-2" />
                  ) : matchData.variance_amount < 0 ? (
                    <Minus className="h-8 w-8 mx-auto text-green-600 mb-2" />
                  ) : (
                    <CheckCircle className="h-8 w-8 mx-auto text-green-600 mb-2" />
                  )}
                  <p className="text-sm font-medium text-gray-900">Variance</p>
                  <p className={`text-lg font-bold ${
                    matchData.variance_amount === 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ${Math.abs(matchData.variance_amount).toLocaleString()} 
                    ({matchData.variance_percentage.toFixed(1)}%)
                  </p>
                </div>
              </div>

              {/* Progress Bar for Confidence */}
              <div className="mt-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Match Confidence</span>
                  <span className="text-sm text-gray-600">{matchData.confidence_score.toFixed(1)}%</span>
                </div>
                <Progress value={matchData.confidence_score} className="h-3" />
              </div>
            </CardContent>
          </Card>

          {/* Detailed Line Item Comparison */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Line Item Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="comparison" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="comparison">Side-by-Side</TabsTrigger>
                  <TabsTrigger value="variances">Variances</TabsTrigger>
                  <TabsTrigger value="summary">Summary</TabsTrigger>
                </TabsList>
                
                <TabsContent value="comparison" className="space-y-4">
                  {matchData.line_items.map((item, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium">{item.invoice_line.description}</h4>
                        <Badge className={getMatchStatusColor(item.match_status)}>
                          {React.createElement(getLineItemStatusIcon(item.match_status), { className: "h-3 w-3 mr-1" })}
                          {item.match_status.replace('_', ' ')}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        {/* Invoice */}
                        <div className="p-3 bg-blue-50 rounded">
                          <p className="font-medium text-blue-800 mb-2">Invoice</p>
                          <p>Qty: {item.invoice_line.quantity}</p>
                          <p>Price: ${item.invoice_line.unit_price.toFixed(2)}</p>
                          <p className="font-medium">Total: ${item.invoice_line.total.toFixed(2)}</p>
                        </div>

                        {/* PO */}
                        {item.po_line && (
                          <div className="p-3 bg-green-50 rounded">
                            <p className="font-medium text-green-800 mb-2">Purchase Order</p>
                            <p>Qty: {item.po_line.quantity}</p>
                            <p>Price: ${item.po_line.unit_price.toFixed(2)}</p>
                            <p className="font-medium">Total: ${item.po_line.total.toFixed(2)}</p>
                          </div>
                        )}

                        {/* Variance */}
                        <div className="p-3 bg-gray-50 rounded">
                          <p className="font-medium text-gray-800 mb-2">Variance</p>
                          <p className={`font-medium ${
                            item.variance_amount === 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            ${Math.abs(item.variance_amount).toFixed(2)}
                          </p>
                          <p className="text-gray-600">
                            {item.variance_percentage.toFixed(1)}%
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </TabsContent>

                <TabsContent value="variances" className="space-y-4">
                  {matchData.line_items
                    .filter(item => item.variance_amount !== 0)
                    .map((item, index) => (
                      <Alert key={index} variant={Math.abs(item.variance_percentage) > 5 ? "destructive" : "default"}>
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <div className="space-y-2">
                            <p className="font-medium">{item.invoice_line.description}</p>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <p>Invoice: ${item.invoice_line.total.toFixed(2)}</p>
                                <p>PO: ${item.po_line?.total.toFixed(2) || 'N/A'}</p>
                              </div>
                              <div>
                                <p className="font-medium text-red-600">
                                  Variance: ${Math.abs(item.variance_amount).toFixed(2)} 
                                  ({item.variance_percentage.toFixed(1)}%)
                                </p>
                              </div>
                            </div>
                          </div>
                        </AlertDescription>
                      </Alert>
                    ))}
                  {matchData.line_items.filter(item => item.variance_amount !== 0).length === 0 && (
                    <div className="text-center py-8">
                      <CheckCircle className="h-12 w-12 mx-auto text-green-600 mb-4" />
                      <p className="text-lg font-medium text-green-600">Perfect Match!</p>
                      <p className="text-gray-600">No variances detected in any line items</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="summary" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Match Statistics */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm">Match Statistics</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex justify-between">
                          <span>Perfect Matches:</span>
                          <Badge className="bg-green-100 text-green-800">
                            {matchData.line_items.filter(item => item.match_status === 'perfect').length}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Price Variances:</span>
                          <Badge className="bg-yellow-100 text-yellow-800">
                            {matchData.line_items.filter(item => item.match_status === 'price_variance').length}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Quantity Variances:</span>
                          <Badge className="bg-orange-100 text-orange-800">
                            {matchData.line_items.filter(item => item.match_status === 'quantity_variance').length}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Missing Items:</span>
                          <Badge className="bg-red-100 text-red-800">
                            {matchData.line_items.filter(item => item.match_status === 'missing').length}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Recommendations */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm">AI Recommendations</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {matchData.suggested_actions.length > 0 ? (
                          <div className="space-y-2">
                            {matchData.suggested_actions.map((action, index) => (
                              <div key={index} className="flex items-start space-x-2">
                                <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                                <p className="text-sm text-blue-800">{action}</p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-gray-600">No specific actions recommended</p>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Warnings and Actions */}
          {matchData.warnings.length > 0 && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-1">
                  <p className="font-medium">Attention Required:</p>
                  {matchData.warnings.map((warning, index) => (
                    <p key={index} className="text-sm">• {warning}</p>
                  ))}
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Action Buttons */}
          <div className="flex justify-between">
            <div className="flex space-x-2">
              <Button 
                variant="outline" 
                onClick={() => {
                  if (matchData.po_number) {
                    window.open(`/dashboard/purchase-orders/${matchData.po_number}`, '_blank')
                  } else {
                    notifications.info('No PO number available to view details')
                  }
                }}
              >
                <Eye className="h-4 w-4 mr-2" />
                View PO Details
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  // Export 3-way match report
                  const reportData = {
                    match_summary: matchData,
                    generated_at: new Date().toISOString(),
                    generated_by: 'AI ERP SaaS System'
                  }
                  
                  const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
                  const url = URL.createObjectURL(blob)
                  const link = document.createElement('a')
                  link.href = url
                  link.download = `3way-match-report-${matchData.invoice_id}.json`
                  document.body.appendChild(link)
                  link.click()
                  document.body.removeChild(link)
                  URL.revokeObjectURL(url)
                  
                  notifications.success('3-way match report exported successfully')
                }}
              >
                <Download className="h-4 w-4 mr-2" />
                Export Report
              </Button>
            </div>
            
            <div className="flex space-x-2">
              {matchData.match_status === 'perfect_match' && (
                <Button className="bg-green-600 hover:bg-green-700">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Auto-Approve
                </Button>
              )}
              {matchData.variance_amount !== 0 && (
                <Button variant="outline" className="text-yellow-600">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Require Manual Review
                </Button>
              )}
            </div>
          </div>
        </>
      )}

      {/* Initial State */}
      {!matchData && !isLoading && (
        <Card>
          <CardContent className="p-8 text-center">
            <Target className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Ready for 3-Way Matching</h3>
            <p className="text-gray-600 mb-4">
              Enter a PO number and click "Run Match" to compare this invoice against purchase order and receipt data
            </p>
            <Button 
              onClick={performMatch}
              disabled={!poNumber}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Target className="h-4 w-4 mr-2" />
              Start 3-Way Match
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
