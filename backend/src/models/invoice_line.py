from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.core.database import Base

class InvoiceLine(Base):
    """Invoice line item model"""
    __tablename__ = "invoice_lines"
    __table_args__ = {'extend_existing': True}
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to invoice
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    
    # Line item details
    line_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # GL coding
    gl_account = Column(String(50), nullable=True)
    cost_center = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)
    project_code = Column(String(50), nullable=True)
    
    # Tax information
    tax_rate = Column(Numeric(5, 4), nullable=True)
    tax_amount = Column(Numeric(15, 2), nullable=True)
    
    # Relationships
    invoice = relationship("models.invoice.Invoice", back_populates="line_items")
    
    def __repr__(self):
        return f"<InvoiceLine(id={self.id}, description='{self.description[:50]}...', amount={self.total_amount})>"
    
    @property
    def calculated_total(self) -> float:
        """Calculate total amount from quantity and unit price"""
        return float(self.quantity * self.unit_price)
    
    def validate_totals(self) -> bool:
        """Validate that calculated total matches stored total"""
        return abs(self.calculated_total - float(self.total_amount)) < 0.01