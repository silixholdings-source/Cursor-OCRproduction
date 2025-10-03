'use client'

import React from 'react'

export default function DashboardPage() {
  const stats = [
    { title: 'Total Invoices', value: '1,234', change: '+12%', changeType: 'positive' },
    { title: 'Total Amount', value: '$45,678', change: '+8%', changeType: 'positive' },
    { title: 'Pending Approvals', value: '23', change: '-5%', changeType: 'negative' },
    { title: 'Processed Today', value: '156', change: '+15%', changeType: 'positive' }
  ]

  const recentInvoices = [
    { id: 'INV-001', vendor: 'Tech Solutions Inc', amount: '$1,250.00', status: 'Approved', date: '2024-01-15' },
    { id: 'INV-002', vendor: 'Office Supplies Co', amount: '$450.00', status: 'Pending', date: '2024-01-14' },
    { id: 'INV-003', vendor: 'Cloud Services Ltd', amount: '$2,100.00', status: 'Processing', date: '2024-01-13' },
    { id: 'INV-004', vendor: 'Marketing Agency', amount: '$850.00', status: 'Approved', date: '2024-01-12' },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's what's happening with your invoices.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white p-6 rounded-lg border shadow-sm">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="text-sm font-medium text-gray-600">
                {stat.title}
              </h3>
            </div>
            <div className="pt-2">
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
              <div className="flex items-center text-xs">
                <span className={`font-medium ${
                  stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {stat.change}
                </span>
                <span className="text-gray-500 ml-1">from last month</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Invoices */}
        <div className="bg-white p-6 rounded-lg border shadow-sm">
          <div className="pb-4">
            <h3 className="text-xl font-semibold">Recent Invoices</h3>
          </div>
          <div>
            <div className="space-y-4">
              {recentInvoices.map((invoice) => (
                <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{invoice.id}</div>
                    <div className="text-sm text-gray-500">{invoice.vendor}</div>
                    <div className="text-xs text-gray-400">{invoice.date}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium text-gray-900">{invoice.amount}</div>
                    <div className={`text-xs px-2 py-1 rounded-full ${
                      invoice.status === 'Approved' ? 'bg-green-100 text-green-800' :
                      invoice.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {invoice.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50">
                View All Invoices
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white p-6 rounded-lg border shadow-sm">
          <div className="pb-4">
            <h3 className="text-xl font-semibold">Quick Actions</h3>
          </div>
          <div>
            <div className="space-y-4">
              <button className="w-full justify-start flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                📄 Upload New Invoice
              </button>
              <button className="w-full justify-start flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50">
                📊 View Analytics
              </button>
              <button className="w-full justify-start flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50">
                ⚠️ Review Pending
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}