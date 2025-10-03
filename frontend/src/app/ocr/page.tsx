'use client'

import React, { useState } from 'react'

export default function OcrPage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [saveStatus, setSaveStatus] = useState<string | null>(null)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    setSaveStatus(null)
    
    if (!file) {
      setError('Please select a file first')
      return
    }
    
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      console.log('Uploading file:', file.name)
      
      const res = await fetch(`${apiUrl}/api/v1/ocr/process`, {
        method: 'POST',
        body: formData,
      })
      
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.message || `HTTP ${res.status}`)
      }
      
      const data = await res.json()
      console.log('Full response:', data)
      
      setResult(data)
      
      // Check if invoice was saved successfully
      console.log('Checking save status...')
      console.log('data.save_result:', data.save_result)
      console.log('data.id:', data.id)
      
      if (data.save_result && data.save_result.success) {
        console.log('Using save_result path')
        setSaveStatus(`✅ Invoice saved successfully (ID: ${data.save_result.invoice_id})`)
      } else if (data.id) {
        console.log('Using fallback id path')
        setSaveStatus(`✅ Invoice saved successfully (ID: ${data.id})`)
      } else {
        console.log('No save indicators found')
        setSaveStatus('❌ Invoice processing completed but not saved')
      }
      
    } catch (err: any) {
      console.error('Error:', err)
      setError(err.message || 'Failed to process document')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">OCR Upload</h1>
          <a
            href="/invoices"
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            View Saved Invoices
          </a>
        </div>
        
        <form onSubmit={onSubmit} className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
          <input
            type="file"
            accept="image/*,application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <button
            type="submit"
            disabled={loading || !file}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Process Document'}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 rounded bg-red-50 text-red-700 border border-red-200">
            {error}
          </div>
        )}

        {saveStatus && (
          <div className="mt-6 p-4 rounded bg-green-50 text-green-700 border border-green-200">
            <div className="flex justify-between items-center">
              <span>{saveStatus}</span>
              <a
                href={`/invoices/review/${result?.save_result?.invoice_id || result?.id || '1'}`}
                className="ml-4 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Review & Edit
              </a>
            </div>
          </div>
        )}

        {result && (
          <div className="mt-6 p-6 rounded bg-white border shadow-sm">
            <h2 className="text-xl font-semibold mb-2">Extracted Data</h2>
            {result.extracted_data && (
              <div className="mb-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <strong>Invoice #:</strong> {result.extracted_data.invoice_number || 'N/A'}
                  </div>
                  <div>
                    <strong>PO #:</strong> {result.extracted_data.po_number || 'N/A'}
                  </div>
                  <div>
                    <strong>Vendor:</strong> {result.extracted_data.vendor_name || 'N/A'}
                  </div>
                  <div>
                    <strong>Customer:</strong> {result.extracted_data.customer_name || 'N/A'}
                  </div>
                  <div>
                    <strong>Total:</strong> {result.extracted_data.currency} {result.extracted_data.grand_total || result.extracted_data.total_amount || 'N/A'}
                  </div>
                  <div>
                    <strong>Date:</strong> {result.extracted_data.date || 'N/A'}
                  </div>
                </div>
                {result.extracted_data.line_items && result.extracted_data.line_items.length > 0 && (
                  <div className="mt-4">
                    <strong>Line Items ({result.extracted_data.line_items.length}):</strong>
                    <ul className="mt-2 space-y-1">
                      {result.extracted_data.line_items.map((item: any, index: number) => (
                        <li key={index} className="text-sm text-gray-600">
                          {item.item_code}: {item.description} - {item.quantity} x {item.unit_price} = {item.amount}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            <details className="mt-4">
              <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
                View Raw JSON Data
              </summary>
              <pre className="mt-2 text-xs whitespace-pre-wrap break-words bg-gray-50 p-2 rounded">
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  )
}
