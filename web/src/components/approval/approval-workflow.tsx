'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  User,
  ArrowRight,
  Settings,
  Zap
} from 'lucide-react'

interface WorkflowStep {
  id: string
  name: string
  type: 'approval' | 'notification' | 'auto'
  approver?: string
  status: 'pending' | 'completed' | 'skipped' | 'rejected'
  completedAt?: string
  completedBy?: string
  comment?: string
  order: number
}

interface ApprovalWorkflowProps {
  workflowId: string
  steps: WorkflowStep[]
  currentStep: number
  onStepComplete: (stepId: string, action: 'approve' | 'reject', comment?: string) => void
  onStepSkip: (stepId: string) => void
  canApprove: boolean
}

export function ApprovalWorkflow({
  workflowId,
  steps,
  currentStep,
  onStepComplete,
  onStepSkip,
  canApprove
}: ApprovalWorkflowProps) {
  const [selectedStep, setSelectedStep] = useState<string | null>(null)
  const [comment, setComment] = useState('')

  const getStepIcon = (step: WorkflowStep) => {
    switch (step.type) {
      case 'approval':
        return step.status === 'completed' ? CheckCircle : 
               step.status === 'rejected' ? XCircle : Clock
      case 'notification':
        return User
      case 'auto':
        return Zap
      default:
        return Clock
    }
  }

  const getStepColor = (step: WorkflowStep) => {
    switch (step.status) {
      case 'completed':
        return 'text-green-600 bg-green-100'
      case 'rejected':
        return 'text-red-600 bg-red-100'
      case 'skipped':
        return 'text-gray-400 bg-gray-100'
      default:
        return 'text-yellow-600 bg-yellow-100'
    }
  }

  const handleStepAction = (stepId: string, action: 'approve' | 'reject') => {
    onStepComplete(stepId, action, comment)
    setComment('')
    setSelectedStep(null)
  }

  const handleStepSkip = (stepId: string) => {
    onStepSkip(stepId)
    setSelectedStep(null)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Settings className="h-5 w-5 mr-2" />
          Approval Workflow
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {steps.map((step, index) => {
            const Icon = getStepIcon(step)
            const isCurrentStep = index === currentStep
            const isCompleted = step.status === 'completed'
            const isRejected = step.status === 'rejected'
            const isSkipped = step.status === 'skipped'

            return (
              <div key={step.id} className="relative">
                {/* Connection Line */}
                {index < steps.length - 1 && (
                  <div className="absolute left-6 top-12 w-0.5 h-8 bg-gray-200" />
                )}

                <div className={`flex items-start space-x-4 p-4 rounded-lg border ${
                  isCurrentStep ? 'border-blue-200 bg-blue-50' : 
                  isCompleted ? 'border-green-200 bg-green-50' :
                  isRejected ? 'border-red-200 bg-red-50' :
                  'border-gray-200 bg-white'
                }`}>
                  {/* Step Icon */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${getStepColor(step)}`}>
                    <Icon className="h-6 w-6" />
                  </div>

                  {/* Step Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          {step.name}
                        </h4>
                        {step.approver && (
                          <p className="text-sm text-gray-600">
                            Assigned to: {step.approver}
                          </p>
                        )}
                        {step.completedAt && step.completedBy && (
                          <p className="text-xs text-gray-500">
                            {step.status === 'completed' ? 'Approved' : 'Rejected'} by {step.completedBy} • 
                            {new Date(step.completedAt).toLocaleString()}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStepColor(step)}>
                          {step.status.toUpperCase()}
                        </Badge>
                        {isCurrentStep && canApprove && step.type === 'approval' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedStep(step.id)}
                          >
                            Review
                          </Button>
                        )}
                      </div>
                    </div>

                    {step.comment && (
                      <div className="mt-2 p-2 bg-gray-100 rounded text-sm text-gray-700">
                        {step.comment}
                      </div>
                    )}
                  </div>
                </div>

                {/* Step Actions Modal */}
                {selectedStep === step.id && (
                  <div className="mt-4 p-4 border rounded-lg bg-gray-50">
                    <h5 className="text-sm font-medium text-gray-900 mb-3">
                      Review Step: {step.name}
                    </h5>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Comment (Optional)
                        </label>
                        <textarea
                          value={comment}
                          onChange={(e) => setComment(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          rows={3}
                          placeholder="Add a comment about this step..."
                        />
                      </div>
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedStep(null)}
                        >
                          Cancel
                        </Button>
                        {step.type === 'approval' && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleStepSkip(step.id)}
                              className="text-gray-600"
                            >
                              Skip
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleStepAction(step.id, 'reject')}
                              className="text-red-600 hover:text-red-700"
                            >
                              <XCircle className="h-4 w-4 mr-1" />
                              Reject
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => handleStepAction(step.id, 'approve')}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Approve
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Workflow Summary */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              Progress: {steps.filter(s => s.status === 'completed').length} of {steps.length} steps completed
            </span>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">
                Current Step: {currentStep + 1} of {steps.length}
              </span>
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.round(((currentStep + 1) / steps.length) * 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
