"""
Security schemas
Pydantic models for security-related API requests and responses
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class MFAMethod(str, Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"
    HARDWARE_TOKEN = "hardware_token"
    PUSH_NOTIFICATION = "push_notification"

class SSOProvider(str, Enum):
    AZURE_AD = "azure_ad"
    GOOGLE_WORKSPACE = "google_workspace"
    OKTA = "okta"
    SAML = "saml"
    OAUTH2 = "oauth2"
    LDAP = "ldap"

class SecurityEventType(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGIN_BLOCKED = "login_blocked"
    PASSWORD_CHANGE = "password_change"
    ROLE_CHANGE = "role_change"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_EXPORT = "data_export"
    SYSTEM_CONFIGURATION = "system_configuration"
    SECURITY_VIOLATION = "security_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_VERIFIED = "mfa_verified"
    MFA_VERIFICATION_FAILED = "mfa_verification_failed"
    SSO_LOGIN = "sso_login"
    SSO_CONFIGURED = "sso_configured"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EnforcementLevel(str, Enum):
    ADVISORY = "advisory"
    MANDATORY = "mandatory"
    CRITICAL = "critical"

# MFA Schemas
class MFAEnableRequest(BaseModel):
    method: MFAMethod = Field(..., description="MFA method to enable")

class MFAVerifyRequest(BaseModel):
    code: str = Field(..., description="MFA verification code", min_length=4, max_length=10)
    method: Optional[MFAMethod] = Field(None, description="MFA method (optional)")

class MFAChallengeRequest(BaseModel):
    method: MFAMethod = Field(..., description="MFA method for challenge")

class MFAChallengeVerifyRequest(BaseModel):
    challenge_id: str = Field(..., description="Challenge ID")
    code: str = Field(..., description="Verification code", min_length=4, max_length=10)

class MFAResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    method: Optional[str] = Field(None, description="MFA method")
    message: Optional[str] = Field(None, description="Response message")
    secret: Optional[str] = Field(None, description="TOTP secret (for TOTP setup)")
    qr_code: Optional[str] = Field(None, description="QR code data URL (for TOTP setup)")
    backup_codes: Optional[List[str]] = Field(None, description="Backup recovery codes")
    phone_number: Optional[str] = Field(None, description="Masked phone number (for SMS)")
    email: Optional[str] = Field(None, description="Masked email (for Email)")

# SSO Schemas
class SSOConfigurationRequest(BaseModel):
    provider: SSOProvider = Field(..., description="SSO provider")
    configuration: Dict[str, Any] = Field(..., description="Provider-specific configuration")

class SSOAuthenticationRequest(BaseModel):
    provider: SSOProvider = Field(..., description="SSO provider")
    auth_data: Dict[str, Any] = Field(..., description="Authentication data")
    company_id: str = Field(..., description="Company ID")

class SSOResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    user: Optional[Dict[str, Any]] = Field(None, description="User information")
    session_token: Optional[str] = Field(None, description="Session token")
    is_new_user: Optional[bool] = Field(None, description="Whether user is new")
    sso_provider: Optional[str] = Field(None, description="SSO provider used")

class SAMLMetadataResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="SAML metadata")
    xml_metadata: Optional[str] = Field(None, description="SAML XML metadata")

class SSOUserSyncResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    sync_results: Optional[Dict[str, Any]] = Field(None, description="Sync results")
    message: Optional[str] = Field(None, description="Response message")

# Security Dashboard Schemas
class SecurityDashboardResponse(BaseModel):
    daily_security_events: List[Dict[str, Any]] = Field(..., description="Daily security events")
    event_type_distribution: Dict[str, int] = Field(..., description="Event type distribution")
    risk_level_distribution: Dict[str, int] = Field(..., description="Risk level distribution")
    total_events: int = Field(..., description="Total security events")
    high_risk_events: int = Field(..., description="High risk events count")
    compliance_score: float = Field(..., description="Compliance score")
    period: Dict[str, Any] = Field(..., description="Report period")

# Audit and Compliance Schemas
class AuditReportRequest(BaseModel):
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")

class AuditReportResponse(BaseModel):
    report_id: str = Field(..., description="Report ID")
    company_id: str = Field(..., description="Company ID")
    report_period: Dict[str, str] = Field(..., description="Report period")
    compliance_framework: str = Field(..., description="Compliance framework")
    compliance_metrics: Dict[str, Any] = Field(..., description="Compliance metrics")
    event_summary: Dict[str, int] = Field(..., description="Event summary")
    risk_distribution: Dict[str, int] = Field(..., description="Risk distribution")
    top_active_users: List[tuple] = Field(..., description="Top active users")
    security_policies_applied: List[str] = Field(..., description="Applied security policies")
    generated_at: str = Field(..., description="Report generation timestamp")
    generated_by: str = Field(..., description="Report generated by")

# Security Policy Schemas
class SecurityPolicyRule(BaseModel):
    name: str = Field(..., description="Rule name")
    value: Any = Field(..., description="Rule value")
    description: Optional[str] = Field(None, description="Rule description")

class SecurityPolicyRequest(BaseModel):
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    rules: List[SecurityPolicyRule] = Field(..., description="Policy rules")
    enforcement_level: EnforcementLevel = Field(..., description="Enforcement level")
    applicable_roles: List[str] = Field(..., description="Applicable user roles")

class SecurityPolicyResponse(BaseModel):
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules")
    enforcement_level: str = Field(..., description="Enforcement level")
    applicable_roles: List[str] = Field(..., description="Applicable user roles")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# Security Event Schemas
class SecurityEventResponse(BaseModel):
    id: str = Field(..., description="Event ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    event_type: SecurityEventType = Field(..., description="Event type")
    severity: RiskLevel = Field(..., description="Risk level")
    user_id: Optional[str] = Field(None, description="User ID")
    user_email: Optional[str] = Field(None, description="User email")
    ip_address: str = Field(..., description="IP address")
    user_agent: str = Field(..., description="User agent")
    details: Dict[str, Any] = Field(..., description="Event details")
    location: Optional[Dict[str, str]] = Field(None, description="Geolocation")

class SecurityEventsResponse(BaseModel):
    events: List[SecurityEventResponse] = Field(..., description="Security events")
    total: int = Field(..., description="Total events count")
    limit: int = Field(..., description="Limit applied")
    offset: int = Field(..., description="Offset applied")

# Session Management Schemas
class SessionResponse(BaseModel):
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")
    expires_at: datetime = Field(..., description="Session expiration time")
    ip_address: str = Field(..., description="IP address")
    user_agent: str = Field(..., description="User agent")
    is_current: bool = Field(..., description="Is current session")

class SessionsResponse(BaseModel):
    sessions: List[SessionResponse] = Field(..., description="Active sessions")
    total: int = Field(..., description="Total sessions count")

class SessionRevokeResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")

# Authentication Schemas
class AdvancedAuthRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password", min_length=1)
    mfa_code: Optional[str] = Field(None, description="MFA code (if required)")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")

class AdvancedAuthResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    user: Optional[Dict[str, Any]] = Field(None, description="User information")
    session_token: Optional[str] = Field(None, description="Session token")
    requires_mfa: bool = Field(False, description="Whether MFA is required")
    risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Risk assessment")
    error: Optional[str] = Field(None, description="Error message")

# Password Management Schemas
class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password", min_length=12)
    confirm_password: str = Field(..., description="Confirm new password")

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")

class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., description="New password", min_length=12)
    confirm_password: str = Field(..., description="Confirm new password")

class PasswordResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")

# Compliance Schemas
class ComplianceStatus(BaseModel):
    framework: str = Field(..., description="Compliance framework")
    status: str = Field(..., description="Compliance status")
    score: float = Field(..., description="Compliance score")
    last_assessment: datetime = Field(..., description="Last assessment date")
    next_assessment: datetime = Field(..., description="Next assessment date")
    requirements_met: int = Field(..., description="Requirements met count")
    total_requirements: int = Field(..., description="Total requirements count")

class ComplianceResponse(BaseModel):
    company_id: str = Field(..., description="Company ID")
    compliance_status: List[ComplianceStatus] = Field(..., description="Compliance statuses")
    certifications: List[Dict[str, Any]] = Field(..., description="Certifications")
    audit_trail: Dict[str, Any] = Field(..., description="Audit trail summary")

# Risk Assessment Schemas
class RiskAssessment(BaseModel):
    risk_score: int = Field(..., description="Risk score (0-100)")
    risk_level: RiskLevel = Field(..., description="Risk level")
    risk_factors: List[str] = Field(..., description="Risk factors")
    mitigation_recommendations: List[str] = Field(..., description="Mitigation recommendations")
    assessment_timestamp: datetime = Field(..., description="Assessment timestamp")

class RiskAssessmentResponse(BaseModel):
    user_id: str = Field(..., description="User ID")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment")
    requires_additional_verification: bool = Field(..., description="Requires additional verification")

# Data Encryption Schemas
class EncryptionRequest(BaseModel):
    data: str = Field(..., description="Data to encrypt")

class EncryptionResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    encrypted_data: Optional[str] = Field(None, description="Encrypted data")
    error: Optional[str] = Field(None, description="Error message")

class DecryptionRequest(BaseModel):
    encrypted_data: str = Field(..., description="Encrypted data to decrypt")

class DecryptionResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    decrypted_data: Optional[str] = Field(None, description="Decrypted data")
    error: Optional[str] = Field(None, description="Error message")








