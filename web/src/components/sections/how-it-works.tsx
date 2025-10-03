'use client'

import { Badge } from '@/components/ui/badge'
import { 
  Upload, 
  Brain, 
  Workflow, 
  CheckCircle, 
  Database,
  ArrowRight
} from 'lucide-react'

const steps = [
  {
    icon: Upload,
    title: 'Upload Invoice',
    description: 'Drag & drop or scan invoices in any format (PDF, image, paper)',
    details: ['Multi-format support', 'Batch processing', 'Mobile capture', 'Email integration']
  },
  {
    icon: Brain,
    title: 'AI Processing',
    description: 'Advanced OCR extracts data with 99.9% accuracy in seconds',
    details: ['Data extraction', 'Field validation', 'Confidence scoring', 'Learning feedback']
  },
  {
    icon: Workflow,
    title: 'Smart Routing',
    description: 'Intelligent approval workflows based on amount and department',
    details: ['Auto-approval rules', 'Hierarchical routing', 'Delegation support', 'Escalation handling']
  },
  {
    icon: CheckCircle,
    title: 'Review & Approve',
    description: 'Review extracted data and approve with one click',
    details: ['Side-by-side comparison', 'Bulk operations', 'Comment system', 'Audit trail']
  },
  {
    icon: Database,
    title: 'ERP Integration',
    description: 'Seamlessly sync approved invoices to your ERP system',
    details: ['Real-time sync', 'Bidirectional flow', 'Error handling', 'Custom mapping']
  }
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-3xl text-center mb-16">
          <Badge variant="secondary" className="mb-4 px-4 py-2 text-sm">
            <Workflow className="mr-2 h-4 w-4" />
            Simple Workflow
          </Badge>
          <h2 className="mb-6 text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            How It{' '}
            <span className="bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent">
              Works
            </span>
          </h2>
          <p className="text-lg text-muted-foreground">
            From invoice upload to ERP integration in just 5 simple steps. 
            Our AI handles the complexity while you focus on what matters.
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection Line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-brand-200 via-brand-400 to-brand-200 transform -translate-x-1/2 hidden lg:block" />
          
          <div className="space-y-12">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                <div className={`flex items-center gap-8 ${
                  index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'
                } flex-col`}>
                  {/* Content */}
                  <div className={`flex-1 ${index % 2 === 0 ? 'lg:text-right' : 'lg:text-left'} text-center`}>
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-500 to-brand-600 rounded-full text-white shadow-lg mb-6 lg:hidden">
                      <step.icon className="h-8 w-8" />
                    </div>
                    <h3 className="text-2xl font-bold text-foreground mb-4">
                      {index + 1}. {step.title}
                    </h3>
                    <p className="text-lg text-muted-foreground mb-6">
                      {step.description}
                    </p>
                    <ul className="space-y-2">
                      {step.details.map((detail, detailIndex) => (
                        <li key={detailIndex} className="flex items-center text-sm text-muted-foreground">
                          <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                          {detail}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Icon */}
                  <div className="flex-1 flex justify-center">
                    <div className="relative">
                      <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-brand-500 to-brand-600 rounded-full text-white shadow-lg">
                        <step.icon className="h-10 w-10" />
                      </div>
                      <div className="absolute -top-2 -right-2 w-8 h-8 bg-background border-2 border-brand-500 rounded-full flex items-center justify-center text-sm font-bold text-brand-600">
                        {index + 1}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Arrow */}
                {index < steps.length - 1 && (
                  <div className="flex justify-center mt-8 lg:hidden">
                    <ArrowRight className="h-8 w-8 text-brand-400" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <p className="text-lg text-muted-foreground mb-6">
            Ready to streamline your invoice processing?
          </p>
          <Badge variant="outline" className="px-6 py-3 text-base">
            <CheckCircle className="mr-2 h-4 w-4" />
            Get started in minutes
          </Badge>
        </div>
      </div>
    </section>
  )
}
