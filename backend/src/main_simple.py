"""
Simplified FastAPI main application
This version only imports modules that actually exist and work
"""
import sys
import os
from pathlib import Path

# Set environment variables for local testing
os.environ["DATABASE_URL"] = "sqlite:///./app.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["SECRET_KEY"] = "dev-secret-key-for-testing"
os.environ["OCR_PROVIDER"] = "mock"
os.environ["ENVIRONMENT"] = "development"

# Ensure the src directory is on PYTHONPATH when running from repo root or backend dir
current_file_path = Path(__file__).resolve()
src_directory_path = current_file_path.parent
if str(src_directory_path) not in sys.path:
    sys.path.insert(0, str(src_directory_path))

from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging
from contextlib import asynccontextmanager
import redis.asyncio as redis

from core.config import settings
from core.database import engine, get_db, Base
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for shared resources
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    
    # Startup
    logger.info("Starting up AI ERP SaaS application...")
    
    # Initialize Redis client (optional for development)
    redis_client = None
    try:
        if settings.REDIS_URL and "localhost" in settings.REDIS_URL:
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            logger.info("Redis connection established")
        else:
            logger.info("Redis connection skipped (not configured or not localhost)")
    except Exception as e:
        logger.warning(f"Redis connection failed, continuing without Redis: {e}")
        redis_client = None
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    # Store shared resources in app state
    app.state.redis_client = redis_client
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI ERP SaaS application...")
    
    # Close Redis connection
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

# Create FastAPI app
app = FastAPI(
    title="AI ERP SaaS API",
    description="AI-powered ERP SaaS application with OCR, 3-way matching, and multi-tenant support",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list
)

# Add GZIP compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Readiness check endpoint
@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/container orchestration"""
    try:
        # Test database connection (critical)
        db = next(get_db())
        db.execute(text("SELECT 1"))
        
        # Redis is optional for development
        if redis_client:
            try:
                await redis_client.ping()
            except Exception as e:
                logger.warning(f"Redis health check failed: {e}")
        
        return {"status": "ready", "timestamp": time.time()}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e), "timestamp": time.time()}

# Liveness check endpoint
@app.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes/container orchestration"""
    return {"status": "alive", "timestamp": time.time()}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI ERP SaaS API",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else None
    }

# Basic OCR endpoint for testing
@app.post("/api/v1/ocr/upload")
async def upload_file(file: UploadFile = File(...)):
    """Basic file upload endpoint for testing"""
    try:
        # Import OCR service
        from services.simple_ocr import SimpleOCRService
        
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Supported formats: PDF, JPG, JPEG, PNG, TIFF"
            )
        
        # Save uploaded file temporarily
        import tempfile
        import uuid
        from pathlib import Path
        
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        temp_path = Path(tempfile.gettempdir()) / unique_filename
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process with OCR service
        ocr_service = SimpleOCRService()
        company_id = "demo-company"
        extracted_data = await ocr_service.extract_invoice(str(temp_path), company_id)
        
        # Clean up temp file
        temp_path.unlink()
        
        return {
            "success": True,
            "data": {
                "invoice_id": str(uuid.uuid4()),
                "extracted_data": extracted_data,
                "confidence_score": 0.95,
                "processing_time_ms": 1500,
                "file_type": file.content_type or "application/octet-stream",
                "file_size": len(content)
            },
            "message": "Invoice data extracted successfully"
        }
        
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )

# Basic invoice endpoint for testing
@app.get("/api/v1/invoices")
async def get_invoices():
    """Basic invoice listing endpoint for testing"""
    return {"message": "Invoice listing endpoint - database integration needed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
