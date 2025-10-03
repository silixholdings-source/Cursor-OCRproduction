"""
Azure AD / Office 365 / Active Directory SSO Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
import uuid

from core.database import get_db
from core.config import settings
from services.azure_auth import azure_ad_service, office365_service, active_directory_service, saml_service
from schemas.auth import AuthResponse, MessageResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/azure/login")
async def azure_ad_login():
    """Initiate Azure AD OAuth2 flow"""
    try:
        if not settings.ENABLE_SSO:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SSO is not enabled"
            )
        
        if not all([settings.AZURE_CLIENT_ID, settings.AZURE_CLIENT_SECRET, settings.AZURE_TENANT_ID]):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Azure AD configuration incomplete"
            )
        
        # Generate authorization URL
        auth_data = azure_ad_service.get_authorization_url()
        
        return {
            "auth_url": auth_data["auth_url"],
            "state": auth_data["state"],
            "provider": "azure_ad"
        }
        
    except Exception as e:
        logger.error(f"Azure AD login initiation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Azure AD login: {str(e)}"
        )

@router.get("/azure/callback", response_model=AuthResponse)
async def azure_ad_callback(
    code: str = Query(..., description="Authorization code from Azure AD"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db)
):
    """Handle Azure AD OAuth2 callback"""
    try:
        # Handle the callback and authenticate user
        auth_result = await azure_ad_service.handle_callback(code, state, db)
        
        return AuthResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type="bearer",
            user=auth_result["user"],
            company=auth_result["company"]
        )
        
    except Exception as e:
        logger.error(f"Azure AD callback failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Azure AD authentication failed: {str(e)}"
        )

@router.get("/office365/login")
async def office365_login():
    """Initiate Office 365 OAuth2 flow with extended permissions"""
    try:
        if not settings.ENABLE_SSO:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SSO is not enabled"
            )
        
        # Use Azure AD service with Office 365 specific scopes
        auth_data = azure_ad_service.get_authorization_url()
        
        return {
            "auth_url": auth_data["auth_url"],
            "state": auth_data["state"],
            "provider": "office365",
            "features": ["email", "calendar", "onedrive", "sharepoint"]
        }
        
    except Exception as e:
        logger.error(f"Office 365 login initiation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Office 365 login: {str(e)}"
        )

@router.get("/office365/callback", response_model=AuthResponse)
async def office365_callback(
    code: str = Query(..., description="Authorization code from Office 365"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    db: Session = Depends(get_db)
):
    """Handle Office 365 OAuth2 callback"""
    try:
        # Handle the callback with Office 365 extended features
        auth_result = await office365_service.authenticate_with_office365(code, state, db)
        
        return AuthResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type="bearer",
            user=auth_result["user"],
            company=auth_result["company"]
        )
        
    except Exception as e:
        logger.error(f"Office 365 callback failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Office 365 authentication failed: {str(e)}"
        )

@router.post("/ldap/login", response_model=AuthResponse)
async def active_directory_login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Authenticate user against Active Directory LDAP"""
    try:
        if not settings.ENABLE_SSO:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SSO is not enabled"
            )
        
        if not settings.LDAP_SERVER:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Active Directory LDAP not configured"
            )
        
        # Authenticate against LDAP
        auth_result = await active_directory_service.authenticate_ldap_user(username, password, db)
        
        return AuthResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type="bearer",
            user=auth_result["user"]
        )
        
    except Exception as e:
        logger.error(f"LDAP authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Active Directory authentication failed: {str(e)}"
        )

@router.get("/saml/metadata")
async def saml_metadata():
    """Get SAML service provider metadata"""
    try:
        if not settings.ENABLE_SSO:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SSO is not enabled"
            )
        
        # Return SAML SP metadata XML
        metadata_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                     entityID="{settings.SAML_ENTITY_ID or 'ai-erp-saas'}">
  <md:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <md:AssertionConsumerService 
        Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        Location="{settings.SAML_ACS_URL}"
        index="0"/>
  </md:SPSSODescriptor>
</md:EntityDescriptor>"""
        
        return {
            "metadata": metadata_xml,
            "entity_id": settings.SAML_ENTITY_ID or "ai-erp-saas",
            "acs_url": settings.SAML_ACS_URL
        }
        
    except Exception as e:
        logger.error(f"SAML metadata generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SAML metadata: {str(e)}"
        )

@router.post("/saml/acs", response_model=AuthResponse)
async def saml_assertion_consumer(
    request: Request,
    db: Session = Depends(get_db)
):
    """SAML Assertion Consumer Service (ACS) endpoint"""
    try:
        if not settings.ENABLE_SSO:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SSO is not enabled"
            )
        
        # Get SAML response from form data
        form_data = await request.form()
        saml_response = form_data.get("SAMLResponse")
        
        if not saml_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing SAML response"
            )
        
        # Process SAML response
        auth_result = await saml_service.handle_saml_response(saml_response, db)
        
        return AuthResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type="bearer",
            user=auth_result["user"]
        )
        
    except Exception as e:
        logger.error(f"SAML ACS failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SAML authentication failed: {str(e)}"
        )

@router.get("/sso/status")
async def sso_status():
    """Get SSO configuration status"""
    return {
        "sso_enabled": settings.ENABLE_SSO,
        "providers": {
            "azure_ad": {
                "configured": bool(settings.AZURE_CLIENT_ID and settings.AZURE_CLIENT_SECRET and settings.AZURE_TENANT_ID),
                "name": "Azure Active Directory",
                "login_url": "/api/v1/auth/azure/login"
            },
            "office365": {
                "configured": bool(settings.AZURE_CLIENT_ID and settings.AZURE_CLIENT_SECRET and settings.AZURE_TENANT_ID),
                "name": "Office 365",
                "login_url": "/api/v1/auth/office365/login"
            },
            "active_directory": {
                "configured": bool(settings.LDAP_SERVER and settings.LDAP_BASE_DN),
                "name": "Active Directory (LDAP)",
                "login_url": "/api/v1/auth/ldap/login"
            },
            "saml": {
                "configured": bool(settings.SAML_ENTITY_ID and settings.SAML_SSO_URL),
                "name": "SAML 2.0",
                "metadata_url": "/api/v1/auth/saml/metadata"
            }
        }
    }


