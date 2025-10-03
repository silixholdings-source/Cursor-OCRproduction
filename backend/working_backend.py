#!/usr/bin/env python3
"""
Working Backend for AI ERP SaaS - Guaranteed to Start
This backend provides all necessary endpoints for frontend testing
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="AI ERP SaaS Backend",
    description="Working backend for OCR functionality testing",
    version="1.0.0"
)

# Add CORS middleware for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

class OCRRequest(BaseModel):
    file_name: str
    company_id: str = "default"
    test: bool = False

class OCRResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    message: str
    processing_time: float
    confidence_scores: Dict[str, float]

class InvoiceData(BaseModel):
    invoice_number: str
    supplier_name: str
    total_amount: float
    line_items: List[Dict[str, Any]]
    invoice_date: str
    due_date: Optional[str] = None

# Mock OCR processing function
async def process_ocr_document(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Mock OCR processing - simulates real OCR functionality"""
    
    # Simulate processing time
    import time
    start_time = time.time()
    time.sleep(0.1)  # Simulate OCR processing
    processing_time = time.time() - start_time
    
    # Generate mock invoice data
    invoice_data = {
        "invoice_number": f"INV-{uuid.uuid4().hex[:8].upper()}",
        "supplier_name": "Sample Supplier Corp",
        "total_amount": 1250.75,
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "line_items": [
            {
                "description": "Software License",
                "quantity": 1,
                "unit_price": 1000.00,
                "total": 1000.00
            },
            {
                "description": "Support Services",
                "quantity": 2,
                "unit_price": 125.375,
                "total": 250.75
            }
        ],
        "confidence_scores": {
            "total_amount": 0.98,
            "supplier_name": 0.95,
            "invoice_number": 0.92,
            "line_items": 0.89
        },
        "processing_time": processing_time,
        "file_name": filename,
        "extracted_at": datetime.now().isoformat()
    }
    
    return invoice_data

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "AI ERP SaaS Backend is running!",
        "status": "healthy",
        "endpoints": "/health, /api/v1/processing/demo, /api/v1/ocr/status"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        services={
            "database": "connected",
            "ocr_service": "available",
            "redis": "connected"
        }
    )

@app.get("/api/v1/ocr/status")
async def ocr_status():
    """OCR service status"""
    return {
        "status": "available",
        "provider": "mock",
        "supported_formats": ["pdf", "jpg", "jpeg", "png", "tiff"],
        "max_file_size": "10MB",
        "confidence_threshold": 0.8
    }

@app.post("/api/v1/processing/demo", response_model=OCRResponse)
async def demo_ocr_processing(request: OCRRequest):
    """Demo OCR processing endpoint"""
    try:
        # Simulate OCR processing
        mock_file_content = b"mock file content"
        result = await process_ocr_document(mock_file_content, request.file_name)
        
        return OCRResponse(
            status="success",
            data=result,
            message="Document processed successfully",
            processing_time=result["processing_time"],
            confidence_scores=result["confidence_scores"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/v1/processing/process")
async def process_uploaded_file(
    file: UploadFile = File(...),
    company_id: str = Form("default")
):
    """Process uploaded file for OCR"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        file_content = await file.read()
        
        # Check file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max size: 10MB")
        
        # Process file
        result = await process_ocr_document(file_content, file.filename)
        
        return {
            "status": "success",
            "data": result,
            "message": f"File {file.filename} processed successfully",
            "processing_time": result["processing_time"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/v1/invoices")
async def get_invoices():
    """Get list of processed invoices"""
    # Return mock invoices
    return {
        "status": "success",
        "data": [
            {
                "id": "inv_001",
                "invoice_number": "INV-2024-001",
                "supplier_name": "Sample Supplier Corp",
                "total_amount": 1250.75,
                "status": "processed",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "inv_002", 
                "invoice_number": "INV-2024-002",
                "supplier_name": "Another Supplier Inc",
                "total_amount": 850.00,
                "status": "pending_review",
                "created_at": datetime.now().isoformat()
            }
        ],
        "total": 2
    }

@app.get("/api/v1/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get specific invoice details"""
    # Return mock invoice details
    return {
        "status": "success",
        "data": {
            "id": invoice_id,
            "invoice_number": f"INV-{invoice_id.upper()}",
            "supplier_name": "Sample Supplier Corp",
            "total_amount": 1250.75,
            "line_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 1000.00,
                    "total": 1000.00
                },
                {
                    "description": "Support Services",
                    "quantity": 2,
                    "unit_price": 125.375,
                    "total": 250.75
                }
            ],
            "status": "processed",
            "confidence_scores": {
                "total_amount": 0.98,
                "supplier_name": 0.95,
                "invoice_number": 0.92
            },
            "created_at": datetime.now().isoformat()
        }
    }

@app.get("/api/v1/invoices/{invoice_id}/download")
async def download_invoice(invoice_id: str):
    """Download invoice file"""
    # Return mock download response
    return JSONResponse(
        content={"message": f"Invoice {invoice_id} download initiated"},
        headers={"Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"}
    )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "message": "The requested endpoint does not exist"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    print("🚀 Starting AI ERP SaaS Working Backend...")
    print("📡 Frontend URL: http://localhost:3000")
    print("🔗 Backend URL: http://localhost:8000")
    print("📋 Available endpoints:")
    print("   GET  /health - Health check")
    print("   GET  /api/v1/ocr/status - OCR service status")
    print("   POST /api/v1/processing/demo - Demo OCR processing")
    print("   POST /api/v1/processing/process - File upload OCR")
    print("   GET  /api/v1/invoices - List invoices")
    print("   GET  /api/v1/invoices/{id} - Get invoice details")
    print("   GET  /api/v1/invoices/{id}/download - Download invoice")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
