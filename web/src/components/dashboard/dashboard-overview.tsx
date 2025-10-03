'use client'

import { useRouter } from 'next/navigation'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  FileText, 
  Users,
  Calendar,
  BarChart3,
  Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button'

interface DashboardOverviewProps {
  company: any
}

// Mock data - in production this would come from API
const mockOverviewData = {
  monthlyTrends: [
    { month: 'Oct', invoices: 45, amount: 125000 },
    { month: 'Nov', invoices: 52, amount: 138000 },
    { month: 'Dec', invoices: 48, amount: 142000 },
    { month: 'Jan', invoices: 61, amount: 156000 }
  ],
  topVendors: [
    { name: 'Tech Supplies Inc', invoices: 23, amount: 45600 },
    { name: 'Cloud Services Ltd', invoices: 18, amount: 32400 },
    { name: 'Office Furniture Co', invoices: 15, amount: 28700 },
    { name: 'Marketing Solutions', invoices: 12, amount: 23400 }
  ],
  recentActivity: [
    { type: 'invoice_uploaded', message: 'New invoice uploaded by John Doe', time: '2 hours ago' },
    { type: 'invoice_approved', message: 'Invoice INV-002 approved by Jane Smith', time: '4 hours ago' },
    { type: 'user_added', message: 'New user Sarah Wilson added to system', time: '6 hours ago' },
    { type: 'erp_sync', message: 'ERP sync completed successfully', time: '8 hours ago' }
  ]
}

const activityIcons = {
  invoice_uploaded: FileText,
  invoice_approved: TrendingUp,
  user_added: Users,
  erp_sync: Zap
}

const activityColors = {
  invoice_uploaded: 'text-blue-600 bg-blue-50',
  invoice_approved: 'text-green-600 bg-green-50',
  user_added: 'text-purple-600 bg-purple-50',
  erp_sync: 'text-orange-600 bg-orange-50'
}

export function DashboardOverview({ company }: DashboardOverviewProps) {
  const router = useRouter()
  const currentMonth = mockOverviewData.monthlyTrends[mockOverviewData.monthlyTrends.length - 1]
  const previousMonth = mockOverviewData.monthlyTrends[mockOverviewData.monthlyTrends.length - 2]
  
  const invoiceGrowth = currentMonth && previousMonth 
    ? ((currentMonth.invoices - previousMonth.invoices) / previousMonth.invoices * 100).toFixed(1)
    : '0.0'
  const amountGrowth = currentMonth && previousMonth 
    ? ((currentMonth.amount - previousMonth.amount) / previousMonth.amount * 100).toFixed(1)
    : '0.0'

  return (
    <div className="space-y-6">
      {/* Monthly Trends */}
      <div className="bg-white shadow rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Monthly Trends</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm font-medium text-gray-500">Invoices Processed</h4>
                <div className="flex items-center space-x-2">
                  {parseFloat(invoiceGrowth) >= 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  )}
                  <span className={`text-sm font-medium ${
                    parseFloat(invoiceGrowth) >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {invoiceGrowth}%
                  </span>
                </div>
              </div>
              <div className="text-3xl font-bold text-gray-900">{currentMonth?.invoices || 0}</div>
              <p className="text-sm text-gray-500">vs {previousMonth?.invoices || 0} last month</p>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm font-medium text-gray-500">Total Amount</h4>
                <div className="flex items-center space-x-2">
                  {parseFloat(amountGrowth) >= 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  )}
                  <span className={`text-sm font-medium ${
                    parseFloat(amountGrowth) >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {amountGrowth}%
                  </span>
                </div>
              </div>
              <div className="text-3xl font-bold text-gray-900">
                ${((currentMonth?.amount || 0) / 1000).toFixed(0)}k
              </div>
              <p className="text-sm text-gray-500">vs ${((previousMonth?.amount || 0) / 1000).toFixed(0)}k last month</p>
            </div>
          </div>
          
          {/* Simple chart */}
          <div className="mt-6">
            <div className="flex items-end space-x-2 h-32">
              {mockOverviewData.monthlyTrends.map((month, index) => (
                <div key={month.month} className="flex-1 flex flex-col items-center">
                  <div 
                    className="w-full bg-blue-500 rounded-t transition-all duration-300 hover:bg-blue-600 chart-bar"
                    style={{ 
                      '--chart-height': Math.min((month.invoices / Math.max(...mockOverviewData.monthlyTrends.map(m => m.invoices))) * 100, 100) 
                    } as React.CSSProperties}
                  ></div>
                  <span className="text-xs text-gray-500 mt-2">{month.month}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Top Vendors and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Vendors */}
        <div className="bg-white shadow rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Top Vendors</h3>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => router.push('/dashboard/vendors')}
              >
                View All
              </Button>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {mockOverviewData.topVendors.map((vendor, index) => (
              <div key={vendor.name} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">{index + 1}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{vendor.name}</p>
                      <p className="text-sm text-gray-500">{vendor.invoices} invoices</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      ${vendor.amount.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white shadow rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {mockOverviewData.recentActivity.map((activity, index) => {
              const ActivityIcon = activityIcons[activity.type as keyof typeof activityIcons]
              const iconColor = activityColors[activity.type as keyof typeof activityColors]
              
              return (
                <div key={index} className="px-6 py-4">
                  <div className="flex items-start space-x-3">
                    <div className={`flex-shrink-0 p-2 rounded-md ${iconColor}`}>
                      <ActivityIcon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900">{activity.message}</p>
                      <p className="text-sm text-gray-500">{activity.time}</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Company Insights */}
      <div className="bg-white shadow rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Company Insights</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <BarChart3 className="h-8 w-8 text-blue-600" />
              </div>
              <h4 className="text-sm font-medium text-gray-900">Processing Efficiency</h4>
              <p className="text-2xl font-bold text-blue-600">98.5%</p>
              <p className="text-sm text-gray-500">OCR accuracy rate</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Calendar className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="text-sm font-medium text-gray-900">Avg Processing Time</h4>
              <p className="text-2xl font-bold text-green-600">2.3 days</p>
              <p className="text-sm text-gray-500">From upload to approval</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Zap className="h-8 w-8 text-purple-600" />
              </div>
              <h4 className="text-sm font-medium text-gray-900">Automation Rate</h4>
              <p className="text-2xl font-bold text-purple-600">87%</p>
              <p className="text-sm text-gray-500">Fully automated workflows</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}












