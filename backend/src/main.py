import sys
from pathlib import Path

# Ensure the src directory is on PYTHONPATH when running from repo root or backend dir
current_file_path = Path(__file__).resolve()
src_directory_path = current_file_path.parent
if str(src_directory_path) not in sys.path:
    sys.path.insert(0, str(src_directory_path))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging
from contextlib import asynccontextmanager
import redis.asyncio as redis

from core.config import settings
from core.telemetry import setup_telemetry
from src.core.middleware import MultiTenantMiddleware
from core.security_headers import SecurityHeadersMiddleware
from core.rate_limiting import RateLimitingMiddleware, AdvancedRateLimiter
from core.health_checks import HealthChecker
from core.api_middleware import create_api_middleware_stack
from core.api_documentation import create_openapi_schema, create_enhanced_docs_routes
from core.error_handling import register_error_handlers
from api.v1.api import api_router
from core.database import engine, get_db
from core.database import Base
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for shared resources
redis_client = None
health_checker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, health_checker
    
    # Startup
    logger.info("Starting up AI ERP SaaS application...")
    
    # Initialize Redis client (optional for development)
    redis_client = None
    try:
        if settings.REDIS_URL and "localhost" in settings.REDIS_URL:
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            logger.info("Redis connection established")
        else:
            logger.info("Redis connection skipped (not configured or not localhost)")
    except Exception as e:
        logger.warning(f"Redis connection failed, continuing without Redis: {e}")
        redis_client = None
    
    # Initialize health checker
    health_checker = HealthChecker(redis_client)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    # Setup telemetry
    setup_telemetry()
    logger.info("Telemetry setup complete")
    
    # Store shared resources in app state
    app.state.redis_client = redis_client
    app.state.health_checker = health_checker
    
    # Configure rate limiting if Redis is available
    if redis_client:
        rate_limiter = AdvancedRateLimiter(redis_client)
        # Update the middleware with the rate limiter
        for middleware in app.user_middleware:
            if hasattr(middleware, 'rate_limiter'):
                middleware.rate_limiter = rate_limiter
                break
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI ERP SaaS application...")
    
    # Close Redis connection
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

# Create FastAPI app
app = FastAPI(
    title="AI ERP SaaS API",
    description="AI-powered ERP SaaS application with OCR, 3-way matching, and multi-tenant support",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Set custom OpenAPI schema
app.openapi = lambda: create_openapi_schema(app)

# Add security headers middleware (first for maximum security)
app.add_middleware(SecurityHeadersMiddleware, csp_policy=settings.CSP_POLICY)

# Add multi-tenant middleware
app.add_middleware(MultiTenantMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list
)

# Add GZIP compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add rate limiting middleware (will be configured in lifespan)
app.add_middleware(RateLimitingMiddleware, rate_limiter=None)

# Create enhanced API middleware stack
app = create_api_middleware_stack(app)

# Register error handlers
register_error_handlers(app)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Create enhanced documentation routes
create_enhanced_docs_routes(app)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Comprehensive health check endpoint
@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint with comprehensive system monitoring"""
    if not health_checker:
        return {
            "status": "unhealthy",
            "error": "Health checker not initialized",
            "timestamp": time.time()
        }
    
    return await health_checker.run_all_checks()

# Readiness check endpoint
@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/container orchestration"""
    try:
        # Test database connection (critical)
        db = next(get_db())
        db.execute(text("SELECT 1"))
        
        # Redis is optional for development
        if redis_client:
            try:
                await redis_client.ping()
            except Exception as e:
                logger.warning(f"Redis health check failed: {e}")
        
        return {"status": "ready", "timestamp": time.time()}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e), "timestamp": time.time()}

# Liveness check endpoint
@app.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes/container orchestration"""
    return {"status": "alive", "timestamp": time.time()}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI ERP SaaS API",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
