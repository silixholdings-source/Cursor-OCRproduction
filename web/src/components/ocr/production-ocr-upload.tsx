'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { 
  Upload, 
  FileText, 
  Loader2, 
  CheckCircle, 
  AlertCircle, 
  X,
  Eye,
  Download,
  RefreshCw
} from 'lucide-react'
import { toast } from '@/hooks/use-toast'

interface OCRResult {
  success: boolean
  data?: {
    vendor: string
    invoice_number: string
    amount: number
    currency: string
    invoice_date: string
    due_date: string
    vendor_address: string
    vendor_phone: string
    vendor_email: string
    tax_amount: number
    subtotal: number
    payment_terms: string
    line_items: Array<{
      description: string
      quantity: number
      unit_price: number
      total: number
    }>
    confidence_scores: {
      vendor: number
      invoice_number: number
      amount: number
      date: number
      line_items: number
      vendor_address: number
      tax_amount: number
    }
    overall_confidence: number
    processing_metadata: {
      processing_time_ms: number
      file_size_bytes: number
      file_type: string
      file_name: string
    }
    quality_metrics: {
      text_clarity: number
      image_quality: number
      completeness_score: number
      validation_passed: boolean
    }
  }
  error?: string
  code?: string
}

interface ProductionOCRUploadProps {
  onOCRComplete?: (result: OCRResult) => void
  onError?: (error: string) => void
  className?: string
}

export function ProductionOCRUpload({ onOCRComplete, onError, className }: ProductionOCRUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState<OCRResult[]>([])
  const [progress, setProgress] = useState(0)
  const [currentFile, setCurrentFile] = useState<string>('')

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles])
    setResults([])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  })

  const processFiles = async () => {
    if (files.length === 0) return

    setIsProcessing(true)
    setProgress(0)
    setResults([])

    try {
      const processedResults: OCRResult[] = []

      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        setCurrentFile(file.name)
        setProgress((i / files.length) * 100)

        try {
          const formData = new FormData()
          formData.append('file', file)

          const response = await fetch('/api/ocr/process', {
            method: 'POST',
            body: formData,
          })

          const result: OCRResult = await response.json()

          if (result.success) {
            processedResults.push(result)
            toast({
              title: "OCR Success",
              description: `Successfully processed ${file.name}`,
            })
          } else {
            processedResults.push(result)
            toast({
              title: "OCR Error",
              description: result.error || 'Processing failed',
              variant: "destructive"
            })
            onError?.(result.error || 'Processing failed')
          }
        } catch (error) {
          const errorResult: OCRResult = {
            success: false,
            error: `Failed to process ${file.name}: ${error}`,
            code: 'NETWORK_ERROR'
          }
          processedResults.push(errorResult)
          toast({
            title: "Network Error",
            description: `Failed to process ${file.name}`,
            variant: "destructive"
          })
        }
      }

      setResults(processedResults)
      setProgress(100)
      
      // Notify parent component
      processedResults.forEach(result => {
        onOCRComplete?.(result)
      })

    } catch (error) {
      toast({
        title: "Processing Error",
        description: "Failed to process files",
        variant: "destructive"
      })
      onError?.('Failed to process files')
    } finally {
      setIsProcessing(false)
      setCurrentFile('')
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const clearAll = () => {
    setFiles([])
    setResults([])
    setProgress(0)
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600'
    if (confidence >= 0.8) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.9) return 'bg-green-100 text-green-800'
    if (confidence >= 0.8) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Production OCR Processing
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <div className="space-y-2">
              <p className="text-lg font-medium">
                {isDragActive ? 'Drop files here' : 'Upload Invoice Files'}
              </p>
              <p className="text-sm text-gray-600">
                Drag & drop files or click to browse
              </p>
              <p className="text-xs text-gray-500">
                Supports PDF, JPG, PNG, TIFF • Max 10MB per file
              </p>
            </div>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="mt-6 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Files to Process ({files.length})</h4>
                <Button variant="outline" size="sm" onClick={clearAll}>
                  Clear All
                </Button>
              </div>
              
              {files.map((file, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-gray-500" />
                    <div>
                      <p className="text-sm font-medium">{file.name}</p>
                      <p className="text-xs text-gray-500">
                        {(file.size / 1024).toFixed(1)} KB • {file.type}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                    disabled={isProcessing}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}

              <div className="flex gap-2 pt-4">
                <Button
                  onClick={processFiles}
                  disabled={isProcessing || files.length === 0}
                  className="flex-1"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <FileText className="h-4 w-4 mr-2" />
                      Process {files.length} File{files.length !== 1 ? 's' : ''}
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Processing Progress */}
          {isProcessing && (
            <div className="mt-6 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Processing: {currentFile}</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="w-full" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Processing Results</h3>
          
          {results.map((result, index) => (
            <Card key={index}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base flex items-center gap-2">
                    {result.success ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-red-500" />
                    )}
                    {result.success ? 'Processing Successful' : 'Processing Failed'}
                  </CardTitle>
                  
                  {result.success && result.data && (
                    <Badge className={getConfidenceBadge(result.data.overall_confidence)}>
                      {(result.data.overall_confidence * 100).toFixed(1)}% Confidence
                    </Badge>
                  )}
                </div>
              </CardHeader>
              
              <CardContent>
                {result.success && result.data ? (
                  <div className="space-y-4">
                    {/* Key Information */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Vendor</label>
                        <p className="font-semibold">{result.data.vendor}</p>
                        <p className="text-xs text-gray-600">{result.data.vendor_address}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Invoice Number</label>
                        <p className="font-semibold">{result.data.invoice_number}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Total Amount</label>
                        <p className="font-semibold text-lg">
                          {result.data.currency} {result.data.amount.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Invoice Date</label>
                        <p className="font-semibold">{result.data.invoice_date}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Due Date</label>
                        <p className="font-semibold">{result.data.due_date}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Payment Terms</label>
                        <p className="font-semibold">{result.data.payment_terms}</p>
                      </div>
                    </div>

                    {/* Line Items */}
                    {result.data.line_items.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Line Items</h4>
                        <div className="border rounded-lg overflow-hidden">
                          <table className="w-full text-sm">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="text-left p-3">Description</th>
                                <th className="text-right p-3">Qty</th>
                                <th className="text-right p-3">Unit Price</th>
                                <th className="text-right p-3">Total</th>
                              </tr>
                            </thead>
                            <tbody>
                              {result.data.line_items.map((item, itemIndex) => (
                                <tr key={itemIndex} className="border-t">
                                  <td className="p-3">{item.description}</td>
                                  <td className="text-right p-3">{item.quantity}</td>
                                  <td className="text-right p-3">${item.unit_price.toFixed(2)}</td>
                                  <td className="text-right p-3 font-medium">${item.total.toFixed(2)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}

                    {/* Processing Metadata */}
                    <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded">
                      <p>Processed in {result.data.processing_metadata.processing_time_ms}ms</p>
                      <p>File: {result.data.processing_metadata.file_name} ({(result.data.processing_metadata.file_size_bytes / 1024).toFixed(1)} KB)</p>
                      <p>Quality Score: {(result.data.quality_metrics.completeness_score * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-red-600">
                    <p className="font-medium">Error: {result.error}</p>
                    {result.code && <p className="text-sm">Code: {result.code}</p>}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
















