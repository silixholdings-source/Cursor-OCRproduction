'use client'

import React, { useState, useCallback, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Upload, 
  FileText, 
  Image, 
  File, 
  CheckCircle, 
  AlertCircle,
  X,
  Loader2,
  Brain,
  Zap,
  Camera,
  Scan,
  Eye,
  Download,
  RefreshCw,
  Target,
  Shield,
  XCircle,
  AlertTriangle
} from 'lucide-react'
import { notifications } from '@/lib/notifications'
import { apiClient } from '@/lib/api-client'
import { validateFileUpload } from '@/lib/security'

interface SmartUploadedFile {
  id: string
  file: File
  preview: string
  status: 'uploading' | 'ocr_processing' | 'ai_analysis' | 'validation' | 'completed' | 'error'
  progress: number
  extractedData?: any
  confidenceScores?: Record<string, number>
  processingSteps: Array<{
    step: string
    status: 'pending' | 'processing' | 'completed' | 'error'
    duration?: number
    details?: string
  }>
  error?: string
  warnings?: string[]
  suggestions?: string[]
}

interface SmartInvoiceUploadProps {
  onFilesProcessed: (files: SmartUploadedFile[]) => void
  maxFiles?: number
  enableBatchProcessing?: boolean
  enableRealTimeValidation?: boolean
  enable3WayMatch?: boolean
  acceptedTypes?: string[]
}

export function SmartInvoiceUpload({ 
  onFilesProcessed, 
  maxFiles = 20,
  enableBatchProcessing = true,
  enableRealTimeValidation = true,
  enable3WayMatch = true,
  acceptedTypes = ['image/*', 'application/pdf', '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.heic']
}: SmartInvoiceUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<SmartUploadedFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [batchProgress, setBatchProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const processFileWithAdvancedOCR = useCallback(async (file: SmartUploadedFile) => {
    const updateFileStatus = (status: SmartUploadedFile['status'], progress: number, stepUpdate?: any) => {
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === file.id 
            ? { 
                ...f, 
                status, 
                progress,
                processingSteps: stepUpdate ? [...f.processingSteps, stepUpdate] : f.processingSteps
              }
            : f
        )
      )
    }

    try {
      // Step 1: File Upload
      updateFileStatus('uploading', 10, {
        step: 'File Upload',
        status: 'processing' as const,
        details: 'Uploading file to secure processing server'
      })

      // Simulate upload
      for (let progress = 10; progress <= 30; progress += 5) {
        await new Promise(resolve => setTimeout(resolve, 100))
        updateFileStatus('uploading', progress)
      }

      // Step 2: OCR Processing
      updateFileStatus('ocr_processing', 40, {
        step: 'OCR Processing',
        status: 'processing' as const,
        details: 'Extracting text and data with AI-powered OCR'
      })

      // Call actual OCR API
      const formData = new FormData()
      formData.append('file', file.file)
      
      const ocrResponse = await apiClient.post('/api/v1/ocr/process', formData)
      
      updateFileStatus('ocr_processing', 60)

      // Step 3: AI Analysis
      updateFileStatus('ai_analysis', 70, {
        step: 'AI Analysis',
        status: 'processing' as const,
        details: 'Analyzing data with machine learning models'
      })

      // AI enhancement
      const aiResponse = await apiClient.post('/api/v1/ai/enhance', {
        extracted_data: ocrResponse.data,
        file_metadata: {
          name: file.file.name,
          size: file.file.size,
          type: file.file.type
        }
      })

      updateFileStatus('ai_analysis', 85)

      // Step 4: Validation
      updateFileStatus('validation', 90, {
        step: 'Validation',
        status: 'processing' as const,
        details: 'Validating extracted data and checking for duplicates'
      })

      // Validation
      const validationResponse = await apiClient.post('/api/v1/invoices/validate', aiResponse.data)

      // Step 5: Complete
      updateFileStatus('completed', 100, {
        step: 'Processing Complete',
        status: 'completed' as const,
        duration: Date.now() - parseInt(file.id), // Rough duration
        details: 'Invoice processed successfully'
      })

      // Update with final data
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === file.id 
            ? { 
                ...f, 
                extractedData: aiResponse.data,
                confidenceScores: aiResponse.confidence_scores,
                warnings: validationResponse.warnings,
                suggestions: validationResponse.suggestions
              }
            : f
        )
      )

      // Success notification
        notifications.success(
          `Invoice ${aiResponse.data.invoice_number} processed with ${(aiResponse.overall_confidence * 100).toFixed(1)}% confidence`,
          'OCR Complete',
          {
            label: 'View Results',
            onClick: () => {
              // Scroll to the completed file in the queue
              const fileElement = document.querySelector(`[data-file-id="${file.id}"]`)
              if (fileElement) {
                fileElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
              }
            }
          }
        )

    } catch (error) {
      updateFileStatus('error', 0, {
        step: 'Processing Failed',
        status: 'error' as const,
        details: error instanceof Error ? error.message : 'Unknown error occurred'
      })

      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === file.id 
            ? { ...f, error: error instanceof Error ? error.message : 'Processing failed' }
            : f
        )
      )

      notifications.error(
        `Failed to process ${file.file.name}`,
        'OCR Error'
      )
    }
  }, [])

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      const errorMessages = errors.map((e: any) => e.message).join(', ')
      notifications.error(`${file.name}: ${errorMessages}`, 'File Rejected')
    })

    // Validate accepted files
    const validFiles = acceptedFiles.filter(file => {
      const validation = validateFileUpload(file)
      if (!validation.isValid) {
        notifications.error(`${file.name}: ${validation.errors.join(', ')}`, 'File Validation Failed')
        return false
      }
      return true
    })

    if (validFiles.length === 0) return

    const newFiles: SmartUploadedFile[] = validFiles.map(file => ({
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      file,
      preview: URL.createObjectURL(file),
      status: 'uploading',
      progress: 0,
      processingSteps: [
        {
          step: 'File Validation',
          status: 'completed',
          details: 'File passed security and format validation'
        }
      ]
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])
    
    // Process files
    if (enableBatchProcessing && newFiles.length > 1) {
      processBatch(newFiles)
    } else {
      newFiles.forEach(file => {
        processFileWithAdvancedOCR(file)
      })
    }
  }, [enableBatchProcessing, processFileWithAdvancedOCR, processBatch])

  const processBatch = useCallback(async (files: SmartUploadedFile[]) => {
    setIsProcessing(true)
    setBatchProgress(0)

    try {
      // Process files in parallel batches of 3
      const batchSize = 3
      for (let i = 0; i < files.length; i += batchSize) {
        const batch = files.slice(i, i + batchSize)
        
        await Promise.all(
          batch.map(file => processFileWithAdvancedOCR(file))
        )
        
        setBatchProgress(Math.min(100, ((i + batchSize) / files.length) * 100))
      }

      notifications.success(
        `Batch processing completed: ${files.length} invoices processed`,
        'Batch OCR Complete'
      )
    } catch (error) {
      notifications.error('Batch processing failed', 'Batch Error')
    } finally {
      setIsProcessing(false)
      setBatchProgress(0)
    }
  }, [processFileWithAdvancedOCR])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.heic'],
      'application/pdf': ['.pdf']
    },
    maxFiles,
    maxSize: 25 * 1024 * 1024, // 25MB for high-res scans
    multiple: true
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

  const retryProcessing = (fileId: string) => {
    const file = uploadedFiles.find(f => f.id === fileId)
    if (file) {
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === fileId 
            ? { ...f, status: 'uploading', progress: 0, error: undefined, processingSteps: [] }
            : f
        )
      )
      processFileWithAdvancedOCR(file)
    }
  }

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return Image
    if (file.type === 'application/pdf') return FileText
    return File
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'uploading': return 'bg-blue-100 text-blue-800'
      case 'ocr_processing': return 'bg-purple-100 text-purple-800'
      case 'ai_analysis': return 'bg-indigo-100 text-indigo-800'
      case 'validation': return 'bg-yellow-100 text-yellow-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'uploading': return 'Uploading'
      case 'ocr_processing': return 'OCR Processing'
      case 'ai_analysis': return 'AI Analysis'
      case 'validation': return 'Validating'
      case 'completed': return 'Completed'
      case 'error': return 'Error'
      default: return status
    }
  }

  const completedFiles = uploadedFiles.filter(f => f.status === 'completed')

  return (
    <div className="space-y-6">
      {/* Smart Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Brain className="h-5 w-5 mr-2 text-blue-600" />
            AI-Powered Invoice Upload
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
              ${isDragActive 
                ? 'border-blue-400 bg-blue-50 scale-105' 
                : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
              }
            `}
          >
            <input {...getInputProps()} ref={fileInputRef} />
            <div className="space-y-4">
              {isDragActive ? (
                <>
                  <Upload className="mx-auto h-16 w-16 text-blue-500 animate-bounce" />
                  <h3 className="text-xl font-medium text-blue-600">Drop files here!</h3>
                </>
              ) : (
                <>
                  <div className="flex justify-center space-x-4">
                    <Upload className="h-12 w-12 text-gray-400" />
                    <Brain className="h-12 w-12 text-blue-500" />
                    <Zap className="h-12 w-12 text-yellow-500" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900">
                    Smart Invoice Processing
                  </h3>
                  <p className="text-gray-600">
                    Drag & drop invoices or click to select files
                  </p>
                </>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                <div className="flex items-center justify-center">
                  <Scan className="h-4 w-4 mr-2" />
                  99.9% OCR Accuracy
                </div>
                <div className="flex items-center justify-center">
                  <Target className="h-4 w-4 mr-2" />
                  3-Way Matching
                </div>
                <div className="flex items-center justify-center">
                  <Shield className="h-4 w-4 mr-2" />
                  Enterprise Security
                </div>
              </div>
              
              <div className="space-y-2">
                <p className="text-sm text-gray-500">
                  Supports: PDF, JPG, PNG, TIFF, HEIC (max 25MB each)
                </p>
                <p className="text-xs text-gray-400">
                  Advanced AI processes handwritten text, tables, and multi-language documents
                </p>
              </div>
              
              <div className="flex justify-center space-x-2">
                <Button disabled={isProcessing}>
                  {isProcessing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing Batch...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Select Files
                    </>
                  )}
                </Button>
                <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                  <Camera className="mr-2 h-4 w-4" />
                  Camera
                </Button>
              </div>
            </div>
          </div>

          {/* Batch Progress */}
          {isProcessing && enableBatchProcessing && (
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span>Batch Processing Progress</span>
                <span>{batchProgress.toFixed(0)}%</span>
              </div>
              <Progress value={batchProgress} className="h-3" />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Processing Queue */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Processing Queue ({uploadedFiles.length})
              </CardTitle>
              <div className="flex space-x-2">
                <Badge variant="outline">
                  {completedFiles.length} / {uploadedFiles.length} Complete
                </Badge>
                {completedFiles.length > 0 && (
                  <Button variant="outline" size="sm" onClick={() => onFilesProcessed(completedFiles)}>
                    <Eye className="h-4 w-4 mr-2" />
                    Review Results
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {uploadedFiles.map((file) => {
                const FileIcon = getFileIcon(file.file)
                const currentStep = file.processingSteps[file.processingSteps.length - 1]
                
                return (
                  <div key={file.id} data-file-id={file.id} className="border rounded-lg p-4 space-y-3">
                    {/* File Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <FileIcon className="h-8 w-8 text-gray-400" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                            {file.file.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(file.file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(file.status)}>
                          {getStatusText(file.status)}
                        </Badge>
                        {file.status === 'error' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => retryProcessing(file.id)}
                          >
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                        )}
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

                    {/* Progress Bar */}
                    {file.status !== 'completed' && file.status !== 'error' && (
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span>{currentStep?.details || 'Processing...'}</span>
                          <span>{file.progress}%</span>
                        </div>
                        <Progress value={file.progress} className="h-2" />
                      </div>
                    )}

                    {/* Processing Steps */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {['File Upload', 'OCR Processing', 'AI Analysis', 'Validation'].map((stepName, index) => {
                        const step = file.processingSteps.find(s => s.step === stepName)
                        return (
                          <div key={stepName} className="flex items-center space-x-1 text-xs">
                            {step?.status === 'completed' ? (
                              <CheckCircle className="h-3 w-3 text-green-600" />
                            ) : step?.status === 'processing' ? (
                              <Loader2 className="h-3 w-3 text-blue-600 animate-spin" />
                            ) : step?.status === 'error' ? (
                              <XCircle className="h-3 w-3 text-red-600" />
                            ) : (
                              <div className="h-3 w-3 rounded-full border-2 border-gray-300" />
                            )}
                            <span className={
                              step?.status === 'completed' ? 'text-green-600' :
                              step?.status === 'processing' ? 'text-blue-600' :
                              step?.status === 'error' ? 'text-red-600' :
                              'text-gray-400'
                            }>
                              {stepName}
                            </span>
                          </div>
                        )
                      })}
                    </div>

                    {/* Results Preview */}
                    {file.status === 'completed' && file.extractedData && (
                      <div className="bg-green-50 rounded-lg p-3 space-y-2">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600">Vendor:</p>
                            <p className="font-medium">{file.extractedData.vendor}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Amount:</p>
                            <p className="font-medium">${file.extractedData.amount?.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Invoice #:</p>
                            <p className="font-medium">{file.extractedData.invoice_number}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Confidence:</p>
                            <Badge size="sm" className={getConfidenceColor(file.extractedData.overall_confidence || 0)}>
                              {((file.extractedData.overall_confidence || 0) * 100).toFixed(1)}%
                            </Badge>
                          </div>
                        </div>

                        {file.warnings && file.warnings.length > 0 && (
                          <Alert>
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>
                              <p className="text-sm">{file.warnings.length} validation warnings detected</p>
                            </AlertDescription>
                          </Alert>
                        )}
                      </div>
                    )}

                    {/* Error Display */}
                    {file.status === 'error' && file.error && (
                      <Alert variant="destructive">
                        <XCircle className="h-4 w-4" />
                        <AlertDescription>
                          <p className="text-sm">{file.error}</p>
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Processing Summary */}
      {completedFiles.length > 0 && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center text-green-800">
              <CheckCircle className="h-5 w-5 mr-2" />
              Processing Complete
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <p className="text-green-600 font-medium">Files Processed</p>
                <p className="text-2xl font-bold text-green-800">{completedFiles.length}</p>
              </div>
              <div className="text-center">
                <p className="text-green-600 font-medium">Average Confidence</p>
                <p className="text-2xl font-bold text-green-800">
                  {completedFiles.length > 0 
                    ? (completedFiles.reduce((acc, f) => acc + (f.extractedData?.overall_confidence || 0), 0) / completedFiles.length * 100).toFixed(1)
                    : 0}%
                </p>
              </div>
              <div className="text-center">
                <p className="text-green-600 font-medium">Total Value</p>
                <p className="text-2xl font-bold text-green-800">
                  ${completedFiles.reduce((acc, f) => acc + (f.extractedData?.amount || 0), 0).toLocaleString()}
                </p>
              </div>
            </div>
            
            <div className="mt-4 flex justify-center">
              <Button onClick={() => onFilesProcessed(completedFiles)}>
                <Eye className="h-4 w-4 mr-2" />
                Review {completedFiles.length} Invoice{completedFiles.length !== 1 ? 's' : ''}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )

  function getConfidenceColor(confidence: number): string {
    if (confidence >= 0.95) return 'bg-green-100 text-green-800 border-green-200'
    if (confidence >= 0.85) return 'bg-blue-100 text-blue-800 border-blue-200'
    if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-red-100 text-red-800 border-red-200'
  }
}
