'use client'

import { useState, useEffect } from 'react'
import { useWebSocket } from '@/hooks/use-websocket'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  FileText, 
  Clock, 
  CheckCircle,
  AlertTriangle,
  Users,
  Loader2,
  Wifi,
  WifiOff
} from 'lucide-react'
import { logger } from '@/lib/logger'

interface DashboardStatsProps {
  company: any
}

interface StatsData {
  totalInvoices: number
  pendingApprovals: number
  approvedThisMonth: number
  totalSpent: number
  avgProcessingTime: number
  accuracyRate: number
  activeUsers: number
  storageUsed: number
  company?: {
    max_users: number
    max_storage_gb: number
  }
}

export function DashboardStats({ company }: DashboardStatsProps) {
  const [stats, setStats] = useState<StatsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Real-time WebSocket connection
  const { isConnected, lastMessage } = useWebSocket('ws://localhost:8001/ws', {
    onMessage: (message) => {
      if (message.type === 'stats_update') {
        setStats(message.data)
      }
    },
    onConnect: () => {
      logger.info('Real-time dashboard connected')
    }
  })

  useEffect(() => {
    const loadStats = async () => {
      setIsLoading(true)
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'}/stats/dashboard`)
        if (response.ok) {
          const data = await response.json()
          setStats(data)
        } else {
          throw new Error('Failed to load stats')
        }
      } catch (error) {
        logger.error('Failed to load dashboard stats:', error)
        setError('Failed to load statistics')
        // Fallback to mock data
        setStats({
          totalInvoices: 1247,
          pendingApprovals: 23,
          approvedThisMonth: 89,
          totalSpent: 456789,
          avgProcessingTime: 2.3,
          accuracyRate: 98.5,
          activeUsers: 12,
          storageUsed: 8.2,
          company: {
            max_users: company?.max_users || 5,
            max_storage_gb: company?.max_storage_gb || 10
          }
        })
      } finally {
        setIsLoading(false)
      }
    }
    
    loadStats()
  }, [company])

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, index) => (
          <div key={index} className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 animate-pulse">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0 p-3 rounded-md bg-gray-200">
                  <div className="h-6 w-6 bg-gray-300 rounded"></div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded"></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="col-span-full bg-red-50 border border-red-200 rounded-lg p-4 text-center">
          <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-2" />
          <p className="text-red-800">Failed to load dashboard statistics</p>
        </div>
      </div>
    )
  }
  const statsItems = [
    {
      name: 'Total Invoices',
      value: stats.totalInvoices.toLocaleString(),
      change: '+12%',
      changeType: 'increase' as const,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      name: 'Pending Approvals',
      value: stats.pendingApprovals,
      change: '-5%',
      changeType: 'decrease' as const,
      icon: Clock,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50'
    },
    {
      name: 'Approved This Month',
      value: stats.approvedThisMonth,
      change: '+8%',
      changeType: 'increase' as const,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      name: 'Total Spent',
      value: `$${stats.totalSpent.toLocaleString()}`,
      change: '+15%',
      changeType: 'increase' as const,
      icon: DollarSign,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      name: 'Avg Processing Time',
      value: `${stats.avgProcessingTime} days`,
      change: '-0.5 days',
      changeType: 'decrease' as const,
      icon: TrendingDown,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      name: 'OCR Accuracy',
      value: `${stats.accuracyRate}%`,
      change: '+1.2%',
      changeType: 'increase' as const,
      icon: TrendingUp,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      name: 'Active Users',
      value: stats.activeUsers,
      change: '+2',
      changeType: 'increase' as const,
      icon: Users,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50'
    },
    {
      name: 'Storage Used',
      value: `${stats.storageUsed} GB`,
      change: '2.1 GB',
      changeType: 'increase' as const,
      icon: AlertTriangle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statsItems.map((stat) => (
        <div
          key={stat.name}
          className="bg-white overflow-hidden shadow rounded-lg border border-gray-200"
        >
          <div className="p-5">
            <div className="flex items-center">
              <div className={`flex-shrink-0 p-3 rounded-md ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    {stat.name}
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {stat.value}
                    </div>
                    
                    <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                      stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.changeType === 'increase' ? (
                        <TrendingUp className="self-center flex-shrink-0 h-4 w-4 text-green-500" />
                      ) : (
                        <TrendingDown className="self-center flex-shrink-0 h-4 w-4 text-red-500" />
                      )}
                      <span className="sr-only">
                        {stat.changeType === 'increase' ? 'Increased' : 'Decreased'} by
                      </span>
                      {stat.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          
          {/* Usage indicator for storage */}
          {stat.name === 'Storage Used' && (
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <div className="flex items-center justify-between text-gray-600">
                  <span>Storage Limit</span>
                  <span>{stats.company?.max_storage_gb || 10} GB</span>
                </div>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-orange-500 h-2 rounded-full transition-all duration-300" 
                    style={{ 
                      width: `${Math.min((stats.storageUsed / (stats.company?.max_storage_gb || 10)) * 100, 100)}%` 
                    }}
                  ></div>
                </div>
              </div>
            </div>
          )}
          
          {/* User limit indicator */}
          {stat.name === 'Active Users' && (
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <div className="flex items-center justify-between text-gray-600">
                  <span>User Limit</span>
                  <span>{stats.company?.max_users || 5}</span>
                </div>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-indigo-500 h-2 rounded-full transition-all duration-300" 
                    style={{ 
                      width: `${Math.min((stats.activeUsers / (stats.company?.max_users || 5)) * 100, 100)}%` 
                    }}
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}












