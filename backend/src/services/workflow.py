"""
Workflow Engine for invoice approval workflows
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, UTC
from enum import Enum
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.user import User, UserRole
from src.models.invoice import Invoice, InvoiceStatus
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from src.core.config import settings

logger = logging.getLogger(__name__)

class WorkflowStepType(str, Enum):
    """Types of workflow steps"""
    APPROVAL = "approval"
    DELEGATION = "delegation"
    NOTIFICATION = "notification"
    CONDITIONAL = "conditional"

class WorkflowStepStatus(str, Enum):
    """Status of workflow steps"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    DELEGATED = "delegated"

class WorkflowEngine:
    """Workflow engine for managing invoice approval processes"""
    
    def __init__(self):
        self.default_approval_thresholds = {
            "basic": 1000.0,      # Basic tier: $1000
            "professional": 5000.0, # Professional tier: $5000
            "enterprise": 25000.0   # Enterprise tier: $25000
        }
    
    def create_approval_workflow(self, invoice: Invoice, company_tier: str, db: Session) -> Dict[str, Any]:
        """Create approval workflow for an invoice"""
        logger.info(f"Creating approval workflow for invoice {invoice.invoice_number}")
        
        # Determine approval threshold based on company tier
        threshold = self.default_approval_thresholds.get(company_tier, 1000.0)
        
        # Create workflow steps
        workflow_steps = []
        
        if invoice.total_amount <= threshold:
            # Single approver for amounts below threshold
            workflow_steps.append({
                "step_id": str(uuid.uuid4()),
                "type": WorkflowStepType.APPROVAL,
                "order": 1,
                "approver_role": UserRole.MANAGER,
                "threshold": threshold,
                "status": WorkflowStepStatus.PENDING,
                "created_at": datetime.now(UTC).isoformat()
            })
        else:
            # Multi-step approval for amounts above threshold
            workflow_steps.extend([
                {
                    "step_id": str(uuid.uuid4()),
                    "type": WorkflowStepType.APPROVAL,
                    "order": 1,
                    "approver_role": UserRole.MANAGER,
                    "threshold": threshold,
                    "status": WorkflowStepStatus.PENDING,
                    "created_at": datetime.now(UTC).isoformat()
                },
                {
                    "step_id": str(uuid.uuid4()),
                    "type": WorkflowStepType.APPROVAL,
                    "order": 2,
                    "approver_role": UserRole.ADMIN,
                    "threshold": None,  # No threshold for final approver
                    "status": WorkflowStepStatus.PENDING,
                    "created_at": datetime.now(UTC).isoformat()
                }
            ])
        
        # Update invoice with workflow
        invoice.workflow_data = {
            "workflow_id": str(uuid.uuid4()),
            "steps": workflow_steps,
            "current_step": 1,
            "status": "active",
            "created_at": datetime.now(UTC).isoformat(),
            "threshold": threshold
        }
        
        # Set current approver
        if workflow_steps:
            first_step = workflow_steps[0]
            invoice.current_approver_id = self._find_approver(
                invoice.company_id, 
                first_step["approver_role"], 
                db
            )
        
        # Update invoice status
        invoice.status = InvoiceStatus.PENDING_APPROVAL
        
        return invoice.workflow_data
    
    def _find_approver(self, company_id: uuid.UUID, role: UserRole, db: Session) -> Optional[uuid.UUID]:
        """Find an approver with the specified role in the company"""
        approver = db.query(User).filter(
            and_(
                User.company_id == company_id,
                User.role == role,
                User.status == "active"
            )
        ).first()
        
        return approver.id if approver else None
    
    def get_next_approver(self, invoice: Invoice, db: Session) -> Optional[User]:
        """Get the next approver in the workflow"""
        if not invoice.workflow_data or "steps" not in invoice.workflow_data:
            return None
        
        current_step = invoice.workflow_data.get("current_step", 1)
        steps = invoice.workflow_data["steps"]
        
        # Find current step
        current_step_data = next(
            (step for step in steps if step["order"] == current_step), 
            None
        )
        
        if not current_step_data:
            return None
        
        # Check if current step is completed
        if current_step_data["status"] == WorkflowStepStatus.COMPLETED:
            # Move to next step
            next_step = current_step + 1
            next_step_data = next(
                (step for step in steps if step["order"] == next_step), 
                None
            )
            
            if next_step_data:
                invoice.workflow_data["current_step"] = next_step
                approver_id = self._find_approver(
                    invoice.company_id,
                    next_step_data["approver_role"],
                    db
                )
                if approver_id:
                    invoice.current_approver_id = approver_id
                    return db.query(User).filter(User.id == approver_id).first()
            else:
                # Workflow completed
                invoice.workflow_data["status"] = "completed"
                invoice.workflow_data["completed_at"] = datetime.now(UTC).isoformat()
                return None
        
        return None
    
    def process_approval_sync(self, invoice: Invoice, approver: User, approved: bool, 
                             db: Session, reason: str = None) -> Dict[str, Any]:
        """Synchronous wrapper for process_approval for testing"""
        import asyncio
        
        # Use asyncio.run for a clean event loop
        action = "approve" if approved else "reject"
        return asyncio.run(
            self.process_approval(invoice.id, approver.id, action, db, reason)
        )
    
    async def process_approval(self, invoice_id, approver_id, action: str, 
                              db: Session, reason: str = None) -> Dict[str, Any]:
        """Process approval decision"""
        # Get invoice and approver
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        approver = db.query(User).filter(User.id == approver_id).first()
        if not approver:
            raise ValueError(f"Approver {approver_id} not found")
        
        logger.info(f"Processing approval decision for invoice {invoice.invoice_number}")
        
        if not invoice.workflow_data or "steps" not in invoice.workflow_data:
            raise ValueError("No workflow found for invoice")
        
        approved = action.lower() == "approve"
        
        current_step = invoice.workflow_data.get("current_step", 1)
        steps = invoice.workflow_data["steps"]
        
        # Find current step
        current_step_data = next(
            (step for step in steps if step["order"] == current_step), 
            None
        )
        
        if not current_step_data:
            raise ValueError("Current workflow step not found")
        
        # Update step status
        if approved:
            current_step_data["status"] = WorkflowStepStatus.COMPLETED
            current_step_data["completed_at"] = datetime.now(UTC).isoformat()
            current_step_data["approved_by"] = str(approver.id)
            
            # Check if this was the final step
            logger.info(f"Current step: {current_step}, Total steps: {len(steps)}")
            if current_step == len(steps):
                # Workflow completed successfully
                logger.info("Final step reached, completing workflow")
                invoice.status = InvoiceStatus.APPROVED
                invoice.approved_by_id = approver.id
                invoice.approved_at = datetime.now(UTC)
                invoice.workflow_data["status"] = "completed"
                invoice.workflow_data["completed_at"] = datetime.now(UTC).isoformat()
                # Mark the JSON field as dirty so SQLAlchemy knows it changed
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(invoice, "workflow_data")
                
                result = {
                    "status": "approved",
                    "message": "Invoice approved and workflow completed",
                    "workflow_status": "completed"
                }
            else:
                # Move to next step
                next_approver = self.get_next_approver(invoice, db)
                if next_approver:
                    result = {
                        "status": "approved",
                        "message": f"Step {current_step} approved, moved to step {current_step + 1}",
                        "next_approver": next_approver.email,
                        "workflow_status": "in_progress"
                    }
                else:
                    result = {
                        "status": "approved",
                        "message": "Step approved but no next approver found",
                        "workflow_status": "error"
                    }
        else:
            # Rejection
            current_step_data["status"] = WorkflowStepStatus.FAILED
            current_step_data["rejected_at"] = datetime.now(UTC).isoformat()
            current_step_data["rejected_by"] = str(approver.id)
            current_step_data["rejection_reason"] = reason
            
            invoice.status = InvoiceStatus.REJECTED
            invoice.rejection_reason = reason
            invoice.workflow_data["status"] = "rejected"
            invoice.workflow_data["rejected_at"] = datetime.now(UTC).isoformat()
            # Mark the JSON field as dirty so SQLAlchemy knows it changed
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(invoice, "workflow_data")
            
            result = {
                "status": "rejected",
                "message": f"Invoice rejected: {reason}",
                "workflow_status": "rejected"
            }
        
        # Update workflow data
        invoice.workflow_data["last_updated"] = datetime.now(UTC).isoformat()
        # Mark the JSON field as dirty so SQLAlchemy knows it changed
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(invoice, "workflow_data")
        
        # Commit changes
        db.commit()
        
        return result
    
    def delegate_approval(self, invoice: Invoice, from_user: User, to_user: User, 
                         reason: str, db: Session) -> Dict[str, Any]:
        """Delegate approval to another user"""
        logger.info(f"Delegating approval for invoice {invoice.invoice_number}")
        
        if not invoice.workflow_data or "steps" not in invoice.workflow_data:
            raise ValueError("No workflow found for invoice")
        
        current_step = invoice.workflow_data.get("current_step", 1)
        steps = invoice.workflow_data["steps"]
        
        # Find current step
        current_step_data = next(
            (step for step in steps if step["order"] == current_step), 
            None
        )
        
        if not current_step_data:
            raise ValueError("Current workflow step not found")
        
        # Check if delegation is allowed
        if current_step_data["type"] != WorkflowStepType.APPROVAL:
            raise ValueError("Only approval steps can be delegated")
        
        # Update step with delegation
        current_step_data["status"] = WorkflowStepStatus.DELEGATED
        current_step_data["delegated_at"] = datetime.now(UTC).isoformat()
        current_step_data["delegated_from"] = str(from_user.id)
        current_step_data["delegated_to"] = str(to_user.id)
        current_step_data["delegation_reason"] = reason
        
        # Update invoice current approver
        invoice.current_approver_id = to_user.id
        
        # Add delegation step
        delegation_step = {
            "step_id": str(uuid.uuid4()),
            "type": WorkflowStepType.DELEGATION,
            "order": current_step,
            "delegated_from": str(from_user.id),
            "delegated_to": str(to_user.id),
            "reason": reason,
            "status": WorkflowStepStatus.IN_PROGRESS,
            "created_at": datetime.now(UTC).isoformat()
        }
        
        invoice.workflow_data["steps"].append(delegation_step)
        
        return {
            "status": "delegated",
            "message": f"Approval delegated to {to_user.email}",
            "delegation_reason": reason,
            "workflow_status": "in_progress"
        }
    
    def get_workflow_summary(self, invoice: Invoice) -> Dict[str, Any]:
        """Get summary of workflow status"""
        if not invoice.workflow_data:
            return {"status": "no_workflow"}
        
        workflow = invoice.workflow_data
        steps = workflow.get("steps", [])
        
        completed_steps = [s for s in steps if s["status"] == WorkflowStepStatus.COMPLETED]
        pending_steps = [s for s in steps if s["status"] == WorkflowStepStatus.PENDING]
        failed_steps = [s for s in steps if s["status"] == WorkflowStepStatus.FAILED]
        
        return {
            "workflow_id": workflow.get("workflow_id"),
            "status": workflow.get("status"),
            "current_step": workflow.get("current_step"),
            "total_steps": len(steps),
            "completed_steps": len(completed_steps),
            "pending_steps": len(pending_steps),
            "failed_steps": len(failed_steps),
            "threshold": workflow.get("threshold"),
            "created_at": workflow.get("created_at"),
            "last_updated": workflow.get("last_updated"),
            "steps": steps
        }
    
    def can_user_approve(self, invoice: Invoice, user: User) -> bool:
        """Check if user can approve the current workflow step"""
        if not invoice.workflow_data or "steps" not in invoice.workflow_data:
            return False
        
        current_step = invoice.workflow_data.get("current_step", 1)
        steps = invoice.workflow_data["steps"]
        
        # Find current step
        current_step_data = next(
            (step for step in steps if step["order"] == current_step), 
            None
        )
        
        if not current_step_data:
            return False
        
        # Check if user is the current approver
        if invoice.current_approver_id != user.id:
            return False
        
        # Check if step is pending
        if current_step_data["status"] != WorkflowStepStatus.PENDING:
            return False
        
        # Check if user has required role
        required_role = current_step_data.get("approver_role")
        if required_role and user.role != required_role:
            return False
        
        return True
    
    def get_pending_approvals(self, user: User, db: Session) -> List[Invoice]:
        """Get list of invoices pending approval by user"""
        return db.query(Invoice).filter(
            and_(
                Invoice.current_approver_id == user.id,
                Invoice.status == InvoiceStatus.PENDING_APPROVAL,
                Invoice.company_id == user.company_id
            )
        ).all()
    
    def get_overdue_approvals(self, user: User, db: Session, days_overdue: int = 3) -> List[Invoice]:
        """Get list of overdue approvals"""
        cutoff_date = datetime.now(UTC) - timedelta(days=days_overdue)
        
        return db.query(Invoice).filter(
            and_(
                Invoice.current_approver_id == user.id,
                Invoice.status == InvoiceStatus.PENDING_APPROVAL,
                Invoice.company_id == user.company_id,
                Invoice.created_at < cutoff_date
            )
        ).all()
    
    async def get_workflow_status(self, invoice_id: str, db: Session) -> Dict[str, Any]:
        """Get workflow status for an invoice"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        return self.get_workflow_summary(invoice)
    
    async def create_workflow_for_invoice(self, invoice_id: str, company_tier: str, db: Session) -> Dict[str, Any]:
        """Create workflow for an invoice"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        workflow_data = self.create_approval_workflow(invoice, company_tier, db)
        db.commit()
        
        return workflow_data
