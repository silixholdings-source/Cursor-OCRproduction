"""
Azure AD / Office 365 Authentication Service
Enterprise SSO integration with Microsoft ecosystem
"""
import logging
import msal
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session

from core.config import settings
from src.models.user import User, UserRole, UserStatus
from src.models.company import Company, CompanyStatus
from core.auth import auth_manager

logger = logging.getLogger(__name__)

class AzureADService:
    """Azure Active Directory authentication service"""
    
    def __init__(self):
        self.client_id = settings.AZURE_CLIENT_ID
        self.client_secret = settings.AZURE_CLIENT_SECRET
        self.tenant_id = settings.AZURE_TENANT_ID
        self.redirect_uri = settings.AZURE_REDIRECT_URI
        
        # Microsoft Graph scopes for user info and organization
        self.scopes = [
            "https://graph.microsoft.com/User.Read",
            "https://graph.microsoft.com/Organization.Read.All",
            "https://graph.microsoft.com/Directory.Read.All"
        ]
        
        # Initialize MSAL application
        if all([self.client_id, self.client_secret, self.tenant_id]):
            self.app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            )
        else:
            logger.warning("Azure AD configuration incomplete")
            self.app = None
    
    def get_authorization_url(self, state: str = None) -> Dict[str, str]:
        """Get Azure AD authorization URL for OAuth2 flow"""
        if not self.app:
            raise ValueError("Azure AD not configured")
        
        auth_url = self.app.get_authorization_request_url(
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
            state=state or str(uuid.uuid4())
        )
        
        return {
            "auth_url": auth_url,
            "state": state
        }
    
    async def handle_callback(self, code: str, state: str, db: Session) -> Dict[str, Any]:
        """Handle Azure AD OAuth2 callback and create/login user"""
        if not self.app:
            raise ValueError("Azure AD not configured")
        
        try:
            # Exchange authorization code for tokens
            result = self.app.acquire_token_by_authorization_code(
                code=code,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            if "error" in result:
                raise Exception(f"Azure AD authentication failed: {result.get('error_description', result['error'])}")
            
            # Get user info from Microsoft Graph
            access_token = result["access_token"]
            user_info = await self._get_user_info(access_token)
            org_info = await self._get_organization_info(access_token)
            
            # Create or update user
            user = await self._create_or_update_user(user_info, org_info, db)
            
            # Create JWT tokens for our application
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "company_id": str(user.company_id),
                "role": user.role.value,
                "auth_provider": "azure_ad"
            }
            
            access_token_jwt = auth_manager.create_access_token(token_data)
            refresh_token_jwt = auth_manager.create_refresh_token(token_data)
            
            return {
                "status": "success",
                "access_token": access_token_jwt,
                "refresh_token": refresh_token_jwt,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.full_name,
                    "role": user.role.value,
                    "company_id": str(user.company_id),
                    "auth_provider": "azure_ad"
                },
                "company": {
                    "id": str(user.company.id),
                    "name": user.company.name,
                    "tier": user.company.tier.value
                }
            }
            
        except Exception as e:
            logger.error(f"Azure AD callback handling failed: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
    
    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Microsoft Graph"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers=headers
        )
        response.raise_for_status()
        
        user_data = response.json()
        
        return {
            "id": user_data.get("id"),
            "email": user_data.get("mail") or user_data.get("userPrincipalName"),
            "first_name": user_data.get("givenName", ""),
            "last_name": user_data.get("surname", ""),
            "display_name": user_data.get("displayName", ""),
            "job_title": user_data.get("jobTitle"),
            "department": user_data.get("department"),
            "office_location": user_data.get("officeLocation"),
            "mobile_phone": user_data.get("mobilePhone"),
            "business_phones": user_data.get("businessPhones", [])
        }
    
    async def _get_organization_info(self, access_token: str) -> Dict[str, Any]:
        """Get organization information from Microsoft Graph"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(
                "https://graph.microsoft.com/v1.0/organization",
                headers=headers
            )
            response.raise_for_status()
            
            org_data = response.json()
            if org_data.get("value"):
                org = org_data["value"][0]
                return {
                    "id": org.get("id"),
                    "name": org.get("displayName"),
                    "domain": org.get("verifiedDomains", [{}])[0].get("name"),
                    "country": org.get("countryLetterCode"),
                    "city": org.get("city"),
                    "state": org.get("state")
                }
        except Exception as e:
            logger.warning(f"Failed to get organization info: {e}")
        
        # Fallback organization info
        return {
            "id": str(uuid.uuid4()),
            "name": "Unknown Organization",
            "domain": "unknown.com"
        }
    
    async def _create_or_update_user(self, user_info: Dict[str, Any], org_info: Dict[str, Any], db: Session) -> User:
        """Create or update user from Azure AD information"""
        
        # Check if user already exists
        user = db.query(User).filter(User.email == user_info["email"]).first()
        
        if user:
            # Update existing user with latest Azure AD info
            user.first_name = user_info["first_name"]
            user.last_name = user_info["last_name"]
            user.status = UserStatus.ACTIVE
            user.is_email_verified = True
            user.last_login = datetime.now(UTC)
            
            # Update Azure AD specific fields
            if not hasattr(user, 'azure_ad_id'):
                user.azure_ad_id = user_info["id"]
            
            db.commit()
            return user
        
        # Check if company exists
        company = db.query(Company).filter(Company.domain == org_info["domain"]).first()
        
        if not company:
            # Create new company from Azure AD org info
            company = Company(
                id=uuid.uuid4(),
                name=org_info["name"],
                domain=org_info["domain"],
                status=CompanyStatus.ACTIVE,
                country=org_info.get("country"),
                city=org_info.get("city"),
                state=org_info.get("state"),
                auth_provider="azure_ad",
                azure_tenant_id=self.tenant_id
            )
            db.add(company)
            db.flush()  # Get company ID
        
        # Create new user
        user = User(
            id=uuid.uuid4(),
            email=user_info["email"],
            username=user_info["email"].split("@")[0],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            company_id=company.id,
            role=UserRole.USER,  # Default role, can be updated by admin
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            auth_provider="azure_ad",
            azure_ad_id=user_info["id"],
            job_title=user_info.get("job_title"),
            department=user_info.get("department"),
            phone=user_info.get("mobile_phone")
        )
        
        # Set first user as admin
        if db.query(User).filter(User.company_id == company.id).count() == 0:
            user.role = UserRole.ADMIN
        
        db.add(user)
        db.commit()
        
        return user

class Office365Service:
    """Office 365 specific authentication and integration"""
    
    def __init__(self):
        self.azure_service = AzureADService()
        
        # Office 365 specific scopes
        self.office365_scopes = [
            "https://graph.microsoft.com/User.Read",
            "https://graph.microsoft.com/Mail.Read",
            "https://graph.microsoft.com/Calendars.Read",
            "https://graph.microsoft.com/Files.Read",
            "https://graph.microsoft.com/Sites.Read.All"
        ]
    
    async def authenticate_with_office365(self, code: str, state: str, db: Session) -> Dict[str, Any]:
        """Authenticate user with Office 365 and get extended permissions"""
        
        # Use Azure AD service for base authentication
        auth_result = await self.azure_service.handle_callback(code, state, db)
        
        # Add Office 365 specific features
        auth_result["office365_features"] = {
            "email_integration": True,
            "calendar_integration": True,
            "onedrive_integration": True,
            "sharepoint_integration": True
        }
        
        return auth_result
    
    async def get_user_calendar(self, access_token: str) -> List[Dict[str, Any]]:
        """Get user's calendar events (for invoice due date integration)"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me/events",
                headers=headers,
                params={"$top": 10, "$orderby": "start/dateTime"}
            )
            response.raise_for_status()
            
            events = response.json().get("value", [])
            return events
            
        except Exception as e:
            logger.error(f"Failed to get calendar events: {e}")
            return []

class ActiveDirectoryService:
    """Active Directory integration service for on-premises SSO"""
    
    def __init__(self):
        self.ldap_server = settings.LDAP_SERVER
        self.ldap_base_dn = settings.LDAP_BASE_DN
        self.ldap_bind_user = settings.LDAP_BIND_USER
        self.ldap_bind_password = settings.LDAP_BIND_PASSWORD
        self.ldap_user_filter = settings.LDAP_USER_FILTER or "(sAMAccountName={username})"
        
    async def authenticate_ldap_user(self, username: str, password: str, db: Session) -> Dict[str, Any]:
        """Authenticate user against Active Directory LDAP"""
        
        try:
            # Note: In production, you would use python-ldap or ldap3
            # For now, implementing the structure for enterprise deployment
            
            # Simulate LDAP authentication
            ldap_user_info = await self._ldap_authenticate(username, password)
            
            if not ldap_user_info:
                raise Exception("LDAP authentication failed")
            
            # Create or update user from LDAP info
            user = await self._create_or_update_ldap_user(ldap_user_info, db)
            
            # Create JWT tokens
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "company_id": str(user.company_id),
                "role": user.role.value,
                "auth_provider": "active_directory"
            }
            
            access_token = auth_manager.create_access_token(token_data)
            refresh_token = auth_manager.create_refresh_token(token_data)
            
            return {
                "status": "success",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.full_name,
                    "role": user.role.value,
                    "auth_provider": "active_directory"
                }
            }
            
        except Exception as e:
            logger.error(f"Active Directory authentication failed: {str(e)}")
            raise Exception(f"LDAP authentication failed: {str(e)}")
    
    async def _ldap_authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate against LDAP server"""
        
        # In production, implement actual LDAP authentication:
        # import ldap3
        # server = ldap3.Server(self.ldap_server, use_ssl=True)
        # conn = ldap3.Connection(server, user=bind_dn, password=password)
        # if conn.bind():
        #     # Search for user and get attributes
        #     return user_attributes
        
        # For demo purposes, return mock LDAP user data
        if username and password:
            return {
                "username": username,
                "email": f"{username}@company.com",
                "first_name": username.title(),
                "last_name": "User",
                "department": "IT",
                "title": "Employee",
                "groups": ["Domain Users", "ERP Users"]
            }
        
        return None
    
    async def _create_or_update_ldap_user(self, ldap_info: Dict[str, Any], db: Session) -> User:
        """Create or update user from LDAP information"""
        
        # Check if user exists
        user = db.query(User).filter(User.email == ldap_info["email"]).first()
        
        if user:
            # Update existing user
            user.first_name = ldap_info["first_name"]
            user.last_name = ldap_info["last_name"]
            user.status = UserStatus.ACTIVE
            user.is_email_verified = True
            user.last_login = datetime.now(UTC)
            user.department = ldap_info.get("department")
            user.job_title = ldap_info.get("title")
            
            db.commit()
            return user
        
        # Get or create company
        domain = ldap_info["email"].split("@")[1]
        company = db.query(Company).filter(Company.domain == domain).first()
        
        if not company:
            company = Company(
                id=uuid.uuid4(),
                name=domain.split(".")[0].title(),
                domain=domain,
                status=CompanyStatus.ACTIVE,
                auth_provider="active_directory"
            )
            db.add(company)
            db.flush()
        
        # Create new user
        user = User(
            id=uuid.uuid4(),
            email=ldap_info["email"],
            username=ldap_info["username"],
            first_name=ldap_info["first_name"],
            last_name=ldap_info["last_name"],
            company_id=company.id,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            auth_provider="active_directory",
            department=ldap_info.get("department"),
            job_title=ldap_info.get("title")
        )
        
        db.add(user)
        db.commit()
        
        return user

class SAMLService:
    """SAML 2.0 authentication service for enterprise SSO"""
    
    def __init__(self):
        self.entity_id = settings.SAML_ENTITY_ID
        self.sso_url = settings.SAML_SSO_URL
        self.x509_cert = settings.SAML_X509_CERT
        self.private_key = settings.SAML_PRIVATE_KEY
    
    def generate_saml_request(self) -> str:
        """Generate SAML authentication request"""
        
        # In production, use python-saml library
        # For now, return structure for enterprise deployment
        
        saml_request_template = f"""
        <samlp:AuthnRequest 
            xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
            ID="_{uuid.uuid4()}"
            Version="2.0"
            IssueInstant="{datetime.now(UTC).isoformat()}Z"
            Destination="{self.sso_url}"
            AssertionConsumerServiceURL="{settings.SAML_ACS_URL}">
            <saml:Issuer>{self.entity_id}</saml:Issuer>
        </samlp:AuthnRequest>
        """
        
        return saml_request_template
    
    async def handle_saml_response(self, saml_response: str, db: Session) -> Dict[str, Any]:
        """Handle SAML response and authenticate user"""
        
        # In production, validate SAML response signature and extract user attributes
        # For now, implement structure for enterprise deployment
        
        # Mock SAML user extraction
        user_attributes = {
            "email": "user@enterprise.com",
            "first_name": "Enterprise",
            "last_name": "User",
            "department": "Finance",
            "role": "Manager"
        }
        
        # Create or update user
        user = await self._create_or_update_saml_user(user_attributes, db)
        
        # Create JWT tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "company_id": str(user.company_id),
            "role": user.role.value,
            "auth_provider": "saml"
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        return {
            "status": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "role": user.role.value,
                "auth_provider": "saml"
            }
        }
    
    async def _create_or_update_saml_user(self, saml_attributes: Dict[str, Any], db: Session) -> User:
        """Create or update user from SAML attributes"""
        
        # Implementation similar to Azure AD user creation
        # Check if user exists, create/update accordingly
        
        user = db.query(User).filter(User.email == saml_attributes["email"]).first()
        
        if not user:
            # Create new user from SAML attributes
            domain = saml_attributes["email"].split("@")[1]
            company = db.query(Company).filter(Company.domain == domain).first()
            
            if not company:
                company = Company(
                    id=uuid.uuid4(),
                    name=domain.split(".")[0].title(),
                    domain=domain,
                    status=CompanyStatus.ACTIVE,
                    auth_provider="saml"
                )
                db.add(company)
                db.flush()
            
            user = User(
                id=uuid.uuid4(),
                email=saml_attributes["email"],
                username=saml_attributes["email"].split("@")[0],
                first_name=saml_attributes["first_name"],
                last_name=saml_attributes["last_name"],
                company_id=company.id,
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                auth_provider="saml",
                department=saml_attributes.get("department")
            )
            
            db.add(user)
            db.commit()
        
        return user

# Global service instances
azure_ad_service = AzureADService()
office365_service = Office365Service()
active_directory_service = ActiveDirectoryService()
saml_service = SAMLService()


