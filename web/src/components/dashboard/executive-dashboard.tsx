'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart,
  Scatter,
  ScatterChart,
  ZAxis
} from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  Clock,
  Shield,
  Brain,
  AlertTriangle,
  CheckCircle,
  Users,
  FileText,
  Zap,
  Target,
  BarChart3,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon,
  RefreshCw,
  Download,
  Settings,
  Eye,
  Filter,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Star,
  Lightbulb,
  AlertCircle,
  Info,
  ExternalLink,
  Play,
  Pause,
  RotateCcw,
  Maximize2,
  Minimize2
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface KPI {
  name: string
  value: number
  target?: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  change_percent: number
  period: string
  metadata?: Record<string, any>
}

interface Insight {
  title: string
  description: string
  impact: 'high' | 'medium' | 'low'
  category: string
  recommendation: string
  confidence: number
  actionable: boolean
}

interface TrendData {
  date: string
  invoice_count: number
  volume: number
  value?: number
}

interface Prediction {
  date: string
  predicted_value: number
  confidence_interval_lower?: number
  confidence_interval_upper?: number
  confidence: number
}

interface ExecutiveDashboardData {
  dashboard_id: string
  generated_at: string
  period: {
    start_date: string
    end_date: string
    days: number
  }
  kpis: KPI[]
  predictions: {
    cash_flow: {
      predictions: Prediction[]
      total_predicted_inflow: number
      average_daily_flow: number
      confidence_trend: string
    }
    approval_predictions: Array<{
      invoice_id: string
      invoice_number: string
      supplier_name: string
      amount: number
      approval_probability: number
      confidence: number
      recommendations: string[]
    }>
  }
  ai_insights: Insight[]
  trends: {
    daily_volumes: TrendData[]
    trend_direction: 'up' | 'down' | 'stable'
    trend_strength: number
    period: string
  }
  risk_assessment: {
    overall_risk_level: 'HIGH' | 'MEDIUM' | 'LOW'
    high_value_pending: number
    supplier_concentration: number
    processing_backlog: number
    risk_factors: string[]
  }
  summary: {
    performance_score: number
    key_metrics: KPI[]
    critical_insights: Insight[]
    risk_level: 'HIGH' | 'MEDIUM' | 'LOW'
    recommendations: string[]
  }
}

const COLORS = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#06b6d4',
  gray: '#6b7280'
}

const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#84cc16', '#f97316']

export function ExecutiveDashboard() {
  const [dashboardData, setDashboardData] = useState<ExecutiveDashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPeriod, setSelectedPeriod] = useState('30')
  const [refreshing, setRefreshing] = useState(false)
  const [fullscreen, setFullscreen] = useState(false)

  const fetchDashboardData = async (period: string = '30') => {
    try {
      setLoading(true)
      setError(null)
      
      // Mock data - in production, this would fetch from the API
      const mockData: ExecutiveDashboardData = {
        dashboard_id: `executive_${Date.now()}`,
        generated_at: new Date().toISOString(),
        period: {
          start_date: new Date(Date.now() - parseInt(period) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          end_date: new Date().toISOString().split('T')[0],
          days: parseInt(period)
        },
        kpis: [
          {
            name: 'Total Invoice Volume',
            value: 2847500,
            unit: 'USD',
            trend: 'up',
            change_percent: 12.5,
            period: 'Last 30 days'
          },
          {
            name: 'Automation Rate',
            value: 78.5,
            target: 80,
            unit: '%',
            trend: 'up',
            change_percent: 5.2,
            period: 'Last 30 days'
          },
          {
            name: 'Average Processing Time',
            value: 18.5,
            target: 24,
            unit: 'hours',
            trend: 'down',
            change_percent: -8.3,
            period: 'Last 30 days'
          },
          {
            name: 'Approval Rate',
            value: 87.2,
            target: 85,
            unit: '%',
            trend: 'up',
            change_percent: 3.1,
            period: 'Last 30 days'
          },
          {
            name: 'OCR Accuracy',
            value: 96.8,
            target: 95,
            unit: '%',
            trend: 'stable',
            change_percent: 0.5,
            period: 'Last 30 days'
          },
          {
            name: 'System Uptime',
            value: 99.95,
            target: 99.5,
            unit: '%',
            trend: 'stable',
            change_percent: 0.1,
            period: 'Last 30 days'
          }
        ],
        predictions: {
          cash_flow: {
            predictions: [
              { date: '2024-01-01', predicted_value: 95000, confidence: 0.92 },
              { date: '2024-01-02', predicted_value: 102000, confidence: 0.89 },
              { date: '2024-01-03', predicted_value: 88000, confidence: 0.85 },
              { date: '2024-01-04', predicted_value: 115000, confidence: 0.91 },
              { date: '2024-01-05', predicted_value: 98000, confidence: 0.87 }
            ],
            total_predicted_inflow: 498000,
            average_daily_flow: 99600,
            confidence_trend: 'stable'
          },
          approval_predictions: [
            {
              invoice_id: 'inv_001',
              invoice_number: 'INV-2024-001',
              supplier_name: 'Tech Solutions Inc.',
              amount: 25000,
              approval_probability: 0.92,
              confidence: 0.88,
              recommendations: ['High confidence auto-approval candidate']
            },
            {
              invoice_id: 'inv_002',
              invoice_number: 'INV-2024-002',
              supplier_name: 'Global Services Ltd.',
              amount: 15000,
              approval_probability: 0.67,
              confidence: 0.75,
              recommendations: ['Review supplier history', 'Verify invoice details']
            }
          ]
        },
        ai_insights: [
          {
            title: 'High Supplier Concentration Risk',
            description: 'Top 3 suppliers represent 65% of invoice volume, creating concentration risk',
            impact: 'high',
            category: 'supplier_risk',
            recommendation: 'Diversify supplier base and negotiate backup suppliers',
            confidence: 0.92,
            actionable: true
          },
          {
            title: 'Automation Opportunity',
            description: '45% of invoices could be auto-approved based on ML analysis',
            impact: 'medium',
            category: 'efficiency',
            recommendation: 'Increase auto-approval thresholds to reduce manual processing',
            confidence: 0.88,
            actionable: true
          },
          {
            title: 'Cost Savings Potential',
            description: 'Bulk discount opportunities identified with 3 major suppliers',
            impact: 'medium',
            category: 'cost_optimization',
            recommendation: 'Negotiate volume discounts for high-frequency suppliers',
            confidence: 0.85,
            actionable: true
          }
        ],
        trends: {
          daily_volumes: [
            { date: '2024-01-01', invoice_count: 45, volume: 85000 },
            { date: '2024-01-02', invoice_count: 52, volume: 102000 },
            { date: '2024-01-03', invoice_count: 38, volume: 78000 },
            { date: '2024-01-04', invoice_count: 61, volume: 125000 },
            { date: '2024-01-05', invoice_count: 47, volume: 95000 },
            { date: '2024-01-06', invoice_count: 55, volume: 112000 },
            { date: '2024-01-07', invoice_count: 43, volume: 88000 }
          ],
          trend_direction: 'up',
          trend_strength: 15.2,
          period: 'Last 7 days'
        },
        risk_assessment: {
          overall_risk_level: 'MEDIUM',
          high_value_pending: 8,
          supplier_concentration: 65.2,
          processing_backlog: 12,
          risk_factors: [
            'High volume of large pending invoices',
            'High supplier concentration risk'
          ]
        },
        summary: {
          performance_score: 87.5,
          key_metrics: [],
          critical_insights: [],
          risk_level: 'MEDIUM',
          recommendations: [
            'Focus on diversifying supplier base to reduce concentration risk',
            'Implement automated payment reminders for overdue invoices',
            'Consider increasing auto-approval thresholds for efficiency gains'
          ]
        }
      }
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setDashboardData(mockData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchDashboardData(selectedPeriod)
  }, [selectedPeriod])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchDashboardData(selectedPeriod)
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" />
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-500" />
      default:
        return <Minus className="h-4 w-4 text-gray-500" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'LOW':
        return 'bg-green-100 text-green-800 border-green-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getImpactBadgeColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (loading && !dashboardData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center space-y-4">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
          <p className="text-gray-600">Loading executive dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Dashboard</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={handleRefresh} disabled={refreshing}>
            {refreshing ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : null}
            Retry
          </Button>
        </div>
      </div>
    )
  }

  if (!dashboardData) return null

  return (
    <div className={cn("space-y-6", fullscreen && "fixed inset-0 z-50 bg-white p-6 overflow-auto")}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Executive Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Performance overview for {dashboardData.period.start_date} to {dashboardData.period.end_date}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">7 days</SelectItem>
              <SelectItem value="30">30 days</SelectItem>
              <SelectItem value="90">90 days</SelectItem>
              <SelectItem value="365">1 year</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setFullscreen(!fullscreen)}
          >
            {fullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Performance Score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Target className="h-5 w-5" />
            <span>Performance Score</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-6">
            <div className="relative w-32 h-32">
              <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  className="text-gray-200"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray={`${dashboardData.summary.performance_score * 2.51} 251`}
                  className="text-blue-500"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-900">
                  {dashboardData.summary.performance_score.toFixed(1)}
                </span>
              </div>
            </div>
            <div className="flex-1">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Overall Performance</span>
                  <Badge variant="outline" className={cn(
                    dashboardData.summary.performance_score >= 90 ? "border-green-500 text-green-700" :
                    dashboardData.summary.performance_score >= 70 ? "border-yellow-500 text-yellow-700" :
                    "border-red-500 text-red-700"
                  )}>
                    {dashboardData.summary.performance_score >= 90 ? "Excellent" :
                     dashboardData.summary.performance_score >= 70 ? "Good" : "Needs Improvement"}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Risk Level</span>
                  <Badge className={getRiskBadgeColor(dashboardData.summary.risk_level)}>
                    {dashboardData.summary.risk_level}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Last Updated</span>
                  <span className="text-sm text-gray-500">
                    {new Date(dashboardData.generated_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* KPIs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboardData.kpis.map((kpi, index) => (
          <Card key={index}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">{kpi.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {kpi.value.toLocaleString()}{kpi.unit}
                  </div>
                  {kpi.target && (
                    <div className="text-sm text-gray-500 mt-1">
                      Target: {kpi.target.toLocaleString()}{kpi.unit}
                    </div>
                  )}
                </div>
                <div className="flex flex-col items-end space-y-1">
                  <div className="flex items-center space-x-1">
                    {getTrendIcon(kpi.trend)}
                    <span className={cn("text-sm font-medium", getTrendColor(kpi.trend))}>
                      {Math.abs(kpi.change_percent).toFixed(1)}%
                    </span>
                  </div>
                  {kpi.target && (
                    <div className="text-xs text-gray-500">
                      {((kpi.value / kpi.target) * 100).toFixed(1)}% of target
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="risks">Risk Assessment</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Daily Volume Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Daily Invoice Volume</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={dashboardData.trends.daily_volumes}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="volume"
                      stroke={COLORS.primary}
                      fill={COLORS.primary}
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Approval Predictions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5" />
                  <span>Approval Predictions</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData.predictions.approval_predictions.map((prediction, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <div className="font-medium">{prediction.invoice_number}</div>
                          <div className="text-sm text-gray-600">{prediction.supplier_name}</div>
                        </div>
                        <Badge variant="outline">
                          {prediction.amount.toLocaleString()} USD
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="flex-1">
                          <div className="text-sm text-gray-600 mb-1">Approval Probability</div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${prediction.approval_probability * 100}%` }}
                            />
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {(prediction.approval_probability * 100).toFixed(1)}%
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-600">Confidence</div>
                          <div className="font-medium">
                            {(prediction.confidence * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <LineChartIcon className="h-5 w-5" />
                <span>Volume Trends</span>
                <Badge variant="outline" className={cn(
                  dashboardData.trends.trend_direction === 'up' ? "border-green-500 text-green-700" :
                  dashboardData.trends.trend_direction === 'down' ? "border-red-500 text-red-700" :
                  "border-gray-500 text-gray-700"
                )}>
                  {dashboardData.trends.trend_direction} {dashboardData.trends.trend_strength.toFixed(1)}%
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={dashboardData.trends.daily_volumes}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="volume"
                    stroke={COLORS.primary}
                    strokeWidth={2}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="invoice_count"
                    stroke={COLORS.secondary}
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {dashboardData.ai_insights.map((insight, index) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center space-x-2">
                      <Lightbulb className="h-5 w-5" />
                      <span>{insight.title}</span>
                    </CardTitle>
                    <Badge className={getImpactBadgeColor(insight.impact)}>
                      {insight.impact}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-4">{insight.description}</p>
                  <div className="space-y-3">
                    <div>
                      <div className="text-sm font-medium text-gray-700 mb-1">Recommendation</div>
                      <p className="text-sm text-gray-600">{insight.recommendation}</p>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-600">
                        Confidence: {(insight.confidence * 100).toFixed(0)}%
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {insight.category.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="predictions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5" />
                <span>Cash Flow Predictions</span>
                <Badge variant="outline">
                  {dashboardData.predictions.cash_flow.confidence_trend}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={dashboardData.predictions.cash_flow.predictions}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="predicted_value"
                        stroke={COLORS.primary}
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">
                        {dashboardData.predictions.cash_flow.total_predicted_inflow.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600">Total Predicted Inflow</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">
                        {dashboardData.predictions.cash_flow.average_daily_flow.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600">Average Daily Flow</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {dashboardData.predictions.cash_flow.predictions.map((prediction, index) => (
                      <div key={index} className="flex items-center justify-between p-2 border rounded">
                        <span className="text-sm">{prediction.date}</span>
                        <span className="font-medium">
                          {prediction.predicted_value.toLocaleString()}
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {(prediction.confidence * 100).toFixed(0)}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risks" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>Risk Overview</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <Badge className={getRiskBadgeColor(dashboardData.risk_assessment.overall_risk_level)} size="lg">
                      {dashboardData.risk_assessment.overall_risk_level}
                    </Badge>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">High Value Pending</span>
                      <span className="font-medium">{dashboardData.risk_assessment.high_value_pending}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Supplier Concentration</span>
                      <span className="font-medium">{dashboardData.risk_assessment.supplier_concentration.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Processing Backlog</span>
                      <span className="font-medium">{dashboardData.risk_assessment.processing_backlog}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5" />
                  <span>Risk Factors</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {dashboardData.risk_assessment.risk_factors.map((factor, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                      <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5" />
                      <div>
                        <div className="font-medium text-gray-900">{factor}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          Monitor closely and implement mitigation strategies
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5" />
                <span>Recommendations</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {dashboardData.summary.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                    <Lightbulb className="h-5 w-5 text-blue-500 mt-0.5" />
                    <div className="text-sm text-gray-700">{recommendation}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
