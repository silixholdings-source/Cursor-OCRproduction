"""
Email Processing Service for handling incoming invoice attachments.
This service monitors a dedicated email inbox, extracts attachments,
and triggers the invoice processing workflow.
"""
import logging
import asyncio
import email
from email import policy
from email.header import decode_header
import imaplib
import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

from sqlalchemy.orm import Session

from core.config import settings
from src.models.company import Company
from src.models.user import User
from src.models.invoice import InvoiceType
from services.invoice_processor import InvoiceProcessor

logger = logging.getLogger(__name__)

class EmailProcessorService:
    """Monitors email inbox for invoice attachments and processes them."""

    def __init__(self):
        self.invoice_processor = InvoiceProcessor()
        self.email_host = getattr(settings, 'INVOICE_EMAIL_IMAP_HOST', None)
        self.email_port = getattr(settings, 'INVOICE_EMAIL_IMAP_PORT', 993)
        self.email_user = getattr(settings, 'INVOICE_EMAIL_USER', None)
        self.email_password = getattr(settings, 'INVOICE_EMAIL_PASSWORD', None)
        self.attachment_dir = Path(settings.UPLOAD_DIR)
        self.supported_attachment_types = getattr(settings, 'ALLOWED_FILE_TYPES', ['.pdf', '.jpg', '.jpeg', '.png', '.tiff'])

        if not self.attachment_dir.exists():
            self.attachment_dir.mkdir(parents=True, exist_ok=True)

    async def check_and_process_emails(self, db: Session):
        """Check for new emails and process invoice attachments."""
        if not all([self.email_host, self.email_user, self.email_password]):
            logger.warning("Email processing credentials not configured. Skipping email check.")
            return

        logger.info("Checking for new invoice emails...")
        try:
            mail = imaplib.IMAP4_SSL(self.email_host, self.email_port)
            mail.login(self.email_user, self.email_password)
            mail.select("inbox")

            status, email_ids = mail.search(None, "UNSEEN")
            if status != "OK":
                logger.error(f"Failed to search emails: {status}")
                return

            for email_id in email_ids[0].split():
                await self._process_single_email(mail, email_id, db)

            mail.logout()
            logger.info("Finished checking invoice emails.")

        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP connection or login failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during email processing: {e}", exc_info=True)

    async def _process_single_email(self, mail: imaplib.IMAP4_SSL, email_id: bytes, db: Session):
        """Process a single email and extract attachments."""
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            logger.error(f"Failed to fetch email {email_id}: {status}")
            return

        msg = email.message_from_bytes(msg_data[0][1], policy=policy.default)

        # Get sender and recipient
        sender_email = msg.get("From")
        recipient_email = msg.get("To")

        # Find company and user for this email
        company_id, user_id = await self._find_company_and_user(db, recipient_email, sender_email)
        
        if not company_id or not user_id:
            logger.warning(f"Could not find company/user for email {email_id}. Skipping.")
            return

        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")

        logger.info(f"Processing email from '{sender_email}' with subject '{subject}'")

        attachments_found = False
        for part in msg.walk():
            if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if filename:
                decoded_filename, encoding = decode_header(filename)[0]
                if isinstance(decoded_filename, bytes):
                    decoded_filename = decoded_filename.decode(encoding if encoding else "utf-8")

                file_extension = Path(decoded_filename).suffix.lower()
                if file_extension in self.supported_attachment_types:
                    attachments_found = True
                    unique_filename = f"{uuid.uuid4()}{file_extension}"
                    file_path = self.attachment_dir / unique_filename

                    try:
                        with open(file_path, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        logger.info(f"Downloaded attachment: {decoded_filename} to {file_path}")

                        # Trigger invoice processing
                        processing_result = await self.invoice_processor.process_invoice(
                            file_path=str(file_path),
                            company_id=company_id,
                            user_id=user_id,
                            db=db
                        )
                        logger.info(f"Invoice processing result: {processing_result['status']}")

                    except Exception as e:
                        logger.error(f"Error processing attachment {decoded_filename}: {e}", exc_info=True)
                    finally:
                        if file_path.exists():
                            file_path.unlink()

        if not attachments_found:
            logger.info(f"No supported invoice attachments found in email from '{sender_email}'.")

        # Mark email as read
        mail.store(email_id, "+FLAGS", "\\Seen")

    async def _find_company_and_user(self, db: Session, recipient_email: str, sender_email: str) -> tuple[Optional[str], Optional[str]]:
        """Find company and user based on email addresses."""
        # For now, use the first available company and user
        # In a real system, this would map email addresses to companies
        default_company = db.query(Company).first()
        default_user = db.query(User).filter(User.company_id == default_company.id).first() if default_company else None

        if not default_company or not default_user:
            return None, None

        return str(default_company.id), str(default_user.id)

    async def start_email_monitoring(self, db: Session):
        """Start continuous email monitoring."""
        logger.info("Starting email monitoring service...")
        
        while True:
            try:
                await self.check_and_process_emails(db)
                await asyncio.sleep(settings.EMAIL_CHECK_INTERVAL_MINUTES * 60)
            except Exception as e:
                logger.error(f"Error in email monitoring: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute before retrying