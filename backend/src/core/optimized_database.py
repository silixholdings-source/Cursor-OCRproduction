"""
Optimized Database Configuration for Production
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Create optimized engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections when pool is exhausted
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
    echo=settings.ENVIRONMENT == "development",  # Log SQL queries in dev
    connect_args={
        "options": "-c timezone=utc"  # Set timezone to UTC
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database with optimized settings"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Create additional indexes for performance
        with engine.connect() as conn:
            # Create composite indexes for common queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_invoices_company_status_created 
                ON invoices(company_id, status, created_at DESC)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_invoices_supplier_amount 
                ON invoices(supplier_name, total_amount)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_company_created 
                ON audit_logs(company_id, created_at DESC)
            """))
            
            # Create partial indexes for active records
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_active_company 
                ON users(company_id) WHERE is_active = true
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_invoices_pending 
                ON invoices(company_id, created_at) 
                WHERE status = 'pending_approval'
            """))
            
            conn.commit()
        
        logger.info("Database initialized with optimized indexes")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def health_check():
    """Check database health"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Database optimization functions
async def optimize_database():
    """Run database optimization tasks"""
    try:
        with engine.connect() as conn:
            # Update table statistics
            conn.execute(text("ANALYZE"))
            
            # Vacuum tables (PostgreSQL specific)
            conn.execute(text("VACUUM ANALYZE"))
            
            conn.commit()
        
        logger.info("Database optimization completed")
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        raise

