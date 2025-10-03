'use client'

import React, { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'

interface InvoiceData {
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

interface Invoice {
  id: number
  extracted_data: InvoiceData
  confidence: number
  processing_method: string
  manually_corrected?: boolean
  created_at: string
  updated_at?: string
}

export default function InvoiceReviewPage() {
  const router = useRouter()
  const params = useParams()
  const invoiceId = params.id as string

  const [invoice, setInvoice] = useState<Invoice | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form data
  const [formData, setFormData] = useState<InvoiceData>({
    invoice_number: '',
    po_number: '',
    vendor_name: '',
    customer_name: '',
    total_amount: 0,
    currency: 'ZAR',
    date: '',
    line_items: [],
    subtotal: 0,
    vat_amount: 0,
    grand_total: 0
  })

  useEffect(() => {
    if (invoiceId) {
      fetchInvoice()
    }
  }, [invoiceId])

  const fetchInvoice = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/invoices/${invoiceId}`)
      if (response.ok) {
        const data = await response.json()
        setInvoice(data.invoice)
        setFormData(data.invoice.extracted_data)
      } else {
        setError('Failed to load invoice')
      }
    } catch (err) {
      setError('Error loading invoice')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field: keyof InvoiceData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleLineItemChange = (index: number, field: string, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      line_items: prev.line_items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }))
  }

  const addLineItem = () => {
    setFormData(prev => ({
      ...prev,
      line_items: [...prev.line_items, {
        item_code: '',
        description: '',
        quantity: 1,
        unit: 'EACH',
        unit_price: 0,
        amount: 0
      }]
    }))
  }

  const removeLineItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index)
    }))
  }

  const calculateTotals = () => {
    const subtotal = formData.line_items.reduce((sum, item) => sum + (item.amount || 0), 0)
    const vat = subtotal * 0.15 // 15% VAT
    const grandTotal = subtotal + vat

    setFormData(prev => ({
      ...prev,
      subtotal,
      vat_amount: vat,
      grand_total: grandTotal
    }))
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const response = await fetch(`http://localhost:8000/api/v1/invoices/${invoiceId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          extracted_data: formData
        })
      })

      if (response.ok) {
        setSuccess('Invoice updated successfully!')
        setTimeout(() => {
          router.push('/invoices')
        }, 2000)
      } else {
        setError('Failed to update invoice')
      }
    } catch (err) {
      setError('Error updating invoice')
    } finally {
      setSaving(false)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.8) return 'High'
    if (confidence >= 0.5) return 'Medium'
    return 'Low'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading invoice...</p>
        </div>
      </div>
    )
  }

  if (!invoice) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Invoice Not Found</h1>
          <button
            onClick={() => router.push('/invoices')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Back to Invoices
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Review Invoice #{invoiceId}</h1>
              <p className="text-gray-600">
                Confidence: <span className={getConfidenceColor(invoice.confidence)}>
                  {getConfidenceText(invoice.confidence)}
                </span> ({Math.round(invoice.confidence * 100)}%)
              </p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => router.push('/invoices')}
                className="px-4 py-2 text-gray-700 hover:text-blue-600"
              >
                Back to Invoices
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4">
            <p className="text-green-800">{success}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Invoice Number *
                </label>
                <input
                  type="text"
                  value={formData.invoice_number}
                  onChange={(e) => handleInputChange('invoice_number', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter invoice number"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  PO Number
                </label>
                <input
                  type="text"
                  value={formData.po_number}
                  onChange={(e) => handleInputChange('po_number', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter PO number"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Vendor Name *
                </label>
                <input
                  type="text"
                  value={formData.vendor_name}
                  onChange={(e) => handleInputChange('vendor_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter vendor name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Customer Name
                </label>
                <input
                  type="text"
                  value={formData.customer_name}
                  onChange={(e) => handleInputChange('customer_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter customer name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date
                </label>
                <input
                  type="text"
                  value={formData.date}
                  onChange={(e) => handleInputChange('date', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter date (DD/MM/YY)"
                />
              </div>
            </div>
          </div>

          {/* Financial Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Information</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Currency
                </label>
                <select
                  value={formData.currency}
                  onChange={(e) => handleInputChange('currency', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ZAR">ZAR (South African Rand)</option>
                  <option value="USD">USD (US Dollar)</option>
                  <option value="EUR">EUR (Euro)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subtotal
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.subtotal}
                  onChange={(e) => handleInputChange('subtotal', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  VAT Amount
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.vat_amount}
                  onChange={(e) => handleInputChange('vat_amount', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Grand Total
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.grand_total}
                  onChange={(e) => handleInputChange('grand_total', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={calculateTotals}
                className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Recalculate Totals
              </button>
            </div>
          </div>
        </div>

        {/* Line Items */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Line Items</h2>
            <button
              onClick={addLineItem}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Add Line Item
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Item Code
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Qty
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unit Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {formData.line_items.map((item, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="text"
                        value={item.item_code}
                        onChange={(e) => handleLineItemChange(index, 'item_code', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <input
                        type="text"
                        value={item.description}
                        onChange={(e) => handleLineItemChange(index, 'description', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => handleLineItemChange(index, 'quantity', parseInt(e.target.value) || 0)}
                        className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="text"
                        value={item.unit}
                        onChange={(e) => handleLineItemChange(index, 'unit', e.target.value)}
                        className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="number"
                        step="0.01"
                        value={item.unit_price}
                        onChange={(e) => handleLineItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                        className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="number"
                        step="0.01"
                        value={item.amount}
                        onChange={(e) => handleLineItemChange(index, 'amount', parseFloat(e.target.value) || 0)}
                        className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => removeLineItem(index)}
                        className="text-red-600 hover:text-red-900 text-sm"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* OCR Information */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">OCR Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Processing Method:</span>
              <span className="ml-2 text-gray-600">{invoice.processing_method}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Created:</span>
              <span className="ml-2 text-gray-600">
                {new Date(invoice.created_at).toLocaleString()}
              </span>
            </div>
            {invoice.manually_corrected && (
              <div>
                <span className="font-medium text-gray-700">Manually Corrected:</span>
                <span className="ml-2 text-green-600">Yes</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
