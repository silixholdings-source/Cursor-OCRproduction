from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from core.auth import AuthManager
from src.models.user import User, UserRole
from src.models.company import Company
from schemas.auth import UserResponse, UserListResponse, UserCreate, UserUpdate, UserRoleUpdate

router = APIRouter()

@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of users with filtering options (Admin only)"""
    try:
        query = db.query(User).filter(User.company_id == current_user.company_id)
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if search:
            query = query.filter(
                (User.first_name.ilike(f"%{search}%")) |
                (User.last_name.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%"))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        return UserListResponse(
            users=[UserResponse.from_orm(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(AuthManager.get_current_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific user by ID (Admin only)"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.company_id == current_user.company_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new user (Admin only)"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.company_id == current_user.company_id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = AuthManager.get_password_hash(user_data.password)
        
        # Create user
        user = User(
            **user_data.dict(exclude={"password"}),
            password_hash=hashed_password,
            company_id=current_user.company_id
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing user (Admin only)"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.company_id == current_user.company_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password" and value:
                # Hash new password
                setattr(user, "password_hash", AuthManager.get_password_hash(value))
            elif field != "password":
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user: {str(e)}"
        )

@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    role_data: UserRoleUpdate,
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user role (Admin only)"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.company_id == current_user.company_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from changing their own role
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )
        
        user.role = role_data.role
        db.commit()
        db.refresh(user)
        
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user role: {str(e)}"
        )

@router.put("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Activate a user (Admin only)"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.company_id == current_user.company_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        db.commit()
        
        return {"message": "User activated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )

@router.put("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user (Admin only)"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.company_id == current_user.company_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deactivating themselves
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate yourself"
            )
        
        user.is_active = False
        db.commit()
        
        return {"message": "User deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a user (Admin only)"""
    try:
        user = db.query(User).filter(
            User.id == user_id,
            User.company_id == current_user.company_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deleting themselves
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself"
            )
        
        # Soft delete by deactivating
        user.is_active = False
        db.commit()
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.get("/analytics/summary")
async def get_user_analytics(
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user analytics summary (Admin only)"""
    try:
        # Get user counts by role
        total_users = db.query(User).filter(User.company_id == current_user.company_id).count()
        active_users = db.query(User).filter(
            User.company_id == current_user.company_id,
            User.is_active == True
        ).count()
        admin_users = db.query(User).filter(
            User.company_id == current_user.company_id,
            User.role == UserRole.ADMIN
        ).count()
        manager_users = db.query(User).filter(
            User.company_id == current_user.company_id,
            User.role == UserRole.MANAGER
        ).count()
        approver_users = db.query(User).filter(
            User.company_id == current_user.company_id,
            User.role == UserRole.APPROVER
        ).count()
        viewer_users = db.query(User).filter(
            User.company_id == current_user.company_id,
            User.role == UserRole.VIEWER
        ).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admin_users": admin_users,
            "manager_users": manager_users,
            "approver_users": approver_users,
            "viewer_users": viewer_users,
            "activation_rate": (active_users / total_users * 100) if total_users > 0 else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user analytics: {str(e)}"
        )