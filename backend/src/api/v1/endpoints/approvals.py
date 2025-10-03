"""
Approvals Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from core.database import get_db
from core.auth import auth_manager
from src.models.invoice import Invoice, InvoiceStatus
from src.models.user import User, UserRole
from schemas.approval import ApprovalResponse, ApprovalListResponse, ApprovalAction

router = APIRouter()

@router.get("/pending")
async def get_pending_approvals(
    limit: int = Query(10, ge=1, le=50, description="Number of pending approvals to return"),
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending approvals for dashboard display"""
    try:
        # Get invoices pending approval for the user's company
        pending_invoices = db.query(Invoice)\
            .filter(
                Invoice.company_id == current_user.company_id,
                Invoice.status == InvoiceStatus.PENDING_APPROVAL
            )\
            .order_by(Invoice.created_at.desc())\
            .limit(limit)\
            .all()
        
        # Transform to frontend format
        approval_data = []
        for invoice in pending_invoices:
            approval_data.append({
                "id": f"APR-{str(invoice.id)[:8]}",
                "invoiceId": str(invoice.id),
                "vendor": invoice.supplier_name,
                "amount": float(invoice.total_amount),
                "submittedBy": invoice.created_by_name or "Unknown",
                "submittedAt": invoice.created_at.isoformat() if invoice.created_at else None,
                "dueDate": invoice.due_date.isoformat() if invoice.due_date else None,
                "priority": "high" if invoice.total_amount > 1000 else "medium" if invoice.total_amount > 500 else "low",
                "category": invoice.category or "General",
                "description": invoice.description or f"Invoice {invoice.invoice_number}"
            })
        
        return {
            "approvals": approval_data,
            "total": len(approval_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending approvals: {str(e)}"
        )

@router.post("/{approval_id}/approve")
async def approve_invoice(
    approval_id: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a pending invoice"""
    try:
        # Extract invoice ID from approval ID
        invoice_id = approval_id.replace("APR-", "")
        
        # Get the invoice
        invoice = db.query(Invoice)\
            .filter(
                Invoice.company_id == current_user.company_id,
                Invoice.id.like(f"{invoice_id}%")
            )\
            .first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Update invoice status
        invoice.status = InvoiceStatus.APPROVED
        invoice.approved_by = current_user.id
        invoice.approved_at = datetime.now(UTC)
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Invoice {invoice.invoice_number} approved successfully",
            "invoice_id": str(invoice.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve invoice: {str(e)}"
        )

@router.post("/{approval_id}/reject")
async def reject_invoice(
    approval_id: str,
    rejection_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a pending invoice"""
    try:
        # Extract invoice ID from approval ID
        invoice_id = approval_id.replace("APR-", "")
        
        # Get the invoice
        invoice = db.query(Invoice)\
            .filter(
                Invoice.company_id == current_user.company_id,
                Invoice.id.like(f"{invoice_id}%")
            )\
            .first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Update invoice status
        invoice.status = InvoiceStatus.REJECTED
        invoice.rejected_by = current_user.id
        invoice.rejected_at = datetime.now(UTC)
        invoice.rejection_reason = rejection_data.get("reason", "No reason provided")
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Invoice {invoice.invoice_number} rejected successfully",
            "invoice_id": str(invoice.id),
            "reason": invoice.rejection_reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject invoice: {str(e)}"
        )

@router.post("/bulk/approve")
async def bulk_approve_invoices(
    request_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk approve multiple invoices"""
    try:
        approval_ids = request_data.get("approval_ids", [])
        comment = request_data.get("comment", "")
        
        if not approval_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No approval IDs provided"
            )
        
        # Extract invoice IDs from approval IDs
        invoice_ids = [aid.replace("APR-", "") for aid in approval_ids]
        
        # Get all invoices
        invoices = db.query(Invoice)\
            .filter(
                Invoice.company_id == current_user.company_id,
                Invoice.id.in_(invoice_ids)
            )\
            .all()
        
        if not invoices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No invoices found"
            )
        
        # Update all invoice statuses
        approved_count = 0
        for invoice in invoices:
            invoice.status = InvoiceStatus.APPROVED
            invoice.approved_by = current_user.id
            invoice.approved_at = datetime.now(UTC)
            if comment:
                invoice.approval_comment = comment
            approved_count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Successfully approved {approved_count} invoices",
            "approved_count": approved_count,
            "total_requested": len(approval_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk approve invoices: {str(e)}"
        )

@router.post("/bulk/reject")
async def bulk_reject_invoices(
    request_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk reject multiple invoices"""
    try:
        approval_ids = request_data.get("approval_ids", [])
        reason = request_data.get("reason", "")
        
        if not approval_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No approval IDs provided"
            )
        
        if not reason.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required for bulk rejection"
            )
        
        # Extract invoice IDs from approval IDs
        invoice_ids = [aid.replace("APR-", "") for aid in approval_ids]
        
        # Get all invoices
        invoices = db.query(Invoice)\
            .filter(
                Invoice.company_id == current_user.company_id,
                Invoice.id.in_(invoice_ids)
            )\
            .all()
        
        if not invoices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No invoices found"
            )
        
        # Update all invoice statuses
        rejected_count = 0
        for invoice in invoices:
            invoice.status = InvoiceStatus.REJECTED
            invoice.rejected_by = current_user.id
            invoice.rejected_at = datetime.now(UTC)
            invoice.rejection_reason = reason
            rejected_count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Successfully rejected {rejected_count} invoices",
            "rejected_count": rejected_count,
            "total_requested": len(approval_ids),
            "reason": reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk reject invoices: {str(e)}"
        )

