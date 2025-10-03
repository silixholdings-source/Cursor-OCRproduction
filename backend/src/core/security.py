"""
Advanced Security Module for AI ERP SaaS
Implements enterprise-grade security features
"""
import secrets
import hashlib
import hmac
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from src.models.user import User
from src.models.audit import AuditLog, AuditAction, AuditResourceType
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Advanced security management"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.rate_limit_window = 60  # 1 minute
        self.max_attempts = 5
        
    def generate_csrf_token(self, user_id: str) -> str:
        """Generate CSRF token for user session"""
        timestamp = str(int(time.time()))
        data = f"{user_id}:{timestamp}"
        token = hmac.new(
            settings.JWT_SECRET.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Store token in Redis with expiration
        self.redis_client.setex(
            f"csrf:{user_id}:{token}",
            3600,  # 1 hour
            timestamp
        )
        return token
    
    def validate_csrf_token(self, user_id: str, token: str) -> bool:
        """Validate CSRF token"""
        try:
            stored_timestamp = self.redis_client.get(f"csrf:{user_id}:{token}")
            if not stored_timestamp:
                return False
            
            # Check if token is not too old (1 hour)
            current_time = int(time.time())
            token_time = int(stored_timestamp.decode())
            if current_time - token_time > 3600:
                self.redis_client.delete(f"csrf:{user_id}:{token}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"CSRF validation error: {e}")
            return False
    
    def check_rate_limit(self, identifier: str, endpoint: str) -> bool:
        """Check if request exceeds rate limit"""
        key = f"rate_limit:{identifier}:{endpoint}"
        current = self.redis_client.incr(key)
        
        if current == 1:
            self.redis_client.expire(key, self.rate_limit_window)
        
        return current <= self.max_attempts
    
    def log_security_event(self, event_type: str, user_id: Optional[str], 
                          ip_address: str, details: Dict[str, Any]):
        """Log security events for monitoring"""
        try:
            with get_db() as db:
                audit_log = AuditLog(
                    user_id=user_id,
                    company_id=None,  # Will be set by middleware
                    action=AuditAction.LOGIN,  # Use appropriate action
                    resource_type=AuditResourceType.USER,
                    resource_id=user_id or "system",
                    details={
                        "event_type": event_type,
                        "ip_address": ip_address,
                        "user_agent": details.get("user_agent"),
                        "timestamp": datetime.now(UTC).isoformat(),
                        **details
                    },
                    ip_address=ip_address,
                    user_agent=details.get("user_agent", "Unknown")
                )
                db.add(audit_log)
                db.commit()
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    def detect_anomalous_activity(self, user_id: str, ip_address: str, 
                                 user_agent: str) -> bool:
        """Detect potentially malicious activity"""
        try:
            # Check for rapid requests from same IP
            ip_key = f"rapid_requests:{ip_address}"
            ip_count = self.redis_client.incr(ip_key)
            if ip_count == 1:
                self.redis_client.expire(ip_key, 60)  # 1 minute window
            
            if ip_count > 20:  # More than 20 requests per minute
                self.log_security_event(
                    "rapid_requests",
                    user_id,
                    ip_address,
                    {"user_agent": user_agent, "request_count": ip_count}
                )
                return True
            
            # Check for unusual user agent patterns
            if len(user_agent) < 10 or "bot" in user_agent.lower():
                self.log_security_event(
                    "suspicious_user_agent",
                    user_id,
                    ip_address,
                    {"user_agent": user_agent}
                )
                return True
            
            return False
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return False
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """Generate secure filename to prevent path traversal"""
        # Remove any path components
        filename = original_filename.split('/')[-1].split('\\')[-1]
        
        # Generate secure random name
        secure_name = secrets.token_urlsafe(16)
        extension = filename.split('.')[-1] if '.' in filename else ''
        
        return f"{secure_name}.{extension}" if extension else secure_name
    
    def validate_file_upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Validate uploaded file for security"""
        result = {
            "valid": True,
            "reason": None,
            "file_type": None,
            "size": len(file_content)
        }
        
        # Check file size
        max_size = 10 * 1024 * 1024  # 10MB
        if result["size"] > max_size:
            result["valid"] = False
            result["reason"] = "File too large"
            return result
        
        # Check file type by content (magic bytes)
        file_signatures = {
            b'\x25\x50\x44\x46': 'pdf',
            b'\xFF\xD8\xFF': 'jpg',
            b'\x89\x50\x4E\x47': 'png',
            b'\x49\x49\x2A\x00': 'tiff',
            b'\x4D\x4D\x2A\x00': 'tiff'
        }
        
        file_type = None
        for signature, file_type in file_signatures.items():
            if file_content.startswith(signature):
                result["file_type"] = file_type
                break
        
        if not result["file_type"]:
            result["valid"] = False
            result["reason"] = "Unsupported file type"
            return result
        
        # Check for malicious content patterns
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'data:text/html',
            b'<?php',
            b'<iframe'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in file_content.lower():
                result["valid"] = False
                result["reason"] = "Potentially malicious content detected"
                return result
        
        return result

# Global security manager instance
security_manager = SecurityManager()

class SecurityHeaders:
    """Security headers middleware"""
    
    @staticmethod
    def add_security_headers(response):
        """Add comprehensive security headers"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # HSTS for HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class IPWhitelist:
    """IP whitelist management"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.whitelist_key = "ip_whitelist"
    
    def add_ip(self, ip_address: str, description: str = ""):
        """Add IP to whitelist"""
        self.redis_client.hset(
            self.whitelist_key,
            ip_address,
            f"{description}:{int(time.time())}"
        )
    
    def remove_ip(self, ip_address: str):
        """Remove IP from whitelist"""
        self.redis_client.hdel(self.whitelist_key, ip_address)
    
    def is_whitelisted(self, ip_address: str) -> bool:
        """Check if IP is whitelisted"""
        return self.redis_client.hexists(self.whitelist_key, ip_address)
    
    def get_whitelist(self) -> Dict[str, str]:
        """Get all whitelisted IPs"""
        return self.redis_client.hgetall(self.whitelist_key)

# Global instances
ip_whitelist = IPWhitelist()
