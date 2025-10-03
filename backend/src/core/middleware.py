from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging
from .database import get_db
from .auth import auth_manager
from src.models.user import User
from src.models.company import Company

logger = logging.getLogger(__name__)

class MultiTenantMiddleware:
    """Middleware for multi-tenant support and company isolation"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip middleware for public endpoints
            if self._is_public_endpoint(request.url.path):
                await self.app(scope, receive, send)
                return
            
            # Extract company context from request
            company_context = await self._extract_company_context(request)
            
            # Add company context to request state
            request.state.company_context = company_context
            
            # Add company context to scope for WebSocket support
            scope["company_context"] = company_context
            
            await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no authentication required)"""
        public_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/verify-email",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password"
        ]
        return any(path.startswith(public_path) for public_path in public_paths)
    
    async def _extract_company_context(self, request: Request) -> Optional[dict]:
        """Extract company context from request headers or JWT token"""
        try:
            # Try to get company context from JWT token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = auth_manager.verify_token(token)
                user_id = payload.get("sub")
                company_id = payload.get("company_id")
                
                if user_id and company_id:
                    return {
                        "user_id": user_id,
                        "company_id": company_id,
                        "user_role": payload.get("role"),
                        "source": "jwt"
                    }
            
            # Try to get company context from custom headers
            company_id = request.headers.get("X-Company-ID")
            if company_id:
                return {
                    "company_id": company_id,
                    "source": "header"
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting company context: {e}")
            return None

def get_company_context(request: Request) -> Optional[dict]:
    """Get company context from request state"""
    return getattr(request.state, "company_context", None)

def require_company_context():
    """Dependency to require company context"""
    def company_checker(request: Request):
        company_context = get_company_context(request)
        if not company_context:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company context required"
            )
        return company_context
    return company_checker

def get_current_company(
    company_context: dict = Depends(require_company_context),
    db: Session = Depends(get_db)
) -> Company:
    """Get current company from context"""
    company_id = company_context.get("company_id")
    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company ID not found in context"
        )
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if not company.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company is not active"
        )
    
    return company

def validate_company_access(
    current_user: User = Depends(auth_manager.get_current_user),
    company_context: dict = Depends(require_company_context)
):
    """Validate that user has access to the company in context"""
    if not current_user.can_access_company(company_context["company_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    return current_user
