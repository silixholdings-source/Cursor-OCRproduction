from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ERPType(str, Enum):
    """Supported ERP system types"""
    DYNAMICS_GP = "dynamics_gp"
    DYNAMICS_365_BC = "dynamics_365_bc"
    XERO = "xero"
    SAGE = "sage"
    QUICKBOOKS = "quickbooks"
    NETSUITE = "netsuite"
    SAP = "sap"
    ORACLE = "oracle"
    MOCK = "mock"

class ERPConnectionStatus(str, Enum):
    """ERP connection status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"

class ERPConnectionRequest(BaseModel):
    """Request schema for ERP connection registration"""
    erp_type: ERPType = Field(..., description="Type of ERP system")
    connection_name: str = Field(..., min_length=1, max_length=100, description="User-friendly connection name")
    configuration: Dict[str, Any] = Field(..., description="ERP-specific connection configuration")

class ERPConnectionResponse(BaseModel):
    """Response schema for ERP connection"""
    id: str = Field(..., description="Connection ID")
    erp_type: ERPType = Field(..., description="Type of ERP system")
    connection_name: str = Field(..., description="User-friendly connection name")
    status: ERPConnectionStatus = Field(..., description="Connection status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_tested_at: Optional[datetime] = Field(None, description="Last test timestamp")
    error_message: Optional[str] = Field(None, description="Error message if status is error")

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        return str(v) if v is not None else v

class ERPConnectionListResponse(BaseModel):
    """Response schema for ERP connection list"""
    connections: List[ERPConnectionResponse] = Field(..., description="List of ERP connections")
    total: int = Field(..., description="Total number of connections")
    page: int = Field(..., ge=1, description="Current page")
    size: int = Field(..., ge=1, le=100, description="Page size")
    has_next: bool = Field(..., description="Has next page")

class ERPConnectionUpdate(BaseModel):
    """Request schema for ERP connection update"""
    connection_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User-friendly connection name")
    configuration: Optional[Dict[str, Any]] = Field(None, description="ERP-specific connection configuration")
    status: Optional[ERPConnectionStatus] = Field(None, description="Connection status")

class ERPHealthCheckResponse(BaseModel):
    """Response schema for ERP health check"""
    erp_type: ERPType = Field(..., description="Type of ERP system")
    status: str = Field(..., description="Health status")
    message: str = Field(..., description="Status message")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    last_checked: datetime = Field(..., description="Last check timestamp")

class ERPHealthCheckAllResponse(BaseModel):
    """Response schema for all ERP health checks"""
    adapters: Dict[str, ERPHealthCheckResponse] = Field(..., description="Health check results for all adapters")
    overall_status: str = Field(..., description="Overall system status")
    total_adapters: int = Field(..., description="Total number of adapters")
    healthy_adapters: int = Field(..., description="Number of healthy adapters")

class ERPInvoicePostRequest(BaseModel):
    """Request schema for posting invoice to ERP"""
    invoice_id: str = Field(..., description="Invoice ID")
    erp_connection_id: str = Field(..., description="ERP connection ID")
    posting_method: str = Field(default="WITH_PO", description="Posting method (WITH_PO, WITHOUT_PO)")

class ERPInvoicePostResponse(BaseModel):
    """Response schema for ERP invoice posting"""
    success: bool = Field(..., description="Posting success")
    message: str = Field(..., description="Response message")
    erp_document_id: Optional[str] = Field(None, description="ERP document ID")
    erp_invoice_number: Optional[str] = Field(None, description="ERP invoice number")
    posted_at: Optional[datetime] = Field(None, description="Posting timestamp")

class ERPInvoiceStatusRequest(BaseModel):
    """Request schema for checking ERP invoice status"""
    invoice_id: str = Field(..., description="Invoice ID")
    erp_connection_id: str = Field(..., description="ERP connection ID")
    erp_document_id: str = Field(..., description="ERP document ID")

class ERPInvoiceStatusResponse(BaseModel):
    """Response schema for ERP invoice status"""
    invoice_id: str = Field(..., description="Invoice ID")
    erp_document_id: str = Field(..., description="ERP document ID")
    status: str = Field(..., description="Invoice status in ERP")
    message: str = Field(..., description="Status message")
    last_checked: datetime = Field(..., description="Last check timestamp")

class ERPConfigurationValidationRequest(BaseModel):
    """Request schema for ERP configuration validation"""
    erp_type: ERPType = Field(..., description="Type of ERP system")
    configuration: Dict[str, Any] = Field(..., description="ERP-specific connection configuration")

class ERPConfigurationValidationResponse(BaseModel):
    """Response schema for ERP configuration validation"""
    valid: bool = Field(..., description="Configuration validity")
    message: str = Field(..., description="Validation message")
    errors: List[str] = Field(default=[], description="List of validation errors")
    warnings: List[str] = Field(default=[], description="List of validation warnings")

class ERPVendorSyncRequest(BaseModel):
    """Request schema for vendor synchronization"""
    erp_connection_id: str = Field(..., description="ERP connection ID")
    sync_all: bool = Field(default=False, description="Sync all vendors")
    vendor_ids: Optional[List[str]] = Field(None, description="Specific vendor IDs to sync")

class ERPVendorSyncResponse(BaseModel):
    """Response schema for vendor synchronization"""
    success: bool = Field(..., description="Sync success")
    message: str = Field(..., description="Response message")
    vendors_synced: int = Field(..., description="Number of vendors synced")
    vendors_created: int = Field(..., description="Number of vendors created")
    vendors_updated: int = Field(..., description="Number of vendors updated")
    sync_timestamp: datetime = Field(..., description="Sync timestamp")

# Additional schemas for compatibility
class ERPHealthResponse(BaseModel):
    """ERP health response schema"""
    status: str = Field(..., description="Health status")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Check timestamp")

class ERPPostingRequest(BaseModel):
    """ERP posting request schema"""
    invoice_id: str = Field(..., description="Invoice ID")
    connection_id: str = Field(..., description="Connection ID")

class ERPPostingResponse(BaseModel):
    """ERP posting response schema"""
    success: bool = Field(..., description="Posting success")
    message: str = Field(..., description="Response message")
    erp_document_id: Optional[str] = Field(None, description="ERP document ID")

class ERPStatusResponse(BaseModel):
    """ERP status response schema"""
    invoice_id: str = Field(..., description="Invoice ID")
    status: str = Field(..., description="Status")
    message: str = Field(..., description="Status message")

class ERPConfigurationSchema(BaseModel):
    """ERP configuration schema"""
    erp_type: ERPType = Field(..., description="ERP type")
    configuration: Dict[str, Any] = Field(..., description="Configuration")

class ERPValidationResult(BaseModel):
    """ERP validation result schema"""
    valid: bool = Field(..., description="Valid")
    message: str = Field(..., description="Message")
    errors: List[str] = Field(default=[], description="Errors")

class ERPConnectionInfo(BaseModel):
    """ERP connection info schema"""
    id: str = Field(..., description="Connection ID")
    name: str = Field(..., description="Connection name")
    type: ERPType = Field(..., description="ERP type")
    status: ERPConnectionStatus = Field(..., description="Status")

class ERPCapabilities(BaseModel):
    """ERP capabilities schema"""
    erp_type: ERPType = Field(..., description="ERP type")
    capabilities: List[str] = Field(..., description="Capabilities")

class ERPBatchPostingRequest(BaseModel):
    """ERP batch posting request schema"""
    invoice_ids: List[str] = Field(..., description="Invoice IDs")
    connection_id: str = Field(..., description="Connection ID")

class ERPBatchPostingResponse(BaseModel):
    """ERP batch posting response schema"""
    success: bool = Field(..., description="Success")
    message: str = Field(..., description="Message")
    results: List[Dict[str, Any]] = Field(..., description="Results")

class ERPAuditLog(BaseModel):
    """ERP audit log schema"""
    id: str = Field(..., description="Log ID")
    action: str = Field(..., description="Action")
    timestamp: datetime = Field(..., description="Timestamp")
    details: Dict[str, Any] = Field(..., description="Details")

class ERPMetrics(BaseModel):
    """ERP metrics schema"""
    total_connections: int = Field(..., description="Total connections")
    active_connections: int = Field(..., description="Active connections")
    total_postings: int = Field(..., description="Total postings")
    success_rate: float = Field(..., description="Success rate")

class ERPSyncRequest(BaseModel):
    """ERP sync request schema"""
    connection_id: str = Field(..., description="Connection ID")
    sync_type: str = Field(..., description="Sync type")

class ERPSyncResponse(BaseModel):
    """ERP sync response schema"""
    success: bool = Field(..., description="Success")
    message: str = Field(..., description="Message")
    synced_count: int = Field(..., description="Synced count")

class ERPPostingMethod(str, Enum):
    """ERP posting method"""
    WITH_PO = "WITH_PO"
    WITHOUT_PO = "WITHOUT_PO"