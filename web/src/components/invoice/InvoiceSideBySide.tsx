'use client'

import React, { useCallback, useMemo, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, FileText, Upload, X } from 'lucide-react'
import { getApiBaseUrl } from '@/lib/api'

type ExtractedInvoice = {
  supplier_name?: string
  invoice_number?: string
  invoice_date?: string
  due_date?: string
  total_amount?: number
  currency?: string
  tax_amount?: number
  subtotal?: number
  total_with_tax?: number
  line_items?: Array<{
    description?: string
    quantity?: number
    unit_price?: number
    total?: number
  }>
  confidence_scores?: Record<string, number>
  processing_metadata?: Record<string, any>
}

export function InvoiceSideBySide() {
  const [file, setFile] = useState<File | null>(null)
  const [fileUrl, setFileUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [data, setData] = useState<ExtractedInvoice | null>(null)

  const validatePdfMagic = async (file: File) => {
    // Lightweight header check for PDF
    const header = await file.slice(0, 5).arrayBuffer()
    const bytes = new Uint8Array(header)
    const isPdf = bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46
    if (!isPdf) throw new Error('Invalid PDF file format')
  }

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setError(null)
    setData(null)
    setProgress(0)
    const f = acceptedFiles[0]
    if (!f) return

    // Client-side validation
    if (!f.name.toLowerCase().endsWith('.pdf')) {
      setError('Unsupported file type. Please upload a PDF.')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit')
      return
    }
    try {
      await validatePdfMagic(f)
    } catch (e: any) {
      setError(e.message || 'Invalid PDF file')
      return
    }

    const url = URL.createObjectURL(f)
    setFile(f)
    setFileUrl(url)

    // Upload and process
    setIsProcessing(true)
    setProgress(20)
    try {
      const form = new FormData()
      form.append('file', f)

      setProgress(40)
      const apiBase = getApiBaseUrl()
      const token = (typeof window !== 'undefined') ? localStorage.getItem('auth_token') : null
      // Prefer authenticated processing; fall back to demo endpoint if unauthenticated or 401
      // Prefer proxy first to avoid CSP/CORS variations across ports
      let resp = await fetch(`/api/processing/process`, {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : undefined,
        body: form,
      })
      if (!resp.ok && (!token || resp.status === 401)) {
        // Try backend directly; if blocked by CSP/CORS, fall back to Next.js API route proxy
        try {
          resp = await fetch(`${apiBase}/processing/process`, {
            method: 'POST',
            headers: token ? { 'Authorization': `Bearer ${token}` } : undefined,
            body: form,
          })
        } catch (_) {
          // finally try demo
          try {
            resp = await fetch(`${apiBase}/processing/demo`, {
              method: 'POST',
              body: form,
            })
          } catch {
            resp = await fetch(`/api/processing/demo`, {
            method: 'POST',
            body: form,
          })
          }
        }
      }

      setProgress(70)
      if (!resp.ok) {
        const detail = await resp.json().catch(() => null)
        throw new Error(detail?.detail || 'Invoice processing failed')
      }
      const result = await resp.json()

      // If demo route returned OCR directly, use it without status lookup
      if (result?.ocr_data && !result?.invoice_id) {
        const ocr = result.ocr_data || {}
        setProgress(90)
        setData({
          supplier_name: ocr.supplier_name,
          invoice_number: ocr.invoice_number,
          invoice_date: ocr.invoice_date,
          due_date: ocr.due_date,
          total_amount: ocr.total_amount,
          currency: ocr.currency,
          tax_amount: ocr.tax_amount,
          subtotal: ocr.subtotal,
          total_with_tax: ocr.total_with_tax,
          line_items: ocr.line_items,
          confidence_scores: ocr.confidence_scores,
          processing_metadata: ocr.processing_metadata,
        })
        setProgress(100)
        return
      }

      // Handle duplicate or error statuses from processing API
      if (result?.status === 'duplicate') {
        throw new Error('Duplicate invoice detected')
      }

      // Fetch status by invoice_id to get OCR data stored on invoice
      if (result?.invoice_id) {
        const statusResp = await fetch(`${apiBase}/processing/status/${result.invoice_id}`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : undefined,
        })
        if (!statusResp.ok) {
          const detail = await statusResp.json().catch(() => null)
          throw new Error(detail?.detail || 'Failed to retrieve invoice status')
        }
        const statusJson = await statusResp.json()

        const ocr = statusJson?.ocr_data || {}
        setProgress(90)
        setData({
          supplier_name: ocr.supplier_name,
          invoice_number: ocr.invoice_number,
          invoice_date: ocr.invoice_date,
          due_date: ocr.due_date,
          total_amount: ocr.total_amount,
          currency: ocr.currency,
          tax_amount: ocr.tax_amount,
          subtotal: ocr.subtotal,
          total_with_tax: ocr.total_with_tax,
          line_items: ocr.line_items,
          confidence_scores: ocr.confidence_scores,
          processing_metadata: ocr.processing_metadata,
        })
      } else {
        throw new Error('Processing did not return an invoice ID')
      }
      setProgress(100)
    } catch (e: any) {
      setError(e.message || 'Processing failed')
      setData(null)
      setProgress(0)
    } finally {
      setIsProcessing(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  })

  const confidence = useMemo(() => {
    const scores = data?.confidence_scores
    if (!scores) return null
    const vals = Object.values(scores)
    if (!vals.length) return null
    const avg = vals.reduce((a, b) => a + (typeof b === 'number' ? b : 0), 0) / vals.length
    return Math.round(avg * 100)
  }, [data])

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Upload PDF Invoice</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
              isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <FileText className="h-10 w-10 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-800 font-medium">{isDragActive ? 'Drop the PDF here' : 'Drag & drop or click to select a PDF'}</p>
            <p className="text-sm text-gray-500">Only PDF, up to 10MB</p>
            {isProcessing && (
              <div className="mt-3">
                <Progress value={progress} />
                <p className="text-xs text-gray-500 mt-1">Processing...</p>
              </div>
            )}
            {error && (
              <div className="mt-3 inline-flex items-center text-sm text-red-700">
                <AlertTriangle className="h-4 w-4 mr-1" /> {error}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Side-by-side layout */}
      {fileUrl && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Left: PDF preview */}
          <Card>
            <CardHeader>
              <CardTitle>PDF Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="w-full aspect-[8.5/11] border rounded overflow-hidden bg-gray-100">
                <iframe src={fileUrl} className="w-full h-[80vh]" title="Invoice PDF" />
              </div>
              <div className="flex justify-end mt-2">
                <Button variant="ghost" size="sm" onClick={() => { if (fileUrl) URL.revokeObjectURL(fileUrl); setFile(null); setFileUrl(null); setData(null); setError(null); }}>
                  <X className="h-4 w-4 mr-1" /> Clear
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Right: Extracted data */}
          <Card>
            <CardHeader>
              <CardTitle>Extracted Data</CardTitle>
            </CardHeader>
            <CardContent>
              {!data ? (
                <p className="text-gray-500">Processing results will appear here.</p>
              ) : (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label>Supplier</Label>
                      <Input value={data.supplier_name || ''} readOnly />
                    </div>
                    <div>
                      <Label>Invoice #</Label>
                      <Input value={data.invoice_number || ''} readOnly />
                    </div>
                    <div>
                      <Label>Invoice Date</Label>
                      <Input value={data.invoice_date || ''} readOnly />
                    </div>
                    <div>
                      <Label>Due Date</Label>
                      <Input value={data.due_date || ''} readOnly />
                    </div>
                    <div>
                      <Label>Total Amount</Label>
                      <Input value={data.total_amount != null ? String(data.total_amount) : ''} readOnly />
                    </div>
                    <div>
                      <Label>Currency</Label>
                      <Input value={data.currency || ''} readOnly />
                    </div>
                  </div>

                  {confidence != null && (
                    <div>
                      <Badge>{confidence}% average confidence</Badge>
                    </div>
                  )}

                  <div>
                    <Label>Line Items</Label>
                    <div className="mt-2 space-y-2">
                      {(data.line_items || []).map((li, idx) => (
                        <div key={idx} className="grid grid-cols-12 gap-2 text-sm border rounded p-2">
                          <div className="col-span-6">
                            <span className="text-gray-500">Description</span>
                            <div>{li.description || ''}</div>
                          </div>
                          <div className="col-span-2">
                            <span className="text-gray-500">Qty</span>
                            <div>{li.quantity != null ? String(li.quantity) : ''}</div>
                          </div>
                          <div className="col-span-2">
                            <span className="text-gray-500">Unit</span>
                            <div>{li.unit_price != null ? String(li.unit_price) : ''}</div>
                          </div>
                          <div className="col-span-2">
                            <span className="text-gray-500">Total</span>
                            <div>{li.total != null ? String(li.total) : ''}</div>
                          </div>
                        </div>
                      ))}
                      {(data.line_items || []).length === 0 && (
                        <div className="text-sm text-gray-500">No line items extracted.</div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}


