"""
Mock OCR Service - For development and testing
"""
import logging
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any

from .ocr_processor import OCRProcessor

logger = logging.getLogger(__name__)

class MockOCRService(OCRProcessor):
    """Mock OCR service for development and testing"""
    
    def __init__(self, confidence_threshold: float = 0.8):
        super().__init__(confidence_threshold)
        logger.info("Mock OCR Service initialized")
    
    async def extract_invoice(self, file_path: str, company_id: str) -> Dict[str, Any]:
        """Extract invoice data with mock data"""
        logger.info(f"Mock OCR processing file: {file_path}")
        
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Generate realistic mock data
        invoice_number = f"INV-{random.randint(1000, 9999)}"
        vendor_names = [
            "Tech Solutions Inc", "Office Supplies Co", "Cloud Services Ltd", 
            "Marketing Agency", "Consulting Group", "Software Corp",
            "Hardware Solutions", "Professional Services LLC"
        ]
        vendor = random.choice(vendor_names)
        amount = round(random.uniform(100, 5000), 2)
        tax_rate = random.choice([0.08, 0.10, 0.12])
        tax_amount = round(amount * tax_rate, 2)
        
        # Generate recent dates
        invoice_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=random.randint(15, 45))).strftime("%Y-%m-%d")
        
        # Generate line items
        line_items = []
        base_amount = amount * 0.8  # 80% for line items, 20% for tax
        
        # Main service/product
        main_item = {
            "description": random.choice([
                "Professional Services", "Software License", "Consulting Hours",
                "Office Supplies", "Cloud Services", "Marketing Campaign",
                "Hardware Equipment", "Training Services"
            ]),
            "quantity": random.randint(1, 5),
            "unit_price": round(base_amount / random.randint(1, 5), 2),
            "total": round(base_amount, 2),
            "gl_account": random.choice(["6000", "6500", "7000", "7500"])
        }
        main_item["total"] = round(main_item["quantity"] * main_item["unit_price"], 2)
        line_items.append(main_item)
        
        # Additional line items (sometimes)
        if random.random() > 0.5:
            additional_item = {
                "description": random.choice([
                    "Setup Fee", "Support Services", "Additional Licenses",
                    "Customization", "Training", "Maintenance"
                ]),
                "quantity": 1,
                "unit_price": round(amount * 0.1, 2),
                "total": round(amount * 0.1, 2),
                "gl_account": random.choice(["6000", "6500", "7000"])
            }
            line_items.append(additional_item)
        
        # Calculate totals
        subtotal = sum(item["total"] for item in line_items)
        total_with_tax = subtotal + tax_amount
        
        return {
            "supplier_name": vendor,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "due_date": due_date,
            "total_amount": amount,
            "currency": "USD",
            "tax_amount": tax_amount,
            "tax_rate": tax_rate,
            "subtotal": subtotal,
            "total_with_tax": total_with_tax,
            "line_items": line_items,
            "confidence_scores": {
                "supplier_name": 0.95,
                "invoice_number": 0.98,
                "invoice_date": 0.92,
                "due_date": 0.90,
                "total_amount": 0.99,
                "line_items": 0.94,
                "overall_confidence": 0.95
            },
            "processing_metadata": {
                "provider": "mock",
                "processing_time_ms": 100,
                "file_size_bytes": 1024,
                "extraction_method": "mock_simulation",
                "timestamp": datetime.utcnow().isoformat()
            }
        }









