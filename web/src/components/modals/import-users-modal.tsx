'use client'

import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Upload, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { useDropzone } from 'react-dropzone'

interface ImportUsersModalProps {
  isOpen: boolean
  onClose: () => void
  onUsersImported: (users: any[]) => void
}

export function ImportUsersModal({ isOpen, onClose, onUsersImported }: ImportUsersModalProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [importResults, setImportResults] = useState<{
    success: number
    errors: string[]
  } | null>(null)

  const parseCSV = (csvText: string) => {
    const lines = csvText.split('\n').filter(line => line.trim())
    if (lines.length < 2) {
      throw new Error('CSV file must have at least a header row and one data row')
    }

    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
    const requiredHeaders = ['Name', 'Email', 'Role', 'Status']
    
    for (const required of requiredHeaders) {
      if (!headers.includes(required)) {
        throw new Error(`Missing required column: ${required}`)
      }
    }

    const users = []
    const errors = []

    for (let i = 1; i < lines.length; i++) {
      try {
        const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''))
        if (values.length !== headers.length) {
          errors.push(`Row ${i + 1}: Column count mismatch`)
          continue
        }

        const user: any = {}
        headers.forEach((header, index) => {
          user[header.toLowerCase().replace(/\s+/g, '')] = values[index]
        })

        // Validate required fields
        if (!user.name || !user.email) {
          errors.push(`Row ${i + 1}: Missing required fields`)
          continue
        }

        // Validate email format
        if (!/\S+@\S+\.\S+/.test(user.email)) {
          errors.push(`Row ${i + 1}: Invalid email format`)
          continue
        }

        // Create user object
        const newUser = {
          id: Date.now().toString() + i,
          name: user.name,
          email: user.email,
          role: user.role || 'user',
          status: user.status || 'active',
          lastLogin: null,
          avatar: null,
          permissions: ['read'],
          createdAt: new Date().toISOString()
        }

        users.push(newUser)
      } catch (error) {
        errors.push(`Row ${i + 1}: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    }

    return { users, errors }
  }

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    if (!file.name.toLowerCase().endsWith('.csv')) {
      console.log('Please select a CSV file')
      return
    }

    setIsProcessing(true)
    setImportResults(null)

    try {
      const text = await file.text()
      const { users, errors } = parseCSV(text)

      setImportResults({
        success: users.length,
        errors
      })

      if (users.length > 0) {
        onUsersImported(users)
      }
    } catch (error) {
      setImportResults({
        success: 0,
        errors: [error instanceof Error ? error.message : 'Failed to parse CSV file']
      })
    } finally {
      setIsProcessing(false)
    }
  }, [onUsersImported])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: false
  })

  const handleClose = () => {
    setImportResults(null)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Import Users from CSV
          </DialogTitle>
          <DialogDescription>
            Upload a CSV file to import multiple users at once. The file should include columns for Name, Email, Role, and Status.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {!importResults ? (
            <Card>
              <CardContent className="p-6">
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                    isDragActive
                      ? 'border-blue-400 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <input {...getInputProps()} />
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  {isDragActive ? (
                    <p className="text-lg font-medium text-blue-600">
                      Drop the CSV file here...
                    </p>
                  ) : (
                    <div>
                      <p className="text-lg font-medium text-gray-900 mb-2">
                        Drag & drop a CSV file here
                      </p>
                      <p className="text-sm text-gray-500">
                        or click to select a file
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Import Results
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                  <span className="font-medium">
                    Successfully imported {importResults.success} users
                  </span>
                </div>

                {importResults.errors.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 text-red-600 mb-2">
                      <XCircle className="h-5 w-5" />
                      <span className="font-medium">
                        {importResults.errors.length} errors found:
                      </span>
                    </div>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 max-h-32 overflow-y-auto">
                      {importResults.errors.map((error, index) => (
                        <p key={index} className="text-sm text-red-600">
                          {error}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {isProcessing && (
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="text-gray-600">Processing CSV file...</span>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={handleClose}>
            {importResults ? 'Close' : 'Cancel'}
          </Button>
          {importResults && (
            <Button onClick={handleClose} className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Done
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
