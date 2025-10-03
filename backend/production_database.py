#!/usr/bin/env python3
"""
Production Database Setup for AI ERP SaaS
Configures PostgreSQL with proper connection pooling, SSL, and migrations
"""

import os
import asyncio
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)

class ProductionDatabase:
    """Production-grade database configuration"""
    
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://ai_erp_user:secure_password@localhost:5432/ai_erp_production"
        )
        self.pool_size = int(os.getenv("DATABASE_POOL_SIZE", "20"))
        self.max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))
        
    def create_engine(self):
        """Create production database engine with SSL and pooling"""
        connect_args = {
            "sslmode": "prefer",  # Use SSL if available
            "connect_timeout": 10,
            "command_timeout": 30,
            "server_settings": {
                "application_name": "ai_erp_saas_backend",
                "jit": "off"  # Disable JIT for consistent performance
            }
        }
        
        engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_pre_ping=True,  # Validate connections
            pool_recycle=3600,   # Recycle connections every hour
            echo=False,          # Disable SQL logging in production
            connect_args=connect_args,
            execution_options={
                "isolation_level": "READ_COMMITTED"
            }
        )
        
        return engine
    
    def create_session_factory(self, engine):
        """Create session factory for database operations"""
        return sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False
        )
    
    async def test_connection(self):
        """Test database connection and performance"""
        try:
            # Test basic connectivity
            conn = await asyncpg.connect(self.database_url)
            
            # Test query performance
            start_time = asyncio.get_event_loop().time()
            await conn.execute("SELECT 1")
            query_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Get database info
            db_info = await conn.fetchrow("""
                SELECT 
                    version() as version,
                    current_database() as database,
                    current_user as user,
                    inet_server_addr() as server_ip
            """)
            
            await conn.close()
            
            return {
                "status": "connected",
                "query_time_ms": round(query_time, 2),
                "database_info": dict(db_info) if db_info else {},
                "pool_status": {
                    "pool_size": self.pool_size,
                    "max_overflow": self.max_overflow
                }
            }
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def create_tables_sql(self):
        """SQL for creating production tables"""
        return """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            is_active BOOLEAN DEFAULT true,
            is_verified BOOLEAN DEFAULT false,
            company_id UUID,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Companies table
        CREATE TABLE IF NOT EXISTS companies (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            industry VARCHAR(100),
            tier VARCHAR(50) DEFAULT 'starter',
            status VARCHAR(50) DEFAULT 'active',
            settings JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Invoices table
        CREATE TABLE IF NOT EXISTS invoices (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            invoice_number VARCHAR(100) NOT NULL,
            vendor_name VARCHAR(255) NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            invoice_date DATE NOT NULL,
            due_date DATE,
            status VARCHAR(50) DEFAULT 'pending',
            company_id UUID NOT NULL,
            user_id UUID NOT NULL,
            file_path VARCHAR(500),
            ocr_data JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        -- Audit logs table
        CREATE TABLE IF NOT EXISTS audit_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID,
            company_id UUID,
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(100) NOT NULL,
            resource_id VARCHAR(100),
            details JSONB DEFAULT '{}',
            ip_address INET,
            user_agent TEXT,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_invoices_company_id ON invoices(company_id);
        CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
        CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_company_id ON users(company_id);
        """

# Initialize production database
production_db = ProductionDatabase()
