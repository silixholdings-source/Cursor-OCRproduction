'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { 
  Calculator, 
  TrendingUp, 
  DollarSign, 
  Clock, 
  Users, 
  FileText,
  CheckCircle,
  AlertCircle,
  Shield,
  ArrowRight
} from 'lucide-react'

interface ROICalculation {
  currentCosts: {
    manualProcessing: number
    errorCorrection: number
    latePaymentPenalties: number
    staffTime: number
    total: number
  }
  aiErpSavings: {
    timeReduction: number
    errorReduction: number
    penaltyAvoidance: number
    staffEfficiency: number
    total: number
  }
  netSavings: number
  paybackPeriod: number
  threeYearROI: number
}

export default function ROICalculator() {
  const router = useRouter()
  const [inputs, setInputs] = useState({
    monthlyInvoices: 500,
    avgInvoiceValue: 2500,
    currentProcessingTime: 15, // minutes per invoice
    currentErrorRate: 5, // percentage
    staffHourlyRate: 25,
    latePaymentPenalties: 1000, // monthly
    currentStaffCount: 3
  })

  const [calculation, setCalculation] = useState<ROICalculation | null>(null)

  const calculateROI = useCallback(() => {
    const {
      monthlyInvoices,
      avgInvoiceValue,
      currentProcessingTime,
      currentErrorRate,
      staffHourlyRate,
      latePaymentPenalties,
      currentStaffCount
    } = inputs

    // Current costs calculation
    const monthlyProcessingHours = (monthlyInvoices * currentProcessingTime) / 60
    const monthlyStaffCost = monthlyProcessingHours * staffHourlyRate
    const monthlyErrorCost = (monthlyInvoices * currentErrorRate / 100) * avgInvoiceValue * 0.1 // 10% of invoice value for error correction
    const monthlyPenaltyCost = latePaymentPenalties

    const currentCosts = {
      manualProcessing: monthlyStaffCost,
      errorCorrection: monthlyErrorCost,
      latePaymentPenalties: monthlyPenaltyCost,
      staffTime: monthlyProcessingHours,
      total: monthlyStaffCost + monthlyErrorCost + monthlyPenaltyCost
    }

    // AI ERP savings calculation
    const timeReduction = monthlyStaffCost * 0.8 // 80% time reduction
    const errorReduction = monthlyErrorCost * 0.9 // 90% error reduction
    const penaltyAvoidance = monthlyPenaltyCost * 0.7 // 70% penalty reduction
    const staffEfficiency = monthlyStaffCost * 0.3 // 30% additional efficiency

    const aiErpSavings = {
      timeReduction,
      errorReduction,
      penaltyAvoidance,
      staffEfficiency,
      total: timeReduction + errorReduction + penaltyAvoidance + staffEfficiency
    }

    const netSavings = aiErpSavings.total
    const aiErpCost = monthlyInvoices <= 50 ? 19 : monthlyInvoices <= 500 ? 49 : 99 // Based on our pricing
    const paybackPeriod = aiErpCost / netSavings // months
    const threeYearROI = ((netSavings * 36) - (aiErpCost * 36)) / (aiErpCost * 36) * 100

    setCalculation({
      currentCosts,
      aiErpSavings,
      netSavings,
      paybackPeriod,
      threeYearROI
    })
  }, [inputs])

  useEffect(() => {
    calculateROI()
  }, [inputs, calculateROI])

  const handleInputChange = (field: string, value: number) => {
    setInputs(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <div className="py-16 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <Badge variant="secondary" className="mb-4 bg-green-100 text-green-800">
            <Calculator className="w-4 h-4 mr-1" />
            ROI Calculator
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Calculate Your Savings
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See exactly how much you can save by switching to AI ERP SaaS. 
            Most businesses save 60-80% on invoice processing costs.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calculator className="w-5 h-5 mr-2" />
                Your Current Situation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="monthlyInvoices">Monthly Invoices</Label>
                  <Input
                    id="monthlyInvoices"
                    type="number"
                    value={inputs.monthlyInvoices}
                    onChange={(e) => handleInputChange('monthlyInvoices', parseInt(e.target.value) || 0)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="avgInvoiceValue">Avg Invoice Value ($)</Label>
                  <Input
                    id="avgInvoiceValue"
                    type="number"
                    value={inputs.avgInvoiceValue}
                    onChange={(e) => handleInputChange('avgInvoiceValue', parseInt(e.target.value) || 0)}
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="currentProcessingTime">Processing Time (min)</Label>
                  <Input
                    id="currentProcessingTime"
                    type="number"
                    value={inputs.currentProcessingTime}
                    onChange={(e) => handleInputChange('currentProcessingTime', parseInt(e.target.value) || 0)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="currentErrorRate">Error Rate (%)</Label>
                  <Input
                    id="currentErrorRate"
                    type="number"
                    value={inputs.currentErrorRate}
                    onChange={(e) => handleInputChange('currentErrorRate', parseInt(e.target.value) || 0)}
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="staffHourlyRate">Staff Hourly Rate ($)</Label>
                  <Input
                    id="staffHourlyRate"
                    type="number"
                    value={inputs.staffHourlyRate}
                    onChange={(e) => handleInputChange('staffHourlyRate', parseInt(e.target.value) || 0)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="latePaymentPenalties">Late Payment Penalties ($/month)</Label>
                  <Input
                    id="latePaymentPenalties"
                    type="number"
                    value={inputs.latePaymentPenalties}
                    onChange={(e) => handleInputChange('latePaymentPenalties', parseInt(e.target.value) || 0)}
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="currentStaffCount">AP Staff Count</Label>
                <Input
                  id="currentStaffCount"
                  type="number"
                  value={inputs.currentStaffCount}
                  onChange={(e) => handleInputChange('currentStaffCount', parseInt(e.target.value) || 0)}
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          <div className="space-y-6">
            {/* Current Costs */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-red-600">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  Current Monthly Costs
                </CardTitle>
              </CardHeader>
              <CardContent>
                {calculation && (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Manual Processing:</span>
                      <span className="font-semibold">${calculation.currentCosts.manualProcessing.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Error Correction:</span>
                      <span className="font-semibold">${calculation.currentCosts.errorCorrection.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Late Payment Penalties:</span>
                      <span className="font-semibold">${calculation.currentCosts.latePaymentPenalties.toLocaleString()}</span>
                    </div>
                    <div className="border-t pt-3">
                      <div className="flex justify-between text-lg font-bold">
                        <span>Total Monthly Cost:</span>
                        <span className="text-red-600">${calculation.currentCosts.total.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* AI ERP Savings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-green-600">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  AI ERP Monthly Savings
                </CardTitle>
              </CardHeader>
              <CardContent>
                {calculation && (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Time Reduction (80%):</span>
                      <span className="font-semibold text-green-600">${calculation.aiErpSavings.timeReduction.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Error Reduction (90%):</span>
                      <span className="font-semibold text-green-600">${calculation.aiErpSavings.errorReduction.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Penalty Avoidance (70%):</span>
                      <span className="font-semibold text-green-600">${calculation.aiErpSavings.penaltyAvoidance.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Staff Efficiency (30%):</span>
                      <span className="font-semibold text-green-600">${calculation.aiErpSavings.staffEfficiency.toLocaleString()}</span>
                    </div>
                    <div className="border-t pt-3">
                      <div className="flex justify-between text-lg font-bold">
                        <span>Total Monthly Savings:</span>
                        <span className="text-green-600">${calculation.aiErpSavings.total.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* ROI Summary */}
            <Card className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Your ROI Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                {calculation && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold">
                          {calculation.paybackPeriod < 1 
                            ? `${Math.round(calculation.paybackPeriod * 30)} days`
                            : `${calculation.paybackPeriod.toFixed(1)} months`
                          }
                        </div>
                        <div className="text-sm opacity-90">Payback Period</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold">
                          {calculation.threeYearROI.toFixed(0)}%
                        </div>
                        <div className="text-sm opacity-90">3-Year ROI</div>
                      </div>
                    </div>
                    
                    <div className="text-center pt-4 border-t border-white/20">
                      <div className="text-3xl font-bold mb-2">
                        ${calculation.netSavings.toLocaleString()}
                      </div>
                      <div className="text-sm opacity-90">Monthly Net Savings</div>
                    </div>

                    <div className="text-center">
                      <Badge variant="secondary" className="bg-white/20 text-white">
                        <DollarSign className="w-3 h-3 mr-1" />
                        ${(calculation.netSavings * 12).toLocaleString()} Annual Savings
                      </Badge>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* CTA */}
            <div className="text-center">
              <Button 
                size="lg" 
                className="w-full bg-green-600 hover:bg-green-700"
                onClick={() => router.push('/auth/register')}
              >
                Start Your Free Trial
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <p className="text-sm text-gray-600 mt-2">
                No credit card required • 3-day free trial
              </p>
            </div>
          </div>
        </div>

        {/* Additional Benefits */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Additional Benefits Not Included in ROI
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="text-center">
              <CardContent className="p-6">
                <Clock className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h4 className="text-lg font-semibold mb-2">Faster Approvals</h4>
                <p className="text-gray-600">
                  Reduce approval time from days to hours with mobile-first design
                </p>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-6">
                <Shield className="w-12 h-12 text-green-600 mx-auto mb-4" />
                <h4 className="text-lg font-semibold mb-2">Better Security</h4>
                <p className="text-gray-600">
                  Enterprise-grade security with SOC 2 compliance and audit trails
                </p>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardContent className="p-6">
                <FileText className="w-12 h-12 text-purple-600 mx-auto mb-4" />
                <h4 className="text-lg font-semibold mb-2">Better Insights</h4>
                <p className="text-gray-600">
                  Advanced analytics and reporting for better business decisions
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
