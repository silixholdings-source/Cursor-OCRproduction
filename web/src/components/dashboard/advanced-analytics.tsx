'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Clock, 
  Users,
  Target,
  Zap,
  AlertTriangle,
  CheckCircle,
  PieChart,
  LineChart,
  Activity,
  Calendar,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react'
import { useWebSocket } from '@/hooks/use-websocket'
import { formatCurrency } from '@/lib/currency'

interface AnalyticsData {
  overview: {
    totalSpend: number
    avgProcessingTime: number
    approvalRate: number
    costSavings: number
    efficiency: number
  }
  trends: {
    monthly: Array<{month: string, amount: number, invoices: number}>
    weekly: Array<{week: string, amount: number, efficiency: number}>
  }
  vendors: Array<{
    name: string
    amount: number
    invoices: number
    avgPaymentTime: number
    reliability: number
  }>
  categories: Array<{
    name: string
    amount: number
    percentage: number
    trend: 'up' | 'down' | 'stable'
  }>
  performance: {
    ocrAccuracy: number
    automationRate: number
    errorRate: number
    userSatisfaction: number
  }
  predictions: {
    nextMonthSpend: number
    budgetVariance: number
    riskFactors: string[]
    opportunities: string[]
  }
}

export function AdvancedAnalytics() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState('month')
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  // Real-time updates
  const { isConnected } = useWebSocket('ws://localhost:8001/ws', {
    onMessage: (message) => {
      if (message.type === 'analytics_update') {
        setAnalytics(message.data)
        setLastUpdated(new Date())
      }
    }
  })

  useEffect(() => {
    loadAnalytics()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAnalytics, 30000)
    return () => clearInterval(interval)
  }, [selectedPeriod])

  const loadAnalytics = async () => {
    setIsLoading(true)
    try {
      // Simulate comprehensive analytics data
      const mockAnalytics: AnalyticsData = {
        overview: {
          totalSpend: 456789,
          avgProcessingTime: 2.3,
          approvalRate: 94.5,
          costSavings: 125000,
          efficiency: 87.2
        },
        trends: {
          monthly: [
            {month: "Jan", amount: 45000, invoices: 89},
            {month: "Feb", amount: 48000, invoices: 92},
            {month: "Mar", amount: 52000, invoices: 87},
            {month: "Apr", amount: 49000, invoices: 95},
            {month: "May", amount: 55000, invoices: 103},
            {month: "Jun", amount: 51000, invoices: 98}
          ],
          weekly: [
            {week: "Week 1", amount: 12500, efficiency: 89},
            {week: "Week 2", amount: 13200, efficiency: 91},
            {week: "Week 3", amount: 11800, efficiency: 88},
            {week: "Week 4", amount: 13500, efficiency: 93}
          ]
        },
        vendors: [
          {name: "Tech Supplies Inc", amount: 25000, invoices: 15, avgPaymentTime: 28, reliability: 98},
          {name: "Cloud Services Ltd", amount: 18000, invoices: 12, avgPaymentTime: 22, reliability: 95},
          {name: "Office Furniture Co", amount: 12000, invoices: 8, avgPaymentTime: 35, reliability: 92},
          {name: "Marketing Solutions", amount: 9500, invoices: 6, avgPaymentTime: 31, reliability: 89},
          {name: "Internet Provider", amount: 7200, invoices: 4, avgPaymentTime: 15, reliability: 99}
        ],
        categories: [
          {name: "Office Supplies", amount: 125000, percentage: 35, trend: "up"},
          {name: "Software & Technology", amount: 89000, percentage: 25, trend: "stable"},
          {name: "Marketing & Advertising", amount: 67000, percentage: 19, trend: "down"},
          {name: "Utilities", amount: 45000, percentage: 13, trend: "stable"},
          {name: "Travel & Expenses", amount: 28000, percentage: 8, trend: "up"}
        ],
        performance: {
          ocrAccuracy: 98.7,
          automationRate: 87.3,
          errorRate: 1.2,
          userSatisfaction: 94.8
        },
        predictions: {
          nextMonthSpend: 58000,
          budgetVariance: 12.5,
          riskFactors: [
            "Q4 spending trending 15% above budget",
            "Marketing category showing unusual spike",
            "3 vendors with delayed payment patterns"
          ],
          opportunities: [
            "Negotiate better terms with top 3 vendors",
            "Automate approval for sub-$500 invoices",
            "Implement early payment discounts"
          ]
        }
      }
      
      setAnalytics(mockAnalytics)
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-8 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (!analytics) return null

  return (
    <div className="space-y-6">
      {/* Header with Real-time Status */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Advanced Analytics</h2>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </div>
          <Button variant="outline" size="sm" onClick={loadAnalytics}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2 mb-2">
              <DollarSign className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-gray-600">Total Spend</span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(analytics.overview.totalSpend, 'USD')}
            </div>
            <Badge className="bg-green-100 text-green-800" size="sm">
              +12% vs last month
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-600">Avg Processing</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {analytics.overview.avgProcessingTime} days
            </div>
            <Badge className="bg-blue-100 text-blue-800" size="sm">
              -0.5 days improved
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2 mb-2">
              <CheckCircle className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium text-gray-600">Approval Rate</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">
              {analytics.overview.approvalRate}%
            </div>
            <Badge className="bg-purple-100 text-purple-800" size="sm">
              Excellent
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2 mb-2">
              <Zap className="h-4 w-4 text-orange-600" />
              <span className="text-sm font-medium text-gray-600">Automation</span>
            </div>
            <div className="text-2xl font-bold text-orange-600">
              {analytics.performance.automationRate}%
            </div>
            <Badge className="bg-orange-100 text-orange-800" size="sm">
              AI-powered
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2 mb-2">
              <Target className="h-4 w-4 text-red-600" />
              <span className="text-sm font-medium text-gray-600">Cost Savings</span>
            </div>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(analytics.overview.costSavings, 'USD')}
            </div>
            <Badge className="bg-red-100 text-red-800" size="sm">
              60% vs competitors
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics Tabs */}
      <Tabs defaultValue="trends" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="vendors">Vendors</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
        </TabsList>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Spending Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-4">Monthly Overview</h4>
                  <div className="space-y-3">
                    {analytics.trends.monthly.map((month) => (
                      <div key={month.month} className="flex items-center justify-between p-3 border rounded">
                        <span className="font-medium">{month.month}</span>
                        <div className="text-right">
                          <div className="font-bold">{formatCurrency(month.amount, 'USD')}</div>
                          <div className="text-sm text-gray-600">{month.invoices} invoices</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium mb-4">Weekly Efficiency</h4>
                  <div className="space-y-3">
                    {analytics.trends.weekly.map((week) => (
                      <div key={week.week} className="flex items-center justify-between p-3 border rounded">
                        <span className="font-medium">{week.week}</span>
                        <div className="text-right">
                          <div className="font-bold">{week.efficiency}%</div>
                          <div className="text-sm text-gray-600">{formatCurrency(week.amount, 'USD')}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vendors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Top Vendors Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.vendors.map((vendor, index) => (
                  <div key={vendor.name} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-blue-600">#{index + 1}</span>
                      </div>
                      <div>
                        <div className="font-medium">{vendor.name}</div>
                        <div className="text-sm text-gray-600">{vendor.invoices} invoices</div>
                      </div>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="font-bold">{formatCurrency(vendor.amount, 'USD')}</div>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-green-100 text-green-800" size="sm">
                          {vendor.reliability}% reliable
                        </Badge>
                        <span className="text-xs text-gray-500">{vendor.avgPaymentTime}d avg</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categories" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Spending by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.categories.map((category) => (
                  <div key={category.name} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">{category.name}</span>
                        {category.trend === 'up' && <TrendingUp className="h-4 w-4 text-green-600" />}
                        {category.trend === 'down' && <TrendingDown className="h-4 w-4 text-red-600" />}
                        {category.trend === 'stable' && <Activity className="h-4 w-4 text-gray-600" />}
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{formatCurrency(category.amount, 'USD')}</div>
                        <div className="text-sm text-gray-600">{category.percentage}% of total</div>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`bg-blue-600 h-2 rounded-full transition-all duration-500`}
                        style={{ width: `${Math.min(category.percentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="h-5 w-5 text-blue-600" />
                  <span>Predictions</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Calendar className="h-4 w-4 text-blue-600" />
                      <span className="font-medium">Next Month Forecast</span>
                    </div>
                    <div className="text-2xl font-bold text-blue-600">
                      {formatCurrency(analytics.predictions.nextMonthSpend, 'USD')}
                    </div>
                    <div className="text-sm text-gray-600">
                      {analytics.predictions.budgetVariance > 0 ? '+' : ''}{analytics.predictions.budgetVariance}% vs budget
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-3 text-green-700">Opportunities</h4>
                    <div className="space-y-2">
                      {analytics.predictions.opportunities.map((opportunity, index) => (
                        <div key={index} className="flex items-start space-x-2 p-2 bg-green-50 rounded">
                          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                          <span className="text-sm text-green-800">{opportunity}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5 text-orange-600" />
                  <span>Risk Factors</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 rounded-lg text-center">
                      <div className="text-2xl font-bold text-gray-900">{analytics.performance.ocrAccuracy}%</div>
                      <div className="text-sm text-gray-600">OCR Accuracy</div>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg text-center">
                      <div className="text-2xl font-bold text-gray-900">{analytics.performance.errorRate}%</div>
                      <div className="text-sm text-gray-600">Error Rate</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-3 text-orange-700">Risk Factors</h4>
                    <div className="space-y-2">
                      {analytics.predictions.riskFactors.map((risk, index) => (
                        <div key={index} className="flex items-start space-x-2 p-2 bg-orange-50 rounded">
                          <AlertTriangle className="h-4 w-4 text-orange-600 mt-0.5" />
                          <span className="text-sm text-orange-800">{risk}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

