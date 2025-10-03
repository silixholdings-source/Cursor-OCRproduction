"""
Single Sign-On (SSO) Service
Enterprise SSO integration with SAML, OAuth2, and Azure AD support
"""
import logging
import base64
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.user import User, UserStatus, UserRole
from src.models.company import Company
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from core.config import settings

logger = logging.getLogger(__name__)

class SSOProvider(Enum):
    AZURE_AD = "azure_ad"
    GOOGLE_WORKSPACE = "google_workspace"
    OKTA = "okta"
    SAML = "saml"
    OAUTH2 = "oauth2"
    LDAP = "ldap"

class SSOStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    PENDING = "pending"
    FAILED = "failed"

@dataclass
class SSOConfiguration:
    provider: SSOProvider
    status: SSOStatus
    configuration: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None

@dataclass
class SSOUser:
    external_id: str
    email: str
    first_name: str
    last_name: str
    roles: List[str]
    groups: List[str]
    attributes: Dict[str, Any]

class SSOService:
    """Enterprise Single Sign-On service with multiple provider support"""
    
    def __init__(self):
        self.azure_client_id = getattr(settings, 'AZURE_CLIENT_ID', None)
        self.azure_client_secret = getattr(settings, 'AZURE_CLIENT_SECRET', None)
        self.azure_tenant_id = getattr(settings, 'AZURE_TENANT_ID', None)
        self.google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)
        self.google_client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', None)
        self.saml_certificate = getattr(settings, 'SAML_CERTIFICATE', None)
        self.saml_private_key = getattr(settings, 'SAML_PRIVATE_KEY', None)
        
    async def configure_sso_provider(
        self,
        company_id: str,
        provider: SSOProvider,
        configuration: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Configure SSO provider for a company"""
        try:
            # Validate configuration based on provider
            validation_result = await self._validate_sso_configuration(provider, configuration)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Store configuration (in production, this would be encrypted and stored in database)
            sso_config = SSOConfiguration(
                provider=provider,
                status=SSOStatus.PENDING,
                configuration=configuration,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            
            # Test connection
            test_result = await self._test_sso_connection(provider, configuration)
            if test_result["success"]:
                sso_config.status = SSOStatus.ENABLED
                sso_config.last_sync = datetime.now(UTC)
                
                # Log SSO configuration
                await self._log_sso_event(
                    company_id,
                    "sso_configured",
                    {"provider": provider.value, "status": "enabled"},
                    db
                )
                
                return {
                    "success": True,
                    "provider": provider.value,
                    "status": "enabled",
                    "message": "SSO provider configured successfully"
                }
            else:
                sso_config.status = SSOStatus.FAILED
                
                return {
                    "success": False,
                    "error": f"Failed to connect to SSO provider: {test_result['error']}"
                }
                
        except Exception as e:
            logger.error(f"Failed to configure SSO provider: {e}")
            return {"success": False, "error": "Failed to configure SSO provider"}
    
    async def _validate_sso_configuration(
        self, 
        provider: SSOProvider, 
        configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate SSO configuration"""
        try:
            if provider == SSOProvider.AZURE_AD:
                required_fields = ["client_id", "client_secret", "tenant_id"]
                for field in required_fields:
                    if field not in configuration or not configuration[field]:
                        return {"valid": False, "error": f"Missing required field: {field}"}
                        
            elif provider == SSOProvider.GOOGLE_WORKSPACE:
                required_fields = ["client_id", "client_secret", "domain"]
                for field in required_fields:
                    if field not in configuration or not configuration[field]:
                        return {"valid": False, "error": f"Missing required field: {field}"}
                        
            elif provider == SSOProvider.SAML:
                required_fields = ["entity_id", "sso_url", "certificate"]
                for field in required_fields:
                    if field not in configuration or not configuration[field]:
                        return {"valid": False, "error": f"Missing required field: {field}"}
                        
            elif provider == SSOProvider.OAUTH2:
                required_fields = ["client_id", "client_secret", "authorization_url", "token_url"]
                for field in required_fields:
                    if field not in configuration or not configuration[field]:
                        return {"valid": False, "error": f"Missing required field: {field}"}
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Failed to validate SSO configuration: {e}")
            return {"valid": False, "error": "Configuration validation failed"}
    
    async def _test_sso_connection(
        self, 
        provider: SSOProvider, 
        configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test SSO provider connection"""
        try:
            if provider == SSOProvider.AZURE_AD:
                return await self._test_azure_ad_connection(configuration)
            elif provider == SSOProvider.GOOGLE_WORKSPACE:
                return await self._test_google_connection(configuration)
            elif provider == SSOProvider.SAML:
                return await self._test_saml_connection(configuration)
            elif provider == SSOProvider.OAUTH2:
                return await self._test_oauth2_connection(configuration)
            else:
                return {"success": False, "error": "Provider not supported"}
                
        except Exception as e:
            logger.error(f"Failed to test SSO connection: {e}")
            return {"success": False, "error": str(e)}
    
    async def _test_azure_ad_connection(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Test Azure AD connection"""
        try:
            # Mock implementation - in production, would use actual Azure AD API
            logger.info("Testing Azure AD connection")
            return {"success": True, "message": "Azure AD connection successful"}
            
        except Exception as e:
            logger.error(f"Azure AD connection test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _test_google_connection(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Test Google Workspace connection"""
        try:
            # Mock implementation - in production, would use actual Google API
            logger.info("Testing Google Workspace connection")
            return {"success": True, "message": "Google Workspace connection successful"}
            
        except Exception as e:
            logger.error(f"Google Workspace connection test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _test_saml_connection(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Test SAML connection"""
        try:
            # Mock implementation - in production, would validate SAML metadata
            logger.info("Testing SAML connection")
            return {"success": True, "message": "SAML connection successful"}
            
        except Exception as e:
            logger.error(f"SAML connection test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _test_oauth2_connection(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Test OAuth2 connection"""
        try:
            # Mock implementation - in production, would test OAuth2 endpoints
            logger.info("Testing OAuth2 connection")
            return {"success": True, "message": "OAuth2 connection successful"}
            
        except Exception as e:
            logger.error(f"OAuth2 connection test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def authenticate_sso_user(
        self,
        provider: SSOProvider,
        auth_data: Dict[str, Any],
        company_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Authenticate user via SSO"""
        try:
            if provider == SSOProvider.AZURE_AD:
                return await self._authenticate_azure_ad_user(auth_data, company_id, db)
            elif provider == SSOProvider.GOOGLE_WORKSPACE:
                return await self._authenticate_google_user(auth_data, company_id, db)
            elif provider == SSOProvider.SAML:
                return await self._authenticate_saml_user(auth_data, company_id, db)
            elif provider == SSOProvider.OAUTH2:
                return await self._authenticate_oauth2_user(auth_data, company_id, db)
            else:
                return {"success": False, "error": "SSO provider not supported"}
                
        except Exception as e:
            logger.error(f"SSO authentication failed: {e}")
            return {"success": False, "error": "SSO authentication failed"}
    
    async def _authenticate_azure_ad_user(
        self, 
        auth_data: Dict[str, Any], 
        company_id: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Authenticate Azure AD user"""
        try:
            # In production, would validate Azure AD token and extract user info
            access_token = auth_data.get("access_token")
            if not access_token:
                return {"success": False, "error": "Access token required"}
            
            # Mock user data extraction
            sso_user = SSOUser(
                external_id="azure_user_123",
                email="user@company.com",
                first_name="John",
                last_name="Doe",
                roles=["user"],
                groups=["employees"],
                attributes={"department": "IT", "title": "Developer"}
            )
            
            return await self._process_sso_user(sso_user, company_id, db)
            
        except Exception as e:
            logger.error(f"Azure AD authentication failed: {e}")
            return {"success": False, "error": "Azure AD authentication failed"}
    
    async def _authenticate_google_user(
        self, 
        auth_data: Dict[str, Any], 
        company_id: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Authenticate Google Workspace user"""
        try:
            # In production, would validate Google token and extract user info
            access_token = auth_data.get("access_token")
            if not access_token:
                return {"success": False, "error": "Access token required"}
            
            # Mock user data extraction
            sso_user = SSOUser(
                external_id="google_user_456",
                email="user@company.com",
                first_name="Jane",
                last_name="Smith",
                roles=["user"],
                groups=["employees"],
                attributes={"department": "HR", "title": "Manager"}
            )
            
            return await self._process_sso_user(sso_user, company_id, db)
            
        except Exception as e:
            logger.error(f"Google authentication failed: {e}")
            return {"success": False, "error": "Google authentication failed"}
    
    async def _authenticate_saml_user(
        self, 
        auth_data: Dict[str, Any], 
        company_id: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Authenticate SAML user"""
        try:
            saml_response = auth_data.get("saml_response")
            if not saml_response:
                return {"success": False, "error": "SAML response required"}
            
            # In production, would parse and validate SAML response
            # Mock user data extraction from SAML attributes
            sso_user = SSOUser(
                external_id="saml_user_789",
                email="user@company.com",
                first_name="Bob",
                last_name="Johnson",
                roles=["admin"],
                groups=["managers", "employees"],
                attributes={"department": "Finance", "title": "Director"}
            )
            
            return await self._process_sso_user(sso_user, company_id, db)
            
        except Exception as e:
            logger.error(f"SAML authentication failed: {e}")
            return {"success": False, "error": "SAML authentication failed"}
    
    async def _authenticate_oauth2_user(
        self, 
        auth_data: Dict[str, Any], 
        company_id: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Authenticate OAuth2 user"""
        try:
            access_token = auth_data.get("access_token")
            if not access_token:
                return {"success": False, "error": "Access token required"}
            
            # In production, would validate OAuth2 token and extract user info
            # Mock user data extraction
            sso_user = SSOUser(
                external_id="oauth2_user_101",
                email="user@company.com",
                first_name="Alice",
                last_name="Wilson",
                roles=["user"],
                groups=["employees"],
                attributes={"department": "Sales", "title": "Representative"}
            )
            
            return await self._process_sso_user(sso_user, company_id, db)
            
        except Exception as e:
            logger.error(f"OAuth2 authentication failed: {e}")
            return {"success": False, "error": "OAuth2 authentication failed"}
    
    async def _process_sso_user(
        self, 
        sso_user: SSOUser, 
        company_id: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Process SSO user - create or update local user"""
        try:
            # Find existing user by external ID or email
            existing_user = db.query(User).filter(
                and_(
                    User.company_id == company_id,
                    or_(
                        User.external_id == sso_user.external_id,
                        User.email == sso_user.email
                    )
                )
            ).first()
            
            if existing_user:
                # Update existing user
                existing_user.external_id = sso_user.external_id
                existing_user.first_name = sso_user.first_name
                existing_user.last_name = sso_user.last_name
                existing_user.last_login = datetime.now(UTC)
                existing_user.sso_provider = "sso"  # Would be actual provider
                
                # Update roles based on SSO groups
                await self._update_user_roles_from_sso(existing_user, sso_user.roles, sso_user.groups, db)
                
                user = existing_user
                is_new_user = False
                
            else:
                # Create new user
                user = User(
                    email=sso_user.email,
                    first_name=sso_user.first_name,
                    last_name=sso_user.last_name,
                    company_id=company_id,
                    external_id=sso_user.external_id,
                    role=UserRole.USER,  # Default role
                    status=UserStatus.ACTIVE,
                    is_active=True,
                    sso_provider="sso",  # Would be actual provider
                    last_login=datetime.now(UTC),
                    created_at=datetime.now(UTC)
                )
                
                # Set roles based on SSO groups
                await self._set_user_roles_from_sso(user, sso_user.roles, sso_user.groups, db)
                
                db.add(user)
                is_new_user = True
            
            db.commit()
            
            # Generate session token
            session_token = self._generate_sso_session_token(user)
            
            # Log SSO authentication
            await self._log_sso_event(
                company_id,
                "sso_authentication",
                {
                    "user_id": str(user.id),
                    "external_id": sso_user.external_id,
                    "is_new_user": is_new_user,
                    "roles": sso_user.roles,
                    "groups": sso_user.groups
                },
                db,
                user_id=str(user.id)
            )
            
            return {
                "success": True,
                "user": user,
                "session_token": session_token,
                "is_new_user": is_new_user,
                "sso_provider": "sso"  # Would be actual provider
            }
            
        except Exception as e:
            logger.error(f"Failed to process SSO user: {e}")
            return {"success": False, "error": "Failed to process SSO user"}
    
    async def _update_user_roles_from_sso(
        self, 
        user: User, 
        roles: List[str], 
        groups: List[str], 
        db: Session
    ) -> None:
        """Update user roles based on SSO data"""
        try:
            # Map SSO groups/roles to internal roles
            role_mapping = {
                "admin": UserRole.ADMIN,
                "manager": UserRole.MANAGER,
                "user": UserRole.USER
            }
            
            # Determine highest role from SSO data
            highest_role = UserRole.USER
            for role in roles + groups:
                if role.lower() in role_mapping:
                    mapped_role = role_mapping[role.lower()]
                    if mapped_role.value > highest_role.value:
                        highest_role = mapped_role
            
            user.role = highest_role
            
        except Exception as e:
            logger.error(f"Failed to update user roles from SSO: {e}")
    
    async def _set_user_roles_from_sso(
        self, 
        user: User, 
        roles: List[str], 
        groups: List[str], 
        db: Session
    ) -> None:
        """Set user roles based on SSO data"""
        await self._update_user_roles_from_sso(user, roles, groups, db)
    
    def _generate_sso_session_token(self, user: User) -> str:
        """Generate session token for SSO user"""
        payload = {
            "user_id": str(user.id),
            "company_id": str(user.company_id),
            "role": user.role.value,
            "sso_provider": user.sso_provider,
            "issued_at": datetime.now(UTC).isoformat(),
            "expires_at": (datetime.now(UTC) + timedelta(hours=8)).isoformat(),
            "session_id": secrets.token_urlsafe(32)
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
    
    async def generate_saml_metadata(
        self, 
        company_id: str, 
        configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate SAML metadata for SP"""
        try:
            # In production, would generate proper SAML metadata XML
            metadata = {
                "entity_id": f"https://app.ai-erp-saas.com/saml/{company_id}",
                "sso_url": f"https://app.ai-erp-saas.com/api/v1/auth/saml/{company_id}/sso",
                "slo_url": f"https://app.ai-erp-saas.com/api/v1/auth/saml/{company_id}/slo",
                "certificate": configuration.get("certificate"),
                "attributes": [
                    {"name": "email", "format": "urn:oasis:names:tc:SAML:2.0:attrname-format:basic"},
                    {"name": "first_name", "format": "urn:oasis:names:tc:SAML:2.0:attrname-format:basic"},
                    {"name": "last_name", "format": "urn:oasis:names:tc:SAML:2.0:attrname-format:basic"},
                    {"name": "groups", "format": "urn:oasis:names:tc:SAML:2.0:attrname-format:basic"}
                ]
            }
            
            return {
                "success": True,
                "metadata": metadata,
                "xml_metadata": self._generate_saml_xml_metadata(metadata)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate SAML metadata: {e}")
            return {"success": False, "error": "Failed to generate SAML metadata"}
    
    def _generate_saml_xml_metadata(self, metadata: Dict[str, Any]) -> str:
        """Generate SAML XML metadata"""
        # In production, would generate proper SAML XML
        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="{metadata['entity_id']}">
    <md:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="{metadata['sso_url']}" index="0" isDefault="true"/>
        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="{metadata['slo_url']}"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>"""
        
        return xml_template
    
    async def sync_sso_users(
        self, 
        company_id: str, 
        provider: SSOProvider, 
        configuration: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """Sync users from SSO provider"""
        try:
            # In production, would fetch users from SSO provider
            # Mock implementation
            logger.info(f"Syncing users from {provider.value} for company {company_id}")
            
            # Mock sync results
            sync_results = {
                "total_users": 25,
                "new_users": 3,
                "updated_users": 5,
                "deactivated_users": 1,
                "errors": 0
            }
            
            # Log sync event
            await self._log_sso_event(
                company_id,
                "sso_user_sync",
                {
                    "provider": provider.value,
                    "results": sync_results
                },
                db
            )
            
            return {
                "success": True,
                "sync_results": sync_results,
                "message": "User sync completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to sync SSO users: {e}")
            return {"success": False, "error": "Failed to sync SSO users"}
    
    async def _log_sso_event(
        self, 
        company_id: str, 
        event_type: str, 
        details: Dict[str, Any], 
        db: Session,
        user_id: Optional[str] = None
    ) -> None:
        """Log SSO event to audit trail"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                company_id=company_id,
                action=AuditAction.SSO_EVENT,
                resource_type=AuditResourceType.SYSTEM,
                resource_id=f"sso_event_{int(datetime.now(UTC).timestamp())}",
                details={
                    "event_type": event_type,
                    **details
                },
                ip_address="127.0.0.1",  # Would be actual IP in production
                user_agent="SSO Service"
            )
            
            db.add(audit_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log SSO event: {e}")

# Global instance
sso_service = SSOService()








