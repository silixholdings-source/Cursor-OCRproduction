"""
Advanced Security Headers Middleware
Implements comprehensive security headers for production deployment
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Advanced security headers middleware for production security"""
    
    def __init__(self, app, csp_policy: str = None):
        super().__init__(app)
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security Headers
        security_headers = {
            # Prevent XSS attacks
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            
            # Content Security Policy
            "Content-Security-Policy": self.csp_policy,
            
            # Referrer Policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions Policy (formerly Feature Policy)
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "interest-cohort=(), payment=(), usb=()"
            ),
            
            # HSTS (HTTP Strict Transport Security)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Cross-Origin Policies
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            
            # Additional Security
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Download-Options": "noopen",
            "X-DNS-Prefetch-Control": "off",
            
            # Cache Control for sensitive endpoints
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        
        # Add security headers to response
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
