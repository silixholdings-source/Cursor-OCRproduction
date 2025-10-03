"""
3-Way Match API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from core.database import get_db
from core.auth import AuthManager
from src.models.user import User
from services.three_way_match import ThreeWayMatchService, MatchResult
from schemas.erp import ThreeWayMatchResponse, ThreeWayMatchRequest

router = APIRouter()

@router.post("/match", response_model=ThreeWayMatchResponse)
async def perform_three_way_match(
    match_request: ThreeWayMatchRequest,
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Perform 3-way matching between invoice, PO, and receipt"""
    try:
        match_service = ThreeWayMatchService()
        
        result = await match_service.perform_three_way_match(
            invoice_id=str(match_request.invoice_id),
            po_number=match_request.po_number,
            receipt_number=match_request.receipt_number,
            db=db
        )
        
        return ThreeWayMatchResponse(
            invoice_id=match_request.invoice_id,
            po_number=match_request.po_number,
            receipt_number=match_request.receipt_number,
            match_status=result.status.value,
            confidence_level=result.confidence.value,
            confidence_score=result.confidence_score,
            matches=result.matches,
            mismatches=result.mismatches,
            warnings=result.warnings,
            suggested_actions=result.suggested_actions,
            total_invoice_amount=float(result.total_invoice_amount),
            total_po_amount=float(result.total_po_amount),
            total_receipt_amount=float(result.total_receipt_amount),
            variance_amount=float(result.variance_amount),
            variance_percentage=result.variance_percentage
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"3-way match failed: {str(e)}"
        )

@router.get("/invoice/{invoice_id}")
async def get_invoice_match_status(
    invoice_id: UUID,
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get 3-way match status for a specific invoice"""
    try:
        match_service = ThreeWayMatchService()
        
        result = await match_service.perform_three_way_match(
            invoice_id=str(invoice_id),
            db=db
        )
        
        return {
            "invoice_id": invoice_id,
            "match_status": result.status.value,
            "confidence_level": result.confidence.value,
            "confidence_score": result.confidence_score,
            "has_matches": len(result.matches) > 0,
            "has_mismatches": len(result.mismatches) > 0,
            "variance_amount": float(result.variance_amount),
            "variance_percentage": result.variance_percentage,
            "warnings_count": len(result.warnings),
            "suggested_actions_count": len(result.suggested_actions)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match status: {str(e)}"
        )

@router.get("/analytics/summary")
async def get_match_analytics(
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get 3-way match analytics summary"""
    try:
        # This would typically query the database for match statistics
        # For now, return a placeholder structure
        return {
            "total_matches_performed": 0,
            "perfect_matches": 0,
            "partial_matches": 0,
            "price_mismatches": 0,
            "quantity_mismatches": 0,
            "no_matches": 0,
            "average_confidence_score": 0.0,
            "average_variance_percentage": 0.0,
            "most_common_issues": [],
            "match_accuracy_trend": []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )
