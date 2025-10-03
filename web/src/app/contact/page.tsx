'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Mail, 
  Phone, 
  MapPin, 
  Clock,
  MessageCircle,
  Send,
  Calendar,
  Video,
  User,
  Home
} from 'lucide-react'
import Link from 'next/link'

export default function ContactPage() {
  const searchParams = useSearchParams()
  const inquiryParam = searchParams.get('inquiry')
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    subject: '',
    inquiryType: inquiryParam === 'sales' ? 'sales' : '',
    message: '',
    preferredDate: '',
    preferredTime: '',
    timezone: '',
    attendees: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [contactId, setContactId] = useState('')

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccessMessage('')
    setIsSubmitting(true)

    // Enhanced validation
    const validationErrors = []
    
    if (!formData.firstName.trim()) validationErrors.push('First name is required')
    if (!formData.lastName.trim()) validationErrors.push('Last name is required')
    if (!formData.email.trim()) {
      validationErrors.push('Email address is required')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      validationErrors.push('Please enter a valid email address')
    }
    if (!formData.message.trim()) validationErrors.push('Message is required')
    if (!formData.inquiryType) validationErrors.push('Please select an inquiry type')
    
    // Demo-specific validation
    if (formData.inquiryType === 'demo') {
      if (!formData.preferredDate) validationErrors.push('Preferred date is required for demo scheduling')
      if (!formData.preferredTime) validationErrors.push('Preferred time is required for demo scheduling')
      if (!formData.timezone) validationErrors.push('Timezone is required for demo scheduling')
      if (!formData.attendees || parseInt(formData.attendees) < 1 || parseInt(formData.attendees) > 20) {
        validationErrors.push('Please enter a valid number of attendees (1-20)')
      }
    }

    if (validationErrors.length > 0) {
      setError(validationErrors.join('. ') + '.')
      setIsSubmitting(false)
      return
    }

    try {
      // Call the contact API endpoint
      const response = await fetch('/api/v1/contact/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        const result = await response.json()
        setSubmitted(true)
        setSuccessMessage(result.message || 'Thank you for your message! We\'ll get back to you within 24 hours.')
        setContactId(result.contact_id || '')
        setFormData({
          firstName: '',
          lastName: '',
          email: '',
          company: '',
          subject: '',
          inquiryType: '',
          message: '',
          preferredDate: '',
          preferredTime: '',
          timezone: '',
          attendees: ''
        })
      } else {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to send message')
      }
    } catch (error) {
      console.error('Contact form error:', error)
      setError('Failed to send message. Please try again or contact us directly.')
    } finally {
      setIsSubmitting(false)
    }
  }
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Home Button */}
      <div className="absolute top-4 left-4 z-10">
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

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Contact Us</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get in touch with our team. We're here to help you with any questions about our AI-powered invoice processing platform.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Contact Information */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Mail className="h-5 w-5 mr-2" />
                  Email Support
                </CardTitle>
                <CardDescription>
                  Send us a detailed message and we'll get back to you within 24 hours.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-2">General Inquiries:</p>
                <p className="font-medium">support@aierpsaas.com</p>
                <p className="text-sm text-gray-600 mt-4 mb-2">Sales:</p>
                <p className="font-medium">sales@aierpsaas.com</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Phone className="h-5 w-5 mr-2" />
                  Phone Support
                </CardTitle>
                <CardDescription>
                  Call us for urgent issues or immediate assistance.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-2">US & Canada:</p>
                <p className="font-medium">+1 (555) 123-4567</p>
                <p className="text-sm text-gray-600 mt-4 mb-2">International:</p>
                <p className="font-medium">+1 (555) 123-4568</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MapPin className="h-5 w-5 mr-2" />
                  Office Location
                </CardTitle>
                <CardDescription>
                  Visit our headquarters for in-person meetings.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="font-medium">AI ERP SaaS Inc.</p>
                <p className="text-sm text-gray-600 mt-1">
                  123 Technology Drive<br />
                  Suite 500<br />
                  San Francisco, CA 94105<br />
                  United States
                </p>
              </CardContent>
            </Card>

            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center text-blue-800">
                  <Video className="h-5 w-5 mr-2" />
                  Schedule a Demo
                </CardTitle>
                <CardDescription className="text-blue-700">
                  Book a personalized demo to see our AI-powered invoice processing in action.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-blue-700">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span>30-45 minute personalized walkthrough</span>
                  </div>
                  <div className="flex items-center text-sm text-blue-700">
                    <User className="h-4 w-4 mr-2" />
                    <span>Up to 20 attendees</span>
                  </div>
                  <div className="flex items-center text-sm text-blue-700">
                    <Clock className="h-4 w-4 mr-2" />
                    <span>Available Monday-Friday, 9 AM - 6 PM PST</span>
                  </div>
                  <div className="text-xs text-blue-600 mt-2 bg-blue-100 p-2 rounded">
                    Select "Schedule a Demo" in the form to book your session
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="h-5 w-5 mr-2" />
                  Business Hours
                </CardTitle>
                <CardDescription>
                  Our support team is available during these hours.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Monday - Friday:</span>
                    <span className="font-medium">9:00 AM - 6:00 PM PST</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Saturday:</span>
                    <span className="font-medium">10:00 AM - 4:00 PM PST</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Sunday:</span>
                    <span className="font-medium">Closed</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Contact Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MessageCircle className="h-5 w-5 mr-2" />
                  Send us a Message
                </CardTitle>
                <CardDescription>
                  Fill out the form below and we'll get back to you as soon as possible.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Success Message */}
                {submitted && successMessage && (
                  <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-green-800">
                          Message Sent Successfully!
                        </h3>
                        <div className="mt-2 text-sm text-green-700">
                          <p>{successMessage}</p>
                          {contactId && (
                            <p className="mt-1">
                              <strong>Reference ID:</strong> {contactId}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Error Message */}
                {error && (
                  <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-red-800">
                          Error Sending Message
                        </h3>
                        <div className="mt-2 text-sm text-red-700">
                          <p>{error}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="firstName">First Name</Label>
                      <Input
                        id="firstName"
                        name="firstName"
                        value={formData.firstName}
                        onChange={handleInputChange}
                        placeholder="John"
                        className="mt-1"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="lastName">Last Name</Label>
                      <Input
                        id="lastName"
                        name="lastName"
                        value={formData.lastName}
                        onChange={handleInputChange}
                        placeholder="Doe"
                        className="mt-1"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="john@company.com"
                      className="mt-1"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="company">Company</Label>
                    <Input
                      id="company"
                      name="company"
                      value={formData.company}
                      onChange={handleInputChange}
                      placeholder="Your Company Name"
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="subject">Subject</Label>
                    <Input
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleInputChange}
                      placeholder="How can we help you?"
                      className="mt-1"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="inquiryType">Type of Inquiry</Label>
                    <select
                      id="inquiryType"
                      name="inquiryType"
                      value={formData.inquiryType}
                      onChange={handleInputChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      aria-label="Type of inquiry"
                      required
                    >
                      <option value="">Select an option</option>
                      <option value="demo">Schedule a Demo</option>
                      <option value="general">General Question</option>
                      <option value="sales">Sales Inquiry</option>
                      <option value="support">Technical Support</option>
                      <option value="billing">Billing Question</option>
                      <option value="partnership">Partnership</option>
                      <option value="other">Other</option>
                    </select>
                  </div>

                  {/* Demo Scheduling Fields - Only show when "Schedule a Demo" is selected */}
                  {formData.inquiryType === 'demo' && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-4">
                      <div className="flex items-center text-blue-800 font-medium">
                        <Video className="h-5 w-5 mr-2" />
                        Demo Scheduling Details
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="preferredDate">Preferred Date</Label>
                          <Input
                            id="preferredDate"
                            name="preferredDate"
                            type="date"
                            value={formData.preferredDate}
                            onChange={handleInputChange}
                            className="mt-1"
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="preferredTime">Preferred Time</Label>
                          <select
                            id="preferredTime"
                            name="preferredTime"
                            value={formData.preferredTime}
                            onChange={handleInputChange}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            aria-label="Preferred time for demo"
                            required
                          >
                            <option value="">Select time</option>
                            <option value="9:00 AM">9:00 AM</option>
                            <option value="10:00 AM">10:00 AM</option>
                            <option value="11:00 AM">11:00 AM</option>
                            <option value="12:00 PM">12:00 PM</option>
                            <option value="1:00 PM">1:00 PM</option>
                            <option value="2:00 PM">2:00 PM</option>
                            <option value="3:00 PM">3:00 PM</option>
                            <option value="4:00 PM">4:00 PM</option>
                            <option value="5:00 PM">5:00 PM</option>
                          </select>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="timezone">Timezone</Label>
                          <select
                            id="timezone"
                            name="timezone"
                            value={formData.timezone}
                            onChange={handleInputChange}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            aria-label="Timezone for demo"
                            required
                          >
                            <option value="">Select timezone</option>
                            <option value="PST">Pacific Standard Time (PST)</option>
                            <option value="MST">Mountain Standard Time (MST)</option>
                            <option value="CST">Central Standard Time (CST)</option>
                            <option value="EST">Eastern Standard Time (EST)</option>
                            <option value="GMT">Greenwich Mean Time (GMT)</option>
                            <option value="CET">Central European Time (CET)</option>
                            <option value="JST">Japan Standard Time (JST)</option>
                            <option value="AEST">Australian Eastern Standard Time (AEST)</option>
                          </select>
                        </div>
                        <div>
                          <Label htmlFor="attendees">Number of Attendees</Label>
                          <Input
                            id="attendees"
                            name="attendees"
                            type="number"
                            min="1"
                            max="20"
                            value={formData.attendees}
                            onChange={handleInputChange}
                            placeholder="1-20"
                            className="mt-1"
                            required
                          />
                        </div>
                      </div>

                      <div className="text-sm text-blue-700 bg-blue-100 p-3 rounded-md">
                        <strong>Demo Details:</strong> Our demo typically lasts 30-45 minutes and includes a personalized walkthrough of our AI-powered invoice processing platform, Q&A session, and discussion of your specific use case.
                      </div>
                    </div>
                  )}

                  <div>
                    <Label htmlFor="message">Message</Label>
                    <Textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleInputChange}
                      placeholder={formData.inquiryType === 'demo' ? "Please tell us about your current invoice processing workflow and any specific features you'd like to see in the demo..." : "Please describe your inquiry in detail..."}
                      className="mt-1"
                      rows={6}
                      required
                    />
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full" 
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        {formData.inquiryType === 'demo' ? 'Scheduling Demo...' : 'Sending Message...'}
                      </>
                    ) : formData.inquiryType === 'demo' ? (
                      <>
                        <Calendar className="h-4 w-4 mr-2" />
                        Schedule Demo
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Send Message
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">How quickly can I get started?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  You can get started immediately with our free trial. Our onboarding process typically takes 15-30 minutes, and you'll be processing invoices within the first hour.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Do you offer custom integrations?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Yes! We offer custom integrations with any ERP system or business application. Our team can work with you to create seamless data flows.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">What file formats do you support?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  We support PDF, PNG, JPG, and TIFF formats. Our AI can extract data from both digital and scanned documents with high accuracy.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Is my data secure?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Absolutely. We're SOC 2 Type II certified and ISO 27001 compliant. All data is encrypted in transit and at rest, and we never share your information.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

