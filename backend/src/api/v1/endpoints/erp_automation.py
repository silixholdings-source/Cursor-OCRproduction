"""
ERP Automation Endpoints - Fully Automated ERP Integration Management
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime
import json

from core.database import get_db
from core.auth import auth_manager
from src.models.user import User, UserRole
from src.models.invoice import Invoice, InvoiceStatus
from src.models.company import Company
from services.erp_automation import erp_automation, AutomationRule

router = APIRouter()

@router.post("/auto-sync/{invoice_id}")
async def trigger_auto_sync(
    invoice_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger automated ERP sync for a specific invoice"""
    try:
        # Validate permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for ERP operations"
            )
        
        # Verify invoice exists and is approved
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        if invoice.status != InvoiceStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice must be approved before ERP sync"
            )
        
        # Trigger automated sync in background
        background_tasks.add_task(
            erp_automation.auto_sync_on_approval,
            invoice_id,
            str(current_user.company_id),
            db
        )
        
        return {
            "status": "success",
            "message": "Automated ERP sync initiated",
            "invoice_id": invoice_id,
            "initiated_at": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger auto-sync: {str(e)}"
        )

@router.post("/bulk-auto-sync")
async def trigger_bulk_auto_sync(
    request_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger automated ERP sync for multiple invoices"""
    try:
        invoice_ids = request_data.get("invoice_ids", [])
        
        if not invoice_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No invoice IDs provided"
            )
        
        # Validate permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for bulk ERP operations"
            )
        
        # Verify all invoices exist and are approved
        invoices = db.query(Invoice).filter(
            Invoice.id.in_(invoice_ids),
            Invoice.company_id == current_user.company_id,
            Invoice.status == InvoiceStatus.APPROVED
        ).all()
        
        if len(invoices) != len(invoice_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some invoices not found or not approved"
            )
        
        # Trigger bulk sync in background
        for invoice in invoices:
            background_tasks.add_task(
                erp_automation.auto_sync_on_approval,
                str(invoice.id),
                str(current_user.company_id),
                db
            )
        
        return {
            "status": "success",
            "message": f"Automated ERP sync initiated for {len(invoices)} invoices",
            "invoice_count": len(invoices),
            "initiated_at": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger bulk auto-sync: {str(e)}"
        )

@router.get("/automation-status")
async def get_automation_status(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get current ERP automation status"""
    try:
        # Get company ERP configuration
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Check automation rules status
        automation_status = {}
        for rule in AutomationRule:
            automation_status[rule.value] = erp_automation.automation_rules.get(rule, False)
        
        # Get ERP system status
        erp_systems = {}
        
        if company.erp_dynamics_gp_enabled:
            erp_systems["dynamics_gp"] = {
                "enabled": True,
                "status": "active",
                "last_sync": company.erp_dynamics_gp_last_sync.isoformat() if company.erp_dynamics_gp_last_sync else None,
                "auto_sync": automation_status["auto_sync_on_approval"]
            }
        
        if company.erp_sap_enabled:
            erp_systems["sap"] = {
                "enabled": True,
                "status": "active",
                "last_sync": company.erp_sap_last_sync.isoformat() if company.erp_sap_last_sync else None,
                "auto_sync": automation_status["auto_sync_on_approval"]
            }
        
        if company.erp_quickbooks_enabled:
            erp_systems["quickbooks"] = {
                "enabled": True,
                "status": "active",
                "last_sync": company.erp_quickbooks_last_sync.isoformat() if company.erp_quickbooks_last_sync else None,
                "auto_sync": automation_status["auto_sync_on_approval"]
            }
        
        if company.erp_xero_enabled:
            erp_systems["xero"] = {
                "enabled": True,
                "status": "active",
                "last_sync": company.erp_xero_last_sync.isoformat() if company.erp_xero_last_sync else None,
                "auto_sync": automation_status["auto_sync_on_approval"]
            }
        
        return {
            "automation_enabled": True,
            "automation_rules": automation_status,
            "erp_systems": erp_systems,
            "monitoring_active": erp_automation.monitoring_active,
            "last_health_check": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get automation status: {str(e)}"
        )

@router.post("/configure-automation")
async def configure_automation(
    config_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Configure ERP automation rules"""
    try:
        # Validate permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can configure automation rules"
            )
        
        # Update automation rules
        for rule_name, enabled in config_data.get("rules", {}).items():
            if rule_name in [rule.value for rule in AutomationRule]:
                erp_automation.automation_rules[AutomationRule(rule_name)] = enabled
        
        return {
            "status": "success",
            "message": "Automation rules updated successfully",
            "updated_rules": config_data.get("rules", {}),
            "updated_at": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure automation: {str(e)}"
        )

@router.get("/sync-history")
async def get_sync_history(
    limit: int = 50,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get ERP sync history for the company"""
    try:
        # Get recent invoices with ERP sync data
        invoices = db.query(Invoice).filter(
            Invoice.company_id == current_user.company_id,
            Invoice.erp_synced_at.isnot(None)
        ).order_by(Invoice.erp_synced_at.desc()).limit(limit).all()
        
        sync_history = []
        for invoice in invoices:
            sync_results = {}
            if invoice.erp_sync_results:
                try:
                    sync_results = json.loads(invoice.erp_sync_results)
                except:
                    sync_results = {}
            
            sync_history.append({
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "vendor": invoice.supplier_name,
                "amount": float(invoice.total_amount),
                "sync_status": invoice.erp_sync_status,
                "synced_at": invoice.erp_synced_at.isoformat() if invoice.erp_synced_at else None,
                "retry_count": invoice.erp_retry_count or 0,
                "erp_systems": list(sync_results.keys()),
                "sync_results": sync_results
            })
        
        return {
            "sync_history": sync_history,
            "total_synced": len(sync_history),
            "generated_at": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sync history: {str(e)}"
        )

