'use client'

import React from 'react'
import { InvoiceSideBySide } from '@/components/invoice/InvoiceSideBySide'

export default function InvoiceUploadPage() {
  return (
    <div className="px-4 sm:px-6 lg:px-8 py-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-4">Upload Invoice</h1>
      <p className="text-gray-600 mb-6">Upload a PDF invoice. The document will preview on the left and extracted data will appear on the right.</p>
      <InvoiceSideBySide />
    </div>
  )
}

















