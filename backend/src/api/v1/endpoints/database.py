"""
Database Management API Endpoints
Provides comprehensive database monitoring, optimization, and management endpoints
"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from core.database import get_db
from core.auth import auth_manager
from core.database_optimization import db_optimizer, index_manager, db_maintenance
from core.database_migrations import get_migration_manager, get_data_migration_manager, get_schema_validator
from core.database_connection import connection_pool, session_manager, db_health_checker
from core.api_design import APIResponse
from src.models.user import User, UserRole

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def get_database_health(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Get comprehensive database health status.
    Requires ADMIN or OWNER role.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view database health"
        )
    
    try:
        health_status = await db_health_checker.check_health()
        
        return APIResponse.success(
            data=health_status,
            message="Database health status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get database health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database health: {str(e)}"
        )

@router.get("/performance", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def get_database_performance(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Get comprehensive database performance analysis.
    Requires ADMIN or OWNER role.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view database performance"
        )
    
    try:
        performance_data = await db_optimizer.analyze_database_performance()
        
        return APIResponse.success(
            data=performance_data,
            message="Database performance analysis completed"
        )
    except Exception as e:
        logger.error(f"Failed to analyze database performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze database performance: {str(e)}"
        )

@router.get("/indexes", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def get_index_status(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Get database index status and usage statistics.
    Requires ADMIN or OWNER role.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view index status"
        )
    
    try:
        # Get performance data which includes index information
        performance_data = await db_optimizer.analyze_database_performance()
        index_data = performance_data.get("index_usage", {})
        
        return APIResponse.success(
            data=index_data,
            message="Index status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get index status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get index status: {str(e)}"
        )

@router.post("/indexes/optimize", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def optimize_database_indexes(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Create performance-optimized database indexes.
    Requires OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to optimize database indexes"
        )
    
    try:
        # Run index optimization in background
        background_tasks.add_task(optimize_indexes_task)
        
        return APIResponse.success(
            data={"message": "Index optimization started in background"},
            message="Database index optimization initiated"
        )
    except Exception as e:
        logger.error(f"Failed to start index optimization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start index optimization: {str(e)}"
        )

async def optimize_indexes_task():
    """Background task for index optimization"""
    try:
        result = await index_manager.create_performance_indexes()
        logger.info(f"Index optimization completed: {result}")
    except Exception as e:
        logger.error(f"Index optimization failed: {e}")

@router.post("/maintenance", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def run_database_maintenance(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Run comprehensive database maintenance tasks.
    Requires OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to run database maintenance"
        )
    
    try:
        # Run maintenance in background
        background_tasks.add_task(maintenance_task)
        
        return APIResponse.success(
            data={"message": "Database maintenance started in background"},
            message="Database maintenance initiated"
        )
    except Exception as e:
        logger.error(f"Failed to start database maintenance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start database maintenance: {str(e)}"
        )

async def maintenance_task():
    """Background task for database maintenance"""
    try:
        result = await db_maintenance.run_maintenance_tasks()
        logger.info(f"Database maintenance completed: {result}")
    except Exception as e:
        logger.error(f"Database maintenance failed: {e}")

@router.get("/migrations", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def get_migration_status(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Get database migration status and history.
    Requires ADMIN or OWNER role.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view migration status"
        )
    
    try:
        migration_status = await get_migration_manager().get_migration_status()
        
        return APIResponse.success(
            data=migration_status,
            message="Migration status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get migration status: {str(e)}"
        )

@router.post("/migrations/run", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def run_migrations(
    target_revision: str = "head",
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Run pending database migrations.
    Requires OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to run migrations"
        )
    
    try:
        migration_result = await get_migration_manager().run_migrations(target_revision)
        
        return APIResponse.success(
            data=migration_result,
            message="Database migrations executed successfully"
        )
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run migrations: {str(e)}"
        )

@router.post("/migrations/rollback", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def rollback_migration(
    target_revision: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Rollback database to a specific revision.
    Requires OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to rollback migrations"
        )
    
    try:
        rollback_result = await get_migration_manager().rollback_migration(target_revision)
        
        return APIResponse.success(
            data=rollback_result,
            message="Database rollback completed successfully"
        )
    except Exception as e:
        logger.error(f"Failed to rollback migration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rollback migration: {str(e)}"
        )

@router.get("/schema/validate", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def validate_database_schema(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Validate database schema integrity.
    Requires ADMIN or OWNER role.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to validate database schema"
        )
    
    try:
        validation_result = await get_schema_validator().validate_schema_integrity()
        
        return APIResponse.success(
            data=validation_result,
            message="Database schema validation completed"
        )
    except Exception as e:
        logger.error(f"Failed to validate database schema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate database schema: {str(e)}"
        )

@router.get("/connection-pool", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def get_connection_pool_status(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Get connection pool status and statistics.
    Requires ADMIN or OWNER role.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view connection pool status"
        )
    
    try:
        pool_stats = connection_pool.get_stats()
        
        return APIResponse.success(
            data=pool_stats,
            message="Connection pool status retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get connection pool status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connection pool status: {str(e)}"
        )

@router.post("/data-migration/register", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def register_data_migration(
    migration_name: str,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Register a new data migration.
    Requires OWNER role.
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to register data migrations"
        )
    
    try:
        # This would typically be done through a more sophisticated interface
        # For now, we'll just return a success message
        return APIResponse.success(
            data={"migration_name": migration_name, "status": "registered"},
            message="Data migration registration endpoint (implementation needed)"
        )
    except Exception as e:
        logger.error(f"Failed to register data migration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register data migration: {str(e)}"
        )

@router.get("/statistics", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def get_database_statistics(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """
    Get comprehensive database statistics.
    Requires ADMIN or OWNER role.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view database statistics"
        )
    
    try:
        # Get performance data which includes statistics
        performance_data = await db_optimizer.analyze_database_performance()
        stats_data = performance_data.get("database_stats", {})
        
        return APIResponse.success(
            data=stats_data,
            message="Database statistics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get database statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database statistics: {str(e)}"
        )
