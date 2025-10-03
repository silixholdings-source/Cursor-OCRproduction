"""
Contact Form Model
"""
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from datetime import datetime
from src.core.database import Base

class InquiryType(str, enum.Enum):
    """Contact form inquiry types"""
    DEMO = "demo"
    GENERAL = "general"
    SALES = "sales"
    SUPPORT = "support"
    BILLING = "billing"
    PARTNERSHIP = "partnership"
    OTHER = "other"

class ContactStatus(str, enum.Enum):
    """Contact form status"""
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ContactSubmission(Base):
    """Contact form submission model"""
    __tablename__ = "contact_submissions"
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Contact information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    company = Column(String(100), nullable=True)
    subject = Column(String(200), nullable=True)
    
    # Inquiry details
    inquiry_type = Column(Enum(InquiryType), nullable=False, default=InquiryType.GENERAL)
    message = Column(Text, nullable=False)
    
    # Demo scheduling fields
    preferred_date = Column(String(20), nullable=True)
    preferred_time = Column(String(20), nullable=True)
    timezone = Column(String(50), nullable=True)
    attendees = Column(String(10), nullable=True)
    
    # Status and tracking
    status = Column(Enum(ContactStatus), nullable=False, default=ContactStatus.RECEIVED)
    client_ip = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Internal notes (for support team)
    internal_notes = Column(Text, nullable=True)
    assigned_to = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<ContactSubmission(id={self.id}, email={self.email}, type={self.inquiry_type})>"
    
    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_demo_request(self):
        """Check if this is a demo request"""
        return self.inquiry_type == InquiryType.DEMO
    
    @property
    def is_urgent(self):
        """Check if this inquiry is urgent"""
        return self.inquiry_type in [InquiryType.SUPPORT, InquiryType.BILLING]
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'company': self.company,
            'subject': self.subject,
            'inquiry_type': self.inquiry_type.value,
            'message': self.message,
            'preferred_date': self.preferred_date,
            'preferred_time': self.preferred_time,
            'timezone': self.timezone,
            'attendees': self.attendees,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

