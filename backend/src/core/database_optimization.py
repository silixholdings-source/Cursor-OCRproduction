"""
Advanced Database Optimization and Management
Provides comprehensive database optimization, indexing, and performance monitoring
"""
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import text, Index, func, desc, asc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
import psutil
import asyncio
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, SessionLocal

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Advanced database optimization and performance monitoring"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.optimization_stats = {}
    
    async def analyze_database_performance(self) -> Dict[str, Any]:
        """Analyze database performance and identify optimization opportunities"""
        try:
            with SessionLocal() as db:
                # Get database statistics
                stats = await self._get_database_stats(db)
                
                # Analyze query performance
                query_stats = await self._analyze_query_performance(db)
                
                # Check index usage
                index_stats = await self._analyze_index_usage(db)
                
                # Analyze table sizes and growth
                table_stats = await self._analyze_table_sizes(db)
                
                # Check for missing indexes
                missing_indexes = await self._find_missing_indexes(db)
                
                # Analyze connection pool usage
                pool_stats = await self._analyze_connection_pool()
                
                return {
                    "database_stats": stats,
                    "query_performance": query_stats,
                    "index_usage": index_stats,
                    "table_sizes": table_stats,
                    "missing_indexes": missing_indexes,
                    "connection_pool": pool_stats,
                    "timestamp": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze database performance: {e}")
            return {"error": str(e)}
    
    async def _get_database_stats(self, db: Session) -> Dict[str, Any]:
        """Get basic database statistics"""
        try:
            # Get database size
            size_query = text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as database_size,
                       pg_database_size(current_database()) as database_size_bytes
            """)
            size_result = db.execute(size_query).fetchone()
            
            # Get connection count
            conn_query = text("""
                SELECT count(*) as active_connections
                FROM pg_stat_activity 
                WHERE state = 'active'
            """)
            conn_result = db.execute(conn_query).fetchone()
            
            # Get table count
            table_query = text("""
                SELECT count(*) as table_count
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_result = db.execute(table_query).fetchone()
            
            return {
                "database_size": size_result[0] if size_result else "Unknown",
                "database_size_bytes": size_result[1] if size_result else 0,
                "active_connections": conn_result[0] if conn_result else 0,
                "table_count": table_result[0] if table_result else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"error": str(e)}
    
    async def _analyze_query_performance(self, db: Session) -> Dict[str, Any]:
        """Analyze query performance from pg_stat_statements"""
        try:
            # Check if pg_stat_statements is available
            check_query = text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                ) as extension_exists
            """)
            extension_exists = db.execute(check_query).fetchone()[0]
            
            if not extension_exists:
                return {"message": "pg_stat_statements extension not available"}
            
            # Get slow queries
            slow_queries = text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements 
                WHERE mean_time > 1000  -- Queries taking more than 1 second on average
                ORDER BY mean_time DESC 
                LIMIT 10
            """)
            
            slow_results = db.execute(slow_queries).fetchall()
            
            # Get most frequent queries
            frequent_queries = text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time
                FROM pg_stat_statements 
                ORDER BY calls DESC 
                LIMIT 10
            """)
            
            frequent_results = db.execute(frequent_queries).fetchall()
            
            return {
                "slow_queries": [
                    {
                        "query": row[0][:200] + "..." if len(row[0]) > 200 else row[0],
                        "calls": row[1],
                        "total_time": row[2],
                        "mean_time": row[3],
                        "rows": row[4],
                        "hit_percent": row[5]
                    }
                    for row in slow_results
                ],
                "frequent_queries": [
                    {
                        "query": row[0][:200] + "..." if len(row[0]) > 200 else row[0],
                        "calls": row[1],
                        "total_time": row[2],
                        "mean_time": row[3]
                    }
                    for row in frequent_results
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze query performance: {e}")
            return {"error": str(e)}
    
    async def _analyze_index_usage(self, db: Session) -> Dict[str, Any]:
        """Analyze index usage and efficiency"""
        try:
            # Get index usage statistics
            index_usage = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC
            """)
            
            usage_results = db.execute(index_usage).fetchall()
            
            # Get unused indexes
            unused_indexes = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname
                FROM pg_stat_user_indexes 
                WHERE idx_scan = 0
                AND schemaname = 'public'
            """)
            
            unused_results = db.execute(unused_indexes).fetchall()
            
            return {
                "index_usage": [
                    {
                        "schema": row[0],
                        "table": row[1],
                        "index": row[2],
                        "scans": row[3],
                        "tuples_read": row[4],
                        "tuples_fetched": row[5]
                    }
                    for row in usage_results
                ],
                "unused_indexes": [
                    {
                        "schema": row[0],
                        "table": row[1],
                        "index": row[2]
                    }
                    for row in unused_results
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze index usage: {e}")
            return {"error": str(e)}
    
    async def _analyze_table_sizes(self, db: Session) -> Dict[str, Any]:
        """Analyze table sizes and growth patterns"""
        try:
            table_sizes = text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            size_results = db.execute(table_sizes).fetchall()
            
            return {
                "table_sizes": [
                    {
                        "schema": row[0],
                        "table": row[1],
                        "total_size": row[2],
                        "total_size_bytes": row[3],
                        "table_size": row[4],
                        "index_size": row[5]
                    }
                    for row in size_results
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze table sizes: {e}")
            return {"error": str(e)}
    
    async def _find_missing_indexes(self, db: Session) -> List[Dict[str, Any]]:
        """Find potentially missing indexes based on query patterns"""
        try:
            # This is a simplified version - in production, you'd use more sophisticated analysis
            missing_indexes = []
            
            # Check for common patterns that might benefit from indexes
            common_patterns = [
                {
                    "table": "users",
                    "column": "email",
                    "reason": "Frequent lookups by email"
                },
                {
                    "table": "invoices",
                    "column": "company_id",
                    "reason": "Multi-tenant filtering"
                },
                {
                    "table": "invoices",
                    "column": "status",
                    "reason": "Status-based filtering"
                },
                {
                    "table": "invoices",
                    "column": "created_at",
                    "reason": "Time-based queries"
                }
            ]
            
            for pattern in common_patterns:
                # Check if index exists
                index_check = text("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = :table_name 
                    AND indexdef LIKE :column_pattern
                """)
                
                result = db.execute(index_check, {
                    "table_name": pattern["table"],
                    "column_pattern": f"%{pattern['column']}%"
                }).fetchone()
                
                if not result:
                    missing_indexes.append(pattern)
            
            return missing_indexes
            
        except Exception as e:
            logger.error(f"Failed to find missing indexes: {e}")
            return []
    
    async def _analyze_connection_pool(self) -> Dict[str, Any]:
        """Analyze connection pool usage and performance"""
        try:
            pool = self.engine.pool
            
            return {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
                "pool_pre_ping": getattr(self.engine.pool, '_pre_ping', False)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze connection pool: {e}")
            return {"error": str(e)}

class DatabaseIndexManager:
    """Advanced index management and optimization"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
    
    async def create_performance_indexes(self) -> Dict[str, Any]:
        """Create performance-optimized indexes for common query patterns"""
        try:
            with SessionLocal() as db:
                indexes_created = []
                
                # Define performance indexes
                performance_indexes = [
                    {
                        "name": "idx_users_email_company",
                        "table": "users",
                        "columns": ["email", "company_id"],
                        "unique": True
                    },
                    {
                        "name": "idx_invoices_company_status",
                        "table": "invoices", 
                        "columns": ["company_id", "status"],
                        "unique": False
                    },
                    {
                        "name": "idx_invoices_created_at",
                        "table": "invoices",
                        "columns": ["created_at"],
                        "unique": False
                    },
                    {
                        "name": "idx_invoices_supplier_amount",
                        "table": "invoices",
                        "columns": ["supplier_name", "total_amount"],
                        "unique": False
                    },
                    {
                        "name": "idx_audit_logs_company_created",
                        "table": "audit_logs",
                        "columns": ["company_id", "created_at"],
                        "unique": False
                    },
                    {
                        "name": "idx_companies_status_tier",
                        "table": "companies",
                        "columns": ["status", "tier"],
                        "unique": False
                    }
                ]
                
                for index_def in performance_indexes:
                    try:
                        # Check if index already exists
                        check_query = text("""
                            SELECT indexname 
                            FROM pg_indexes 
                            WHERE indexname = :index_name
                        """)
                        
                        exists = db.execute(check_query, {"index_name": index_def["name"]}).fetchone()
                        
                        if not exists:
                            # Create index
                            columns_str = ", ".join(index_def["columns"])
                            unique_str = "UNIQUE" if index_def["unique"] else ""
                            
                            create_query = text(f"""
                                CREATE {unique_str} INDEX {index_def['name']} 
                                ON {index_def['table']} ({columns_str})
                            """)
                            
                            db.execute(create_query)
                            db.commit()
                            
                            indexes_created.append({
                                "name": index_def["name"],
                                "table": index_def["table"],
                                "columns": index_def["columns"],
                                "status": "created"
                            })
                        else:
                            indexes_created.append({
                                "name": index_def["name"],
                                "table": index_def["table"],
                                "columns": index_def["columns"],
                                "status": "already_exists"
                            })
                            
                    except Exception as e:
                        logger.error(f"Failed to create index {index_def['name']}: {e}")
                        indexes_created.append({
                            "name": index_def["name"],
                            "table": index_def["table"],
                            "columns": index_def["columns"],
                            "status": "failed",
                            "error": str(e)
                        })
                
                return {
                    "indexes_created": len([i for i in indexes_created if i["status"] == "created"]),
                    "indexes_existed": len([i for i in indexes_created if i["status"] == "already_exists"]),
                    "indexes_failed": len([i for i in indexes_created if i["status"] == "failed"]),
                    "details": indexes_created
                }
                
        except Exception as e:
            logger.error(f"Failed to create performance indexes: {e}")
            return {"error": str(e)}
    
    async def optimize_database_settings(self) -> Dict[str, Any]:
        """Optimize database settings for performance"""
        try:
            with SessionLocal() as db:
                optimizations = []
                
                # Check current settings
                settings_query = text("""
                    SELECT name, setting, unit, context
                    FROM pg_settings 
                    WHERE name IN (
                        'shared_buffers',
                        'effective_cache_size', 
                        'work_mem',
                        'maintenance_work_mem',
                        'random_page_cost',
                        'effective_io_concurrency'
                    )
                """)
                
                current_settings = db.execute(settings_query).fetchall()
                
                # Analyze and suggest optimizations
                for setting in current_settings:
                    name, value, unit, context = setting
                    
                    # This is a simplified analysis - in production, you'd have more sophisticated logic
                    suggestions = []
                    
                    if name == "shared_buffers" and int(value) < 256:
                        suggestions.append("Consider increasing shared_buffers to 25% of RAM")
                    
                    if name == "work_mem" and int(value) < 4:
                        suggestions.append("Consider increasing work_mem for better sort performance")
                    
                    if name == "random_page_cost" and float(value) > 4.0:
                        suggestions.append("Consider reducing random_page_cost for SSD storage")
                    
                    optimizations.append({
                        "setting": name,
                        "current_value": value,
                        "unit": unit,
                        "context": context,
                        "suggestions": suggestions
                    })
                
                return {
                    "current_settings": optimizations,
                    "timestamp": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to optimize database settings: {e}")
            return {"error": str(e)}

class DatabaseMaintenance:
    """Database maintenance and cleanup operations"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
    
    async def run_maintenance_tasks(self) -> Dict[str, Any]:
        """Run comprehensive database maintenance tasks"""
        try:
            with SessionLocal() as db:
                results = {}
                
                # Analyze tables
                analyze_result = await self._analyze_tables(db)
                results["analyze"] = analyze_result
                
                # Vacuum tables
                vacuum_result = await self._vacuum_tables(db)
                results["vacuum"] = vacuum_result
                
                # Update statistics
                stats_result = await self._update_statistics(db)
                results["statistics"] = stats_result
                
                # Clean up old data
                cleanup_result = await self._cleanup_old_data(db)
                results["cleanup"] = cleanup_result
                
                return {
                    "maintenance_tasks": results,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "status": "completed"
                }
                
        except Exception as e:
            logger.error(f"Failed to run maintenance tasks: {e}")
            return {"error": str(e)}
    
    async def _analyze_tables(self, db: Session) -> Dict[str, Any]:
        """Analyze all tables for query optimization"""
        try:
            analyze_query = text("ANALYZE")
            db.execute(analyze_query)
            db.commit()
            
            return {"status": "completed", "message": "All tables analyzed"}
            
        except Exception as e:
            logger.error(f"Failed to analyze tables: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _vacuum_tables(self, db: Session) -> Dict[str, Any]:
        """Vacuum tables to reclaim space and update statistics"""
        try:
            # Get list of tables
            tables_query = text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            
            tables = db.execute(tables_query).fetchall()
            vacuumed_tables = []
            
            for table in tables:
                try:
                    vacuum_query = text(f"VACUUM ANALYZE {table[0]}")
                    db.execute(vacuum_query)
                    vacuumed_tables.append(table[0])
                except Exception as e:
                    logger.error(f"Failed to vacuum table {table[0]}: {e}")
            
            db.commit()
            
            return {
                "status": "completed",
                "vacuumed_tables": vacuumed_tables,
                "count": len(vacuumed_tables)
            }
            
        except Exception as e:
            logger.error(f"Failed to vacuum tables: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _update_statistics(self, db: Session) -> Dict[str, Any]:
        """Update table statistics for better query planning"""
        try:
            stats_query = text("ANALYZE")
            db.execute(stats_query)
            db.commit()
            
            return {"status": "completed", "message": "Statistics updated"}
            
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _cleanup_old_data(self, db: Session) -> Dict[str, Any]:
        """Clean up old data based on retention policies"""
        try:
            cleanup_results = {}
            
            # Clean up old audit logs (older than 1 year)
            audit_cleanup = text("""
                DELETE FROM audit_logs 
                WHERE created_at < NOW() - INTERVAL '1 year'
            """)
            
            audit_result = db.execute(audit_cleanup)
            cleanup_results["audit_logs_deleted"] = audit_result.rowcount
            
            # Clean up old failed login attempts (older than 30 days)
            login_cleanup = text("""
                UPDATE users 
                SET failed_login_attempts = 0, locked_until = NULL
                WHERE locked_until < NOW() - INTERVAL '30 days'
            """)
            
            login_result = db.execute(login_cleanup)
            cleanup_results["login_attempts_reset"] = login_result.rowcount
            
            db.commit()
            
            return {
                "status": "completed",
                "cleanup_results": cleanup_results
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return {"status": "failed", "error": str(e)}

# Global instances
db_optimizer = DatabaseOptimizer(engine)
index_manager = DatabaseIndexManager(engine)
db_maintenance = DatabaseMaintenance(engine)
