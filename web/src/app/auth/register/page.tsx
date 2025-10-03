'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { logger } from '@/lib/logger'
import { Eye, EyeOff, Loader2, Building2, User, Home } from 'lucide-react'

export default function RegisterPage() {
  const searchParams = useSearchParams()
  const isTrial = searchParams.get('trial') === 'true'
  const trialSource = searchParams.get('source') || 'unknown'
  const selectedPlan = searchParams.get('plan') || 'professional'
  
  const [formData, setFormData] = useState({
    company_name: '',
    company_email: '',
    industry: '',
    company_size: '',
    owner_email: '',
    owner_username: '',
    owner_password: '',
    owner_confirm_password: '',
    owner_first_name: '',
    owner_last_name: ''
  })
  
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const { register } = useAuth()
  const router = useRouter()

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Enhanced validation
    const validationErrors = []
    
    // Company validation
    if (!formData.company_name.trim()) {
      validationErrors.push('Company name is required')
    }
    
    if (!formData.company_email.trim()) {
      validationErrors.push('Company email is required')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.company_email)) {
      validationErrors.push('Please enter a valid company email address')
    }
    
    // Owner validation
    if (!formData.owner_first_name.trim()) {
      validationErrors.push('First name is required')
    }
    
    if (!formData.owner_last_name.trim()) {
      validationErrors.push('Last name is required')
    }
    
    if (!formData.owner_email.trim()) {
      validationErrors.push('Owner email is required')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.owner_email)) {
      validationErrors.push('Please enter a valid owner email address')
    }
    
    // Password validation
    if (!formData.owner_password.trim()) {
      validationErrors.push('Password is required')
    } else if (formData.owner_password.length < 8) {
      validationErrors.push('Password must be at least 8 characters long')
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.owner_password)) {
      validationErrors.push('Password must contain at least one uppercase letter, one lowercase letter, and one number')
    }
    
    if (formData.owner_password !== formData.owner_confirm_password) {
      validationErrors.push('Passwords do not match')
    }
    
    if (validationErrors.length > 0) {
      setError(validationErrors.join('. ') + '.')
      return
    }

    setIsLoading(true)

        try {
          logger.debug('Registration attempt:', { 
            email: formData.owner_email,
            companyName: formData.company_name,
            industry: formData.industry
          })
          await register({
            email: formData.owner_email,
            password: formData.owner_password,
            name: `${formData.owner_first_name} ${formData.owner_last_name}`,
            companyName: formData.company_name,
            industry: formData.industry
          })
          logger.debug('Registration successful, redirecting to dashboard...')
          router.push('/dashboard')
    } catch (err: any) {
      logger.error('Registration error:', err)
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Home Button */}
      <div className="absolute top-4 left-4">
        <Button
          variant="outline"
          size="sm"
          asChild
          className="flex items-center gap-2"
        >
          <Link href="/">
            <Home className="h-4 w-4" />
            Back to Home
          </Link>
        </Button>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">AI</span>
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {isTrial ? 'Start Your Free 3-Day Trial' : 'Create your company account'}
        </h2>
        {isTrial && selectedPlan && (
          <div className="mt-4 text-center">
            <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              Selected Plan: <span className="ml-1 capitalize font-semibold">{selectedPlan}</span>
            </div>
          </div>
        )}
        <p className="mt-2 text-center text-sm text-gray-600">
          {isTrial ? (
            <>
              No credit card required • Full access to all features • Cancel anytime
            </>
          ) : (
            <>
              Or{' '}
              <Link 
                href="/auth/login" 
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                sign in to your existing account
              </Link>
            </>
          )}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {isTrial && (
              <Alert className="border-blue-200 bg-blue-50">
                <AlertDescription className="text-blue-800">
                  <strong>Free Trial Active:</strong> You're starting a 3-day free trial with full access to all features. 
                  No payment required and you can cancel anytime.
                </AlertDescription>
              </Alert>
            )}
            
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Company Information */}
            <div className="border-b border-gray-200 pb-6">
              <div className="flex items-center space-x-2 mb-4">
                <Building2 className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-medium text-gray-900">Company Information</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="company_name" className="block text-sm font-medium text-gray-700">
                    Company Name *
                  </Label>
                  <Input
                    id="company_name"
                    name="company_name"
                    type="text"
                    required
                    value={formData.company_name}
                    onChange={handleInputChange}
                    className="mt-1"
                    placeholder="Enter company name"
                  />
                </div>

                <div>
                  <Label htmlFor="company_email" className="block text-sm font-medium text-gray-700">
                    Company Email *
                  </Label>
                  <Input
                    id="company_email"
                    name="company_email"
                    type="email"
                    required
                    value={formData.company_email}
                    onChange={handleInputChange}
                    className="mt-1"
                    placeholder="Enter company email"
                  />
                </div>

                <div>
                  <Label htmlFor="industry" className="block text-sm font-medium text-gray-700">
                    Industry
                  </Label>
                  <select
                    id="industry"
                    name="industry"
                    value={formData.industry}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    aria-label="Select industry"
                  >
                    <option value="">Select industry</option>
                    <option value="Technology">Technology</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Finance">Finance</option>
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="Retail">Retail</option>
                    <option value="Education">Education</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="company_size" className="block text-sm font-medium text-gray-700">
                    Company Size
                  </Label>
                  <select
                    id="company_size"
                    name="company_size"
                    value={formData.company_size}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    aria-label="Select company size"
                  >
                    <option value="">Select size</option>
                    <option value="1-10">1-10 employees</option>
                    <option value="11-50">11-50 employees</option>
                    <option value="51-200">51-200 employees</option>
                    <option value="201-1000">201-1000 employees</option>
                    <option value="1000+">1000+ employees</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Owner Information */}
            <div className="border-b border-gray-200 pb-6">
              <div className="flex items-center space-x-2 mb-4">
                <User className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-medium text-gray-900">Owner Information</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="owner_first_name" className="block text-sm font-medium text-gray-700">
                    First Name *
                  </Label>
                  <Input
                    id="owner_first_name"
                    name="owner_first_name"
                    type="text"
                    required
                    value={formData.owner_first_name}
                    onChange={handleInputChange}
                    className="mt-1"
                    placeholder="Enter first name"
                  />
                </div>

                <div>
                  <Label htmlFor="owner_last_name" className="block text-sm font-medium text-gray-700">
                    Last Name *
                  </Label>
                  <Input
                    id="owner_last_name"
                    name="owner_last_name"
                    type="text"
                    required
                    value={formData.owner_last_name}
                    onChange={handleInputChange}
                    className="mt-1"
                    placeholder="Enter last name"
                  />
                </div>

                <div>
                  <Label htmlFor="owner_email" className="block text-sm font-medium text-gray-700">
                    Email Address *
                  </Label>
                  <Input
                    id="owner_email"
                    name="owner_email"
                    type="email"
                    required
                    value={formData.owner_email}
                    onChange={handleInputChange}
                    className="mt-1"
                    placeholder="Enter email address"
                  />
                </div>

                <div>
                  <Label htmlFor="owner_username" className="block text-sm font-medium text-gray-700">
                    Username *
                  </Label>
                  <Input
                    id="owner_username"
                    name="owner_username"
                    type="text"
                    required
                    value={formData.owner_username}
                    onChange={handleInputChange}
                    className="mt-1"
                    placeholder="Choose username"
                  />
                </div>

                <div>
                  <Label htmlFor="owner_password" className="block text-sm font-medium text-gray-700">
                    Password *
                  </Label>
                  <div className="mt-1 relative">
                    <Input
                      id="owner_password"
                      name="owner_password"
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={formData.owner_password}
                      onChange={handleInputChange}
                      className="pr-10"
                      placeholder="Create password"
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4 text-gray-400" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>

                <div>
                  <Label htmlFor="owner_confirm_password" className="block text-sm font-medium text-gray-700">
                    Confirm Password *
                  </Label>
                  <div className="mt-1 relative">
                    <Input
                      id="owner_confirm_password"
                      name="owner_confirm_password"
                      type={showConfirmPassword ? 'text' : 'password'}
                      required
                      value={formData.owner_confirm_password}
                      onChange={handleInputChange}
                      className="pr-10"
                      placeholder="Confirm password"
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4 text-gray-400" />
                      ) : (
                        <Eye className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                    Creating account...
                  </>
                ) : (
                  'Create company account'
                )}
              </Button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Already have an account?</span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                href="/auth/login"
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Sign in to existing account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}












