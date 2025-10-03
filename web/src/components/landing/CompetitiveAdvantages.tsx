'use client'

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  DollarSign, 
  Zap, 
  Shield, 
  Smartphone, 
  Clock, 
  Users, 
  CheckCircle, 
  TrendingUp,
  Award,
  Globe,
  Lock,
  Headphones
} from 'lucide-react'

const advantages = [
  {
    icon: DollarSign,
    title: "Up to 60% Cost Savings",
    description: "Our aggressive pricing undercuts major competitors like Bill.com, Tipalti, and Stampli while providing superior features.",
    highlight: "Save $1,000s annually",
    color: "text-green-600"
  },
  {
    icon: Zap,
    title: "AI-Powered Automation",
    description: "Advanced OCR and machine learning algorithms that learn from your data to improve accuracy over time.",
    highlight: "95%+ accuracy rate",
    color: "text-blue-600"
  },
  {
    icon: Clock,
    title: "Lightning Fast Setup",
    description: "Get up and running in minutes, not weeks. Our intuitive interface requires minimal training.",
    highlight: "5-minute setup",
    color: "text-purple-600"
  },
  {
    icon: Shield,
    title: "Enterprise-Grade Security",
    description: "SOC 2 compliant with end-to-end encryption, audit trails, and advanced fraud detection.",
    highlight: "SOC 2 Type II",
    color: "text-red-600"
  },
  {
    icon: Smartphone,
    title: "Mobile-First Design",
    description: "Native mobile apps for iOS and Android with offline capabilities and push notifications.",
    highlight: "Offline approvals",
    color: "text-indigo-600"
  },
  {
    icon: Users,
    title: "Unlimited Scalability",
    description: "From 3 users to 10,000+ users, our platform scales seamlessly with your business growth.",
    highlight: "Unlimited plans",
    color: "text-orange-600"
  }
]

const competitorComparison = [
  {
    feature: "Starting Price",
    aiErp: "$19/month",
    billCom: "$39/month",
    tipalti: "$45/month",
    stampli: "$35/month",
    winner: "aiErp"
  },
  {
    feature: "AI-Powered OCR",
    aiErp: "✅ Included",
    billCom: "❌ Basic",
    tipalti: "❌ Basic", 
    stampli: "✅ Included",
    winner: "aiErp"
  },
  {
    feature: "Mobile App",
    aiErp: "✅ Native iOS/Android",
    billCom: "❌ Web only",
    tipalti: "❌ Limited",
    stampli: "✅ Basic",
    winner: "aiErp"
  },
  {
    feature: "Fraud Detection",
    aiErp: "✅ Advanced AI",
    billCom: "❌ Basic",
    tipalti: "✅ Good",
    stampli: "❌ Basic",
    winner: "aiErp"
  },
  {
    feature: "Three-Way Matching",
    aiErp: "✅ AI-Enhanced",
    billCom: "✅ Standard",
    tipalti: "✅ Standard",
    stampli: "✅ Standard",
    winner: "aiErp"
  },
  {
    feature: "API Access",
    aiErp: "✅ Full REST API",
    billCom: "❌ Limited",
    tipalti: "✅ Good",
    stampli: "❌ Limited",
    winner: "aiErp"
  },
  {
    feature: "White Labeling",
    aiErp: "✅ Available",
    billCom: "❌ Not available",
    tipalti: "❌ Not available",
    stampli: "❌ Not available",
    winner: "aiErp"
  },
  {
    feature: "Setup Time",
    aiErp: "5 minutes",
    billCom: "2-4 weeks",
    tipalti: "1-2 weeks",
    stampli: "1-2 weeks",
    winner: "aiErp"
  }
]

const testimonials = [
  {
    name: "Sarah Johnson",
    company: "TechStart Inc.",
    role: "CFO",
    content: "We saved $2,400 annually compared to Bill.com while getting better features and faster setup.",
    savings: "$2,400/year saved"
  },
  {
    name: "Michael Chen",
    company: "Global Manufacturing Co.",
    role: "AP Manager", 
    content: "The AI-powered fraud detection caught 3 suspicious invoices in our first month. ROI was immediate.",
    savings: "Prevented $15K fraud"
  },
  {
    name: "Emily Rodriguez",
    company: "Retail Chain",
    role: "Finance Director",
    content: "Mobile approvals have been a game-changer. Our team can approve invoices from anywhere.",
    savings: "50% faster approvals"
  }
]

export default function CompetitiveAdvantages() {
  return (
    <div className="py-16 bg-white">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4 bg-green-100 text-green-800">
            <Award className="w-4 h-4 mr-1" />
            Industry Leader
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Why Choose AI ERP SaaS?
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We're not just another invoice automation tool. We're the future of AP automation, 
            built with cutting-edge AI and designed for modern businesses.
          </p>
        </div>

        {/* Advantages Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {advantages.map((advantage, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-lg bg-gray-50 ${advantage.color}`}>
                    <advantage.icon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {advantage.title}
                    </h3>
                    <p className="text-gray-600 mb-3">
                      {advantage.description}
                    </p>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                      {advantage.highlight}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Competitor Comparison Table */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-8">
            Head-to-Head Comparison
          </h3>
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">Feature</th>
                    <th className="px-6 py-4 text-center text-sm font-medium text-blue-600 bg-blue-50">
                      AI ERP SaaS
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-medium text-gray-900">Bill.com</th>
                    <th className="px-6 py-4 text-center text-sm font-medium text-gray-900">Tipalti</th>
                    <th className="px-6 py-4 text-center text-sm font-medium text-gray-900">Stampli</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {competitorComparison.map((row, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        {row.feature}
                      </td>
                      <td className={`px-6 py-4 text-sm text-center ${
                        row.winner === 'aiErp' ? 'text-green-600 font-semibold' : 'text-gray-900'
                      }`}>
                        {row.aiErp}
                        {row.winner === 'aiErp' && <CheckCircle className="w-4 h-4 inline ml-1" />}
                      </td>
                      <td className="px-6 py-4 text-sm text-center text-gray-900">
                        {row.billCom}
                      </td>
                      <td className="px-6 py-4 text-sm text-center text-gray-900">
                        {row.tipalti}
                      </td>
                      <td className="px-6 py-4 text-sm text-center text-gray-900">
                        {row.stampli}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Customer Testimonials */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-8">
            What Our Customers Say
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Users className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="ml-4">
                      <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                      <p className="text-sm text-gray-600">{testimonial.role}</p>
                      <p className="text-sm text-gray-500">{testimonial.company}</p>
                    </div>
                  </div>
                  <p className="text-gray-700 mb-4 italic">"{testimonial.content}"</p>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {testimonial.savings}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="bg-gray-50 rounded-lg p-8">
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Trusted by Industry Leaders
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">10,000+</div>
              <div className="text-sm text-gray-600">Active Users</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">$50M+</div>
              <div className="text-sm text-gray-600">Invoices Processed</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
              <div className="text-sm text-gray-600">Uptime SLA</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
              <div className="text-sm text-gray-600">Support</div>
            </div>
          </div>
        </div>

        {/* Security & Compliance */}
        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-8">
            Enterprise Security & Compliance
          </h3>
          <div className="flex flex-wrap justify-center items-center gap-8">
            <div className="flex items-center space-x-2">
              <Shield className="w-6 h-6 text-green-600" />
              <span className="text-gray-700">SOC 2 Type II</span>
            </div>
            <div className="flex items-center space-x-2">
              <Lock className="w-6 h-6 text-green-600" />
              <span className="text-gray-700">GDPR Compliant</span>
            </div>
            <div className="flex items-center space-x-2">
              <Globe className="w-6 h-6 text-green-600" />
              <span className="text-gray-700">ISO 27001</span>
            </div>
            <div className="flex items-center space-x-2">
              <Headphones className="w-6 h-6 text-green-600" />
              <span className="text-gray-700">24/7 Support</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
