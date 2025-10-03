from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from src.models.invoice import InvoiceStatus, InvoiceType
from src.models.company import CompanyTier

class InvoiceLineItem(BaseModel):
    """Invoice line item schema"""
    description: str = Field(..., description="Line item description")
    quantity: float = Field(..., gt=0, description="Quantity")
    unit_price: float = Field(..., gt=0, description="Unit price")
    total_amount: float = Field(..., gt=0, description="Total amount")
    tax_rate: Optional[float] = Field(None, ge=0, le=1, description="Tax rate")
    tax_amount: Optional[float] = Field(None, ge=0, description="Tax amount")

class InvoiceResponse(BaseModel):
    """Invoice response schema"""
    id: str = Field(..., description="Invoice ID")
    invoice_number: str = Field(..., description="Invoice number")
    supplier_name: str = Field(..., description="Supplier name")
    supplier_email: Optional[EmailStr] = Field(None, description="Supplier email")
    total_amount: float = Field(..., gt=0, description="Total amount")
    currency: str = Field(default="USD", description="Currency")
    status: InvoiceStatus = Field(..., description="Invoice status")
    invoice_date: datetime = Field(..., description="Invoice date")
    due_date: Optional[datetime] = Field(None, description="Due date")
    line_items: List[InvoiceLineItem] = Field(default=[], description="Line items")
    company_id: str = Field(..., description="Company ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator('id', 'company_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        return str(v) if v is not None else v

class InvoiceListResponse(BaseModel):
    """Invoice list response schema"""
    invoices: List[InvoiceResponse] = Field(..., description="List of invoices")
    total: int = Field(..., description="Total number of invoices")
    page: int = Field(..., ge=1, description="Current page")
    size: int = Field(..., ge=1, le=100, description="Page size")
    has_next: bool = Field(..., description="Has next page")

class InvoiceCreate(BaseModel):
    """Invoice creation schema"""
    invoice_number: str = Field(..., description="Invoice number")
    supplier_name: str = Field(..., description="Supplier name")
    supplier_email: Optional[EmailStr] = Field(None, description="Supplier email")
    total_amount: float = Field(..., gt=0, description="Total amount")
    currency: str = Field(default="USD", description="Currency")
    invoice_date: datetime = Field(..., description="Invoice date")
    due_date: Optional[datetime] = Field(None, description="Due date")
    line_items: List[InvoiceLineItem] = Field(default=[], description="Line items")

class InvoiceUpdate(BaseModel):
    """Invoice update schema"""
    supplier_name: Optional[str] = Field(None, description="Supplier name")
    supplier_email: Optional[EmailStr] = Field(None, description="Supplier email")
    total_amount: Optional[float] = Field(None, gt=0, description="Total amount")
    currency: Optional[str] = Field(None, description="Currency")
    invoice_date: Optional[datetime] = Field(None, description="Invoice date")
    due_date: Optional[datetime] = Field(None, description="Due date")
    line_items: Optional[List[InvoiceLineItem]] = Field(None, description="Line items")

class InvoiceProcessingRequest(BaseModel):
    """Invoice processing request schema"""
    invoice_id: str = Field(..., description="Invoice ID")
    action: str = Field(..., description="Processing action")
    notes: Optional[str] = Field(None, description="Processing notes")

class InvoiceProcessingResponse(BaseModel):
    """Invoice processing response schema"""
    success: bool = Field(..., description="Processing success")
    message: str = Field(..., description="Response message")
    invoice_id: str = Field(..., description="Invoice ID")
    new_status: Optional[InvoiceStatus] = Field(None, description="New invoice status")

class InvoiceSearchRequest(BaseModel):
    """Invoice search request schema"""
    query: Optional[str] = Field(None, description="Search query")
    status: Optional[InvoiceStatus] = Field(None, description="Invoice status filter")
    supplier_name: Optional[str] = Field(None, description="Supplier name filter")
    date_from: Optional[datetime] = Field(None, description="Date from filter")
    date_to: Optional[datetime] = Field(None, description="Date to filter")
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum amount filter")
    max_amount: Optional[float] = Field(None, ge=0, description="Maximum amount filter")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")

class InvoiceApprovalRequest(BaseModel):
    """Invoice approval request schema"""
    invoice_id: str = Field(..., description="Invoice ID")
    approved: bool = Field(..., description="Approval decision")
    notes: Optional[str] = Field(None, description="Approval notes")

class InvoiceApprovalResponse(BaseModel):
    """Invoice approval response schema"""
    success: bool = Field(..., description="Approval success")
    message: str = Field(..., description="Response message")
    invoice_id: str = Field(..., description="Invoice ID")
    new_status: InvoiceStatus = Field(..., description="New invoice status")