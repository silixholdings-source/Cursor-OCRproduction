'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Search, 
  HelpCircle, 
  MessageCircle, 
  Mail, 
  Phone, 
  BookOpen,
  Video,
  FileText,
  ExternalLink,
  ArrowRight,
  Home,
  User
} from 'lucide-react'
import Link from 'next/link'

export default function HelpPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')

  const handleStartChat = () => {
    window.open('mailto:support@ai-erp-saas.com?subject=Live Chat Support Request', '_blank')
  }
  
  const handleSendEmail = () => {
    window.open('mailto:support@ai-erp-saas.com?subject=Support Request', '_blank')
  }
  
  const handleCallNow = () => {
    window.open('tel:+1-555-0123', '_self')
  }

  const faqs = [
    {
      question: "How do I get started with AI ERP SaaS?",
      answer: "Simply sign up for a free trial, upload your first invoice, and watch our AI extract the data automatically. Our onboarding guide will walk you through each step."
    },
    {
      question: "How does the AI invoice processing work?",
      answer: "Our advanced OCR technology reads invoices in any format (PDF, image, scanned documents) and extracts key data like vendor, amount, date, and line items with 99.9% accuracy."
    },
    {
      question: "Can I integrate with my existing ERP system?",
      answer: "Yes! We support integration with major ERP systems including SAP, Oracle, Microsoft Dynamics, QuickBooks, Xero, and more. Setup takes just a few minutes."
    },
    {
      question: "Is my data secure?",
      answer: "Absolutely. We use enterprise-grade security with encryption, secure data centers, SOC 2 compliance, and strict access controls. Your data is never shared with third parties."
    },
    {
      question: "How much does it cost?",
      answer: "We offer flexible pricing starting at $19/month for small businesses, with enterprise plans available. All plans include a 3-day free trial with no credit card required."
    },
    {
      question: "Do you offer customer support?",
      answer: "Yes! We provide 24/7 support via email, live chat, and phone. Enterprise customers get dedicated account managers and priority support."
    }
  ]

  const helpCategories = [
    {
      title: "Getting Started",
      icon: BookOpen,
      items: [
        { title: "Quick Start Guide", href: "/demo/trial", type: "guide" },
        { title: "Account Setup", href: "/auth/register", type: "guide" },
        { title: "First Invoice Upload", href: "/demo", type: "guide" }
      ]
    },
    {
      title: "Features & Tutorials",
      icon: FileText,
      items: [
        { title: "Invoice Processing", href: "/features", type: "guide" },
        { title: "Approval Workflows", href: "/features#workflows", type: "guide" },
        { title: "ERP Integration", href: "/features#integrations", type: "guide" }
      ]
    },
    {
      title: "Account & Billing",
      icon: User,
      items: [
        { title: "Pricing Plans", href: "/pricing", type: "guide" },
        { title: "Account Settings", href: "/auth/login", type: "guide" },
        { title: "Billing Questions", href: "/contact?inquiry=billing", type: "guide" }
      ]
    },
    {
      title: "Video Tutorials",
      icon: Video,
      items: [
        { title: "Platform Overview", href: "/demo", type: "video" },
        { title: "Interactive Demo", href: "/demo/trial", type: "video" },
        { title: "Advanced Features", href: "/features", type: "video" }
      ]
    }
  ]

  const filteredFaqs = faqs.filter(faq => 
    faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" asChild>
                <Link href="/">
                  <Home className="w-4 h-4 mr-2" />
                  Back to Home
                </Link>
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Help & Support</h1>
                <p className="text-gray-600">
                  Find answers, get help, and learn how to use AI ERP SaaS
                </p>
              </div>
            </div>
            <Button asChild>
              <Link href="/auth/register?trial=true">
                Start Free Trial
              </Link>
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        {/* Search */}
        <div className="mb-12">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              How can we help you?
            </h2>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <Input
                type="text"
                placeholder="Search help articles, features, or ask a question..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 py-4 text-lg"
              />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={handleStartChat}>
            <CardContent className="p-6 text-center">
              <MessageCircle className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Live Chat</h3>
              <p className="text-gray-600 mb-4">Get instant help from our support team</p>
              <Button className="w-full">Start Chat</Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={handleSendEmail}>
            <CardContent className="p-6 text-center">
              <Mail className="h-12 w-12 text-green-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Email Support</h3>
              <p className="text-gray-600 mb-4">Send us a detailed message</p>
              <Button variant="outline" className="w-full">Send Email</Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={handleCallNow}>
            <CardContent className="p-6 text-center">
              <Phone className="h-12 w-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Phone Support</h3>
              <p className="text-gray-600 mb-4">Call us for urgent issues</p>
              <Button variant="outline" className="w-full">Call Now</Button>
            </CardContent>
          </Card>
        </div>

        {/* Help Categories */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Browse Help Topics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {helpCategories.map((category, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <category.icon className="h-6 w-6 text-blue-600 mr-3" />
                    {category.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {category.items.map((item, itemIndex) => (
                      <li key={itemIndex}>
                        <Link
                          href={item.href}
                          className="text-blue-600 hover:text-blue-800 text-sm flex items-center group"
                        >
                          {item.title}
                          {item.type === 'video' && (
                            <Video className="ml-2 h-3 w-3" />
                          )}
                          <ArrowRight className="ml-1 h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </Link>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* FAQ Section */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Frequently Asked Questions</h2>
          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredFaqs.map((faq, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">{faq.question}</h3>
                    <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
            
            {filteredFaqs.length === 0 && searchQuery && (
              <div className="text-center py-12">
                <HelpCircle className="mx-auto h-16 w-16 text-gray-400" />
                <h3 className="mt-4 text-lg font-medium text-gray-900">No results found</h3>
                <p className="mt-2 text-gray-500">
                  Try searching with different keywords or browse our help categories above.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-8 text-center text-white">
          <h2 className="text-2xl font-bold mb-4">Still Need Help?</h2>
          <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
            Our support team is here to help you succeed. Get personalized assistance 
            with setup, integrations, or any questions about AI ERP SaaS.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              onClick={() => router.push('/contact')}
              className="bg-white text-blue-600 hover:bg-gray-100 transition-all duration-200 hover:scale-105 shadow-lg"
            >
              Contact Support
            </Button>
            <Button 
              onClick={() => router.push('/auth/register?trial=true')}
              variant="outline" 
              className="border-white text-white hover:bg-white hover:text-blue-600"
            >
              Start Free Trial
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

