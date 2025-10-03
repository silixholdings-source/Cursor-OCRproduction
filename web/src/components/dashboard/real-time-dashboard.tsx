'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Activity, TrendingUp, Clock, Users } from 'lucide-react'

export function RealTimeDashboard() {
  const [stats, setStats] = useState({
    activeUsers: 0,
    processingInvoices: 0,
    approvalsPending: 0,
    systemLoad: 0
  })

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setStats(prev => ({
        activeUsers: Math.floor(Math.random() * 50) + 10,
        processingInvoices: Math.floor(Math.random() * 20) + 5,
        approvalsPending: Math.floor(Math.random() * 15) + 3,
        systemLoad: Math.floor(Math.random() * 30) + 10
      }))
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Active Users</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.activeUsers}</div>
          <Badge variant="secondary" className="mt-2">
            <Activity className="w-3 h-3 mr-1" />
            Live
          </Badge>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Processing</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.processingInvoices}</div>
          <Badge variant="secondary" className="mt-2">
            <Clock className="w-3 h-3 mr-1" />
            Real-time
          </Badge>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.approvalsPending}</div>
          <Badge variant="secondary" className="mt-2">
            Awaiting Review
          </Badge>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">System Load</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.systemLoad}%</div>
          <Badge variant="secondary" className="mt-2">
            Optimal
          </Badge>
        </CardContent>
      </Card>
    </div>
  )
}