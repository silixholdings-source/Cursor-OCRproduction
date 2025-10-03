export default function DemoPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4 text-gray-900">OCR Demo</h1>
            <p className="text-xl text-gray-600 mb-6">
              Upload an invoice image or PDF to see our AI extract data automatically
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upload Section */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Upload Invoice</h2>
              <p className="text-gray-600 mb-4">Select a PDF or image file to process</p>
              
              <div className="space-y-4">
                <div>
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg,.tiff"
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>
                
                <div className="flex gap-2">
                  <button className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                    Process File
                  </button>
                  <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors">
                    Reset
                  </button>
                </div>
              </div>
            </div>

            {/* Results Section */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">Extracted Data</h2>
              <p className="text-gray-600 mb-4">AI-processed invoice information</p>
              
              <div className="text-center py-8 text-gray-500">
                <div className="w-12 h-12 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center">
                  📄
                </div>
                <p>Upload a file to see extracted data here</p>
              </div>
            </div>
          </div>

          {/* Instructions */}
          <div className="mt-8 bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">How to Test</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-blue-600 font-bold">1</span>
                </div>
                <h4 className="font-medium mb-1 text-gray-900">Upload File</h4>
                <p className="text-sm text-gray-600">Select a PDF or image file</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-blue-600 font-bold">2</span>
                </div>
                <h4 className="font-medium mb-1 text-gray-900">AI Processing</h4>
                <p className="text-sm text-gray-600">Our AI extracts data automatically</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-blue-600 font-bold">3</span>
                </div>
                <h4 className="font-medium mb-1 text-gray-900">View Results</h4>
                <p className="text-sm text-gray-600">See extracted invoice data</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}