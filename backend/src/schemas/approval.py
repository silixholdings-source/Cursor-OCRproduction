"""
Approval-related Pydantic schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ApprovalBase(BaseModel):
    """Base approval schema"""
    invoice_id: UUID
    priority: str = Field(..., description="Approval priority: high, medium, low")
    description: Optional[str] = None

class ApprovalCreate(ApprovalBase):
    """Schema for creating approval requests"""
    pass

class ApprovalUpdate(BaseModel):
    """Schema for updating approval requests"""
    priority: Optional[str] = None
    description: Optional[str] = None

class ApprovalAction(BaseModel):
    """Schema for approval actions"""
    action: str = Field(..., description="Action to take: approve, reject")
    reason: Optional[str] = Field(None, description="Reason for rejection")
    notes: Optional[str] = None

class ApprovalResponse(BaseModel):
    """Schema for approval response"""
    id: str
    invoice_id: str
    vendor: str
    amount: float
    submitted_by: str
    submitted_at: datetime
    due_date: Optional[datetime] = None
    priority: str
    category: str
    description: str
    
    model_config = ConfigDict(
        from_attributes=True
    )

class ApprovalListResponse(BaseModel):
    """Schema for approval list response"""
    approvals: List[ApprovalResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class ApprovalWorkflow(BaseModel):
    """Schema for approval workflow"""
    id: str
    name: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class ApprovalWorkflowCreate(BaseModel):
    """Schema for creating approval workflow"""
    name: str
    description: Optional[str] = None
    steps: List[Dict[str, Any]]

class ApprovalWorkflowUpdate(BaseModel):
    """Schema for updating approval workflow"""
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

class ApprovalStep(BaseModel):
    """Schema for approval step"""
    id: str
    workflow_id: str
    step_order: int
    approver_role: str
    approval_type: str
    conditions: Optional[Dict[str, Any]] = None
    is_required: bool = True

class ApprovalStepCreate(BaseModel):
    """Schema for creating approval step"""
    workflow_id: str
    step_order: int
    approver_role: str
    approval_type: str
    conditions: Optional[Dict[str, Any]] = None
    is_required: bool = True

class ApprovalStepUpdate(BaseModel):
    """Schema for updating approval step"""
    step_order: Optional[int] = None
    approver_role: Optional[str] = None
    approval_type: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    is_required: Optional[bool] = None

class ApprovalAudit(BaseModel):
    """Schema for approval audit trail"""
    id: str
    approval_id: str
    action: str
    performed_by: str
    performed_at: datetime
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class ApprovalStats(BaseModel):
    """Schema for approval statistics"""
    total_approvals: int
    pending_approvals: int
    approved_count: int
    rejected_count: int
    average_processing_time: float
    approval_rate: float
    rejection_rate: float

class ApprovalNotification(BaseModel):
    """Schema for approval notifications"""
    id: str
    approval_id: str
    recipient_id: str
    notification_type: str
    message: str
    sent_at: datetime
    is_read: bool = False

class ApprovalEscalation(BaseModel):
    """Schema for approval escalation"""
    id: str
    approval_id: str
    escalated_at: datetime
    escalated_by: str
    escalation_reason: str
    new_approver_id: str
    is_resolved: bool = False

class ApprovalTemplate(BaseModel):
    """Schema for approval template"""
    id: str
    name: str
    description: Optional[str] = None
    template_data: Dict[str, Any]
    is_default: bool = False
    created_at: datetime
    updated_at: datetime

class ApprovalTemplateCreate(BaseModel):
    """Schema for creating approval template"""
    name: str
    description: Optional[str] = None
    template_data: Dict[str, Any]
    is_default: bool = False

class ApprovalTemplateUpdate(BaseModel):
    """Schema for updating approval template"""
    name: Optional[str] = None
    description: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None