"""
Security API endpoints
Enterprise security features including MFA, SSO, and audit trails
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from core.database import get_db
from core.auth import get_current_user
from src.models.user import User
from src.models.company import Company
from services.enterprise_security import enterprise_security_service
from services.mfa_service import mfa_service, MFAMethod
from services.sso_service import sso_service, SSOProvider
from schemas.security import (
    MFAEnableRequest,
    MFAVerifyRequest,
    MFAChallengeRequest,
    MFAChallengeVerifyRequest,
    SSOConfigurationRequest,
    SSOAuthenticationRequest,
    SecurityDashboardResponse,
    AuditReportRequest,
    SecurityPolicyRequest
)

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# MFA Endpoints
@router.post("/mfa/enable")
async def enable_mfa(
    request: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable MFA for the current user"""
    try:
        result = await mfa_service.enable_mfa_for_user(
            user=current_user,
            method=request.method,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to enable MFA: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable MFA")

@router.post("/mfa/verify")
async def verify_mfa_code(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify MFA code"""
    try:
        result = await mfa_service.verify_mfa_code(
            user=current_user,
            code=request.code,
            method=request.method,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to verify MFA code: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify MFA code")

@router.post("/mfa/challenge")
async def generate_mfa_challenge(
    request: MFAChallengeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate MFA challenge"""
    try:
        result = await mfa_service.generate_mfa_challenge(
            user=current_user,
            method=request.method,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate MFA challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate MFA challenge")

@router.post("/mfa/challenge/verify")
async def verify_mfa_challenge(
    request: MFAChallengeVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify MFA challenge"""
    try:
        result = await mfa_service.verify_mfa_challenge(
            challenge_id=request.challenge_id,
            code=request.code,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to verify MFA challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify MFA challenge")

@router.delete("/mfa/disable")
async def disable_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable MFA for the current user"""
    try:
        result = await mfa_service.disable_mfa_for_user(
            user=current_user,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to disable MFA: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable MFA")

@router.post("/mfa/backup-codes/regenerate")
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate backup codes for the current user"""
    try:
        result = await mfa_service.regenerate_backup_codes(
            user=current_user,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to regenerate backup codes: {e}")
        raise HTTPException(status_code=500, detail="Failed to regenerate backup codes")

# SSO Endpoints
@router.post("/sso/configure")
async def configure_sso(
    request: SSOConfigurationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure SSO provider for the company"""
    try:
        # Check if user has admin privileges
        if current_user.role.value not in ["admin", "owner"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = await sso_service.configure_sso_provider(
            company_id=str(current_user.company_id),
            provider=request.provider,
            configuration=request.configuration,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to configure SSO: {e}")
        raise HTTPException(status_code=500, detail="Failed to configure SSO")

@router.post("/sso/authenticate")
async def authenticate_sso(
    request: SSOAuthenticationRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user via SSO"""
    try:
        result = await sso_service.authenticate_sso_user(
            provider=request.provider,
            auth_data=request.auth_data,
            company_id=request.company_id,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to authenticate via SSO: {e}")
        raise HTTPException(status_code=500, detail="Failed to authenticate via SSO")

@router.get("/sso/metadata/{company_id}")
async def get_saml_metadata(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SAML metadata for the company"""
    try:
        # Check if user has admin privileges
        if current_user.role.value not in ["admin", "owner"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # In production, would get actual configuration from database
        configuration = {
            "entity_id": f"https://app.ai-erp-saas.com/saml/{company_id}",
            "certificate": "mock_certificate"
        }
        
        result = await sso_service.generate_saml_metadata(
            company_id=company_id,
            configuration=configuration
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get SAML metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SAML metadata")

@router.post("/sso/sync-users")
async def sync_sso_users(
    provider: SSOProvider,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync users from SSO provider"""
    try:
        # Check if user has admin privileges
        if current_user.role.value not in ["admin", "owner"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # In production, would get actual configuration from database
        configuration = {}
        
        result = await sso_service.sync_sso_users(
            company_id=str(current_user.company_id),
            provider=provider,
            configuration=configuration,
            db=db
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to sync SSO users: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync SSO users")

# Security Dashboard
@router.get("/dashboard")
async def get_security_dashboard(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security dashboard data"""
    try:
        result = await enterprise_security_service.get_security_dashboard_data(
            company_id=str(current_user.company_id),
            db=db,
            days=days
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get security dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security dashboard")

# Audit and Compliance
@router.post("/audit/report")
async def generate_audit_report(
    request: AuditReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate audit report for compliance"""
    try:
        # Check if user has admin privileges
        if current_user.role.value not in ["admin", "owner"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = await enterprise_security_service.generate_audit_report(
            company_id=str(current_user.company_id),
            start_date=request.start_date,
            end_date=request.end_date,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate audit report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audit report")

@router.get("/policies")
async def get_security_policies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security policies"""
    try:
        # In production, would get from database
        policies = [
            {
                "name": "Password Policy",
                "description": "Strong password requirements",
                "enforcement_level": "mandatory",
                "rules": [
                    {"min_length": 12, "require_uppercase": True, "require_lowercase": True,
                     "require_numbers": True, "require_special_chars": True, "max_age_days": 90},
                    {"prevent_reuse": 5, "lockout_attempts": 5, "lockout_duration_minutes": 30}
                ]
            },
            {
                "name": "Session Management",
                "description": "Secure session handling",
                "enforcement_level": "mandatory",
                "rules": [
                    {"max_session_duration_hours": 8, "idle_timeout_minutes": 30,
                     "require_reauth_for_sensitive_actions": True},
                    {"concurrent_session_limit": 3, "ip_validation": True}
                ]
            },
            {
                "name": "Data Access Control",
                "description": "Role-based data access",
                "enforcement_level": "mandatory",
                "rules": [
                    {"principle": "least_privilege", "require_justification": True,
                     "audit_all_access": True, "data_classification": True},
                    {"encryption_at_rest": True, "encryption_in_transit": True}
                ]
            }
        ]
        
        return {"policies": policies}
        
    except Exception as e:
        logger.error(f"Failed to get security policies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security policies")

@router.put("/policies")
async def update_security_policy(
    request: SecurityPolicyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update security policy"""
    try:
        # Check if user has admin privileges
        if current_user.role.value not in ["admin", "owner"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # In production, would update policy in database
        logger.info(f"Updating security policy: {request.name}")
        
        return {"success": True, "message": "Security policy updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update security policy: {e}")
        raise HTTPException(status_code=500, detail="Failed to update security policy")

# Security Events
@router.get("/events")
async def get_security_events(
    limit: int = 50,
    offset: int = 0,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security events"""
    try:
        # Check if user has admin privileges
        if current_user.role.value not in ["admin", "owner"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # In production, would query audit logs with filters
        events = []  # Mock data
        
        return {
            "events": events,
            "total": len(events),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Failed to get security events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get security events")

# Session Management
@router.get("/sessions")
async def get_active_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active sessions for the current user"""
    try:
        # In production, would get from session store
        sessions = []  # Mock data
        
        return {"sessions": sessions}
        
    except Exception as e:
        logger.error(f"Failed to get active sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active sessions")

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session"""
    try:
        # In production, would revoke session from session store
        logger.info(f"Revoking session {session_id} for user {current_user.id}")
        
        return {"success": True, "message": "Session revoked successfully"}
        
    except Exception as e:
        logger.error(f"Failed to revoke session: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke session")

@router.delete("/sessions")
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke all sessions for the current user"""
    try:
        # In production, would revoke all sessions from session store
        logger.info(f"Revoking all sessions for user {current_user.id}")
        
        return {"success": True, "message": "All sessions revoked successfully"}
        
    except Exception as e:
        logger.error(f"Failed to revoke all sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke all sessions")
