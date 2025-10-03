'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Users, 
  Target, 
  Award, 
  Globe,
  Shield,
  Zap,
  TrendingUp,
  Heart,
  Home
} from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { CTAButton } from '@/components/ui/cta-button'

export default function AboutPage() {
  const team = [
    {
      name: 'Sarah Johnson',
      role: 'CEO & Co-Founder',
      bio: 'Former VP of Engineering at Microsoft with 15+ years in enterprise software.',
      image: '/api/placeholder/150/150'
    },
    {
      name: 'Michael Chen',
      role: 'CTO & Co-Founder',
      bio: 'AI/ML expert with PhD from Stanford, previously at Google DeepMind.',
      image: '/api/placeholder/150/150'
    },
    {
      name: 'Emily Rodriguez',
      role: 'Head of Product',
      bio: 'Product leader with 10+ years building B2B SaaS platforms.',
      image: '/api/placeholder/150/150'
    },
    {
      name: 'David Kim',
      role: 'Head of Engineering',
      bio: 'Full-stack architect specializing in scalable enterprise systems.',
      image: '/api/placeholder/150/150'
    }
  ]

  const values = [
    {
      icon: Shield,
      title: 'Security First',
      description: 'Enterprise-grade security with SOC 2 Type II and ISO 27001 compliance.'
    },
    {
      icon: Zap,
      title: 'Innovation',
      description: 'Cutting-edge AI technology that continuously improves and adapts.'
    },
    {
      icon: Users,
      title: 'Customer Success',
      description: 'Dedicated support team ensuring your success with our platform.'
    },
    {
      icon: Globe,
      title: 'Global Scale',
      description: 'Built to handle enterprise workloads across multiple regions.'
    }
  ]

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
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">About AI ERP SaaS</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We&apos;re revolutionizing enterprise invoice processing with cutting-edge AI technology, 
            helping businesses automate their accounts payable workflows and integrate seamlessly with existing ERP systems.
          </p>
        </div>

        {/* Mission & Vision */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="h-6 w-6 mr-2 text-blue-600" />
                Our Mission
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                To eliminate manual invoice processing and transform how enterprises handle their 
                accounts payable workflows through intelligent automation, reducing errors, 
                saving time, and providing actionable insights that drive business growth.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-6 w-6 mr-2 text-green-600" />
                Our Vision
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                To become the world's leading AI-powered enterprise automation platform, 
                enabling every business to achieve 100% accuracy in financial document processing 
                while reducing operational costs by 80% and processing time by 95%.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Company Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-16">
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="text-3xl font-bold text-blue-600 mb-2">500+</div>
              <div className="text-sm text-gray-600">Enterprise Clients</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="text-3xl font-bold text-green-600 mb-2">99.8%</div>
              <div className="text-sm text-gray-600">Accuracy Rate</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="text-3xl font-bold text-purple-600 mb-2">50M+</div>
              <div className="text-sm text-gray-600">Documents Processed</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="pt-6">
              <div className="text-3xl font-bold text-orange-600 mb-2">95%</div>
              <div className="text-sm text-gray-600">Time Saved</div>
            </CardContent>
          </Card>
        </div>

        {/* Our Values */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">Our Values</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {values.map((value, index) => (
              <Card key={index}>
                <CardHeader className="text-center">
                  <value.icon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                  <CardTitle className="text-lg">{value.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 text-center">{value.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Team Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">Meet Our Team</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {team.map((member, index) => (
              <Card key={index}>
                <CardContent className="pt-6 text-center">
                  <div className="w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <Users className="h-8 w-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{member.name}</h3>
                  <p className="text-sm text-blue-600 mb-3">{member.role}</p>
                  <p className="text-sm text-gray-600">{member.bio}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Awards & Certifications */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">Awards & Certifications</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="text-center">
              <CardHeader>
                <Award className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                <CardTitle className="text-lg">SOC 2 Type II</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Certified for security, availability, and confidentiality controls.
                </p>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardHeader>
                <Shield className="h-12 w-12 text-blue-500 mx-auto mb-4" />
                <CardTitle className="text-lg">ISO 27001</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  International standard for information security management.
                </p>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardHeader>
                <Badge className="bg-green-100 text-green-800 mx-auto mb-4">Best AI Startup 2024</Badge>
                <CardTitle className="text-lg">TechCrunch Award</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">
                  Recognized for innovation in enterprise AI automation.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center bg-blue-50 rounded-lg p-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Transform Your Invoice Processing?</h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Join hundreds of enterprises already using AI ERP SaaS to automate their 
            accounts payable workflows and reduce processing time by 95%.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <CTAButton href="/auth/register" backgroundType="white">
              Start Free Trial
            </CTAButton>
            <CTAButton href="/contact" backgroundType="white">
              Contact Sales
            </CTAButton>
          </div>
        </div>
      </div>
    </div>
  )
}

