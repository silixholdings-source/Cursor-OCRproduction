"""
Workflow Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.database import get_db
from core.auth import auth_manager
from src.models.user import User, UserRole
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from services.workflow_engine import workflow_engine, WorkflowStatus, ApprovalAction
from schemas.workflow import (
    WorkflowCreateRequest,
    WorkflowResponse,
    ApprovalActionRequest,
    WorkflowStatusResponse,
    WorkflowStepResponse
)

router = APIRouter()


@router.post("/create", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowCreateRequest,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new approval workflow for an invoice"""
    try:
        # Validate user has permission to create workflows
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create workflows"
            )
        
        # Create workflow
        workflow = workflow_engine.create_workflow(
            invoice_id=request.invoice_id,
            company_id=str(current_user.company_id),
            invoice_amount=request.invoice_amount,
            company_settings=request.company_settings
        )
        
        # Create audit log
        audit_log = AuditLog(
            company_id=current_user.company_id,
            user_id=current_user.id,
            action=AuditAction.CREATE,
            resource_type=AuditResourceType.WORKFLOW,
            resource_id=workflow.workflow_id,
            details={
                "invoice_id": request.invoice_id,
                "workflow_id": workflow.workflow_id,
                "invoice_amount": request.invoice_amount
            }
        )
        db.add(audit_log)
        db.commit()
        
        return WorkflowResponse(
            workflow_id=workflow.workflow_id,
            invoice_id=workflow.invoice_id,
            company_id=workflow.company_id,
            status=workflow.status,
            current_step=workflow.current_step,
            total_steps=len(workflow.steps),
            created_at=workflow.created_at,
            steps=[
                WorkflowStepResponse(
                    step_id=step.step_id,
                    name=step.name,
                    description=step.description,
                    approver_role=step.approver_role,
                    is_required=step.is_required,
                    timeout_hours=step.timeout_hours
                )
                for step in workflow.steps
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.post("/{workflow_id}/approve", response_model=Dict[str, Any])
async def process_approval(
    workflow_id: str,
    request: ApprovalActionRequest,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Process approval action for a workflow"""
    try:
        # Get workflow status
        workflow_status = workflow_engine.get_workflow_status(workflow_id)
        if not workflow_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Check if user has permission for current step
        current_step_info = workflow_status.get("current_step_info")
        if not current_step_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow is not active"
            )
        
        # Process approval action
        result = workflow_engine.process_approval(
            workflow_id=workflow_id,
            user_id=str(current_user.id),
            action=ApprovalAction(request.action),
            comments=request.comments,
            delegation_user_id=request.delegation_user_id
        )
        
        if result["status"] == "success":
            # Create audit log
            audit_log = AuditLog(
                company_id=current_user.company_id,
                user_id=current_user.id,
                action=AuditAction.UPDATE,
                resource_type=AuditResourceType.WORKFLOW,
                resource_id=workflow_id,
                details={
                    "action": request.action,
                    "comments": request.comments,
                    "delegation_user_id": request.delegation_user_id,
                    "result": result
                }
            )
            db.add(audit_log)
            db.commit()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process approval: {str(e)}"
        )


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get workflow status"""
    try:
        workflow_status = workflow_engine.get_workflow_status(workflow_id)
        
        if not workflow_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Check if user has access to this workflow
        if workflow_status["company_id"] != str(current_user.company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workflow"
            )
        
        return WorkflowStatusResponse(
            workflow_id=workflow_status["workflow_id"],
            invoice_id=workflow_status["invoice_id"],
            company_id=workflow_status["company_id"],
            status=workflow_status["status"],
            current_step=workflow_status["current_step"],
            total_steps=workflow_status["total_steps"],
            created_at=workflow_status["created_at"],
            completed_at=workflow_status["completed_at"],
            approved_by=workflow_status["approved_by"],
            rejection_reason=workflow_status["rejection_reason"],
            current_step_info=workflow_status["current_step_info"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )


@router.get("/company/{company_id}/workflows", response_model=List[WorkflowStatusResponse])
async def list_company_workflows(
    company_id: str,
    status_filter: Optional[WorkflowStatus] = None,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """List workflows for a company"""
    try:
        # Check if user has access to company workflows
        if str(current_user.company_id) != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to company workflows"
            )
        
        # Get all workflows for company
        workflows = []
        for workflow_id, workflow in workflow_engine.workflows.items():
            if workflow.company_id == company_id:
                if status_filter is None or workflow.status == status_filter:
                    workflow_status = workflow_engine.get_workflow_status(workflow_id)
                    if workflow_status:
                        workflows.append(WorkflowStatusResponse(
                            workflow_id=workflow_status["workflow_id"],
                            invoice_id=workflow_status["invoice_id"],
                            company_id=workflow_status["company_id"],
                            status=workflow_status["status"],
                            current_step=workflow_status["current_step"],
                            total_steps=workflow_status["total_steps"],
                            created_at=workflow_status["created_at"],
                            completed_at=workflow_status["completed_at"],
                            approved_by=workflow_status["approved_by"],
                            rejection_reason=workflow_status["rejection_reason"],
                            current_step_info=workflow_status["current_step_info"]
                        ))
        
        return workflows
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )


@router.post("/check-timeouts", response_model=List[Dict[str, Any]])
async def check_workflow_timeouts(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Check for timed out workflows"""
    try:
        # Only admins can check timeouts
        if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to check timeouts"
            )
        
        timed_out_workflows = workflow_engine.check_timeouts()
        
        # Filter to only company workflows
        company_timed_out = [
            workflow for workflow in timed_out_workflows
            if workflow_engine.get_workflow_status(workflow["workflow_id"])["company_id"] == str(current_user.company_id)
        ]
        
        return company_timed_out
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check timeouts: {str(e)}"
        )


@router.get("/user/{user_id}/pending", response_model=List[WorkflowStatusResponse])
async def get_user_pending_workflows(
    user_id: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending workflows for a specific user"""
    try:
        # Check if user has permission to view user workflows
        if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view user workflows"
            )
        
        pending_workflows = []
        for workflow_id, workflow in workflow_engine.workflows.items():
            if workflow.status == WorkflowStatus.IN_PROGRESS:
                current_step_info = workflow.steps[workflow.current_step] if workflow.current_step < len(workflow.steps) else None
                
                # Check if this user is responsible for current step
                if current_step_info and current_step_info.approver_role == current_user.role.value:
                    workflow_status = workflow_engine.get_workflow_status(workflow_id)
                    if workflow_status:
                        pending_workflows.append(WorkflowStatusResponse(
                            workflow_id=workflow_status["workflow_id"],
                            invoice_id=workflow_status["invoice_id"],
                            company_id=workflow_status["company_id"],
                            status=workflow_status["status"],
                            current_step=workflow_status["current_step"],
                            total_steps=workflow_status["total_steps"],
                            created_at=workflow_status["created_at"],
                            completed_at=workflow_status["completed_at"],
                            approved_by=workflow_status["approved_by"],
                            rejection_reason=workflow_status["rejection_reason"],
                            current_step_info=workflow_status["current_step_info"]
                        ))
        
        return pending_workflows
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending workflows: {str(e)}"
        )








