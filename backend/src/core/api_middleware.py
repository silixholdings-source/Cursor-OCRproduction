"""
Advanced API Middleware for Request/Response Processing
Provides comprehensive middleware for logging, validation, and response enhancement
"""
import logging
import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json

from .config import settings
from .monitoring import api_monitor

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging"""
    
    def __init__(self, app: ASGIApp, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            # Start timing
            start_time = time.time()
            
            # Log request
            if self.log_requests:
                await self._log_request(request, request_id)
            
            # Process request
            try:
                response = await call_next(request)
                
                # Calculate processing time
                process_time = time.time() - start_time
                
                # Add headers
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time"] = str(process_time)
                
                # Log response
                if self.log_responses:
                    await self._log_response(request, response, process_time, request_id)
                
                # Record metrics
                api_monitor.track_request(
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    response_time_ms=process_time * 1000
                )
                
                return response
                
            except Exception as e:
                process_time = time.time() - start_time
                # Don't log HTTPExceptions as errors - they're normal client errors
                if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                    logger.warning(
                        f"Client error: {str(e)}",
                        extra={
                            "request_id": request_id,
                            "method": request.method,
                            "path": request.url.path,
                            "process_time": process_time,
                            "status_code": e.status_code
                        }
                    )
                else:
                    logger.error(
                        f"Request processing failed: {str(e)}",
                        extra={
                            "request_id": request_id,
                            "method": request.method,
                            "path": request.url.path,
                            "process_time": process_time
                        },
                        exc_info=True
                    )
                # For non-HTTP exceptions, return a 500 error response instead of re-raising
                if not hasattr(e, 'status_code'):
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": {
                                "code": "INTERNAL_ERROR",
                                "message": "Internal server error",
                                "request_id": request_id
                            }
                        },
                        headers={
                            "X-Request-ID": request_id,
                            "X-Process-Time": str(process_time)
                        }
                    )
                raise
                
        except Exception as e:
            # Handle exceptions that occur during middleware setup (like time.time() failing)
            logger.error(
                f"Middleware error: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path
                },
                exc_info=True
            )
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "Internal server error",
                        "request_id": request_id
                    }
                },
                headers={
                    "X-Request-ID": request_id
                }
            )
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details"""
        # Extract request details
        request_details = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "content_type": request.headers.get("content-type", "unknown"),
            "content_length": request.headers.get("content-length", "0")
        }
        
        # Add user info if available
        if hasattr(request.state, "user_id"):
            request_details["user_id"] = request.state.user_id
        if hasattr(request.state, "company_id"):
            request_details["company_id"] = request.state.company_id
        
        # Log request body for non-streaming requests (be careful with sensitive data)
        if request.method in ["POST", "PUT", "PATCH"] and not self._is_file_upload(request):
            try:
                body = await request.body()
                if body and len(body) < 10000:  # Only log small bodies
                    request_details["body"] = body.decode("utf-8")
            except Exception:
                request_details["body"] = "<unable to decode>"
        
        logger.info(f"Incoming request: {request.method} {request.url.path}", extra=request_details)
    
    async def _log_response(self, request: Request, response: Response, process_time: float, request_id: str):
        """Log outgoing response details"""
        response_details = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": process_time,
            "content_type": response.headers.get("content-type", "unknown"),
            "content_length": response.headers.get("content-length", "0")
        }
        
        # Add user info if available
        if hasattr(request.state, "user_id"):
            response_details["user_id"] = request.state.user_id
        if hasattr(request.state, "company_id"):
            response_details["company_id"] = request.state.company_id
        
        # Log response body for small responses (be careful with sensitive data)
        if not isinstance(response, StreamingResponse) and response.status_code < 500:
            try:
                if hasattr(response, "body") and len(response.body) < 10000:
                    response_details["body"] = response.body.decode("utf-8")
            except Exception:
                pass
        
        log_level = logging.INFO if response.status_code < 400 else logging.WARNING
        logger.log(log_level, f"Outgoing response: {response.status_code} for {request.method} {request.url.path}", extra=response_details)
    
    def _is_file_upload(self, request: Request) -> bool:
        """Check if request contains file upload"""
        content_type = request.headers.get("content-type", "")
        return "multipart/form-data" in content_type

class ResponseEnhancementMiddleware(BaseHTTPMiddleware):
    """Middleware for enhancing API responses with additional metadata"""
    
    def __init__(self, app: ASGIApp, add_metadata: bool = True):
        super().__init__(app)
        self.add_metadata = add_metadata
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        if self.add_metadata:
            # Add API version
            response.headers["X-API-Version"] = settings.APP_VERSION
            
            # Add server info
            response.headers["X-Server"] = "AI-ERP-SaaS"
            
            # Add CORS headers for API responses
            if request.method == "OPTIONS":
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID"
                response.headers["Access-Control-Max-Age"] = "86400"
        
        return response

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for advanced request validation"""
    
    def __init__(self, app: ASGIApp, validate_content_length: bool = True, max_content_length: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.validate_content_length = validate_content_length
        self.max_content_length = max_content_length
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Validate content length
        if self.validate_content_length:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_content_length:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=413,
                    detail=f"Request entity too large. Maximum size: {self.max_content_length} bytes"
                )
        
        # Validate content type for certain endpoints
        # Skip validation for endpoints that don't exist (let routing handle 404/405)
        if request.method in ["POST", "PUT", "PATCH"]:
            # Only validate content type for API endpoints
            if request.url.path.startswith("/api/"):
                content_type = request.headers.get("content-type", "")
                if not content_type or not self._is_valid_content_type(content_type):
                    from fastapi import HTTPException
                    raise HTTPException(
                        status_code=415,
                        detail="Unsupported media type. Expected: application/json or multipart/form-data"
                    )
        
        return await call_next(request)
    
    def _is_valid_content_type(self, content_type: str) -> bool:
        """Check if content type is valid for API requests"""
        valid_types = [
            "application/json",
            "multipart/form-data",
            "application/x-www-form-urlencoded",
            "text/plain"
        ]
        return any(valid_type in content_type for valid_type in valid_types)

class APIVersioningMiddleware(BaseHTTPMiddleware):
    """Middleware for API versioning and backward compatibility"""
    
    def __init__(self, app: ASGIApp, default_version: str = "v1"):
        super().__init__(app)
        self.default_version = default_version
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract API version from path
        path_parts = request.url.path.split("/")
        if len(path_parts) >= 3 and path_parts[1] == "api":
            api_version = path_parts[2]
            request.state.api_version = api_version
        else:
            request.state.api_version = self.default_version
        
        # Add version header to response
        response = await call_next(request)
        response.headers["X-API-Version"] = request.state.api_version
        
        return response

class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware for adding request context and correlation IDs"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate correlation ID if not present
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        # Add request timestamp
        request.state.request_timestamp = time.time()
        
        # Add response headers
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response

def create_api_middleware_stack(app: ASGIApp) -> ASGIApp:
    """Create a complete middleware stack for the API"""
    
    # Add middleware in reverse order (last added is first executed)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(APIVersioningMiddleware)
    app.add_middleware(RequestValidationMiddleware)
    app.add_middleware(ResponseEnhancementMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    return app
