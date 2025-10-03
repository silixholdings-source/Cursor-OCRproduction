'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts'
import { notifications } from '@/lib/notifications'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ClientButton } from '@/components/ui/client-button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  RealTimeDashboard,
  AnalyticsDashboard,
  PerformanceDashboard,
  SecurityDashboard,
  AuditDashboard,
  IntegrationDashboard,
  AIInsightsDashboard,
  AdvancedDashboard,
} from '@/components/dashboard'
import { AdvancedAnalytics } from '@/components/dashboard/advanced-analytics'
import { EnhancedInvoiceProcessor } from '@/components/invoice/enhanced-invoice-processor'
import { AdvancedSearch } from '@/components/search/advanced-search'
import { TrialBanner } from '@/components/trial/trial-banner'
import {
  Activity,
  BarChart3,
  Cpu,
  Shield,
  FileText,
  Plug,
  Brain,
  Settings,
  TrendingUp,
  Users,
  DollarSign,
  Clock,
  CheckCircle,
  AlertTriangle,
  Zap,
  Database,
  Server,
  Globe,
  HardDrive,
  Wifi,
  AlertCircle,
  XCircle,
  Play,
  Pause,
  RotateCcw,
  Download,
  Filter,
  Calendar,
  Eye,
  RefreshCw,
  Lightbulb,
  Target,
  TrendingDown,
  BarChart3 as BarChart3Icon,
  PieChart as PieChartIcon,
  LineChart as LineChartIcon,
  Activity as ActivityIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  DollarSign as DollarSignIcon,
  FileText as FileTextIcon,
  Clock as ClockIcon,
  Users as UsersIcon,
  Building as BuildingIcon,
  Zap as ZapIcon,
  Database as DatabaseIcon,
  Server as ServerIcon,
  Globe as GlobeIcon,
  Cpu as CpuIcon,
  HardDrive as HardDriveIcon,
  Wifi as WifiIcon,
  AlertTriangle as AlertTriangleIcon,
  XCircle as XCircleIcon,
  Play as PlayIcon,
  Pause as PauseIcon,
  RotateCcw as RotateCcwIcon,
  Settings as SettingsIcon,
  Plug as PlugIcon,
  Brain as BrainIcon,
  Download as DownloadIcon,
  Filter as FilterIcon,
  Calendar as CalendarIcon,
  Eye as EyeIcon,
  RefreshCw as RefreshCwIcon,
  Lightbulb as LightbulbIcon,
  Target as TargetIcon,
  Shield as ShieldIcon,
  CheckCircle as CheckCircleIcon,
  AlertCircle as AlertCircleIcon,
  Activity as ActivityIcon2,
  TrendingUp as TrendingUpIcon2,
  TrendingDown as TrendingDownIcon2,
  DollarSign as DollarSignIcon2,
  FileText as FileTextIcon2,
  Clock as ClockIcon2,
  Users as UsersIcon2,
  Building as BuildingIcon2,
  Zap as ZapIcon2,
  Database as DatabaseIcon2,
  Server as ServerIcon2,
  Globe as GlobeIcon2,
  Cpu as CpuIcon2,
  HardDrive as HardDriveIcon2,
  Wifi as WifiIcon2,
  AlertTriangle as AlertTriangleIcon2,
  XCircle as XCircleIcon2,
  Play as PlayIcon2,
  Pause as PauseIcon2,
  RotateCcw as RotateCcwIcon2,
  Settings as SettingsIcon2,
  Download as DownloadIcon2,
  Filter as FilterIcon2,
  Calendar as CalendarIcon2,
  Eye as EyeIcon2,
  RefreshCw as RefreshCwIcon2,
  Lightbulb as LightbulbIcon2,
  Target as TargetIcon2,
  Shield as ShieldIcon2,
  CheckCircle as CheckCircleIcon2,
  AlertCircle as AlertCircleIcon2,
} from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState('overview')
  const [isConnected, setIsConnected] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Setup keyboard shortcuts for dashboard
  useKeyboardShortcuts([
    {
      key: '1',
      ctrlKey: true,
      description: 'Switch to Overview tab',
      action: () => setActiveTab('overview')
    },
    {
      key: '2',
      ctrlKey: true,
      description: 'Switch to Real-time tab',
      action: () => setActiveTab('realtime')
    },
    {
      key: '3',
      ctrlKey: true,
      description: 'Switch to Analytics tab',
      action: () => setActiveTab('analytics')
    },
    {
      key: 'f5',
      description: 'Refresh dashboard data',
      action: () => {
        notifications.info('Refreshing dashboard data...', 'Dashboard')
        window.location.reload()
      }
    }
  ])

  // Quick Actions handlers
  const handleProcessInvoice = () => {
    router.push('/dashboard/invoices?action=upload')
  }

  const handleApprovePending = () => {
    router.push('/dashboard/approvals')
  }

  const handleViewReports = () => {
    router.push('/dashboard/analytics')
  }

  const handleERPSettings = () => {
    router.push('/dashboard/erp')
  }

  // Mock data for quick overview
  const quickStats = [
    {
      title: 'Total Invoices',
      value: '12,450',
      change: 12.5,
      changeType: 'positive' as const,
      icon: <FileTextIcon className="h-4 w-4" />,
      description: 'All time processed',
    },
    {
      title: 'Processed Today',
      value: '245',
      change: 8.2,
      changeType: 'positive' as const,
      icon: <TrendingUpIcon className="h-4 w-4" />,
      description: 'Last 24 hours',
    },
    {
      title: 'Pending Approval',
      value: '18',
      change: -15.3,
      changeType: 'positive' as const,
      icon: <ClockIcon className="h-4 w-4" />,
      description: 'Awaiting review',
    },
    {
      title: 'Total Amount',
      value: '$2,450,000',
      change: 23.1,
      changeType: 'positive' as const,
      icon: <DollarSignIcon className="h-4 w-4" />,
      description: 'Processed value',
    },
    {
      title: 'Success Rate',
      value: '98.5%',
      change: 2.1,
      changeType: 'positive' as const,
      icon: <CheckCircleIcon className="h-4 w-4" />,
      description: 'Processing accuracy',
    },
    {
      title: 'Avg Processing Time',
      value: '2.3s',
      change: -8.5,
      changeType: 'positive' as const,
      icon: <ClockIcon className="h-4 w-4" />,
      description: 'Per invoice',
    },
    {
      title: 'Active Users',
      value: '156',
      change: 5.2,
      changeType: 'positive' as const,
      icon: <UsersIcon className="h-4 w-4" />,
      description: 'Currently online',
    },
    {
      title: 'System Health',
      value: '99.9%',
      change: 0.1,
      changeType: 'positive' as const,
      icon: <ShieldIcon className="h-4 w-4" />,
      description: 'Uptime',
    },
  ]

  const dashboardTabs = [
    { id: 'overview', label: 'Overview', icon: <ActivityIcon className="h-4 w-4" /> },
    { id: 'realtime', label: 'Real-time', icon: <ZapIcon className="h-4 w-4" /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3Icon className="h-4 w-4" /> },
    { id: 'performance', label: 'Performance', icon: <CpuIcon className="h-4 w-4" /> },
    { id: 'security', label: 'Security', icon: <ShieldIcon className="h-4 w-4" /> },
    { id: 'audit', label: 'Audit', icon: <FileTextIcon className="h-4 w-4" /> },
    { id: 'integrations', label: 'Integrations', icon: <PlugIcon className="h-4 w-4" /> },
    { id: 'ai', label: 'AI Insights', icon: <BrainIcon className="h-4 w-4" /> },
    { id: 'advanced', label: 'Advanced', icon: <SettingsIcon className="h-4 w-4" /> },
  ]

  const renderDashboardContent = () => {
    switch (activeTab) {
      case 'realtime':
        return <RealTimeDashboard />
      case 'analytics':
        return <AnalyticsDashboard />
      case 'performance':
        return <PerformanceDashboard />
      case 'security':
        return <SecurityDashboard />
      case 'audit':
        return <AuditDashboard />
      case 'integrations':
        return <IntegrationDashboard />
      case 'ai':
        return <AIInsightsDashboard />
      case 'advanced':
        return <AdvancedDashboard />
      default:
        return (
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {quickStats.map((stat, index) => (
                <Card key={index}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      {stat.title}
                    </CardTitle>
                    <div className="text-gray-400">{stat.icon}</div>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stat.value}</div>
                    <div className="flex items-center space-x-2 text-xs">
                      <Badge
                        variant={
                          stat.changeType === 'positive'
                            ? 'default'
                            : stat.changeType === 'negative'
                            ? 'destructive'
                            : 'secondary'
                        }
                      >
                        {stat.changeType === 'positive' && '+'}
                        {stat.change}%
                      </Badge>
                      <span className="text-gray-500">vs last month</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{stat.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <ClientButton 
                    variant="outline" 
                    className="h-20 flex-col hover:bg-blue-50 hover:border-blue-200 transition-colors"
                    onClick={handleProcessInvoice}
                  >
                    <FileTextIcon className="h-6 w-6 mb-2 text-blue-600" />
                    <span className="text-sm font-medium">Process Invoice</span>
                  </ClientButton>
                  <ClientButton 
                    variant="outline" 
                    className="h-20 flex-col hover:bg-green-50 hover:border-green-200 transition-colors"
                    onClick={handleApprovePending}
                  >
                    <CheckCircleIcon className="h-6 w-6 mb-2 text-green-600" />
                    <span className="text-sm font-medium">Approve Pending</span>
                  </ClientButton>
                  <ClientButton 
                    variant="outline" 
                    className="h-20 flex-col hover:bg-purple-50 hover:border-purple-200 transition-colors"
                    onClick={handleViewReports}
                  >
                    <BarChart3Icon className="h-6 w-6 mb-2 text-purple-600" />
                    <span className="text-sm font-medium">View Reports</span>
                  </ClientButton>
                  <ClientButton 
                    variant="outline" 
                    className="h-20 flex-col hover:bg-orange-50 hover:border-orange-200 transition-colors"
                    onClick={handleERPSettings}
                  >
                    <BuildingIcon className="h-6 w-6 mb-2 text-orange-600" />
                    <span className="text-sm font-medium">ERP Settings</span>
                  </ClientButton>
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { action: 'Invoice processed', user: 'John Doe', time: '2 minutes ago', status: 'success' },
                    { action: 'Approval given', user: 'Jane Smith', time: '5 minutes ago', status: 'success' },
                    { action: 'Error occurred', user: 'System', time: '10 minutes ago', status: 'error' },
                    { action: 'User logged in', user: 'Mike Johnson', time: '15 minutes ago', status: 'success' },
                  ].map((activity, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          {activity.status === 'success' ? (
                            <CheckCircleIcon className="h-4 w-4 text-green-500" />
                          ) : (
                            <XCircleIcon className="h-4 w-4 text-red-500" />
                          )}
                        </div>
                        <div>
                          <div className="font-medium">{activity.action}</div>
                          <div className="text-sm text-gray-500">by {activity.user}</div>
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">{activity.time}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="space-y-6 p-6">
        {/* Trial Banner */}
        <TrialBanner />
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-gray-600">Comprehensive system monitoring and analytics</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <ClientButton
              variant={autoRefresh ? 'default' : 'outline'}
              onClick={() => setAutoRefresh(!autoRefresh)}
            >
              <RefreshCwIcon className="h-4 w-4 mr-2" />
              {autoRefresh ? 'Auto Refresh ON' : 'Auto Refresh OFF'}
            </ClientButton>
          </div>
        </div>

        {/* Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 md:grid-cols-5 lg:grid-cols-9">
            {dashboardTabs.map((tab) => (
              <TabsTrigger key={tab.id} value={tab.id} className="flex items-center space-x-2">
                {tab.icon}
                <span className="hidden sm:inline">{tab.label}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="overview">
            {renderDashboardContent()}
          </TabsContent>
          <TabsContent value="realtime">
            <RealTimeDashboard />
          </TabsContent>
          <TabsContent value="analytics">
            <AnalyticsDashboard />
          </TabsContent>
          <TabsContent value="performance">
            <PerformanceDashboard />
          </TabsContent>
          <TabsContent value="security">
            <SecurityDashboard />
          </TabsContent>
          <TabsContent value="audit">
            <AuditDashboard />
          </TabsContent>
          <TabsContent value="integrations">
            <IntegrationDashboard />
          </TabsContent>
          <TabsContent value="ai">
            <AIInsightsDashboard />
          </TabsContent>
          <TabsContent value="advanced">
            <AdvancedDashboard />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}