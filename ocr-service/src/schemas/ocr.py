"""
OCR Service Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime

class ProcessingStatus(str, Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"

class LineItem(BaseModel):
    """Invoice line item schema"""
    description: str
    quantity: float = 1.0
    unit_price: float
    total: float
    gl_account: Optional[str] = None

class ConfidenceScores(BaseModel):
    """Confidence scores for extracted data"""
    supplier_name: Optional[float] = None
    invoice_number: Optional[float] = None
    invoice_date: Optional[float] = None
    due_date: Optional[float] = None
    total_amount: Optional[float] = None
    line_items: Optional[float] = None
    overall_confidence: Optional[float] = None

class ProcessingMetadata(BaseModel):
    """Processing metadata"""
    provider: str
    processing_time_ms: float
    file_size_bytes: int
    extraction_method: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ExtractedData(BaseModel):
    """Extracted invoice data"""
    supplier_name: str
    invoice_number: str
    invoice_date: str
    due_date: Optional[str] = None
    total_amount: float
    currency: str = "USD"
    tax_amount: float = 0.0
    tax_rate: float = 0.0
    subtotal: float
    total_with_tax: float
    line_items: List[LineItem] = []
    confidence_scores: ConfidenceScores
    processing_metadata: ProcessingMetadata

class OCRRequest(BaseModel):
    """OCR processing request"""
    company_id: str
    file_path: str
    invoice_type: Optional[str] = None

class OCRResponse(BaseModel):
    """OCR processing response"""
    status: ProcessingStatus
    data: Optional[ExtractedData] = None
    message: str
    errors: List[str] = []
    warnings: List[str] = []

class JobStatus(BaseModel):
    """Async job status"""
    job_id: str
    status: ProcessingStatus
    progress: int = 0  # 0-100
    message: str
    result: Optional[ExtractedData] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)









