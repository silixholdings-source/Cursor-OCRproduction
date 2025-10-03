'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { 
  Upload, 
  FileText, 
  Image, 
  File, 
  CheckCircle, 
  AlertCircle,
  X,
  Loader2
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { getApiBaseUrl } from '@/lib/api'

interface UploadedFile {
  id: string
  file: File
  preview: string
  status: 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  extractedData?: any
  error?: string
}

interface InvoiceUploadProps {
  onFilesProcessed: (files: UploadedFile[]) => void
  maxFiles?: number
  acceptedTypes?: string[]
}

export function InvoiceUpload({ 
  onFilesProcessed, 
  maxFiles = 10,
  acceptedTypes = ['image/*', 'application/pdf', '.pdf', '.jpg', '.jpeg', '.png', '.tiff']
}: InvoiceUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)

  const processWithProductionOCR = useCallback(async (file: UploadedFile) => {
    try {
      console.log('Processing file:', file.file.name, 'Size:', file.file.size, 'Type:', file.file.type)
      
      // Update status to uploading
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === file.id 
            ? { ...f, status: 'uploading', progress: 30 }
            : f
        )
      )

      // Create form data for OCR API
      const formData = new FormData()
      formData.append('file', file.file)
      console.log('FormData created, file added')

      // Update to processing
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === file.id 
            ? { ...f, status: 'processing', progress: 60 }
            : f
        )
      )

      // Call OCR API
      const apiUrl = `${getApiBaseUrl()}/api/v1/ocr/upload`
      console.log('Making request to:', apiUrl)
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      })
      
      console.log('Response received, status:', response.status)

      const result = await response.json()
      console.log('OCR Response:', result)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (result.success && result.data && result.data.extracted_data) {
        // Success - update with extracted data
        const extractedData = result.data.extracted_data
        console.log('Processing extracted data:', extractedData)
        
        setUploadedFiles(prev => {
          const updatedFiles = prev.map(f => 
            f.id === file.id 
              ? { 
                  ...f, 
                  status: 'completed', 
                  progress: 100,
                  extractedData: {
                    vendor: extractedData.vendor,
                    invoiceNumber: extractedData.invoice_number,
                    amount: extractedData.amount,
                    currency: extractedData.currency,
                    date: extractedData.invoice_date,
                    dueDate: extractedData.due_date,
                    lineItems: extractedData.line_items ? extractedData.line_items.map((item: any) => ({
                      description: item.description,
                      quantity: item.quantity,
                      unitPrice: item.unit_price,
                      total: item.total
                    })) : [],
                    confidence: result.data.confidence_score,
                    taxAmount: extractedData.tax_amount,
                    subtotal: extractedData.subtotal,
                    totalAmount: extractedData.total_amount
                  }
                }
              : f
          )
          
          // Notify parent component
          const completedFiles = updatedFiles.filter(f => f.status === 'completed')
          onFilesProcessed(completedFiles)
          
          return updatedFiles
        })
      } else {
        // Error - update with error status
        console.error('OCR processing failed:', result)
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === file.id 
              ? { 
                  ...f, 
                  status: 'error', 
                  progress: 0,
                  error: result.message || result.error || 'OCR processing failed'
                }
              : f
          )
        )
      }
    } catch (error) {
      // Network or other error
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === file.id 
            ? { 
                ...f, 
                status: 'error', 
                progress: 0,
                error: `Processing failed: ${error}`
              }
            : f
        )
      )
    }
  }, [onFilesProcessed])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      preview: URL.createObjectURL(file),
      status: 'uploading',
      progress: 0
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])
    
    // Process with production OCR
    newFiles.forEach(file => {
      processWithProductionOCR(file)
    })
  }, [processWithProductionOCR])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff'],
      'application/pdf': ['.pdf']
    },
    maxFiles,
    maxSize: 10 * 1024 * 1024, // 10MB
  })


  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => {
      const file = prev.find(f => f.id === fileId)
      if (file?.preview) {
        URL.revokeObjectURL(file.preview)
      }
      return prev.filter(f => f.id !== fileId)
    })
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return Image
    if (file.type === 'application/pdf') return FileText
    return File
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'uploading': return 'bg-blue-100 text-blue-800'
      case 'processing': return 'bg-yellow-100 text-yellow-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'uploading': return 'Uploading'
      case 'processing': return 'Processing'
      case 'completed': return 'Completed'
      case 'error': return 'Error'
      default: return status
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card>
        <CardContent className="p-6">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive 
                ? 'border-blue-400 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
              }
            `}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop files here' : 'Upload Invoices'}
            </h3>
            <p className="text-gray-600 mb-4">
              Drag & drop files here, or click to select files
            </p>
            <p className="text-sm text-gray-500">
              Supports PDF, JPG, PNG, TIFF (max 10MB each)
            </p>
            <Button className="mt-4" disabled={isProcessing}>
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                'Select Files'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Uploaded Files ({uploadedFiles.length})
            </h3>
            <div className="space-y-4">
              {uploadedFiles.map((file) => {
                const FileIcon = getFileIcon(file.file)
                return (
                  <div key={file.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                    <FileIcon className="h-8 w-8 text-gray-400" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.file.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {(file.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      {file.status === 'uploading' && (
                        <div className="mt-2">
                          <Progress value={file.progress} className="h-2" />
                        </div>
                      )}
                      {file.status === 'processing' && (
                        <div className="flex items-center mt-2">
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                          <span className="text-sm text-gray-600">Processing with AI...</span>
                        </div>
                      )}
                      {file.status === 'completed' && file.extractedData && (
                        <div className="mt-2 space-y-1">
                          <p className="text-sm text-gray-600">
                            Vendor: {file.extractedData.vendor}
                          </p>
                          <p className="text-sm text-gray-600">
                            Amount: ${file.extractedData.amount.toFixed(2)}
                          </p>
                          <p className="text-sm text-gray-600">
                            Confidence: {((file.extractedData.confidence || 0) * 100).toFixed(1)}%
                          </p>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(file.status)}>
                        {getStatusText(file.status)}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(file.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}





