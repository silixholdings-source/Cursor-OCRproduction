"""
ERP Integration Service with multi-ERP adapter support
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime, UTC
import httpx
from sqlalchemy.orm import Session

from core.config import settings
from src.models.invoice import Invoice, InvoiceStatus
from src.models.audit import AuditLog, AuditAction, AuditResourceType

logger = logging.getLogger(__name__)

class ERPAdapter(ABC):
    """Abstract base class for ERP adapters"""
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check ERP system health"""
        pass
    
    @abstractmethod
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to ERP system"""
        pass
    
    @abstractmethod
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Get invoice status from ERP system"""
        pass
    
    @abstractmethod
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate ERP connection and credentials"""
        pass
    
    # Enhanced invoice processing methods
    async def process_invoice_with_po(self, invoice: Invoice, po_number: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice with Purchase Order matching (default implementation)"""
        # Default implementation calls standard post_invoice
        # Subclasses can override for PO-specific processing
        return await self.post_invoice(invoice, company_settings)
    
    async def process_invoice_without_po(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice without Purchase Order (default implementation)"""
        # Default implementation calls standard post_invoice
        # Subclasses can override for no-PO specific processing
        return await self.post_invoice(invoice, company_settings)
    
    def supports_po_matching(self) -> bool:
        """Check if ERP supports Purchase Order matching"""
        return True  # Most ERPs support PO matching
    
    def supports_no_po_processing(self) -> bool:
        """Check if ERP supports processing invoices without PO"""
        return True  # Most ERPs support direct invoice entry
    
    def get_supported_invoice_types(self) -> List[str]:
        """Get list of supported invoice processing types"""
        types = []
        if self.supports_no_po_processing():
            types.append("no_purchase_order")
        if self.supports_po_matching():
            types.append("with_purchase_order")
        return types

class MockERPAdapter(ERPAdapter):
    """Mock ERP adapter for testing and development"""
    
    def __init__(self, erp_name: str = "MockERP"):
        self.erp_name = erp_name
        self.posted_invoices = {}
        self.health_status = "healthy"
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check"""
        await asyncio.sleep(0.1)  # Simulate network delay
        return {
            "status": self.health_status,
            "erp_name": self.erp_name,
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0.0"
        }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Mock invoice posting"""
        await asyncio.sleep(0.2)  # Simulate processing time
        
        # Generate mock ERP document ID
        erp_doc_id = f"{self.erp_name}-{invoice.invoice_number}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        
        # Store for status checks
        self.posted_invoices[erp_doc_id] = {
            "invoice_id": str(invoice.id),
            "status": "posted",
            "posted_at": datetime.now(UTC).isoformat(),
            "company_settings": company_settings
        }
        
        return {
            "status": "success",
            "erp_doc_id": erp_doc_id,
            "method": "POST",
            "timestamp": datetime.now(UTC).isoformat(),
            "message": f"Invoice successfully posted to {self.erp_name}"
        }
    
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Mock invoice status check"""
        await asyncio.sleep(0.1)
        
        if erp_document_id in self.posted_invoices:
            return {
                "status": "posted",
                "erp_doc_id": erp_document_id,
                "posted_at": self.posted_invoices[erp_document_id]["posted_at"],
                "erp_name": self.erp_name
            }
        else:
            return {
                "status": "not_found",
                "erp_doc_id": erp_document_id,
                "message": "Invoice not found in ERP system"
            }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Mock connection validation"""
        await asyncio.sleep(0.1)
        return {
            "status": "success",
            "erp_name": self.erp_name,
            "connection_type": "mock",
            "validated_at": datetime.now(UTC).isoformat(),
            "message": f"Mock connection to {self.erp_name} validated successfully"
        }
    
    def set_health_status(self, status: str):
        """Set mock health status for testing"""
        self.health_status = status

class MicrosoftDynamicsGPAdapter(ERPAdapter):
    """Microsoft Dynamics GP ERP adapter with comprehensive PO and No-PO support"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.erp_name = "Dynamics GP"
        self.connection_config = connection_config
        self.base_url = connection_config.get("base_url")
        self.api_key = connection_config.get("api_key")
        self.company_id = connection_config.get("company_id")
        self.timeout = connection_config.get("timeout", 30)
        
        # Validate required configuration
        if not all([self.base_url, self.api_key, self.company_id]):
            raise ValueError("Missing required Dynamics GP connection configuration")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Company-ID": self.company_id
            },
            timeout=self.timeout
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Dynamics GP system health"""
        try:
            response = await self.client.get("/api/health")
            response.raise_for_status()
            return {
                "status": "healthy",
                "erp_name": "Microsoft Dynamics GP",
                "timestamp": datetime.now(UTC).isoformat(),
                "version": response.json().get("version", "unknown"),
                "company_id": self.company_id
            }
        except Exception as e:
            logger.error(f"Dynamics GP health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "erp_name": "Microsoft Dynamics GP",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to Dynamics GP"""
        try:
            # Validate company settings
            if not company_settings.get("gp_company_id"):
                raise ValueError("GP Company ID not configured")
            if not company_settings.get("gp_vendor_id"):
                raise ValueError("GP Vendor ID not configured")
            
            # Transform invoice to Dynamics GP format
            gp_invoice_data = self._transform_to_gp_format(invoice, company_settings)
            
            # Post to Dynamics GP
            response = await self.client.post(
                "/api/purchasing/invoices",
                json=gp_invoice_data
            )
            response.raise_for_status()
            
            gp_response = response.json()
            
            return {
                "status": "success",
                "erp_doc_id": gp_response.get("document_id"),
                "method": "POST",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Invoice successfully posted to Dynamics GP",
                "gp_data": gp_response
            }
            
        except Exception as e:
            logger.error(f"Failed to post invoice to Dynamics GP: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to post invoice to Dynamics GP"
            }
    
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Get invoice status from Dynamics GP"""
        try:
            response = await self.client.get(f"/api/purchasing/invoices/{erp_document_id}")
            response.raise_for_status()
            
            gp_data = response.json()
            
            return {
                "status": gp_data.get("status", "unknown"),
                "erp_doc_id": erp_document_id,
                "posted_at": gp_data.get("posted_date"),
                "erp_name": "Microsoft Dynamics GP",
                "gp_data": gp_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get invoice status from Dynamics GP: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "erp_doc_id": erp_document_id,
                "message": "Failed to get invoice status from Dynamics GP"
            }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate Dynamics GP connection and credentials"""
        try:
            # Test authentication and basic connectivity
            response = await self.client.get("/api/companies")
            response.raise_for_status()
            
            companies = response.json()
            company_exists = any(c.get("id") == self.company_id for c in companies)
            
            if not company_exists:
                return {
                    "status": "error",
                    "message": f"Company ID {self.company_id} not found in Dynamics GP",
                    "timestamp": datetime.now(UTC).isoformat()
                }
            
            return {
                "status": "success",
                "message": "Dynamics GP connection validated successfully",
                "company_id": self.company_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dynamics GP connection validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Connection validation failed: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    def _transform_to_gp_format(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to Dynamics GP format"""
        return {
            "vendor_id": self._get_or_create_vendor_id(invoice.supplier_name),
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else datetime.now().date().isoformat(),
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "total_amount": float(invoice.total_amount) if invoice.total_amount else 0.0,
            "tax_amount": float(invoice.tax_amount) if invoice.tax_amount else 0.0,
            "currency_id": invoice.currency if invoice.currency else "USD",
            "line_items": [
                {
                    "item_id": line.item_id if hasattr(line, 'item_id') else None,
                    "description": line.description if hasattr(line, 'description') else "",
                    "quantity": float(line.quantity) if hasattr(line, 'quantity') and line.quantity else 1.0,
                    "unit_price": float(line.unit_price) if hasattr(line, 'unit_price') and line.unit_price else 0.0,
                    "total": float(line.total) if hasattr(line, 'total') and line.total else 0.0,
                    "gl_account": line.gl_account if hasattr(line, 'gl_account') else None
                }
                for line in (invoice.line_items if hasattr(invoice, 'line_items') and invoice.line_items else [])
            ],
            "po_number": invoice.po_number if hasattr(invoice, 'po_number') else None,
            "department": invoice.department if hasattr(invoice, 'department') else None,
            "cost_center": invoice.cost_center if hasattr(invoice, 'cost_center') else None,
            "project_code": invoice.project_code if hasattr(invoice, 'project_code') else None,
            "notes": invoice.notes if hasattr(invoice, 'notes') else None
        }
    
    def _get_or_create_vendor_id(self, supplier_name: str) -> str:
        """Get or create vendor ID in Dynamics GP"""
        # In production, this would check if vendor exists or create new one
        # Dynamics GP vendor IDs are typically alphanumeric and limited length
        return f"VENDOR-{supplier_name.upper().replace(' ', '-')[:10]}"

class Dynamics365BCAdapter(ERPAdapter):
    """Dynamics 365 Business Central ERP adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.erp_name = "D365BC"
        self.connection_config = connection_config
        self.base_url = connection_config.get("base_url")
        self.api_key = connection_config.get("api_key")
        self.company_id = connection_config.get("company_id")
        self.timeout = connection_config.get("timeout", 30)
        
        if not all([self.base_url, self.api_key, self.company_id]):
            raise ValueError("Missing required Dynamics 365 BC connection configuration")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Dynamics 365 BC system health"""
        try:
            response = await self.client.get(f"/companies({self.company_id})")
            response.raise_for_status()
            return {
                "status": "healthy",
                "erp_name": "Dynamics 365 Business Central",
                "timestamp": datetime.now(UTC).isoformat(),
                "company_id": self.company_id
            }
        except Exception as e:
            logger.error(f"Dynamics 365 BC health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "erp_name": "Dynamics 365 Business Central",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to Dynamics 365 BC"""
        try:
            # Validate company settings
            if not company_settings.get("bc_environment"):
                raise ValueError("BC Environment not configured")
            
            # Transform to BC format
            bc_invoice_data = self._transform_to_bc_format(invoice, company_settings)
            
            response = await self.client.post(
                f"/companies({self.company_id})/purchaseInvoices",
                json=bc_invoice_data
            )
            response.raise_for_status()
            
            bc_response = response.json()
            
            return {
                "status": "success",
                "erp_doc_id": bc_response.get("id"),
                "method": "POST",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Invoice successfully posted to Dynamics 365 BC",
                "bc_data": bc_response
            }
            
        except Exception as e:
            logger.error(f"Failed to post invoice to Dynamics 365 BC: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to post invoice to Dynamics 365 BC"
            }
    
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Get invoice status from Dynamics 365 BC"""
        try:
            response = await self.client.get(f"/companies({self.company_id})/purchaseInvoices({erp_document_id})")
            response.raise_for_status()
            
            bc_data = response.json()
            
            return {
                "status": bc_data.get("status", "unknown"),
                "erp_doc_id": erp_document_id,
                "posted_at": bc_data.get("postingDate"),
                "erp_name": "Dynamics 365 Business Central",
                "bc_data": bc_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get invoice status from Dynamics 365 BC: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "erp_doc_id": erp_document_id,
                "message": "Failed to get invoice status from Dynamics 365 BC"
            }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate Dynamics 365 BC connection"""
        try:
            response = await self.client.get(f"/companies({self.company_id})")
            response.raise_for_status()
            
            return {
                "status": "success",
                "message": "Dynamics 365 BC connection validated successfully",
                "company_id": self.company_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dynamics 365 BC connection validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Connection validation failed: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    def _transform_to_bc_format(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to Dynamics 365 BC format"""
        return {
            "vendorNumber": self._get_or_create_vendor_number(invoice.supplier_name),
            "invoiceNumber": invoice.invoice_number,
            "invoiceDate": invoice.invoice_date.isoformat() if invoice.invoice_date else datetime.now().date().isoformat(),
            "dueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "currencyCode": invoice.currency if invoice.currency else "USD",
            "purchaseLines": [
                {
                    "description": line.description if hasattr(line, 'description') else "",
                    "quantity": float(line.quantity) if hasattr(line, 'quantity') and line.quantity else 1.0,
                    "unitPrice": float(line.unit_price) if hasattr(line, 'unit_price') and line.unit_price else 0.0,
                    "lineAmount": float(line.total) if hasattr(line, 'total') and line.total else 0.0,
                    "accountNo": line.gl_account if hasattr(line, 'gl_account') else None
                }
                for line in (invoice.line_items if hasattr(invoice, 'line_items') and invoice.line_items else [])
            ],
            "buyFromVendorName": invoice.supplier_name,
            "payToVendorName": invoice.supplier_name
        }
    
    def _get_or_create_vendor_number(self, supplier_name: str) -> str:
        """Get or create vendor number in Dynamics 365 BC"""
        return f"V{supplier_name.upper().replace(' ', '')[:8]}"

class XeroAdapter(ERPAdapter):
    """Xero ERP adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.erp_name = "Xero"
        self.connection_config = connection_config
        self.base_url = connection_config.get("base_url")
        self.api_key = connection_config.get("api_key")
        self.company_id = connection_config.get("company_id")
        self.tenant_id = connection_config.get("tenant_id")
        
        if not all([self.base_url, self.api_key, self.company_id]):
            raise ValueError("Missing required Xero connection configuration")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Xero-tenant-id": self.tenant_id or self.company_id
            },
            timeout=30
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Xero system health"""
        try:
            response = await self.client.get("/Organisation")
            response.raise_for_status()
            return {
                "status": "healthy",
                "erp_name": "Xero",
                "timestamp": datetime.now(UTC).isoformat(),
                "tenant_id": self.tenant_id or self.company_id
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "erp_name": "Xero",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to Xero"""
        try:
            # Validate company settings
            if not company_settings.get("xero_tenant_id"):
                raise ValueError("Xero Tenant ID not configured")
            
            # Transform invoice to Xero format
            xero_data = self._transform_to_xero_format(invoice, company_settings)
            
            # Post to Xero API
            response = await self.client.post("/Bills", json=xero_data)
            response.raise_for_status()
            
            xero_response = response.json()
            bill_data = xero_response.get("Bills", [{}])[0]
            
            return {
                "status": "success",
                "erp_doc_id": bill_data.get("BillID"),
                "method": "WITHOUT_PO",
                "timestamp": datetime.now(UTC).isoformat(),
                "erp_name": "Xero",
                "posted_at": bill_data.get("DateString"),
                "xero_data": bill_data,
                "message": "Invoice posted to Xero successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to post invoice to Xero: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to post invoice to Xero"
            }
    
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Get invoice status from Xero"""
        try:
            response = await self.client.get(f"/Bills/{erp_document_id}")
            response.raise_for_status()
            
            xero_data = response.json()
            bill_data = xero_data.get("Bills", [{}])[0]
            
            return {
                "status": bill_data.get("Status", "unknown"),
                "erp_doc_id": erp_document_id,
                "erp_name": "Xero",
                "xero_data": bill_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get invoice status from Xero: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "erp_doc_id": erp_document_id,
                "message": "Failed to get invoice status from Xero"
            }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate Xero connection"""
        try:
            response = await self.client.get("/Organisation")
            response.raise_for_status()
            
            org_data = response.json()
            organisations = org_data.get("Organisations", [])
            
            if not organisations:
                return {
                    "status": "error",
                    "message": "No organisations found in Xero account",
                    "timestamp": datetime.now(UTC).isoformat()
                }
            
            return {
                "status": "connected",
                "message": "Xero connection validated successfully",
                "organisation": organisations[0].get("Name"),
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Xero connection validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Connection validation failed: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    def _transform_to_xero_format(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to Xero format"""
        return {
            "Type": "ACCPAY",  # Accounts Payable
            "Contact": {
                "Name": invoice.supplier_name
            },
            "Date": invoice.invoice_date.isoformat() if invoice.invoice_date else datetime.now().date().isoformat(),
            "DueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "InvoiceNumber": invoice.invoice_number,
            "Reference": invoice.po_number if hasattr(invoice, 'po_number') else None,
            "CurrencyCode": invoice.currency if invoice.currency else "USD",
            "LineItems": [
                {
                    "Description": line.description if hasattr(line, 'description') else "",
                    "Quantity": float(line.quantity) if hasattr(line, 'quantity') and line.quantity else 1.0,
                    "UnitAmount": float(line.unit_price) if hasattr(line, 'unit_price') and line.unit_price else 0.0,
                    "LineAmount": float(line.total) if hasattr(line, 'total') and line.total else 0.0,
                    "AccountCode": line.gl_account if hasattr(line, 'gl_account') else company_settings.get('default_expense_account', '400')
                }
                for line in (invoice.line_items if hasattr(invoice, 'line_items') and invoice.line_items else [])
            ]
        }

class ERPIntegrationService:
    """Main ERP integration service"""
    
    def __init__(self):
        self.adapters = {
            "mock": MockERPAdapter()
        }
        self.connection_cache = {}
        
        # Only initialize adapters with valid configurations
        if hasattr(settings, 'DYNAMICS_GP_CONFIG') and settings.DYNAMICS_GP_CONFIG:
            try:
                self.adapters["dynamics_gp"] = MicrosoftDynamicsGPAdapter(settings.DYNAMICS_GP_CONFIG)
            except Exception as e:
                logger.warning(f"Failed to initialize Dynamics GP adapter: {e}")
        
        if hasattr(settings, 'DYNAMICS_365_BC_CONFIG') and settings.DYNAMICS_365_BC_CONFIG:
            try:
                self.adapters["d365_bc"] = Dynamics365BCAdapter(settings.DYNAMICS_365_BC_CONFIG)
            except Exception as e:
                logger.warning(f"Failed to initialize Dynamics 365 BC adapter: {e}")
        
        if hasattr(settings, 'XERO_CONFIG') and settings.XERO_CONFIG:
            try:
                self.adapters["xero"] = XeroAdapter(settings.XERO_CONFIG)
            except Exception as e:
                logger.warning(f"Failed to initialize Xero adapter: {e}")
    
    def get_adapter(self, erp_type: str) -> Optional[ERPAdapter]:
        """Get ERP adapter by type"""
        return self.adapters.get(erp_type)
    
    def get_adapter_by_company(self, company_id: str) -> Optional[ERPAdapter]:
        """Get ERP adapter by company ID"""
        connection_info = self.connection_cache.get(company_id)
        return connection_info.get("adapter") if connection_info else None
    
    async def post_invoice(
        self, 
        erp_type: str, 
        invoice: Invoice, 
        company_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Post invoice to specified ERP system"""
        adapter = self.get_adapter(erp_type)
        
        if not adapter:
            return {
                "status": "error",
                "message": f"Unknown ERP type: {erp_type}",
                "timestamp": datetime.now(UTC).isoformat()
            }
        
        try:
            result = await adapter.post_invoice(invoice, company_settings)
            return result
        except Exception as e:
            logger.error(f"Failed to post invoice to {erp_type}: {e}")
            return {
                "status": "error",
                "message": f"Failed to post invoice to {erp_type}: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all registered ERP connections"""
        results = {}
        
        for company_id, connection_info in self.connection_cache.items():
            try:
                adapter = connection_info["adapter"]
                health_result = await adapter.health_check()
                results[company_id] = {
                    "erp_type": connection_info["erp_type"],
                    "status": health_result.get("status"),
                    "timestamp": health_result.get("timestamp"),
                    "health": health_result
                }
            except Exception as e:
                results[company_id] = {
                    "erp_type": connection_info.get("erp_type"),
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat()
                }
        
        return results
    
    async def validate_erp_configuration(self, erp_type: str, connection_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ERP connection configuration"""
        try:
            if erp_type == "mock":
                adapter = MockERPAdapter("MockERP")
            elif erp_type == "dynamics_gp":
                adapter = MicrosoftDynamicsGPAdapter(connection_config)
            elif erp_type == "d365_bc":
                adapter = Dynamics365BCAdapter(connection_config)
            elif erp_type == "xero":
                adapter = XeroAdapter(connection_config)
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported ERP type: {erp_type}",
                    "timestamp": datetime.now(UTC).isoformat()
                }
            
            validation_result = await adapter.validate_connection()
            return {
                "status": "success" if validation_result.get("status") == "success" else "error",
                "erp_type": erp_type,
                "message": validation_result.get("message", "unknown"),
                "validated_at": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "erp_type": erp_type,
                "message": str(e),
                "validated_at": datetime.now(UTC).isoformat()
            }
    
    async def check_invoice_status(self, erp_document_id: str, erp_type: str) -> Dict[str, Any]:
        """Check invoice status in ERP system"""
        try:
            adapter = self.get_adapter(erp_type)
            if not adapter:
                return {
                    "status": "error",
                    "message": f"Unknown ERP type: {erp_type}"
                }
            
            result = await adapter.get_invoice_status(erp_document_id)
            return result
            
        except Exception as e:
            logger.error(f"Failed to check invoice status: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to check invoice status: {str(e)}"
            }
    
    async def register_erp(self, company_id: str, erp_type: str, connection_config: Dict[str, Any]) -> Dict[str, Any]:
        """Register ERP connection for a company"""
        try:
            # Validate configuration first
            validation_result = await self.validate_erp_configuration(erp_type, connection_config)
            if validation_result.get("status") != "success":
                return {
                    "status": "error",
                    "message": f"Invalid ERP configuration: {validation_result.get('message', 'Unknown error')}"
                }
            
            # Create adapter with the configuration
            if erp_type == "mock":
                adapter = MockERPAdapter("MockERP")
            elif erp_type == "dynamics_gp":
                adapter = MicrosoftDynamicsGPAdapter(connection_config)
            elif erp_type == "d365_bc":
                adapter = Dynamics365BCAdapter(connection_config)
            elif erp_type == "xero":
                adapter = XeroAdapter(connection_config)
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported ERP type: {erp_type}"
                }
            
            # Store in connection cache
            self.connection_cache[company_id] = {
                "erp_type": erp_type,
                "adapter": adapter,
                "status": "connected",
                "registered_at": datetime.now(UTC).isoformat()
            }
            
            return {
                "status": "success",
                "erp_type": erp_type,
                "company_id": company_id,
                "message": f"ERP {erp_type} registered successfully for company {company_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to register ERP: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to register ERP: {str(e)}"
            }
    
    async def post_invoice_to_erp(self, company_id: str, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to registered ERP for a company"""
        try:
            # Get company's ERP connection
            connection_info = self.connection_cache.get(company_id)
            if not connection_info:
                return {
                    "status": "error",
                    "message": f"No ERP integration found for company {company_id}"
                }
            
            adapter = connection_info["adapter"]
            result = await adapter.post_invoice(invoice, company_settings)
            return result
            
        except Exception as e:
            logger.error(f"Failed to post invoice to ERP: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to post invoice to ERP: {str(e)}"
            }
    
    def get_connection_status(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get connection status for a company"""
        return self.connection_cache.get(company_id)
    
    def list_registered_erps(self) -> List[Dict[str, Any]]:
        """List all registered ERP connections"""
        return [
            {
                "company_id": company_id,
                "erp_type": info.get("erp_type"),
                "status": info.get("status"),
                "registered_at": info.get("registered_at")
            }
            for company_id, info in self.connection_cache.items()
        ]
