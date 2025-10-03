from sqlalchemy import create_engine, MetaData
from pathlib import Path
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
connect_args = {}
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite"):
    # Ensure parent directory exists for file-based SQLite
    try:
        # Extract filesystem path part from URL forms like sqlite:///./data/app.db
        db_path_str = database_url.replace("sqlite:///", "")
        db_path = Path(db_path_str).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    # SQLite-specific options
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    connect_args=connect_args
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        # Models should already be imported elsewhere
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def check_db_connection():
    """Check database connection"""
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            connection.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
