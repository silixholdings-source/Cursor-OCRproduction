"""
Advanced Database Connection Management
Provides comprehensive connection pooling, session management, and performance monitoring
"""
import logging
import time
import asyncio
from typing import Dict, Any, Optional, List, Callable
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta, UTC
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool, NullPool
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
import threading
import psutil
from dataclasses import dataclass
from enum import Enum

from .config import settings

logger = logging.getLogger(__name__)

class ConnectionPoolType(Enum):
    """Connection pool types"""
    QUEUE = "queue"
    STATIC = "static"
    NULL = "null"

@dataclass
class ConnectionStats:
    """Connection pool statistics"""
    pool_size: int
    checked_in: int
    checked_out: int
    overflow: int
    invalid: int
    created_at: datetime
    last_checked: datetime

class AdvancedConnectionPool:
    """Advanced connection pool with monitoring and optimization"""
    
    def __init__(self, database_url: str, pool_type: ConnectionPoolType = ConnectionPoolType.QUEUE):
        self.database_url = database_url
        self.pool_type = pool_type
        self.engine = None
        self.session_factory = None
        self.stats = ConnectionStats(0, 0, 0, 0, 0, datetime.now(UTC), datetime.now(UTC))
        self._lock = threading.Lock()
        self._monitoring_active = False
        self._monitoring_thread = None
        
        # Performance metrics
        self.query_times = []
        self.connection_errors = []
        self.max_query_time = 0
        self.avg_query_time = 0
        
        self._initialize_engine()
        self._setup_event_listeners()
        self._start_monitoring()
    
    def _initialize_engine(self):
        """Initialize the database engine with optimized settings"""
        try:
            # Configure pool based on type
            pool_config = self._get_pool_config()
            
            # Create engine with advanced configuration
            self.engine = create_engine(
                self.database_url,
                **pool_config,
                pool_pre_ping=True,
                echo=settings.DEBUG,
                echo_pool=settings.DEBUG,
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "ai-erp-saas",
                    "options": "-c default_transaction_isolation=read committed"
                }
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            logger.info(f"Database engine initialized with {self.pool_type.value} pool")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def _get_pool_config(self) -> Dict[str, Any]:
        """Get pool configuration based on type"""
        base_config = {
            "pool_recycle": 3600,
        }
        
        if self.pool_type == ConnectionPoolType.QUEUE:
            base_config.update({
                "poolclass": QueuePool,
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            })
        elif self.pool_type == ConnectionPoolType.STATIC:
            base_config.update({
                "poolclass": StaticPool,
                "pool_size": settings.DATABASE_POOL_SIZE,
            })
        elif self.pool_type == ConnectionPoolType.NULL:
            base_config.update({
                "poolclass": NullPool,
            })
        
        return base_config
    
    def _setup_event_listeners(self):
        """Setup event listeners for monitoring and optimization"""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set database-specific connection parameters"""
            if "postgresql" in self.database_url:
                # PostgreSQL specific settings
                with dbapi_connection.cursor() as cursor:
                    cursor.execute("SET timezone TO 'UTC'")
                    cursor.execute("SET statement_timeout TO '30s'")
                    cursor.execute("SET lock_timeout TO '10s'")
            elif "sqlite" in self.database_url:
                # SQLite specific settings
                with dbapi_connection.cursor() as cursor:
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Monitor connection checkout"""
            with self._lock:
                self.stats.checked_out += 1
                self.stats.last_checked = datetime.now(UTC)
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Monitor connection checkin"""
            with self._lock:
                self.stats.checked_in += 1
                self.stats.last_checked = datetime.now(UTC)
    
    def _start_monitoring(self):
        """Start background monitoring of connection pool"""
        if not self._monitoring_active:
            self._monitoring_active = True
            self._monitoring_thread = threading.Thread(target=self._monitor_pool, daemon=True)
            self._monitoring_thread.start()
            logger.info("Connection pool monitoring started")
    
    def _monitor_pool(self):
        """Background monitoring of connection pool health"""
        while self._monitoring_active:
            try:
                self._update_stats()
                self._check_pool_health()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in pool monitoring: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _update_stats(self):
        """Update connection pool statistics"""
        try:
            if self.engine and hasattr(self.engine, 'pool'):
                pool = self.engine.pool
                with self._lock:
                    self.stats.pool_size = pool.size()
                    self.stats.checked_in = pool.checkedin()
                    self.stats.checked_out = pool.checkedout()
                    self.stats.overflow = pool.overflow()
                    # QueuePool doesn't have invalid() method, set to 0
                    self.stats.invalid = 0
                    self.stats.last_checked = datetime.now(UTC)
        except Exception as e:
            logger.error(f"Failed to update pool stats: {e}")
    
    def _check_pool_health(self):
        """Check connection pool health and log warnings"""
        try:
            with self._lock:
                # Check for high connection usage
                usage_percentage = (self.stats.checked_out / self.stats.pool_size) * 100 if self.stats.pool_size > 0 else 0
                
                if usage_percentage > 80:
                    logger.warning(f"High connection pool usage: {usage_percentage:.1f}%")
                
                # Check for invalid connections
                if self.stats.invalid > 0:
                    logger.warning(f"Invalid connections detected: {self.stats.invalid}")
                
                # Check for overflow
                if self.stats.overflow > 0:
                    logger.warning(f"Connection pool overflow: {self.stats.overflow}")
                
        except Exception as e:
            logger.error(f"Failed to check pool health: {e}")
    
    def get_session(self) -> Session:
        """Get a database session"""
        if not self.session_factory:
            raise RuntimeError("Database engine not initialized")
        
        return self.session_factory()
    
    @contextmanager
    def get_session_context(self):
        """Get a database session with automatic cleanup"""
        session = self.get_session()
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session_context(self):
        """Get an async database session context"""
        # This would be implemented with async SQLAlchemy
        # For now, we'll use the synchronous version
        session = self.get_session()
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection pool statistics"""
        with self._lock:
            return {
                "pool_type": self.pool_type.value,
                "pool_size": self.stats.pool_size,
                "checked_in": self.stats.checked_in,
                "checked_out": self.stats.checked_out,
                "overflow": self.stats.overflow,
                "invalid": self.stats.invalid,
                "created_at": self.stats.created_at.isoformat(),
                "last_checked": self.stats.last_checked.isoformat(),
                "usage_percentage": (self.stats.checked_out / self.stats.pool_size * 100) if self.stats.pool_size > 0 else 0,
                "query_metrics": {
                    "max_query_time": self.max_query_time,
                    "avg_query_time": self.avg_query_time,
                    "total_queries": len(self.query_times)
                },
                "connection_errors": len(self.connection_errors)
            }
    
    def record_query_time(self, query_time: float):
        """Record query execution time for performance monitoring"""
        self.query_times.append(query_time)
        
        # Keep only last 1000 query times
        if len(self.query_times) > 1000:
            self.query_times = self.query_times[-1000:]
        
        # Update statistics
        self.max_query_time = max(self.max_query_time, query_time)
        self.avg_query_time = sum(self.query_times) / len(self.query_times)
    
    def record_connection_error(self, error: Exception):
        """Record connection error for monitoring"""
        self.connection_errors.append({
            "error": str(error),
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        # Keep only last 100 errors
        if len(self.connection_errors) > 100:
            self.connection_errors = self.connection_errors[-100:]
    
    def close(self):
        """Close the connection pool and cleanup resources"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection pool closed")

class DatabaseSessionManager:
    """Advanced session management with retry logic and error handling"""
    
    def __init__(self, connection_pool: AdvancedConnectionPool):
        self.connection_pool = connection_pool
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    @contextmanager
    def get_session(self, retry_on_disconnect: bool = True):
        """Get a database session with retry logic"""
        session = None
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                session = self.connection_pool.get_session()
                yield session
                return
                
            except (DisconnectionError, SQLAlchemyError) as e:
                last_error = e
                self.connection_pool.record_connection_error(e)
                
                if session:
                    session.close()
                
                if not retry_on_disconnect or attempt == self.max_retries - 1:
                    break
                
                logger.warning(f"Database connection error (attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
        
        # If we get here, all retries failed
        if last_error:
            raise last_error
        else:
            raise RuntimeError("Failed to get database session")
    
    async def execute_with_retry(self, operation: Callable, *args, **kwargs):
        """Execute a database operation with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                with self.get_session() as session:
                    return operation(session, *args, **kwargs)
                    
            except (DisconnectionError, SQLAlchemyError) as e:
                last_error = e
                self.connection_pool.record_connection_error(e)
                
                if attempt == self.max_retries - 1:
                    break
                
                logger.warning(f"Database operation failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        if last_error:
            raise last_error
        else:
            raise RuntimeError("Failed to execute database operation")

class DatabaseHealthChecker:
    """Advanced database health checking with performance metrics"""
    
    def __init__(self, connection_pool: AdvancedConnectionPool):
        self.connection_pool = connection_pool
    
    async def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive database health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": {}
        }
        
        # Check connection pool health
        pool_health = await self._check_connection_pool()
        health_status["checks"]["connection_pool"] = pool_health
        
        # Check database connectivity
        connectivity_health = await self._check_connectivity()
        health_status["checks"]["connectivity"] = connectivity_health
        
        # Check query performance
        performance_health = await self._check_query_performance()
        health_status["checks"]["performance"] = performance_health
        
        # Check database locks
        locks_health = await self._check_database_locks()
        health_status["checks"]["locks"] = locks_health
        
        # Overall status
        all_healthy = all(
            check.get("status") == "healthy" 
            for check in health_status["checks"].values()
        )
        
        if not all_healthy:
            health_status["status"] = "unhealthy"
        
        return health_status
    
    async def _check_connection_pool(self) -> Dict[str, Any]:
        """Check connection pool health"""
        try:
            stats = self.connection_pool.get_stats()
            
            # Check usage percentage
            usage_percentage = stats["usage_percentage"]
            status = "healthy"
            issues = []
            
            if usage_percentage > 90:
                status = "critical"
                issues.append(f"Connection pool usage is {usage_percentage:.1f}%")
            elif usage_percentage > 80:
                status = "warning"
                issues.append(f"Connection pool usage is {usage_percentage:.1f}%")
            
            # Check for invalid connections
            if stats["invalid"] > 0:
                status = "warning" if status == "healthy" else status
                issues.append(f"Invalid connections: {stats['invalid']}")
            
            return {
                "status": status,
                "usage_percentage": usage_percentage,
                "pool_size": stats["pool_size"],
                "checked_out": stats["checked_out"],
                "issues": issues
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            start_time = time.time()
            
            with self.connection_pool.get_session_context() as session:
                result = session.execute(text("SELECT 1")).fetchone()
                
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "message": "Database connection successful"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Database connection failed"
            }
    
    async def _check_query_performance(self) -> Dict[str, Any]:
        """Check query performance"""
        try:
            stats = self.connection_pool.get_stats()
            query_metrics = stats["query_metrics"]
            
            status = "healthy"
            issues = []
            
            # Check average query time
            if query_metrics["avg_query_time"] > 1.0:  # More than 1 second
                status = "warning"
                issues.append(f"Average query time is {query_metrics['avg_query_time']:.3f}s")
            
            # Check max query time
            if query_metrics["max_query_time"] > 5.0:  # More than 5 seconds
                status = "critical" if status == "healthy" else status
                issues.append(f"Max query time is {query_metrics['max_query_time']:.3f}s")
            
            return {
                "status": status,
                "avg_query_time": query_metrics["avg_query_time"],
                "max_query_time": query_metrics["max_query_time"],
                "total_queries": query_metrics["total_queries"],
                "issues": issues
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_database_locks(self) -> Dict[str, Any]:
        """Check for database locks and blocking queries"""
        try:
            with self.connection_pool.get_session_context() as session:
                # Check for blocking queries (PostgreSQL specific)
                if "postgresql" in self.connection_pool.database_url:
                    locks_query = text("""
                        SELECT 
                            blocked_locks.pid AS blocked_pid,
                            blocked_activity.usename AS blocked_user,
                            blocking_locks.pid AS blocking_pid,
                            blocking_activity.usename AS blocking_user,
                            blocked_activity.query AS blocked_statement,
                            blocking_activity.query AS current_statement_in_blocking_process
                        FROM pg_catalog.pg_locks blocked_locks
                        JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
                        JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
                            AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
                            AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                            AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                            AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                            AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                            AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                            AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                            AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                            AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                            AND blocking_locks.pid != blocked_locks.pid
                        JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
                        WHERE NOT blocked_locks.granted
                    """)
                    
                    locks = session.execute(locks_query).fetchall()
                    
                    if locks:
                        return {
                            "status": "warning",
                            "blocking_queries": len(locks),
                            "message": f"Found {len(locks)} blocking queries"
                        }
                    else:
                        return {
                            "status": "healthy",
                            "blocking_queries": 0,
                            "message": "No blocking queries found"
                        }
                else:
                    return {
                        "status": "healthy",
                        "message": "Lock checking not available for this database type"
                    }
                    
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global connection pool instance
connection_pool = AdvancedConnectionPool(
    settings.DATABASE_URL,
    ConnectionPoolType.QUEUE
)

# Global session manager
session_manager = DatabaseSessionManager(connection_pool)

# Global health checker
db_health_checker = DatabaseHealthChecker(connection_pool)
