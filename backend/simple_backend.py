#!/usr/bin/env python3
"""
Simple backend for AI ERP SaaS application
This is a minimal version that can run without complex dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import os
from typing import Dict, Any

# Create FastAPI app
app = FastAPI(
    title="AI ERP SaaS API",
    description="AI-powered ERP SaaS application with OCR and invoice processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": "development"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI ERP SaaS API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# OCR endpoint
@app.post("/api/v1/ocr/process")
async def process_ocr(file_data: Dict[str, Any]):
    """Process OCR for uploaded file"""
    try:
        # Mock OCR processing
        mock_result = {
            "success": True,
            "data": {
                "invoice_number": "INV-2024-001",
                "vendor": "Sample Vendor",
                "amount": 1250.00,
                "date": "2024-01-15",
                "items": [
                    {"description": "Sample Item 1", "quantity": 2, "price": 500.00},
                    {"description": "Sample Item 2", "quantity": 1, "price": 250.00}
                ]
            },
            "confidence": 0.95,
            "processing_time": 1.2
        }
        return mock_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

# Invoice endpoints
@app.get("/api/v1/invoices")
async def get_invoices():
    """Get all invoices"""
    return {
        "invoices": [
            {
                "id": 1,
                "invoice_number": "INV-2024-001",
                "vendor": "Sample Vendor",
                "amount": 1250.00,
                "status": "pending",
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]
    }

@app.post("/api/v1/invoices")
async def create_invoice(invoice_data: Dict[str, Any]):
    """Create a new invoice"""
    return {
        "success": True,
        "invoice": {
            "id": 2,
            "invoice_number": "INV-2024-002",
            "vendor": invoice_data.get("vendor", "Unknown Vendor"),
            "amount": invoice_data.get("amount", 0.0),
            "status": "pending",
            "created_at": time.time()
        }
    }

# Dashboard endpoint
@app.get("/api/v1/dashboard")
async def get_dashboard():
    """Get dashboard data"""
    return {
        "total_invoices": 150,
        "pending_invoices": 25,
        "approved_invoices": 120,
        "rejected_invoices": 5,
        "total_amount": 125000.00,
        "monthly_trend": [
            {"month": "Jan", "amount": 25000},
            {"month": "Feb", "amount": 30000},
            {"month": "Mar", "amount": 35000},
            {"month": "Apr", "amount": 35000}
        ]
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)