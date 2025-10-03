import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { 
      email, 
      password, 
      name, 
      companyName, 
      industry 
    } = body

    // Enhanced validation
    const validationErrors = []
    
    if (!email || !email.trim()) {
      validationErrors.push('Email is required')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      validationErrors.push('Please enter a valid email address')
    }
    
    if (!password || !password.trim()) {
      validationErrors.push('Password is required')
    } else if (password.length < 8) {
      validationErrors.push('Password must be at least 8 characters long')
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      validationErrors.push('Password must contain at least one uppercase letter, one lowercase letter, and one number')
    }
    
    if (!name || !name.trim()) {
      validationErrors.push('Name is required')
    }
    
    if (!companyName || !companyName.trim()) {
      validationErrors.push('Company name is required')
    }
    
    if (validationErrors.length > 0) {
      return NextResponse.json(
        { error: validationErrors.join('. ') + '.' },
        { status: 400 }
      )
    }

    // In production, this would:
    // 1. Check if email already exists
    // 2. Hash the password
    // 3. Create company and user records
    // 4. Send welcome email
    // 5. Generate JWT token
    
    // Mock registration response
    const token = 'mock_jwt_token_' + Date.now()
    
    return NextResponse.json({
      success: true,
      token,
      user: {
        id: '1',
        email: email.toLowerCase().trim(),
        name: name.trim(),
        role: 'owner',
        company_id: '1'
      },
      company: {
        id: '1',
        name: companyName.trim(),
        max_users: 10,
        max_storage_gb: 100,
        plan: 'professional',
        industry: industry || 'Technology'
      }
    })
    
  } catch (error) {
    console.error('Registration error:', error)
    return NextResponse.json(
      { error: 'Registration failed. Please try again.' },
      { status: 500 }
    )
  }
}