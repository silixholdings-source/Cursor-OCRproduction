"""
Contact Form Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import logging
import re
from pydantic import BaseModel, EmailStr, field_validator
from core.advanced_rate_limiting import rate_limit
from core.database import get_db
from src.models.contact import ContactSubmission, InquiryType, ContactStatus

router = APIRouter()
logger = logging.getLogger(__name__)

class ContactFormRequest(BaseModel):
    """Contact form request schema"""
    firstName: str
    lastName: str
    email: EmailStr
    company: str = ""
    subject: str = ""
    inquiryType: str
    message: str
    preferredDate: str = ""
    preferredTime: str = ""
    timezone: str = ""
    attendees: str = ""
    
    @field_validator('firstName', 'lastName')
    @classmethod
    def validate_names(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v.strip()) > 50:
            raise ValueError('Name must be less than 50 characters')
        return v.strip()
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters long')
        if len(v.strip()) > 2000:
            raise ValueError('Message must be less than 2000 characters')
        return v.strip()
    
    @field_validator('inquiryType')
    @classmethod
    def validate_inquiry_type(cls, v):
        valid_types = ['demo', 'general', 'sales', 'support', 'billing', 'partnership', 'other']
        if v not in valid_types:
            raise ValueError(f'Invalid inquiry type. Must be one of: {valid_types}')
        return v
    
    @field_validator('attendees')
    @classmethod
    def validate_attendees(cls, v, values):
        if values.get('inquiryType') == 'demo':
            if not v:
                raise ValueError('Number of attendees is required for demo scheduling')
            try:
                attendees = int(v)
                if attendees < 1 or attendees > 20:
                    raise ValueError('Number of attendees must be between 1 and 20')
            except ValueError:
                raise ValueError('Invalid number of attendees')
        return v

@router.post("/")
@rate_limit("contact_form")
async def submit_contact_form(
    form_data: ContactFormRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Submit contact form with comprehensive validation and security"""
    try:
        # Additional security checks
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Check for potential spam patterns
        spam_indicators = [
            len(form_data.message) > 1000 and form_data.message.count('http') > 3,
            form_data.email.endswith('.tk') or form_data.email.endswith('.ml'),
            any(word in form_data.message.lower() for word in ['viagra', 'casino', 'lottery', 'winner'])
        ]
        
        if any(spam_indicators):
            logger.warning(f"Potential spam detected from {client_ip}: {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message appears to be spam and cannot be processed."
            )
        
        # Log the contact form submission
        logger.info(f"Contact form submitted by {form_data.firstName} {form_data.lastName} ({form_data.email}) from {client_ip}")
        
        # Create contact submission record
        contact_submission = ContactSubmission(
            first_name=form_data.firstName,
            last_name=form_data.lastName,
            email=form_data.email,
            company=form_data.company,
            subject=form_data.subject,
            inquiry_type=InquiryType(form_data.inquiryType),
            message=form_data.message,
            preferred_date=form_data.preferredDate,
            preferred_time=form_data.preferredTime,
            timezone=form_data.timezone,
            attendees=form_data.attendees,
            status=ContactStatus.RECEIVED,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        # Save to database
        try:
            db.add(contact_submission)
            db.commit()
            db.refresh(contact_submission)
        except Exception as db_error:
            db.rollback()
            logger.error(f"Database error saving contact submission: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save contact submission. Please try again."
            )
        
        # Generate contact ID for response
        contact_id = f"CONTACT-{contact_submission.id}"
        
        # TODO: In production, implement:
        # 1. Send email notification to support team
        # 2. Send confirmation email to user
        # 3. Create support ticket if needed
        # 4. Schedule demo if inquiry type is 'demo'
        
        # Determine response message based on inquiry type
        if form_data.inquiryType == 'demo':
            message = "Thank you for requesting a demo! Our sales team will contact you within 24 hours to schedule your personalized walkthrough."
        elif form_data.inquiryType == 'sales':
            message = "Thank you for your sales inquiry! Our sales team will contact you within 24 hours to discuss your needs."
        elif form_data.inquiryType == 'support':
            message = "Thank you for contacting support! Our technical team will respond to your inquiry within 24 hours."
        else:
            message = "Thank you for your message! We'll get back to you within 24 hours."
        
        return {
            "status": "success",
            "message": message,
            "contact_id": contact_id,
            "submitted_at": contact_submission.created_at.isoformat(),
            "inquiry_type": form_data.inquiryType
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit contact form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit contact form. Please try again or contact us directly."
        )

@router.get("/inquiry-types")
async def get_inquiry_types():
    """Get available inquiry types for contact form"""
    return {
        "inquiry_types": [
            {"value": "general", "label": "General Inquiry"},
            {"value": "sales", "label": "Sales Inquiry"},
            {"value": "support", "label": "Technical Support"},
            {"value": "demo", "label": "Request Demo"},
            {"value": "partnership", "label": "Partnership"},
            {"value": "billing", "label": "Billing Question"},
            {"value": "feedback", "label": "Feedback"}
        ]
    }

