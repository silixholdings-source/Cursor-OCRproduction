"""
OCR Client - Communicates with OCR microservice
"""
import logging
import httpx
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import os

from core.config import settings

logger = logging.getLogger(__name__)

class OCRClient:
    """Client for communicating with OCR microservice"""
    
    def __init__(self):
        self.base_url = settings.OCR_SERVICE_URL or "http://localhost:8001"
        self.timeout = 30.0
        logger.info(f"OCR Client initialized with URL: {self.base_url}")
    
    async def extract_invoice(self, file_path: str, company_id: str) -> Dict[str, Any]:
        """Extract invoice data using OCR microservice"""
        logger.info(f"Sending file to OCR service: {file_path}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Read file
                with open(file_path, "rb") as f:
                    file_content = f.read()
                
                # Prepare file for upload
                files = {"file": (Path(file_path).name, file_content, "application/octet-stream")}
                data = {"company_id": company_id}
                
                # Send request to OCR service
                response = await client.post(
                    f"{self.base_url}/process",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        return result.get("data", {})
                    else:
                        raise Exception(f"OCR processing failed: {result.get('message', 'Unknown error')}")
                else:
                    raise Exception(f"OCR service error: {response.status_code} - {response.text}")
                    
        except httpx.TimeoutException:
            logger.error("OCR service timeout")
            raise Exception("OCR service timeout")
        except httpx.ConnectError:
            logger.error("Cannot connect to OCR service")
            raise Exception("OCR service unavailable")
        except Exception as e:
            logger.error(f"OCR client error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if OCR service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"OCR health check failed: {e}")
            return False









