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
            "status": "connected",
            "erp_name": self.erp_name,
            "connection_type": "mock",
            "validated_at": datetime.now(UTC).isoformat()
        }
    
    def set_health_status(self, status: str):
        """Set mock health status for testing"""
        self.health_status = status

class MicrosoftDynamicsGPAdapter(ERPAdapter):
    """Microsoft Dynamics GP ERP adapter with comprehensive PO and No-PO support"""
    
    def __init__(self, connection_config: Dict[str, Any]):
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
    
    def supports_po_matching(self) -> bool:
        """Dynamics GP has excellent PO matching capabilities"""
        return True
    
    def supports_no_po_processing(self) -> bool:
        """Dynamics GP supports direct Payables Management entry"""
        return True
    
    async def process_invoice_with_po(self, invoice: Invoice, po_number: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice with Purchase Order matching using GP's advanced matching"""
        try:
            # Transform invoice to GP format with PO reference
            gp_data = self._transform_to_gp_format_with_po(invoice, po_number, company_settings)
            
            # Post to Dynamics GP with PO matching
            response = await self.client.post(
                "/api/purchasing/invoices/match-po",
                json=gp_data
            )
            response.raise_for_status()
            
            gp_response = response.json()
            
            return {
                "status": "success",
                "processing_type": "with_purchase_order",
                "erp_doc_id": gp_response.get("document_id"),
                "po_number": po_number,
                "po_match_status": gp_response.get("po_match_status"),
                "variance_details": gp_response.get("variances", []),
                "auto_approved": gp_response.get("auto_approved", False),
                "method": "PO_MATCHING",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": f"Invoice matched to PO {po_number} and posted to Dynamics GP",
                "gp_data": gp_response
            }
            
        except Exception as e:
            logger.error(f"Failed to process GP invoice with PO: {str(e)}")
            return {
                "status": "error",
                "processing_type": "with_purchase_order",
                "po_number": po_number,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to process invoice with PO in Dynamics GP"
            }
    
    async def process_invoice_without_po(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice without PO directly into Payables Management"""
        try:
            # Transform invoice to GP Payables Management format
            gp_data = self._transform_to_gp_payables_format(invoice, company_settings)
            
            # Post directly to Payables Management
            response = await self.client.post(
                "/api/payables/invoices",
                json=gp_data
            )
            response.raise_for_status()
            
            gp_response = response.json()
            
            return {
                "status": "success",
                "processing_type": "no_purchase_order",
                "erp_doc_id": gp_response.get("document_id"),
                "vendor_id": gp_response.get("vendor_id"),
                "gl_distributions": gp_response.get("gl_distributions", []),
                "method": "PAYABLES_DIRECT",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Invoice posted directly to Dynamics GP Payables Management",
                "gp_data": gp_response
            }
            
        except Exception as e:
            logger.error(f"Failed to process GP invoice without PO: {str(e)}")
            return {
                "status": "error",
                "processing_type": "no_purchase_order",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to process invoice without PO in Dynamics GP"
            }
    
    def _transform_to_gp_format_with_po(self, invoice: Invoice, po_number: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to GP format with PO matching"""
        return {
            "vendor_id": self._get_or_create_vendor_id(invoice.supplier_name),
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "total_amount": float(invoice.total_amount),
            "tax_amount": float(invoice.tax_amount),
            "currency_id": invoice.currency,
            "po_number": po_number,
            "matching_type": "PO_MATCH",
            "line_items": [
                {
                    "item_id": line.item_id if hasattr(line, 'item_id') else None,
                    "description": line.description,
                    "quantity": float(line.quantity),
                    "unit_price": float(line.unit_price),
                    "total": float(line.total),
                    "po_line_reference": getattr(line, 'po_line_reference', None)
                }
                for line in invoice.line_items
            ]
        }
    
    def _transform_to_gp_payables_format(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to GP Payables Management format"""
        return {
            "vendor_id": self._get_or_create_vendor_id(invoice.supplier_name),
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "total_amount": float(invoice.total_amount),
            "tax_amount": float(invoice.tax_amount),
            "currency_id": invoice.currency,
            "processing_type": "DIRECT_PAYABLES",
            "auto_create_vendor": True,
            "gl_distributions": self._generate_gl_distributions(invoice, company_settings),
            "line_items": [
                {
                    "description": line.description,
                    "quantity": float(line.quantity),
                    "unit_price": float(line.unit_price),
                    "total": float(line.total),
                    "gl_account": self._determine_gl_account(line, company_settings)
                }
                for line in invoice.line_items
            ]
        }
    
    def _generate_gl_distributions(self, invoice: Invoice, company_settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate GL distributions for direct payables posting"""
        distributions = []
        
        # Accounts Payable (Credit)
        distributions.append({
            "account": company_settings.get("accounts_payable_account", "2000-00"),
            "debit_amount": 0.0,
            "credit_amount": float(invoice.total_amount),
            "description": f"AP - {invoice.invoice_number}"
        })
        
        # Expense accounts (Debit)
        for line in invoice.line_items:
            gl_account = self._determine_gl_account(line, company_settings)
            distributions.append({
                "account": gl_account,
                "debit_amount": float(line.total),
                "credit_amount": 0.0,
                "description": line.description[:30]
            })
        
        # Tax account (Debit) if applicable
        if invoice.tax_amount > 0:
            distributions.append({
                "account": company_settings.get("tax_account", "2200-00"),
                "debit_amount": float(invoice.tax_amount),
                "credit_amount": 0.0,
                "description": f"Tax - {invoice.invoice_number}"
            })
        
        return distributions
    
    def _determine_gl_account(self, line_item, company_settings: Dict[str, Any]) -> str:
        """Intelligent GL account determination"""
        # Check if line item has specific GL account
        if hasattr(line_item, 'gl_account') and line_item.gl_account:
            return line_item.gl_account
        
        # Categorize based on description
        description = line_item.description.lower() if line_item.description else ""
        
        if any(word in description for word in ["office", "supplies", "stationery"]):
            return company_settings.get("office_supplies_account", "5200-00")
        elif any(word in description for word in ["travel", "mileage", "hotel"]):
            return company_settings.get("travel_account", "5300-00")
        elif any(word in description for word in ["software", "license", "subscription"]):
            return company_settings.get("software_account", "5400-00")
        elif any(word in description for word in ["consulting", "professional", "legal"]):
            return company_settings.get("professional_services_account", "5600-00")
        else:
            return company_settings.get("general_expense_account", "5000-00")
    
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
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "total_amount": float(invoice.total_amount),
            "tax_amount": float(invoice.tax_amount),
            "currency_id": invoice.currency,
            "line_items": [
                {
                    "item_id": line.item_id if hasattr(line, 'item_id') else None,
                    "description": line.description,
                    "quantity": float(line.quantity),
                    "unit_price": float(line.unit_price),
                    "total": float(line.total),
                    "gl_account": line.gl_account if hasattr(line, 'gl_account') else None
                }
                for line in invoice.line_items
            ],
            "po_number": invoice.po_number,
            "department": invoice.department,
            "cost_center": invoice.cost_center,
            "project_code": invoice.project_code,
            "notes": invoice.notes
        }
    
    def _get_or_create_vendor_id(self, supplier_name: str) -> str:
        """Get or create vendor ID in Dynamics GP"""
        # In production, this would check if vendor exists or create new one
        # Dynamics GP vendor IDs are typically alphanumeric and limited length
        return f"VENDOR-{supplier_name.upper().replace(' ', '-')[:10]}"

class Dynamics365BCAdapter(ERPAdapter):
    """Dynamics 365 Business Central ERP adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
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
            "invoiceDate": invoice.invoice_date.isoformat(),
            "dueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "currencyCode": invoice.currency,
            "purchaseLines": [
                {
                    "description": line.description,
                    "quantity": float(line.quantity),
                    "unitPrice": float(line.unit_price),
                    "lineAmount": float(line.total),
                    "accountNo": line.gl_account if hasattr(line, 'gl_account') else None
                }
                for line in invoice.line_items
            ],
            "buyFromVendorName": invoice.supplier_name,
            "payToVendorName": invoice.supplier_name
        }
    
    def _get_or_create_vendor_number(self, supplier_name: str) -> str:
        """Get or create vendor number in Dynamics 365 BC"""
        return f"V{supplier_name.upper().replace(' ', '')[:8]}"

class SageAdapter(ERPAdapter):
    """Sage ERP adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.connection_config = connection_config
        # Sage-specific configuration
        self.base_url = connection_config.get("base_url")
        self.api_key = connection_config.get("api_key")
        self.company_id = connection_config.get("company_id")
        
        if not all([self.base_url, self.api_key, self.company_id]):
            raise ValueError("Missing required Sage connection configuration")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Sage system health"""
        try:
            response = await self.client.get("/api/health")
            response.raise_for_status()
            return {
                "status": "healthy",
                "erp_name": "Sage",
                "timestamp": datetime.now(UTC).isoformat(),
                "company_id": self.company_id
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "erp_name": "Sage",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to Sage"""
        try:
            # Transform invoice to Sage format
            sage_data = self._transform_to_sage_format(invoice, company_settings)
            
            # Post to Sage API
            response = await self.client.post(
                f"/api/companies/{self.company_id}/purchase-invoices",
                json=sage_data
            )
            response.raise_for_status()
            
            sage_response = response.json()
            
            return {
                "status": "success",
                "erp_doc_id": sage_response.get("id"),
                "erp_name": "Sage",
                "posted_at": sage_response.get("created_date"),
                "sage_data": sage_response,
                "message": "Invoice posted to Sage successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to post invoice to Sage: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to post invoice to Sage"
            }
    
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Get invoice status from Sage"""
        return {
            "status": "posted",
            "erp_doc_id": erp_document_id,
            "erp_name": "Sage"
        }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate Sage connection"""
        try:
            # Test authentication and basic connectivity
            response = await self.client.get("/api/companies")
            response.raise_for_status()
            
            companies = response.json()
            company_exists = any(c.get("id") == self.company_id for c in companies)
            
            if not company_exists:
                return {
                    "status": "error",
                    "message": f"Company ID {self.company_id} not found in Sage",
                    "timestamp": datetime.now(UTC).isoformat()
                }
            
            return {
                "status": "connected",
                "message": "Sage connection validated successfully",
                "company_id": self.company_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sage connection validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Connection validation failed: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    def _transform_to_sage_format(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to Sage format"""
        return {
            "supplier_id": self._get_or_create_supplier_id(invoice.supplier_name),
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "currency_code": invoice.currency,
            "net_amount": float(invoice.subtotal or invoice.total_amount),
            "tax_amount": float((invoice.total_with_tax or invoice.total_amount) - (invoice.subtotal or invoice.total_amount)),
            "gross_amount": float(invoice.total_with_tax or invoice.total_amount),
            "purchase_lines": [
                {
                    "description": line.description,
                    "quantity": float(line.quantity),
                    "unit_price": float(line.unit_price),
                    "net_amount": float(line.total),
                    "account_code": line.gl_account if hasattr(line, 'gl_account') else company_settings.get('default_expense_account')
                }
                for line in invoice.line_items
            ],
            "supplier_name": invoice.supplier_name
        }
    
    def _get_or_create_supplier_id(self, supplier_name: str) -> str:
        """Get or create supplier ID in Sage"""
        # In production, this would check if supplier exists or create new one
        return f"SUP-{supplier_name.upper().replace(' ', '')[:8]}"

class QuickBooksAdapter(ERPAdapter):
    """QuickBooks ERP adapter with PO and No-PO support"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.connection_config = connection_config
        # QuickBooks-specific configuration
        self.base_url = connection_config.get("base_url")
        self.api_key = connection_config.get("api_key")
        self.company_id = connection_config.get("company_id")
        
        if not all([self.base_url, self.api_key, self.company_id]):
            raise ValueError("Missing required QuickBooks connection configuration")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    def supports_po_matching(self) -> bool:
        """QuickBooks supports PO matching through Purchase Order references"""
        return True
    
    def supports_no_po_processing(self) -> bool:
        """QuickBooks supports direct Bill creation without PO"""
        return True
    
    async def process_invoice_with_po(self, invoice: Invoice, po_number: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice with Purchase Order reference in QuickBooks"""
        try:
            # Transform invoice to QuickBooks Bill format with PO reference
            qb_data = self._transform_to_qb_format_with_po(invoice, po_number, company_settings)
            
            # Create Bill with PO reference
            response = await self.client.post(
                f"/v3/company/{self.company_id}/bill",
                json=qb_data
            )
            response.raise_for_status()
            
            qb_response = response.json()
            bill_data = qb_response.get("Bill", {})
            
            return {
                "status": "success",
                "processing_type": "with_purchase_order",
                "erp_doc_id": bill_data.get("Id"),
                "po_number": po_number,
                "qb_bill_number": bill_data.get("DocNumber"),
                "vendor_ref": bill_data.get("VendorRef", {}).get("name"),
                "method": "PO_REFERENCE",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": f"Bill created in QuickBooks with PO reference {po_number}",
                "qb_data": bill_data
            }
            
        except Exception as e:
            logger.error(f"Failed to process QuickBooks invoice with PO: {str(e)}")
            return {
                "status": "error",
                "processing_type": "with_purchase_order",
                "po_number": po_number,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to process invoice with PO in QuickBooks"
            }
    
    async def process_invoice_without_po(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice without PO as direct Bill in QuickBooks"""
        try:
            # Transform invoice to QuickBooks Bill format
            qb_data = self._transform_to_qb_format_no_po(invoice, company_settings)
            
            # Create Bill directly
            response = await self.client.post(
                f"/v3/company/{self.company_id}/bill",
                json=qb_data
            )
            response.raise_for_status()
            
            qb_response = response.json()
            bill_data = qb_response.get("Bill", {})
            
            return {
                "status": "success",
                "processing_type": "no_purchase_order",
                "erp_doc_id": bill_data.get("Id"),
                "qb_bill_number": bill_data.get("DocNumber"),
                "vendor_ref": bill_data.get("VendorRef", {}).get("name"),
                "method": "DIRECT_BILL",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Bill created directly in QuickBooks",
                "qb_data": bill_data
            }
            
        except Exception as e:
            logger.error(f"Failed to process QuickBooks invoice without PO: {str(e)}")
            return {
                "status": "error",
                "processing_type": "no_purchase_order",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to process invoice without PO in QuickBooks"
            }
    
    def _transform_to_qb_format_with_po(self, invoice: Invoice, po_number: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to QuickBooks Bill format with PO reference"""
        return {
            "VendorRef": {
                "value": self._get_or_create_vendor_ref(invoice.supplier_name),
                "name": invoice.supplier_name
            },
            "TxnDate": invoice.invoice_date.isoformat(),
            "DueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "DocNumber": invoice.invoice_number,
            "PoNumber": po_number,  # PO reference
            "CurrencyRef": {
                "value": invoice.currency
            },
            "PrivateNote": f"Invoice {invoice.invoice_number} matched to PO {po_number}",
            "Line": [
                {
                    "Amount": float(line.total),
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {
                            "value": self._determine_qb_account(line, company_settings)
                        },
                        "CustomerRef": getattr(line, 'customer_ref', None),
                        "BillableStatus": "NotBillable"
                    },
                    "Description": f"{line.description} (PO: {po_number})"
                }
                for line in invoice.line_items
            ]
        }
    
    def _transform_to_qb_format_no_po(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to QuickBooks Bill format without PO"""
        return {
            "VendorRef": {
                "value": self._get_or_create_vendor_ref(invoice.supplier_name),
                "name": invoice.supplier_name
            },
            "TxnDate": invoice.invoice_date.isoformat(),
            "DueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "DocNumber": invoice.invoice_number,
            "CurrencyRef": {
                "value": invoice.currency
            },
            "PrivateNote": f"Direct invoice entry: {invoice.invoice_number}",
            "Line": [
                {
                    "Amount": float(line.total),
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {
                            "value": self._determine_qb_account(line, company_settings)
                        },
                        "BillableStatus": "NotBillable"
                    },
                    "Description": line.description
                }
                for line in invoice.line_items
            ]
        }
    
    def _determine_qb_account(self, line_item, company_settings: Dict[str, Any]) -> str:
        """Determine QuickBooks account for line item"""
        # Check if line item has specific account
        if hasattr(line_item, 'qb_account') and line_item.qb_account:
            return line_item.qb_account
        
        # Categorize based on description
        description = line_item.description.lower() if line_item.description else ""
        
        if any(word in description for word in ["office", "supplies"]):
            return company_settings.get("qb_office_supplies_account", "64")  # Office Supplies
        elif any(word in description for word in ["travel", "hotel"]):
            return company_settings.get("qb_travel_account", "65")  # Travel Expense
        elif any(word in description for word in ["software", "license"]):
            return company_settings.get("qb_software_account", "66")  # Computer and Internet Expenses
        elif any(word in description for word in ["consulting", "professional"]):
            return company_settings.get("qb_professional_account", "67")  # Professional Fees
        else:
            return company_settings.get("qb_general_expense_account", "68")  # Other Business Expenses
    
    async def health_check(self) -> Dict[str, Any]:
        """Check QuickBooks system health"""
        try:
            response = await self.client.get("/api/health")
            response.raise_for_status()
            return {
                "status": "healthy",
                "erp_name": "QuickBooks",
                "timestamp": datetime.now(UTC).isoformat(),
                "company_id": self.company_id
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "erp_name": "QuickBooks",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to QuickBooks"""
        try:
            # Transform invoice to QuickBooks format
            qb_data = self._transform_to_qb_format_no_po(invoice, company_settings)
            
            # Post to QuickBooks API
            response = await self.client.post(
                f"/v3/company/{self.company_id}/bill",
                json=qb_data
            )
            response.raise_for_status()
            
            qb_response = response.json()
            bill_data = qb_response.get("QueryResponse", {}).get("Bill", [{}])[0]
            
            return {
                "status": "success",
                "erp_doc_id": bill_data.get("Id"),
                "erp_name": "QuickBooks",
                "posted_at": bill_data.get("MetaData", {}).get("CreateTime"),
                "qb_data": bill_data,
                "message": "Invoice posted to QuickBooks successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to post invoice to QuickBooks: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to post invoice to QuickBooks"
            }
    
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Get invoice status from QuickBooks"""
        return {
            "status": "posted",
            "erp_doc_id": erp_document_id,
            "erp_name": "QuickBooks"
        }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate QuickBooks connection"""
        try:
            # Test authentication and basic connectivity
            response = await self.client.get(f"/v3/company/{self.company_id}/companyinfo/{self.company_id}")
            response.raise_for_status()
            
            return {
                "status": "connected",
                "message": "QuickBooks connection validated successfully",
                "company_id": self.company_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"QuickBooks connection validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Connection validation failed: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }

class XeroAdapter(ERPAdapter):
    """Xero ERP adapter with comprehensive PO and No-PO support"""
    
    def __init__(self, connection_config: Dict[str, Any]):
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
    
    def supports_po_matching(self) -> bool:
        """Xero supports PO references in Bills"""
        return True
    
    def supports_no_po_processing(self) -> bool:
        """Xero supports direct Bill creation without PO"""
        return True
    
    async def process_invoice_with_po(self, invoice: Invoice, po_number: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice with Purchase Order reference in Xero"""
        try:
            # Transform invoice to Xero Bill format with PO reference
            xero_data = self._transform_to_xero_format_with_po(invoice, po_number, company_settings)
            
            # Create Bill with PO reference
            response = await self.client.post("/Bills", json=xero_data)
            response.raise_for_status()
            
            xero_response = response.json()
            bill_data = xero_response.get("Bills", [{}])[0]
            
            return {
                "status": "success",
                "processing_type": "with_purchase_order",
                "erp_doc_id": bill_data.get("BillID"),
                "po_number": po_number,
                "xero_bill_number": bill_data.get("BillNumber"),
                "contact_name": bill_data.get("Contact", {}).get("Name"),
                "method": "PO_REFERENCE",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": f"Bill created in Xero with PO reference {po_number}",
                "xero_data": bill_data
            }
            
        except Exception as e:
            logger.error(f"Failed to process Xero invoice with PO: {str(e)}")
            return {
                "status": "error",
                "processing_type": "with_purchase_order",
                "po_number": po_number,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to process invoice with PO in Xero"
            }
    
    async def process_invoice_without_po(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice without PO as direct Bill in Xero"""
        try:
            # Transform invoice to Xero Bill format
            xero_data = self._transform_to_xero_format_no_po(invoice, company_settings)
            
            # Create Bill directly
            response = await self.client.post("/Bills", json=xero_data)
            response.raise_for_status()
            
            xero_response = response.json()
            bill_data = xero_response.get("Bills", [{}])[0]
            
            return {
                "status": "success",
                "processing_type": "no_purchase_order",
                "erp_doc_id": bill_data.get("BillID"),
                "xero_bill_number": bill_data.get("BillNumber"),
                "contact_name": bill_data.get("Contact", {}).get("Name"),
                "method": "DIRECT_BILL",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Bill created directly in Xero",
                "xero_data": bill_data
            }
            
        except Exception as e:
            logger.error(f"Failed to process Xero invoice without PO: {str(e)}")
            return {
                "status": "error",
                "processing_type": "no_purchase_order",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to process invoice without PO in Xero"
            }
    
    def _transform_to_xero_format_with_po(self, invoice: Invoice, po_number: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to Xero Bill format with PO reference"""
        return {
            "Type": "ACCPAY",  # Accounts Payable
            "Contact": {
                "Name": invoice.supplier_name
            },
            "Date": invoice.invoice_date.isoformat(),
            "DueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "InvoiceNumber": invoice.invoice_number,
            "Reference": po_number,  # PO reference
            "CurrencyCode": invoice.currency,
            "Status": "DRAFT",
            "LineItems": [
                {
                    "Description": f"{line.description} (PO: {po_number})",
                    "Quantity": float(line.quantity),
                    "UnitAmount": float(line.unit_price),
                    "LineAmount": float(line.total),
                    "AccountCode": self._determine_xero_account(line, company_settings)
                }
                for line in invoice.line_items
            ]
        }
    
    def _transform_to_xero_format_no_po(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to Xero Bill format without PO"""
        return {
            "Type": "ACCPAY",  # Accounts Payable
            "Contact": {
                "Name": invoice.supplier_name
            },
            "Date": invoice.invoice_date.isoformat(),
            "DueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "InvoiceNumber": invoice.invoice_number,
            "Reference": f"Direct Entry - {invoice.invoice_number}",
            "CurrencyCode": invoice.currency,
            "Status": "DRAFT",
            "LineItems": [
                {
                    "Description": line.description,
                    "Quantity": float(line.quantity),
                    "UnitAmount": float(line.unit_price),
                    "LineAmount": float(line.total),
                    "AccountCode": self._determine_xero_account(line, company_settings)
                }
                for line in invoice.line_items
            ]
        }
    
    def _determine_xero_account(self, line_item, company_settings: Dict[str, Any]) -> str:
        """Determine Xero account code for line item"""
        # Check if line item has specific account
        if hasattr(line_item, 'xero_account') and line_item.xero_account:
            return line_item.xero_account
        
        # Categorize based on description
        description = line_item.description.lower() if line_item.description else ""
        
        if any(word in description for word in ["office", "supplies"]):
            return company_settings.get("xero_office_account", "420")  # Office Expenses
        elif any(word in description for word in ["travel", "hotel"]):
            return company_settings.get("xero_travel_account", "421")  # Travel Expenses
        elif any(word in description for word in ["software", "license"]):
            return company_settings.get("xero_software_account", "422")  # Computer Expenses
        elif any(word in description for word in ["consulting", "professional"]):
            return company_settings.get("xero_professional_account", "423")  # Professional Fees
        else:
            return company_settings.get("xero_general_account", "400")  # General Expenses
    
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
            "Date": invoice.invoice_date.isoformat(),
            "DueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "InvoiceNumber": invoice.invoice_number,
            "Reference": invoice.po_number,
            "CurrencyCode": invoice.currency,
            "LineItems": [
                {
                    "Description": line.description,
                    "Quantity": float(line.quantity),
                    "UnitAmount": float(line.unit_price),
                    "LineAmount": float(line.total),
                    "AccountCode": line.gl_account if hasattr(line, 'gl_account') else company_settings.get('default_expense_account', '400')
                }
                for line in invoice.line_items
            ]
        }

class SAPAdapter(ERPAdapter):
    """SAP ERP adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.connection_config = connection_config
        self.base_url = connection_config.get("base_url")
        self.api_key = connection_config.get("api_key")
        self.company_id = connection_config.get("company_id")
        self.client_id = connection_config.get("client_id")
        
        if not all([self.base_url, self.api_key, self.company_id]):
            raise ValueError("Missing required SAP connection configuration")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "SAP-Client": self.client_id or "100"
            },
            timeout=30
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check SAP system health"""
        try:
            response = await self.client.get("/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner")
            response.raise_for_status()
            return {
                "status": "healthy",
                "erp_name": "SAP",
                "timestamp": datetime.now(UTC).isoformat(),
                "company_id": self.company_id
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "erp_name": "SAP",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to SAP"""
        try:
            # Transform invoice to SAP format
            sap_data = self._transform_to_sap_format(invoice, company_settings)
            
            # Post to SAP API
            response = await self.client.post(
                "/sap/opu/odata/sap/API_SUPPLIERINVOICE_PROCESS_SRV/A_SupplierInvoice",
                json=sap_data
            )
            response.raise_for_status()
            
            sap_response = response.json()
            invoice_data = sap_response.get("d", {})
            
            return {
                "status": "success",
                "erp_doc_id": invoice_data.get("SupplierInvoice"),
                "erp_name": "SAP",
                "posted_at": invoice_data.get("DocumentDate"),
                "sap_data": invoice_data,
                "message": "Invoice posted to SAP successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to post invoice to SAP: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to post invoice to SAP"
            }
    
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Get invoice status from SAP"""
        try:
            response = await self.client.get(
                f"/sap/opu/odata/sap/API_SUPPLIERINVOICE_PROCESS_SRV/A_SupplierInvoice('{erp_document_id}')"
            )
            response.raise_for_status()
            
            sap_data = response.json()
            invoice_data = sap_data.get("d", {})
            
            return {
                "status": invoice_data.get("SupplierInvoiceStatus", "unknown"),
                "erp_doc_id": erp_document_id,
                "erp_name": "SAP",
                "sap_data": invoice_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get invoice status from SAP: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "erp_doc_id": erp_document_id,
                "message": "Failed to get invoice status from SAP"
            }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate SAP connection"""
        try:
            response = await self.client.get("/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner?$top=1")
            response.raise_for_status()
            
            return {
                "status": "connected",
                "message": "SAP connection validated successfully",
                "company_id": self.company_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"SAP connection validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Connection validation failed: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    def _transform_to_sap_format(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to SAP format"""
        return {
            "SupplierInvoice": invoice.invoice_number,
            "FiscalYear": str(invoice.invoice_date.year),
            "CompanyCode": self.company_id,
            "DocumentDate": invoice.invoice_date.isoformat(),
            "PostingDate": invoice.invoice_date.isoformat(),
            "SupplierInvoiceIDByInvcgParty": invoice.invoice_number,
            "InvoicingParty": self._get_or_create_supplier_id(invoice.supplier_name),
            "DocumentCurrency": invoice.currency,
            "InvoiceGrossAmount": str(invoice.total_amount),
            "PaymentTerms": "0001",  # Default payment terms
            "PaymentMethod": "",
            "SupplierInvoiceItemText": f"Invoice from {invoice.supplier_name}",
            "to_SupplierInvoiceItemPurOrdRef": {
                "results": [
                    {
                        "PurchaseOrder": invoice.po_number,
                        "PurchaseOrderItem": "10"
                    }
                ] if invoice.po_number else []
            }
        }
    
    def _get_or_create_supplier_id(self, supplier_name: str) -> str:
        """Get or create supplier ID in SAP"""
        # In production, this would check if supplier exists or create new one
        return f"{supplier_name.upper().replace(' ', '')[:10]}"

class ERPIntegrationService:
    """Main ERP integration service that manages all ERP adapters"""
    
    def __init__(self):
        self.adapters = {}
        self.adapter_classes = {
            "mock": MockERPAdapter,
            "dynamics_gp": MicrosoftDynamicsGPAdapter,
            "dynamics_bc": Dynamics365BCAdapter,
            "sage": SageAdapter,
            "quickbooks": QuickBooksAdapter,
            "xero": XeroAdapter,
            "sap": SAPAdapter
        }
    
    async def register_erp_connection(
        self, 
        company_id: str, 
        erp_type: str, 
        connection_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register an ERP connection for a company"""
        try:
            if erp_type not in self.adapter_classes:
                return {
                    "status": "error",
                    "message": f"Unsupported ERP type: {erp_type}"
                }
            
            # Create adapter instance
            adapter_class = self.adapter_classes[erp_type]
            adapter = adapter_class(connection_config)
            
            # Test connection
            validation_result = await adapter.validate_connection()
            if validation_result.get("status") != "connected":
                return {
                    "status": "error",
                    "message": f"Connection validation failed: {validation_result.get('message', 'Unknown error')}"
                }
            
            # Store adapter
            self.adapters[f"{company_id}_{erp_type}"] = adapter
            
            return {
                "status": "success",
                "message": f"ERP connection {erp_type} registered successfully for company {company_id}",
                "erp_type": erp_type,
                "company_id": company_id
            }
            
        except Exception as e:
            logger.error(f"Failed to register ERP connection: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_erp_adapter(self, company_id: str, erp_type: str) -> Optional[ERPAdapter]:
        """Get ERP adapter for a company"""
        adapter_key = f"{company_id}_{erp_type}"
        return self.adapters.get(adapter_key)
    
    async def health_check_all(self, company_id: str) -> Dict[str, Any]:
        """Perform health check on all ERP connections for a company"""
        results = {}
        
        for adapter_key, adapter in self.adapters.items():
            if adapter_key.startswith(f"{company_id}_"):
                erp_type = adapter_key.split("_", 1)[1]
                try:
                    results[erp_type] = await adapter.health_check()
                except Exception as e:
                    results[erp_type] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now(UTC).isoformat()
                    }
        
        return {
            "company_id": company_id,
            "erp_systems": results,
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    async def post_invoice_to_erp(
        self, 
        company_id: str, 
        erp_type: str, 
        invoice: Invoice, 
        company_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Post invoice to specific ERP system"""
        adapter = await self.get_erp_adapter(company_id, erp_type)
        
        if not adapter:
            return {
                "status": "error",
                "message": f"No {erp_type} adapter found for company {company_id}"
            }
        
        try:
            return await adapter.post_invoice(invoice, company_settings)
        except Exception as e:
            logger.error(f"Failed to post invoice to {erp_type}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _transform_to_quickbooks_format(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to QuickBooks format"""
        return {
            "VendorRef": {
                "value": self._get_or_create_vendor_ref(invoice.supplier_name),
                "name": invoice.supplier_name
            },
            "TxnDate": invoice.invoice_date.isoformat(),
            "DueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "DocNumber": invoice.invoice_number,
            "CurrencyRef": {
                "value": invoice.currency
            },
            "Line": [
                {
                    "Amount": float(line.total),
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {
                            "value": line.gl_account if hasattr(line, 'gl_account') else company_settings.get('default_expense_account', "1")
                        }
                    },
                    "Description": line.description
                }
                for line in invoice.line_items
            ],
            "TotalAmt": float(invoice.total_with_tax or invoice.total_amount)
        }
    
    def _get_or_create_vendor_ref(self, supplier_name: str) -> str:
        """Get or create vendor reference in QuickBooks"""
        # In production, this would check if vendor exists or create new one
        return f"1"  # Default vendor ref, should be dynamically determined

class XeroAdapter(ERPAdapter):
    """Xero ERP adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.connection_config = connection_config
        # Xero-specific configuration
        self.base_url = connection_config.get("base_url", "https://api.xero.com")
        self.access_token = connection_config.get("access_token")
        self.tenant_id = connection_config.get("tenant_id")
        self.client_id = connection_config.get("client_id")
        self.client_secret = connection_config.get("client_secret")
        
        if not all([self.access_token, self.tenant_id]):
            raise ValueError("Missing required Xero connection configuration: access_token and tenant_id")
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "xero-tenant-id": self.tenant_id
            }
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Xero system health"""
        try:
            # Check organisation info to verify connection
            response = await self.client.get("/api.xro/2.0/Organisation")
            response.raise_for_status()
            
            org_data = response.json()
            organisations = org_data.get("Organisations", [])
            
            return {
                "status": "healthy",
                "erp_name": "Xero",
                "timestamp": datetime.now(UTC).isoformat(),
                "tenant_id": self.tenant_id,
                "organisation_name": organisations[0].get("Name") if organisations else "Unknown"
            }
        except Exception as e:
            logger.error(f"Xero health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "erp_name": "Xero",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to Xero"""
        try:
            # Transform invoice to Xero format
            xero_data = self._transform_to_xero_format(invoice, company_settings)
            
            # Post to Xero API
            response = await self.client.post(
                "/api.xro/2.0/Bills",
                json={"Bills": [xero_data]}
            )
            response.raise_for_status()
            
            xero_response = response.json()
            bills = xero_response.get("Bills", [])
            bill_data = bills[0] if bills else {}
            
            return {
                "status": "success",
                "erp_doc_id": bill_data.get("BillID"),
                "erp_name": "Xero",
                "posted_at": bill_data.get("UpdatedDateUTC"),
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
        return {
            "status": "posted",
            "erp_doc_id": erp_document_id,
            "erp_name": "Xero"
        }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate Xero connection"""
        try:
            # Test authentication and basic connectivity
            response = await self.client.get("/api.xro/2.0/Organisation")
            response.raise_for_status()
            
            org_data = response.json()
            organisations = org_data.get("Organisations", [])
            
            if not organisations:
                return {
                    "status": "error",
                    "message": "No organisations found for this Xero tenant",
                    "timestamp": datetime.now(UTC).isoformat()
                }
            
            return {
                "status": "connected",
                "message": "Xero connection validated successfully",
                "tenant_id": self.tenant_id,
                "organisation_name": organisations[0].get("Name"),
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
            "Contact": {
                "ContactID": self._get_or_create_contact_id(invoice.supplier_name),
                "Name": invoice.supplier_name
            },
            "Date": invoice.invoice_date.isoformat(),
            "DueDate": invoice.due_date.isoformat() if invoice.due_date else None,
            "Reference": invoice.invoice_number,
            "CurrencyCode": invoice.currency,
            "LineAmountTypes": "Exclusive",
            "LineItems": [
                {
                    "Description": line.description,
                    "Quantity": float(line.quantity),
                    "UnitAmount": float(line.unit_price),
                    "AccountCode": line.gl_account if hasattr(line, 'gl_account') else company_settings.get('default_expense_account', '400'),
                    "LineAmount": float(line.total)
                }
                for line in invoice.line_items
            ],
            "Status": "AUTHORISED"
        }
    
    def _get_or_create_contact_id(self, supplier_name: str) -> str:
        """Get or create contact ID in Xero"""
        # In production, this would check if contact exists or create new one
        return f"contact-{supplier_name.lower().replace(' ', '-')}"

class SAPAdapter(ERPAdapter):
    """SAP ERP adapter"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.connection_config = connection_config
        # SAP-specific configuration
        self.base_url = connection_config.get("base_url")
        self.username = connection_config.get("username")
        self.password = connection_config.get("password")
        self.client = connection_config.get("client", "100")
        self.system_id = connection_config.get("system_id")
        
        if not all([self.base_url, self.username, self.password, self.system_id]):
            raise ValueError("Missing required SAP connection configuration")
        
        # SAP typically uses basic auth or OAuth2
        import base64
        credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        
        self.client_http = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json",
                "X-CSRF-Token": "Fetch"
            }
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check SAP system health"""
        try:
            response = await self.client_http.get(f"/sap/opu/odata/sap/API_BUSINESS_PARTNER/$metadata")
            response.raise_for_status()
            
            return {
                "status": "healthy",
                "erp_name": "SAP",
                "timestamp": datetime.now(UTC).isoformat(),
                "system_id": self.system_id
            }
        except Exception as e:
            logger.error(f"SAP health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "erp_name": "SAP",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to SAP"""
        try:
            # Transform invoice to SAP format
            sap_data = self._transform_to_sap_format(invoice, company_settings)
            
            # Post to SAP API
            response = await self.client_http.post(
                "/sap/opu/odata/sap/API_SUPPLIER_INVOICE_SRV/A_SupplierInvoice",
                json=sap_data
            )
            response.raise_for_status()
            
            sap_response = response.json()
            invoice_data = sap_response.get("d", {})
            
            return {
                "status": "success",
                "erp_doc_id": invoice_data.get("SupplierInvoice"),
                "erp_name": "SAP",
                "posted_at": invoice_data.get("CreationDate"),
                "sap_data": invoice_data,
                "message": "Invoice posted to SAP successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to post invoice to SAP: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to post invoice to SAP"
            }
    
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Get invoice status from SAP"""
        try:
            response = await self.client_http.get(
                f"/sap/opu/odata/sap/API_SUPPLIER_INVOICE_SRV/A_SupplierInvoice('{erp_document_id}')"
            )
            response.raise_for_status()
            
            sap_data = response.json().get("d", {})
            
            return {
                "status": sap_data.get("DocumentStatus", "unknown"),
                "erp_doc_id": erp_document_id,
                "erp_name": "SAP",
                "posted_at": sap_data.get("PostingDate"),
                "sap_data": sap_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get invoice status from SAP: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "erp_doc_id": erp_document_id,
                "message": "Failed to get invoice status from SAP"
            }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate SAP connection"""
        try:
            # Test authentication and basic connectivity
            response = await self.client_http.get("/sap/opu/odata/sap/API_BUSINESS_PARTNER/$metadata")
            response.raise_for_status()
            
            return {
                "status": "connected",
                "message": "SAP connection validated successfully",
                "system_id": self.system_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"SAP connection validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Connection validation failed: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    def _transform_to_sap_format(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to SAP format"""
        return {
            "CompanyCode": company_settings.get("sap_company_code", "1000"),
            "SupplierInvoiceIDByInvcgParty": invoice.invoice_number,
            "InvoicingParty": self._get_or_create_supplier_code(invoice.supplier_name),
            "DocumentDate": invoice.invoice_date.strftime("%Y-%m-%d"),
            "PostingDate": invoice.invoice_date.strftime("%Y-%m-%d"),
            "InvoiceGrossAmount": str(invoice.total_with_tax or invoice.total_amount),
            "DocumentCurrency": invoice.currency,
            "InvoiceReference": invoice.invoice_number,
            "PaymentTerms": company_settings.get("default_payment_terms", "Z001"),
            "SupplierInvoiceItem": [
                {
                    "SupplierInvoiceItem": str(idx + 1),
                    "PurchaseOrder": line.po_number if hasattr(line, 'po_number') else None,
                    "PurchaseOrderItem": line.po_line_number if hasattr(line, 'po_line_number') else None,
                    "SupplierInvoiceItemAmount": str(line.total),
                    "QuantityInPurchaseOrderUnit": str(line.quantity),
                    "SupplierInvoiceItemText": line.description,
                    "GLAccount": line.gl_account if hasattr(line, 'gl_account') else company_settings.get('default_expense_account')
                }
                for idx, line in enumerate(invoice.line_items)
            ]
        }
    
    def _get_or_create_supplier_code(self, supplier_name: str) -> str:
        """Get or create supplier code in SAP"""
        # In production, this would check if supplier exists or create new one
        # SAP supplier codes are typically 10-digit numeric
        return f"{abs(hash(supplier_name)) % 10000000000:010d}"

class NetSuiteAdapter(ERPAdapter):
    """NetSuite ERP adapter with comprehensive PO and No-PO support"""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.connection_config = connection_config
        self.base_url = connection_config.get("base_url")
        self.consumer_key = connection_config.get("consumer_key")
        self.consumer_secret = connection_config.get("consumer_secret")
        self.token_id = connection_config.get("token_id")
        self.token_secret = connection_config.get("token_secret")
        self.account_id = connection_config.get("account_id")
        self.script_id = connection_config.get("script_id")
        self.deploy_id = connection_config.get("deploy_id")
        
        if not all([self.base_url, self.consumer_key, self.consumer_secret, 
                   self.token_id, self.token_secret, self.account_id]):
            raise ValueError("Missing required NetSuite connection configuration")
        
        # NetSuite uses OAuth 1.0a
        from requests_oauthlib import OAuth1Session
        self.oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.token_id,
            resource_owner_secret=self.token_secret,
            signature_method='HMAC-SHA256',
            realm=self.account_id
        )
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"OAuth realm=\"{self.account_id}\", oauth_consumer_key=\"{self.consumer_key}\", oauth_token=\"{self.token_id}\", oauth_signature_method=\"HMAC-SHA256\", oauth_timestamp=\"{int(datetime.now(UTC).timestamp())}\", oauth_nonce=\"{uuid.uuid4().hex}\""
            }
        )
    
    def supports_po_matching(self) -> bool:
        """NetSuite supports comprehensive PO matching through Vendor Bills"""
        return True
    
    def supports_no_po_processing(self) -> bool:
        """NetSuite supports direct Vendor Bill creation without PO"""
        return True
    
    async def process_invoice_with_po(self, invoice: Invoice, po_number: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice with Purchase Order matching in NetSuite"""
        try:
            # Transform invoice to NetSuite Vendor Bill format with PO reference
            netsuite_data = self._transform_to_netsuite_format_with_po(invoice, po_number, company_settings)
            
            # Create Vendor Bill with PO reference
            response = await self.client.post(
                f"/services/rest/record/v1/vendorbill",
                json=netsuite_data
            )
            response.raise_for_status()
            
            netsuite_response = response.json()
            
            return {
                "status": "success",
                "processing_type": "with_purchase_order",
                "erp_doc_id": netsuite_response.get("id"),
                "po_number": po_number,
                "netsuite_bill_number": netsuite_response.get("tranid"),
                "vendor_name": netsuite_response.get("entity", {}).get("name"),
                "method": "PO_REFERENCE",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": f"Vendor Bill created in NetSuite with PO reference {po_number}",
                "netsuite_data": netsuite_response
            }
            
        except Exception as e:
            logger.error(f"Failed to process NetSuite invoice with PO: {str(e)}")
            return {
                "status": "error",
                "processing_type": "with_purchase_order",
                "po_number": po_number,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to process invoice with PO in NetSuite"
            }
    
    async def process_invoice_without_po(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice without PO as direct Vendor Bill in NetSuite"""
        try:
            # Transform invoice to NetSuite Vendor Bill format
            netsuite_data = self._transform_to_netsuite_format_no_po(invoice, company_settings)
            
            # Create Vendor Bill directly
            response = await self.client.post(
                f"/services/rest/record/v1/vendorbill",
                json=netsuite_data
            )
            response.raise_for_status()
            
            netsuite_response = response.json()
            
            return {
                "status": "success",
                "processing_type": "no_purchase_order",
                "erp_doc_id": netsuite_response.get("id"),
                "netsuite_bill_number": netsuite_response.get("tranid"),
                "vendor_name": netsuite_response.get("entity", {}).get("name"),
                "method": "DIRECT_BILL",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Vendor Bill created directly in NetSuite",
                "netsuite_data": netsuite_response
            }
            
        except Exception as e:
            logger.error(f"Failed to process NetSuite invoice without PO: {str(e)}")
            return {
                "status": "error",
                "processing_type": "no_purchase_order",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "message": "Failed to process invoice without PO in NetSuite"
            }
    
    def _transform_to_netsuite_format_with_po(self, invoice: Invoice, po_number: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to NetSuite Vendor Bill format with PO reference"""
        return {
            "entity": {
                "id": self._get_or_create_vendor_id(invoice.supplier_name)
            },
            "tranid": invoice.invoice_number,
            "trandate": invoice.invoice_date.strftime("%Y-%m-%d"),
            "duedate": invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else None,
            "currency": {
                "id": self._get_currency_id(invoice.currency)
            },
            "memo": f"Invoice {invoice.invoice_number} matched to PO {po_number}",
            "purchaseorder": {
                "id": po_number
            },
            "item": [
                {
                    "item": {
                        "id": self._get_or_create_item_id(line.description)
                    },
                    "quantity": float(line.quantity),
                    "rate": float(line.unit_price),
                    "amount": float(line.total),
                    "description": f"{line.description} (PO: {po_number})",
                    "class": {
                        "id": self._get_department_class(line.department, company_settings)
                    }
                }
                for line in invoice.line_items
            ]
        }
    
    def _transform_to_netsuite_format_no_po(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to NetSuite Vendor Bill format without PO"""
        return {
            "entity": {
                "id": self._get_or_create_vendor_id(invoice.supplier_name)
            },
            "tranid": invoice.invoice_number,
            "trandate": invoice.invoice_date.strftime("%Y-%m-%d"),
            "duedate": invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else None,
            "currency": {
                "id": self._get_currency_id(invoice.currency)
            },
            "memo": f"Direct invoice entry: {invoice.invoice_number}",
            "item": [
                {
                    "item": {
                        "id": self._get_or_create_item_id(line.description)
                    },
                    "quantity": float(line.quantity),
                    "rate": float(line.unit_price),
                    "amount": float(line.total),
                    "description": line.description,
                    "class": {
                        "id": self._get_department_class(line.department, company_settings)
                    },
                    "account": {
                        "id": self._determine_netsuite_account(line, company_settings)
                    }
                }
                for line in invoice.line_items
            ]
        }
    
    def _get_or_create_vendor_id(self, supplier_name: str) -> str:
        """Get or create vendor ID in NetSuite"""
        # In production, this would search for existing vendor or create new one
        return f"vendor-{supplier_name.lower().replace(' ', '-')}"
    
    def _get_or_create_item_id(self, description: str) -> str:
        """Get or create item ID in NetSuite"""
        # In production, this would search for existing item or create new one
        return f"item-{description.lower().replace(' ', '-')[:20]}"
    
    def _get_currency_id(self, currency_code: str) -> str:
        """Get NetSuite currency ID"""
        currency_map = {
            "USD": "1",
            "EUR": "2", 
            "GBP": "3",
            "CAD": "4",
            "AUD": "5"
        }
        return currency_map.get(currency_code, "1")  # Default to USD
    
    def _get_department_class(self, department: str, company_settings: Dict[str, Any]) -> str:
        """Get NetSuite department class ID"""
        if not department:
            return company_settings.get("default_department_class", "1")
        
        # Map department to class ID
        dept_map = company_settings.get("department_class_mapping", {})
        return dept_map.get(department, company_settings.get("default_department_class", "1"))
    
    def _determine_netsuite_account(self, line_item, company_settings: Dict[str, Any]) -> str:
        """Determine NetSuite account for line item"""
        if hasattr(line_item, 'netsuite_account') and line_item.netsuite_account:
            return line_item.netsuite_account
        
        description = line_item.description.lower() if line_item.description else ""
        
        if any(word in description for word in ["office", "supplies"]):
            return company_settings.get("netsuite_office_account", "5000")
        elif any(word in description for word in ["travel", "hotel"]):
            return company_settings.get("netsuite_travel_account", "5100")
        elif any(word in description for word in ["software", "license"]):
            return company_settings.get("netsuite_software_account", "5200")
        elif any(word in description for word in ["consulting", "professional"]):
            return company_settings.get("netsuite_professional_account", "5300")
        else:
            return company_settings.get("netsuite_general_account", "5000")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check NetSuite system health"""
        try:
            response = await self.client.get("/services/rest/record/v1/metadata-catalog")
            response.raise_for_status()
            return {
                "status": "healthy",
                "erp_name": "NetSuite",
                "timestamp": datetime.now(UTC).isoformat(),
                "account_id": self.account_id
            }
        except Exception as e:
            logger.error(f"NetSuite health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "erp_name": "NetSuite",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
    
    async def post_invoice(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to NetSuite"""
        try:
            netsuite_data = self._transform_to_netsuite_format_no_po(invoice, company_settings)
            
            response = await self.client.post(
                f"/services/rest/record/v1/vendorbill",
                json=netsuite_data
            )
            response.raise_for_status()
            
            netsuite_response = response.json()
            
            return {
                "status": "success",
                "erp_doc_id": netsuite_response.get("id"),
                "erp_name": "NetSuite",
                "posted_at": netsuite_response.get("trandate"),
                "netsuite_data": netsuite_response,
                "message": "Invoice posted to NetSuite successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to post invoice to NetSuite: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to post invoice to NetSuite"
            }
    
    async def get_invoice_status(self, erp_document_id: str) -> Dict[str, Any]:
        """Get invoice status from NetSuite"""
        try:
            response = await self.client.get(f"/services/rest/record/v1/vendorbill/{erp_document_id}")
            response.raise_for_status()
            
            netsuite_data = response.json()
            
            return {
                "status": netsuite_data.get("status", "unknown"),
                "erp_doc_id": erp_document_id,
                "erp_name": "NetSuite",
                "netsuite_data": netsuite_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get invoice status from NetSuite: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "erp_doc_id": erp_document_id,
                "message": "Failed to get invoice status from NetSuite"
            }
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate NetSuite connection"""
        try:
            response = await self.client.get("/services/rest/record/v1/metadata-catalog")
            response.raise_for_status()
            
            return {
                "status": "connected",
                "message": "NetSuite connection validated successfully",
                "account_id": self.account_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"NetSuite connection validation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Connection validation failed: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat()
            }

class ERPIntegrationService:
    """Main ERP integration service"""
    
    def __init__(self):
        self.adapters = {
            "mock": MockERPAdapter()
        }
        
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
        
        if hasattr(settings, 'QUICKBOOKS_CONFIG') and settings.QUICKBOOKS_CONFIG:
            try:
                self.adapters["quickbooks"] = QuickBooksAdapter(settings.QUICKBOOKS_CONFIG)
            except Exception as e:
                logger.warning(f"Failed to initialize QuickBooks adapter: {e}")
        
        if hasattr(settings, 'SAGE_CONFIG') and settings.SAGE_CONFIG:
            try:
                self.adapters["sage"] = SageAdapter(settings.SAGE_CONFIG)
            except Exception as e:
                logger.warning(f"Failed to initialize Sage adapter: {e}")
        
        if hasattr(settings, 'SAP_CONFIG') and settings.SAP_CONFIG:
            try:
                self.adapters["sap"] = SAPAdapter(settings.SAP_CONFIG)
            except Exception as e:
                logger.warning(f"Failed to initialize SAP adapter: {e}")
        
        if hasattr(settings, 'NETSUITE_CONFIG') and settings.NETSUITE_CONFIG:
            try:
                self.adapters["netsuite"] = NetSuiteAdapter(settings.NETSUITE_CONFIG)
            except Exception as e:
                logger.warning(f"Failed to initialize NetSuite adapter: {e}")
        
        self.default_adapter = "mock"
    
    def get_adapter(self, erp_type: str) -> ERPAdapter:
        """Get ERP adapter by type"""
        if erp_type not in self.adapters:
            logger.warning(f"Unknown ERP type: {erp_type}, using default")
            return self.adapters[self.default_adapter]
        return self.adapters[erp_type]
    
    async def post_invoice(self, invoice: Invoice, erp_type: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Post invoice to specified ERP system"""
        adapter = self.get_adapter(erp_type)
        
        try:
            # Validate connection first
            connection_status = await adapter.validate_connection()
            if connection_status["status"] != "connected":
                raise ConnectionError(f"ERP connection failed: {connection_status}")
            
            # Post invoice
            result = await adapter.post_invoice(invoice, company_settings)
            
            # Update invoice status
            if result["status"] == "success":
                invoice.posted_to_erp = True
                invoice.erp_document_id = result["erp_doc_id"]
                invoice.erp_posting_date = datetime.now(UTC)
                invoice.status = InvoiceStatus.POSTED_TO_ERP
            
            return result
            
        except Exception as e:
            logger.error(f"ERP posting failed: {e}")
            invoice.erp_error_message = str(e)
            invoice.status = InvoiceStatus.ERROR
            raise
    
    async def check_invoice_status(self, erp_document_id: str, erp_type: str) -> Dict[str, Any]:
        """Check invoice status in ERP system"""
        adapter = self.get_adapter(erp_type)
        return await adapter.get_invoice_status(erp_document_id)
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Check health of all ERP adapters"""
        health_status = {}
        
        for erp_type, adapter in self.adapters.items():
            try:
                status = await adapter.health_check()
                health_status[erp_type] = status
            except Exception as e:
                health_status[erp_type] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat()
                }
        
        return health_status
    
    async def validate_erp_configuration(self, erp_type: str, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ERP configuration for a company"""
        adapter = self.get_adapter(erp_type)
        
        try:
            # Test connection
            connection_status = await adapter.validate_connection()
            
            # Test with sample data if connection successful
            if connection_status["status"] == "connected":
                # Create a test invoice for validation
                from src.models.invoice import Invoice
                test_invoice = Invoice(
                    invoice_number="TEST-001",
                    supplier_name="Test Supplier",
                    total_amount=100.00,
                    currency="USD"
                )
                
                # Try to post test invoice
                test_result = await adapter.post_invoice(test_invoice, company_settings)
                
                return {
                    "status": "valid",
                    "erp_type": erp_type,
                    "connection": connection_status,
                    "test_posting": test_result,
                    "validated_at": datetime.now(UTC).isoformat()
                }
            else:
                return {
                    "status": "invalid",
                    "erp_type": erp_type,
                    "connection": connection_status,
                    "error": "Connection validation failed"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "erp_type": erp_type,
                "error": str(e),
                "validated_at": datetime.now(UTC).isoformat()
            }
