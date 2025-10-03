'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, TrendingUp, TrendingDown, DollarSign, Clock, AlertTriangle, CheckCircle, XCircle, BarChart3, PieChart, LineChart, Download, Filter, RefreshCw } from 'lucide-react';
import { format } from 'date-fns';

interface AnalyticsData {
  overview: {
    totalInvoices: number;
    totalAmount: number;
    processedToday: number;
    pendingApproval: number;
    avgProcessingTime: number;
    accuracyRate: number;
  };
  trends: {
    daily: Array<{ date: string; count: number; amount: number }>;
    weekly: Array<{ week: string; count: number; amount: number }>;
    monthly: Array<{ month: string; count: number; amount: number }>;
  };
  performance: {
    processingSpeed: Array<{ period: string; avgTime: number }>;
    accuracyMetrics: Array<{ period: string; accuracy: number }>;
    errorRates: Array<{ period: string; errors: number }>;
  };
  insights: {
    topVendors: Array<{ name: string; count: number; amount: number }>;
    commonIssues: Array<{ issue: string; count: number; severity: 'low' | 'medium' | 'high' }>;
    costSavings: Array<{ category: string; saved: number; percentage: number }>;
  };
  compliance: {
    auditTrail: Array<{ action: string; user: string; timestamp: string; details: string }>;
    policyViolations: Array<{ violation: string; count: number; severity: string }>;
    certifications: Array<{ name: string; status: 'valid' | 'expired' | 'pending'; expiryDate: string }>;
  };
}

export const EnhancedAnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState<{ from: Date; to: Date }>({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    to: new Date()
  });
  const [selectedMetric, setSelectedMetric] = useState('processing');
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  useEffect(() => {
    fetchAnalyticsData();
    const interval = setInterval(fetchAnalyticsData, refreshInterval);
    return () => clearInterval(interval);
  }, [dateRange, refreshInterval]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockData: AnalyticsData = {
        overview: {
          totalInvoices: 1247,
          totalAmount: 2847392.50,
          processedToday: 45,
          pendingApproval: 12,
          avgProcessingTime: 2.3,
          accuracyRate: 96.8
        },
        trends: {
          daily: Array.from({ length: 30 }, (_, i) => ({
            date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            count: Math.floor(Math.random() * 50) + 20,
            amount: Math.floor(Math.random() * 100000) + 50000
          })),
          weekly: Array.from({ length: 12 }, (_, i) => ({
            week: `Week ${i + 1}`,
            count: Math.floor(Math.random() * 200) + 100,
            amount: Math.floor(Math.random() * 500000) + 200000
          })),
          monthly: Array.from({ length: 12 }, (_, i) => ({
            month: new Date(2024, i).toLocaleString('default', { month: 'short' }),
            count: Math.floor(Math.random() * 800) + 400,
            amount: Math.floor(Math.random() * 2000000) + 1000000
          }))
        },
        performance: {
          processingSpeed: Array.from({ length: 7 }, (_, i) => ({
            period: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
            avgTime: Math.random() * 5 + 1
          })),
          accuracyMetrics: Array.from({ length: 7 }, (_, i) => ({
            period: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
            accuracy: Math.random() * 10 + 90
          })),
          errorRates: Array.from({ length: 7 }, (_, i) => ({
            period: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
            errors: Math.floor(Math.random() * 20) + 1
          }))
        },
        insights: {
          topVendors: [
            { name: 'Office Supplies Inc.', count: 45, amount: 125000 },
            { name: 'Tech Solutions Ltd.', count: 32, amount: 89000 },
            { name: 'Marketing Agency', count: 28, amount: 67000 },
            { name: 'Consulting Services', count: 22, amount: 45000 },
            { name: 'Equipment Rental', count: 18, amount: 38000 }
          ],
          commonIssues: [
            { issue: 'Missing PO Number', count: 12, severity: 'medium' },
            { issue: 'Invalid Tax Amount', count: 8, severity: 'high' },
            { issue: 'Duplicate Invoice', count: 5, severity: 'high' },
            { issue: 'Incorrect Vendor', count: 15, severity: 'low' },
            { issue: 'Missing Line Items', count: 7, severity: 'medium' }
          ],
          costSavings: [
            { category: 'Automated Processing', saved: 45000, percentage: 75 },
            { category: 'Error Reduction', saved: 23000, percentage: 60 },
            { category: 'Faster Approvals', saved: 18000, percentage: 45 },
            { category: 'Compliance Automation', saved: 12000, percentage: 80 }
          ]
        },
        compliance: {
          auditTrail: Array.from({ length: 10 }, (_, i) => ({
            action: ['Invoice Approved', 'Invoice Rejected', 'Vendor Added', 'Settings Changed', 'User Login'][Math.floor(Math.random() * 5)],
            user: ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson'][Math.floor(Math.random() * 4)],
            timestamp: new Date(Date.now() - i * 60 * 60 * 1000).toISOString(),
            details: 'System generated action'
          })),
          policyViolations: [
            { violation: 'Approval Limit Exceeded', count: 3, severity: 'High' },
            { violation: 'Missing Documentation', count: 7, severity: 'Medium' },
            { violation: 'Late Submission', count: 12, severity: 'Low' }
          ],
          certifications: [
            { name: 'SOC 2 Type II', status: 'valid', expiryDate: '2025-06-15' },
            { name: 'ISO 27001', status: 'valid', expiryDate: '2025-03-20' },
            { name: 'GDPR Compliance', status: 'expired', expiryDate: '2024-01-10' }
          ]
        }
      };
      setData(mockData);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'outline';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'valid': return 'default';
      case 'expired': return 'destructive';
      case 'pending': return 'secondary';
      default: return 'outline';
    }
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-8">
        <AlertTriangle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <p className="text-muted-foreground">Failed to load analytics data</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-muted-foreground">Real-time insights and performance metrics</p>
        </div>
        <div className="flex items-center gap-2">
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className="w-[280px] justify-start text-left font-normal">
                <CalendarIcon className="mr-2 h-4 w-4" />
                {format(dateRange.from, 'MMM dd')} - {format(dateRange.to, 'MMM dd, yyyy')}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="range"
                selected={{ from: dateRange.from, to: dateRange.to }}
                onSelect={(range) => range && setDateRange(range)}
                numberOfMonths={2}
              />
            </PopoverContent>
          </Popover>
          <Select value={selectedMetric} onValueChange={setSelectedMetric}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select metric" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="processing">Processing</SelectItem>
              <SelectItem value="accuracy">Accuracy</SelectItem>
              <SelectItem value="cost">Cost Savings</SelectItem>
              <SelectItem value="compliance">Compliance</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon" onClick={fetchAnalyticsData}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Invoices</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.overview.totalInvoices.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+12.5%</span> from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Amount</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(data.overview.totalAmount)}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+8.2%</span> from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processing Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.overview.avgProcessingTime}h</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">-15.3%</span> improvement
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Accuracy Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.overview.accuracyRate}%</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600">+2.1%</span> from last month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Processing Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  <LineChart className="h-8 w-8" />
                  <span className="ml-2">Chart visualization would go here</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Pending Approvals</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">High Priority</span>
                    <Badge variant="destructive">3</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Medium Priority</span>
                    <Badge variant="default">5</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Low Priority</span>
                    <Badge variant="secondary">4</Badge>
                  </div>
                  <Progress value={75} className="mt-4" />
                  <p className="text-xs text-muted-foreground">
                    {data.overview.pendingApproval} invoices pending approval
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Processing Speed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                  <TrendingUp className="h-8 w-8" />
                  <span className="ml-2">Speed chart</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Accuracy Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                  <PieChart className="h-8 w-8" />
                  <span className="ml-2">Accuracy chart</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Error Rates</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                  <TrendingDown className="h-8 w-8" />
                  <span className="ml-2">Error chart</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Top Vendors</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.insights.topVendors.map((vendor, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">{vendor.name}</p>
                        <p className="text-xs text-muted-foreground">{vendor.count} invoices</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{formatCurrency(vendor.amount)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Common Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.insights.commonIssues.map((issue, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm">{issue.issue}</span>
                      <div className="flex items-center gap-2">
                        <Badge variant={getSeverityColor(issue.severity) as any}>
                          {issue.count}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Cost Savings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.insights.costSavings.map((saving, index) => (
                    <div key={index}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{saving.category}</span>
                        <span className="text-sm font-medium">{formatCurrency(saving.saved)}</span>
                      </div>
                      <Progress value={saving.percentage} className="h-2" />
                      <p className="text-xs text-muted-foreground mt-1">
                        {saving.percentage}% efficiency gain
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="compliance" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Audit Trail</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.compliance.auditTrail.slice(0, 5).map((entry, index) => (
                    <div key={index} className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium">{entry.action}</p>
                        <p className="text-xs text-muted-foreground">
                          by {entry.user} • {format(new Date(entry.timestamp), 'MMM dd, HH:mm')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Compliance Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.compliance.certifications.map((cert, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm">{cert.name}</span>
                      <Badge variant={getStatusColor(cert.status) as any}>
                        {cert.status}
                      </Badge>
                    </div>
                  ))}
                  <div className="pt-4 border-t">
                    <h4 className="text-sm font-medium mb-2">Policy Violations</h4>
                    {data.compliance.policyViolations.map((violation, index) => (
                      <div key={index} className="flex items-center justify-between mb-1">
                        <span className="text-xs">{violation.violation}</span>
                        <Badge variant={getSeverityColor(violation.severity) as any} className="text-xs">
                          {violation.count}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};








