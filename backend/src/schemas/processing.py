from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    """Invoice processing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_APPROVAL = "requires_approval"
    APPROVED = "approved"
    REJECTED = "rejected"

class ProcessingResult(BaseModel):
    """Invoice processing result schema"""
    status: ProcessingStatus = Field(..., description="Processing status")
    message: str = Field(..., description="Processing message")
    invoice_id: str = Field(..., description="Invoice ID")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    fraud_score: Optional[float] = Field(None, description="Fraud detection score")
    confidence_score: Optional[float] = Field(None, description="OCR confidence score")
    duplicate_id: Optional[str] = Field(None, description="Duplicate invoice ID if detected")

class ProcessingRequest(BaseModel):
    """Invoice processing request schema"""
    invoice_id: str = Field(..., description="Invoice ID")
    file_path: str = Field(..., description="Invoice file path")
    company_id: str = Field(..., description="Company ID")
    force_reprocess: bool = Field(default=False, description="Force reprocessing")

class ProcessingResponse(BaseModel):
    """Invoice processing response schema"""
    success: bool = Field(..., description="Processing success")
    message: str = Field(..., description="Response message")
    result: ProcessingResult = Field(..., description="Processing result")

class BatchProcessingRequest(BaseModel):
    """Batch processing request schema"""
    invoice_ids: List[str] = Field(..., description="List of invoice IDs")
    company_id: str = Field(..., description="Company ID")
    force_reprocess: bool = Field(default=False, description="Force reprocessing")

class BatchProcessingResponse(BaseModel):
    """Batch processing response schema"""
    success: bool = Field(..., description="Batch processing success")
    message: str = Field(..., description="Response message")
    results: List[ProcessingResult] = Field(..., description="Processing results")
    total_processed: int = Field(..., description="Total invoices processed")
    successful: int = Field(..., description="Successfully processed")
    failed: int = Field(..., description="Failed to process")

class ProcessingStatusRequest(BaseModel):
    """Processing status request schema"""
    invoice_id: str = Field(..., description="Invoice ID")

class ProcessingStatusResponse(BaseModel):
    """Processing status response schema"""
    invoice_id: str = Field(..., description="Invoice ID")
    status: ProcessingStatus = Field(..., description="Current processing status")
    progress_percentage: Optional[float] = Field(None, description="Processing progress percentage")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class ProcessingMetrics(BaseModel):
    """Processing metrics schema"""
    total_processed: int = Field(..., description="Total invoices processed")
    successful: int = Field(..., description="Successfully processed")
    failed: int = Field(..., description="Failed to process")
    pending: int = Field(..., description="Pending processing")
    in_progress: int = Field(..., description="Currently processing")
    average_processing_time_ms: float = Field(..., description="Average processing time")
    success_rate: float = Field(..., description="Success rate percentage")

class ProcessingQueueStatus(BaseModel):
    """Processing queue status schema"""
    queue_size: int = Field(..., description="Current queue size")
    active_workers: int = Field(..., description="Active worker processes")
    queue_health: str = Field(..., description="Queue health status")
    last_processed: Optional[datetime] = Field(None, description="Last processed timestamp")

class ProcessingConfiguration(BaseModel):
    """Processing configuration schema"""
    enable_fraud_detection: bool = Field(default=True, description="Enable fraud detection")
    enable_duplicate_detection: bool = Field(default=True, description="Enable duplicate detection")
    confidence_threshold: float = Field(default=0.8, description="OCR confidence threshold")
    fraud_threshold: float = Field(default=0.7, description="Fraud detection threshold")
    max_processing_time_ms: int = Field(default=30000, description="Maximum processing time")

class ProcessingRetryRequest(BaseModel):
    """Processing retry request schema"""
    invoice_id: str = Field(..., description="Invoice ID")
    reason: str = Field(..., description="Retry reason")
    reset_status: bool = Field(default=True, description="Reset processing status")

class ProcessingRetryResponse(BaseModel):
    """Processing retry response schema"""
    success: bool = Field(..., description="Retry success")
    message: str = Field(..., description="Response message")
    invoice_id: str = Field(..., description="Invoice ID")
    new_status: ProcessingStatus = Field(..., description="New processing status")

class ReprocessingRequest(BaseModel):
    """Reprocessing request schema"""
    invoice_id: str = Field(..., description="Invoice ID")
    reason: str = Field(..., description="Reprocessing reason")
    reset_data: bool = Field(default=False, description="Reset extracted data")