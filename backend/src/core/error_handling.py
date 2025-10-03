"""
Advanced Error Handling and Response Management
Provides comprehensive error handling with proper HTTP status codes and logging
"""
import logging
import traceback
from typing import Any, Dict, Optional, Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import uuid
from datetime import datetime, UTC

from .config import settings

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API error class"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "API_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )

class AuthenticationError(APIError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )

class AuthorizationError(APIError):
    """Authorization error"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )

class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )

class ConflictError(APIError):
    """Resource conflict error"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT"
        )

class RateLimitError(APIError):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )

class DatabaseError(APIError):
    """Database operation error"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR"
        )

class ExternalServiceError(APIError):
    """External service error"""
    def __init__(self, message: str = "External service unavailable"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR"
        )

class ErrorHandler:
    """Centralized error handling and response management"""
    
    @staticmethod
    def create_error_response(
        error: Exception,
        request: Request,
        error_id: Optional[str] = None
    ) -> JSONResponse:
        """Create standardized error response"""
        
        # Generate error ID for tracking
        if not error_id:
            error_id = str(uuid.uuid4())
        
        # Determine error details
        if isinstance(error, APIError):
            status_code = error.status_code
            error_code = error.error_code
            message = error.message
            details = error.details
        elif isinstance(error, HTTPException):
            status_code = error.status_code
            error_code = "HTTP_ERROR"
            message = error.detail
            details = {}
        elif isinstance(error, RequestValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            error_code = "VALIDATION_ERROR"
            message = "Request validation failed"
            details = {"validation_errors": error.errors()}
        elif isinstance(error, SQLAlchemyError):
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            error_code = "DATABASE_ERROR"
            message = "Database operation failed"
            details = {}
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            error_code = "INTERNAL_ERROR"
            message = "An unexpected error occurred"
            details = {}
        
        # Log error details
        ErrorHandler._log_error(error, request, error_id, status_code)
        
        # Create error response
        error_response = {
            "error": {
                "id": error_id,
                "code": error_code,
                "message": message,
                "details": details,
                "timestamp": datetime.now(UTC).isoformat(),
                "path": str(request.url.path),
                "method": request.method
            }
        }
        
        # Add stack trace in development
        if settings.DEBUG and status_code >= 500:
            error_response["error"]["stack_trace"] = traceback.format_exc()
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    @staticmethod
    def _log_error(
        error: Exception,
        request: Request,
        error_id: str,
        status_code: int
    ) -> None:
        """Log error with appropriate level and details"""
        
        # Extract request details
        request_details = {
            "error_id": error_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "status_code": status_code
        }
        
        # Add user info if available
        if hasattr(request.state, "user_id"):
            request_details["user_id"] = request.state.user_id
        if hasattr(request.state, "company_id"):
            request_details["company_id"] = request.state.company_id
        
        # Log based on error severity
        if status_code >= 500:
            logger.error(
                f"Internal server error: {str(error)}",
                extra=request_details,
                exc_info=True
            )
        elif status_code >= 400:
            logger.warning(
                f"Client error: {str(error)}",
                extra=request_details
            )
        else:
            logger.info(
                f"Request error: {str(error)}",
                extra=request_details
            )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions"""
    # Don't handle HTTPExceptions here - they should be handled by specific handlers
    if isinstance(exc, (HTTPException, StarletteHTTPException, RequestValidationError, SQLAlchemyError)):
        raise exc
    return ErrorHandler.create_error_response(exc, request)

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP exception handler"""
    # For HTTPExceptions, just return the error directly without complex processing
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Validation exception handler"""
    return ErrorHandler.create_error_response(exc, request)

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """SQLAlchemy exception handler"""
    return ErrorHandler.create_error_response(exc, request)

def register_error_handlers(app):
    """Register all error handlers with the FastAPI app"""
    # Register specific handlers only
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, sqlalchemy_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    # Note: Global handler removed to prevent interference with HTTPException handling

class ErrorContext:
    """Context manager for error handling with automatic logging"""
    
    def __init__(self, operation: str, request: Optional[Request] = None):
        self.operation = operation
        self.request = request
        self.error_id = str(uuid.uuid4())
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(
                f"Error in {self.operation}",
                extra={
                    "error_id": self.error_id,
                    "operation": self.operation,
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val)
                },
                exc_info=True
            )
        return False

def handle_database_error(func):
    """Decorator for handling database errors"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}", exc_info=True)
            raise DatabaseError(f"Database operation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise APIError(f"Operation failed: {str(e)}")
    return wrapper

def handle_validation_error(func):
    """Decorator for handling validation errors"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            raise ValidationError(f"Validation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise APIError(f"Operation failed: {str(e)}")
    return wrapper
