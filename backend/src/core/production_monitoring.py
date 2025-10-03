"""
Production Monitoring and Logging Configuration
"""
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json
import traceback
from contextlib import asynccontextmanager

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response as StarletteResponse

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
DATABASE_CONNECTIONS = Gauge('database_connections', 'Number of database connections')
OCR_PROCESSING_TIME = Histogram('ocr_processing_seconds', 'OCR processing time')
INVOICE_PROCESSING_TIME = Histogram('invoice_processing_seconds', 'Invoice processing time')

class ProductionLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for production logging and metrics"""
    
    def __init__(self, app, logger_name: str = "api"):
        super().__init__(app)
        self.logger = structlog.get_logger(logger_name)
    
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now(UTC)
        
        # Extract request info
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request
        self.logger.info(
            "Request started",
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent,
            request_id=request.headers.get("x-request-id", "unknown")
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = (datetime.now(UTC) - start_time).total_seconds()
            
            # Update metrics
            REQUEST_COUNT.labels(method=method, endpoint=path, status=response.status_code).inc()
            REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)
            
            # Log response
            self.logger.info(
                "Request completed",
                method=method,
                path=path,
                status_code=response.status_code,
                duration=duration,
                request_id=request.headers.get("x-request-id", "unknown")
            )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = (datetime.now(UTC) - start_time).total_seconds()
            
            # Update metrics
            REQUEST_COUNT.labels(method=method, endpoint=path, status=500).inc()
            REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)
            
            # Log error
            self.logger.error(
                "Request failed",
                method=method,
                path=path,
                error=str(e),
                duration=duration,
                traceback=traceback.format_exc(),
                request_id=request.headers.get("x-request-id", "unknown")
            )
            
            raise

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for Prometheus metrics endpoint"""
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return StarletteResponse(
                generate_latest(),
                media_type=CONTENT_TYPE_LATEST
            )
        return await call_next(request)

class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware for health check endpoints"""
    
    def __init__(self, app, health_checker=None):
        super().__init__(app)
        self.health_checker = health_checker
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await self.health_check(request)
        elif request.url.path == "/ready":
            return await self.readiness_check(request)
        return await call_next(request)
    
    async def health_check(self, request: Request):
        """Basic health check"""
        return StarletteResponse(
            json.dumps({
                "status": "healthy",
                "timestamp": datetime.now(UTC).isoformat(),
                "version": "1.0.0"
            }),
            media_type="application/json"
        )
    
    async def readiness_check(self, request: Request):
        """Readiness check with dependencies"""
        if not self.health_checker:
            return StarletteResponse(
                json.dumps({"status": "not_ready", "reason": "Health checker not available"}),
                status_code=503,
                media_type="application/json"
            )
        
        try:
            health_status = await self.health_checker.run_all_checks()
            return StarletteResponse(
                json.dumps(health_status),
                media_type="application/json"
            )
        except Exception as e:
            return StarletteResponse(
                json.dumps({
                    "status": "not_ready",
                    "reason": str(e),
                    "timestamp": datetime.now(UTC).isoformat()
                }),
                status_code=503,
                media_type="application/json"
            )

def setup_production_logging():
    """Setup production logging configuration"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    @staticmethod
    def time_operation(operation_name: str):
        """Decorator to time operations"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = datetime.now(UTC)
                try:
                    result = await func(*args, **kwargs)
                    duration = (datetime.now(UTC) - start_time).total_seconds()
                    
                    # Log performance
                    logger = structlog.get_logger("performance")
                    logger.info(
                        "Operation completed",
                        operation=operation_name,
                        duration=duration,
                        status="success"
                    )
                    
                    return result
                except Exception as e:
                    duration = (datetime.now(UTC) - start_time).total_seconds()
                    
                    # Log error
                    logger = structlog.get_logger("performance")
                    logger.error(
                        "Operation failed",
                        operation=operation_name,
                        duration=duration,
                        error=str(e),
                        status="error"
                    )
                    raise
            return wrapper
        return decorator
    
    @staticmethod
    def update_ocr_metrics(duration: float, success: bool = True):
        """Update OCR processing metrics"""
        OCR_PROCESSING_TIME.observe(duration)
        if not success:
            # Could add error counter here
            pass
    
    @staticmethod
    def update_invoice_metrics(duration: float, success: bool = True):
        """Update invoice processing metrics"""
        INVOICE_PROCESSING_TIME.observe(duration)
        if not success:
            # Could add error counter here
            pass

class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def log_error(error: Exception, context: Dict[str, Any] = None):
        """Log error with context"""
        logger = structlog.get_logger("error")
        logger.error(
            "Error occurred",
            error=str(error),
            error_type=type(error).__name__,
            traceback=traceback.format_exc(),
            context=context or {}
        )
    
    @staticmethod
    def format_error_response(error: Exception, request_id: str = None) -> Dict[str, Any]:
        """Format error response for API"""
        return {
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": request_id,
            "timestamp": datetime.now(UTC).isoformat()
        }

# Health checker for dependencies
class HealthChecker:
    """Health checker for external dependencies"""
    
    def __init__(self, redis_client=None, db_session=None):
        self.redis_client = redis_client
        self.db_session = db_session
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            if self.db_session:
                result = self.db_session.execute("SELECT 1")
                return {"status": "healthy", "response_time_ms": 0}
            return {"status": "not_configured"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            if self.redis_client:
                await self.redis_client.ping()
                return {"status": "healthy", "response_time_ms": 0}
            return {"status": "not_configured"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_ocr_service(self) -> Dict[str, Any]:
        """Check OCR service health"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://ocr-service:8001/health")
                if response.status_code == 200:
                    return {"status": "healthy", "response_time_ms": 0}
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        checks = {
            "database": await self.check_database(),
            "redis": await self.check_redis(),
            "ocr_service": await self.check_ocr_service()
        }
        
        overall_status = "healthy"
        for check_name, result in checks.items():
            if result.get("status") != "healthy":
                overall_status = "unhealthy"
                break
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": checks
        }









