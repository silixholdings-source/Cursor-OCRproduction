'use client'

import React, { useState } from 'react'

export default function TestOcrPage() {
  const [showButton, setShowButton] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-6">Test OCR Button</h1>
      
      <button
        onClick={() => setShowButton(true)}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mb-4"
      >
        Simulate Success
      </button>

      {showButton && (
        <div className="mt-6 p-4 rounded bg-green-50 text-green-700 border border-green-200">
          <div className="flex justify-between items-center">
            <span>✅ Invoice saved successfully (ID: 999)</span>
            <a
              href="/invoices/review/999"
              className="ml-4 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Review & Edit
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
