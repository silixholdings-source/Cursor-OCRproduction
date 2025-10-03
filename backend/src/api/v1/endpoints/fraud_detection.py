"""
Fraud Detection API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from core.database import get_db
from core.auth import AuthManager
from src.models.user import User
from services.fraud_detection import FraudDetectionService, FraudAnalysisResult
from schemas.erp import FraudAnalysisResponse, FraudAnalyticsResponse

router = APIRouter()

@router.post("/analyze/{invoice_id}", response_model=FraudAnalysisResponse)
async def analyze_fraud_risk(
    invoice_id: UUID,
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze fraud risk for a specific invoice"""
    try:
        fraud_service = FraudDetectionService()
        
        # Get invoice
        from src.models.invoice import Invoice
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Perform fraud analysis
        result = await fraud_service.analyze_fraud_risk(invoice, db)
        
        return FraudAnalysisResponse(
            invoice_id=invoice_id,
            risk_level=result.risk_level.value,
            risk_score=result.risk_score,
            confidence=result.confidence,
            indicators=result.indicators,
            recommendations=result.recommendations,
            requires_manual_review=result.requires_manual_review,
            auto_approve=result.auto_approve,
            auto_reject=result.auto_reject,
            investigation_priority=result.investigation_priority
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud analysis failed: {str(e)}"
        )

@router.get("/analytics", response_model=FraudAnalyticsResponse)
async def get_fraud_analytics(
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get fraud analytics for the company"""
    try:
        fraud_service = FraudDetectionService()
        
        analytics = await fraud_service.get_fraud_analytics(
            company_id=str(current_user.company_id),
            db=db
        )
        
        return FraudAnalyticsResponse(**analytics)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get fraud analytics: {str(e)}"
        )

@router.get("/indicators")
async def get_fraud_indicators(
    current_user: User = Depends(AuthManager.get_current_user)
):
    """Get list of available fraud indicators"""
    from services.fraud_detection import FraudIndicator
    
    return {
        "indicators": [
            {
                "type": indicator.value,
                "name": indicator.name.replace("_", " ").title(),
                "description": f"Detects {indicator.value.replace('_', ' ')} patterns"
            }
            for indicator in FraudIndicator
        ]
    }

@router.get("/risk-levels")
async def get_risk_levels(
    current_user: User = Depends(AuthManager.get_current_user)
):
    """Get fraud risk level definitions"""
    from services.fraud_detection import FraudRiskLevel
    
    return {
        "risk_levels": [
            {
                "level": level.value,
                "name": level.name.title(),
                "description": f"{level.value.title()} fraud risk level"
            }
            for level in FraudRiskLevel
        ]
    }
