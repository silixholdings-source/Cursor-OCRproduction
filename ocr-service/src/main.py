"""
OCR Microservice - Dedicated service for document processing and OCR
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseSettings
from typing import Dict, Any, Optional
import asyncio
import tempfile
import os
from pathlib import Path

from services.ocr_processor import OCRProcessor
from services.azure_ocr import AzureOCRService
from services.mock_ocr import MockOCRService
from schemas.ocr import OCRRequest, OCRResponse, ProcessingStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """OCR Service Configuration"""
    # Azure Form Recognizer
    AZURE_FORM_RECOGNIZER_ENDPOINT: Optional[str] = None
    AZURE_FORM_RECOGNIZER_KEY: Optional[str] = None
    
    # OCR Configuration
    OCR_PROVIDER: str = "mock"  # mock, azure
    CONFIDENCE_THRESHOLD: float = 0.8
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png,tiff"
    
    # Service Configuration
    SERVICE_NAME: str = "OCR Service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Global OCR processor
ocr_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ocr_processor
    
    # Startup
    logger.info("Starting OCR Microservice...")
    
    # Initialize OCR processor based on configuration
    if settings.OCR_PROVIDER == "azure" and settings.AZURE_FORM_RECOGNIZER_ENDPOINT:
        try:
            ocr_processor = AzureOCRService(
                endpoint=settings.AZURE_FORM_RECOGNIZER_ENDPOINT,
                key=settings.AZURE_FORM_RECOGNIZER_KEY,
                confidence_threshold=settings.CONFIDENCE_THRESHOLD
            )
            logger.info("Azure OCR service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Azure OCR, falling back to mock: {e}")
            ocr_processor = MockOCRService(confidence_threshold=settings.CONFIDENCE_THRESHOLD)
    else:
        ocr_processor = MockOCRService(confidence_threshold=settings.CONFIDENCE_THRESHOLD)
        logger.info("Mock OCR service initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OCR Microservice...")

# Create FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Dedicated OCR service for document processing and data extraction",
    version=settings.VERSION,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

def get_ocr_processor() -> OCRProcessor:
    """Dependency to get OCR processor"""
    if ocr_processor is None:
        raise HTTPException(status_code=503, detail="OCR service not initialized")
    return ocr_processor

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "provider": settings.OCR_PROVIDER
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    if ocr_processor is None:
        raise HTTPException(status_code=503, detail="OCR service not ready")
    return {"status": "ready"}

@app.post("/process", response_model=OCRResponse)
async def process_document(
    file: UploadFile = File(...),
    company_id: str = "default",
    ocr_proc: OCRProcessor = Depends(get_ocr_processor)
):
    """Process uploaded document for OCR extraction"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    allowed_extensions = settings.ALLOWED_EXTENSIONS.split(',')
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not supported. Allowed: {allowed_extensions}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Process document
            result = await ocr_proc.extract_invoice(temp_file_path, company_id)
            
            return OCRResponse(
                status=ProcessingStatus.SUCCESS,
                data=result,
                message="Document processed successfully"
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process/async", response_model=Dict[str, str])
async def process_document_async(
    file: UploadFile = File(...),
    company_id: str = "default",
    ocr_proc: OCRProcessor = Depends(get_ocr_processor)
):
    """Process document asynchronously and return job ID"""
    # This would typically queue the job and return a job ID
    # For now, we'll process synchronously but return a job-like response
    try:
        result = await process_document(file, company_id, ocr_proc)
        return {
            "job_id": f"ocr_{company_id}_{asyncio.get_event_loop().time()}",
            "status": "completed",
            "result": result.dict()
        }
    except Exception as e:
        return {
            "job_id": f"ocr_{company_id}_{asyncio.get_event_loop().time()}",
            "status": "failed",
            "error": str(e)
        }

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of async processing job"""
    # In a real implementation, this would check job status from a queue
    return {
        "job_id": job_id,
        "status": "completed",
        "message": "Job status checking not implemented in this version"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)









