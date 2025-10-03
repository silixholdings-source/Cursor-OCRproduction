"""
Workflow Management Schemas
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class WorkflowStatus(str, Enum):
    """Workflow status types"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    ERROR = "error"


class ApprovalAction(str, Enum):
    """Approval action types"""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_INFO = "request_info"
    DELEGATE = "delegate"
    ESCALATE = "escalate"


class WorkflowCreateRequest(BaseModel):
    """Request schema for creating a workflow"""
    invoice_id: str = Field(..., description="Invoice ID to create workflow for")
    invoice_amount: float = Field(..., description="Invoice amount for workflow determination")
    company_settings: Dict[str, Any] = Field(default_factory=dict, description="Company workflow settings")
    
            model_config = ConfigDict(
            schema_extra = {
            "example": {
            "invoice_id": "inv_123456"
            "invoice_amount": 5000.00
            "company_settings": {
            "manager_approval_threshold": 1000
            "director_approval_threshold": 5000
            "cfo_approval_threshold": 25000
            }
            }
            }
        )


class WorkflowStepResponse(BaseModel):
    """Response schema for workflow step"""
    step_id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Step name")
    description: str = Field(..., description="Step description")
    approver_role: str = Field(..., description="Required approver role")
    is_required: bool = Field(..., description="Whether step is required")
    timeout_hours: int = Field(..., description="Step timeout in hours")


class WorkflowResponse(BaseModel):
    """Response schema for workflow creation"""
    workflow_id: str = Field(..., description="Unique workflow identifier")
    invoice_id: str = Field(..., description="Associated invoice ID")
    company_id: str = Field(..., description="Company ID")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    current_step: int = Field(..., description="Current step index")
    total_steps: int = Field(..., description="Total number of steps")
    created_at: datetime = Field(..., description="Workflow creation timestamp")
    steps: List[WorkflowStepResponse] = Field(..., description="All workflow steps")


class ApprovalActionRequest(BaseModel):
    """Request schema for approval actions"""
    action: ApprovalAction = Field(..., description="Approval action to take")
    comments: str = Field(default="", description="Comments for the action")
    delegation_user_id: Optional[str] = Field(None, description="User ID to delegate to (for delegate action)")
    
            model_config = ConfigDict(
            schema_extra = {
            "example": {
            "action": "approve"
            "comments": "Invoice approved after review"
            "delegation_user_id": None
            }
            }
        )


class WorkflowStatusResponse(BaseModel):
    """Response schema for workflow status"""
    workflow_id: str = Field(..., description="Unique workflow identifier")
    invoice_id: str = Field(..., description="Associated invoice ID")
    company_id: str = Field(..., description="Company ID")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    current_step: int = Field(..., description="Current step index")
    total_steps: int = Field(..., description="Total number of steps")
    created_at: str = Field(..., description="Workflow creation timestamp")
    completed_at: Optional[str] = Field(None, description="Workflow completion timestamp")
    approved_by: Optional[str] = Field(None, description="User who completed the workflow")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if applicable")
    current_step_info: Optional[Dict[str, Any]] = Field(None, description="Current step details")


class WorkflowMetrics(BaseModel):
    """Workflow performance metrics"""
    company_id: str = Field(..., description="Company ID")
    period_start: datetime = Field(..., description="Metrics period start")
    period_end: datetime = Field(..., description="Metrics period end")
    
    # Volume metrics
    total_workflows: int = Field(0, description="Total workflows created")
    completed_workflows: int = Field(0, description="Completed workflows")
    rejected_workflows: int = Field(0, description="Rejected workflows")
    timed_out_workflows: int = Field(0, description="Timed out workflows")
    
    # Performance metrics
    avg_completion_time_hours: Optional[float] = Field(None, description="Average completion time")
    avg_step_time_hours: Optional[float] = Field(None, description="Average step processing time")
    
    # Approval metrics
    approval_rate: float = Field(0.0, description="Approval rate percentage")
    rejection_rate: float = Field(0.0, description="Rejection rate percentage")
    
    # Bottleneck analysis
    slowest_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Steps with longest processing times")
    common_rejection_reasons: List[Dict[str, Any]] = Field(default_factory=list, description="Most common rejection reasons")


class WorkflowConfiguration(BaseModel):
    """Workflow configuration schema"""
    company_id: str = Field(..., description="Company ID")
    approval_thresholds: Dict[str, float] = Field(..., description="Approval amount thresholds")
    timeout_settings: Dict[str, int] = Field(..., description="Timeout settings in hours")
    auto_approval_rules: Dict[str, Any] = Field(default_factory=dict, description="Auto-approval rules")
    escalation_rules: Dict[str, Any] = Field(default_factory=dict, description="Escalation rules")
    notification_settings: Dict[str, bool] = Field(default_factory=dict, description="Notification preferences")
    
            model_config = ConfigDict(
            schema_extra = {
            "example": {
            "company_id": "comp_123"
            "approval_thresholds": {
            "manager_approval_threshold": 1000
            "director_approval_threshold": 5000
            "cfo_approval_threshold": 25000
            }
            "timeout_settings": {
            "default_timeout": 72
            "escalation_timeout": 24
            "urgent_timeout": 4
            }
            "auto_approval_rules": {
            "enabled": True
            "max_amount": 1000
            "allowed_categories": ["office_supplies", "utilities"]
            }
            "escalation_rules": {
            "enabled": True
            "escalate_after_hours": 24
            "escalation_chain": ["manager", "director", "cfo"]
            }
            "notification_settings": {
            "email_notifications": True
            "push_notifications": True
            "reminder_intervals": [24, 48, 72]
            }
            }
            }
        )


class WorkflowTemplate(BaseModel):
    """Workflow template schema"""
    template_id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category")
    steps: List[WorkflowStepResponse] = Field(..., description="Template steps")
    is_active: bool = Field(True, description="Whether template is active")
    created_by: str = Field(..., description="Template creator user ID")
    created_at: datetime = Field(..., description="Template creation timestamp")
    
            model_config = ConfigDict(
            schema_extra = {
            "example": {
            "template_id": "template_001"
            "name": "Standard Invoice Approval"
            "description": "Standard workflow for invoice approval"
            "category": "invoice_processing"
            "steps": [
            {
            "step_id": "preparer_review"
            "name": "Preparer Review"
            "description": "Initial review by invoice preparer"
            "approver_role": "preparer"
            "is_required": True
            "timeout_hours": 24
            }
            {
            "step_id": "manager_approval"
            "name": "Manager Approval"
            "description": "Manager approval required"
            "approver_role": "manager"
            "is_required": True
            "timeout_hours": 72
            }
            ]
            "is_active": True
            "created_by": "user_123"
            "created_at": "2024-01-15T10:30:00Z"
            }
            }
        )


class WorkflowAuditLog(BaseModel):
    """Workflow audit log entry"""
    log_id: str = Field(..., description="Unique log identifier")
    workflow_id: str = Field(..., description="Associated workflow ID")
    user_id: str = Field(..., description="User who performed the action")
    action: str = Field(..., description="Action performed")
    timestamp: datetime = Field(..., description="Action timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Action details")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")


class WorkflowNotification(BaseModel):
    """Workflow notification schema"""
    notification_id: str = Field(..., description="Unique notification identifier")
    workflow_id: str = Field(..., description="Associated workflow ID")
    user_id: str = Field(..., description="Target user ID")
    notification_type: str = Field(..., description="Type of notification")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    is_read: bool = Field(False, description="Whether notification has been read")
    created_at: datetime = Field(..., description="Notification creation timestamp")
    read_at: Optional[datetime] = Field(None, description="Notification read timestamp")








