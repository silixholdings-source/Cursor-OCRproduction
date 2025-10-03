"""
OCR Service for invoice processing using Azure Form Recognizer
"""
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
from datetime import datetime, UTC

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError

from core.config import settings
from src.models.invoice import Invoice
from src.models.invoice_line import InvoiceLine
from src.models.audit import AuditLog, AuditAction, AuditResourceType

logger = logging.getLogger(__name__)

class MockOCRService:
    """Mock OCR service for testing and development"""
    
    def __init__(self):
        self.confidence_threshold = settings.OCR_CONFIDENCE_THRESHOLD
    
    async def extract_invoice(self, file_path: str, company_id: str) -> Dict[str, Any]:
        """Mock invoice extraction for testing"""
        logger.info(f"Mock OCR processing file: {file_path}")
        
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Return mock extracted data with recent dates
        from datetime import datetime, timedelta
        recent_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        import uuid
        unique_id = str(uuid.uuid4())[:8].upper()
        return {
            "supplier_name": f"Mock Supplier Corp {unique_id}",
            "invoice_number": f"MOCK-{unique_id}",
            "invoice_date": recent_date,
            "due_date": due_date,
            "total_amount": 1500.00,
            "currency": "USD",
            "tax_amount": 120.00,
            "tax_rate": 0.08,
            "subtotal": 1500.00,
            "total_with_tax": 1620.00,
            "line_items": [
                {
                    "description": "Software License",
                    "quantity": 1,
                    "unit_price": 1000.00,
                    "total": 1000.00,
                    "gl_account": "6000"
                },
                {
                    "description": "Implementation Services",
                    "quantity": 10,
                    "unit_price": 50.00,
                    "total": 500.00,
                    "gl_account": "6500"
                }
            ],
            "confidence_scores": {
                "supplier_name": 0.95,
                "invoice_number": 0.98,
                "total_amount": 0.99,
                "line_items": 0.92
            },
            "processing_metadata": {
                "provider": "mock",
                "processing_time_ms": 100,
                "file_size_bytes": 1024,
                "extraction_method": "mock"
            }
        }

class AzureOCRService:
    """Azure Form Recognizer OCR service"""
    
    def __init__(self):
        if not settings.AZURE_FORM_RECOGNIZER_ENDPOINT or not settings.AZURE_FORM_RECOGNIZER_KEY:
            raise ValueError("Azure Form Recognizer credentials not configured")
        
        self.client = DocumentAnalysisClient(
            endpoint=settings.AZURE_FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_FORM_RECOGNIZER_KEY)
        )
        self.confidence_threshold = settings.OCR_CONFIDENCE_THRESHOLD
    
    async def extract_invoice(self, file_path: str, company_id: str) -> Dict[str, Any]:
        """Extract invoice data using Azure Form Recognizer"""
        logger.info(f"Processing invoice with Azure OCR: {file_path}")
        
        try:
            with open(file_path, "rb") as document:
                poller = await self.client.begin_analyze_document(
                    "prebuilt-invoice", document
                )
                result = await poller.result()
            
            # Extract invoice data
            extracted_data = self._parse_azure_result(result)
            
            # Validate confidence scores
            self._validate_confidence_scores(extracted_data.get("confidence_scores", {}))
            
            logger.info(f"Successfully extracted invoice data: {extracted_data.get('invoice_number')}")
            return extracted_data
            
        except AzureError as e:
            logger.error(f"Azure OCR error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OCR processing: {e}")
            raise
    
    def _parse_azure_result(self, result) -> Dict[str, Any]:
        """Parse Azure Form Recognizer result into structured data"""
        extracted_data = {
            "supplier_name": "",
            "invoice_number": "",
            "invoice_date": "",
            "due_date": "",
            "total_amount": 0.0,
            "currency": "USD",
            "tax_amount": 0.0,
            "tax_rate": 0.0,
            "subtotal": 0.0,
            "total_with_tax": 0.0,
            "line_items": [],
            "confidence_scores": {},
            "processing_metadata": {
                "provider": "azure",
                "processing_time_ms": 0,
                "extraction_method": "azure_form_recognizer"
            }
        }
        
        # Extract basic invoice information
        for field in result.fields:
            field_name = field.key.content if field.key else ""
            field_value = field.value.content if field.value else ""
            confidence = field.confidence if hasattr(field, 'confidence') else 1.0
            
            if field_name.lower() in ["vendor name", "supplier name", "bill from"]:
                extracted_data["supplier_name"] = field_value
                extracted_data["confidence_scores"]["supplier_name"] = confidence
            elif field_name.lower() in ["invoice number", "invoice id", "invoice #"]:
                extracted_data["invoice_number"] = field_value
                extracted_data["confidence_scores"]["invoice_number"] = confidence
            elif field_name.lower() in ["invoice date", "date", "bill date"]:
                extracted_data["invoice_date"] = field_value
                extracted_data["confidence_scores"]["invoice_date"] = confidence
            elif field_name.lower() in ["due date", "payment due date"]:
                extracted_data["due_date"] = field_value
                extracted_data["confidence_scores"]["due_date"] = confidence
            elif field_name.lower() in ["total", "amount due", "total amount"]:
                try:
                    extracted_data["total_amount"] = float(field_value.replace("$", "").replace(",", ""))
                    extracted_data["confidence_scores"]["total_amount"] = confidence
                except ValueError:
                    logger.warning(f"Could not parse total amount: {field_value}")
        
        # Extract line items if available
        if hasattr(result, 'tables') and result.tables:
            extracted_data["line_items"] = self._extract_line_items(result.tables)
            extracted_data["confidence_scores"]["line_items"] = 0.9  # Default confidence for line items
        
        # Calculate derived fields
        extracted_data["subtotal"] = extracted_data["total_amount"]
        extracted_data["total_with_tax"] = extracted_data["total_amount"] + extracted_data["tax_amount"]
        
        return extracted_data
    
    def _extract_line_items(self, tables) -> List[Dict[str, Any]]:
        """Extract line items from table data"""
        line_items = []
        
        for table in tables:
            # Look for table with line item data
            if table.row_count > 1:  # More than header row
                for row in table.rows[1:]:  # Skip header
                    if len(row.cells) >= 3:  # At least description, quantity, price
                        line_item = {
                            "description": row.cells[0].content if row.cells[0] else "",
                            "quantity": 1.0,
                            "unit_price": 0.0,
                            "total": 0.0,
                            "gl_account": ""
                        }
                        
                        # Try to extract quantity and price
                        if len(row.cells) > 1 and row.cells[1].content:
                            try:
                                line_item["quantity"] = float(row.cells[1].content)
                            except ValueError:
                                pass
                        
                        if len(row.cells) > 2 and row.cells[2].content:
                            try:
                                line_item["unit_price"] = float(row.cells[2].content.replace("$", "").replace(",", ""))
                                line_item["total"] = line_item["quantity"] * line_item["unit_price"]
                            except ValueError:
                                pass
                        
                        line_items.append(line_item)
        
        return line_items
    
    def _validate_confidence_scores(self, confidence_scores: Dict[str, float]):
        """Validate that confidence scores meet minimum thresholds"""
        critical_fields = ["supplier_name", "invoice_number", "total_amount"]
        
        for field in critical_fields:
            if field in confidence_scores:
                confidence = confidence_scores[field]
                if confidence < self.confidence_threshold:
                    logger.warning(f"Low confidence for {field}: {confidence} < {self.confidence_threshold}")

class OCRService:
    """Main OCR service that delegates to appropriate provider"""
    
    def __init__(self):
        if settings.OCR_PROVIDER == "azure":
            try:
                self.provider = AzureOCRService()
            except ValueError:
                logger.warning("Azure OCR not available, falling back to mock")
                self.provider = MockOCRService()
        elif settings.OCR_PROVIDER == "advanced":
            # Use advanced mock service for development
            self.provider = MockOCRService()
        else:
            self.provider = MockOCRService()
    
    async def extract_invoice(self, file_path: str, company_id: str) -> Dict[str, Any]:
        """Extract invoice data using configured OCR provider"""
        start_time = datetime.now(UTC)
        
        try:
            result = await self.provider.extract_invoice(file_path, company_id)
            
            # Add processing metadata
            processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            if "processing_metadata" not in result:
                result["processing_metadata"] = {}
            result["processing_metadata"]["processing_time_ms"] = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise
    
    async def validate_extraction(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data and return validation results"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "overall_confidence": 0.0
        }
        
        # Check required fields
        required_fields = ["supplier_name", "invoice_number", "total_amount"]
        for field in required_fields:
            if not extracted_data.get(field):
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Check confidence scores
        confidence_scores = extracted_data.get("confidence_scores", {})
        if confidence_scores:
            total_confidence = sum(confidence_scores.values())
            avg_confidence = total_confidence / len(confidence_scores)
            validation_result["overall_confidence"] = avg_confidence
            
            if avg_confidence < self.provider.confidence_threshold:
                validation_result["warnings"].append(f"Low overall confidence: {avg_confidence:.2f}")
        
        # Check line items
        line_items = extracted_data.get("line_items", [])
        if not line_items:
            validation_result["warnings"].append("No line items extracted")
        
        return validation_result
