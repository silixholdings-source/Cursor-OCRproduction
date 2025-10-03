import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }

    // Validate file type
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff']
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'Unsupported file type. Please upload PDF, JPG, PNG, or TIFF files.' },
        { status: 400 }
      )
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: 'File too large. Maximum size is 10MB.' },
        { status: 400 }
      )
    }

    // Simulate OCR processing with realistic data
    const fileName = file.name.toLowerCase()
    const isInvoice = fileName.includes('invoice') || fileName.includes('bill')
    
    // Generate realistic mock data based on file name
    const mockVendors = [
      'Acme Corporation', 'Tech Solutions Inc', 'Global Services Ltd', 
      'Office Supplies Co', 'Professional Services LLC', 'Digital Marketing Group',
      'Software Licensing Corp', 'Consulting Partners', 'Equipment Rentals Inc'
    ]
    
    const mockCategories = [
      'Office Supplies', 'Software License', 'Consulting Services', 
      'Equipment Purchase', 'Marketing Services', 'Professional Services',
      'Utilities', 'Travel & Entertainment', 'Training & Development'
    ]
    
    const vendor = mockVendors[Math.floor(Math.random() * mockVendors.length)]
    const category = mockCategories[Math.floor(Math.random() * mockCategories.length)]
    const amount = Math.round((Math.random() * 5000 + 100) * 100) / 100
    const invoiceNum = `INV-${Math.random().toString(36).substr(2, 6).toUpperCase()}`
    const confidence = Math.round((Math.random() * 0.15 + 0.85) * 100) / 100 // 85-100% confidence
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const extractedData = {
      vendor: vendor,
      invoice_number: invoiceNum,
      invoice_date: new Date().toISOString().split('T')[0],
      due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      amount: amount,
      currency: 'USD',
      tax_amount: Math.round(amount * 0.08 * 100) / 100,
      subtotal: Math.round(amount * 0.92 * 100) / 100,
      total_with_tax: amount,
      category: category,
      description: `${category} from ${vendor}`,
      line_items: [
        {
          description: category,
          quantity: Math.floor(Math.random() * 5) + 1,
          unit_price: Math.round((amount / (Math.floor(Math.random() * 3) + 1)) * 100) / 100,
          total: amount,
          gl_account: '6000'
        }
      ],
      confidence_scores: {
        vendor: confidence,
        invoice_number: confidence + 0.05,
        amount: confidence + 0.02,
        date: confidence - 0.03,
        line_items: confidence - 0.05
      },
      overall_confidence: confidence,
      processing_metadata: {
        provider: 'ai-erp-ocr',
        processing_time_ms: 2000,
        file_size_bytes: file.size,
        extraction_method: 'advanced_ai_ocr',
        language_detected: 'en',
        page_count: 1
      }
    }

    return NextResponse.json(extractedData)
    
  } catch (error) {
    console.error('OCR processing error:', error)
    return NextResponse.json(
      { error: 'OCR processing failed. Please try again.' },
      { status: 500 }
    )
  }
}




