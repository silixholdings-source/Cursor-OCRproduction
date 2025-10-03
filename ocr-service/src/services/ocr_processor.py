"""
OCR Processor - Abstract base class for OCR implementations
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class OCRProcessor(ABC):
    """Abstract base class for OCR processors"""
    
    def __init__(self, confidence_threshold: float = 0.8):
        self.confidence_threshold = confidence_threshold
    
    @abstractmethod
    async def extract_invoice(self, file_path: str, company_id: str) -> Dict[str, Any]:
        """Extract invoice data from document"""
        pass
    
    def validate_confidence_scores(self, confidence_scores: Dict[str, float]) -> bool:
        """Validate confidence scores meet threshold"""
        if not confidence_scores:
            return False
        
        critical_fields = ["supplier_name", "invoice_number", "total_amount"]
        for field in critical_fields:
            if field in confidence_scores:
                if confidence_scores[field] < self.confidence_threshold:
                    logger.warning(f"Low confidence for {field}: {confidence_scores[field]}")
                    return False
        
        return True









