'use client'

import React from 'react'
// import { DashboardSidebar } from '@/components/dashboard/dashboard-sidebar'
// import { DashboardHeader } from '@/components/dashboard/dashboard-header'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">AI ERP Dashboard</h1>
            <div className="flex items-center space-x-4">
              <button className="px-4 py-2 text-gray-700 hover:text-blue-600">Settings</button>
              <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
      <main className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>
    </div>
  )
}

