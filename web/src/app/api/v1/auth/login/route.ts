import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    // Basic validation
    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required' },
        { status: 400 }
      )
    }

    // Mock authentication - in production, this would validate against your backend
    if (email === 'demo@example.com' && password === 'password') {
      // Mock JWT token
      const token = 'mock_jwt_token_' + Date.now()
      
      return NextResponse.json({
        success: true,
        token,
        user: {
          id: '1',
          email: 'demo@example.com',
          name: 'Demo User',
          role: 'admin',
          company_id: '1'
        },
        company: {
          id: '1',
          name: 'Demo Company',
          max_users: 10,
          max_storage_gb: 100,
          plan: 'enterprise'
        }
      })
    }

    return NextResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    )
  } catch (error) {
    console.error('Login error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}





































