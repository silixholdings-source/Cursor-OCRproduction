"""
Advanced Database Migration Management
Provides comprehensive migration management with rollback capabilities and data integrity
"""
import logging
import os
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from sqlalchemy import text, MetaData, Table, Column, String, DateTime, Text, JSON
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import alembic
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from .database import engine, SessionLocal, Base
from .config import settings

logger = logging.getLogger(__name__)

class MigrationManager:
    """Advanced migration management with rollback and data integrity features"""
    
    def __init__(self, engine, alembic_cfg_path: str = "alembic.ini"):
        self.engine = engine
        self.alembic_cfg_path = alembic_cfg_path
        self.alembic_cfg = Config(alembic_cfg_path)
        self.script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        
        # Create migration tracking table
        self._create_migration_tracking_table()
    
    def _create_migration_tracking_table(self):
        """Create migration tracking table for custom migration management"""
        try:
            with SessionLocal() as db:
                # Create migration_tracking table if it doesn't exist
                create_table_sql = text("""
                    CREATE TABLE IF NOT EXISTS migration_tracking (
                        id SERIAL PRIMARY KEY,
                        migration_name VARCHAR(255) NOT NULL UNIQUE,
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        rollback_sql TEXT,
                        checksum VARCHAR(64),
                        status VARCHAR(50) DEFAULT 'applied',
                        created_by VARCHAR(255),
                        notes TEXT
                    )
                """)
                db.execute(create_table_sql)
                db.commit()
                logger.info("Migration tracking table created/verified")
        except Exception as e:
            logger.error(f"Failed to create migration tracking table: {e}")
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get comprehensive migration status"""
        try:
            with SessionLocal() as db:
                # Get current database revision
                context = MigrationContext.configure(db.connection())
                current_rev = context.get_current_revision()
                
                # Get all available migrations
                available_migrations = []
                for revision in self.script_dir.walk_revisions():
                    available_migrations.append({
                        "revision": revision.revision,
                        "down_revision": revision.down_revision,
                        "branch_labels": revision.branch_labels,
                        "depends_on": revision.depends_on,
                        "comment": revision.comment,
                        "doc": revision.doc
                    })
                
                # Get applied migrations from tracking table
                tracking_query = text("""
                    SELECT migration_name, applied_at, status, checksum, created_by, notes
                    FROM migration_tracking
                    ORDER BY applied_at DESC
                """)
                applied_migrations = db.execute(tracking_query).fetchall()
                
                # Check for pending migrations
                pending_migrations = []
                for migration in available_migrations:
                    is_applied = any(
                        applied.migration_name == migration["revision"] 
                        for applied in applied_migrations
                    )
                    if not is_applied:
                        pending_migrations.append(migration)
                
                return {
                    "current_revision": current_rev,
                    "available_migrations": available_migrations,
                    "applied_migrations": [
                        {
                            "migration_name": row[0],
                            "applied_at": row[1].isoformat() if row[1] else None,
                            "status": row[2],
                            "checksum": row[3],
                            "created_by": row[4],
                            "notes": row[5]
                        }
                        for row in applied_migrations
                    ],
                    "pending_migrations": pending_migrations,
                    "is_up_to_date": len(pending_migrations) == 0,
                    "timestamp": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {"error": str(e)}
    
    async def run_migrations(self, target_revision: str = "head") -> Dict[str, Any]:
        """Run pending migrations"""
        try:
            with SessionLocal() as db:
                # Get current status before migration
                status_before = await self.get_migration_status()
                
                # Run alembic upgrade
                command.upgrade(self.alembic_cfg, target_revision)
                
                # Get status after migration
                status_after = await self.get_migration_status()
                
                # Track the migration
                self._track_migration("upgrade", target_revision, "success")
                
                return {
                    "status": "success",
                    "target_revision": target_revision,
                    "migrations_applied": len(status_after.get("applied_migrations", [])) - 
                                        len(status_before.get("applied_migrations", [])),
                    "before_status": status_before,
                    "after_status": status_after,
                    "timestamp": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            self._track_migration("upgrade", target_revision, "failed", str(e))
            return {"error": str(e)}
    
    async def rollback_migration(self, target_revision: str) -> Dict[str, Any]:
        """Rollback to a specific revision"""
        try:
            with SessionLocal() as db:
                # Get current status before rollback
                status_before = await self.get_migration_status()
                
                # Run alembic downgrade
                command.downgrade(self.alembic_cfg, target_revision)
                
                # Get status after rollback
                status_after = await self.get_migration_status()
                
                # Track the rollback
                self._track_migration("rollback", target_revision, "success")
                
                return {
                    "status": "success",
                    "target_revision": target_revision,
                    "rollback_completed": True,
                    "before_status": status_before,
                    "after_status": status_after,
                    "timestamp": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to rollback migration: {e}")
            self._track_migration("rollback", target_revision, "failed", str(e))
            return {"error": str(e)}
    
    async def create_migration(self, message: str, autogenerate: bool = True) -> Dict[str, Any]:
        """Create a new migration"""
        try:
            # Generate migration file
            if autogenerate:
                command.revision(self.alembic_cfg, message=message, autogenerate=True)
            else:
                command.revision(self.alembic_cfg, message=message)
            
            # Get the latest migration file
            revisions = list(self.script_dir.walk_revisions())
            latest_revision = revisions[0] if revisions else None
            
            if latest_revision:
                self._track_migration("create", latest_revision.revision, "created", message)
                
                return {
                    "status": "success",
                    "migration_created": latest_revision.revision,
                    "message": message,
                    "file_path": latest_revision.path,
                    "timestamp": datetime.now(UTC).isoformat()
                }
            else:
                return {"error": "No migration file created"}
                
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            return {"error": str(e)}
    
    def _track_migration(self, operation: str, revision: str, status: str, 
                        notes: str = None, created_by: str = "system"):
        """Track migration operations in the database"""
        try:
            with SessionLocal() as db:
                # Calculate checksum for the migration
                checksum = self._calculate_checksum(revision)
                
                # Insert tracking record
                insert_query = text("""
                    INSERT INTO migration_tracking 
                    (migration_name, rollback_sql, checksum, status, created_by, notes)
                    VALUES (:migration_name, :rollback_sql, :checksum, :status, :created_by, :notes)
                    ON CONFLICT (migration_name) 
                    DO UPDATE SET 
                        status = EXCLUDED.status,
                        notes = EXCLUDED.notes,
                        applied_at = NOW()
                """)
                
                db.execute(insert_query, {
                    "migration_name": f"{operation}_{revision}",
                    "rollback_sql": None,  # Could be populated with actual rollback SQL
                    "checksum": checksum,
                    "status": status,
                    "created_by": created_by,
                    "notes": notes
                })
                db.commit()
                
        except Exception as e:
            logger.error(f"Failed to track migration: {e}")
    
    def _calculate_checksum(self, revision: str) -> str:
        """Calculate checksum for a migration revision"""
        try:
            import hashlib
            migration_file = self.script_dir.get_revision(revision)
            if migration_file and migration_file.path:
                with open(migration_file.path, 'rb') as f:
                    content = f.read()
                    return hashlib.md5(content).hexdigest()
            return "unknown"
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {e}")
            return "error"

class DataMigrationManager:
    """Advanced data migration management with validation and rollback"""
    
    def __init__(self, engine):
        self.engine = engine
        self.data_migrations = {}
    
    async def register_data_migration(self, name: str, migration_func, rollback_func=None):
        """Register a data migration function"""
        self.data_migrations[name] = {
            "migration": migration_func,
            "rollback": rollback_func,
            "registered_at": datetime.now(UTC)
        }
        logger.info(f"Data migration '{name}' registered")
    
    async def run_data_migration(self, name: str) -> Dict[str, Any]:
        """Run a specific data migration"""
        try:
            if name not in self.data_migrations:
                return {"error": f"Data migration '{name}' not found"}
            
            migration = self.data_migrations[name]
            
            with SessionLocal() as db:
                # Run the migration
                result = await migration["migration"](db)
                
                # Track the migration
                self._track_data_migration(name, "success", result)
                
                return {
                    "status": "success",
                    "migration_name": name,
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to run data migration '{name}': {e}")
            self._track_data_migration(name, "failed", str(e))
            return {"error": str(e)}
    
    async def rollback_data_migration(self, name: str) -> Dict[str, Any]:
        """Rollback a specific data migration"""
        try:
            if name not in self.data_migrations:
                return {"error": f"Data migration '{name}' not found"}
            
            migration = self.data_migrations[name]
            
            if not migration["rollback"]:
                return {"error": f"No rollback function available for '{name}'"}
            
            with SessionLocal() as db:
                # Run the rollback
                result = await migration["rollback"](db)
                
                # Track the rollback
                self._track_data_migration(f"{name}_rollback", "success", result)
                
                return {
                    "status": "success",
                    "migration_name": name,
                    "rollback_result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to rollback data migration '{name}': {e}")
            return {"error": str(e)}
    
    def _track_data_migration(self, name: str, status: str, result: Any):
        """Track data migration operations"""
        try:
            with SessionLocal() as db:
                insert_query = text("""
                    INSERT INTO migration_tracking 
                    (migration_name, status, notes, created_by)
                    VALUES (:migration_name, :status, :notes, :created_by)
                """)
                
                db.execute(insert_query, {
                    "migration_name": f"data_{name}",
                    "status": status,
                    "notes": str(result)[:1000] if result else None,
                    "created_by": "data_migration_manager"
                })
                db.commit()
                
        except Exception as e:
            logger.error(f"Failed to track data migration: {e}")

class DatabaseSchemaValidator:
    """Advanced database schema validation and integrity checking"""
    
    def __init__(self, engine):
        self.engine = engine
    
    async def validate_schema_integrity(self) -> Dict[str, Any]:
        """Validate database schema integrity"""
        try:
            with SessionLocal() as db:
                validation_results = {}
                
                # Check table existence
                table_check = await self._check_table_existence(db)
                validation_results["tables"] = table_check
                
                # Check foreign key constraints
                fk_check = await self._check_foreign_keys(db)
                validation_results["foreign_keys"] = fk_check
                
                # Check indexes
                index_check = await self._check_indexes(db)
                validation_results["indexes"] = index_check
                
                # Check constraints
                constraint_check = await self._check_constraints(db)
                validation_results["constraints"] = constraint_check
                
                # Check data integrity
                data_check = await self._check_data_integrity(db)
                validation_results["data_integrity"] = data_check
                
                return {
                    "validation_results": validation_results,
                    "overall_status": "healthy" if all(
                        result.get("status") == "healthy" 
                        for result in validation_results.values()
                    ) else "issues_found",
                    "timestamp": datetime.now(UTC).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to validate schema integrity: {e}")
            return {"error": str(e)}
    
    async def _check_table_existence(self, db: Session) -> Dict[str, Any]:
        """Check if all expected tables exist"""
        try:
            expected_tables = [
                "users", "companies", "invoices", "invoice_lines", 
                "audit_logs", "migration_tracking"
            ]
            
            existing_tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            existing_tables = [row[0] for row in db.execute(existing_tables_query).fetchall()]
            
            missing_tables = [table for table in expected_tables if table not in existing_tables]
            
            return {
                "status": "healthy" if not missing_tables else "issues_found",
                "expected_tables": expected_tables,
                "existing_tables": existing_tables,
                "missing_tables": missing_tables
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_foreign_keys(self, db: Session) -> Dict[str, Any]:
        """Check foreign key constraints"""
        try:
            fk_query = text("""
                SELECT 
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    tc.constraint_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
            """)
            
            foreign_keys = db.execute(fk_query).fetchall()
            
            return {
                "status": "healthy",
                "foreign_keys": [
                    {
                        "table": row[0],
                        "column": row[1],
                        "references_table": row[2],
                        "references_column": row[3],
                        "constraint_name": row[4]
                    }
                    for row in foreign_keys
                ]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_indexes(self, db: Session) -> Dict[str, Any]:
        """Check database indexes"""
        try:
            index_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)
            
            indexes = db.execute(index_query).fetchall()
            
            return {
                "status": "healthy",
                "indexes": [
                    {
                        "schema": row[0],
                        "table": row[1],
                        "index": row[2],
                        "definition": row[3]
                    }
                    for row in indexes
                ]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_constraints(self, db: Session) -> Dict[str, Any]:
        """Check database constraints"""
        try:
            constraint_query = text("""
                SELECT 
                    tc.table_name,
                    tc.constraint_name,
                    tc.constraint_type,
                    cc.check_clause
                FROM information_schema.table_constraints tc
                LEFT JOIN information_schema.check_constraints cc
                    ON tc.constraint_name = cc.constraint_name
                WHERE tc.table_schema = 'public'
                ORDER BY tc.table_name, tc.constraint_name
            """)
            
            constraints = db.execute(constraint_query).fetchall()
            
            return {
                "status": "healthy",
                "constraints": [
                    {
                        "table": row[0],
                        "name": row[1],
                        "type": row[2],
                        "check_clause": row[3]
                    }
                    for row in constraints
                ]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_data_integrity(self, db: Session) -> Dict[str, Any]:
        """Check data integrity across tables"""
        try:
            integrity_checks = []
            
            # Check for orphaned records
            orphan_check = text("""
                SELECT COUNT(*) as orphaned_invoices
                FROM invoices i
                LEFT JOIN companies c ON i.company_id = c.id
                WHERE c.id IS NULL
            """)
            
            orphan_result = db.execute(orphan_check).fetchone()
            integrity_checks.append({
                "check": "orphaned_invoices",
                "count": orphan_result[0] if orphan_result else 0,
                "status": "healthy" if (orphan_result[0] if orphan_result else 0) == 0 else "issues_found"
            })
            
            # Check for invalid email formats
            email_check = text("""
                SELECT COUNT(*) as invalid_emails
                FROM users
                WHERE email !~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
            """)
            
            email_result = db.execute(email_check).fetchone()
            integrity_checks.append({
                "check": "invalid_emails",
                "count": email_result[0] if email_result else 0,
                "status": "healthy" if (email_result[0] if email_result else 0) == 0 else "issues_found"
            })
            
            return {
                "status": "healthy" if all(check["status"] == "healthy" for check in integrity_checks) else "issues_found",
                "checks": integrity_checks
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global instances - lazy initialization
migration_manager = None
data_migration_manager = None
schema_validator = None

def get_migration_manager():
    global migration_manager
    if migration_manager is None:
        migration_manager = MigrationManager(engine)
    return migration_manager

def get_data_migration_manager():
    global data_migration_manager
    if data_migration_manager is None:
        data_migration_manager = DataMigrationManager(engine)
    return data_migration_manager

def get_schema_validator():
    global schema_validator
    if schema_validator is None:
        schema_validator = DatabaseSchemaValidator(engine)
    return schema_validator
