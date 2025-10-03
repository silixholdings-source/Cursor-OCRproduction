"""
Multi-Factor Authentication Service
Enterprise-grade MFA with TOTP, SMS, and hardware token support
"""
import logging
import secrets
import pyotp
import qrcode
import io
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.user import User, UserStatus, UserRole
from src.models.company import Company
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from core.config import settings

logger = logging.getLogger(__name__)

class MFAMethod(Enum):
    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"    # SMS-based codes
    EMAIL = "email"  # Email-based codes
    BACKUP_CODES = "backup_codes"  # Backup recovery codes
    HARDWARE_TOKEN = "hardware_token"  # FIDO2/WebAuthn
    PUSH_NOTIFICATION = "push_notification"  # Mobile push notifications

class MFAStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    REQUIRED = "required"
    BYPASSED = "bypassed"

@dataclass
class MFAChallenge:
    challenge_id: str
    user_id: str
    method: MFAMethod
    expires_at: datetime
    attempts_remaining: int
    metadata: Dict[str, Any]

@dataclass
class MFARecoveryCode:
    code: str
    used: bool
    used_at: Optional[datetime]

class MFAService:
    """Enterprise-grade Multi-Factor Authentication service"""
    
    def __init__(self):
        self.totp_issuer = getattr(settings, 'MFA_ISSUER_NAME', 'AI ERP SaaS')
        self.sms_provider = None  # Would be configured with actual SMS provider
        self.email_provider = None  # Would be configured with actual email provider
        self.push_service = None  # Would be configured with push notification service
        self.active_challenges = {}  # In production, use Redis or database
        
    async def enable_mfa_for_user(
        self,
        user: User,
        method: MFAMethod,
        db: Session
    ) -> Dict[str, Any]:
        """Enable MFA for a user with the specified method"""
        try:
            if method == MFAMethod.TOTP:
                return await self._setup_totp_mfa(user, db)
            elif method == MFAMethod.SMS:
                return await self._setup_sms_mfa(user, db)
            elif method == MFAMethod.EMAIL:
                return await self._setup_email_mfa(user, db)
            elif method == MFAMethod.BACKUP_CODES:
                return await self._setup_backup_codes(user, db)
            else:
                return {"success": False, "error": f"MFA method {method.value} not supported"}
                
        except Exception as e:
            logger.error(f"Failed to enable MFA for user {user.id}: {e}")
            return {"success": False, "error": "Failed to enable MFA"}
    
    async def _setup_totp_mfa(self, user: User, db: Session) -> Dict[str, Any]:
        """Setup TOTP (Google Authenticator) MFA"""
        try:
            # Generate secret key
            secret = pyotp.random_base32()
            
            # Create TOTP object
            totp = pyotp.TOTP(secret)
            
            # Generate provisioning URI
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name=self.totp_issuer
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            
            # Store MFA secret (encrypted)
            mfa_data = {
                "method": MFAMethod.TOTP.value,
                "secret": secret,
                "enabled_at": datetime.now(UTC).isoformat(),
                "backup_codes": await self._generate_backup_codes()
            }
            
            # Update user MFA settings
            user.mfa_enabled = True
            user.mfa_method = MFAMethod.TOTP.value
            user.mfa_secret = await self._encrypt_mfa_data(mfa_data)
            user.mfa_backup_codes = await self._encrypt_backup_codes(mfa_data["backup_codes"])
            
            db.commit()
            
            # Log MFA setup
            await self._log_mfa_event(
                user, 
                "mfa_enabled", 
                {"method": MFAMethod.TOTP.value}, 
                db
            )
            
            return {
                "success": True,
                "method": MFAMethod.TOTP.value,
                "secret": secret,
                "qr_code": f"data:image/png;base64,{qr_code_base64}",
                "provisioning_uri": provisioning_uri,
                "backup_codes": mfa_data["backup_codes"]
            }
            
        except Exception as e:
            logger.error(f"Failed to setup TOTP MFA: {e}")
            return {"success": False, "error": "Failed to setup TOTP MFA"}
    
    async def _setup_sms_mfa(self, user: User, db: Session) -> Dict[str, Any]:
        """Setup SMS-based MFA"""
        try:
            if not user.phone_number:
                return {"success": False, "error": "Phone number required for SMS MFA"}
            
            # Generate verification code
            verification_code = self._generate_numeric_code()
            
            # Send SMS (mock implementation)
            await self._send_sms_code(user.phone_number, verification_code)
            
            # Store pending verification
            mfa_data = {
                "method": MFAMethod.SMS.value,
                "phone_number": user.phone_number,
                "verification_code": verification_code,
                "code_expires_at": (datetime.now(UTC) + timedelta(minutes=5)).isoformat(),
                "setup_initiated_at": datetime.now(UTC).isoformat()
            }
            
            user.mfa_pending_data = await self._encrypt_mfa_data(mfa_data)
            db.commit()
            
            return {
                "success": True,
                "method": MFAMethod.SMS.value,
                "message": "Verification code sent to your phone",
                "phone_number": self._mask_phone_number(user.phone_number)
            }
            
        except Exception as e:
            logger.error(f"Failed to setup SMS MFA: {e}")
            return {"success": False, "error": "Failed to setup SMS MFA"}
    
    async def _setup_email_mfa(self, user: User, db: Session) -> Dict[str, Any]:
        """Setup Email-based MFA"""
        try:
            # Generate verification code
            verification_code = self._generate_alphanumeric_code()
            
            # Send email (mock implementation)
            await self._send_email_code(user.email, verification_code)
            
            # Store pending verification
            mfa_data = {
                "method": MFAMethod.EMAIL.value,
                "email": user.email,
                "verification_code": verification_code,
                "code_expires_at": (datetime.now(UTC) + timedelta(minutes=10)).isoformat(),
                "setup_initiated_at": datetime.now(UTC).isoformat()
            }
            
            user.mfa_pending_data = await self._encrypt_mfa_data(mfa_data)
            db.commit()
            
            return {
                "success": True,
                "method": MFAMethod.EMAIL.value,
                "message": "Verification code sent to your email",
                "email": self._mask_email(user.email)
            }
            
        except Exception as e:
            logger.error(f"Failed to setup Email MFA: {e}")
            return {"success": False, "error": "Failed to setup Email MFA"}
    
    async def _setup_backup_codes(self, user: User, db: Session) -> Dict[str, Any]:
        """Setup backup recovery codes"""
        try:
            backup_codes = await self._generate_backup_codes()
            
            mfa_data = {
                "method": MFAMethod.BACKUP_CODES.value,
                "backup_codes": backup_codes,
                "enabled_at": datetime.now(UTC).isoformat()
            }
            
            user.mfa_enabled = True
            user.mfa_method = MFAMethod.BACKUP_CODES.value
            user.mfa_secret = await self._encrypt_mfa_data(mfa_data)
            user.mfa_backup_codes = await self._encrypt_backup_codes(backup_codes)
            
            db.commit()
            
            # Log MFA setup
            await self._log_mfa_event(
                user, 
                "mfa_enabled", 
                {"method": MFAMethod.BACKUP_CODES.value}, 
                db
            )
            
            return {
                "success": True,
                "method": MFAMethod.BACKUP_CODES.value,
                "backup_codes": backup_codes
            }
            
        except Exception as e:
            logger.error(f"Failed to setup backup codes: {e}")
            return {"success": False, "error": "Failed to setup backup codes"}
    
    async def verify_mfa_code(
        self,
        user: User,
        code: str,
        method: Optional[MFAMethod] = None,
        db: Session
    ) -> Dict[str, Any]:
        """Verify MFA code for user"""
        try:
            if not user.mfa_enabled:
                return {"success": False, "error": "MFA not enabled for user"}
            
            # Decrypt MFA data
            mfa_data = await self._decrypt_mfa_data(user.mfa_secret)
            current_method = MFAMethod(mfa_data.get("method", user.mfa_method))
            
            if method and method != current_method:
                return {"success": False, "error": "Invalid MFA method"}
            
            # Verify based on method
            if current_method == MFAMethod.TOTP:
                return await self._verify_totp_code(user, code, mfa_data, db)
            elif current_method == MFAMethod.SMS:
                return await self._verify_sms_code(user, code, mfa_data, db)
            elif current_method == MFAMethod.EMAIL:
                return await self._verify_email_code(user, code, mfa_data, db)
            elif current_method == MFAMethod.BACKUP_CODES:
                return await self._verify_backup_code(user, code, db)
            else:
                return {"success": False, "error": "Unsupported MFA method"}
                
        except Exception as e:
            logger.error(f"Failed to verify MFA code: {e}")
            return {"success": False, "error": "Failed to verify MFA code"}
    
    async def _verify_totp_code(
        self, 
        user: User, 
        code: str, 
        mfa_data: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """Verify TOTP code"""
        try:
            secret = mfa_data.get("secret")
            if not secret:
                return {"success": False, "error": "TOTP not properly configured"}
            
            totp = pyotp.TOTP(secret)
            
            # Allow for time drift (30 seconds window)
            if totp.verify(code, valid_window=1):
                # Log successful verification
                await self._log_mfa_event(
                    user, 
                    "mfa_verified", 
                    {"method": MFAMethod.TOTP.value}, 
                    db
                )
                
                return {"success": True, "method": MFAMethod.TOTP.value}
            else:
                # Log failed verification
                await self._log_mfa_event(
                    user, 
                    "mfa_verification_failed", 
                    {"method": MFAMethod.TOTP.value, "reason": "invalid_code"}, 
                    db
                )
                
                return {"success": False, "error": "Invalid TOTP code"}
                
        except Exception as e:
            logger.error(f"TOTP verification failed: {e}")
            return {"success": False, "error": "TOTP verification failed"}
    
    async def _verify_sms_code(
        self, 
        user: User, 
        code: str, 
        mfa_data: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """Verify SMS code"""
        try:
            expected_code = mfa_data.get("verification_code")
            code_expires_at = datetime.fromisoformat(mfa_data.get("code_expires_at", ""))
            
            if datetime.now(UTC) > code_expires_at:
                return {"success": False, "error": "SMS code expired"}
            
            if code == expected_code:
                # SMS MFA verified, complete setup
                user.mfa_enabled = True
                user.mfa_method = MFAMethod.SMS.value
                user.mfa_secret = await self._encrypt_mfa_data({
                    "method": MFAMethod.SMS.value,
                    "phone_number": mfa_data["phone_number"],
                    "enabled_at": datetime.now(UTC).isoformat()
                })
                user.mfa_pending_data = None
                user.mfa_backup_codes = await self._encrypt_backup_codes(await self._generate_backup_codes())
                
                db.commit()
                
                # Log successful verification
                await self._log_mfa_event(
                    user, 
                    "mfa_verified", 
                    {"method": MFAMethod.SMS.value}, 
                    db
                )
                
                return {"success": True, "method": MFAMethod.SMS.value}
            else:
                # Log failed verification
                await self._log_mfa_event(
                    user, 
                    "mfa_verification_failed", 
                    {"method": MFAMethod.SMS.value, "reason": "invalid_code"}, 
                    db
                )
                
                return {"success": False, "error": "Invalid SMS code"}
                
        except Exception as e:
            logger.error(f"SMS verification failed: {e}")
            return {"success": False, "error": "SMS verification failed"}
    
    async def _verify_email_code(
        self, 
        user: User, 
        code: str, 
        mfa_data: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """Verify Email code"""
        try:
            expected_code = mfa_data.get("verification_code")
            code_expires_at = datetime.fromisoformat(mfa_data.get("code_expires_at", ""))
            
            if datetime.now(UTC) > code_expires_at:
                return {"success": False, "error": "Email code expired"}
            
            if code == expected_code:
                # Email MFA verified, complete setup
                user.mfa_enabled = True
                user.mfa_method = MFAMethod.EMAIL.value
                user.mfa_secret = await self._encrypt_mfa_data({
                    "method": MFAMethod.EMAIL.value,
                    "email": mfa_data["email"],
                    "enabled_at": datetime.now(UTC).isoformat()
                })
                user.mfa_pending_data = None
                user.mfa_backup_codes = await self._encrypt_backup_codes(await self._generate_backup_codes())
                
                db.commit()
                
                # Log successful verification
                await self._log_mfa_event(
                    user, 
                    "mfa_verified", 
                    {"method": MFAMethod.EMAIL.value}, 
                    db
                )
                
                return {"success": True, "method": MFAMethod.EMAIL.value}
            else:
                # Log failed verification
                await self._log_mfa_event(
                    user, 
                    "mfa_verification_failed", 
                    {"method": MFAMethod.EMAIL.value, "reason": "invalid_code"}, 
                    db
                )
                
                return {"success": False, "error": "Invalid Email code"}
                
        except Exception as e:
            logger.error(f"Email verification failed: {e}")
            return {"success": False, "error": "Email verification failed"}
    
    async def _verify_backup_code(self, user: User, code: str, db: Session) -> Dict[str, Any]:
        """Verify backup recovery code"""
        try:
            if not user.mfa_backup_codes:
                return {"success": False, "error": "No backup codes available"}
            
            backup_codes = await self._decrypt_backup_codes(user.mfa_backup_codes)
            
            # Find and validate backup code
            for backup_code in backup_codes:
                if backup_code["code"] == code and not backup_code["used"]:
                    # Mark code as used
                    backup_code["used"] = True
                    backup_code["used_at"] = datetime.now(UTC).isoformat()
                    
                    user.mfa_backup_codes = await self._encrypt_backup_codes(backup_codes)
                    db.commit()
                    
                    # Log successful verification
                    await self._log_mfa_event(
                        user, 
                        "mfa_verified", 
                        {"method": MFAMethod.BACKUP_CODES.value}, 
                        db
                    )
                    
                    return {"success": True, "method": MFAMethod.BACKUP_CODES.value}
            
            # Log failed verification
            await self._log_mfa_event(
                user, 
                "mfa_verification_failed", 
                {"method": MFAMethod.BACKUP_CODES.value, "reason": "invalid_code"}, 
                db
            )
            
            return {"success": False, "error": "Invalid backup code"}
            
        except Exception as e:
            logger.error(f"Backup code verification failed: {e}")
            return {"success": False, "error": "Backup code verification failed"}
    
    async def generate_mfa_challenge(
        self,
        user: User,
        method: MFAMethod,
        db: Session
    ) -> Dict[str, Any]:
        """Generate MFA challenge for user"""
        try:
            if not user.mfa_enabled:
                return {"success": False, "error": "MFA not enabled for user"}
            
            challenge_id = secrets.token_urlsafe(32)
            expires_at = datetime.now(UTC) + timedelta(minutes=5)
            
            # Create challenge
            challenge = MFAChallenge(
                challenge_id=challenge_id,
                user_id=str(user.id),
                method=method,
                expires_at=expires_at,
                attempts_remaining=3,
                metadata={}
            )
            
            # Store challenge
            self.active_challenges[challenge_id] = challenge
            
            # Send challenge based on method
            if method == MFAMethod.SMS:
                code = self._generate_numeric_code()
                await self._send_sms_code(user.phone_number, code)
                challenge.metadata["code"] = code
            elif method == MFAMethod.EMAIL:
                code = self._generate_alphanumeric_code()
                await self._send_email_code(user.email, code)
                challenge.metadata["code"] = code
            
            return {
                "success": True,
                "challenge_id": challenge_id,
                "method": method.value,
                "expires_at": expires_at.isoformat(),
                "message": f"MFA challenge sent via {method.value.upper()}"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate MFA challenge: {e}")
            return {"success": False, "error": "Failed to generate MFA challenge"}
    
    async def verify_mfa_challenge(
        self,
        challenge_id: str,
        code: str,
        db: Session
    ) -> Dict[str, Any]:
        """Verify MFA challenge"""
        try:
            if challenge_id not in self.active_challenges:
                return {"success": False, "error": "Invalid or expired challenge"}
            
            challenge = self.active_challenges[challenge_id]
            
            if datetime.now(UTC) > challenge.expires_at:
                del self.active_challenges[challenge_id]
                return {"success": False, "error": "Challenge expired"}
            
            if challenge.attempts_remaining <= 0:
                del self.active_challenges[challenge_id]
                return {"success": False, "error": "Maximum attempts exceeded"}
            
            # Get user
            user = db.query(User).filter(User.id == challenge.user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Verify code based on method
            if challenge.method == MFAMethod.SMS or challenge.method == MFAMethod.EMAIL:
                expected_code = challenge.metadata.get("code")
                if code == expected_code:
                    del self.active_challenges[challenge_id]
                    
                    # Log successful verification
                    await self._log_mfa_event(
                        user, 
                        "mfa_challenge_verified", 
                        {"method": challenge.method.value, "challenge_id": challenge_id}, 
                        db
                    )
                    
                    return {"success": True, "user_id": str(user.id)}
                else:
                    challenge.attempts_remaining -= 1
                    return {"success": False, "error": "Invalid code", "attempts_remaining": challenge.attempts_remaining}
            else:
                # For other methods, use standard verification
                result = await self.verify_mfa_code(user, code, challenge.method, db)
                if result["success"]:
                    del self.active_challenges[challenge_id]
                return result
                
        except Exception as e:
            logger.error(f"Failed to verify MFA challenge: {e}")
            return {"success": False, "error": "Failed to verify MFA challenge"}
    
    async def disable_mfa_for_user(self, user: User, db: Session) -> Dict[str, Any]:
        """Disable MFA for user"""
        try:
            user.mfa_enabled = False
            user.mfa_method = None
            user.mfa_secret = None
            user.mfa_backup_codes = None
            user.mfa_pending_data = None
            
            db.commit()
            
            # Log MFA disable
            await self._log_mfa_event(
                user, 
                "mfa_disabled", 
                {}, 
                db
            )
            
            return {"success": True, "message": "MFA disabled successfully"}
            
        except Exception as e:
            logger.error(f"Failed to disable MFA: {e}")
            return {"success": False, "error": "Failed to disable MFA"}
    
    async def regenerate_backup_codes(self, user: User, db: Session) -> Dict[str, Any]:
        """Regenerate backup codes for user"""
        try:
            if not user.mfa_enabled:
                return {"success": False, "error": "MFA not enabled for user"}
            
            backup_codes = await self._generate_backup_codes()
            user.mfa_backup_codes = await self._encrypt_backup_codes(backup_codes)
            
            db.commit()
            
            # Log backup codes regeneration
            await self._log_mfa_event(
                user, 
                "backup_codes_regenerated", 
                {}, 
                db
            )
            
            return {
                "success": True,
                "backup_codes": backup_codes,
                "message": "Backup codes regenerated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to regenerate backup codes: {e}")
            return {"success": False, "error": "Failed to regenerate backup codes"}
    
    def _generate_numeric_code(self, length: int = 6) -> str:
        """Generate numeric verification code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    def _generate_alphanumeric_code(self, length: int = 8) -> str:
        """Generate alphanumeric verification code"""
        characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join([secrets.choice(characters) for _ in range(length)])
    
    async def _generate_backup_codes(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate backup recovery codes"""
        codes = []
        for _ in range(count):
            code = secrets.token_urlsafe(8).upper()[:8]
            codes.append({
                "code": code,
                "used": False,
                "used_at": None
            })
        return codes
    
    async def _encrypt_mfa_data(self, data: Dict[str, Any]) -> str:
        """Encrypt MFA data"""
        try:
            from cryptography.fernet import Fernet
            key = settings.MFA_ENCRYPTION_KEY.encode() if hasattr(settings, 'MFA_ENCRYPTION_KEY') else Fernet.generate_key()
            f = Fernet(key)
            encrypted_data = f.encrypt(json.dumps(data).encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt MFA data: {e}")
            raise
    
    async def _decrypt_mfa_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt MFA data"""
        try:
            from cryptography.fernet import Fernet
            key = settings.MFA_ENCRYPTION_KEY.encode() if hasattr(settings, 'MFA_ENCRYPTION_KEY') else Fernet.generate_key()
            f = Fernet(key)
            decrypted_data = f.decrypt(base64.b64decode(encrypted_data))
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Failed to decrypt MFA data: {e}")
            raise
    
    async def _encrypt_backup_codes(self, codes: List[Dict[str, Any]]) -> str:
        """Encrypt backup codes"""
        return await self._encrypt_mfa_data({"codes": codes})
    
    async def _decrypt_backup_codes(self, encrypted_codes: str) -> List[Dict[str, Any]]:
        """Decrypt backup codes"""
        data = await self._decrypt_mfa_data(encrypted_codes)
        return data.get("codes", [])
    
    async def _send_sms_code(self, phone_number: str, code: str) -> None:
        """Send SMS verification code (mock implementation)"""
        # In production, integrate with SMS provider (Twilio, AWS SNS, etc.)
        logger.info(f"SMS code {code} sent to {phone_number}")
    
    async def _send_email_code(self, email: str, code: str) -> None:
        """Send Email verification code (mock implementation)"""
        # In production, integrate with email provider (SendGrid, SES, etc.)
        logger.info(f"Email code {code} sent to {email}")
    
    def _mask_phone_number(self, phone_number: str) -> str:
        """Mask phone number for display"""
        if len(phone_number) > 4:
            return "*" * (len(phone_number) - 4) + phone_number[-4:]
        return "*" * len(phone_number)
    
    def _mask_email(self, email: str) -> str:
        """Mask email for display"""
        if "@" in email:
            local, domain = email.split("@", 1)
            if len(local) > 2:
                return local[:2] + "*" * (len(local) - 2) + "@" + domain
            return "*" * len(local) + "@" + domain
        return "*" * len(email)
    
    async def _log_mfa_event(
        self, 
        user: User, 
        event_type: str, 
        details: Dict[str, Any], 
        db: Session
    ) -> None:
        """Log MFA event to audit trail"""
        try:
            audit_log = AuditLog(
                user_id=str(user.id),
                company_id=str(user.company_id),
                action=AuditAction.MFA_EVENT,
                resource_type=AuditResourceType.USER,
                resource_id=str(user.id),
                details={
                    "event_type": event_type,
                    "mfa_method": user.mfa_method,
                    **details
                },
                ip_address="127.0.0.1",  # Would be actual IP in production
                user_agent="MFA Service"
            )
            
            db.add(audit_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log MFA event: {e}")

# Global instance
mfa_service = MFAService()








