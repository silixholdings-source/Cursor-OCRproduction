"""
Invoice Processing Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import os
import uuid
from pathlib import Path

from core.database import get_db
from core.auth import auth_manager
from core.config import settings
from src.models.user import User
from services.invoice_processor import InvoiceProcessor
from services.simple_ocr import SimpleOCRService
from schemas.processing import (
    ProcessingResponse,
    BatchProcessingRequest,
    BatchProcessingResponse,
    ReprocessingRequest,
    ProcessingStatusResponse
)

router = APIRouter()

# Initialize invoice processor
processor = InvoiceProcessor()
simple_ocr = SimpleOCRService()

# Ensure upload directory exists
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/process", response_model=ProcessingResponse)
async def process_invoice(
    file: UploadFile = File(...),
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Process a single invoice file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Supported formats: PDF, JPG, JPEG, PNG, TIFF"
            )
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Process invoice
            result = await processor.process_invoice(
                file_path=str(file_path),
                company_id=str(current_user.company_id),
                user_id=str(current_user.id),
                db=db
            )
            
            if result["status"] == "success":
                return ProcessingResponse(
                    status="success",
                    message=result["message"],
                    invoice_id=result["invoice_id"],
                    processing_status=result["status"],
                    workflow_id=result.get("workflow_id"),
                    fraud_score=result.get("fraud_score"),
                    confidence_score=result.get("confidence_score")
                )
            elif result["status"] == "duplicate":
                return ProcessingResponse(
                    status="duplicate",
                    message=result["message"],
                    invoice_id=result["invoice_id"],
                    duplicate_id=result["duplicate_id"],
                    processing_status="rejected"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["message"]
                )
                
        finally:
            # Clean up uploaded file
            if file_path.exists():
                file_path.unlink()
                
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invoice processing failed: {str(e)}"
        )

@router.post("/batch", response_model=BatchProcessingResponse)
async def batch_process_invoices(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Process multiple invoice files in batch"""
    try:
        # Validate user has permission for batch processing
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for batch processing"
            )
        
        # Validate number of files
        if len(files) > 100:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch size cannot exceed 100 files"
            )
        
        # Validate file types
        for file in files:
            if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type for {file.filename}. Supported formats: PDF, JPG, JPEG, PNG, TIFF"
                )
        
        # Save uploaded files
        file_paths = []
        try:
            for file in files:
                file_extension = Path(file.filename).suffix
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_path = UPLOAD_DIR / unique_filename
                
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                file_paths.append(str(file_path))
            
            # Process invoices in batch
            result = await processor.batch_process_invoices(
                file_paths=file_paths,
                company_id=str(current_user.company_id),
                user_id=str(current_user.id),
                db=db
            )
            
            return BatchProcessingResponse(
                status="completed",
                total=result["total"],
                successful=result["successful"],
                failed=result["failed"],
                results=result["results"]
            )
            
        finally:
            # Clean up uploaded files
            for file_path in file_paths:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {str(e)}"
        )

@router.post("/reprocess", response_model=ProcessingResponse)
async def reprocess_invoice(
    request: ReprocessingRequest,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Reprocess an existing invoice"""
    try:
        # Validate user has permission to reprocess
        if current_user.role not in ["admin", "manager", "approver"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to reprocess invoices"
            )
        
        # Reprocess invoice
        result = await processor.reprocess_invoice(
            invoice_id=request.invoice_id,
            company_id=str(current_user.company_id),
            user_id=str(current_user.id),
            db=db
        )
        
        if result["status"] == "success":
            return ProcessingResponse(
                status="success",
                message=result["message"],
                invoice_id=result["invoice_id"],
                processing_status=result["status"],
                workflow_id=result.get("workflow_id"),
                fraud_score=result.get("fraud_score"),
                confidence_score=result.get("confidence_score")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invoice reprocessing failed: {str(e)}"
        )

@router.get("/status/{invoice_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    invoice_id: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get processing status of an invoice"""
    try:
        # Get invoice from database
        from src.models.invoice import Invoice
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        return ProcessingStatusResponse(
            invoice_id=str(invoice.id),
            status=invoice.status.value,
            processing_stage=_get_processing_stage(invoice),
            fraud_score=float(invoice.fraud_score) if invoice.fraud_score else None,
            confidence_score=float(invoice.confidence_score) if invoice.confidence_score else None,
            workflow_data=invoice.workflow_data,
            ocr_data=invoice.ocr_data,
            ai_gl_coding=invoice.ai_gl_coding,
            erp_status={
                "posted_to_erp": invoice.posted_to_erp,
                "erp_document_id": invoice.erp_document_id,
                "erp_posting_date": invoice.erp_posting_date.isoformat() if invoice.erp_posting_date else None,
                "erp_error_message": invoice.erp_error_message
            } if invoice.posted_to_erp or invoice.erp_document_id else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processing status: {str(e)}"
        )

def _get_processing_stage(invoice) -> str:
    """Determine the current processing stage of an invoice"""
    if invoice.status == "draft":
        return "ocr_extraction"
    elif invoice.status == "pending_approval":
        return "approval_workflow"
    elif invoice.status == "approved":
        return "erp_posting"
    elif invoice.status == "posted_to_erp":
        return "completed"
    elif invoice.status == "rejected":
        return "rejected"
    elif invoice.status == "error":
        return "error"
    else:
        return "unknown"

@router.post("/demo")
async def demo_process_invoice(
    file: UploadFile = File(...)
):
    """Demo processing endpoint that works without authentication and without database writes.
    Extracts data using SimpleOCRService and returns the OCR data payload for UI preview.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Supported formats: PDF, JPG, JPEG, PNG, TIFF"
            )
        # Save uploaded file temporarily
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        try:
            # Use simple OCR to extract without DB side effects
            ocr = await simple_ocr.extract_invoice(str(file_path), company_id="demo")
            return {
                "status": "success",
                "ocr_data": ocr
            }
        finally:
            if file_path.exists():
                file_path.unlink()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demo processing failed: {str(e)}"
        )

@router.get("/queue")
async def get_processing_queue(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get current processing queue for the company"""
    try:
        # Get invoices in various processing stages
        from src.models.invoice import Invoice, InvoiceStatus
        
        # Pending approval
        pending_approval = db.query(Invoice).filter(
            Invoice.company_id == current_user.company_id,
            Invoice.status == InvoiceStatus.PENDING_APPROVAL
        ).count()
        
        # Pending ERP posting
        pending_erp = db.query(Invoice).filter(
            Invoice.company_id == current_user.company_id,
            Invoice.status == InvoiceStatus.APPROVED
        ).count()
        
        # In error state
        error_count = db.query(Invoice).filter(
            Invoice.company_id == current_user.company_id,
            Invoice.status == InvoiceStatus.ERROR
        ).count()
        
        # Processing today
        from datetime import datetime, timedelta
        today = datetime.now().date()
        processing_today = db.query(Invoice).filter(
            Invoice.company_id == current_user.company_id,
            Invoice.created_at >= today
        ).count()
        
        return {
            "status": "success",
            "queue_summary": {
                "pending_approval": pending_approval,
                "pending_erp_posting": pending_erp,
                "error_count": error_count,
                "processing_today": processing_today
            },
            "total_in_queue": pending_approval + pending_erp + error_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processing queue: {str(e)}"
        )

@router.post("/validate")
async def validate_invoice_file(
    file: UploadFile = File(...),
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Validate invoice file before processing"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Supported formats: PDF, JPG, JPEG, PNG, TIFF"
            )
        
        # Check file size (max 10MB)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Basic file validation
        validation_result = {
            "file_name": file.filename,
            "file_size_bytes": len(content),
            "file_type": file.content_type,
            "is_valid": True,
            "validation_messages": []
        }
        
        # Check if file appears to be empty
        if len(content) < 100:  # Less than 100 bytes
            validation_result["is_valid"] = False
            validation_result["validation_messages"].append("File appears to be empty or corrupted")
        
        # Check file header for supported formats
        if file.filename.lower().endswith('.pdf'):
            if not content.startswith(b'%PDF'):
                validation_result["is_valid"] = False
                validation_result["validation_messages"].append("Invalid PDF file format")
        elif file.filename.lower().endswith(('.jpg', '.jpeg')):
            if not content.startswith(b'\xff\xd8\xff'):
                validation_result["is_valid"] = False
                validation_result["validation_messages"].append("Invalid JPEG file format")
        elif file.filename.lower().endswith('.png'):
            if not content.startswith(b'\x89PNG\r\n\x1a\n'):
                validation_result["is_valid"] = False
                validation_result["validation_messages"].append("Invalid PNG file format")
        
        return {
            "status": "success",
            "validation_result": validation_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File validation failed: {str(e)}"
        )












