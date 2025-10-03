'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Search, 
  HelpCircle, 
  MessageCircle, 
  Mail, 
  Phone, 
  BookOpen,
  Video,
  FileText,
  ExternalLink
} from 'lucide-react'

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = useState('')
  
  const handleStartChat = () => {
    // In a real app, this would open a chat widget
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
      question: "How do I upload invoices?",
      answer: "You can upload invoices by going to the Invoices page and clicking the 'Upload Invoice' button. Supported formats include PDF, PNG, and JPG files."
    },
    {
      question: "How does the approval workflow work?",
      answer: "Invoices are automatically processed using AI and then sent to designated approvers based on your company's workflow rules. You can view and manage approvals in the Approvals section."
    },
    {
      question: "Can I integrate with my existing ERP system?",
      answer: "Yes! We support integration with major ERP systems including SAP, Oracle, Microsoft Dynamics, and more. Go to the ERP Integration page to set up your connection."
    },
    {
      question: "How do I add new users to my company?",
      answer: "Company administrators can add new users by going to the Users page and clicking 'Add User'. You can assign different roles and permissions to each user."
    },
    {
      question: "What file formats are supported for invoice processing?",
      answer: "We support PDF, PNG, JPG, and TIFF formats. For best results, ensure your invoices are clear and well-lit when scanning or photographing."
    },
    {
      question: "How do I change my company settings?",
      answer: "Go to the Company page in your dashboard to update company information, billing details, and other settings. Only administrators can make these changes."
    }
  ]

  const helpCategories = [
    {
      title: "Getting Started",
      icon: BookOpen,
      items: [
        { title: "Quick Start Guide", href: "/dashboard/help/quick-start", type: "guide" },
        { title: "Setting Up Your Company", href: "/dashboard/company", type: "guide" },
        { title: "Adding Your First Users", href: "/dashboard/users", type: "guide" }
      ]
    },
    {
      title: "Invoice Processing",
      icon: FileText,
      items: [
        { title: "Uploading Invoices", href: "/dashboard/invoices/upload", type: "guide" },
        { title: "Understanding AI Processing", href: "/dashboard/help/ai-processing", type: "guide" },
        { title: "Approval Workflows", href: "/dashboard/approvals", type: "guide" }
      ]
    },
    {
      title: "Integrations",
      icon: ExternalLink,
      items: [
        { title: "ERP Integration Setup", href: "/dashboard/erp", type: "guide" },
        { title: "API Documentation", href: "/dashboard/help/api-docs", type: "guide" },
        { title: "Webhook Configuration", href: "/dashboard/help/webhooks", type: "guide" }
      ]
    },
    {
      title: "Video Tutorials",
      icon: Video,
      items: [
        { title: "Platform Overview", href: "/dashboard/help/video/overview", type: "video" },
        { title: "Invoice Processing Demo", href: "/dashboard/help/video/demo", type: "video" },
        { title: "Advanced Features", href: "/dashboard/help/video/advanced", type: "video" }
      ]
    }
  ]

  const filteredFaqs = faqs.filter(faq => 
    faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Help & Support</h1>
        <p className="mt-2 text-gray-600">
          Find answers to common questions and get help with using the platform.
        </p>
      </div>

      {/* Search */}
      <div className="mb-8">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Search help articles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <MessageCircle className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Live Chat</h3>
              <p className="text-gray-600">Get instant help from our support team</p>
            </div>
          </div>
          <Button className="mt-4 w-full" onClick={handleStartChat}>Start Chat</Button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Mail className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Email Support</h3>
              <p className="text-gray-600">Send us a detailed message</p>
            </div>
          </div>
          <Button className="mt-4 w-full" variant="outline" onClick={handleSendEmail}>Send Email</Button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Phone className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">Phone Support</h3>
              <p className="text-gray-600">Call us for urgent issues</p>
            </div>
          </div>
          <Button className="mt-4 w-full" variant="outline" onClick={handleCallNow}>Call Now</Button>
        </div>
      </div>

      {/* Help Categories */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Help Categories</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {helpCategories.map((category, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center mb-4">
                <category.icon className="h-6 w-6 text-blue-600" />
                <h3 className="ml-3 text-lg font-medium text-gray-900">{category.title}</h3>
              </div>
              <ul className="space-y-2">
                {category.items.map((item, itemIndex) => (
                  <li key={itemIndex}>
                    <a
                      href={item.href}
                      className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
                    >
                      {item.title}
                      {item.type === 'video' && (
                        <Video className="ml-1 h-3 w-3" />
                      )}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* FAQ Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
        <div className="space-y-4">
          {filteredFaqs.map((faq, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-2">{faq.question}</h3>
              <p className="text-gray-600">{faq.answer}</p>
            </div>
          ))}
        </div>
        
        {filteredFaqs.length === 0 && searchQuery && (
          <div className="text-center py-8">
            <HelpCircle className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try searching with different keywords.
            </p>
          </div>
        )}
      </div>
    </>
  )
}