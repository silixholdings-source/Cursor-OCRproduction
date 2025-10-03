'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ManageBillingModal } from '@/components/modals/manage-billing-modal'
import { UpdatePaymentModal } from '@/components/modals/update-payment-modal'
import { downloadInvoice, downloadAllInvoices, downloadBillingSummary } from '@/lib/invoice-download'
import { 
  CreditCard, 
  Download, 
  Calendar, 
  DollarSign, 
  CheckCircle,
  Clock,
  AlertTriangle,
  FileText,
  Settings,
  Plus,
  Loader2
} from 'lucide-react'

export default function BillingPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [showManageBilling, setShowManageBilling] = useState(false)
  const [showUpdatePayment, setShowUpdatePayment] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadType, setDownloadType] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [error, setError] = useState('')

  // Mock billing data
  const billingData = {
    currentPlan: {
      name: 'Enterprise',
      price: 299,
      period: 'month',
      features: ['Unlimited invoices', 'Advanced analytics', 'Priority support', 'Custom integrations'],
      nextBilling: '2024-02-15'
    },
    usage: {
      invoicesProcessed: 1247,
      storageUsed: 2.3,
      storageLimit: 10,
      apiCalls: 45678,
      apiLimit: 100000
    },
    paymentMethod: {
      type: 'card',
      last4: '4242',
      brand: 'Visa',
      expiryMonth: 12,
      expiryYear: 2025
    },
    invoices: [
      {
        id: 'INV-2024-001',
        date: '2024-01-15',
        amount: 299.00,
        status: 'paid',
        description: 'Enterprise Plan - January 2024'
      },
      {
        id: 'INV-2023-012',
        date: '2023-12-15',
        amount: 299.00,
        status: 'paid',
        description: 'Enterprise Plan - December 2023'
      },
      {
        id: 'INV-2023-011',
        date: '2023-11-15',
        amount: 299.00,
        status: 'paid',
        description: 'Enterprise Plan - November 2023'
      }
    ]
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-green-100 text-green-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'failed': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'paid': return 'Paid'
      case 'pending': return 'Pending'
      case 'failed': return 'Failed'
      default: return status
    }
  }

  // Handler functions
  const handleDownloadAllInvoices = async () => {
    setIsDownloading(true)
    setDownloadType('all')
    setError('')
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate processing
      downloadAllInvoices(billingData)
      setSuccessMessage('All invoices downloaded successfully!')
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err) {
      setError('Failed to download invoices. Please try again.')
    } finally {
      setIsDownloading(false)
      setDownloadType('')
    }
  }

  const handleDownloadBillingSummary = async () => {
    setIsDownloading(true)
    setDownloadType('summary')
    setError('')
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate processing
      downloadBillingSummary(billingData)
      setSuccessMessage('Billing summary downloaded successfully!')
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err) {
      setError('Failed to download billing summary. Please try again.')
    } finally {
      setIsDownloading(false)
      setDownloadType('')
    }
  }

  const handleDownloadInvoice = async (invoice: any) => {
    setIsDownloading(true)
    setDownloadType(invoice.id)
    setError('')
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500)) // Simulate processing
      downloadInvoice(invoice)
      setSuccessMessage(`Invoice ${invoice.id} downloaded successfully!`)
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err) {
      setError('Failed to download invoice. Please try again.')
    } finally {
      setIsDownloading(false)
      setDownloadType('')
    }
  }

  const handleManageBilling = () => {
    setShowManageBilling(true)
    setError('')
  }

  const handleUpdatePayment = () => {
    setShowUpdatePayment(true)
    setError('')
  }

  const handlePlanChange = (newPlan: string) => {
    // In a real app, this would update the plan via API
    console.log('Plan changed to:', newPlan)
    setSuccessMessage('Plan updated successfully!')
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  const handlePaymentMethodUpdate = (newMethod: any) => {
    // In a real app, this would update the payment method via API
    console.log('Payment method updated:', newMethod)
    setSuccessMessage('Payment method updated successfully!')
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  return (
    <>
      {/* Success/Error Messages */}
      {successMessage && (
        <Alert className="mb-4 border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{successMessage}</AlertDescription>
        </Alert>
      )}
      
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Billing & Usage</h1>
            <p className="mt-2 text-gray-600">
              Manage your subscription, payment methods, and view usage statistics
            </p>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              className="flex items-center gap-2"
              onClick={handleDownloadAllInvoices}
              disabled={isDownloading && downloadType === 'all'}
            >
              {isDownloading && downloadType === 'all' ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              Download All Invoices
            </Button>
            <Button 
              className="flex items-center gap-2"
              onClick={handleManageBilling}
            >
              <Settings className="h-4 w-4" />
              Manage Billing
            </Button>
          </div>
        </div>
      </div>

      {/* Current Plan Overview */}
      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-medium text-gray-900">Current Plan</h2>
          <Badge className="bg-green-100 text-green-800">Active</Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">{billingData.currentPlan.name}</h3>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              ${billingData.currentPlan.price}
              <span className="text-lg font-normal text-gray-500">/{billingData.currentPlan.period}</span>
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Next billing: {new Date(billingData.currentPlan.nextBilling).toLocaleDateString()}
            </p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Plan Features</h4>
            <ul className="space-y-2">
              {billingData.currentPlan.features.map((feature, index) => (
                <li key={index} className="flex items-center text-sm text-gray-600">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                  {feature}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Usage Statistics */}
      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-medium text-gray-900">Usage Statistics</h2>
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleDownloadBillingSummary}
            disabled={isDownloading && downloadType === 'summary'}
            className="flex items-center gap-2"
          >
            {isDownloading && downloadType === 'summary' ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Download className="h-4 w-4" />
            )}
            Download Summary
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Invoices Processed
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {billingData.usage.invoicesProcessed.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Storage Used
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {billingData.usage.storageUsed} GB / {billingData.usage.storageLimit} GB
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Settings className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    API Calls
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {billingData.usage.apiCalls.toLocaleString()} / {billingData.usage.apiLimit.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Method */}
      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Payment Method</h2>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <CreditCard className="h-8 w-8 text-gray-400 mr-3" />
            <div>
              <div className="text-sm font-medium text-gray-900">
                {billingData.paymentMethod.brand} •••• {billingData.paymentMethod.last4}
              </div>
              <div className="text-sm text-gray-500">
                Expires {billingData.paymentMethod.expiryMonth}/{billingData.paymentMethod.expiryYear}
              </div>
            </div>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleUpdatePayment}
          >
            Update
          </Button>
        </div>
      </div>

      {/* Billing History */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Billing History</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {billingData.invoices.map((invoice) => (
                <tr key={invoice.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {invoice.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                      {new Date(invoice.date).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {invoice.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 text-gray-400 mr-1" />
                      {invoice.amount.toFixed(2)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge className={getStatusColor(invoice.status)}>
                      {getStatusText(invoice.status)}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleDownloadInvoice(invoice)}
                      disabled={isDownloading && downloadType === invoice.id}
                      title="Download invoice"
                    >
                      {isDownloading && downloadType === invoice.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Download className="h-4 w-4" />
                      )}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modals */}
      <ManageBillingModal
        isOpen={showManageBilling}
        onClose={() => setShowManageBilling(false)}
        currentPlan={billingData.currentPlan}
        onPlanChange={handlePlanChange}
      />

      <UpdatePaymentModal
        isOpen={showUpdatePayment}
        onClose={() => setShowUpdatePayment(false)}
        currentPaymentMethod={billingData.paymentMethod}
        onPaymentMethodUpdate={handlePaymentMethodUpdate}
      />
    </>
  )
}