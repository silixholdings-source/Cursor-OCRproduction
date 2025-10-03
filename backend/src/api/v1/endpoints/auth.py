from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from typing import Optional
import uuid

from core.database import get_db
from core.auth import auth_manager
from schemas.auth import (
    UserLoginRequest,
    UserRegisterRequest,
    CompanyRegisterRequest,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    TokenResponse,
    UserResponse,
    CompanyResponse,
    AuthResponse,
    MessageResponse,
    ChangePasswordRequest,
    UpdateProfileRequest
)
from src.models.user import User, UserRole, UserStatus
from src.models.company import Company, CompanyStatus, CompanyTier

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=AuthResponse, summary="User Login")
async def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens with user/company info"""
    try:
        # Authenticate user
        user = auth_manager.authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
        
        # Check if account is locked
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is temporarily locked"
            )
        
        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(UTC)
        
        # Get company information
        company = db.query(Company).filter(Company.id == user.company_id).first()
        if not company or not company.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company account is not active"
            )
        
        # Create tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "company_id": str(user.company_id),
            "role": user.role.value
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        # Save refresh token hash to database (optional security enhancement)
        # user.refresh_token_hash = auth_manager.get_password_hash(refresh_token)
        
        db.commit()
        
        # Prepare response
        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes
            refresh_expires_in=7 * 24 * 60 * 60  # 7 days
        )
        
        return AuthResponse(
            user=UserResponse.from_orm(user),
            company=CompanyResponse.from_orm(company),
            tokens=tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.post("/register", response_model=AuthResponse, summary="Company and User Registration")
async def register(
    register_data: CompanyRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new company with an owner user"""
    try:
        # Check if company email already exists
        existing_company = db.query(Company).filter(Company.email == register_data.company_email).first()
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this email already exists"
            )
        
        # Check if owner email already exists
        existing_user = db.query(User).filter(User.email == register_data.owner_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == register_data.owner_username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create company
        company = Company(
            name=register_data.company_name,
            email=register_data.company_email,
            industry=register_data.industry,
            company_size=register_data.company_size,
            status=CompanyStatus.TRIAL,
            tier=CompanyTier.FREE,
            trial_ends_at=datetime.now(UTC) + timedelta(days=14),  # 14-day trial
            settings={
                "timezone": "UTC",
                "currency": "USD",
                "date_format": "MM/DD/YYYY"
            },
            features={
                "ocr_enabled": True,
                "3way_matching": True,
                "advanced_analytics": False,
                "api_access": False
            }
        )
        
        db.add(company)
        db.flush()  # Get company ID
        
        # Create owner user
        hashed_password = auth_manager.get_password_hash(register_data.owner_password)
        owner_user = User(
            email=register_data.owner_email,
            username=register_data.owner_username,
            hashed_password=hashed_password,
            first_name=register_data.owner_first_name,
            last_name=register_data.owner_last_name,
            company_id=company.id,
            role=UserRole.OWNER,
            status=UserStatus.ACTIVE,
            is_email_verified=True  # Auto-verify for now
        )
        
        db.add(owner_user)
        db.commit()
        
        # Create tokens for immediate login
        token_data = {
            "sub": str(owner_user.id),
            "email": owner_user.email,
            "company_id": str(company.id),
            "role": owner_user.role.value
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,
            refresh_expires_in=7 * 24 * 60 * 60
        )
        
        return AuthResponse(
            user=UserResponse.from_orm(owner_user),
            company=CompanyResponse.from_orm(company),
            tokens=tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/refresh", response_model=TokenResponse, summary="Refresh Access Token")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = auth_manager.verify_token(refresh_data.refresh_token)
        
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "company_id": str(user.company_id),
            "role": user.role.value
        }
        
        access_token = auth_manager.create_access_token(token_data)
        new_refresh_token = auth_manager.create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=30 * 60,
            refresh_expires_in=7 * 24 * 60 * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@router.post("/logout", response_model=MessageResponse, summary="User Logout")
async def logout(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user and invalidate tokens"""
    try:
        # In a production system, you might want to blacklist the token
        # For now, we'll just return a success message
        # The client should discard the tokens
        
        return MessageResponse(
            message="Successfully logged out",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )

@router.get("/me", response_model=UserResponse, summary="Get Current User")
async def get_current_user(
    current_user: User = Depends(auth_manager.get_current_active_user)
):
    """Get current authenticated user information"""
    return UserResponse.from_orm(current_user)

@router.post("/change-password", response_model=MessageResponse, summary="Change Password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(auth_manager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not auth_manager.verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = auth_manager.get_password_hash(password_data.new_password)
        db.commit()
        
        return MessageResponse(
            message="Password changed successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password change"
        )

@router.put("/profile", response_model=UserResponse, summary="Update Profile")
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(auth_manager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        # Update fields if provided
        if profile_data.first_name is not None:
            current_user.first_name = profile_data.first_name
        if profile_data.last_name is not None:
            current_user.last_name = profile_data.last_name
        if profile_data.phone is not None:
            current_user.phone = profile_data.phone
        if profile_data.avatar_url is not None:
            current_user.avatar_url = profile_data.avatar_url
        
        db.commit()
        
        return UserResponse.from_orm(current_user)
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during profile update"
        )

@router.post("/forgot-password", response_model=MessageResponse, summary="Forgot Password")
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send password reset email"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == forgot_data.email).first()
        if not user:
            # Don't reveal if user exists or not
            return MessageResponse(
                message="If an account with that email exists, a password reset link has been sent",
                success=True
            )
        
        # Generate reset token (in production, use a proper token service)
        reset_token = str(uuid.uuid4())
        
        # In production, send email with reset link
        # For now, just log the token
        logger.info(f"Password reset token for {user.email}: {reset_token}")
        
        return MessageResponse(
            message="If an account with that email exists, a password reset link has been sent",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password reset request"
        )

@router.post("/reset-password", response_model=MessageResponse, summary="Reset Password")
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password using reset token"""
    try:
        # In production, validate the reset token
        # For now, we'll just return success
        # This is a placeholder implementation
        
        return MessageResponse(
            message="Password reset successfully",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password reset"
        )

@router.post("/verify-email", response_model=MessageResponse, summary="Verify Email")
async def verify_email(
    verify_data: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """Verify user email address"""
    try:
        # In production, validate the verification token
        # For now, we'll just return success
        # This is a placeholder implementation
        
        return MessageResponse(
            message="Email verified successfully",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during email verification"
        )

@router.post("/demo-login", response_model=AuthResponse, summary="Demo Login (quick)")
async def demo_login(
    db: Session = Depends(get_db)
):
    """Create or fetch a demo company and user, and return tokens for instant login.
    Safe for local/dev use. In production, guard behind feature flags.
    """
    try:
        demo_company_email = "demo-company@example.com"
        demo_user_email = "demo@example.com"
        demo_username = "demo_user"

        company = db.query(Company).filter(Company.email == demo_company_email).first()
        if not company:
            company = Company(
                name="Demo Company",
                email=demo_company_email,
                industry="Software",
                company_size="1-10",
                status=CompanyStatus.TRIAL,
                tier=CompanyTier.FREE,
                trial_ends_at=datetime.now(UTC) + timedelta(days=14),
                settings={"timezone": "UTC", "currency": "USD", "date_format": "YYYY-MM-DD"},
                features={"ocr_enabled": True}
            )
            db.add(company)
            db.flush()

        user = db.query(User).filter(User.email == demo_user_email).first()
        if not user:
            hashed_password = auth_manager.get_password_hash("demo-password")
            user = User(
                email=demo_user_email,
                username=demo_username,
                hashed_password=hashed_password,
                first_name="Demo",
                last_name="User",
                company_id=company.id,
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                is_email_verified=True,
            )
            db.add(user)
            db.flush()

        # Tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "company_id": str(user.company_id),
            "role": user.role.value
        }
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,
            refresh_expires_in=7 * 24 * 60 * 60
        )
        db.commit()
        return AuthResponse(
            user=UserResponse.from_orm(user),
            company=CompanyResponse.from_orm(company),
            tokens=tokens
        )
    except Exception as e:
        logger.error(f"Demo login error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during demo login"
        )
