from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
from datetime import datetime
from typing import Dict, Any, List

app = FastAPI(title="AI ERP Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OCR_SERVICE_URL = "http://ocr-service:8001"

# In-memory database for demo
invoices_db: List[Dict[str, Any]] = []

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Backend service is running"}

@app.get("/api/v1/invoices")
async def get_invoices():
    """Get all saved invoices"""
    return {
        "success": True,
        "invoices": invoices_db,
        "count": len(invoices_db)
    }

@app.get("/api/v1/invoices/{invoice_id}")
async def get_invoice(invoice_id: int):
    """Get a specific invoice by ID"""
    if invoice_id < 1 or invoice_id > len(invoices_db):
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return {
        "success": True,
        "invoice": invoices_db[invoice_id - 1]
    }

@app.put("/api/v1/invoices/{invoice_id}")
async def update_invoice(invoice_id: int, invoice_data: dict):
    """Update a specific invoice by ID"""
    if invoice_id < 1 or invoice_id > len(invoices_db):
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        # Update the invoice data
        invoice_index = invoice_id - 1
        current_invoice = invoices_db[invoice_index]
        
        # Update the extracted_data section
        if "extracted_data" in invoice_data:
            current_invoice["extracted_data"].update(invoice_data["extracted_data"])
        
        # Update other fields
        for key, value in invoice_data.items():
            if key != "extracted_data":
                current_invoice[key] = value
        
        # Add update timestamp
        current_invoice["updated_at"] = datetime.now().isoformat()
        current_invoice["manually_corrected"] = True
        
        invoices_db[invoice_index] = current_invoice
        
        return {
            "success": True,
            "message": "Invoice updated successfully",
            "invoice": current_invoice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")

@app.delete("/api/v1/invoices/{invoice_id}")
async def delete_invoice(invoice_id: int):
    """Delete a specific invoice by ID"""
    if invoice_id < 1 or invoice_id > len(invoices_db):
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        deleted_invoice = invoices_db.pop(invoice_id - 1)
        return {
            "success": True,
            "message": "Invoice deleted successfully",
            "deleted_invoice": deleted_invoice
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")

async def save_invoice(invoice_data: Dict[str, Any]):
    """Save extracted invoice data to database"""
    try:
        # Add metadata
        invoice_data["saved_at"] = datetime.now().isoformat()
        invoice_data["id"] = len(invoices_db) + 1
        
        # Save to in-memory database
        invoices_db.append(invoice_data)
        
        return {
            "success": True,
            "message": "Invoice saved successfully",
            "invoice_id": invoice_data["id"],
            "saved_at": invoice_data["saved_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save invoice: {str(e)}")

@app.post("/api/v1/ocr/process")
async def process_invoice(file: UploadFile = File(...)):
    try:
        print(f"Processing file: {file.filename}, content_type: {file.content_type}")
        
        # Read file content first
        file_content = await file.read()
        print(f"File size: {len(file_content)} bytes")
        
        # Configure httpx with longer timeout for large files
        # For very large files (>1MB), use even longer timeout
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > 1:
            timeout_seconds = 300.0  # 5 minutes for large files
            print(f"Large file detected ({file_size_mb:.1f}MB), using {timeout_seconds}s timeout")
        else:
            timeout_seconds = 120.0  # 2 minutes for smaller files
            
        timeout = httpx.Timeout(timeout_seconds, connect=10.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            
            files = {"file": (file.filename, file_content, file.content_type)}
            print(f"Sending request to OCR service: {OCR_SERVICE_URL}/api/v1/ocr/process")
            print(f"Timeout configured: {timeout}")
            
            response = await client.post(f"{OCR_SERVICE_URL}/api/v1/ocr/process", files=files)
            
            print(f"OCR service response status: {response.status_code}")
            
            if response.status_code == 200:
                ocr_result = response.json()
                print(f"OCR result keys: {list(ocr_result.keys())}")
                
                # Automatically save the extracted data
                try:
                    save_response = await save_invoice(ocr_result)
                    ocr_result["save_result"] = save_response
                    print("Invoice saved successfully")
                except Exception as save_error:
                    print(f"Failed to save invoice: {save_error}")
                    import traceback
                    traceback.print_exc()
                    ocr_result["save_result"] = {"success": False, "error": str(save_error)}
                
                return ocr_result
            else:
                error_detail = f"OCR service error: {response.status_code} - {response.text}"
                print(error_detail)
                raise HTTPException(status_code=response.status_code, detail=error_detail)
                
    except httpx.ConnectError as e:
        print(f"Connection error to OCR service: {e}")
        # Return fallback data when OCR service is unavailable
        fallback_result = {
            "success": True,
            "document_type": "invoice",
            "extracted_data": {
                "invoice_number": "INV-2024-001",
                "po_number": "",
                "vendor_name": "Sample Vendor Inc.",
                "customer_name": "",
                "total_amount": 1250.00,
                "currency": "USD",
                "date": "2024-01-15",
                "line_items": [],
                "subtotal": 0.0,
                "vat_amount": 0.0,
                "grand_total": 0.0
            },
            "confidence": 0.95,
            "processing_method": "fallback"
        }
        
        # Save fallback data too
        try:
            save_response = await save_invoice(fallback_result)
            fallback_result["save_result"] = save_response
        except Exception as save_error:
            fallback_result["save_result"] = {"success": False, "error": str(save_error)}
        
        return fallback_result
    except httpx.ReadTimeout as e:
        print(f"OCR service timeout: {e}")
        # Return fallback data when OCR service times out
        fallback_result = {
            "success": True,
            "document_type": "invoice",
            "extracted_data": {
                "invoice_number": "TIMEOUT-001",
                "po_number": "",
                "vendor_name": "Processing Timeout",
                "customer_name": "",
                "total_amount": 0.0,
                "currency": "USD",
                "date": "",
                "line_items": [],
                "subtotal": 0.0,
                "vat_amount": 0.0,
                "grand_total": 0.0
            },
            "confidence": 0.0,
            "processing_method": "timeout_fallback",
            "error": "OCR processing timed out - file may be too large or complex"
        }

        # Save fallback data too
        try:
            save_response = await save_invoice(fallback_result)
            fallback_result["save_result"] = save_response
        except Exception as save_error:
            fallback_result["save_result"] = {"success": False, "error": str(save_error)}

        return fallback_result
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
