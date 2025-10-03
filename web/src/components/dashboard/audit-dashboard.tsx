'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { FileText, User, Calendar, Activity } from 'lucide-react'

export function AuditDashboard() {
  const auditEvents = [
    { id: 1, user: 'John Doe', action: 'Invoice Approved', timestamp: '2 minutes ago', type: 'approval' },
    { id: 2, user: 'Jane Smith', action: 'Invoice Uploaded', timestamp: '5 minutes ago', type: 'upload' },
    { id: 3, user: 'Mike Johnson', action: 'Settings Updated', timestamp: '1 hour ago', type: 'settings' },
    { id: 4, user: 'Sarah Wilson', action: 'User Added', timestamp: '2 hours ago', type: 'user' },
  ]

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'approval':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Approval</Badge>
      case 'upload':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Upload</Badge>
      case 'settings':
        return <Badge variant="secondary" className="bg-purple-100 text-purple-800">Settings</Badge>
      case 'user':
        return <Badge variant="secondary" className="bg-orange-100 text-orange-800">User</Badge>
      default:
        return <Badge variant="secondary">Other</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent Audit Events
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {auditEvents.map((event) => (
              <div key={event.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{event.user}</span>
                  </div>
                  <span className="text-muted-foreground">-</span>
                  <span>{event.action}</span>
                </div>
                <div className="flex items-center gap-2">
                  {getEventBadge(event.type)}
                  <span className="text-sm text-muted-foreground flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {event.timestamp}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}