'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, TrendingUp, Target, Zap } from 'lucide-react'

export function AIInsightsDashboard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            AI Accuracy Metrics
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">OCR Accuracy</span>
            <Badge variant="secondary" className="bg-green-100 text-green-800">98.5%</Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Fraud Detection</span>
            <Badge variant="secondary" className="bg-blue-100 text-blue-800">96.2%</Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">GL Coding</span>
            <Badge variant="secondary" className="bg-purple-100 text-purple-800">94.8%</Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Vendor Matching</span>
            <Badge variant="secondary" className="bg-orange-100 text-orange-800">97.1%</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            AI Performance Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-green-600" />
                <span className="text-sm">Processing Speed</span>
              </div>
              <span className="text-sm font-medium text-green-600">+15% faster</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-blue-600" />
                <span className="text-sm">Accuracy Improvement</span>
              </div>
              <span className="text-sm font-medium text-blue-600">+2.3% this month</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4 text-purple-600" />
                <span className="text-sm">Model Learning</span>
              </div>
              <span className="text-sm font-medium text-purple-600">Active</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}