"""
System Management Endpoints
Provides system administration and monitoring capabilities
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, UTC
import psutil
import platform
import sys
from pathlib import Path

from core.database import get_db
from core.auth import auth_manager
from core.advanced_rate_limiting import rate_limit
from src.models.user import User, UserRole
from schemas.system import (
    SystemInfoResponse,
    SystemMetricsResponse,
    DatabaseStatsResponse,
    CacheStatsResponse,
    LogLevelRequest,
    SystemConfigResponse
)

router = APIRouter()

@router.get("/system/info", response_model=SystemInfoResponse)
async def get_system_info(
    current_user: User = Depends(auth_manager.get_current_user),
    request: Request = None
):
    """Get system information (admin only)"""
    # Check if user has admin privileges
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view system information"
        )
    
    try:
        # Get system information
        system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": sys.version,
            "app_version": "1.0.0",
            "environment": "production",  # This should come from settings
            "uptime": 0,  # This should be calculated from app start time
            "timestamp": datetime.now(UTC)
        }
        
        return SystemInfoResponse(**system_info)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system information: {str(e)}"
        )

@router.get("/system/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    current_user: User = Depends(auth_manager.get_current_user),
    request: Request = None
):
    """Get system performance metrics (admin only)"""
    # Check if user has admin privileges
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view system metrics"
        )
    
    try:
        # Get CPU and memory metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get network stats
        network = psutil.net_io_counters()
        
        metrics = {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "usage_percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "usage_percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "timestamp": datetime.now(UTC)
        }
        
        return SystemMetricsResponse(**metrics)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system metrics: {str(e)}"
        )

@router.get("/system/database/stats", response_model=DatabaseStatsResponse)
async def get_database_stats(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get database statistics (admin only)"""
    # Check if user has admin privileges
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view database statistics"
        )
    
    try:
        # Get database connection info
        from sqlalchemy import text
        
        # Get table counts
        tables = ['users', 'companies', 'invoices', 'invoice_lines', 'audit_logs']
        table_counts = {}
        
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                table_counts[table] = result.scalar()
            except Exception:
                table_counts[table] = 0
        
        # Get database size (PostgreSQL specific)
        try:
            result = db.execute(text("SELECT pg_database_size(current_database())"))
            db_size = result.scalar()
        except Exception:
            db_size = 0
        
        # Get connection pool info
        pool_info = {
            "size": db.get_bind().pool.size(),
            "checked_in": db.get_bind().pool.checkedin(),
            "checked_out": db.get_bind().pool.checkedout(),
            "overflow": db.get_bind().pool.overflow(),
            "invalid": db.get_bind().pool.invalid()
        }
        
        stats = {
            "table_counts": table_counts,
            "database_size_bytes": db_size,
            "connection_pool": pool_info,
            "timestamp": datetime.now(UTC)
        }
        
        return DatabaseStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve database statistics: {str(e)}"
        )

@router.get("/system/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get cache statistics (admin only)"""
    # Check if user has admin privileges
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view cache statistics"
        )
    
    try:
        # This would integrate with Redis if available
        # For now, return mock data
        cache_stats = {
            "redis_connected": False,  # This should check actual Redis connection
            "memory_usage": 0,
            "key_count": 0,
            "hit_rate": 0.0,
            "miss_rate": 0.0,
            "timestamp": datetime.now(UTC)
        }
        
        return CacheStatsResponse(**cache_stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cache statistics: {str(e)}"
        )

@router.post("/system/logs/level")
async def set_log_level(
    log_request: LogLevelRequest,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Set application log level (admin only)"""
    # Check if user has admin privileges
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to modify log levels"
        )
    
    try:
        import logging
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_request.level.upper() not in valid_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid log level. Must be one of: {valid_levels}"
            )
        
        # Set log level for root logger
        logging.getLogger().setLevel(getattr(logging, log_request.level.upper()))
        
        return {
            "message": f"Log level set to {log_request.level.upper()}",
            "timestamp": datetime.now(UTC)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set log level: {str(e)}"
        )

@router.get("/system/config", response_model=SystemConfigResponse)
async def get_system_config(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Get system configuration (admin only)"""
    # Check if user has admin privileges
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view system configuration"
        )
    
    try:
        from core.config import settings
        
        # Return safe configuration values (no secrets)
        config = {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "api_v1_str": settings.API_V1_STR,
            "project_name": settings.PROJECT_NAME,
            "database_pool_size": settings.DATABASE_POOL_SIZE,
            "database_max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS,
            "cors_origins": settings.cors_origins_list,
            "allowed_hosts": settings.allowed_hosts_list,
            "timestamp": datetime.now(UTC)
        }
        
        return SystemConfigResponse(**config)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system configuration: {str(e)}"
        )

@router.post("/system/maintenance/cleanup")
async def system_cleanup(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Run system cleanup tasks (admin only)"""
    # Check if user has admin privileges
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to run system cleanup"
        )
    
    try:
        from sqlalchemy import text
        from datetime import datetime, timedelta, UTC
        
        cleanup_tasks = []
        
        # Clean up old audit logs (older than 1 year)
        try:
            cutoff_date = datetime.now(UTC) - timedelta(days=365)
            result = db.execute(
                text("DELETE FROM audit_logs WHERE created_at < :cutoff"),
                {"cutoff": cutoff_date}
            )
            cleanup_tasks.append(f"Cleaned up {result.rowcount} old audit logs")
        except Exception as e:
            cleanup_tasks.append(f"Failed to clean audit logs: {str(e)}")
        
        # Clean up expired sessions (if implemented)
        # This would clean up expired JWT tokens or session records
        
        # Clean up temporary files
        try:
            temp_dir = Path("temp")
            if temp_dir.exists():
                temp_files = list(temp_dir.glob("*.tmp"))
                for temp_file in temp_files:
                    if temp_file.stat().st_mtime < (datetime.now().timestamp() - 3600):  # 1 hour old
                        temp_file.unlink()
                cleanup_tasks.append(f"Cleaned up {len(temp_files)} temporary files")
        except Exception as e:
            cleanup_tasks.append(f"Failed to clean temp files: {str(e)}")
        
        db.commit()
        
        return {
            "message": "System cleanup completed",
            "tasks": cleanup_tasks,
            "timestamp": datetime.now(UTC)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run system cleanup: {str(e)}"
        )

