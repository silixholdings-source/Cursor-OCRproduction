"""Pydantic Schemas for OCR and AI/ML related API requests and responses."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid

class OCRProcessRequest(BaseModel):
    """Schema for requesting OCR processing."""
    invoice_type: Optional[str] = Field("STANDARD", description="Type of invoice to process")

class OCRProcessResponse(BaseModel):
    """Schema for the response after OCR processing."""
    message: str = Field(..., description="A message indicating the result of the OCR processing.")
    extracted_data: Dict[str, Any] = Field(..., description="The full data extracted by the OCR service.")

class OCRCorrectionRequest(BaseModel):
    """Schema for submitting user corrections to OCR data for ML training."""
    invoice_id: uuid.UUID = Field(..., description="The ID of the invoice being corrected.")
    original_ocr_data: Dict[str, Any] = Field(..., description="The original data extracted by the OCR service.")
    corrected_data: Dict[str, Any] = Field(..., description="The user-corrected data for the invoice.")

class OCRCorrectionResponse(BaseModel):
    """Schema for the response after submitting OCR corrections."""
    message: str = Field(..., description="A message indicating the result of the correction submission.")

class OCRConfigResponse(BaseModel):
    """Schema for retrieving OCR configuration settings."""
    primary_provider: str = Field(..., description="The primary OCR provider in use.")
    secondary_provider: Optional[str] = Field(None, description="The secondary OCR provider, if any.")
    confidence_threshold: float = Field(..., description="Minimum confidence score for critical header fields.")
    line_item_confidence_threshold: float = Field(..., description="Minimum confidence score for line item fields.")
    supported_invoice_types: List[str] = Field(..., description="List of supported invoice types.")
    email_processing_enabled: bool = Field(..., description="Indicates if email-based invoice processing is enabled.")
    ml_training_enabled: bool = Field(..., description="Indicates if ML model training for OCR corrections is enabled.")

class OCRQualityMetrics(BaseModel):
    """Schema for OCR quality validation metrics."""
    overall_quality_score: float = Field(..., description="Overall quality score (0-1).")
    field_completeness: float = Field(..., description="Percentage of required fields present.")
    data_consistency: float = Field(..., description="Consistency score for data validation.")
    confidence_distribution: Dict[str, float] = Field(..., description="Confidence scores for each field.")
    recommendations: List[str] = Field(..., description="Recommendations for improving extraction quality.")

class MLTrainingStats(BaseModel):
    """Schema for ML training statistics."""
    total_training_samples: int = Field(..., description="Total number of training samples.")
    last_training_date: Optional[str] = Field(None, description="Date of last model training.")
    retrain_interval_days: float = Field(..., description="Days between retraining cycles.")
    min_samples_required: int = Field(..., description="Minimum samples required for retraining.")
    model_performance: Dict[str, float] = Field(..., description="Model performance metrics.")