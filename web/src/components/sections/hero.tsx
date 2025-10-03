'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, Play, Star, Zap, Shield, CheckCircle } from 'lucide-react'

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-background via-background to-muted/20 py-20 sm:py-32">
      {/* Background decoration */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]" />
        <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-brand-400 opacity-20 blur-[100px]" />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          {/* Badge */}
          <Badge variant="secondary" className="mb-6 px-4 py-2 text-sm">
            <Zap className="mr-2 h-4 w-4" />
            AI-Powered Invoice Processing
          </Badge>

          {/* Main heading */}
          <h1 className="mb-6 text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
            Transform Your{' '}
            <span className="bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent">
              Accounts Payable
            </span>{' '}
            with AI
          </h1>

          {/* Subheading */}
          <p className="mb-8 text-lg text-muted-foreground sm:text-xl lg:text-2xl">
            Automate invoice processing, approval workflows, and ERP integration with 
            enterprise-grade AI. Reduce processing time by 90% and eliminate manual errors.
          </p>

          {/* CTA Buttons */}
          <div className="mb-12 flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-6">
            <Button size="lg" className="group px-8 py-6 text-lg bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg" asChild>
              <Link href="/auth/register?trial=true&plan=professional">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
            </Button>
            <Button size="lg" className="px-8 py-6 text-lg bg-white text-blue-600 hover:bg-gray-100 border border-blue-600 transition-all duration-200 hover:scale-105 shadow-lg" asChild>
              <Link href="/demo">
                <Play className="mr-2 h-5 w-5" />
                Watch Demo
              </Link>
            </Button>
          </div>

          {/* Trust indicators */}
          <div className="flex flex-col items-center justify-center gap-6 sm:flex-row sm:gap-12">
            <div className="flex items-center gap-2">
              <div className="flex -space-x-1">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="h-8 w-8 rounded-full border-2 border-background bg-muted"
                  />
                ))}
              </div>
              <span className="text-sm text-muted-foreground">
                Trusted by 500+ companies
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <span className="text-sm text-muted-foreground">
                4.9/5 rating
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-500" />
              <span className="text-sm text-muted-foreground">
                SOC 2 Type II Certified
              </span>
            </div>
          </div>
        </div>

        {/* Features preview */}
        <div className="mt-20 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[
            {
              icon: Zap,
              title: '90% Faster',
              description: 'Process invoices in minutes, not days',
            },
            {
              icon: CheckCircle,
              title: '99.9% Accuracy',
              description: 'AI-powered OCR with human-level precision',
            },
            {
              icon: Shield,
              title: 'Enterprise Security',
              description: 'Bank-level encryption and compliance',
            },
            {
              icon: ArrowRight,
              title: 'Seamless Integration',
              description: 'Connect with any ERP system',
            },
          ].map((feature, index) => (
            <div
              key={index}
              className="group rounded-xl border bg-card p-6 text-center transition-all hover:border-brand-200 hover:shadow-lg dark:hover:border-brand-800"
            >
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-brand-100 text-brand-600 transition-colors group-hover:bg-brand-200 dark:bg-brand-900 dark:text-brand-400 dark:group-hover:bg-brand-800">
                <feature.icon className="h-6 w-6" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">
                {feature.title}
              </h3>
              <p className="text-sm text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
