'use client'

import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Brain, 
  FileText, 
  Workflow, 
  Zap, 
  Shield, 
  BarChart3, 
  Globe, 
  Lock,
  CheckCircle,
  ArrowRight,
  X,
  ExternalLink,
  Clock,
  Users,
  TrendingUp,
  Target
} from 'lucide-react'

const features = [
  {
    id: 'ai-ocr',
    icon: Brain,
    title: 'AI-Powered OCR',
    description: 'Advanced machine learning extracts data with 99.9% accuracy from any invoice format',
    benefits: ['Multi-language support', 'Handwritten text recognition', 'Table extraction', 'Continuous learning'],
    color: 'from-blue-500 to-cyan-500',
    detailedInfo: {
      whatItDoes: 'Our AI-powered OCR technology uses advanced machine learning algorithms to automatically extract data from invoices, receipts, and other financial documents with 99.9% accuracy.',
      keyCapabilities: [
        'Processes 50+ languages including English, Spanish, French, German, Chinese, and Japanese',
        'Recognizes handwritten text and signatures with 95%+ accuracy',
        'Extracts data from complex tables and multi-column layouts',
        'Learns from corrections to improve accuracy over time',
        'Handles various file formats: PDF, JPG, PNG, TIFF, and scanned documents'
      ],
      businessImpact: [
        'Reduces manual data entry by 95%',
        'Eliminates human errors in data extraction',
        'Processes invoices 10x faster than manual methods',
        'Supports global operations with multi-language processing',
        'Saves 20+ hours per week for AP teams'
      ],
      useCases: [
        'High-volume invoice processing for large enterprises',
        'Multi-language document processing for global companies',
        'Handwritten invoice processing for small businesses',
        'Complex table extraction from detailed invoices',
        'Automated data validation and error detection'
      ]
    }
  },
  {
    id: 'smart-workflows',
    icon: Workflow,
    title: 'Smart Approval Workflows',
    description: 'Intelligent routing based on amount, department, and approval hierarchy',
    benefits: ['Multi-step approvals', 'Delegation support', 'Out-of-office routing', 'Escalation rules'],
    color: 'from-green-500 to-emerald-500',
    detailedInfo: {
      whatItDoes: 'Our smart approval workflow engine automatically routes invoices through the appropriate approval chain based on predefined rules, amounts, departments, and approval hierarchies.',
      keyCapabilities: [
        'Configurable approval rules based on amount thresholds',
        'Department-specific routing and approval chains',
        'Automatic delegation when approvers are unavailable',
        'Escalation rules for overdue approvals',
        'Integration with existing organizational hierarchies'
      ],
      businessImpact: [
        'Reduces approval time by 70%',
        'Eliminates bottlenecks in approval processes',
        'Ensures compliance with company policies',
        'Provides full audit trail for all approvals',
        'Reduces approval errors by 90%'
      ],
      useCases: [
        'Large enterprise approval processes',
        'Multi-department invoice routing',
        'Compliance-driven approval workflows',
        'Emergency approval escalations',
        'Vendor-specific approval requirements'
      ]
    }
  },
  {
    id: 'erp-integration',
    icon: Globe,
    title: 'Multi-ERP Integration',
    description: 'Seamlessly connect with Microsoft Dynamics, Sage, Xero, QuickBooks, and more',
    benefits: ['Universal adapter framework', 'Real-time sync', 'Bidirectional data flow', 'Custom connectors'],
    color: 'from-purple-500 to-pink-500',
    detailedInfo: {
      whatItDoes: 'Our universal ERP integration platform connects seamlessly with all major ERP systems, providing real-time data synchronization and bidirectional data flow.',
      keyCapabilities: [
        'Pre-built connectors for 20+ ERP systems',
        'Real-time data synchronization',
        'Bidirectional data flow between systems',
        'Custom connector development for unique systems',
        'Data mapping and transformation tools'
      ],
      businessImpact: [
        'Eliminates manual data entry between systems',
        'Reduces integration costs by 80%',
        'Provides real-time visibility across systems',
        'Eliminates data inconsistencies',
        'Speeds up implementation by 60%'
      ],
      useCases: [
        'SAP to QuickBooks integration',
        'Microsoft Dynamics 365 synchronization',
        'Sage Intacct data flow',
        'Custom ERP system integration',
        'Multi-ERP environment management'
      ]
    }
  },
  {
    id: 'three-way-match',
    icon: Zap,
    title: '3-Way Match Automation',
    description: 'Automatically match invoices with purchase orders and receipts',
    benefits: ['PO matching', 'Receipt validation', 'Discrepancy detection', 'Exception handling'],
    color: 'from-orange-500 to-red-500',
    detailedInfo: {
      whatItDoes: 'Our 3-way match automation system automatically matches invoices with purchase orders and receipts, detecting discrepancies and handling exceptions intelligently.',
      keyCapabilities: [
        'Automatic PO matching with 98% accuracy',
        'Receipt validation and verification',
        'Discrepancy detection and flagging',
        'Exception handling and resolution workflows',
        'Tolerance-based matching rules'
      ],
      businessImpact: [
        'Reduces matching time by 85%',
        'Eliminates manual matching errors',
        'Speeds up payment processing',
        'Reduces exception handling time by 70%',
        'Improves cash flow management'
      ],
      useCases: [
        'High-volume invoice matching',
        'Complex multi-line PO matching',
        'Receipt validation and verification',
        'Exception handling and resolution',
        'Compliance-driven matching processes'
      ]
    }
  },
  {
    id: 'enterprise-security',
    icon: Shield,
    title: 'Enterprise Security',
    description: 'Bank-level encryption, SOC 2 compliance, and role-based access control',
    benefits: ['End-to-end encryption', 'Audit trails', 'GDPR compliance', 'SSO integration'],
    color: 'from-indigo-500 to-blue-500',
    detailedInfo: {
      whatItDoes: 'Our enterprise-grade security platform provides bank-level encryption, comprehensive audit trails, and compliance with major security standards including SOC 2, GDPR, and HIPAA.',
      keyCapabilities: [
        'AES-256 encryption for data at rest and in transit',
        'SOC 2 Type II compliance certification',
        'GDPR and HIPAA compliance features',
        'Single Sign-On (SSO) integration',
        'Comprehensive audit trails and logging'
      ],
      businessImpact: [
        'Meets enterprise security requirements',
        'Reduces security audit preparation time by 90%',
        'Ensures compliance with data protection regulations',
        'Provides peace of mind for sensitive financial data',
        'Reduces security-related risks and liabilities'
      ],
      useCases: [
        'Financial services compliance',
        'Healthcare data protection',
        'Government contractor requirements',
        'International data protection compliance',
        'Enterprise security audit preparation'
      ]
    }
  },
  {
    id: 'advanced-analytics',
    icon: BarChart3,
    title: 'Advanced Analytics',
    description: 'Real-time insights into AP performance, vendor analysis, and cost optimization',
    benefits: ['Custom dashboards', 'Predictive analytics', 'Vendor scoring', 'Cost tracking'],
    color: 'from-teal-500 to-green-500',
    detailedInfo: {
      whatItDoes: 'Our advanced analytics platform provides real-time insights into accounts payable performance, vendor analysis, and cost optimization opportunities through AI-powered predictive analytics.',
      keyCapabilities: [
        'Real-time AP performance dashboards',
        'Predictive analytics for cash flow forecasting',
        'Vendor performance scoring and analysis',
        'Cost optimization recommendations',
        'Custom report generation and scheduling'
      ],
      businessImpact: [
        'Improves cash flow visibility by 100%',
        'Reduces costs through optimization insights',
        'Enhances vendor relationship management',
        'Provides data-driven decision making',
        'Increases AP team productivity by 40%'
      ],
      useCases: [
        'AP performance monitoring and optimization',
        'Vendor relationship management',
        'Cash flow forecasting and planning',
        'Cost reduction and optimization',
        'Executive reporting and dashboards'
      ]
    }
  }
]

export function Features() {
  const [selectedFeature, setSelectedFeature] = useState<any>(null)
  const [showModal, setShowModal] = useState(false)

  const handleLearnMore = (feature: any) => {
    setSelectedFeature(feature)
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setSelectedFeature(null)
  }

  return (
    <section id="features" className="py-20 bg-muted/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-3xl text-center mb-16">
          <Badge variant="secondary" className="mb-4 px-4 py-2 text-sm">
            <CheckCircle className="mr-2 h-4 w-4" />
            Powerful Features
          </Badge>
          <h2 className="mb-6 text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            Everything You Need for{' '}
            <span className="bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent">
              Modern AP
            </span>
          </h2>
          <p className="text-lg text-muted-foreground">
            Our comprehensive platform combines cutting-edge AI technology with enterprise-grade 
            security to transform your accounts payable process.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative overflow-hidden rounded-2xl border bg-card p-8 transition-all hover:shadow-lg hover:shadow-brand-500/10"
            >
              {/* Icon */}
              <div className={`mb-6 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br ${feature.color} text-white shadow-lg`}>
                <feature.icon className="h-8 w-8" />
              </div>

              {/* Content */}
              <h3 className="mb-3 text-xl font-semibold text-foreground">
                {feature.title}
              </h3>
              <p className="mb-6 text-muted-foreground">
                {feature.description}
              </p>

              {/* Benefits */}
              <ul className="mb-6 space-y-2">
                {feature.benefits.map((benefit, benefitIndex) => (
                  <li key={benefitIndex} className="flex items-center text-sm text-muted-foreground">
                    <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                    {benefit}
                  </li>
                ))}
              </ul>

              {/* Learn More Link */}
              <button 
                onClick={() => handleLearnMore(feature)}
                className="flex items-center text-sm font-medium text-brand-600 group-hover:text-brand-700 transition-colors cursor-pointer hover:underline"
              >
                Learn more
                <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </button>

              {/* Hover Effect */}
              <div className="absolute inset-0 -z-10 bg-gradient-to-br from-brand-50/50 to-transparent opacity-0 transition-opacity group-hover:opacity-100 dark:from-brand-950/50" />
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <p className="mb-6 text-lg text-muted-foreground">
            Ready to see these features in action?
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-6">
            <Badge variant="outline" className="px-6 py-3 text-base">
              <Lock className="mr-2 h-4 w-4" />
              Free 3-day trial
            </Badge>
            <Badge variant="outline" className="px-6 py-3 text-base">
              <Shield className="mr-2 h-4 w-4" />
              No credit card required
            </Badge>
          </div>
        </div>
      </div>

      {/* Feature Detail Modal */}
      {showModal && selectedFeature && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b">
              <div className="flex items-center">
                <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${selectedFeature.color} text-white shadow-lg mr-4`}>
                  <selectedFeature.icon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold">{selectedFeature.title}</h3>
                  <p className="text-muted-foreground">{selectedFeature.description}</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCloseModal}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="space-y-8">
                {/* What It Does */}
                <div>
                  <h4 className="text-lg font-semibold mb-4 flex items-center">
                    <Target className="h-5 w-5 mr-2 text-brand-500" />
                    What It Does
                  </h4>
                  <p className="text-muted-foreground leading-relaxed">
                    {selectedFeature.detailedInfo.whatItDoes}
                  </p>
                </div>

                {/* Key Capabilities */}
                <div>
                  <h4 className="text-lg font-semibold mb-4 flex items-center">
                    <CheckCircle className="h-5 w-5 mr-2 text-green-500" />
                    Key Capabilities
                  </h4>
                  <ul className="space-y-3">
                    {selectedFeature.detailedInfo.keyCapabilities.map((capability: string, index: number) => (
                      <li key={index} className="flex items-start">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-muted-foreground">{capability}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Business Impact */}
                <div>
                  <h4 className="text-lg font-semibold mb-4 flex items-center">
                    <TrendingUp className="h-5 w-5 mr-2 text-blue-500" />
                    Business Impact
                  </h4>
                  <ul className="space-y-3">
                    {selectedFeature.detailedInfo.businessImpact.map((impact: string, index: number) => (
                      <li key={index} className="flex items-start">
                        <TrendingUp className="h-4 w-4 text-blue-500 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-muted-foreground">{impact}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Use Cases */}
                <div>
                  <h4 className="text-lg font-semibold mb-4 flex items-center">
                    <Users className="h-5 w-5 mr-2 text-purple-500" />
                    Use Cases
                  </h4>
                  <ul className="space-y-3">
                    {selectedFeature.detailedInfo.useCases.map((useCase: string, index: number) => (
                      <li key={index} className="flex items-start">
                        <Users className="h-4 w-4 text-purple-500 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-muted-foreground">{useCase}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Stats */}
                <div className="bg-muted/50 rounded-lg p-6">
                  <h4 className="text-lg font-semibold mb-4 flex items-center">
                    <Clock className="h-5 w-5 mr-2 text-orange-500" />
                    Performance Metrics
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-brand-500">99.9%</div>
                      <div className="text-sm text-muted-foreground">Accuracy Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-brand-500">10x</div>
                      <div className="text-sm text-muted-foreground">Faster Processing</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-brand-500">95%</div>
                      <div className="text-sm text-muted-foreground">Time Saved</div>
                    </div>
                  </div>
                </div>

                {/* CTA */}
                <div className="flex justify-center pt-6 border-t">
                  <Button 
                    size="lg" 
                    variant="outline" 
                    className="px-8 py-3"
                    onClick={() => {
                      handleCloseModal()
                      window.location.href = '/contact?inquiryType=demo'
                    }}
                  >
                    Schedule Demo
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
