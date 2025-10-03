"""
Receipt/Shipment Model for ERP Integration
Supports Dynamics GP, SAP, Oracle, and other ERP systems
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey, Numeric, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from src.core.database import Base

class ReceiptType(str, enum.Enum):
    """Receipt Type"""
    GOODS_RECEIPT = "goods_receipt"
    SERVICE_RECEIPT = "service_receipt"
    PARTIAL_RECEIPT = "partial_receipt"
    RETURN_RECEIPT = "return_receipt"
    INSPECTION_RECEIPT = "inspection_receipt"

class ReceiptStatus(str, enum.Enum):
    """Receipt Status"""
    PENDING = "pending"
    RECEIVED = "received"
    INSPECTED = "inspected"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    RETURNED = "returned"

class Receipt(Base):
    """Receipt/Shipment model for ERP integration"""
    __tablename__ = "receipts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Receipt identification
    receipt_number = Column(String(50), nullable=False, unique=True, index=True)
    external_receipt_id = Column(String(100), nullable=True)  # ERP system receipt ID
    
    # Related documents
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    po_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=True)
    po_number = Column(String(50), nullable=True, index=True)
    
    # Vendor information
    vendor_id = Column(String(50), nullable=False)
    vendor_name = Column(String(255), nullable=False)
    vendor_packing_slip = Column(String(100), nullable=True)
    
    # Receipt details
    receipt_date = Column(DateTime(timezone=True), nullable=False)
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    expected_date = Column(DateTime(timezone=True), nullable=True)
    
    # Financial information
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)
    freight_amount = Column(Numeric(15, 2), nullable=False, default=0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Status and type
    status = Column(Enum(ReceiptStatus), default=ReceiptStatus.PENDING, nullable=False)
    receipt_type = Column(Enum(ReceiptType), default=ReceiptType.GOODS_RECEIPT, nullable=False)
    
    # Shipping information
    carrier = Column(String(100), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    freight_bill_number = Column(String(100), nullable=True)
    
    # Receiving location
    warehouse_location = Column(String(100), nullable=True)
    dock_door = Column(String(20), nullable=True)
    received_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Quality control
    inspection_required = Column(Boolean, default=False, nullable=False)
    inspected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    inspected_at = Column(DateTime(timezone=True), nullable=True)
    inspection_notes = Column(Text, nullable=True)
    
    # ERP integration fields
    erp_system = Column(String(50), nullable=True)  # GP, SAP, Oracle, etc.
    erp_company_db = Column(String(50), nullable=True)  # GP company database
    erp_document_id = Column(String(100), nullable=True)
    erp_last_sync = Column(DateTime(timezone=True), nullable=True)
    erp_sync_status = Column(String(20), nullable=True)
    
    # Additional fields
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Custom fields for ERP-specific data
    custom_fields = Column(JSON, default=dict, nullable=False)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("src.models.company.Company")
    purchase_order = relationship("src.models.purchase_order.PurchaseOrder", back_populates="receipts")
    creator = relationship("User", foreign_keys=[created_by])
    receiver = relationship("User", foreign_keys=[received_by])
    inspector = relationship("User", foreign_keys=[inspected_by])
    line_items = relationship("ReceiptLine", back_populates="receipt", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Receipt(receipt_number='{self.receipt_number}', vendor='{self.vendor_name}', total={self.total_amount})>"
    
    @property
    def is_complete(self) -> bool:
        """Check if receipt is complete"""
        return self.status in [ReceiptStatus.RECEIVED, ReceiptStatus.ACCEPTED]
    
    @property
    def requires_inspection(self) -> bool:
        """Check if receipt requires inspection"""
        return self.inspection_required and not self.inspected_at
    
    def calculate_totals(self):
        """Calculate receipt totals from line items"""
        if self.line_items:
            self.subtotal = sum(line.extended_cost for line in self.line_items)
            self.total_amount = self.subtotal + self.tax_amount + self.freight_amount

class ReceiptLine(Base):
    """Receipt Line Item"""
    __tablename__ = "receipt_lines"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Receipt relationship
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), nullable=False)
    po_line_id = Column(UUID(as_uuid=True), ForeignKey("po_lines.id"), nullable=True)
    line_number = Column(Integer, nullable=False)
    
    # Item information
    item_number = Column(String(100), nullable=True)
    item_description = Column(Text, nullable=False)
    vendor_item_number = Column(String(100), nullable=True)
    
    # Quantities
    quantity_ordered = Column(Numeric(15, 4), nullable=False, default=0)
    quantity_received = Column(Numeric(15, 4), nullable=False)
    quantity_accepted = Column(Numeric(15, 4), nullable=False, default=0)
    quantity_rejected = Column(Numeric(15, 4), nullable=False, default=0)
    unit_of_measure = Column(String(20), nullable=True)
    
    # Pricing
    unit_cost = Column(Numeric(15, 4), nullable=False)
    extended_cost = Column(Numeric(15, 2), nullable=False)
    
    # Location and lot information
    location = Column(String(100), nullable=True)
    lot_number = Column(String(100), nullable=True)
    serial_numbers = Column(Text, nullable=True)  # JSON array of serial numbers
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    
    # Quality control
    inspection_status = Column(String(20), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
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
    receipt = relationship("Receipt", back_populates="line_items")
    po_line = relationship("POLine", back_populates="receipt_lines")
    
    def __repr__(self):
        return f"<ReceiptLine(line_number={self.line_number}, item='{self.item_description}', qty={self.quantity_received})>"
    
    @property
    def acceptance_percentage(self) -> float:
        """Calculate acceptance percentage"""
        if self.quantity_received == 0:
            return 0.0
        return float(self.quantity_accepted / self.quantity_received * 100)
    
    @property
    def rejection_percentage(self) -> float:
        """Calculate rejection percentage"""
        if self.quantity_received == 0:
            return 0.0
        return float(self.quantity_rejected / self.quantity_received * 100)
