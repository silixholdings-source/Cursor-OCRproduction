"""
Optimized Database Queries for Production
"""
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, desc, asc, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging

from models.optimized_models import Invoice, User, Company, InvoiceLine, AuditLog

logger = logging.getLogger(__name__)

class OptimizedInvoiceQueries:
    """Optimized queries for invoice operations"""
    
    @staticmethod
    def get_invoices_paginated(
        db: Session,
        company_id: str,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        supplier_name: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get paginated invoices with filters"""
        
        # Build query with filters
        query = db.query(Invoice).filter(Invoice.company_id == company_id)
        
        if status:
            query = query.filter(Invoice.status == status)
        
        if supplier_name:
            query = query.filter(Invoice.supplier_name.ilike(f"%{supplier_name}%"))
        
        if date_from:
            query = query.filter(Invoice.invoice_date >= date_from)
        
        if date_to:
            query = query.filter(Invoice.invoice_date <= date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        invoices = query.order_by(desc(Invoice.created_at))\
                       .offset((page - 1) * per_page)\
                       .limit(per_page)\
                       .all()
        
        return {
            "invoices": invoices,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def get_invoice_with_lines(db: Session, invoice_id: str, company_id: str) -> Optional[Invoice]:
        """Get invoice with line items in single query"""
        return db.query(Invoice)\
                 .options(selectinload(Invoice.line_items))\
                 .filter(Invoice.id == invoice_id)\
                 .filter(Invoice.company_id == company_id)\
                 .first()
    
    @staticmethod
    def get_invoice_stats(db: Session, company_id: str) -> Dict[str, Any]:
        """Get invoice statistics for dashboard"""
        
        # Use raw SQL for better performance
        stats_query = text("""
            SELECT 
                COUNT(*) as total_invoices,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_count,
                COUNT(CASE WHEN status = 'pending_approval' THEN 1 END) as pending_count,
                COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_count,
                COALESCE(SUM(CASE WHEN status = 'approved' THEN total_amount END), 0) as approved_amount,
                COALESCE(SUM(CASE WHEN status = 'pending_approval' THEN total_amount END), 0) as pending_amount,
                COALESCE(AVG(total_amount), 0) as avg_amount
            FROM invoices 
            WHERE company_id = :company_id
        """)
        
        result = db.execute(stats_query, {"company_id": company_id}).fetchone()
        
        return {
            "total_invoices": result.total_invoices or 0,
            "approved_count": result.approved_count or 0,
            "pending_count": result.pending_count or 0,
            "rejected_count": result.rejected_count or 0,
            "approved_amount": float(result.approved_amount or 0),
            "pending_amount": float(result.pending_amount or 0),
            "avg_amount": float(result.avg_amount or 0)
        }
    
    @staticmethod
    def get_recent_invoices(db: Session, company_id: str, limit: int = 10) -> List[Invoice]:
        """Get recent invoices for dashboard"""
        return db.query(Invoice)\
                 .filter(Invoice.company_id == company_id)\
                 .order_by(desc(Invoice.created_at))\
                 .limit(limit)\
                 .all()
    
    @staticmethod
    def search_invoices(
        db: Session,
        company_id: str,
        search_term: str,
        limit: int = 20
    ) -> List[Invoice]:
        """Search invoices by multiple fields"""
        search_filter = or_(
            Invoice.invoice_number.ilike(f"%{search_term}%"),
            Invoice.supplier_name.ilike(f"%{search_term}%"),
            Invoice.ocr_data["supplier_name"].astext.ilike(f"%{search_term}%")
        )
        
        return db.query(Invoice)\
                 .filter(Invoice.company_id == company_id)\
                 .filter(search_filter)\
                 .order_by(desc(Invoice.created_at))\
                 .limit(limit)\
                 .all()

class OptimizedUserQueries:
    """Optimized queries for user operations"""
    
    @staticmethod
    def get_active_users_by_company(db: Session, company_id: str) -> List[User]:
        """Get active users for a company"""
        return db.query(User)\
                 .filter(User.company_id == company_id)\
                 .filter(User.is_active == True)\
                 .order_by(User.first_name, User.last_name)\
                 .all()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email with company info"""
        return db.query(User)\
                 .options(joinedload(User.company))\
                 .filter(User.email == email)\
                 .first()

class OptimizedAnalyticsQueries:
    """Optimized queries for analytics"""
    
    @staticmethod
    def get_monthly_invoice_trends(
        db: Session,
        company_id: str,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """Get monthly invoice trends"""
        
        query = text("""
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                COUNT(*) as invoice_count,
                SUM(total_amount) as total_amount,
                AVG(total_amount) as avg_amount
            FROM invoices 
            WHERE company_id = :company_id
            AND created_at >= :start_date
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month DESC
        """)
        
        start_date = datetime.now() - timedelta(days=months * 30)
        
        results = db.execute(query, {
            "company_id": company_id,
            "start_date": start_date
        }).fetchall()
        
        return [
            {
                "month": row.month.strftime("%Y-%m"),
                "invoice_count": row.invoice_count,
                "total_amount": float(row.total_amount or 0),
                "avg_amount": float(row.avg_amount or 0)
            }
            for row in results
        ]
    
    @staticmethod
    def get_top_suppliers(
        db: Session,
        company_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top suppliers by invoice count and amount"""
        
        query = text("""
            SELECT 
                supplier_name,
                COUNT(*) as invoice_count,
                SUM(total_amount) as total_amount,
                AVG(total_amount) as avg_amount
            FROM invoices 
            WHERE company_id = :company_id
            GROUP BY supplier_name
            ORDER BY total_amount DESC
            LIMIT :limit
        """)
        
        results = db.execute(query, {
            "company_id": company_id,
            "limit": limit
        }).fetchall()
        
        return [
            {
                "supplier_name": row.supplier_name,
                "invoice_count": row.invoice_count,
                "total_amount": float(row.total_amount or 0),
                "avg_amount": float(row.avg_amount or 0)
            }
            for row in results
        ]

class OptimizedAuditQueries:
    """Optimized queries for audit logs"""
    
    @staticmethod
    def get_audit_logs_paginated(
        db: Session,
        company_id: str,
        page: int = 1,
        per_page: int = 50,
        action: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated audit logs"""
        
        query = db.query(AuditLog).filter(AuditLog.company_id == company_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        total = query.count()
        
        logs = query.order_by(desc(AuditLog.created_at))\
                   .offset((page - 1) * per_page)\
                   .limit(per_page)\
                   .all()
        
        return {
            "logs": logs,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }









