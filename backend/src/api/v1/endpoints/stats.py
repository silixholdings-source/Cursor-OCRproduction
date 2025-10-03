"""
Dashboard Statistics Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any
from datetime import datetime, timedelta

from core.database import get_db
from core.auth import auth_manager
from src.models.user import User, UserRole
from src.models.invoice import Invoice, InvoiceStatus
from src.models.company import Company

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics for the current user's company"""
    try:
        company_id = current_user.company_id
        
        # Get total invoices
        total_invoices = db.query(func.count(Invoice.id)).filter(
            Invoice.company_id == company_id
        ).scalar() or 0
        
        # Get pending approvals
        pending_approvals = db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.status == InvoiceStatus.PENDING_APPROVAL
            )
        ).scalar() or 0
        
        # Get approved this month
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        approved_this_month = db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.status == InvoiceStatus.APPROVED,
                Invoice.updated_at >= start_of_month
            )
        ).scalar() or 0
        
        # Get total spent this month
        total_spent = db.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.status.in_([InvoiceStatus.APPROVED, InvoiceStatus.PAID]),
                Invoice.updated_at >= start_of_month
            )
        ).scalar() or 0.0
        
        # Get company info for limits
        company = db.query(Company).filter(Company.id == company_id).first()
        
        # Get active users count
        active_users = db.query(func.count(User.id)).filter(
            User.company_id == company_id
        ).scalar() or 0
        
        # Calculate average processing time (mock for now)
        avg_processing_time = 2.3
        
        # OCR accuracy (mock for now)
        ocr_accuracy = 98.5
        
        # Storage used (mock for now)
        storage_used = 8.2
        
        return {
            "totalInvoices": total_invoices,
            "pendingApprovals": pending_approvals,
            "approvedThisMonth": approved_this_month,
            "totalSpent": float(total_spent),
            "avgProcessingTime": avg_processing_time,
            "accuracyRate": ocr_accuracy,
            "activeUsers": active_users,
            "storageUsed": storage_used,
            "company": {
                "max_users": company.max_users if company else 5,
                "max_storage_gb": company.max_storage_gb if company else 10
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard statistics: {str(e)}"
        )

@router.get("/processing-metrics")
async def get_processing_metrics(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get invoice processing metrics"""
    try:
        company_id = current_user.company_id
        
        # Get invoices processed in the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        processed_invoices = db.query(Invoice).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.created_at >= thirty_days_ago
            )
        ).all()
        
        # Calculate metrics
        total_processed = len(processed_invoices)
        
        # Status breakdown
        status_counts = {}
        for invoice in processed_invoices:
            status = invoice.status.value if hasattr(invoice.status, 'value') else str(invoice.status)
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Processing time analysis (mock data for now)
        avg_processing_time = 2.3
        fastest_processing = 0.5
        slowest_processing = 8.2
        
        return {
            "totalProcessed": total_processed,
            "statusBreakdown": status_counts,
            "avgProcessingTime": avg_processing_time,
            "fastestProcessing": fastest_processing,
            "slowestProcessing": slowest_processing,
            "timeRange": "last_30_days"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch processing metrics: {str(e)}"
        )

