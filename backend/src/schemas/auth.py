from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from src.models.user import UserRole, UserStatus
from src.models.company import CompanyStatus, CompanyTier

# Authentication Request Schemas
class UserLoginRequest(BaseModel):
    """User login request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")

class UserRegisterRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    company_email: EmailStr = Field(..., description="Company email address")

class CompanyRegisterRequest(BaseModel):
    """Company registration request schema"""
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    company_email: EmailStr = Field(..., description="Company email address")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    company_size: Optional[str] = Field(None, max_length=50, description="Company size")
    
    # Owner user information
    owner_email: EmailStr = Field(..., description="Owner email address")
    owner_username: str = Field(..., min_length=3, max_length=100, description="Owner username")
    owner_password: str = Field(..., min_length=8, description="Owner password")
    owner_first_name: str = Field(..., min_length=1, max_length=100, description="Owner first name")
    owner_last_name: str = Field(..., min_length=1, max_length=100, description="Owner last name")

class TokenRequest(BaseModel):
    """Token request schema"""
    grant_type: str = Field(default="password", description="Grant type")
    username: EmailStr = Field(..., description="Username (email)")
    password: str = Field(..., description="Password")
    scope: Optional[str] = Field(default="read write", description="Requested scopes")

class TokenRefreshRequest(BaseModel):
    """Token refresh request schema"""
    refresh_token: str = Field(..., description="Refresh token")

class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email address")

class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation request schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")

# Response Schemas
class UserResponse(BaseModel):
    """User response schema"""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    role: UserRole = Field(..., description="User role")
    status: UserStatus = Field(..., description="User status")
    is_email_verified: bool = Field(..., description="Email verification status")
    company_id: str = Field(..., description="Company ID")
    created_at: datetime = Field(..., description="User creation time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_validator('id', 'company_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        return str(v) if v is not None else v

class CompanyResponse(BaseModel):
    """Company response schema"""
    id: str = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    email: str = Field(..., description="Company email")
    status: CompanyStatus = Field(..., description="Company status")
    tier: CompanyTier = Field(..., description="Subscription tier")
    created_at: datetime = Field(..., description="Company creation time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        return str(v) if v is not None else v

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: str = Field(..., description="Refresh token")
    scope: str = Field(..., description="Token scope")

class AuthResponse(BaseModel):
    """Authentication response schema"""
    user: UserResponse = Field(..., description="User information")
    company: CompanyResponse = Field(..., description="Company information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")

class PasswordResetResponse(BaseModel):
    """Password reset response schema"""
    message: str = Field(..., description="Response message")
    email: str = Field(..., description="Email address where reset link was sent")

class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    token: str = Field(..., description="Verification token")

class EmailVerificationResponse(BaseModel):
    """Email verification response schema"""
    message: str = Field(..., description="Response message")
    verified: bool = Field(..., description="Verification status")

# Additional schemas for compatibility
class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")

class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""
    email: EmailStr = Field(..., description="User email address")

class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")

class VerifyEmailRequest(BaseModel):
    """Verify email request schema"""
    token: str = Field(..., description="Verification token")

class MessageResponse(BaseModel):
    """Message response schema"""
    message: str = Field(..., description="Response message")

class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

class UpdateProfileRequest(BaseModel):
    """Update profile request schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")

class UserListResponse(BaseModel):
    """User list response schema"""
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., ge=1, description="Current page")
    size: int = Field(..., ge=1, le=100, description="Page size")
    has_next: bool = Field(..., description="Has next page")

class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    company_id: str = Field(..., description="Company ID")

class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    role: Optional[UserRole] = Field(None, description="User role")
    status: Optional[UserStatus] = Field(None, description="User status")

class UserRoleUpdate(BaseModel):
    """User role update schema"""
    role: UserRole = Field(..., description="New user role")