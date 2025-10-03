"""Simple FastAPI OCR service"""
import uuid
import asyncio
import random
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Simple OCR API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "simple-ocr"}

@app.post("/api/v1/ocr/process")
async def process_ocr(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    await asyncio.sleep(0.5)  # Simulate processing
    
    vendor_names = ["Tech Solutions Inc", "Office Supplies Co", "Cloud Services Ltd"]
    vendor = random.choice(vendor_names)
    amount = round(random.uniform(100, 5000), 2)
    
    return {
        "vendor": vendor,
        "invoice_number": f"INV-{random.randint(1000, 9999)}",
        "amount": amount,
        "currency": "USD",
        "invoice_date": datetime.now().strftime("%Y-%m-%d"),
        "overall_confidence": 0.95
    }


















