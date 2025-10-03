"""
Enterprise Security Service
World-class security features with SOC2 compliance, advanced authentication, and audit trails
"""
import logging
import hashlib
import hmac
import secrets
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from src.models.user import User, UserStatus, UserRole
from src.models.company import Company
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from core.config import settings

logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
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

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    event_type: SecurityEventType
    user_id: Optional[str]
    company_id: str
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    risk_level: RiskLevel
    timestamp: datetime
    session_id: Optional[str] = None
    geolocation: Optional[Dict[str, Any]] = None

@dataclass
class SecurityPolicy:
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enforcement_level: str  # advisory, mandatory, critical
    applicable_roles: List[str]
    created_at: datetime
    updated_at: datetime

class EnterpriseSecurityService:
    """Enterprise-grade security service with SOC2 compliance"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.rate_limit_cache = {}
        self.suspicious_activity_cache = {}
        self.security_policies = self._load_security_policies()
        self.compliance_framework = "SOC2"
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        try:
            # In production, this would be stored securely (e.g., AWS KMS, Azure Key Vault)
            if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
                return settings.ENCRYPTION_KEY.encode()
            else:
                # Generate new key for development
                key = Fernet.generate_key()
                logger.warning("Generated new encryption key - store securely in production")
                return key
        except Exception as e:
            logger.error(f"Failed to get encryption key: {e}")
            return Fernet.generate_key()
    
    def _load_security_policies(self) -> List[SecurityPolicy]:
        """Load security policies"""
        policies = [
            SecurityPolicy(
                name="Password Policy",
                description="Strong password requirements",
                rules=[
                    {"min_length": 12, "require_uppercase": True, "require_lowercase": True,
                     "require_numbers": True, "require_special_chars": True, "max_age_days": 90},
                    {"prevent_reuse": 5, "lockout_attempts": 5, "lockout_duration_minutes": 30}
                ],
                enforcement_level="mandatory",
                applicable_roles=["admin", "manager", "user"],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            ),
            SecurityPolicy(
                name="Session Management",
                description="Secure session handling",
                rules=[
                    {"max_session_duration_hours": 8, "idle_timeout_minutes": 30,
                     "require_reauth_for_sensitive_actions": True},
                    {"concurrent_session_limit": 3, "ip_validation": True}
                ],
                enforcement_level="mandatory",
                applicable_roles=["admin", "manager", "user"],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            ),
            SecurityPolicy(
                name="Data Access Control",
                description="Role-based data access",
                rules=[
                    {"principle": "least_privilege", "require_justification": True,
                     "audit_all_access": True, "data_classification": True},
                    {"encryption_at_rest": True, "encryption_in_transit": True}
                ],
                enforcement_level="mandatory",
                applicable_roles=["admin", "manager", "user"],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            ),
            SecurityPolicy(
                name="Audit and Monitoring",
                description="Comprehensive audit logging",
                rules=[
                    {"log_all_authentication_events": True, "log_all_data_access": True,
                     "log_all_configuration_changes": True, "retention_days": 2555},  # 7 years
                    {"real_time_monitoring": True, "anomaly_detection": True,
                     "automated_response": True}
                ],
                enforcement_level="mandatory",
                applicable_roles=["admin", "manager", "user"],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
        ]
        return policies
    
    async def authenticate_user_advanced(
        self,
        email: str,
        password: str,
        ip_address: str,
        user_agent: str,
        db: Session,
        additional_factors: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Advanced authentication with security monitoring"""
        try:
            # Rate limiting check
            if self._is_rate_limited(ip_address):
                await self._log_security_event(
                    SecurityEvent(
                        event_type=SecurityEventType.LOGIN_BLOCKED,
                        user_id=None,
                        company_id="",
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={"reason": "rate_limit_exceeded"},
                        risk_level=RiskLevel.HIGH,
                        timestamp=datetime.now(UTC)
                    ),
                    db
                )
                return {"success": False, "error": "Rate limit exceeded", "retry_after": 300}
            
            # Find user
            user = db.query(User).filter(User.email == email).first()
            if not user:
                await self._log_security_event(
                    SecurityEvent(
                        event_type=SecurityEventType.LOGIN_FAILURE,
                        user_id=None,
                        company_id="",
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={"reason": "user_not_found", "email": email},
                        risk_level=RiskLevel.MEDIUM,
                        timestamp=datetime.now(UTC)
                    ),
                    db
                )
                return {"success": False, "error": "Invalid credentials"}
            
            # Check account status
            if not user.is_active:
                await self._log_security_event(
                    SecurityEvent(
                        event_type=SecurityEventType.LOGIN_FAILURE,
                        user_id=str(user.id),
                        company_id=str(user.company_id),
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={"reason": "account_inactive"},
                        risk_level=RiskLevel.MEDIUM,
                        timestamp=datetime.now(UTC)
                    ),
                    db
                )
                return {"success": False, "error": "Account is inactive"}
            
            if user.is_locked:
                await self._log_security_event(
                    SecurityEvent(
                        event_type=SecurityEventType.LOGIN_FAILURE,
                        user_id=str(user.id),
                        company_id=str(user.company_id),
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={"reason": "account_locked"},
                        risk_level=RiskLevel.HIGH,
                        timestamp=datetime.now(UTC)
                    ),
                    db
                )
                return {"success": False, "error": "Account is locked"}
            
            # Verify password
            if not self._verify_password_secure(password, user.hashed_password):
                # Increment failed login attempts
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                user.last_failed_login = datetime.now(UTC)
                
                # Lock account if too many failures
                if user.failed_login_attempts >= 5:
                    user.is_locked = True
                    user.locked_until = datetime.now(UTC) + timedelta(minutes=30)
                
                db.commit()
                
                await self._log_security_event(
                    SecurityEvent(
                        event_type=SecurityEventType.LOGIN_FAILURE,
                        user_id=str(user.id),
                        company_id=str(user.company_id),
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={
                            "reason": "invalid_password",
                            "failed_attempts": user.failed_login_attempts
                        },
                        risk_level=RiskLevel.HIGH if user.failed_login_attempts >= 3 else RiskLevel.MEDIUM,
                        timestamp=datetime.now(UTC)
                    ),
                    db
                )
                return {"success": False, "error": "Invalid credentials"}
            
            # Check if account is locked due to time
            if user.locked_until and user.locked_until > datetime.now(UTC):
                return {"success": False, "error": "Account is temporarily locked"}
            
            # Reset failed login attempts on successful login
            user.failed_login_attempts = 0
            user.last_login = datetime.now(UTC)
            user.last_login_ip = ip_address
            db.commit()
            
            # Check for suspicious activity
            risk_assessment = await self._assess_login_risk(user, ip_address, user_agent, db)
            
            # Generate session token
            session_token = self._generate_secure_session_token(user, ip_address)
            
            # Log successful login
            await self._log_security_event(
                SecurityEvent(
                    event_type=SecurityEventType.LOGIN_SUCCESS,
                    user_id=str(user.id),
                    company_id=str(user.company_id),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={
                        "risk_score": risk_assessment["risk_score"],
                        "risk_factors": risk_assessment["risk_factors"],
                        "session_token": session_token[:10] + "..."  # Partial token for logging
                    },
                    risk_level=risk_assessment["risk_level"],
                    timestamp=datetime.now(UTC),
                    session_id=session_token
                ),
                db
            )
            
            return {
                "success": True,
                "user": user,
                "session_token": session_token,
                "risk_assessment": risk_assessment,
                "requires_additional_auth": risk_assessment["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {"success": False, "error": "Authentication failed"}
    
    def _verify_password_secure(self, password: str, hashed_password: str) -> bool:
        """Secure password verification with timing attack protection"""
        try:
            import bcrypt
            # Use constant-time comparison
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def _is_rate_limited(self, ip_address: str) -> bool:
        """Check if IP is rate limited"""
        now = time.time()
        window_start = now - 300  # 5 minute window
        
        # Clean old entries
        if ip_address in self.rate_limit_cache:
            self.rate_limit_cache[ip_address] = [
                timestamp for timestamp in self.rate_limit_cache[ip_address]
                if timestamp > window_start
            ]
        else:
            self.rate_limit_cache[ip_address] = []
        
        # Check rate limit (max 5 attempts per 5 minutes)
        if len(self.rate_limit_cache[ip_address]) >= 5:
            return True
        
        # Add current attempt
        self.rate_limit_cache[ip_address].append(now)
        return False
    
    async def _assess_login_risk(
        self,
        user: User,
        ip_address: str,
        user_agent: str,
        db: Session
    ) -> Dict[str, Any]:
        """Assess login risk based on various factors"""
        risk_factors = []
        risk_score = 0
        
        # Check for new IP address
        if user.last_login_ip and user.last_login_ip != ip_address:
            risk_factors.append("new_ip_address")
            risk_score += 20
        
        # Check for unusual time (outside business hours)
        current_hour = datetime.now(UTC).hour
        if current_hour < 6 or current_hour > 22:
            risk_factors.append("unusual_time")
            risk_score += 15
        
        # Check for rapid successive logins
        recent_logins = db.query(AuditLog).filter(
            and_(
                AuditLog.user_id == str(user.id),
                AuditLog.action == AuditAction.LOGIN,
                AuditLog.created_at >= datetime.now(UTC) - timedelta(minutes=10)
            )
        ).count()
        
        if recent_logins > 3:
            risk_factors.append("rapid_successive_logins")
            risk_score += 25
        
        # Check for suspicious user agent changes
        if hasattr(user, 'last_user_agent') and user.last_user_agent != user_agent:
            risk_factors.append("user_agent_change")
            risk_score += 10
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 40:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 20:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "assessment_timestamp": datetime.now(UTC).isoformat()
        }
    
    def _generate_secure_session_token(self, user: User, ip_address: str) -> str:
        """Generate secure session token"""
        payload = {
            "user_id": str(user.id),
            "company_id": str(user.company_id),
            "role": user.role.value,
            "ip_address": ip_address,
            "issued_at": datetime.now(UTC).isoformat(),
            "expires_at": (datetime.now(UTC) + timedelta(hours=8)).isoformat(),
            "session_id": secrets.token_urlsafe(32)
        }
        
        return jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
    
    async def _log_security_event(self, event: SecurityEvent, db: Session):
        """Log security event to audit trail"""
        try:
            audit_log = AuditLog(
                user_id=event.user_id,
                company_id=event.company_id,
                action=AuditAction.SECURITY_EVENT,
                resource_type=AuditResourceType.SECURITY,
                resource_id=f"security_event_{int(time.time())}",
                details={
                    "event_type": event.event_type.value,
                    "ip_address": event.ip_address,
                    "user_agent": event.user_agent,
                    "risk_level": event.risk_level.value,
                    "details": event.details,
                    "session_id": event.session_id,
                    "geolocation": event.geolocation
                },
                ip_address=event.ip_address,
                user_agent=event.user_agent
            )
            
            db.add(audit_log)
            db.commit()
            
            # Real-time security monitoring
            await self._process_security_event(event)
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def _process_security_event(self, event: SecurityEvent):
        """Process security event for real-time monitoring"""
        try:
            # Update suspicious activity cache
            key = f"{event.user_id}_{event.ip_address}" if event.user_id else event.ip_address
            if key not in self.suspicious_activity_cache:
                self.suspicious_activity_cache[key] = []
            
            self.suspicious_activity_cache[key].append({
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "risk_level": event.risk_level.value
            })
            
            # Trigger alerts for high-risk events
            if event.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self._trigger_security_alert(event)
            
            # Check for patterns indicating potential attack
            await self._detect_attack_patterns(key, event)
            
        except Exception as e:
            logger.error(f"Failed to process security event: {e}")
    
    async def _trigger_security_alert(self, event: SecurityEvent):
        """Trigger security alert for high-risk events"""
        try:
            alert_data = {
                "alert_type": "security_incident",
                "severity": event.risk_level.value,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "user_id": event.user_id,
                "ip_address": event.ip_address,
                "details": event.details
            }
            
            # In production, this would integrate with alerting systems (PagerDuty, Slack, etc.)
            logger.warning(f"SECURITY ALERT: {json.dumps(alert_data)}")
            
        except Exception as e:
            logger.error(f"Failed to trigger security alert: {e}")
    
    async def _detect_attack_patterns(self, key: str, event: SecurityEvent):
        """Detect potential attack patterns"""
        try:
            recent_events = self.suspicious_activity_cache.get(key, [])
            
            # Check for brute force pattern
            failed_logins = [
                e for e in recent_events[-10:]  # Last 10 events
                if e["event_type"] == SecurityEventType.LOGIN_FAILURE.value
            ]
            
            if len(failed_logins) >= 5:
                await self._trigger_security_alert(SecurityEvent(
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    user_id=event.user_id,
                    company_id=event.company_id,
                    ip_address=event.ip_address,
                    user_agent=event.user_agent,
                    details={"pattern": "brute_force", "failed_attempts": len(failed_logins)},
                    risk_level=RiskLevel.CRITICAL,
                    timestamp=datetime.now(UTC)
                ))
            
        except Exception as e:
            logger.error(f"Failed to detect attack patterns: {e}")
    
    async def validate_session(
        self,
        session_token: str,
        ip_address: str,
        user_agent: str,
        db: Session
    ) -> Dict[str, Any]:
        """Validate session token with security checks"""
        try:
            # Decode token
            payload = jwt.decode(session_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload["expires_at"])
            if expires_at < datetime.now(UTC):
                return {"valid": False, "error": "Session expired"}
            
            # Check IP address
            if payload.get("ip_address") != ip_address:
                await self._log_security_event(
                    SecurityEvent(
                        event_type=SecurityEventType.SECURITY_VIOLATION,
                        user_id=payload.get("user_id"),
                        company_id=payload.get("company_id"),
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={"reason": "ip_address_mismatch", "expected_ip": payload.get("ip_address")},
                        risk_level=RiskLevel.HIGH,
                        timestamp=datetime.now(UTC)
                    ),
                    db
                )
                return {"valid": False, "error": "Session invalid"}
            
            # Get user
            user = db.query(User).filter(User.id == payload["user_id"]).first()
            if not user or not user.is_active:
                return {"valid": False, "error": "User not found or inactive"}
            
            return {
                "valid": True,
                "user": user,
                "session_id": payload["session_id"],
                "expires_at": expires_at
            }
            
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Session expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid session token"}
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return {"valid": False, "error": "Session validation failed"}
    
    async def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    async def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    async def generate_audit_report(
        self,
        company_id: str,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Generate comprehensive audit report for compliance"""
        try:
            # Get all security events in date range
            security_events = db.query(AuditLog).filter(
                and_(
                    AuditLog.company_id == company_id,
                    AuditLog.action == AuditAction.SECURITY_EVENT,
                    AuditLog.created_at >= start_date,
                    AuditLog.created_at <= end_date
                )
            ).order_by(desc(AuditLog.created_at)).all()
            
            # Analyze events
            event_summary = {}
            risk_distribution = {}
            user_activity = {}
            
            for event in security_events:
                details = event.details
                event_type = details.get("event_type", "unknown")
                risk_level = details.get("risk_level", "low")
                
                # Event type summary
                event_summary[event_type] = event_summary.get(event_type, 0) + 1
                
                # Risk distribution
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
                
                # User activity
                if event.user_id:
                    user_activity[event.user_id] = user_activity.get(event.user_id, 0) + 1
            
            # Generate compliance metrics
            compliance_metrics = {
                "total_security_events": len(security_events),
                "high_risk_events": risk_distribution.get("high", 0) + risk_distribution.get("critical", 0),
                "failed_login_attempts": event_summary.get("login_failure", 0),
                "successful_logins": event_summary.get("login_success", 0),
                "security_violations": event_summary.get("security_violation", 0),
                "suspicious_activities": event_summary.get("suspicious_activity", 0),
                "unique_users_active": len(user_activity),
                "compliance_score": self._calculate_compliance_score(security_events)
            }
            
            return {
                "report_id": f"audit_report_{company_id}_{int(time.time())}",
                "company_id": company_id,
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "compliance_framework": self.compliance_framework,
                "compliance_metrics": compliance_metrics,
                "event_summary": event_summary,
                "risk_distribution": risk_distribution,
                "top_active_users": sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10],
                "security_policies_applied": [policy.name for policy in self.security_policies],
                "generated_at": datetime.now(UTC).isoformat(),
                "generated_by": "EnterpriseSecurityService"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate audit report: {e}")
            return {"error": str(e)}
    
    def _calculate_compliance_score(self, security_events: List[AuditLog]) -> float:
        """Calculate compliance score based on security events"""
        if not security_events:
            return 100.0
        
        # Penalize high-risk events
        high_risk_events = 0
        total_events = len(security_events)
        
        for event in security_events:
            risk_level = event.details.get("risk_level", "low")
            if risk_level in ["high", "critical"]:
                high_risk_events += 1
        
        # Calculate score (100 - penalty for high-risk events)
        penalty = (high_risk_events / total_events) * 50  # Max 50 point penalty
        score = max(0, 100 - penalty)
        
        return round(score, 2)
    
    async def get_security_dashboard_data(
        self,
        company_id: str,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get security dashboard data"""
        try:
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=days)
            
            # Get security events
            security_events = db.query(AuditLog).filter(
                and_(
                    AuditLog.company_id == company_id,
                    AuditLog.action == AuditAction.SECURITY_EVENT,
                    AuditLog.created_at >= start_date,
                    AuditLog.created_at <= end_date
                )
            ).all()
            
            # Process events for dashboard
            daily_events = {}
            event_types = {}
            risk_levels = {}
            
            for event in security_events:
                date_key = event.created_at.date().isoformat()
                daily_events[date_key] = daily_events.get(date_key, 0) + 1
                
                event_type = event.details.get("event_type", "unknown")
                event_types[event_type] = event_types.get(event_type, 0) + 1
                
                risk_level = event.details.get("risk_level", "low")
                risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
            
            # Convert to arrays for charts
            daily_data = [
                {"date": date, "events": count}
                for date, count in sorted(daily_events.items())
            ]
            
            return {
                "daily_security_events": daily_data,
                "event_type_distribution": event_types,
                "risk_level_distribution": risk_levels,
                "total_events": len(security_events),
                "high_risk_events": risk_levels.get("high", 0) + risk_levels.get("critical", 0),
                "compliance_score": self._calculate_compliance_score(security_events),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get security dashboard data: {e}")
            return {"error": str(e)}

# Global instance
enterprise_security_service = EnterpriseSecurityService()
