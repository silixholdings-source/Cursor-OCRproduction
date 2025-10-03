import { SimpleOCRUpload } from '@/components/ocr/simple-ocr-upload'

export default function OCRTestPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            OCR Functionality Test
          </h1>
          <p className="text-lg text-gray-600">
            Upload an invoice file to test the OCR processing
          </p>
        </div>
        
        <SimpleOCRUpload />
      </div>
    </div>
  )
}


















