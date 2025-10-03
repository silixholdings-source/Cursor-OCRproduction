'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Calendar as CalendarIcon, 
  User, 
  FileText, 
  Shield, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { format } from 'date-fns';

interface AuditEntry {
  id: string;
  timestamp: string;
  action: string;
  category: 'authentication' | 'invoice' | 'vendor' | 'user' | 'system' | 'security' | 'workflow';
  severity: 'low' | 'medium' | 'high' | 'critical';
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
  };
  resource: {
    type: string;
    id: string;
    name: string;
  };
  details: {
    description: string;
    oldValues?: Record<string, any>;
    newValues?: Record<string, any>;
    metadata?: Record<string, any>;
  };
  ipAddress: string;
  userAgent: string;
  sessionId: string;
  location?: {
    country: string;
    city: string;
    region: string;
  };
}

interface AuditFilters {
  dateRange: {
    from: Date;
    to: Date;
  };
  categories: string[];
  severities: string[];
  users: string[];
  actions: string[];
  searchTerm: string;
}

export const AdvancedAuditTrail: React.FC = () => {
  const [auditEntries, setAuditEntries] = useState<AuditEntry[]>([]);
  const [filteredEntries, setFilteredEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEntry, setSelectedEntry] = useState<AuditEntry | null>(null);
  const [filters, setFilters] = useState<AuditFilters>({
    dateRange: {
      from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      to: new Date()
    },
    categories: [],
    severities: [],
    users: [],
    actions: [],
    searchTerm: ''
  });

  useEffect(() => {
    fetchAuditEntries();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [auditEntries, filters]);

  const fetchAuditEntries = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockEntries: AuditEntry[] = [
        {
          id: '1',
          timestamp: '2024-01-20T14:30:00Z',
          action: 'Invoice Approved',
          category: 'invoice',
          severity: 'medium',
          user: {
            id: 'user-1',
            name: 'John Doe',
            email: 'john.doe@company.com',
            role: 'Manager'
          },
          resource: {
            type: 'invoice',
            id: 'INV-001',
            name: 'Office Supplies Invoice'
          },
          details: {
            description: 'Invoice approved after review',
            newValues: { status: 'approved', approvedBy: 'john.doe@company.com' },
            metadata: { approvalTime: '2.5 minutes', amount: 1250.00 }
          },
          ipAddress: '192.168.1.100',
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          sessionId: 'sess-12345',
          location: {
            country: 'United States',
            city: 'New York',
            region: 'NY'
          }
        },
        {
          id: '2',
          timestamp: '2024-01-20T14:25:00Z',
          action: 'User Login',
          category: 'authentication',
          severity: 'low',
          user: {
            id: 'user-2',
            name: 'Jane Smith',
            email: 'jane.smith@company.com',
            role: 'Admin'
          },
          resource: {
            type: 'session',
            id: 'sess-12346',
            name: 'User Session'
          },
          details: {
            description: 'Successful login with MFA',
            metadata: { loginMethod: 'email+totp', deviceType: 'desktop' }
          },
          ipAddress: '192.168.1.101',
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
          sessionId: 'sess-12346',
          location: {
            country: 'United States',
            city: 'San Francisco',
            region: 'CA'
          }
        },
        {
          id: '3',
          timestamp: '2024-01-20T14:20:00Z',
          action: 'Invoice Rejected',
          category: 'invoice',
          severity: 'high',
          user: {
            id: 'user-3',
            name: 'Mike Johnson',
            email: 'mike.johnson@company.com',
            role: 'Finance Manager'
          },
          resource: {
            type: 'invoice',
            id: 'INV-002',
            name: 'Marketing Services Invoice'
          },
          details: {
            description: 'Invoice rejected due to missing documentation',
            newValues: { status: 'rejected', rejectionReason: 'Missing PO number' },
            metadata: { amount: 5500.00, vendor: 'Marketing Agency LLC' }
          },
          ipAddress: '192.168.1.102',
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          sessionId: 'sess-12347',
          location: {
            country: 'United States',
            city: 'Chicago',
            region: 'IL'
          }
        },
        {
          id: '4',
          timestamp: '2024-01-20T14:15:00Z',
          action: 'Vendor Created',
          category: 'vendor',
          severity: 'medium',
          user: {
            id: 'user-4',
            name: 'Sarah Wilson',
            email: 'sarah.wilson@company.com',
            role: 'Procurement'
          },
          resource: {
            type: 'vendor',
            id: 'VENDOR-001',
            name: 'New Supplier Corp'
          },
          details: {
            description: 'New vendor added to system',
            newValues: { 
              name: 'New Supplier Corp',
              email: 'contact@newsupplier.com',
              status: 'pending_approval'
            },
            metadata: { vendorType: 'supplier', category: 'office_supplies' }
          },
          ipAddress: '192.168.1.103',
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
          sessionId: 'sess-12348',
          location: {
            country: 'United States',
            city: 'Seattle',
            region: 'WA'
          }
        },
        {
          id: '5',
          timestamp: '2024-01-20T14:10:00Z',
          action: 'Failed Login Attempt',
          category: 'security',
          severity: 'high',
          user: {
            id: 'unknown',
            name: 'Unknown User',
            email: 'attacker@example.com',
            role: 'Unknown'
          },
          resource: {
            type: 'authentication',
            id: 'auth-001',
            name: 'Login Attempt'
          },
          details: {
            description: 'Multiple failed login attempts detected',
            metadata: { 
              attemptCount: 5,
              blocked: true,
              reason: 'brute_force_attack'
            }
          },
          ipAddress: '203.0.113.42',
          userAgent: 'Mozilla/5.0 (compatible; Bot/1.0)',
          sessionId: 'sess-blocked',
          location: {
            country: 'Unknown',
            city: 'Unknown',
            region: 'Unknown'
          }
        },
        {
          id: '6',
          timestamp: '2024-01-20T14:05:00Z',
          action: 'System Configuration Changed',
          category: 'system',
          severity: 'critical',
          user: {
            id: 'user-5',
            name: 'Admin User',
            email: 'admin@company.com',
            role: 'System Administrator'
          },
          resource: {
            type: 'configuration',
            id: 'config-001',
            name: 'Security Settings'
          },
          details: {
            description: 'Password policy updated',
            oldValues: { minLength: 8, requireSpecialChars: false },
            newValues: { minLength: 12, requireSpecialChars: true },
            metadata: { changeType: 'security_policy' }
          },
          ipAddress: '192.168.1.104',
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          sessionId: 'sess-12349',
          location: {
            country: 'United States',
            city: 'Boston',
            region: 'MA'
          }
        }
      ];
      setAuditEntries(mockEntries);
    } catch (error) {
      console.error('Failed to fetch audit entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = auditEntries;

    // Date range filter
    filtered = filtered.filter(entry => {
      const entryDate = new Date(entry.timestamp);
      return entryDate >= filters.dateRange.from && entryDate <= filters.dateRange.to;
    });

    // Category filter
    if (filters.categories.length > 0) {
      filtered = filtered.filter(entry => filters.categories.includes(entry.category));
    }

    // Severity filter
    if (filters.severities.length > 0) {
      filtered = filtered.filter(entry => filters.severities.includes(entry.severity));
    }

    // User filter
    if (filters.users.length > 0) {
      filtered = filtered.filter(entry => filters.users.includes(entry.user.email));
    }

    // Action filter
    if (filters.actions.length > 0) {
      filtered = filtered.filter(entry => filters.actions.includes(entry.action));
    }

    // Search filter
    if (filters.searchTerm) {
      const searchLower = filters.searchTerm.toLowerCase();
      filtered = filtered.filter(entry => 
        entry.action.toLowerCase().includes(searchLower) ||
        entry.user.name.toLowerCase().includes(searchLower) ||
        entry.user.email.toLowerCase().includes(searchLower) ||
        entry.resource.name.toLowerCase().includes(searchLower) ||
        entry.details.description.toLowerCase().includes(searchLower)
      );
    }

    setFilteredEntries(filtered);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'destructive';
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'outline';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'authentication': return <User className="h-4 w-4" />;
      case 'invoice': return <FileText className="h-4 w-4" />;
      case 'vendor': return <User className="h-4 w-4" />;
      case 'user': return <User className="h-4 w-4" />;
      case 'system': return <Shield className="h-4 w-4" />;
      case 'security': return <AlertTriangle className="h-4 w-4" />;
      case 'workflow': return <Clock className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const exportAuditLog = () => {
    const csvContent = [
      ['Timestamp', 'Action', 'Category', 'Severity', 'User', 'Resource', 'Description', 'IP Address'],
      ...filteredEntries.map(entry => [
        entry.timestamp,
        entry.action,
        entry.category,
        entry.severity,
        entry.user.email,
        entry.resource.name,
        entry.details.description,
        entry.ipAddress
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-log-${format(new Date(), 'yyyy-MM-dd')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Audit Trail</h1>
          <p className="text-muted-foreground">Complete activity log and security monitoring</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchAuditEntries}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" onClick={exportAuditLog}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Date Range</label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-full justify-start text-left font-normal">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {format(filters.dateRange.from, 'MMM dd')} - {format(filters.dateRange.to, 'MMM dd, yyyy')}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="range"
                    selected={{ from: filters.dateRange.from, to: filters.dateRange.to }}
                    onSelect={(range) => range && setFilters({ ...filters, dateRange: range })}
                    numberOfMonths={2}
                  />
                </PopoverContent>
              </Popover>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Category</label>
              <Select 
                value={filters.categories[0] || ''} 
                onValueChange={(value) => setFilters({ ...filters, categories: value ? [value] : [] })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All categories</SelectItem>
                  <SelectItem value="authentication">Authentication</SelectItem>
                  <SelectItem value="invoice">Invoice</SelectItem>
                  <SelectItem value="vendor">Vendor</SelectItem>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                  <SelectItem value="security">Security</SelectItem>
                  <SelectItem value="workflow">Workflow</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Severity</label>
              <Select 
                value={filters.severities[0] || ''} 
                onValueChange={(value) => setFilters({ ...filters, severities: value ? [value] : [] })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All severities" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All severities</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Search</label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search audit log..."
                  value={filters.searchTerm}
                  onChange={(e) => setFilters({ ...filters, searchTerm: e.target.value })}
                  className="pl-8"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Audit Entries */}
      <div className="space-y-4">
        {filteredEntries.map((entry) => (
          <Card key={entry.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {getCategoryIcon(entry.category)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-sm font-medium">{entry.action}</h3>
                      <Badge variant={getSeverityColor(entry.severity) as any} className="text-xs">
                        {entry.severity}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {entry.category}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {entry.details.description}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        {entry.user.name} ({entry.user.role})
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {format(new Date(entry.timestamp), 'MMM dd, yyyy HH:mm')}
                      </span>
                      <span>IP: {entry.ipAddress}</span>
                      {entry.location && (
                        <span>{entry.location.city}, {entry.location.region}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>Audit Entry Details</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-medium mb-2">Action Information</h4>
                            <div className="space-y-1 text-sm">
                              <p><span className="font-medium">Action:</span> {entry.action}</p>
                              <p><span className="font-medium">Category:</span> {entry.category}</p>
                              <p><span className="font-medium">Severity:</span> {entry.severity}</p>
                              <p><span className="font-medium">Timestamp:</span> {format(new Date(entry.timestamp), 'PPP p')}</p>
                            </div>
                          </div>
                          <div>
                            <h4 className="font-medium mb-2">User Information</h4>
                            <div className="space-y-1 text-sm">
                              <p><span className="font-medium">Name:</span> {entry.user.name}</p>
                              <p><span className="font-medium">Email:</span> {entry.user.email}</p>
                              <p><span className="font-medium">Role:</span> {entry.user.role}</p>
                              <p><span className="font-medium">Session ID:</span> {entry.sessionId}</p>
                            </div>
                          </div>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2">Resource Information</h4>
                          <div className="space-y-1 text-sm">
                            <p><span className="font-medium">Type:</span> {entry.resource.type}</p>
                            <p><span className="font-medium">ID:</span> {entry.resource.id}</p>
                            <p><span className="font-medium">Name:</span> {entry.resource.name}</p>
                          </div>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2">Technical Details</h4>
                          <div className="space-y-1 text-sm">
                            <p><span className="font-medium">IP Address:</span> {entry.ipAddress}</p>
                            <p><span className="font-medium">User Agent:</span> {entry.userAgent}</p>
                            {entry.location && (
                              <p><span className="font-medium">Location:</span> {entry.location.city}, {entry.location.region}, {entry.location.country}</p>
                            )}
                          </div>
                        </div>
                        {entry.details.oldValues && (
                          <div>
                            <h4 className="font-medium mb-2">Changes</h4>
                            <div className="space-y-2">
                              {Object.entries(entry.details.oldValues).map(([key, value]) => (
                                <div key={key} className="text-sm">
                                  <span className="font-medium">{key}:</span>
                                  <span className="text-red-600 ml-2">{JSON.stringify(value)}</span>
                                  <span className="mx-2">→</span>
                                  <span className="text-green-600">{JSON.stringify(entry.details.newValues?.[key])}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        {entry.details.metadata && (
                          <div>
                            <h4 className="font-medium mb-2">Metadata</h4>
                            <pre className="text-xs bg-muted p-2 rounded overflow-auto">
                              {JSON.stringify(entry.details.metadata, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredEntries.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No audit entries found</h3>
            <p className="text-muted-foreground">
              No audit entries match your current filters. Try adjusting your search criteria.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};








