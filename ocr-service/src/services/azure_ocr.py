"""
Azure Form Recognizer OCR Service
"""
import logging
from typing import Dict, Any, List
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError

from .ocr_processor import OCRProcessor

logger = logging.getLogger(__name__)

class AzureOCRService(OCRProcessor):
    """Azure Form Recognizer OCR service"""
    
    def __init__(self, endpoint: str, key: str, confidence_threshold: float = 0.8):
        super().__init__(confidence_threshold)
        
        if not endpoint or not key:
            raise ValueError("Azure Form Recognizer credentials not provided")
        
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        logger.info("Azure OCR Service initialized")
    
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
            if not self.validate_confidence_scores(extracted_data.get("confidence_scores", {})):
                logger.warning("Low confidence scores detected")
            
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
                "extraction_method": "azure_form_recognizer",
                "timestamp": None
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
            extracted_data["confidence_scores"]["line_items"] = 0.9
        
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









