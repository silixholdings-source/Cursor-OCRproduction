'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Play, 
  Pause, 
  Users, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Workflow,
  Settings,
  Copy,
  Save,
  RefreshCw
} from 'lucide-react';

interface WorkflowStep {
  id: string;
  name: string;
  type: 'approval' | 'review' | 'notification' | 'condition' | 'automation';
  approvers: string[];
  conditions?: {
    field: string;
    operator: 'equals' | 'greater_than' | 'less_than' | 'contains';
    value: string;
  }[];
  timeout?: number; // hours
  isRequired: boolean;
  order: number;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
  steps: WorkflowStep[];
  createdAt: string;
  updatedAt: string;
  usageCount: number;
  category: 'invoice' | 'vendor' | 'expense' | 'custom';
  conditions?: {
    amountThreshold?: number;
    vendorCategories?: string[];
    departments?: string[];
  };
}

interface WorkflowExecution {
  id: string;
  workflowId: string;
  invoiceId: string;
  status: 'pending' | 'in_progress' | 'completed' | 'rejected' | 'timeout';
  currentStep: number;
  startedAt: string;
  completedAt?: string;
  assignedTo: string;
  comments: string[];
}

export const AdvancedWorkflowManager: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newWorkflow, setNewWorkflow] = useState<Partial<Workflow>>({
    name: '',
    description: '',
    category: 'invoice',
    isActive: true,
    steps: [],
    conditions: {}
  });

  useEffect(() => {
    fetchWorkflows();
    fetchExecutions();
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockWorkflows: Workflow[] = [
        {
          id: '1',
          name: 'High Value Invoice Approval',
          description: 'Multi-level approval for invoices over $10,000',
          isActive: true,
          category: 'invoice',
          usageCount: 45,
          createdAt: '2024-01-15T10:00:00Z',
          updatedAt: '2024-01-20T14:30:00Z',
          conditions: {
            amountThreshold: 10000,
            departments: ['finance', 'operations']
          },
          steps: [
            {
              id: '1-1',
              name: 'Manager Review',
              type: 'approval',
              approvers: ['manager@company.com'],
              timeout: 24,
              isRequired: true,
              order: 1
            },
            {
              id: '1-2',
              name: 'Finance Approval',
              type: 'approval',
              approvers: ['finance@company.com'],
              timeout: 48,
              isRequired: true,
              order: 2
            },
            {
              id: '1-3',
              name: 'Executive Approval',
              type: 'approval',
              approvers: ['executive@company.com'],
              timeout: 72,
              isRequired: true,
              order: 3
            }
          ]
        },
        {
          id: '2',
          name: 'Vendor Onboarding',
          description: 'Standard vendor registration and approval process',
          isActive: true,
          category: 'vendor',
          usageCount: 23,
          createdAt: '2024-01-10T09:00:00Z',
          updatedAt: '2024-01-18T11:15:00Z',
          steps: [
            {
              id: '2-1',
              name: 'Document Review',
              type: 'review',
              approvers: ['procurement@company.com'],
              timeout: 48,
              isRequired: true,
              order: 1
            },
            {
              id: '2-2',
              name: 'Compliance Check',
              type: 'automation',
              approvers: [],
              timeout: 24,
              isRequired: true,
              order: 2
            },
            {
              id: '2-3',
              name: 'Final Approval',
              type: 'approval',
              approvers: ['procurement-manager@company.com'],
              timeout: 24,
              isRequired: true,
              order: 3
            }
          ]
        },
        {
          id: '3',
          name: 'Low Value Invoice Auto-Approval',
          description: 'Automated approval for invoices under $1,000',
          isActive: true,
          category: 'invoice',
          usageCount: 156,
          createdAt: '2024-01-05T08:00:00Z',
          updatedAt: '2024-01-12T16:45:00Z',
          conditions: {
            amountThreshold: 1000
          },
          steps: [
            {
              id: '3-1',
              name: 'Automated Validation',
              type: 'automation',
              approvers: [],
              timeout: 1,
              isRequired: true,
              order: 1
            },
            {
              id: '3-2',
              name: 'Notification',
              type: 'notification',
              approvers: ['finance@company.com'],
              timeout: 0,
              isRequired: false,
              order: 2
            }
          ]
        }
      ];
      setWorkflows(mockWorkflows);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchExecutions = async () => {
    try {
      // Mock data - replace with actual API call
      const mockExecutions: WorkflowExecution[] = [
        {
          id: 'exec-1',
          workflowId: '1',
          invoiceId: 'INV-001',
          status: 'in_progress',
          currentStep: 2,
          startedAt: '2024-01-20T09:00:00Z',
          assignedTo: 'finance@company.com',
          comments: ['Initial review completed', 'Waiting for finance approval']
        },
        {
          id: 'exec-2',
          workflowId: '2',
          invoiceId: 'VENDOR-002',
          status: 'completed',
          currentStep: 3,
          startedAt: '2024-01-19T14:00:00Z',
          completedAt: '2024-01-20T10:30:00Z',
          assignedTo: 'procurement@company.com',
          comments: ['Vendor approved successfully']
        },
        {
          id: 'exec-3',
          workflowId: '3',
          invoiceId: 'INV-003',
          status: 'completed',
          currentStep: 2,
          startedAt: '2024-01-20T11:00:00Z',
          completedAt: '2024-01-20T11:05:00Z',
          assignedTo: 'system',
          comments: ['Auto-approved']
        }
      ];
      setExecutions(mockExecutions);
    } catch (error) {
      console.error('Failed to fetch executions:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'default';
      case 'in_progress': return 'secondary';
      case 'pending': return 'outline';
      case 'rejected': return 'destructive';
      case 'timeout': return 'destructive';
      default: return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'in_progress': return <Clock className="h-4 w-4" />;
      case 'pending': return <AlertTriangle className="h-4 w-4" />;
      case 'rejected': return <XCircle className="h-4 w-4" />;
      case 'timeout': return <AlertTriangle className="h-4 w-4" />;
      default: return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const handleCreateWorkflow = async () => {
    try {
      // Mock API call - replace with actual implementation
      const workflow: Workflow = {
        id: Date.now().toString(),
        name: newWorkflow.name!,
        description: newWorkflow.description!,
        category: newWorkflow.category!,
        isActive: newWorkflow.isActive!,
        steps: newWorkflow.steps || [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        usageCount: 0,
        conditions: newWorkflow.conditions
      };
      
      setWorkflows([...workflows, workflow]);
      setIsCreating(false);
      setNewWorkflow({
        name: '',
        description: '',
        category: 'invoice',
        isActive: true,
        steps: [],
        conditions: {}
      });
    } catch (error) {
      console.error('Failed to create workflow:', error);
    }
  };

  const handleToggleWorkflow = async (workflowId: string) => {
    try {
      setWorkflows(workflows.map(w => 
        w.id === workflowId ? { ...w, isActive: !w.isActive } : w
      ));
    } catch (error) {
      console.error('Failed to toggle workflow:', error);
    }
  };

  const handleDeleteWorkflow = async (workflowId: string) => {
    try {
      setWorkflows(workflows.filter(w => w.id !== workflowId));
    } catch (error) {
      console.error('Failed to delete workflow:', error);
    }
  };

  const handleDuplicateWorkflow = async (workflow: Workflow) => {
    try {
      const duplicatedWorkflow: Workflow = {
        ...workflow,
        id: Date.now().toString(),
        name: `${workflow.name} (Copy)`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        usageCount: 0
      };
      setWorkflows([...workflows, duplicatedWorkflow]);
    } catch (error) {
      console.error('Failed to duplicate workflow:', error);
    }
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
          <h1 className="text-3xl font-bold tracking-tight">Workflow Management</h1>
          <p className="text-muted-foreground">Design and manage approval workflows</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchWorkflows}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={isCreating} onOpenChange={setIsCreating}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Workflow
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Workflow</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={newWorkflow.name}
                      onChange={(e) => setNewWorkflow({ ...newWorkflow, name: e.target.value })}
                      placeholder="Workflow name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="category">Category</Label>
                    <Select 
                      value={newWorkflow.category} 
                      onValueChange={(value) => setNewWorkflow({ ...newWorkflow, category: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="invoice">Invoice</SelectItem>
                        <SelectItem value="vendor">Vendor</SelectItem>
                        <SelectItem value="expense">Expense</SelectItem>
                        <SelectItem value="custom">Custom</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newWorkflow.description}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, description: e.target.value })}
                    placeholder="Workflow description"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="active"
                    checked={newWorkflow.isActive}
                    onCheckedChange={(checked) => setNewWorkflow({ ...newWorkflow, isActive: checked })}
                  />
                  <Label htmlFor="active">Active</Label>
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsCreating(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateWorkflow}>
                    <Save className="h-4 w-4 mr-2" />
                    Create
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="workflows" className="space-y-4">
        <TabsList>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="executions">Executions</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
        </TabsList>

        <TabsContent value="workflows" className="space-y-4">
          <div className="grid gap-4">
            {workflows.map((workflow) => (
              <Card key={workflow.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Workflow className="h-5 w-5" />
                      <div>
                        <CardTitle className="text-lg">{workflow.name}</CardTitle>
                        <p className="text-sm text-muted-foreground">{workflow.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={workflow.isActive ? 'default' : 'secondary'}>
                        {workflow.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                      <Badge variant="outline">{workflow.category}</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Steps</p>
                      <p className="text-lg font-semibold">{workflow.steps.length}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Usage</p>
                      <p className="text-lg font-semibold">{workflow.usageCount}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Created</p>
                      <p className="text-lg font-semibold">
                        {new Date(workflow.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Updated</p>
                      <p className="text-lg font-semibold">
                        {new Date(workflow.updatedAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-2 mb-4">
                    <h4 className="text-sm font-medium">Workflow Steps</h4>
                    {workflow.steps.map((step, index) => (
                      <div key={step.id} className="flex items-center gap-2 text-sm">
                        <span className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs">
                          {index + 1}
                        </span>
                        <span>{step.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {step.type}
                        </Badge>
                        {step.timeout && (
                          <span className="text-muted-foreground">
                            ({step.timeout}h timeout)
                          </span>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedWorkflow(workflow)}
                    >
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggleWorkflow(workflow.id)}
                    >
                      {workflow.isActive ? (
                        <Pause className="h-4 w-4 mr-2" />
                      ) : (
                        <Play className="h-4 w-4 mr-2" />
                      )}
                      {workflow.isActive ? 'Pause' : 'Activate'}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDuplicateWorkflow(workflow)}
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Duplicate
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteWorkflow(workflow.id)}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="executions" className="space-y-4">
          <div className="grid gap-4">
            {executions.map((execution) => {
              const workflow = workflows.find(w => w.id === execution.workflowId);
              return (
                <Card key={execution.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">
                          {workflow?.name || 'Unknown Workflow'}
                        </CardTitle>
                        <p className="text-sm text-muted-foreground">
                          Invoice: {execution.invoiceId}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(execution.status)}
                        <Badge variant={getStatusColor(execution.status) as any}>
                          {execution.status.replace('_', ' ')}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Current Step</p>
                        <p className="text-lg font-semibold">
                          {execution.currentStep} / {workflow?.steps.length || 0}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Assigned To</p>
                        <p className="text-lg font-semibold">{execution.assignedTo}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Started</p>
                        <p className="text-lg font-semibold">
                          {new Date(execution.startedAt).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Completed</p>
                        <p className="text-lg font-semibold">
                          {execution.completedAt 
                            ? new Date(execution.completedAt).toLocaleDateString()
                            : 'In Progress'
                          }
                        </p>
                      </div>
                    </div>
                    
                    {execution.comments.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium">Comments</h4>
                        {execution.comments.map((comment, index) => (
                          <div key={index} className="text-sm text-muted-foreground bg-muted p-2 rounded">
                            {comment}
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <Alert>
            <Settings className="h-4 w-4" />
            <AlertDescription>
              Workflow templates will be available in the next update. You can create custom workflows using the "Create Workflow" button.
            </AlertDescription>
          </Alert>
        </TabsContent>
      </Tabs>
    </div>
  );
};








