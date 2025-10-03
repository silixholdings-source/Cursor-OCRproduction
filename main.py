"""
OCR Automation Service - Standalone FastAPI service for document processing
"""
import logging
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import pytesseract
from PIL import Image
import pdfplumber
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """OCR Service Configuration"""
    # Azure Form Recognizer (optional)
    AZURE_FORM_RECOGNIZER_ENDPOINT: Optional[str] = None
    AZURE_FORM_RECOGNIZER_KEY: Optional[str] = None
    
    # OCR Configuration
    OCR_PROVIDER: str = "tesseract"  # tesseract, azure
    CONFIDENCE_THRESHOLD: float = 0.8
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png,tiff"
    
    # Service Configuration
    SERVICE_NAME: str = "OCR Automation Service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()

# Pydantic models
class OCRRequest(BaseModel):
    """OCR processing request"""
    company_id: str = "default"
    language: str = "eng"
    confidence_threshold: float = 0.8

class OCRResponse(BaseModel):
    """OCR processing response"""
    success: bool
    text: str
    confidence: float
    processing_time: float
    file_type: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    provider: str

# OCR Processor Class
class OCRProcessor:
    """Main OCR processing class"""
    
    def __init__(self, confidence_threshold: float = 0.8):
        self.confidence_threshold = confidence_threshold
        self.supported_formats = ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'tif']
    
    async def extract_text_from_image(self, image_path: str, language: str = "eng") -> Dict[str, Any]:
        """Extract text from image using Tesseract OCR"""
        try:
            # Load image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text with confidence scores
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Filter text by confidence
            text_elements = []
            for i, conf in enumerate(data['conf']):
                if int(conf) > (self.confidence_threshold * 100):
                    text = data['text'][i].strip()
                    if text:
                        text_elements.append(text)
            
            # Get overall text
            full_text = pytesseract.image_to_string(image, lang=language)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0
            
            return {
                "text": full_text.strip(),
                "confidence": avg_confidence,
                "filtered_text": " ".join(text_elements),
                "word_count": len(text_elements)
            }
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            raise e
    
    async def extract_text_from_pdf(self, pdf_path: str, language: str = "eng") -> Dict[str, Any]:
        """Extract text from PDF using pdfplumber"""
        try:
            # Use pdfplumber for text extraction
            with pdfplumber.open(pdf_path) as pdf:
                all_text = []
                page_count = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages):
                    logger.info(f"Processing PDF page {i+1}/{page_count}")
                    
                    # Extract text from page
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(page_text.strip())
                
                # Combine results
                combined_text = "\n\n".join(all_text)
                
                # For PDFs, we'll use a default confidence since pdfplumber doesn't provide confidence scores
                # In a production environment, you might want to use OCR on images extracted from PDFs
                confidence = 0.9 if combined_text.strip() else 0.0
                
                return {
                    "text": combined_text,
                    "confidence": confidence,
                    "page_count": page_count
                }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise e
    
    async def process_file(self, file_path: str, file_type: str, language: str = "eng") -> Dict[str, Any]:
        """Process file based on type"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if file_type.lower() == 'pdf':
                result = await self.extract_text_from_pdf(file_path, language)
            else:
                result = await self.extract_text_from_image(file_path, language)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            result["processing_time"] = processing_time
            
            return result
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            raise HTTPException(
                status_code=500, 
                detail=f"OCR processing failed: {str(e)}"
            )

# Global OCR processor
ocr_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ocr_processor
    
    # Startup
    logger.info("Starting OCR Automation Service...")
    
    # Initialize OCR processor
    ocr_processor = OCRProcessor(confidence_threshold=settings.CONFIDENCE_THRESHOLD)
    logger.info("OCR processor initialized with Tesseract")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OCR Automation Service...")

# Create FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Standalone OCR service for document text extraction",
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

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        provider=settings.OCR_PROVIDER
    )

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    if ocr_processor is None:
        raise HTTPException(status_code=503, detail="OCR service not ready")
    return {"status": "ready"}

@app.post("/ocr", response_model=OCRResponse)
async def process_ocr(
    file: UploadFile = File(...),
    language: str = "eng",
    confidence_threshold: float = 0.8,
    ocr_proc: OCRProcessor = Depends(get_ocr_processor)
):
    """
    Process uploaded document for OCR text extraction
    
    - **file**: Image or PDF file to process
    - **language**: Language code for OCR (default: eng)
    - **confidence_threshold**: Minimum confidence score (0.0-1.0)
    """
    
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
            result = await ocr_proc.process_file(temp_file_path, file_ext, language)
            
            return OCRResponse(
                success=True,
                text=result["text"],
                confidence=result["confidence"],
                processing_time=result["processing_time"],
                file_type=file_ext,
                error=None
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        return OCRResponse(
            success=False,
            text="",
            confidence=0.0,
            processing_time=0.0,
            file_type=file_ext,
            error=str(e)
        )

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "ocr": "/ocr",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 8000))
    )
