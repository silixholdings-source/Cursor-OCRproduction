'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function TestOCRPage() {
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setResult(null)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      console.log('Uploading file:', file.name, 'to:', 'http://127.0.0.1:8001/api/v1/ocr/upload')

      const response = await fetch('http://127.0.0.1:8001/api/v1/ocr/upload', {
        method: 'POST',
        body: formData,
      })

      console.log('Response status:', response.status)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Response data:', data)
      setResult(data)
    } catch (err) {
      console.error('Upload error:', err)
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-8">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>OCR Test Page</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label htmlFor="file" className="block text-sm font-medium mb-2">
              Select a file to upload:
            </label>
            <input
              id="file"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.tiff"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          {file && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <p><strong>Selected file:</strong> {file.name}</p>
              <p><strong>File size:</strong> {file.size} bytes</p>
              <p><strong>File type:</strong> {file.type}</p>
            </div>
          )}

          <Button 
            onClick={handleUpload} 
            disabled={!file || loading}
            className="w-full"
          >
            {loading ? 'Processing...' : 'Upload and Process'}
          </Button>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800"><strong>Error:</strong> {error}</p>
            </div>
          )}

          {result && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="font-semibold text-green-800 mb-2">OCR Result:</h3>
              <pre className="text-sm text-green-700 whitespace-pre-wrap">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}









