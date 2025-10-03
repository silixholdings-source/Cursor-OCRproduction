'use client'

import React from 'react'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">AI ERP SaaS</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                className="px-4 py-2 text-gray-700 hover:text-blue-600"
                onClick={() => router.push('/login')}
              >
                Sign In
              </button>
              <button 
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                onClick={() => router.push('/signup')}
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            AI-Powered ERP
            <span className="text-blue-600"> Made Simple</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Automate invoice processing, streamline approvals, and gain real-time insights 
            with our intelligent ERP solution.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => router.push('/dashboard')}
              className="text-lg px-8 py-3 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Go to Dashboard
            </button>
            <button 
              onClick={() => router.push('/demo')}
              className="text-lg px-8 py-3 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
            >
              View Demo
            </button>
            <button 
              onClick={() => router.push('/invoices')}
              className="text-lg px-8 py-3 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
            >
              View Saved Invoices
            </button>
            <button 
              onClick={() => router.push('/ocr')}
              className="text-lg px-8 py-3 border border-blue-300 text-blue-700 rounded hover:bg-blue-50"
            >
              Try OCR Upload
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything you need to modernize your ERP
            </h2>
            <p className="text-xl text-gray-600">
              Powerful features designed to save time and reduce errors
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center hover:shadow-lg transition-shadow bg-white p-6 rounded-lg border">
              <div className="mx-auto w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <div className="text-2xl">📄</div>
              </div>
              <h3 className="text-xl font-semibold mb-2">Smart OCR</h3>
              <p className="text-gray-600">Automatically extract data from invoices and documents</p>
            </div>
            
            <div className="text-center hover:shadow-lg transition-shadow bg-white p-6 rounded-lg border">
              <div className="mx-auto w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <div className="text-2xl">⚡</div>
              </div>
              <h3 className="text-xl font-semibold mb-2">Fast Processing</h3>
              <p className="text-gray-600">Process invoices in seconds, not hours</p>
            </div>
            
            <div className="text-center hover:shadow-lg transition-shadow bg-white p-6 rounded-lg border">
              <div className="mx-auto w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <div className="text-2xl">📊</div>
              </div>
              <h3 className="text-xl font-semibold mb-2">Analytics</h3>
              <p className="text-gray-600">Get insights into your business performance</p>
            </div>
            
            <div className="text-center hover:shadow-lg transition-shadow bg-white p-6 rounded-lg border">
              <div className="mx-auto w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <div className="text-2xl">🔒</div>
              </div>
              <h3 className="text-xl font-semibold mb-2">Secure</h3>
              <p className="text-gray-600">Enterprise-grade security for your data</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}