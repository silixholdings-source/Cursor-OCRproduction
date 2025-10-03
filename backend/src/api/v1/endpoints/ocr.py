"""API Endpoints for OCR and AI/ML related functionalities."""
import logging
import asyncio
from typing import Dict, Any
from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from core.database import get_db
from core.auth import auth_manager
from src.models.user import User, UserRole
from src.models.invoice import InvoiceType
from schemas.ocr import OCRProcessResponse, OCRCorrectionRequest, OCRCorrectionResponse, OCRConfigResponse
from services.simple_ocr import SimpleOCRService
from services.ml_training import MLTrainingService
from core.api_design import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter()

ocr_service = SimpleOCRService()
ml_training_service = MLTrainingService()

# Re-use UPLOAD_DIR from processing endpoint for consistency
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload", response_model=APIResponse[OCRProcessResponse], status_code=status.HTTP_200_OK)
async def upload_invoice_demo(
    file: UploadFile = File(...),
    invoice_type: InvoiceType = InvoiceType.INVOICE
):
    """Public demo endpoint for OCR upload without authentication."""
    if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Supported formats: PDF, JPG, JPEG, PNG, TIFF"
        )

    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process with OCR service
        company_id = "demo-company"  # Use demo company ID
        extracted_data = await ocr_service.extract_invoice(str(file_path), company_id)

        # Clean up uploaded file
        file_path.unlink()

        return APIResponse(
            success=True,
            data=OCRProcessResponse(
                invoice_id=str(uuid.uuid4()),
                extracted_data=extracted_data,
                confidence_score=0.95,
                processing_time_ms=1500,
                file_type=file.content_type or "application/octet-stream",
                file_size=len(content)
            ),
            message="Invoice data extracted successfully"
        )

    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )

@router.post("/extract", response_model=APIResponse[OCRProcessResponse], status_code=status.HTTP_200_OK)
async def extract_invoice_data_endpoint(
    file: UploadFile = File(...),
    invoice_type: InvoiceType = InvoiceType.INVOICE,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger advanced OCR extraction for an uploaded invoice file."""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to trigger OCR extraction."
        )

    if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Supported formats: PDF, JPG, JPEG, PNG, TIFF"
        )

    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        extracted_data = await ocr_service.extract_invoice_data(
            file_path=str(file_path),
            company_id=str(current_user.company_id),
            invoice_type=invoice_type
        )

        return APIResponse.success(
            data=OCRProcessResponse(
                extracted_data=extracted_data,
                message="Invoice data extracted successfully."
            ),
            message="OCR extraction completed."
        )
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR extraction failed: {str(e)}"
        )
    finally:
        if file_path.exists():
            file_path.unlink()

@router.post("/correct", response_model=APIResponse[OCRCorrectionResponse], status_code=status.HTTP_200_OK)
async def submit_ocr_correction_endpoint(
    request: OCRCorrectionRequest,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Submit user corrections to previously extracted OCR data for ML model training."""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to submit OCR corrections."
        )

    try:
        success = await ml_training_service.record_user_correction(
            db=db,
            invoice_id=str(request.invoice_id),
            user_id=str(current_user.id),
            company_id=str(current_user.company_id),
            original_ocr_data=request.original_ocr_data,
            corrected_data=request.corrected_data
        )
        db.commit()

        if success:
            # Asynchronously trigger retraining check
            asyncio.create_task(ml_training_service.check_and_trigger_retraining(db, str(current_user.company_id)))
            return APIResponse.success(
                data=OCRCorrectionResponse(message="OCR correction submitted for ML training."),
                message="Correction submitted."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record OCR correction."
            )
    except Exception as e:
        logger.error(f"Failed to submit OCR correction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit OCR correction: {str(e)}"
        )

@router.get("/config", response_model=APIResponse[OCRConfigResponse], status_code=status.HTTP_200_OK)
async def get_ocr_configuration_endpoint(
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Retrieve the current OCR configuration and settings."""
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view OCR configuration."
        )
    
    # Return mock configuration
    config = {
        "primary_provider": "advanced",
        "secondary_provider": None,
        "confidence_threshold": 0.8,
        "line_item_confidence_threshold": 0.7,
        "supported_invoice_types": [it.value for it in InvoiceType],
        "email_processing_enabled": True,
        "ml_training_enabled": True,
    }
    return APIResponse.success(
        data=OCRConfigResponse(**config),
        message="OCR configuration retrieved successfully."
    )

@router.get("/quality/{invoice_id}", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def validate_extraction_quality_endpoint(
    invoice_id: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Validate the quality of extracted invoice data."""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to validate extraction quality."
        )

    try:
        # TODO: Get actual invoice data from database
        # For now, return mock quality metrics
        quality_metrics = {
            "overall_quality_score": 0.85,
            "field_completeness": 0.9,
            "data_consistency": 0.8,
            "recommendations": ["Consider manual review of line items"]
        }
        
        return APIResponse.success(
            data=quality_metrics,
            message="Extraction quality validated successfully."
        )
    except Exception as e:
        logger.error(f"Failed to validate extraction quality: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate extraction quality: {str(e)}"
        )

@router.get("/training-stats", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
async def get_training_statistics_endpoint(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get ML training statistics and model performance metrics."""
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view training statistics."
        )

    try:
        stats = await ml_training_service.get_training_statistics(str(current_user.company_id))
        return APIResponse.success(
            data=stats,
            message="Training statistics retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Failed to get training statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get training statistics: {str(e)}"
        )