'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LinkButton } from '@/components/ui/link-button'
import { CTAButton } from '@/components/ui/cta-button'
import { 
  Brain, 
  Zap, 
  Shield, 
  Smartphone, 
  Database, 
  Workflow, 
  BarChart3, 
  Users, 
  Lock, 
  Globe,
  Headphones,
  Code,
  Palette,
  DollarSign,
  Clock,
  CheckCircle,
  ArrowRight,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'

const featureCategories = [
  {
    id: 'ai-automation',
    name: 'AI & Automation',
    icon: Brain,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50'
  },
  {
    id: 'security-compliance',
    name: 'Security & Compliance',
    icon: Shield,
    color: 'text-red-600',
    bgColor: 'bg-red-50'
  },
  {
    id: 'mobile-offline',
    name: 'Mobile & Offline',
    icon: Smartphone,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50'
  },
  {
    id: 'integrations',
    name: 'Integrations',
    icon: Code,
    color: 'text-green-600',
    bgColor: 'bg-green-50'
  },
  {
    id: 'analytics',
    name: 'Analytics & BI',
    icon: BarChart3,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50'
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    icon: Users,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50'
  }
]

const features = {
  'ai-automation': [
    {
      title: 'AI-Powered OCR',
      description: 'Advanced machine learning algorithms that extract data from invoices with 95%+ accuracy, learning from your specific patterns.',
      highlights: ['95%+ accuracy', 'Multi-language support', 'Handwriting recognition', 'Real-time processing'],
      demo: 'ocr-demo'
    },
    {
      title: 'Intelligent Fraud Detection',
      description: 'AI models that analyze patterns and detect suspicious invoices, duplicate payments, and potential fraud attempts.',
      highlights: ['Pattern analysis', 'Anomaly detection', 'Risk scoring', 'Automated alerts'],
      demo: 'fraud-demo'
    },
    {
      title: 'Smart Three-Way Matching',
      description: 'Automated matching of invoices, purchase orders, and receipts with intelligent exception handling.',
      highlights: ['Auto-matching', 'Exception handling', 'Tolerance rules', 'Approval routing'],
      demo: 'matching-demo'
    },
    {
      title: 'Predictive Analytics',
      description: 'Machine learning models that predict cash flow, identify cost savings opportunities, and optimize payment timing.',
      highlights: ['Cash flow prediction', 'Cost optimization', 'Payment timing', 'Trend analysis'],
      demo: 'analytics-demo'
    }
  ],
  'security-compliance': [
    {
      title: 'SOC 2 Type II Compliance',
      description: 'Enterprise-grade security controls and regular audits to ensure your data is protected at the highest level.',
      highlights: ['SOC 2 Type II', 'Regular audits', 'Security controls', 'Compliance reporting'],
      demo: 'security-demo'
    },
    {
      title: 'End-to-End Encryption',
      description: 'All data is encrypted in transit and at rest using industry-standard AES-256 encryption.',
      highlights: ['AES-256 encryption', 'TLS 1.3', 'Key management', 'Data at rest'],
      demo: 'encryption-demo'
    },
    {
      title: 'Advanced Audit Trails',
      description: 'Comprehensive logging of all user actions, system changes, and data access for complete transparency.',
      highlights: ['Complete audit logs', 'User activity tracking', 'Change history', 'Compliance reporting'],
      demo: 'audit-demo'
    },
    {
      title: 'Role-Based Access Control',
      description: 'Granular permissions system that ensures users only access the data and features they need.',
      highlights: ['Granular permissions', 'Role management', 'Access reviews', 'Multi-factor auth'],
      demo: 'rbac-demo'
    }
  ],
  'mobile-offline': [
    {
      title: 'Native Mobile Apps',
      description: 'Full-featured iOS and Android apps with offline capabilities, camera integration, and push notifications.',
      highlights: ['iOS & Android', 'Offline mode', 'Camera integration', 'Push notifications'],
      demo: 'mobile-demo'
    },
    {
      title: 'Offline Invoice Approval',
      description: 'Approve invoices even when offline. Changes sync automatically when connectivity is restored.',
      highlights: ['Offline approvals', 'Auto-sync', 'Conflict resolution', 'Data integrity'],
      demo: 'offline-demo'
    },
    {
      title: 'Mobile Camera OCR',
      description: 'Capture invoices directly with your mobile camera and process them instantly using AI.',
      highlights: ['Camera capture', 'Instant OCR', 'Quality optimization', 'Batch processing'],
      demo: 'camera-demo'
    },
    {
      title: 'Real-time Notifications',
      description: 'Get instant notifications for approvals, rejections, and important updates across all devices.',
      highlights: ['Real-time alerts', 'Multi-device sync', 'Custom notifications', 'Priority levels'],
      demo: 'notifications-demo'
    }
  ],
  'integrations': [
    {
      title: 'ERP System Integration',
      description: 'Seamless integration with major ERP systems including SAP, Oracle, Microsoft Dynamics, and more.',
      highlights: ['SAP integration', 'Oracle support', 'Dynamics 365', 'Custom connectors'],
      demo: 'erp-demo'
    },
    {
      title: 'RESTful API',
      description: 'Comprehensive API for custom integrations, webhooks, and third-party application connectivity.',
      highlights: ['REST API', 'Webhooks', 'SDK libraries', 'API documentation'],
      demo: 'api-demo'
    },
    {
      title: 'Accounting Software',
      description: 'Direct integration with QuickBooks, Xero, Sage, and other popular accounting platforms.',
      highlights: ['QuickBooks', 'Xero', 'Sage', 'Real-time sync'],
      demo: 'accounting-demo'
    },
    {
      title: 'White Label Solutions',
      description: 'Rebrand the platform with your company\'s branding and integrate it into your existing systems.',
      highlights: ['Custom branding', 'White label', 'Embedded solutions', 'Custom domains'],
      demo: 'white-label-demo'
    }
  ],
  'analytics': [
    {
      title: 'Real-time Dashboard',
      description: 'Comprehensive dashboards with real-time insights into your AP processes and performance metrics.',
      highlights: ['Real-time data', 'Custom dashboards', 'KPI tracking', 'Performance metrics'],
      demo: 'dashboard-demo'
    },
    {
      title: 'Advanced Reporting',
      description: 'Generate detailed reports on spending patterns, vendor performance, and process efficiency.',
      highlights: ['Custom reports', 'Scheduled reports', 'Data export', 'Visualization'],
      demo: 'reporting-demo'
    },
    {
      title: 'Predictive Analytics',
      description: 'AI-powered insights that help predict cash flow, identify cost savings, and optimize processes.',
      highlights: ['Cash flow prediction', 'Cost optimization', 'Trend analysis', 'Forecasting'],
      demo: 'predictive-demo'
    },
    {
      title: 'Compliance Reporting',
      description: 'Automated compliance reports for audits, regulatory requirements, and internal controls.',
      highlights: ['Audit reports', 'Compliance tracking', 'Regulatory reports', 'Automated generation'],
      demo: 'compliance-demo'
    }
  ],
  'enterprise': [
    {
      title: 'Multi-tenant Architecture',
      description: 'Secure, scalable architecture that supports multiple companies with complete data isolation.',
      highlights: ['Data isolation', 'Scalable architecture', 'Tenant management', 'Resource allocation'],
      demo: 'multi-tenant-demo'
    },
    {
      title: 'SSO Integration',
      description: 'Single sign-on integration with Active Directory, SAML, and other enterprise identity providers.',
      highlights: ['Active Directory', 'SAML support', 'OAuth 2.0', 'Identity federation'],
      demo: 'sso-demo'
    },
    {
      title: 'Dedicated Support',
      description: '24/7 dedicated support with account managers, priority response times, and custom training.',
      highlights: ['24/7 support', 'Account managers', 'Priority response', 'Custom training'],
      demo: 'support-demo'
    },
    {
      title: 'Custom Workflows',
      description: 'Design custom approval workflows that match your organization\'s specific business processes.',
      highlights: ['Custom workflows', 'Approval chains', 'Conditional logic', 'Process automation'],
      demo: 'workflow-demo'
    }
  ]
}

const demos = {
  'ocr-demo': {
    title: 'AI-Powered OCR Demo',
    description: 'See how our AI extracts data from invoices with 95%+ accuracy',
    steps: [
      'Upload invoice image',
      'AI processes and extracts data',
      'Review and validate results',
      'Export to your ERP system'
    ]
  },
  'fraud-demo': {
    title: 'Fraud Detection Demo',
    description: 'Watch our AI identify suspicious patterns and potential fraud',
    steps: [
      'AI analyzes invoice patterns',
      'Identifies anomalies and risks',
      'Generates risk scores',
      'Sends alerts for review'
    ]
  },
  'mobile-demo': {
    title: 'Mobile App Demo',
    description: 'Experience our native mobile apps with offline capabilities',
    steps: [
      'Download mobile app',
      'Capture invoice with camera',
      'Approve offline',
      'Sync when online'
    ]
  }
}

export default function AdvancedFeatures() {
  const [activeCategory, setActiveCategory] = useState('ai-automation')
  const [activeDemo, setActiveDemo] = useState<string | null>(null)

  return (
    <div className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4 bg-blue-100 text-blue-800">
            <Zap className="w-4 h-4 mr-1" />
            Advanced Features
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Enterprise-Grade Capabilities
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Built for modern businesses with cutting-edge technology, 
            comprehensive security, and seamless integrations.
          </p>
        </div>

        {/* Category Tabs */}
        <div className="flex flex-wrap justify-center gap-4 mb-12">
          {featureCategories.map((category) => (
            <Button
              key={category.id}
              variant={activeCategory === category.id ? 'default' : 'outline'}
              onClick={() => setActiveCategory(category.id)}
              className={`flex items-center space-x-2 ${
                activeCategory === category.id 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <category.icon className="w-4 h-4" />
              <span>{category.name}</span>
            </Button>
          ))}
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {features[activeCategory as keyof typeof features]?.map((feature, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2">{feature.title}</CardTitle>
                    <p className="text-gray-600">{feature.description}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setActiveDemo(feature.demo)}
                    className="ml-4"
                  >
                    <Play className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {feature.highlights.map((highlight, idx) => (
                    <div key={idx} className="flex items-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm text-gray-700">{highlight}</span>
                    </div>
                  ))}
                </div>
                <Button 
                  variant="outline" 
                  className="w-full mt-4"
                  onClick={() => setActiveDemo(feature.demo)}
                >
                  View Demo
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Demo Modal */}
        {activeDemo && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-2xl mx-4">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>{demos[activeDemo as keyof typeof demos]?.title}</CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setActiveDemo(null)}
                  >
                    <Pause className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-gray-600">{demos[activeDemo as keyof typeof demos]?.description}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {demos[activeDemo as keyof typeof demos]?.steps.map((step, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-semibold text-blue-600">{index + 1}</span>
                      </div>
                      <span className="text-gray-700">{step}</span>
                    </div>
                  ))}
                </div>
                <div className="flex space-x-4 mt-6">
                  <Button className="flex-1">
                    <Play className="w-4 h-4 mr-2" />
                    Start Demo
                  </Button>
                  <Button variant="outline" onClick={() => setActiveDemo(null)}>
                    Close
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Feature Highlights */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-16">
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Why Our Features Matter
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Save Time</h4>
              <p className="text-gray-600">
                Reduce invoice processing time by 80% with AI-powered automation
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <DollarSign className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Save Money</h4>
              <p className="text-gray-600">
                Cut costs by 60% compared to traditional invoice processing
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Stay Secure</h4>
              <p className="text-gray-600">
                Enterprise-grade security with SOC 2 compliance and encryption
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-blue-600 rounded-lg p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Experience These Features?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Start your free trial today and see the difference AI can make
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <CTAButton href="/auth/register" backgroundType="blue">
              Start Free Trial
            </CTAButton>
            <CTAButton href="/contact" backgroundType="blue">
              Schedule Demo
            </CTAButton>
          </div>
        </div>
      </div>
    </div>
  )
}
