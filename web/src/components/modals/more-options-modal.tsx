'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useToast } from '@/hooks/use-toast'
import { 
  History, 
  MessageSquare, 
  TrendingUp, 
  UserCheck, 
  FileText, 
  Star,
  Mail,
  Edit,
  ExternalLink,
  Save
} from 'lucide-react'

interface MoreOptionsModalProps {
  isOpen: boolean
  onClose: () => void
  type: 'approval' | 'invoice' | 'vendor' | 'user'
  itemId: string
  itemName?: string
}

export function MoreOptionsModal({ 
  isOpen, 
  onClose, 
  type,
  itemId,
  itemName 
}: MoreOptionsModalProps) {
  const router = useRouter()
  const { toast } = useToast()
  const [activeAction, setActiveAction] = useState<string | null>(null)
  const [comment, setComment] = useState('')
  const [escalationReason, setEscalationReason] = useState('')
  const [reassignTo, setReassignTo] = useState('')
  const [vendorRating, setVendorRating] = useState('')
  const [vendorNote, setVendorNote] = useState('')
  const [messageSubject, setMessageSubject] = useState('')
  const [messageBody, setMessageBody] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleAction = (action: string) => {
    console.log(`✅ ${action} clicked for ${type}:`, itemId)
    
    // Handle direct actions that don't need forms
    if (action === 'invoices') {
      handleViewInvoices()
      return
    }
    
    setActiveAction(action)
  }

  const handleViewInvoices = () => {
    // Navigate to invoices page with vendor filter
    const vendorName = encodeURIComponent(itemName || '')
    router.push(`/dashboard/invoices?vendor=${vendorName}`)
    onClose()
    toast({
      title: "Viewing Vendor Invoices",
      description: `Showing all invoices for ${itemName}`,
    })
  }

  const handleSubmitAction = async () => {
    setIsLoading(true)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      switch (activeAction) {
        case 'history':
          console.log(`✅ View History completed for ${itemName || itemId}`)
          break
        case 'comment':
          console.log(`✅ Add Comment completed for ${itemName || itemId}:`, comment)
          toast({
            title: "Comment Added",
            description: `Comment added successfully for ${itemName}`,
          })
          break
        case 'escalate':
          console.log(`✅ Escalate completed for ${itemName || itemId}:`, escalationReason)
          toast({
            title: "Request Escalated",
            description: `Request has been escalated with reason: ${escalationReason}`,
          })
          break
        case 'reassign':
          console.log(`✅ Reassign completed for ${itemName || itemId} to:`, reassignTo)
          toast({
            title: "Request Reassigned",
            description: `Request has been reassigned to ${reassignTo}`,
          })
          break
        case 'duplicate':
          console.log(`✅ Duplicate Invoice completed for ${itemName || itemId}`)
          toast({
            title: "Invoice Duplicated",
            description: `Invoice has been duplicated successfully`,
          })
          break
        case 'send':
          console.log(`✅ Send to Vendor completed for ${itemName || itemId}`)
          toast({
            title: "Invoice Sent",
            description: `Invoice has been sent to vendor`,
          })
          break
        case 'paid':
          console.log(`✅ Mark as Paid completed for ${itemName || itemId}`)
          toast({
            title: "Invoice Marked as Paid",
            description: `Invoice has been marked as paid`,
          })
          break
        case 'favorite':
          console.log(`✅ Add to Favorites completed for ${itemName || itemId}`)
          toast({
            title: "Added to Favorites",
            description: `Invoice has been added to favorites`,
          })
          break
        case 'message':
          handleSendMessage()
          break
        case 'rating':
          handleUpdateRating()
          break
        case 'note':
          handleAddNote()
          break
        case 'profile':
          console.log(`✅ View Profile completed for ${itemName || itemId}`)
          break
        case 'permissions':
          console.log(`✅ Manage Permissions completed for ${itemName || itemId}`)
          break
        case 'activity':
          console.log(`✅ View Activity completed for ${itemName || itemId}`)
          break
      }
    } catch (error) {
      console.error('Error performing action:', error)
      toast({
        title: "Error",
        description: "An error occurred while performing the action",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
      setActiveAction(null)
      setComment('')
      setEscalationReason('')
      setReassignTo('')
      setVendorRating('')
      setVendorNote('')
      setMessageSubject('')
      setMessageBody('')
      onClose()
    }
  }

  const handleSendMessage = () => {
    // Create mailto link with pre-filled subject and body
    const subject = encodeURIComponent(messageSubject || `Message regarding ${itemName}`)
    const body = encodeURIComponent(messageBody)
    const mailtoLink = `mailto:vendor@${itemName?.toLowerCase().replace(/\s+/g, '')}.com?subject=${subject}&body=${body}`
    
    // Open email client
    window.open(mailtoLink, '_blank')
    
    toast({
      title: "Message Sent",
      description: `Email client opened for ${itemName}`,
    })
    
    console.log(`✅ Send Message completed for ${itemName || itemId}`)
  }

  const handleUpdateRating = () => {
    // In a real app, this would update the vendor rating in the database
    console.log(`✅ Update Rating completed for ${itemName || itemId}: ${vendorRating}`)
    
    toast({
      title: "Rating Updated",
      description: `Vendor rating updated to ${vendorRating} stars`,
    })
  }

  const handleAddNote = () => {
    // In a real app, this would save the note to the database
    console.log(`✅ Add Note completed for ${itemName || itemId}: ${vendorNote}`)
    
    toast({
      title: "Note Added",
      description: `Internal note added for ${itemName}`,
    })
  }

  const handleCancelAction = () => {
    setActiveAction(null)
    setComment('')
    setEscalationReason('')
    setReassignTo('')
    setVendorRating('')
    setVendorNote('')
    setMessageSubject('')
    setMessageBody('')
  }

  const getHistoryData = () => {
    // Generate realistic approval history data
    return [
      {
        action: 'Approval Created',
        user: 'John Smith',
        timestamp: '2024-01-15 09:30 AM',
        status: 'created',
        comment: 'New approval request submitted for review'
      },
      {
        action: 'Assigned to Manager',
        user: 'System',
        timestamp: '2024-01-15 09:31 AM',
        status: 'assigned',
        comment: 'Automatically assigned to department manager'
      },
      {
        action: 'Under Review',
        user: 'Sarah Johnson',
        timestamp: '2024-01-15 10:15 AM',
        status: 'pending',
        comment: 'Reviewing documentation and requirements'
      },
      {
        action: 'Additional Info Requested',
        user: 'Sarah Johnson',
        timestamp: '2024-01-15 02:30 PM',
        status: 'pending',
        comment: 'Need clarification on budget allocation'
      },
      {
        action: 'Info Provided',
        user: 'John Smith',
        timestamp: '2024-01-16 08:45 AM',
        status: 'updated',
        comment: 'Budget details and justification provided'
      },
      {
        action: 'Approved',
        user: 'Sarah Johnson',
        timestamp: '2024-01-16 11:20 AM',
        status: 'approved',
        comment: 'All requirements met, approval granted'
      }
    ]
  }

  const getOptions = () => {
    switch (type) {
      case 'approval':
        return [
          { id: 'history', label: 'View History', icon: History, description: 'View approval history and timeline' },
          { id: 'comment', label: 'Add Comment', icon: MessageSquare, description: 'Add a comment or note' },
          { id: 'escalate', label: 'Escalate', icon: TrendingUp, description: 'Escalate to higher authority' },
          { id: 'reassign', label: 'Reassign', icon: UserCheck, description: 'Reassign to another approver' }
        ]
      case 'invoice':
        return [
          { id: 'duplicate', label: 'Duplicate Invoice', icon: FileText, description: 'Create a copy of this invoice' },
          { id: 'send', label: 'Send to Vendor', icon: Mail, description: 'Send invoice to vendor via email' },
          { id: 'paid', label: 'Mark as Paid', icon: UserCheck, description: 'Mark invoice as paid' },
          { id: 'favorite', label: 'Add to Favorites', icon: Star, description: 'Add to favorites list' }
        ]
      case 'vendor':
        return [
          { id: 'invoices', label: 'View Invoices', icon: FileText, description: 'View all invoices from this vendor' },
          { id: 'message', label: 'Send Message', icon: Mail, description: 'Send message to vendor' },
          { id: 'rating', label: 'Update Rating', icon: Star, description: 'Update vendor rating' },
          { id: 'note', label: 'Add Note', icon: Edit, description: 'Add internal note about vendor' }
        ]
      case 'user':
        return [
          { id: 'profile', label: 'View Profile', icon: UserCheck, description: 'View user profile details' },
          { id: 'permissions', label: 'Manage Permissions', icon: Edit, description: 'Manage user permissions' },
          { id: 'activity', label: 'View Activity', icon: History, description: 'View user activity log' },
          { id: 'message', label: 'Send Message', icon: Mail, description: 'Send message to user' }
        ]
      default:
        return []
    }
  }

  const options = getOptions()

  const renderActionForm = () => {
    if (!activeAction) return null

    switch (activeAction) {
      case 'history':
        return (
          <div className="space-y-4">
            <div className="text-lg font-medium mb-4">Approval History</div>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {getHistoryData().map((event, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className={`w-3 h-3 rounded-full mt-1 flex-shrink-0 ${
                    event.status === 'approved' ? 'bg-green-500' :
                    event.status === 'rejected' ? 'bg-red-500' :
                    event.status === 'pending' ? 'bg-yellow-500' :
                    event.status === 'created' ? 'bg-blue-500' :
                    event.status === 'assigned' ? 'bg-purple-500' :
                    'bg-gray-500'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm">{event.action}</div>
                    <div className="text-xs text-gray-600">{event.user} • {event.timestamp}</div>
                    {event.comment && (
                      <div className="text-xs text-gray-700 mt-1 italic">"{event.comment}"</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      
      case 'comment':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="comment">Add Comment</Label>
              <Textarea
                id="comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Enter your comment..."
                rows={4}
              />
            </div>
          </div>
        )
      
      case 'escalate':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="escalationReason">Escalation Reason</Label>
              <Select value={escalationReason} onValueChange={setEscalationReason}>
                <SelectTrigger>
                  <SelectValue placeholder="Select reason for escalation" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="urgent">Urgent - Requires immediate attention</SelectItem>
                  <SelectItem value="complex">Complex - Needs higher authority review</SelectItem>
                  <SelectItem value="dispute">Dispute - Requires management intervention</SelectItem>
                  <SelectItem value="other">Other - Specify in notes</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="escalationNotes">Additional Notes</Label>
              <Textarea
                id="escalationNotes"
                placeholder="Provide additional context..."
                rows={3}
              />
            </div>
          </div>
        )
      
      case 'reassign':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="reassignTo">Reassign To</Label>
              <Select value={reassignTo} onValueChange={setReassignTo}>
                <SelectTrigger>
                  <SelectValue placeholder="Select approver" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="manager1">John Manager (Manager)</SelectItem>
                  <SelectItem value="manager2">Sarah Director (Director)</SelectItem>
                  <SelectItem value="manager3">Mike VP (VP Finance)</SelectItem>
                  <SelectItem value="manager4">Lisa CEO (CEO)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="reassignReason">Reason for Reassignment</Label>
              <Textarea
                id="reassignReason"
                placeholder="Explain why this needs to be reassigned..."
                rows={3}
              />
            </div>
          </div>
        )
      
      case 'message':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="messageSubject">Subject</Label>
              <Input
                id="messageSubject"
                value={messageSubject}
                onChange={(e) => setMessageSubject(e.target.value)}
                placeholder={`Message regarding ${itemName}`}
              />
            </div>
            <div>
              <Label htmlFor="messageBody">Message</Label>
              <Textarea
                id="messageBody"
                value={messageBody}
                onChange={(e) => setMessageBody(e.target.value)}
                placeholder="Enter your message..."
                rows={4}
              />
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Mail className="h-4 w-4" />
              <span>This will open your email client to send the message</span>
            </div>
          </div>
        )
      
      case 'rating':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="vendorRating">Rating</Label>
              <Select value={vendorRating} onValueChange={setVendorRating}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a rating (1-5 stars)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">⭐ (1 star) - Poor</SelectItem>
                  <SelectItem value="2">⭐⭐ (2 stars) - Below Average</SelectItem>
                  <SelectItem value="3">⭐⭐⭐ (3 stars) - Average</SelectItem>
                  <SelectItem value="4">⭐⭐⭐⭐ (4 stars) - Good</SelectItem>
                  <SelectItem value="5">⭐⭐⭐⭐⭐ (5 stars) - Excellent</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Star className="h-4 w-4" />
              <span>Update the vendor's performance rating</span>
            </div>
          </div>
        )
      
      case 'note':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="vendorNote">Internal Note</Label>
              <Textarea
                id="vendorNote"
                value={vendorNote}
                onChange={(e) => setVendorNote(e.target.value)}
                placeholder="Add internal notes about this vendor..."
                rows={4}
              />
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Edit className="h-4 w-4" />
              <span>This note will be stored internally and visible to your team</span>
            </div>
          </div>
        )
      
      default:
        return (
          <div className="text-center py-8">
            <div className="text-lg font-medium mb-2">Processing {activeAction}...</div>
            <div className="text-sm text-gray-500">This action will be executed for {itemName || itemId}</div>
          </div>
        )
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={activeAction === 'history' ? 'max-w-2xl' : 'max-w-md'}>
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold">
            {activeAction === 'history' ? `Approval History for ${itemName || itemId}` :
             activeAction ? `${activeAction} for ${itemName || itemId}` : 
             `More Options for ${itemName || itemId}`}
          </DialogTitle>
        </DialogHeader>

        {!activeAction ? (
          <div className="space-y-2">
            {options.map((option) => {
              const Icon = option.icon
              return (
                <Button
                  key={option.id}
                  variant="ghost"
                  className="w-full justify-start h-auto p-4"
                  onClick={() => handleAction(option.id)}
                >
                  <div className="flex items-start space-x-3">
                    <Icon className="h-5 w-5 mt-0.5 text-gray-500" />
                    <div className="text-left">
                      <div className="font-medium">{option.label}</div>
                      <div className="text-sm text-gray-500">{option.description}</div>
                    </div>
                  </div>
                </Button>
              )
            })}
          </div>
        ) : (
          <div className="space-y-4">
            {renderActionForm()}
          </div>
        )}

        <div className="flex justify-end space-x-2 pt-4">
          {activeAction ? (
            activeAction === 'history' ? (
              <Button variant="outline" onClick={handleCancelAction}>
                Close
              </Button>
            ) : (
              <>
                <Button variant="outline" onClick={handleCancelAction} disabled={isLoading}>
                  Cancel
                </Button>
                <Button onClick={handleSubmitAction} disabled={isLoading}>
                  {isLoading ? 'Processing...' : 
                   activeAction === 'message' ? 'Send Message' :
                   activeAction === 'rating' ? 'Update Rating' :
                   activeAction === 'note' ? 'Save Note' :
                   'Submit'}
                </Button>
              </>
            )
          ) : (
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
