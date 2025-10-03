"""Advanced OCR Service for comprehensive invoice data extraction and AI/ML integration."""
import logging
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import hashlib
import re

from core.config import settings
from src.models.invoice import InvoiceType
from services.ocr import MockOCRService, AzureOCRService

logger = logging.getLogger(__name__)

class AdvancedOCRService:
    """Advanced OCR service with AI/ML capabilities and multi-provider support."""

    def __init__(self):
        self.primary_ocr_provider = self._initialize_primary_ocr_provider()
        self.confidence_threshold = settings.OCR_CONFIDENCE_THRESHOLD
        self.min_line_item_confidence = 0.7
        self.training_data_path = Path(settings.ML_MODELS_DIR) / "training_data"
        self.training_data_path.mkdir(parents=True, exist_ok=True)

    def _initialize_primary_ocr_provider(self):
        """Initialize primary OCR provider."""
        if settings.OCR_PROVIDER == "azure":
            try:
                return AzureOCRService()
            except Exception as e:
                logger.warning(f"Azure OCR not configured, using mock: {e}")
                return MockOCRService()
        else:
            return MockOCRService()

    async def extract_invoice_data(self, file_path: str, company_id: str, 
                                 invoice_type: InvoiceType = InvoiceType.INVOICE) -> Dict[str, Any]:
        """Extract comprehensive invoice data with advanced processing."""
        logger.info(f"Advanced OCR processing: {file_path} for company {company_id}")
        
        try:
            # Primary OCR Extraction
            primary_result = await self.primary_ocr_provider.extract_invoice(file_path, company_id)
            
            # Post-processing and enrichment
            processed_data = await self._post_process_extraction(primary_result, invoice_type, company_id)
            
            # Validate confidence scores
            self._validate_extracted_data_confidence(processed_data)
            
            # Generate final result
            final_result = {
                **processed_data,
                "processing_timestamp": datetime.now(UTC).isoformat(),
                "ocr_provider": settings.OCR_PROVIDER,
                "confidence_score": self._calculate_overall_confidence(processed_data)
            }
            
            logger.info(f"Successfully extracted data for {final_result.get('invoice_number')}")
            return final_result
            
        except Exception as e:
            logger.error(f"Advanced OCR extraction failed: {e}", exc_info=True)
            raise

    async def _post_process_extraction(self, ocr_result: Dict[str, Any], 
                                     invoice_type: InvoiceType, company_id: str) -> Dict[str, Any]:
        """Post-process OCR results with normalization and validation."""
        processed_data = ocr_result.copy()
        
        # Normalize dates
        processed_data = await self._normalize_dates(processed_data)
        
        # Normalize currency amounts
        processed_data = await self._normalize_currency(processed_data)
        
        # Handle utility bill specific fields
        if invoice_type == InvoiceType.INVOICE:
            processed_data = await self._process_utility_bill_fields(processed_data)
        
        # Process line items
        if "line_items" not in processed_data:
            processed_data["line_items"] = []
        
        processed_data["line_items"] = await self._process_line_items(processed_data["line_items"])
        processed_data["invoice_type"] = invoice_type.value
        
        return processed_data

    async def _normalize_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize date formats."""
        date_fields = ["invoice_date", "due_date", "service_period_start", "service_period_end"]
        
        for field in date_fields:
            if field in data and isinstance(data[field], str):
                try:
                    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                        try:
                            data[field] = datetime.strptime(data[field], fmt).date()
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    logger.warning(f"Could not parse date field {field}: {data[field]}")
        
        return data

    async def _normalize_currency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize currency amounts."""
        currency_fields = ["total_amount", "subtotal", "tax_amount", "discount_amount"]
        
        for field in currency_fields:
            if field in data and isinstance(data[field], str):
                amount_str = re.sub(r'[^\d.,]', '', data[field])
                try:
                    data[field] = float(amount_str.replace(',', ''))
                except ValueError:
                    logger.warning(f"Could not parse currency field {field}: {data[field]}")
        
        return data

    async def _process_utility_bill_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process utility bill specific fields."""
        text_content = data.get("raw_text", "").lower()
        
        # Extract service period
        service_period_patterns = [
            r"service\s*period\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s*to\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
            r"billing\s*period\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s*to\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})"
        ]
        
        for pattern in service_period_patterns:
            match = re.search(pattern, text_content)
            if match:
                data["service_period_start"] = match.group(1)
                data["service_period_end"] = match.group(2)
                break
        
        # Extract consumption data
        consumption_patterns = [
            r"consumption\s*:?\s*([0-9,]+\.?[0-9]*)\s*([a-z]+)",
            r"usage\s*:?\s*([0-9,]+\.?[0-9]*)\s*([a-z]+)",
            r"kwh\s*:?\s*([0-9,]+\.?[0-9]*)"
        ]
        
        for pattern in consumption_patterns:
            match = re.search(pattern, text_content)
            if match:
                data["consumption"] = {
                    "value": float(match.group(1).replace(',', '')),
                    "unit": match.group(2) if len(match.groups()) > 1 else "unknown"
                }
                break
        
        return data

    async def _process_line_items(self, line_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate line items."""
        processed_items = []
        
        for item in line_items:
            processed_item = item.copy()
            
            # Add unique ID if not present
            if "id" not in processed_item:
                processed_item["id"] = str(uuid.uuid4())
            
            # Normalize numeric fields
            for field in ["quantity", "unit_price", "total_price"]:
                if field in processed_item and isinstance(processed_item[field], str):
                    try:
                        processed_item[field] = float(processed_item[field].replace(',', ''))
                    except ValueError:
                        processed_item[field] = 0.0
            
            # Calculate total if not present
            if "total_price" not in processed_item and "quantity" in processed_item and "unit_price" in processed_item:
                processed_item["total_price"] = processed_item["quantity"] * processed_item["unit_price"]
            
            # Add confidence score
            if "confidence" not in processed_item:
                processed_item["confidence"] = 0.8
            
            processed_items.append(processed_item)
        
        return processed_items

    def _calculate_overall_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate overall confidence score."""
        confidence_scores = data.get("confidence_scores", {})
        if not confidence_scores:
            return 0.8
        
        weights = {
            "supplier_name": 0.3,
            "invoice_number": 0.2,
            "total_amount": 0.2,
            "invoice_date": 0.15,
            "due_date": 0.15
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for field, weight in weights.items():
            if field in confidence_scores:
                weighted_sum += confidence_scores[field] * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.8

    def _validate_extracted_data_confidence(self, extracted_data: Dict[str, Any]):
        """Validate confidence scores for critical fields."""
        critical_fields = ["supplier_name", "invoice_number", "total_amount", "invoice_date"]
        confidence_scores = extracted_data.get("confidence_scores", {})
        
        for field in critical_fields:
            confidence = confidence_scores.get(field, 0.0)
            if confidence < self.confidence_threshold:
                logger.warning(f"Low confidence for field '{field}': {confidence:.2f}")

    async def train_model(self, invoice_data: Dict[str, Any], user_corrections: Dict[str, Any], 
                         company_id: str) -> bool:
        """Train ML model based on user corrections."""
        logger.info(f"Training ML model for company {company_id}")
        
        try:
            training_sample = {
                "invoice_id": invoice_data.get("invoice_id"),
                "company_id": company_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "original_ocr_data": invoice_data,
                "corrected_data": user_corrections,
                "correction_hash": hashlib.md5(json.dumps(user_corrections, sort_keys=True).encode()).hexdigest()
            }
            
            sample_filename = f"training_sample_{company_id}_{datetime.now(UTC).timestamp()}.json"
            sample_path = self.training_data_path / sample_filename
            
            with open(sample_path, "w") as f:
                json.dump(training_sample, f, indent=2)
            
            logger.info(f"Training sample saved: {sample_path}")
            return True
            
        except Exception as e:
            logger.error(f"ML training failed: {e}", exc_info=True)
            return False

    async def validate_extraction_quality(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extraction quality and provide metrics."""
        quality_metrics = {
            "overall_quality_score": 0.0,
            "field_completeness": 0.0,
            "data_consistency": 0.0,
            "recommendations": []
        }
        
        # Calculate field completeness
        required_fields = ["supplier_name", "invoice_number", "total_amount", "invoice_date"]
        present_fields = [field for field in required_fields if field in extracted_data and extracted_data[field]]
        quality_metrics["field_completeness"] = len(present_fields) / len(required_fields)
        
        # Calculate data consistency
        line_items = extracted_data.get("line_items", [])
        if line_items:
            calculated_total = sum(item.get("total_price", 0) for item in line_items)
            invoice_total = extracted_data.get("total_amount", 0)
            if invoice_total > 0:
                quality_metrics["data_consistency"] = 1.0 - abs(calculated_total - invoice_total) / invoice_total
        
        # Calculate overall quality score
        quality_metrics["overall_quality_score"] = (
            quality_metrics["field_completeness"] * 0.4 +
            quality_metrics["data_consistency"] * 0.4 +
            extracted_data.get("confidence_score", 0.8) * 0.2
        )
        
        # Generate recommendations
        if quality_metrics["field_completeness"] < 0.8:
            quality_metrics["recommendations"].append("Some required fields are missing.")
        
        if quality_metrics["data_consistency"] < 0.9:
            quality_metrics["recommendations"].append("Line item totals don't match invoice total.")
        
        return quality_metrics
