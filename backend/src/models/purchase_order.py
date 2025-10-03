"""
Purchase Order Model for ERP Integration
Supports Dynamics GP, SAP, Oracle, and other ERP systems
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey, JSON, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from src.core.database import Base

class POStatus(str, enum.Enum):
    """Purchase Order Status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    PARTIALLY_RECEIVED = "partially_received"
    FULLY_RECEIVED = "fully_received"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class POType(str, enum.Enum):
    """Purchase Order Type"""
    STANDARD = "standard"
    BLANKET = "blanket"
    CONTRACT = "contract"
    PLANNED = "planned"
    SERVICES = "services"

class PurchaseOrder(Base):
    """Purchase Order model for ERP integration"""
    __tablename__ = "purchase_orders"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # PO identification
    po_number = Column(String(50), nullable=False, unique=True, index=True)
    external_po_id = Column(String(100), nullable=True)  # ERP system PO ID
    
    # Company and vendor information
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    vendor_id = Column(String(50), nullable=False)
    vendor_name = Column(String(255), nullable=False)
    vendor_contact = Column(String(255), nullable=True)
    
    # PO details
    po_date = Column(DateTime(timezone=True), nullable=False)
    required_date = Column(DateTime(timezone=True), nullable=True)
    promised_date = Column(DateTime(timezone=True), nullable=True)
    
    # Financial information
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)
    freight_amount = Column(Numeric(15, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Status and type
    status = Column(Enum(POStatus), default=POStatus.DRAFT, nullable=False)
    po_type = Column(Enum(POType), default=POType.STANDARD, nullable=False)
    
    # Shipping information
    ship_to_address = Column(Text, nullable=True)
    ship_to_contact = Column(String(255), nullable=True)
    shipping_method = Column(String(100), nullable=True)
    
    # Terms and conditions
    payment_terms = Column(String(100), nullable=True)
    freight_terms = Column(String(100), nullable=True)
    
    # ERP integration fields
    erp_system = Column(String(50), nullable=True)  # GP, SAP, Oracle, etc.
    erp_company_db = Column(String(50), nullable=True)  # GP company database
    erp_document_id = Column(String(100), nullable=True)
    erp_last_sync = Column(DateTime(timezone=True), nullable=True)
    erp_sync_status = Column(String(20), nullable=True)
    
    # Additional fields
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Approval workflow
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Custom fields for ERP-specific data
    custom_fields = Column(JSON, default=dict, nullable=False)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("src.models.company.Company")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    line_items = relationship("POLine", back_populates="purchase_order", cascade="all, delete-orphan")
    receipts = relationship("src.models.receipt.Receipt", back_populates="purchase_order")
    
    def __repr__(self):
        return f"<PurchaseOrder(po_number='{self.po_number}', vendor='{self.vendor_name}', total={self.total_amount})>"
    
    @property
    def is_approved(self) -> bool:
        """Check if PO is approved"""
        return self.status in [POStatus.APPROVED, POStatus.SENT, POStatus.ACKNOWLEDGED, 
                              POStatus.PARTIALLY_RECEIVED, POStatus.FULLY_RECEIVED]
    
    @property
    def can_receive(self) -> bool:
        """Check if PO can receive goods"""
        return self.status in [POStatus.SENT, POStatus.ACKNOWLEDGED, POStatus.PARTIALLY_RECEIVED]
    
    @property
    def is_closed(self) -> bool:
        """Check if PO is closed"""
        return self.status in [POStatus.CLOSED, POStatus.CANCELLED]
    
    def calculate_totals(self):
        """Calculate PO totals from line items"""
        if self.line_items:
            self.subtotal = sum(line.extended_cost for line in self.line_items)
            self.total_amount = self.subtotal + self.tax_amount + self.freight_amount

class POLine(Base):
    """Purchase Order Line Item"""
    __tablename__ = "po_lines"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # PO relationship
    po_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    # Item information
    item_number = Column(String(100), nullable=True)
    item_description = Column(Text, nullable=False)
    vendor_item_number = Column(String(100), nullable=True)
    
    # Quantities
    quantity_ordered = Column(Numeric(15, 4), nullable=False)
    quantity_received = Column(Numeric(15, 4), nullable=False, default=0)
    quantity_invoiced = Column(Numeric(15, 4), nullable=False, default=0)
    unit_of_measure = Column(String(20), nullable=True)
    
    # Pricing
    unit_cost = Column(Numeric(15, 4), nullable=False)
    extended_cost = Column(Numeric(15, 2), nullable=False)
    
    # Dates
    required_date = Column(DateTime(timezone=True), nullable=True)
    promised_date = Column(DateTime(timezone=True), nullable=True)
    
    # GL and project information
    gl_account = Column(String(50), nullable=True)
    cost_center = Column(String(50), nullable=True)
    project_code = Column(String(50), nullable=True)
    
    # ERP integration
    erp_line_id = Column(String(100), nullable=True)
    custom_fields = Column(JSON, default=dict, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="line_items")
    receipt_lines = relationship("ReceiptLine", back_populates="po_line")
    
    def __repr__(self):
        return f"<POLine(line_number={self.line_number}, item='{self.item_description}', qty={self.quantity_ordered})>"
    
    @property
    def quantity_remaining(self) -> Numeric:
        """Calculate remaining quantity to receive"""
        return self.quantity_ordered - self.quantity_received
    
    @property
    def is_fully_received(self) -> bool:
        """Check if line is fully received"""
        return self.quantity_received >= self.quantity_ordered
    
    @property
    def receive_percentage(self) -> float:
        """Calculate percentage received"""
        if self.quantity_ordered == 0:
            return 0.0
        return float(self.quantity_received / self.quantity_ordered * 100)
