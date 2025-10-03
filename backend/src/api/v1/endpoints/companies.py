from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.auth import auth_manager
from src.models.user import User
from src.models.company import Company
from schemas.auth import CompanyResponse

router = APIRouter()

@router.get("/me", response_model=CompanyResponse, summary="Get Current Company")
async def get_current_company(
    current_user: User = Depends(auth_manager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's company information"""
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return CompanyResponse.from_orm(company)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching company information"
        )

@router.get("/", response_model=List[CompanyResponse], summary="List Companies")
async def list_companies(
    current_user: User = Depends(auth_manager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """List companies (admin only)"""
    # Check if user has admin privileges
    if current_user.role.value not in ['owner', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view all companies"
        )
    
    try:
        companies = db.query(Company).all()
        return [CompanyResponse.from_orm(company) for company in companies]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching companies"
        )

@router.get("/{company_id}", response_model=CompanyResponse, summary="Get Company by ID")
async def get_company(
    company_id: str,
    current_user: User = Depends(auth_manager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get company by ID (admin only or own company)"""
    try:
        # Check if user can access this company
        if current_user.company_id != company_id and current_user.role.value not in ['owner', 'admin']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view this company"
            )
        
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return CompanyResponse.from_orm(company)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching company"
        )

@router.put("/me", response_model=CompanyResponse, summary="Update Current Company")
async def update_current_company(
    company_data: dict,
    current_user: User = Depends(auth_manager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's company information"""
    # Check if user has admin privileges
    if current_user.role.value not in ['owner', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update company information"
        )
    
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Update company fields
        for field, value in company_data.items():
            if hasattr(company, field) and field not in ['id', 'created_at', 'updated_at']:
                setattr(company, field, value)
        
        db.commit()
        db.refresh(company)
        
        return CompanyResponse.from_orm(company)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating company"
        )
