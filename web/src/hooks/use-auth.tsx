'use client'

import { useState, useEffect, createContext, useContext } from 'react'

interface User {
  id: string
  email: string
  name: string
  role: string
  company_id?: string
}

interface Company {
  id: string
  name: string
  max_users: number
  max_storage_gb: number
  plan: string
  trial_ends_at?: string
  is_trial: boolean
}

interface AuthContextType {
  user: User | null
  company: Company | null
  isLoading: boolean
  isAuthenticated: boolean
  isTrialExpired: boolean
  trialDaysLeft: number
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (userData: any) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [company, setCompany] = useState<Company | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Calculate trial status
  const isTrialExpired = company?.is_trial && company?.trial_ends_at 
    ? new Date() > new Date(company.trial_ends_at)
    : false

  const trialDaysLeft = company?.is_trial && company?.trial_ends_at
    ? Math.max(0, Math.ceil((new Date(company.trial_ends_at).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)))
    : 0

  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken === 'mock_token') {
      // Simulate a logged-in user
      setUser({
        id: '1',
        email: 'demo@example.com',
        name: 'Demo User',
        role: 'admin',
        company_id: '1'
      })
      const trialStartDate = new Date()
      const trialEndDate = new Date()
      trialEndDate.setDate(trialStartDate.getDate() + 3) // 3-day trial
      
      setCompany({
        id: '1',
        name: 'Demo Company',
        max_users: 10,
        max_storage_gb: 100,
        plan: 'trial',
        is_trial: true,
        trial_ends_at: trialEndDate.toISOString()
      })
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    console.log('LOGIN CALLED:', { email, password: '***' })
    setIsLoading(true)
    
    // Input validation
    if (!email || !password) {
      throw new Error('Email and password are required')
    }
    
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      throw new Error('Please enter a valid email address')
    }
    
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email.toLowerCase().trim(), 
          password 
        }),
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Login failed')
      }
      
      if (data.success) {
        // Add trial information to company data
        const trialStartDate = new Date()
        const trialEndDate = new Date()
        trialEndDate.setDate(trialStartDate.getDate() + 3) // 3-day trial
        
        const companyWithTrial = {
          ...data.company,
          is_trial: true,
          trial_ends_at: trialEndDate.toISOString()
        }
        
        console.log('LOGIN SUCCESS:', { user: data.user, company: companyWithTrial })
        setUser(data.user)
        setCompany(companyWithTrial)
        localStorage.setItem('auth_token', data.token)
      } else {
        throw new Error('Login failed')
      }
    } catch (error) {
      console.error('LOGIN FAILED:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const demoLogin = async () => {
    setIsLoading(true)
    try {
      const base = 'http://127.0.0.1:8001/api/v1'
      const res = await fetch(`${base}/auth/demo-login`, { method: 'POST' })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.detail || 'Demo login failed')
      setUser(data.user)
      setCompany(data.company)
      const token = data.tokens?.access_token
      if (token) localStorage.setItem('auth_token', token)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    console.log('LOGOUT CALLED')
    
    try {
      // Call logout API endpoint if token exists
      const token = localStorage.getItem('auth_token')
      if (token && token !== 'mock_token') {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        })
      }
    } catch (error) {
      console.error('Logout API call failed:', error)
      // Continue with logout even if API call fails
    }
    
    // Clear local state and storage
    setUser(null)
    setCompany(null)
    localStorage.removeItem('auth_token')
    
    // Redirect to home page
    window.location.href = '/'
  }

  const register = async (userData: any) => {
    console.log('REGISTER CALLED:', userData)
    setIsLoading(true)
    
    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userData.email,
          password: userData.password || 'defaultPassword123',
          name: userData.name,
          companyName: userData.companyName,
          industry: userData.industry
        }),
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Registration failed')
      }
      
      if (data.success) {
        // Add trial information to company data
        const trialStartDate = new Date()
        const trialEndDate = new Date()
        trialEndDate.setDate(trialStartDate.getDate() + 14) // 14-day trial for new registrations
        
        const companyWithTrial = {
          ...data.company,
          is_trial: true,
          trial_ends_at: trialEndDate.toISOString()
        }
        
        console.log('REGISTER SUCCESS:', { user: data.user, company: companyWithTrial })
        setUser(data.user)
        setCompany(companyWithTrial)
        localStorage.setItem('auth_token', data.token)
      } else {
        throw new Error('Registration failed')
      }
    } catch (error) {
      console.error('REGISTER FAILED:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const value = {
    user,
    company,
    isLoading,
    isAuthenticated: !!user,
    isTrialExpired,
    trialDaysLeft,
    login,
    logout,
    register,
    demoLogin
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}