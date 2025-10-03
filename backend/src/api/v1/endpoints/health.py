from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db, check_db_connection
from core.config import settings
import redis
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def check_redis_connection():
    """Check Redis connection"""
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    start_time = time.time()
    
    # Check database connection
    db_healthy = check_db_connection()
    
    # Check Redis connection
    redis_healthy = check_redis_connection()
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Determine overall health
    overall_healthy = db_healthy and redis_healthy
    
    health_status = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy"
        },
        "response_time_ms": round(response_time * 1000, 2)
    }
    
    # Return appropriate status code
    if not overall_healthy:
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@router.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    return {"status": "ready"}

@router.get("/health/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return {"status": "alive"}

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with database query"""
    start_time = time.time()
    
    try:
        # Test database query
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        db_healthy = False
    
    # Check Redis
    redis_healthy = check_redis_connection()
    
    response_time = time.time() - start_time
    
    health_status = {
        "status": "healthy" if (db_healthy and redis_healthy) else "unhealthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "response_time_ms": round(response_time * 1000, 2)
            },
            "redis": {
                "status": "healthy" if redis_healthy else "unhealthy"
            }
        },
        "system": {
            "python_version": "3.11",
            "fastapi_version": "0.104.0"
        }
    }
    
    if not (db_healthy and redis_healthy):
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
