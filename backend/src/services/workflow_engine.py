"""
Advanced Workflow Engine for Invoice Processing
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


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


@dataclass
class WorkflowStep:
    """Individual workflow step"""
    step_id: str
    name: str
    description: str
    approver_role: str
    is_required: bool = True
    timeout_hours: int = 72
    auto_approve_threshold: Optional[float] = None


@dataclass
class WorkflowInstance:
    """Workflow instance for an invoice"""
    workflow_id: str
    invoice_id: str
    company_id: str
    status: WorkflowStatus
    current_step: int
    steps: List[WorkflowStep]
    created_at: datetime
    completed_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None


class WorkflowEngine:
    """Advanced workflow engine for invoice approval with AI-powered features"""
    
    def __init__(self):
        self.workflows = {}
        self.default_timeout = 72  # hours
        self.escalation_timeout = 24  # hours
        
        # AI-powered approval thresholds by company tier
        self.approval_thresholds = {
            "basic": {
                "auto_approval_limit": 1000.0,
                "manager_approval_limit": 5000.0,
                "director_approval_limit": 25000.0,
                "executive_approval_limit": 100000.0
            },
            "professional": {
                "auto_approval_limit": 2500.0,
                "manager_approval_limit": 10000.0,
                "director_approval_limit": 50000.0,
                "executive_approval_limit": 200000.0
            },
            "enterprise": {
                "auto_approval_limit": 25000.0,
                "manager_approval_limit": 50000.0,
                "director_approval_limit": 100000.0,
                "executive_approval_limit": 500000.0
            }
        }
        
        # AI analysis integration
        self.ai_service = None
        try:
            from services.advanced_ml_models import advanced_ml_service
            self.ai_service = advanced_ml_service
        except ImportError:
            logger.warning("Advanced ML service not available, using basic workflow logic")
    
    def create_workflow(self, invoice_id: str, company_id: str, invoice_amount: float, 
                       company_settings: Dict[str, Any]) -> WorkflowInstance:
        """Create a new workflow for an invoice"""
        try:
            workflow_id = f"wf_{invoice_id}_{int(datetime.now(UTC).timestamp())}"
            
            # Determine workflow steps based on amount and company settings
            steps = self._determine_workflow_steps(invoice_amount, company_settings)
            
            workflow = WorkflowInstance(
                workflow_id=workflow_id,
                invoice_id=invoice_id,
                company_id=company_id,
                status=WorkflowStatus.PENDING,
                current_step=0,
                steps=steps,
                created_at=datetime.now(UTC)
            )
            
            self.workflows[workflow_id] = workflow
            
            logger.info(f"Created workflow {workflow_id} for invoice {invoice_id}")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create workflow for invoice {invoice_id}: {str(e)}")
            raise
    
    async def process_approval_workflow(self, invoice, ai_analysis: Dict[str, Any], company) -> Dict[str, Any]:
        """Process AI-powered approval workflow with dynamic thresholds"""
        try:
            # Extract key information
            invoice_amount = float(invoice.total_amount)
            company_tier = company.tier if hasattr(company, 'tier') else "basic"
            
            # Get thresholds for company tier
            thresholds = self.get_approval_thresholds(company_tier)
            
            # Determine approval requirements based on AI analysis
            fraud_probability = ai_analysis.get("fraud_probability", 0.0)
            risk_score = ai_analysis.get("risk_score", 0.0)
            auto_approval_eligible = ai_analysis.get("auto_approval_eligible", False)
            
            # Check for fraud override
            fraud_override = fraud_probability > 0.7 or risk_score > 0.8
            
            # Determine approval level
            if fraud_override or not auto_approval_eligible:
                approval_required = True
                if invoice_amount <= thresholds["manager_approval_limit"]:
                    approval_level = "manager"
                    approval_chain = ["manager"]
                elif invoice_amount <= thresholds["director_approval_limit"]:
                    approval_level = "director"
                    approval_chain = ["manager", "director"]
                else:
                    approval_level = "executive"
                    approval_chain = ["manager", "director", "executive"]
            else:
                approval_required = False
                approval_level = "auto"
                approval_chain = []
            
            # Create workflow if approval required
            if approval_required:
                workflow = self.create_workflow(
                    invoice.id,
                    company.id,
                    invoice_amount,
                    {"company_tier": company_tier}
                )
                workflow_status = WorkflowStatus.PENDING
            else:
                workflow = None
                workflow_status = WorkflowStatus.COMPLETED
            
            return {
                "status": "auto_approved" if not approval_required else "pending_approval",
                "approval_required": approval_required,
                "approval_level": approval_level,
                "approval_chain": approval_chain,
                "workflow_id": workflow.workflow_id if workflow else None,
                "workflow_status": workflow_status,
                "ai_recommendation": ai_analysis.get("recommended_action", "auto_approve"),
                "fraud_detected": fraud_override,
                "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
                "threshold_analysis": ai_analysis.get("threshold_analysis", {}),
                "fraud_indicators": ai_analysis.get("fraud_indicators", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to process approval workflow: {str(e)}")
            raise
    
    def get_approval_thresholds(self, company_tier: str) -> Dict[str, float]:
        """Get approval thresholds for company tier"""
        return self.approval_thresholds.get(company_tier, self.approval_thresholds["basic"])
    
    async def process_approval_step(self, workflow_id: str, step_id: str, action: ApprovalAction, 
                                  approver_id: str, reason: str = None, delegate_to: str = None) -> Dict[str, Any]:
        """Process individual approval step"""
        try:
            workflow = self.get_workflow(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Find the step
            step = None
            for s in workflow.steps:
                if s.step_id == step_id:
                    step = s
                    break
            
            if not step:
                raise ValueError(f"Step {step_id} not found in workflow {workflow_id}")
            
            # Process the action
            if action == ApprovalAction.APPROVE:
                return await self._handle_approval(workflow, step, approver_id, reason)
            elif action == ApprovalAction.REJECT:
                return await self._handle_rejection(workflow, step, approver_id, reason)
            elif action == ApprovalAction.DELEGATE:
                return await self._handle_delegation(workflow, step, approver_id, delegate_to, reason)
            else:
                raise ValueError(f"Unsupported action: {action}")
                
        except Exception as e:
            logger.error(f"Failed to process approval step: {str(e)}")
            raise
    
    async def _handle_approval(self, workflow: WorkflowInstance, step: WorkflowStep, 
                             approver_id: str, reason: str) -> Dict[str, Any]:
        """Handle approval action"""
        # Check if this is the last step
        current_step_index = workflow.current_step
        is_last_step = current_step_index >= len(workflow.steps) - 1
        
        if is_last_step:
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now(UTC)
            workflow.approved_by = approver_id
            next_step = None
        else:
            workflow.current_step += 1
            next_step = workflow.steps[workflow.current_step].step_id if workflow.current_step < len(workflow.steps) else None
        
        return {
            "status": "approved",
            "step_status": "completed",
            "workflow_status": workflow.status,
            "next_step": next_step,
            "approved_by": approver_id,
            "approval_reason": reason
        }
    
    async def _handle_rejection(self, workflow: WorkflowInstance, step: WorkflowStep, 
                              approver_id: str, reason: str) -> Dict[str, Any]:
        """Handle rejection action"""
        workflow.status = WorkflowStatus.REJECTED
        workflow.completed_at = datetime.now(UTC)
        workflow.rejection_reason = reason
        
        return {
            "status": "rejected",
            "step_status": "rejected",
            "workflow_status": workflow.status,
            "rejected_by": approver_id,
            "rejection_reason": reason
        }
    
    async def _handle_delegation(self, workflow: WorkflowInstance, step: WorkflowStep, 
                               approver_id: str, delegate_to: str, reason: str) -> Dict[str, Any]:
        """Handle delegation action"""
        return {
            "status": "delegated",
            "step_status": "delegated",
            "workflow_status": workflow.status,
            "delegated_by": approver_id,
            "delegated_to": delegate_to,
            "delegation_reason": reason
        }
    
    async def handle_workflow_timeout(self, workflow_id: str) -> Dict[str, Any]:
        """Handle workflow timeout and escalation"""
        try:
            workflow = self.get_workflow(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Check if workflow has timed out
            current_time = datetime.now(UTC)
            time_since_creation = current_time - workflow.created_at
            
            # Find current step and check timeout
            if workflow.current_step < len(workflow.steps):
                current_step = workflow.steps[workflow.current_step]
                timeout_threshold = timedelta(hours=current_step.timeout_hours)
                
                if time_since_creation > timeout_threshold:
                    # Escalate workflow
                    workflow.status = WorkflowStatus.IN_PROGRESS  # Mark as escalated
                    
                    return {
                        "status": "escalated",
                        "timeout_detected": True,
                        "escalation_reason": "timeout_exceeded",
                        "timeout_duration_hours": time_since_creation.total_seconds() / 3600,
                        "workflow_status": workflow.status
                    }
            
            return {
                "status": "active",
                "timeout_detected": False,
                "workflow_status": workflow.status
            }
            
        except Exception as e:
            logger.error(f"Failed to handle workflow timeout: {str(e)}")
            raise
    
    async def create_audit_trail(self, workflow_id: str, action: str, description: str, user_id: str) -> Dict[str, Any]:
        """Create audit trail entry for workflow action"""
        try:
            # In a real implementation, this would save to the database
            audit_entry = {
                "workflow_id": workflow_id,
                "action": action,
                "description": description,
                "user_id": user_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            logger.info(f"Audit trail created: {action} for workflow {workflow_id}")
            
            return {
                "status": "success",
                "audit_entry_created": True,
                "audit_entry": audit_entry
            }
            
        except Exception as e:
            logger.error(f"Failed to create audit trail: {str(e)}")
            raise
    
    async def process_bulk_workflows(self, invoices: List, ai_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process multiple invoices in bulk"""
        try:
            results = []
            for invoice in invoices:
                result = await self.process_approval_workflow(invoice, ai_analysis, invoice.company)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process bulk workflows: {str(e)}")
            raise
    
    def _determine_workflow_steps(self, amount: float, company_settings: Dict[str, Any]) -> List[WorkflowStep]:
        """Determine workflow steps based on invoice amount and company settings"""
        steps = []
        
        # Get approval thresholds from company settings
        manager_threshold = company_settings.get("manager_approval_threshold", 1000)
        director_threshold = company_settings.get("director_approval_threshold", 5000)
        cfo_threshold = company_settings.get("cfo_approval_threshold", 25000)
        
        # Always start with preparer review
        steps.append(WorkflowStep(
            step_id="preparer_review",
            name="Preparer Review",
            description="Initial review by invoice preparer",
            approver_role="preparer",
            timeout_hours=24
        ))
        
        # Add approval steps based on amount
        if amount >= cfo_threshold:
            steps.extend([
                WorkflowStep(
                    step_id="manager_approval",
                    name="Manager Approval",
                    description="Manager approval required",
                    approver_role="manager",
                    timeout_hours=self.default_timeout
                ),
                WorkflowStep(
                    step_id="director_approval",
                    name="Director Approval",
                    description="Director approval required",
                    approver_role="director",
                    timeout_hours=self.default_timeout
                ),
                WorkflowStep(
                    step_id="cfo_approval",
                    name="CFO Approval",
                    description="CFO approval required for large amounts",
                    approver_role="cfo",
                    timeout_hours=self.default_timeout
                )
            ])
        elif amount >= director_threshold:
            steps.extend([
                WorkflowStep(
                    step_id="manager_approval",
                    name="Manager Approval",
                    description="Manager approval required",
                    approver_role="manager",
                    timeout_hours=self.default_timeout
                ),
                WorkflowStep(
                    step_id="director_approval",
                    name="Director Approval",
                    description="Director approval required",
                    approver_role="director",
                    timeout_hours=self.default_timeout
                )
            ])
        elif amount >= manager_threshold:
            steps.append(WorkflowStep(
                step_id="manager_approval",
                name="Manager Approval",
                description="Manager approval required",
                approver_role="manager",
                timeout_hours=self.default_timeout
            ))
        
        # Add final processing step
        steps.append(WorkflowStep(
            step_id="final_processing",
            name="Final Processing",
            description="Final processing and ERP posting",
            approver_role="system",
            timeout_hours=1
        ))
        
        return steps
    
    def process_approval(self, workflow_id: str, user_id: str, action: ApprovalAction, 
                        comments: str = "", delegation_user_id: str = None) -> Dict[str, Any]:
        """Process an approval action"""
        try:
            if workflow_id not in self.workflows:
                return {"status": "error", "message": "Workflow not found"}
            
            workflow = self.workflows[workflow_id]
            
            if workflow.status != WorkflowStatus.IN_PROGRESS:
                return {"status": "error", "message": "Workflow is not active"}
            
            current_step = workflow.steps[workflow.current_step]
            
            if action == ApprovalAction.APPROVE:
                return self._process_approval(workflow, user_id, comments)
            elif action == ApprovalAction.REJECT:
                return self._process_rejection(workflow, user_id, comments)
            elif action == ApprovalAction.REQUEST_INFO:
                return self._process_info_request(workflow, user_id, comments)
            elif action == ApprovalAction.DELEGATE:
                return self._process_delegation(workflow, user_id, delegation_user_id, comments)
            elif action == ApprovalAction.ESCALATE:
                return self._process_escalation(workflow, user_id, comments)
            else:
                return {"status": "error", "message": "Invalid action"}
                
        except Exception as e:
            logger.error(f"Failed to process approval for workflow {workflow_id}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _process_approval(self, workflow: WorkflowInstance, user_id: str, comments: str) -> Dict[str, Any]:
        """Process approval action"""
        try:
            # Move to next step
            workflow.current_step += 1
            
            if workflow.current_step >= len(workflow.steps):
                # Workflow completed
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now(UTC)
                workflow.approved_by = user_id
                
                logger.info(f"Workflow {workflow.workflow_id} completed successfully")
                return {
                    "status": "success",
                    "message": "Invoice approved and workflow completed",
                    "workflow_status": workflow.status,
                    "next_action": "erp_posting"
                }
            else:
                # Move to next step
                next_step = workflow.steps[workflow.current_step]
                
                logger.info(f"Workflow {workflow.workflow_id} moved to step: {next_step.name}")
                return {
                    "status": "success",
                    "message": f"Approved, moved to {next_step.name}",
                    "workflow_status": workflow.status,
                    "current_step": workflow.current_step,
                    "next_step": {
                        "step_id": next_step.step_id,
                        "name": next_step.name,
                        "description": next_step.description,
                        "approver_role": next_step.approver_role,
                        "timeout_hours": next_step.timeout_hours
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to process approval: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _process_rejection(self, workflow: WorkflowInstance, user_id: str, comments: str) -> Dict[str, Any]:
        """Process rejection action"""
        try:
            workflow.status = WorkflowStatus.REJECTED
            workflow.completed_at = datetime.now(UTC)
            workflow.rejection_reason = comments
            
            logger.info(f"Workflow {workflow.workflow_id} rejected by user {user_id}")
            return {
                "status": "success",
                "message": "Invoice rejected",
                "workflow_status": workflow.status,
                "rejection_reason": comments
            }
            
        except Exception as e:
            logger.error(f"Failed to process rejection: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _process_info_request(self, workflow: WorkflowInstance, user_id: str, comments: str) -> Dict[str, Any]:
        """Process information request action"""
        try:
            # Keep workflow in current step but add comments
            logger.info(f"Information requested for workflow {workflow.workflow_id} by user {user_id}")
            return {
                "status": "success",
                "message": "Information requested from preparer",
                "workflow_status": workflow.status,
                "current_step": workflow.current_step,
                "comments": comments
            }
            
        except Exception as e:
            logger.error(f"Failed to process info request: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _process_delegation(self, workflow: WorkflowInstance, user_id: str, 
                           delegation_user_id: str, comments: str) -> Dict[str, Any]:
        """Process delegation action"""
        try:
            if not delegation_user_id:
                return {"status": "error", "message": "Delegation user ID required"}
            
            # Update current step with delegated user
            current_step = workflow.steps[workflow.current_step]
            logger.info(f"Workflow {workflow.workflow_id} delegated to user {delegation_user_id}")
            
            return {
                "status": "success",
                "message": f"Workflow delegated to user {delegation_user_id}",
                "workflow_status": workflow.status,
                "current_step": workflow.current_step,
                "delegated_to": delegation_user_id,
                "comments": comments
            }
            
        except Exception as e:
            logger.error(f"Failed to process delegation: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _process_escalation(self, workflow: WorkflowInstance, user_id: str, comments: str) -> Dict[str, Any]:
        """Process escalation action"""
        try:
            # Move to next higher level approver
            current_step = workflow.steps[workflow.current_step]
            
            # Find next higher level role
            role_hierarchy = ["preparer", "manager", "director", "cfo", "ceo"]
            current_role_index = role_hierarchy.index(current_step.approver_role)
            
            if current_role_index < len(role_hierarchy) - 1:
                next_role = role_hierarchy[current_role_index + 1]
                
                # Create escalation step
                escalation_step = WorkflowStep(
                    step_id=f"escalated_{current_step.step_id}",
                    name=f"Escalated {current_step.name}",
                    description=f"Escalated to {next_role.title()}",
                    approver_role=next_role,
                    timeout_hours=self.escalation_timeout
                )
                
                # Insert escalation step
                workflow.steps.insert(workflow.current_step + 1, escalation_step)
                
                logger.info(f"Workflow {workflow.workflow_id} escalated to {next_role}")
                return {
                    "status": "success",
                    "message": f"Workflow escalated to {next_role.title()}",
                    "workflow_status": workflow.status,
                    "current_step": workflow.current_step,
                    "escalated_to": next_role,
                    "comments": comments
                }
            else:
                return {"status": "error", "message": "Cannot escalate further"}
                
        except Exception as e:
            logger.error(f"Failed to process escalation: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def check_timeouts(self) -> List[Dict[str, Any]]:
        """Check for timed out workflows"""
        try:
            timed_out_workflows = []
            current_time = datetime.now(UTC)
            
            for workflow_id, workflow in self.workflows.items():
                if workflow.status == WorkflowStatus.IN_PROGRESS:
                    current_step = workflow.steps[workflow.current_step]
                    timeout_time = workflow.created_at + timedelta(hours=current_step.timeout_hours)
                    
                    if current_time > timeout_time:
                        # Workflow timed out
                        workflow.status = WorkflowStatus.ERROR
                        workflow.completed_at = current_time
                        workflow.rejection_reason = f"Timed out after {current_step.timeout_hours} hours"
                        
                        timed_out_workflows.append({
                            "workflow_id": workflow_id,
                            "invoice_id": workflow.invoice_id,
                            "timed_out_step": current_step.name,
                            "timeout_hours": current_step.timeout_hours
                        })
                        
                        logger.warning(f"Workflow {workflow_id} timed out at step: {current_step.name}")
            
            return timed_out_workflows
            
        except Exception as e:
            logger.error(f"Failed to check timeouts: {str(e)}")
            return []
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        try:
            if workflow_id not in self.workflows:
                return None
            
            workflow = self.workflows[workflow_id]
            
            return {
                "workflow_id": workflow_id,
                "invoice_id": workflow.invoice_id,
                "company_id": workflow.company_id,
                "status": workflow.status,
                "current_step": workflow.current_step,
                "total_steps": len(workflow.steps),
                "created_at": workflow.created_at.isoformat(),
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                "approved_by": workflow.approved_by,
                "rejection_reason": workflow.rejection_reason,
                "current_step_info": {
                    "step_id": workflow.steps[workflow.current_step].step_id,
                    "name": workflow.steps[workflow.current_step].name,
                    "description": workflow.steps[workflow.current_step].description,
                    "approver_role": workflow.steps[workflow.current_step].approver_role,
                    "timeout_hours": workflow.steps[workflow.current_step].timeout_hours
                } if workflow.current_step < len(workflow.steps) else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            return None


# Global instance
workflow_engine = WorkflowEngine()
