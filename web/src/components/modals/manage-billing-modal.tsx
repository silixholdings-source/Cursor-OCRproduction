'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  CreditCard, 
  CheckCircle, 
  AlertTriangle, 
  DollarSign,
  Calendar,
  Zap,
  Shield,
  Users,
  Building2
} from 'lucide-react'

interface ManageBillingModalProps {
  isOpen: boolean
  onClose: () => void
  currentPlan: {
    name: string
    price: number
    period: string
    features: string[]
  }
  onPlanChange?: (newPlan: string) => void
}

const plans = [
  {
    id: 'starter',
    name: 'Starter',
    price: 49,
    period: 'month',
    features: ['Up to 100 invoices/month', 'Basic analytics', 'Email support', 'Standard integrations'],
    popular: false
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 149,
    period: 'month',
    features: ['Up to 1,000 invoices/month', 'Advanced analytics', 'Priority support', 'Custom integrations', 'API access'],
    popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 299,
    period: 'month',
    features: ['Unlimited invoices', 'Advanced analytics', 'Priority support', 'Custom integrations', 'Dedicated support', 'SLA guarantee'],
    popular: false
  }
]

export function ManageBillingModal({ isOpen, onClose, currentPlan, onPlanChange }: ManageBillingModalProps) {
  const [selectedPlan, setSelectedPlan] = useState('')
  const [billingCycle, setBillingCycle] = useState('monthly')
  const [isLoading, setIsLoading] = useState(false)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const [error, setError] = useState('')

  const handlePlanSelect = (planId: string) => {
    setSelectedPlan(planId)
    setError('')
  }

  const handleConfirmChange = async () => {
    if (!selectedPlan) {
      setError('Please select a plan')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Call the plan change handler
      if (onPlanChange) {
        onPlanChange(selectedPlan)
      }
      
      setShowConfirmation(false)
      onClose()
    } catch (err) {
      setError('Failed to update plan. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const selectedPlanData = plans.find(plan => plan.id === selectedPlan)
  const isCurrentPlan = selectedPlan === currentPlan.name.toLowerCase()

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Manage Billing</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Current Plan */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-green-600" />
                Current Plan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold">{currentPlan.name}</h3>
                  <p className="text-2xl font-bold text-blue-600">
                    ${currentPlan.price}
                    <span className="text-lg font-normal text-gray-500">/{currentPlan.period}</span>
                  </p>
                </div>
                <Badge className="bg-green-100 text-green-800">Active</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Billing Cycle */}
          <div>
            <Label className="text-base font-medium">Billing Cycle</Label>
            <Select value={billingCycle} onValueChange={setBillingCycle}>
              <SelectTrigger className="mt-2">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="yearly">Yearly (Save 20%)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Available Plans */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Available Plans</h3>
            <div className="grid md:grid-cols-3 gap-4">
              {plans.map((plan) => (
                <Card 
                  key={plan.id}
                  className={`cursor-pointer transition-all ${
                    selectedPlan === plan.id 
                      ? 'ring-2 ring-blue-500 border-blue-500' 
                      : 'hover:shadow-md'
                  } ${isCurrentPlan ? 'opacity-50 cursor-not-allowed' : ''}`}
                  onClick={() => !isCurrentPlan && handlePlanSelect(plan.id)}
                >
                  <CardHeader className="text-center">
                    {plan.popular && (
                      <Badge className="w-fit mx-auto mb-2 bg-blue-600">Most Popular</Badge>
                    )}
                    <CardTitle className="text-lg">{plan.name}</CardTitle>
                    <div className="text-3xl font-bold text-blue-600">
                      ${billingCycle === 'yearly' ? Math.round(plan.price * 12 * 0.8) : plan.price}
                      <span className="text-lg font-normal text-gray-500">
                        /{billingCycle === 'yearly' ? 'year' : plan.period}
                      </span>
                    </div>
                    {billingCycle === 'yearly' && (
                      <p className="text-sm text-green-600 font-medium">Save 20%</p>
                    )}
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {plan.features.map((feature, index) => (
                        <li key={index} className="flex items-start text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Selected Plan Summary */}
          {selectedPlanData && !isCurrentPlan && (
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-lg">Plan Change Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">{selectedPlanData.name} Plan</h4>
                    <p className="text-sm text-gray-600">
                      {billingCycle === 'yearly' ? 'Annual billing' : 'Monthly billing'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-blue-600">
                      ${billingCycle === 'yearly' ? Math.round(selectedPlanData.price * 12 * 0.8) : selectedPlanData.price}
                      <span className="text-sm font-normal text-gray-500">
                        /{billingCycle === 'yearly' ? 'year' : 'month'}
                      </span>
                    </p>
                    {billingCycle === 'yearly' && (
                      <p className="text-sm text-green-600">Save ${Math.round(selectedPlanData.price * 12 * 0.2)}/year</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          {selectedPlanData && !isCurrentPlan && (
            <Button 
              onClick={() => setShowConfirmation(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg"
            >
              Change Plan
            </Button>
          )}
        </DialogFooter>

        {/* Confirmation Dialog */}
        <Dialog open={showConfirmation} onOpenChange={setShowConfirmation}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Confirm Plan Change</DialogTitle>
            </DialogHeader>
            <div className="py-4">
              <p className="text-gray-600 mb-4">
                Are you sure you want to change to the <strong>{selectedPlanData?.name}</strong> plan?
              </p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <span>New monthly cost:</span>
                  <span className="font-semibold">
                    ${billingCycle === 'yearly' ? Math.round(selectedPlanData?.price! * 12 * 0.8 / 12) : selectedPlanData?.price}
                  </span>
                </div>
                <div className="flex justify-between items-center text-sm text-gray-600 mt-1">
                  <span>Billing cycle:</span>
                  <span>{billingCycle === 'yearly' ? 'Annual' : 'Monthly'}</span>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowConfirmation(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleConfirmChange}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg"
              >
                {isLoading ? 'Updating...' : 'Confirm Change'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </DialogContent>
    </Dialog>
  )
}

















