'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, CheckCircle, Star, Shield } from 'lucide-react'

export function CTA() {
  return (
    <section id="contact" className="py-20 bg-gradient-to-br from-brand-500/10 via-background to-brand-600/10">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <Badge variant="secondary" className="mb-6 px-4 py-2 text-sm">
            <Star className="mr-2 h-4 w-4" />
            Ready to Transform Your Business?
          </Badge>
          
          <h2 className="text-4xl font-bold mb-6">
            Start Your Free Trial Today
          </h2>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join 500+ companies already using AI ERP to streamline their invoice processing. 
            No credit card required. Setup in minutes.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button size="lg" className="group px-8 py-6 text-lg bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg" asChild>
              <Link href="/auth/register">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
            </Button>
            <Button size="lg" className="px-8 py-6 text-lg bg-white text-blue-600 hover:bg-gray-100 border border-blue-600 transition-all duration-200 hover:scale-105 shadow-lg" asChild>
              <Link href="/contact">
                Schedule Demo
              </Link>
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {[
              {
                icon: CheckCircle,
                title: 'No Setup Fees',
                description: 'Start immediately with our free trial'
              },
              {
                icon: Shield,
                title: 'Enterprise Security',
                description: 'SOC 2 Type II certified platform'
              },
              {
                icon: Star,
                title: '24/7 Support',
                description: 'Dedicated customer success team'
              }
            ].map((feature, index) => (
              <div key={index} className="flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-brand-500/10 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-brand-500" />
                </div>
                <h3 className="font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>

          <div className="text-sm text-muted-foreground">
            <p>Trusted by companies like Microsoft, Amazon, and Google</p>
            <div className="flex justify-center items-center gap-8 mt-4 opacity-60">
              <div className="text-2xl font-bold">Microsoft</div>
              <div className="text-2xl font-bold">Amazon</div>
              <div className="text-2xl font-bold">Google</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
