from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from core.database import get_db
from core.auth import auth_manager
from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
from src.models.user import User
from schemas.invoice import InvoiceResponse, InvoiceListResponse, InvoiceCreate, InvoiceUpdate
from services.invoice_processor import InvoiceProcessor
from services.workflow import WorkflowEngine

router = APIRouter()

@router.get("/recent")
async def get_recent_invoices(
    limit: int = Query(5, ge=1, le=20, description="Number of recent invoices to return"),
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent invoices for dashboard display"""
    try:
        # Get recent invoices for the user's company
        invoices = db.query(Invoice)\
            .filter(Invoice.company_id == current_user.company_id)\
            .order_by(Invoice.created_at.desc())\
            .limit(limit)\
            .all()
        
        # Transform to frontend format
        invoice_data = []
        for invoice in invoices:
            invoice_data.append({
                "id": str(invoice.id),
                "vendor": invoice.supplier_name,
                "amount": float(invoice.total_amount),
                "date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                "status": invoice.status.value if invoice.status else "pending",
                "dueDate": invoice.due_date.isoformat() if invoice.due_date else None,
                "invoiceNumber": invoice.invoice_number,
                "category": invoice.category or "General"
            })
        
        return {
            "invoices": invoice_data,
            "total": len(invoice_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent invoices: {str(e)}"
        )

@router.get("/", response_model=InvoiceListResponse)
async def get_invoices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
    invoice_type: Optional[InvoiceType] = Query(None, description="Filter by invoice type"),
    supplier_name: Optional[str] = Query(None, description="Filter by supplier name"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of invoices with filtering options"""
    try:
        query = db.query(Invoice).filter(Invoice.company_id == current_user.company_id)
        
        # Apply filters
        if status:
            query = query.filter(Invoice.status == status)
        if invoice_type:
            query = query.filter(Invoice.type == invoice_type)
        if supplier_name:
            query = query.filter(Invoice.supplier_name.ilike(f"%{supplier_name}%"))
        if date_from:
            query = query.filter(Invoice.invoice_date >= date_from)
        if date_to:
            query = query.filter(Invoice.invoice_date <= date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        invoices = query.offset(skip).limit(limit).all()
        
        return InvoiceListResponse(
            invoices=[InvoiceResponse.from_orm(invoice) for invoice in invoices],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve invoices: {str(e)}"
        )

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific invoice by ID"""
    try:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        return InvoiceResponse.from_orm(invoice)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve invoice: {str(e)}"
        )

@router.post("/", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new invoice"""
    try:
        # Create invoice from data
        invoice = Invoice(
            **invoice_data.dict(),
            company_id=current_user.company_id,
            created_by_id=current_user.id
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        return InvoiceResponse.from_orm(invoice)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create invoice: {str(e)}"
        )

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing invoice"""
    try:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Update fields
        update_data = invoice_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        db.commit()
        db.refresh(invoice)
        
        return InvoiceResponse.from_orm(invoice)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update invoice: {str(e)}"
        )

@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: UUID,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an invoice (soft delete)"""
    try:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Soft delete by updating status
        invoice.status = InvoiceStatus.DELETED
        db.commit()
        
        return {"message": "Invoice deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete invoice: {str(e)}"
        )

@router.post("/{invoice_id}/approve")
async def approve_invoice(
    invoice_id: UUID,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Approve an invoice"""
    try:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Use workflow engine for approval
        workflow_engine = WorkflowEngine()
        result = await workflow_engine.process_approval(
            invoice_id=invoice_id,
            approver_id=current_user.id,
            action="approve",
            db=db
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve invoice: {str(e)}"
        )

@router.post("/{invoice_id}/reject")
async def reject_invoice(
    invoice_id: UUID,
    reason: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Reject an invoice"""
    try:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Use workflow engine for rejection
        workflow_engine = WorkflowEngine()
        result = await workflow_engine.process_approval(
            invoice_id=invoice_id,
            approver_id=current_user.id,
            action="reject",
            reason=reason,
            db=db
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject invoice: {str(e)}"
        )

@router.get("/{invoice_id}/workflow")
async def get_invoice_workflow(
    invoice_id: UUID,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get workflow status for an invoice"""
    try:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        workflow_engine = WorkflowEngine()
        workflow_status = await workflow_engine.get_workflow_status(invoice_id, db)
        
        return workflow_status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )

@router.get("/analytics/summary")
async def get_invoice_analytics(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice analytics summary"""
    try:
        # Get basic counts by status
        total_invoices = db.query(Invoice).filter(Invoice.company_id == current_user.company_id).count()
        pending_invoices = db.query(Invoice).filter(
            Invoice.company_id == current_user.company_id,
            Invoice.status == InvoiceStatus.PENDING_APPROVAL
        ).count()
        approved_invoices = db.query(Invoice).filter(
            Invoice.company_id == current_user.company_id,
            Invoice.status == InvoiceStatus.APPROVED
        ).count()
        rejected_invoices = db.query(Invoice).filter(
            Invoice.company_id == current_user.company_id,
            Invoice.status == InvoiceStatus.REJECTED
        ).count()
        
        # Get total amount by status
        total_amount = db.query(Invoice.total_amount).filter(
            Invoice.company_id == current_user.company_id
        ).all()
        
        return {
            "total_invoices": total_invoices,
            "pending_invoices": pending_invoices,
            "approved_invoices": approved_invoices,
            "rejected_invoices": rejected_invoices,
            "total_amount": sum([amount[0] for amount in total_amount if amount[0]]),
            "average_processing_time": 0,  # TODO: Calculate from audit logs
            "approval_rate": (approved_invoices / total_invoices * 100) if total_invoices > 0 else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )
