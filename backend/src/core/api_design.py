"""
Enhanced API Design and Documentation System
Implements OpenAPI 3.0 specifications with advanced features
"""
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standard API response format"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Error details")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class PaginatedResponse(APIResponse):
    """Paginated API response format"""
    pagination: Optional[Dict[str, Any]] = Field(None, description="Pagination information")

class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    value: Optional[Any] = Field(None, description="Value that caused the error")

class APIError(Exception):
    """Custom API error class"""
    def __init__(self, message: str, status_code: int = 400, 
                 error_code: str = "API_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class APIResponseHandler:
    """Centralized API response handling"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", 
                meta: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Create success response"""
        return APIResponse(
            success=True,
            message=message,
            data=data,
            meta=meta
        )
    
    @staticmethod
    def error(message: str, status_code: int = 400, 
              error_code: str = "API_ERROR", 
              errors: Optional[List[ErrorDetail]] = None,
              meta: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Create error response"""
        return APIResponse(
            success=False,
            message=message,
            errors=[error.dict() for error in errors] if errors else None,
            meta=meta
        )
    
    @staticmethod
    def paginated(data: List[Any], page: int, per_page: int, total: int,
                  message: str = "Success") -> PaginatedResponse:
        """Create paginated response"""
        total_pages = (total + per_page - 1) // per_page
        
        return PaginatedResponse(
            success=True,
            message=message,
            data=data,
            pagination={
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )

class APIMiddleware:
    """Enhanced API middleware"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_middleware()
    
    def setup_middleware(self):
        """Setup all middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure based on environment
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure based on environment
        )
        
        # Custom middleware for response formatting
        @self.app.middleware("http")
        async def response_middleware(request: Request, call_next):
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Add API version header
            response.headers["X-API-Version"] = "1.0.0"
            
            return response

class OpenAPICustomizer:
    """Customize OpenAPI documentation"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.customize_openapi()
    
    def customize_openapi(self):
        """Customize OpenAPI schema"""
        def custom_openapi():
            if self.app.openapi_schema:
                return self.app.openapi_schema
            
            openapi_schema = get_openapi(
                title="AI ERP SaaS API",
                version="1.0.0",
                description="""
                # AI ERP SaaS API Documentation
                
                This is the comprehensive API documentation for the AI ERP SaaS platform.
                
                ## Features
                - **AI-Powered OCR**: Advanced invoice data extraction
                - **Multi-ERP Integration**: Connect with major ERP systems
                - **Smart Workflows**: Intelligent approval routing
                - **Real-time Analytics**: Comprehensive reporting
                - **Enterprise Security**: SOC 2 compliance ready
                
                ## Authentication
                All API endpoints require authentication using JWT tokens.
                Include the token in the Authorization header:
                ```
                Authorization: Bearer <your-token>
                ```
                
                ## Rate Limiting
                API requests are rate limited to ensure fair usage:
                - **Authentication endpoints**: 5 requests per 5 minutes
                - **File processing**: 10 requests per minute
                - **General API**: 1000 requests per hour
                
                ## Error Handling
                All errors follow a consistent format:
                ```json
                {
                    "success": false,
                    "message": "Error description",
                    "errors": [
                        {
                            "code": "ERROR_CODE",
                            "message": "Detailed error message",
                            "field": "field_name"
                        }
                    ],
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                ```
                
                ## Pagination
                List endpoints support pagination:
                - `page`: Page number (1-based)
                - `per_page`: Items per page (max 100)
                - `sort`: Sort field
                - `order`: Sort order (asc/desc)
                
                ## Webhooks
                The API supports webhooks for real-time notifications:
                - Invoice processing completed
                - Approval workflow updates
                - ERP synchronization events
                
                ## SDKs
                Official SDKs are available for:
                - Python
                - JavaScript/Node.js
                - Java
                - C#
                
                ## Support
                For API support and questions:
                - Email: api-support@ai-erp-saas.com
                - Documentation: https://docs.ai-erp-saas.com
                - Status Page: https://status.ai-erp-saas.com
                """,
                routes=self.app.routes,
            )
            
            # Add custom tags
            openapi_schema["tags"] = [
                {
                    "name": "Authentication",
                    "description": "User authentication and authorization"
                },
                {
                    "name": "Companies",
                    "description": "Company management operations"
                },
                {
                    "name": "Users",
                    "description": "User management operations"
                },
                {
                    "name": "Invoices",
                    "description": "Invoice processing and management"
                },
                {
                    "name": "ERP Integration",
                    "description": "ERP system integration"
                },
                {
                    "name": "File Processing",
                    "description": "File upload and OCR processing"
                },
                {
                    "name": "Analytics",
                    "description": "Analytics and reporting"
                },
                {
                    "name": "Webhooks",
                    "description": "Webhook management"
                },
                {
                    "name": "Health",
                    "description": "System health and monitoring"
                }
            ]
            
            # Add security schemes
            openapi_schema["components"]["securitySchemes"] = {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT token authentication"
                },
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API key authentication for webhooks"
                }
            }
            
            # Add examples
            openapi_schema["components"]["examples"] = {
                "InvoiceExample": {
                    "summary": "Sample Invoice",
                    "value": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "invoice_number": "INV-2024-001",
                        "supplier_name": "Acme Corporation",
                        "total_amount": 1500.00,
                        "currency": "USD",
                        "status": "pending_approval",
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                },
                "ErrorExample": {
                    "summary": "Validation Error",
                    "value": {
                        "success": False,
                        "message": "Validation failed",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "Email format is invalid",
                                "field": "email"
                            }
                        ],
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            }
            
            self.app.openapi_schema = openapi_schema
            return self.app.openapi_schema
        
        self.app.openapi = custom_openapi

class APIValidator:
    """API request validation and sanitization"""
    
    @staticmethod
    def validate_pagination(page: int, per_page: int) -> Dict[str, int]:
        """Validate and sanitize pagination parameters"""
        # Ensure page is at least 1
        page = max(1, page)
        
        # Limit per_page to reasonable range
        per_page = max(1, min(100, per_page))
        
        return {"page": page, "per_page": per_page}
    
    @staticmethod
    def validate_sorting(sort: Optional[str], allowed_fields: List[str]) -> Optional[str]:
        """Validate sorting field"""
        if not sort:
            return None
        
        # Check if sort field is allowed
        if sort.lstrip('-') not in allowed_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field. Allowed fields: {', '.join(allowed_fields)}"
            )
        
        return sort
    
    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """Sanitize search query to prevent injection"""
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
        for char in dangerous_chars:
            query = query.replace(char, '')
        
        # Limit length
        query = query[:100]
        
        return query.strip()

class WebhookManager:
    """Webhook management system"""
    
    def __init__(self):
        self.webhook_endpoints = {}
    
    def register_webhook(self, event_type: str, url: str, secret: str):
        """Register webhook endpoint"""
        self.webhook_endpoints[event_type] = {
            "url": url,
            "secret": secret
        }
    
    async def send_webhook(self, event_type: str, data: Dict[str, Any]):
        """Send webhook notification"""
        if event_type not in self.webhook_endpoints:
            return
        
        webhook = self.webhook_endpoints[event_type]
        
        # In a real implementation, this would make HTTP request
        logger.info(f"Webhook sent to {webhook['url']} for event {event_type}")

class APIVersioning:
    """API versioning management"""
    
    def __init__(self):
        self.supported_versions = ["1.0", "1.1", "2.0"]
        self.default_version = "1.0"
    
    def get_version_from_header(self, request: Request) -> str:
        """Extract API version from request header"""
        version = request.headers.get("API-Version", self.default_version)
        
        if version not in self.supported_versions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported API version. Supported versions: {', '.join(self.supported_versions)}"
            )
        
        return version
    
    def get_version_from_path(self, path: str) -> str:
        """Extract API version from URL path"""
        parts = path.split('/')
        if len(parts) >= 3 and parts[1] == 'api':
            version = parts[2]
            if version in self.supported_versions:
                return version
        
        return self.default_version

# Global instances
api_response_handler = APIResponseHandler()
webhook_manager = WebhookManager()
api_versioning = APIVersioning()

# Convenience functions
def success_response(data: Any = None, message: str = "Success", 
                   meta: Optional[Dict[str, Any]] = None) -> APIResponse:
    """Create success response"""
    return api_response_handler.success(data, message, meta)

def error_response(message: str, status_code: int = 400, 
                  error_code: str = "API_ERROR", 
                  errors: Optional[List[ErrorDetail]] = None,
                  meta: Optional[Dict[str, Any]] = None) -> APIResponse:
    """Create error response"""
    return api_response_handler.error(message, status_code, error_code, errors, meta)

def paginated_response(data: List[Any], page: int, per_page: int, total: int,
                      message: str = "Success") -> PaginatedResponse:
    """Create paginated response"""
    return api_response_handler.paginated(data, page, per_page, total, message)
