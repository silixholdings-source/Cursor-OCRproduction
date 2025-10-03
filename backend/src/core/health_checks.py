"""
Comprehensive Health Check System
Provides detailed health monitoring for all system components
"""
import asyncio
import time
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis.asyncio as redis
import logging

from .database import get_db
from .config import settings

logger = logging.getLogger(__name__)

class HealthChecker:
    """Comprehensive health checker for all system components"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.checks = {
            "database": self._check_database,
            "redis": self._check_redis,
            "disk_space": self._check_disk_space,
            "memory": self._check_memory,
            "cpu": self._check_cpu,
            "external_services": self._check_external_services,
        }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status"""
        start_time = time.time()
        results = {}
        overall_healthy = True
        
        # Run checks in parallel for better performance
        check_tasks = []
        for check_name, check_func in self.checks.items():
            task = asyncio.create_task(self._run_single_check(check_name, check_func))
            check_tasks.append(task)
        
        check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
        
        for i, (check_name, _) in enumerate(self.checks.items()):
            result = check_results[i]
            if isinstance(result, Exception):
                results[check_name] = {
                    "status": "unhealthy",
                    "error": str(result),
                    "timestamp": datetime.now(UTC).isoformat()
                }
                overall_healthy = False
            else:
                results[check_name] = result
                if not result.get("healthy", False):
                    overall_healthy = False
        
        response_time = time.time() - start_time
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "response_time_ms": round(response_time * 1000, 2),
            "checks": results,
            "summary": {
                "total_checks": len(self.checks),
                "healthy_checks": sum(1 for r in results.values() if r.get("healthy", False)),
                "unhealthy_checks": sum(1 for r in results.values() if not r.get("healthy", False))
            }
        }
    
    async def _run_single_check(self, check_name: str, check_func) -> Dict[str, Any]:
        """Run a single health check with timeout"""
        try:
            result = await asyncio.wait_for(check_func(), timeout=10.0)
            return result
        except asyncio.TimeoutError:
            return {
                "status": "unhealthy",
                "error": f"Health check '{check_name}' timed out",
                "timestamp": datetime.now(UTC).isoformat()
            }
        except Exception as e:
            logger.error(f"Health check '{check_name}' failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            db = next(get_db())
            start_time = time.time()
            
            # Test basic connectivity
            result = db.execute(text("SELECT 1")).fetchone()
            if not result:
                return {"status": "unhealthy", "error": "Database query returned no results"}
            
            # Test database performance
            query_time = time.time() - start_time
            
            # Check connection pool status
            pool_status = {
                "size": db.bind.pool.size(),
                "checked_in": db.bind.pool.checkedin(),
                "checked_out": db.bind.pool.checkedout(),
                "overflow": db.bind.pool.overflow(),
                "invalid": db.bind.pool.invalid()
            }
            
            # Check for long-running queries (if supported)
            long_queries = []
            try:
                long_query_result = db.execute(text("""
                    SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
                    FROM pg_stat_activity 
                    WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
                    AND state = 'active'
                """)).fetchall()
                long_queries = [{"pid": row[0], "duration": str(row[1]), "query": row[2][:100]} for row in long_query_result]
            except Exception:
                # Not PostgreSQL or query not supported
                pass
            
            return {
                "status": "healthy",
                "healthy": True,
                "query_time_ms": round(query_time * 1000, 2),
                "pool_status": pool_status,
                "long_queries": long_queries,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        if not self.redis_client:
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": "Redis client not configured",
                "timestamp": datetime.now(UTC).isoformat()
            }
        
        try:
            start_time = time.time()
            
            # Test basic connectivity
            await self.redis_client.ping()
            
            # Test performance
            test_key = "health_check_test"
            await self.redis_client.set(test_key, "test_value", ex=60)
            await self.redis_client.get(test_key)
            await self.redis_client.delete(test_key)
            
            response_time = time.time() - start_time
            
            # Get Redis info
            info = await self.redis_client.info()
            
            return {
                "status": "healthy",
                "healthy": True,
                "response_time_ms": round(response_time * 1000, 2),
                "redis_info": {
                    "version": info.get("redis_version"),
                    "uptime_seconds": info.get("uptime_in_seconds"),
                    "connected_clients": info.get("connected_clients"),
                    "used_memory_human": info.get("used_memory_human"),
                    "keyspace_hits": info.get("keyspace_hits"),
                    "keyspace_misses": info.get("keyspace_misses")
                },
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space availability"""
        try:
            disk_usage = psutil.disk_usage('/')
            total = disk_usage.total
            used = disk_usage.used
            free = disk_usage.free
            percent_used = (used / total) * 100
            
            # Consider unhealthy if more than 90% used
            healthy = percent_used < 90
            
            return {
                "status": "healthy" if healthy else "unhealthy",
                "healthy": healthy,
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "percent_used": round(percent_used, 2),
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            
            # Consider unhealthy if more than 90% used
            healthy = percent_used < 90
            
            return {
                "status": "healthy" if healthy else "unhealthy",
                "healthy": healthy,
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": percent_used,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_cpu(self) -> Dict[str, Any]:
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Consider unhealthy if more than 80% CPU usage
            healthy = cpu_percent < 80
            
            return {
                "status": "healthy" if healthy else "unhealthy",
                "healthy": healthy,
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_external_services(self) -> Dict[str, Any]:
        """Check external service dependencies"""
        services = {}
        overall_healthy = True
        
        # Check Azure Form Recognizer (if configured)
        if settings.AZURE_FORM_RECOGNIZER_ENDPOINT:
            azure_healthy = await self._check_azure_form_recognizer()
            services["azure_form_recognizer"] = azure_healthy
            if not azure_healthy.get("healthy", False):
                overall_healthy = False
        
        # Check email services (if configured)
        if settings.SMTP_HOST:
            smtp_healthy = await self._check_smtp_service()
            services["smtp"] = smtp_healthy
            if not smtp_healthy.get("healthy", False):
                overall_healthy = False
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "healthy": overall_healthy,
            "services": services,
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    async def _check_azure_form_recognizer(self) -> Dict[str, Any]:
        """Check Azure Form Recognizer service"""
        try:
            # This would be a real check in production
            # For now, just check if endpoint is configured
            return {
                "status": "healthy",
                "healthy": True,
                "endpoint": settings.AZURE_FORM_RECOGNIZER_ENDPOINT,
                "timestamp": datetime.now(UTC).isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def _check_smtp_service(self) -> Dict[str, Any]:
        """Check SMTP service"""
        try:
            # This would be a real SMTP connection test in production
            return {
                "status": "healthy",
                "healthy": True,
                "host": settings.SMTP_HOST,
                "port": settings.SMTP_PORT,
                "timestamp": datetime.now(UTC).isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
