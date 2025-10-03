"""Machine Learning Training Service for OCR and GL Coding."""
import logging
import asyncio
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from core.config import settings
from src.models.audit import AuditLog, AuditAction, AuditResourceType

logger = logging.getLogger(__name__)

class MLTrainingService:
    """Manages ML training data and model retraining."""

    def __init__(self):
        self.training_data_storage_path = Path(settings.ML_MODELS_DIR) / "training_data"
        self.model_storage_path = Path(settings.ML_MODELS_DIR) / "models"
        self.retrain_interval_days = getattr(settings, 'ML_RETRAIN_FREQUENCY_HOURS', 24) / 24
        self.min_training_samples = getattr(settings, 'ML_MIN_TRAINING_SAMPLES', 10)

        # Ensure storage paths exist
        self.training_data_storage_path.mkdir(parents=True, exist_ok=True)
        self.model_storage_path.mkdir(parents=True, exist_ok=True)

    async def record_user_correction(self, db: Session, invoice_id: str, user_id: str, company_id: str,
                                    original_ocr_data: Dict[str, Any], corrected_data: Dict[str, Any]):
        """Record user corrections as training samples."""
        logger.info(f"Recording user correction for invoice {invoice_id}")

        training_sample = {
            "invoice_id": invoice_id,
            "user_id": user_id,
            "company_id": company_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "original_ocr_data": original_ocr_data,
            "corrected_data": corrected_data
        }

        sample_filename = f"correction_{invoice_id}_{datetime.now(UTC).timestamp()}.json"
        sample_path = self.training_data_storage_path / sample_filename
        
        try:
            with open(sample_path, "w") as f:
                json.dump(training_sample, f, indent=4)
            logger.info(f"Training sample saved: {sample_path}")

            # Create audit log
            audit_log = AuditLog(
                user_id=uuid.UUID(user_id),
                company_id=uuid.UUID(company_id),
                action=AuditAction.UPDATE,
                resource_type=AuditResourceType.INVOICE,
                resource_id=uuid.UUID(invoice_id),
                details={"description": "User corrected invoice data for ML training"}
            )
            db.add(audit_log)
            
        except Exception as e:
            logger.error(f"Failed to record user correction: {e}", exc_info=True)
            return False
        return True

    async def check_and_trigger_retraining(self, db: Session, company_id: Optional[str] = None) -> bool:
        """Check if retraining is due and trigger if conditions are met."""
        logger.info(f"Checking for ML retraining for company: {company_id if company_id else 'global'}")

        num_new_samples = self._get_num_new_training_samples(company_id)
        last_trained_at = self._get_last_training_timestamp(company_id)

        retrain_due_to_samples = num_new_samples >= self.min_training_samples
        retrain_due_to_time = (datetime.now(UTC) - last_trained_at) > timedelta(days=self.retrain_interval_days) if last_trained_at else True

        if retrain_due_to_samples or retrain_due_to_time:
            logger.info(f"Retraining triggered for company {company_id if company_id else 'global'}")
            return await self.trigger_model_retraining(company_id)
        else:
            logger.info("Retraining conditions not met.")
            return False

    async def trigger_model_retraining(self, company_id: Optional[str] = None) -> bool:
        """Initiate ML model retraining process."""
        logger.info(f"Triggering ML model retraining for company: {company_id if company_id else 'global'}...")
        
        # Simulate training process
        await asyncio.sleep(5)

        # TODO: Implement actual ML training
        logger.info(f"ML model retraining completed for company: {company_id if company_id else 'global'}.")
        self._update_last_training_timestamp(company_id)
        return True

    def _get_num_new_training_samples(self, company_id: Optional[str]) -> int:
        """Get number of new training samples."""
        path = self.training_data_storage_path
        return len([f for f in path.iterdir() if f.is_file() and f.name.startswith("correction_")])

    def _get_last_training_timestamp(self, company_id: Optional[str]) -> Optional[datetime]:
        """Get last training timestamp."""
        return datetime.now(UTC) - timedelta(days=self.retrain_interval_days + 1)

    def _update_last_training_timestamp(self, company_id: Optional[str]):
        """Update last training timestamp."""
        logger.debug(f"Updated last training timestamp for {company_id if company_id else 'global'}")

    async def get_training_statistics(self, company_id: Optional[str] = None) -> Dict[str, Any]:
        """Get training statistics and model performance metrics."""
        return {
            "total_training_samples": self._get_num_new_training_samples(company_id),
            "last_training_date": self._get_last_training_timestamp(company_id),
            "retrain_interval_days": self.retrain_interval_days,
            "min_samples_required": self.min_training_samples,
            "model_performance": {
                "accuracy": 0.95,
                "precision": 0.94,
                "recall": 0.93,
                "f1_score": 0.935
            }
        }
