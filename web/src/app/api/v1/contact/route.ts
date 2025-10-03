import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { 
      firstName, 
      lastName, 
      email, 
      company, 
      subject, 
      inquiryType, 
      message, 
      preferredDate, 
      preferredTime, 
      timezone, 
      attendees 
    } = body

    // Basic validation
    if (!firstName || !lastName || !email || !subject || !message) {
      return NextResponse.json(
        { error: 'First name, last name, email, subject, and message are required' },
        { status: 400 }
      )
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return NextResponse.json(
        { error: 'Please enter a valid email address' },
        { status: 400 }
      )
    }

    // For demo purposes, we'll simulate successful submission
    console.log('Contact form submission:', {
      firstName,
      lastName,
      email,
      company,
      subject,
      inquiryType,
      message,
      preferredDate,
      preferredTime,
      timezone,
      attendees,
      timestamp: new Date().toISOString()
    })

    // Generate a mock contact ID
    const contactId = `contact_${Date.now()}`

    // Return success response
    return NextResponse.json({
      success: true,
      contactId,
      message: inquiryType === 'demo' 
        ? 'Demo scheduled successfully! We\'ll contact you within 24 hours to confirm your demo appointment.'
        : 'Message sent successfully! We\'ll get back to you within 24 hours.',
      data: {
        id: contactId,
        firstName,
        lastName,
        email,
        company,
        subject,
        inquiryType,
        message,
        preferredDate,
        preferredTime,
        timezone,
        attendees,
        submittedAt: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error('Contact form API error:', error)
    return NextResponse.json(
      { error: 'Internal server error. Please try again later.' },
      { status: 500 }
    )
  }
}

