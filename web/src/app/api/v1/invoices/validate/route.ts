import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const invoiceData = body
    
    if (!invoiceData) {
      return NextResponse.json(
        { error: 'No invoice data provided' },
        { status: 400 }
      )
    }

    // Simulate validation processing
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const warnings = []
    const suggestions = []
    
    // Check for common validation issues
    if (invoiceData.amount > 10000) {
      warnings.push('High-value invoice requires additional approval')
    }
    
    if (invoiceData.confidence_scores?.overall_confidence < 0.9) {
      warnings.push('Low confidence score - manual review recommended')
    }
    
    if (!invoiceData.line_items || invoiceData.line_items.length === 0) {
      warnings.push('No line items detected - verify invoice completeness')
    }
    
    if (invoiceData.vendor && invoiceData.vendor.includes('Test')) {
      warnings.push('Test vendor detected - verify this is a legitimate invoice')
    }
    
    // Generate suggestions
    if (invoiceData.amount < 1000) {
      suggestions.push('Consider setting up auto-approval for this vendor')
    }
    
    if (invoiceData.category === 'Office Supplies') {
      suggestions.push('This category typically has fast approval times')
    }
    
    if (invoiceData.due_date) {
      const dueDate = new Date(invoiceData.due_date)
      const today = new Date()
      const daysUntilDue = Math.ceil((dueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
      
      if (daysUntilDue < 7) {
        suggestions.push('Invoice due soon - prioritize processing')
      }
    }
    
    const validationResult = {
      is_valid: warnings.length === 0,
      warnings,
      suggestions,
      validation_score: Math.round((1 - warnings.length * 0.2) * 100) / 100,
      duplicate_check: {
        is_duplicate: false,
        similar_invoices: []
      },
      compliance_check: {
        is_compliant: true,
        issues: []
      }
    }

    return NextResponse.json(validationResult)
    
  } catch (error) {
    console.error('Invoice validation error:', error)
    return NextResponse.json(
      { error: 'Invoice validation failed. Please try again.' },
      { status: 500 }
    )
  }
}




