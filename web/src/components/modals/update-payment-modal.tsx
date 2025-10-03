'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CreditCard, CheckCircle, AlertTriangle, Lock } from 'lucide-react'

interface UpdatePaymentModalProps {
  isOpen: boolean
  onClose: () => void
  currentPaymentMethod: {
    type: string
    last4: string
    brand: string
    expiryMonth: number
    expiryYear: number
  }
  onPaymentMethodUpdate?: (newMethod: any) => void
}

export function UpdatePaymentModal({ 
  isOpen, 
  onClose, 
  currentPaymentMethod, 
  onPaymentMethodUpdate 
}: UpdatePaymentModalProps) {
  const [formData, setFormData] = useState({
    cardNumber: '',
    expiryMonth: '',
    expiryYear: '',
    cvv: '',
    cardholderName: '',
    billingAddress: '',
    city: '',
    state: '',
    zipCode: '',
    country: 'US'
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [showSuccess, setShowSuccess] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    setError('')
  }

  const formatCardNumber = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '')
    const matches = v.match(/\d{4,16}/g)
    const match = matches && matches[0] || ''
    const parts = []
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4))
    }
    if (parts.length) {
      return parts.join(' ')
    } else {
      return v
    }
  }

  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCardNumber(e.target.value)
    setFormData(prev => ({ ...prev, cardNumber: formatted }))
  }

  const getCardBrand = (cardNumber: string) => {
    const number = cardNumber.replace(/\s/g, '')
    if (number.startsWith('4')) return 'Visa'
    if (number.startsWith('5') || number.startsWith('2')) return 'Mastercard'
    if (number.startsWith('3')) return 'American Express'
    return 'Unknown'
  }

  const validateForm = () => {
    if (!formData.cardNumber || formData.cardNumber.replace(/\s/g, '').length < 13) {
      setError('Please enter a valid card number')
      return false
    }
    if (!formData.expiryMonth || !formData.expiryYear) {
      setError('Please select expiry month and year')
      return false
    }
    if (!formData.cvv || formData.cvv.length < 3) {
      setError('Please enter a valid CVV')
      return false
    }
    if (!formData.cardholderName.trim()) {
      setError('Please enter cardholder name')
      return false
    }
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setIsLoading(true)
    setError('')

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const newPaymentMethod = {
        type: 'card',
        last4: formData.cardNumber.slice(-4),
        brand: getCardBrand(formData.cardNumber),
        expiryMonth: parseInt(formData.expiryMonth),
        expiryYear: parseInt(formData.expiryYear)
      }
      
      if (onPaymentMethodUpdate) {
        onPaymentMethodUpdate(newPaymentMethod)
      }
      
      setShowSuccess(true)
      setTimeout(() => {
        setShowSuccess(false)
        onClose()
      }, 2000)
    } catch (err) {
      setError('Failed to update payment method. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const monthOptions = Array.from({ length: 12 }, (_, i) => {
    const month = i + 1
    return { value: month.toString(), label: month.toString().padStart(2, '0') }
  })

  const yearOptions = Array.from({ length: 10 }, (_, i) => {
    const year = new Date().getFullYear() + i
    return { value: year.toString(), label: year.toString() }
  })

  // All countries sorted alphabetically by name
  const allCountries = [
    { value: 'AF', label: 'Afghanistan' },
    { value: 'AL', label: 'Albania' },
    { value: 'DZ', label: 'Algeria' },
    { value: 'AD', label: 'Andorra' },
    { value: 'AO', label: 'Angola' },
    { value: 'AG', label: 'Antigua and Barbuda' },
    { value: 'AR', label: 'Argentina' },
    { value: 'AM', label: 'Armenia' },
    { value: 'AU', label: 'Australia' },
    { value: 'AT', label: 'Austria' },
    { value: 'AZ', label: 'Azerbaijan' },
    { value: 'BS', label: 'Bahamas' },
    { value: 'BH', label: 'Bahrain' },
    { value: 'BD', label: 'Bangladesh' },
    { value: 'BB', label: 'Barbados' },
    { value: 'BY', label: 'Belarus' },
    { value: 'BE', label: 'Belgium' },
    { value: 'BZ', label: 'Belize' },
    { value: 'BJ', label: 'Benin' },
    { value: 'BT', label: 'Bhutan' },
    { value: 'BO', label: 'Bolivia' },
    { value: 'BA', label: 'Bosnia and Herzegovina' },
    { value: 'BW', label: 'Botswana' },
    { value: 'BR', label: 'Brazil' },
    { value: 'BN', label: 'Brunei' },
    { value: 'BG', label: 'Bulgaria' },
    { value: 'BF', label: 'Burkina Faso' },
    { value: 'BI', label: 'Burundi' },
    { value: 'KH', label: 'Cambodia' },
    { value: 'CM', label: 'Cameroon' },
    { value: 'CA', label: 'Canada' },
    { value: 'CV', label: 'Cape Verde' },
    { value: 'CF', label: 'Central African Republic' },
    { value: 'TD', label: 'Chad' },
    { value: 'CL', label: 'Chile' },
    { value: 'CN', label: 'China' },
    { value: 'CO', label: 'Colombia' },
    { value: 'KM', label: 'Comoros' },
    { value: 'CG', label: 'Republic of the Congo' },
    { value: 'CD', label: 'Democratic Republic of the Congo' },
    { value: 'CR', label: 'Costa Rica' },
    { value: 'CI', label: 'Côte d\'Ivoire' },
    { value: 'HR', label: 'Croatia' },
    { value: 'CU', label: 'Cuba' },
    { value: 'CY', label: 'Cyprus' },
    { value: 'CZ', label: 'Czech Republic' },
    { value: 'DK', label: 'Denmark' },
    { value: 'DJ', label: 'Djibouti' },
    { value: 'DM', label: 'Dominica' },
    { value: 'DO', label: 'Dominican Republic' },
    { value: 'EC', label: 'Ecuador' },
    { value: 'EG', label: 'Egypt' },
    { value: 'SV', label: 'El Salvador' },
    { value: 'GQ', label: 'Equatorial Guinea' },
    { value: 'ER', label: 'Eritrea' },
    { value: 'EE', label: 'Estonia' },
    { value: 'ET', label: 'Ethiopia' },
    { value: 'FJ', label: 'Fiji' },
    { value: 'FI', label: 'Finland' },
    { value: 'FR', label: 'France' },
    { value: 'GA', label: 'Gabon' },
    { value: 'GM', label: 'Gambia' },
    { value: 'GE', label: 'Georgia' },
    { value: 'DE', label: 'Germany' },
    { value: 'GH', label: 'Ghana' },
    { value: 'GR', label: 'Greece' },
    { value: 'GD', label: 'Grenada' },
    { value: 'GT', label: 'Guatemala' },
    { value: 'GN', label: 'Guinea' },
    { value: 'GW', label: 'Guinea-Bissau' },
    { value: 'GY', label: 'Guyana' },
    { value: 'HT', label: 'Haiti' },
    { value: 'HN', label: 'Honduras' },
    { value: 'HK', label: 'Hong Kong' },
    { value: 'HU', label: 'Hungary' },
    { value: 'IS', label: 'Iceland' },
    { value: 'IN', label: 'India' },
    { value: 'ID', label: 'Indonesia' },
    { value: 'IR', label: 'Iran' },
    { value: 'IQ', label: 'Iraq' },
    { value: 'IE', label: 'Ireland' },
    { value: 'IL', label: 'Israel' },
    { value: 'IT', label: 'Italy' },
    { value: 'JM', label: 'Jamaica' },
    { value: 'JP', label: 'Japan' },
    { value: 'JO', label: 'Jordan' },
    { value: 'KZ', label: 'Kazakhstan' },
    { value: 'KE', label: 'Kenya' },
    { value: 'KI', label: 'Kiribati' },
    { value: 'KP', label: 'North Korea' },
    { value: 'KR', label: 'South Korea' },
    { value: 'KW', label: 'Kuwait' },
    { value: 'KG', label: 'Kyrgyzstan' },
    { value: 'LA', label: 'Laos' },
    { value: 'LV', label: 'Latvia' },
    { value: 'LB', label: 'Lebanon' },
    { value: 'LS', label: 'Lesotho' },
    { value: 'LR', label: 'Liberia' },
    { value: 'LY', label: 'Libya' },
    { value: 'LI', label: 'Liechtenstein' },
    { value: 'LT', label: 'Lithuania' },
    { value: 'LU', label: 'Luxembourg' },
    { value: 'MG', label: 'Madagascar' },
    { value: 'MW', label: 'Malawi' },
    { value: 'MY', label: 'Malaysia' },
    { value: 'MV', label: 'Maldives' },
    { value: 'ML', label: 'Mali' },
    { value: 'MT', label: 'Malta' },
    { value: 'MH', label: 'Marshall Islands' },
    { value: 'MR', label: 'Mauritania' },
    { value: 'MU', label: 'Mauritius' },
    { value: 'MX', label: 'Mexico' },
    { value: 'FM', label: 'Micronesia' },
    { value: 'MD', label: 'Moldova' },
    { value: 'MC', label: 'Monaco' },
    { value: 'MN', label: 'Mongolia' },
    { value: 'ME', label: 'Montenegro' },
    { value: 'MA', label: 'Morocco' },
    { value: 'MZ', label: 'Mozambique' },
    { value: 'MM', label: 'Myanmar' },
    { value: 'NA', label: 'Namibia' },
    { value: 'NR', label: 'Nauru' },
    { value: 'NP', label: 'Nepal' },
    { value: 'NL', label: 'Netherlands' },
    { value: 'NZ', label: 'New Zealand' },
    { value: 'NI', label: 'Nicaragua' },
    { value: 'NE', label: 'Niger' },
    { value: 'NG', label: 'Nigeria' },
    { value: 'NO', label: 'Norway' },
    { value: 'OM', label: 'Oman' },
    { value: 'PK', label: 'Pakistan' },
    { value: 'PW', label: 'Palau' },
    { value: 'PS', label: 'Palestine' },
    { value: 'PA', label: 'Panama' },
    { value: 'PG', label: 'Papua New Guinea' },
    { value: 'PY', label: 'Paraguay' },
    { value: 'PE', label: 'Peru' },
    { value: 'PH', label: 'Philippines' },
    { value: 'PL', label: 'Poland' },
    { value: 'PT', label: 'Portugal' },
    { value: 'QA', label: 'Qatar' },
    { value: 'RO', label: 'Romania' },
    { value: 'RU', label: 'Russia' },
    { value: 'RW', label: 'Rwanda' },
    { value: 'KN', label: 'Saint Kitts and Nevis' },
    { value: 'LC', label: 'Saint Lucia' },
    { value: 'VC', label: 'Saint Vincent and the Grenadines' },
    { value: 'WS', label: 'Samoa' },
    { value: 'SM', label: 'San Marino' },
    { value: 'ST', label: 'São Tomé and Príncipe' },
    { value: 'SA', label: 'Saudi Arabia' },
    { value: 'SN', label: 'Senegal' },
    { value: 'RS', label: 'Serbia' },
    { value: 'SC', label: 'Seychelles' },
    { value: 'SL', label: 'Sierra Leone' },
    { value: 'SG', label: 'Singapore' },
    { value: 'SK', label: 'Slovakia' },
    { value: 'SI', label: 'Slovenia' },
    { value: 'SB', label: 'Solomon Islands' },
    { value: 'SO', label: 'Somalia' },
    { value: 'ZA', label: 'South Africa' },
    { value: 'SS', label: 'South Sudan' },
    { value: 'ES', label: 'Spain' },
    { value: 'LK', label: 'Sri Lanka' },
    { value: 'SD', label: 'Sudan' },
    { value: 'SR', label: 'Suriname' },
    { value: 'SZ', label: 'Eswatini' },
    { value: 'SE', label: 'Sweden' },
    { value: 'CH', label: 'Switzerland' },
    { value: 'SY', label: 'Syria' },
    { value: 'TW', label: 'Taiwan' },
    { value: 'TJ', label: 'Tajikistan' },
    { value: 'TZ', label: 'Tanzania' },
    { value: 'TH', label: 'Thailand' },
    { value: 'TL', label: 'Timor-Leste' },
    { value: 'TG', label: 'Togo' },
    { value: 'TO', label: 'Tonga' },
    { value: 'TT', label: 'Trinidad and Tobago' },
    { value: 'TN', label: 'Tunisia' },
    { value: 'TR', label: 'Turkey' },
    { value: 'TM', label: 'Turkmenistan' },
    { value: 'TV', label: 'Tuvalu' },
    { value: 'UG', label: 'Uganda' },
    { value: 'UA', label: 'Ukraine' },
    { value: 'AE', label: 'United Arab Emirates' },
    { value: 'GB', label: 'United Kingdom' },
    { value: 'US', label: 'United States' },
    { value: 'UY', label: 'Uruguay' },
    { value: 'UZ', label: 'Uzbekistan' },
    { value: 'VU', label: 'Vanuatu' },
    { value: 'VA', label: 'Vatican City' },
    { value: 'VE', label: 'Venezuela' },
    { value: 'VN', label: 'Vietnam' },
    { value: 'YE', label: 'Yemen' },
    { value: 'ZM', label: 'Zambia' },
    { value: 'ZW', label: 'Zimbabwe' }
  ]

  // Sort countries alphabetically by label (country name)
  const countryOptions = allCountries.sort((a, b) => a.label.localeCompare(b.label))

  if (showSuccess) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-md">
          <div className="text-center py-8">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Payment Method Updated</h3>
            <p className="text-gray-600">Your payment method has been successfully updated.</p>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <CreditCard className="h-6 w-6" />
            Update Payment Method
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Current Payment Method */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Current Payment Method</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <CreditCard className="h-8 w-8 text-gray-400" />
                <div>
                  <div className="text-sm font-medium text-gray-900">
                    {currentPaymentMethod.brand} •••• {currentPaymentMethod.last4}
                  </div>
                  <div className="text-sm text-gray-500">
                    Expires {currentPaymentMethod.expiryMonth}/{currentPaymentMethod.expiryYear}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* New Payment Method Form */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">New Payment Method</h3>
            
            {/* Card Number */}
            <div>
              <Label htmlFor="cardNumber">Card Number</Label>
              <Input
                id="cardNumber"
                name="cardNumber"
                type="text"
                placeholder="1234 5678 9012 3456"
                value={formData.cardNumber}
                onChange={handleCardNumberChange}
                maxLength={19}
                className="mt-1"
              />
              {formData.cardNumber && (
                <p className="text-sm text-gray-500 mt-1">
                  {getCardBrand(formData.cardNumber)} card detected
                </p>
              )}
            </div>

            {/* Cardholder Name */}
            <div>
              <Label htmlFor="cardholderName">Cardholder Name</Label>
              <Input
                id="cardholderName"
                name="cardholderName"
                type="text"
                placeholder="John Doe"
                value={formData.cardholderName}
                onChange={handleInputChange}
                className="mt-1"
              />
            </div>

            {/* Expiry and CVV */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="expiryMonth">Month</Label>
                <Select value={formData.expiryMonth} onValueChange={(value) => setFormData(prev => ({ ...prev, expiryMonth: value }))}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="MM" />
                  </SelectTrigger>
                  <SelectContent>
                    {monthOptions.map(option => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="expiryYear">Year</Label>
                <Select value={formData.expiryYear} onValueChange={(value) => setFormData(prev => ({ ...prev, expiryYear: value }))}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="YYYY" />
                  </SelectTrigger>
                  <SelectContent>
                    {yearOptions.map(option => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="cvv">CVV</Label>
                <Input
                  id="cvv"
                  name="cvv"
                  type="text"
                  placeholder="123"
                  value={formData.cvv}
                  onChange={handleInputChange}
                  maxLength={4}
                  className="mt-1"
                />
              </div>
            </div>

            {/* Billing Address */}
            <div>
              <Label htmlFor="billingAddress">Billing Address</Label>
              <Input
                id="billingAddress"
                name="billingAddress"
                type="text"
                placeholder="123 Main Street"
                value={formData.billingAddress}
                onChange={handleInputChange}
                className="mt-1"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="city">City</Label>
                <Input
                  id="city"
                  name="city"
                  type="text"
                  placeholder="New York"
                  value={formData.city}
                  onChange={handleInputChange}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="state">State</Label>
                <Input
                  id="state"
                  name="state"
                  type="text"
                  placeholder="NY"
                  value={formData.state}
                  onChange={handleInputChange}
                  className="mt-1"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="zipCode">ZIP Code</Label>
                <Input
                  id="zipCode"
                  name="zipCode"
                  type="text"
                  placeholder="10001"
                  value={formData.zipCode}
                  onChange={handleInputChange}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="country">Country</Label>
                <Select value={formData.country} onValueChange={(value) => setFormData(prev => ({ ...prev, country: value }))}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select country" />
                  </SelectTrigger>
                  <SelectContent className="max-h-60 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                    {countryOptions.map((country) => (
                      <SelectItem key={country.value} value={country.value}>
                        {country.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Security Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <Lock className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-blue-900">Secure Payment Processing</h4>
                <p className="text-sm text-blue-700 mt-1">
                  Your payment information is encrypted and processed securely. We never store your full card details.
                </p>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 shadow-lg"
            >
              {isLoading ? 'Updating...' : 'Update Payment Method'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
