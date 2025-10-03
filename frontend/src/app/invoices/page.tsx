'use client'

import React, { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'

interface Invoice {
  id: number
  success: boolean
  document_type: string
  extracted_data: {
    invoice_number: string
    po_number: string
    vendor_name: string
    customer_name: string
    total_amount: number
    currency: string
    date: string
    line_items: Array<{
      item_code: string
      description: string
      quantity: number
      unit: string
      unit_price: number
      amount: number
    }>
    subtotal: number
    vat_amount: number
    grand_total: number
  }
  confidence: number
  processing_method: string
  saved_at: string
  manually_corrected?: boolean
  updated_at?: string
}

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadInvoices()
  }, [])

  const loadInvoices = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getInvoices() as any
      setInvoices(response.invoices || [])
    } catch (err: any) {
      setError(err.message || 'Failed to load invoices')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: currency === 'ZAR' ? 'ZAR' : 'USD',
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading invoices...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">Error</div>
          <p className="text-gray-600">{error}</p>
          <button
            onClick={loadInvoices}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Saved Invoices</h1>
          <p className="mt-2 text-gray-600">
            {invoices.length} invoice{invoices.length !== 1 ? 's' : ''} saved
          </p>
        </div>

        {invoices.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📄</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No invoices saved yet</h3>
            <p className="text-gray-600 mb-6">Upload and process invoices to see them here.</p>
            <a
              href="/ocr"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Process New Invoice
            </a>
          </div>
        ) : (
          <div className="space-y-6">
            {invoices.map((invoice) => (
              <div key={invoice.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {invoice.extracted_data.invoice_number || 'No Invoice Number'}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {invoice.extracted_data.vendor_name} → {invoice.extracted_data.customer_name}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">
                      {formatCurrency(invoice.extracted_data.grand_total, invoice.extracted_data.currency)}
                    </div>
                    <div className="text-sm text-gray-500">
                      {formatDate(invoice.saved_at)}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">PO Number</label>
                    <p className="text-sm text-gray-900">{invoice.extracted_data.po_number || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Date</label>
                    <p className="text-sm text-gray-900">{invoice.extracted_data.date || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Items</label>
                    <p className="text-sm text-gray-900">{invoice.extracted_data.line_items.length}</p>
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Method</label>
                    <p className="text-sm text-gray-900 capitalize">{invoice.processing_method || 'unknown'}</p>
                  </div>
                </div>

                {invoice.extracted_data.line_items.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Line Items</h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {invoice.extracted_data.line_items.map((item, index) => (
                            <tr key={index}>
                              <td className="px-3 py-2 text-sm text-gray-900">{item.item_code}</td>
                              <td className="px-3 py-2 text-sm text-gray-900">{item.description}</td>
                              <td className="px-3 py-2 text-sm text-gray-900">{item.quantity} {item.unit}</td>
                              <td className="px-3 py-2 text-sm text-gray-900">
                                {formatCurrency(item.unit_price, invoice.extracted_data.currency)}
                              </td>
                              <td className="px-3 py-2 text-sm text-gray-900">
                                {formatCurrency(item.amount, invoice.extracted_data.currency)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex justify-between text-sm">
                    <span>Subtotal:</span>
                    <span>{formatCurrency(invoice.extracted_data.subtotal, invoice.extracted_data.currency)}</span>
                  </div>
                  {invoice.extracted_data.vat_amount > 0 && (
                    <div className="flex justify-between text-sm">
                      <span>VAT:</span>
                      <span>{formatCurrency(invoice.extracted_data.vat_amount, invoice.extracted_data.currency)}</span>
                    </div>
                  )}
                  <div className="flex justify-between font-semibold">
                    <span>Total:</span>
                    <span>{formatCurrency(invoice.extracted_data.grand_total, invoice.extracted_data.currency)}</span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-500">
                        Confidence: <span className={`font-medium ${
                          invoice.confidence >= 0.8 ? 'text-green-600' : 
                          invoice.confidence >= 0.5 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {Math.round(invoice.confidence * 100)}%
                        </span>
                      </span>
                      {invoice.manually_corrected && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Manually Corrected
                        </span>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      <a
                        href={`/invoices/review/${invoice.id}`}
                        className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Review & Edit
                      </a>
                      <button
                        onClick={() => {
                          if (confirm('Are you sure you want to delete this invoice?')) {
                            // TODO: Implement delete functionality
                            console.log('Delete invoice', invoice.id)
                          }
                        }}
                        className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
