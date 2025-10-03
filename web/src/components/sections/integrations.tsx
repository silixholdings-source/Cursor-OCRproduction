'use client'

import { Badge } from '@/components/ui/badge'
import { 
  Building2, 
  Database, 
  Cloud, 
  Zap, 
  CheckCircle,
  ArrowRight,
  ExternalLink
} from 'lucide-react'

const integrations = [
  {
    name: 'SAP',
    description: 'Seamless integration with SAP S/4HANA and SAP Business One',
    icon: Database,
    category: 'ERP',
    status: 'Available'
  },
  {
    name: 'Oracle NetSuite',
    description: 'Native integration with Oracle NetSuite ERP',
    icon: Cloud,
    category: 'ERP',
    status: 'Available'
  },
  {
    name: 'Microsoft Dynamics',
    description: 'Deep integration with Microsoft Dynamics 365',
    icon: Building2,
    category: 'ERP',
    status: 'Available'
  },
  {
    name: 'Salesforce',
    description: 'Connect invoice data with Salesforce CRM',
    icon: Zap,
    category: 'CRM',
    status: 'Available'
  },
  {
    name: 'QuickBooks',
    description: 'Sync with QuickBooks Online and Desktop',
    icon: Building2,
    category: 'Accounting',
    status: 'Available'
  },
  {
    name: 'Xero',
    description: 'Real-time sync with Xero accounting software',
    icon: Cloud,
    category: 'Accounting',
    status: 'Available'
  },
  {
    name: 'Workday',
    description: 'Integration with Workday Financial Management',
    icon: Database,
    category: 'HCM',
    status: 'Coming Soon'
  },
  {
    name: 'ServiceNow',
    description: 'Connect with ServiceNow for IT service management',
    icon: Zap,
    category: 'ITSM',
    status: 'Coming Soon'
  }
]

const categories = [
  { name: 'ERP Systems', icon: Database, count: 4 },
  { name: 'Accounting Software', icon: Building2, count: 2 },
  { name: 'CRM Platforms', icon: Cloud, count: 1 },
  { name: 'Custom APIs', icon: Zap, count: 3 }
]

export function Integrations() {
  const handleRequestIntegration = () => {
    window.open('mailto:integrations@ai-erp-saas.com?subject=Custom Integration Request', '_blank')
  }
  
  const handleViewAPIDocs = () => {
    window.open('/dashboard/help/api-docs', '_self')
  }
  
  return (
    <section id="integrations" className="py-20 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-3xl text-center mb-16">
          <Badge variant="secondary" className="mb-4 px-4 py-2 text-sm">
            <Zap className="mr-2 h-4 w-4" />
            Seamless Integrations
          </Badge>
          <h2 className="mb-6 text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            Connect with{' '}
            <span className="bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent">
              Your Existing Systems
            </span>
          </h2>
          <p className="text-lg text-muted-foreground">
            Our platform integrates with over 50+ business applications, 
            ensuring your invoice processing fits seamlessly into your existing workflow.
          </p>
        </div>

        {/* Categories */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {categories.map((category, index) => (
            <div key={index} className="text-center p-6 rounded-lg border bg-card hover:shadow-md transition-shadow">
              <category.icon className="h-8 w-8 text-brand-600 mx-auto mb-3" />
              <h3 className="font-semibold text-foreground mb-1">{category.name}</h3>
              <p className="text-sm text-muted-foreground">{category.count} integrations</p>
            </div>
          ))}
        </div>

        {/* Integrations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {integrations.map((integration, index) => (
            <div
              key={index}
              className="group relative overflow-hidden rounded-lg border bg-card p-6 transition-all hover:shadow-lg hover:shadow-brand-500/10"
            >
              {/* Logo */}
              <div className="mb-4 flex items-center justify-between">
                <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
                  <integration.icon className="h-6 w-6 text-brand-600" />
                </div>
                <Badge 
                  variant={integration.status === 'Available' ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {integration.status}
                </Badge>
              </div>

              {/* Content */}
              <h3 className="mb-2 text-lg font-semibold text-foreground">
                {integration.name}
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                {integration.description}
              </p>

              {/* Category */}
              <div className="flex items-center justify-between">
                <Badge variant="outline" className="text-xs">
                  {integration.category}
                </Badge>
                <ArrowRight className="h-4 w-4 text-brand-600 group-hover:translate-x-1 transition-transform" />
              </div>

              {/* Hover Effect */}
              <div className="absolute inset-0 -z-10 bg-gradient-to-br from-brand-50/50 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
            </div>
          ))}
        </div>

        {/* Custom Integration */}
        <div className="bg-gradient-to-r from-brand-50 to-blue-50 rounded-2xl p-8 text-center">
          <div className="max-w-2xl mx-auto">
            <Zap className="h-12 w-12 text-brand-600 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-foreground mb-4">
              Don't See Your System?
            </h3>
            <p className="text-muted-foreground mb-6">
              We can build custom integrations for any system with our flexible API framework. 
              Our team works with you to ensure seamless connectivity.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={handleRequestIntegration}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-brand-600 hover:bg-brand-700 transition-colors"
              >
                Request Integration
                <ExternalLink className="ml-2 h-4 w-4" />
              </button>
              <button 
                onClick={handleViewAPIDocs}
                className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
              >
                View API Docs
                <ArrowRight className="ml-2 h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Stats */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-brand-600 mb-2">50+</div>
            <div className="text-sm text-muted-foreground">Pre-built Integrations</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-brand-600 mb-2">99.9%</div>
            <div className="text-sm text-muted-foreground">Uptime Guarantee</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-brand-600 mb-2">24/7</div>
            <div className="text-sm text-muted-foreground">Support Available</div>
          </div>
        </div>
      </div>
    </section>
  )
}















