'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Plug, CheckCircle, XCircle, Clock } from 'lucide-react'

export function IntegrationDashboard() {
  const integrations = [
    { name: 'Dynamics GP', status: 'connected', lastSync: '2 minutes ago' },
    { name: 'QuickBooks', status: 'connected', lastSync: '5 minutes ago' },
    { name: 'Sage', status: 'disconnected', lastSync: '1 hour ago' },
    { name: 'Xero', status: 'connecting', lastSync: 'N/A' },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'disconnected':
        return <XCircle className="h-5 w-5 text-red-600" />
      case 'connecting':
        return <Clock className="h-5 w-5 text-yellow-600" />
      default:
        return <Clock className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'connected':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Connected</Badge>
      case 'disconnected':
        return <Badge variant="secondary" className="bg-red-100 text-red-800">Disconnected</Badge>
      case 'connecting':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Connecting</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plug className="h-5 w-5" />
            ERP Integrations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {integrations.map((integration, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  {getStatusIcon(integration.status)}
                  <div>
                    <h3 className="font-medium">{integration.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      Last sync: {integration.lastSync}
                    </p>
                  </div>
                </div>
                {getStatusBadge(integration.status)}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}