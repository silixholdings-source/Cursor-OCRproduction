"""
ERP Automation Service - Fully Automated ERP Integration
Handles scheduled syncs, real-time monitoring, and automated error recovery
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import json
from enum import Enum

from core.config import settings
from core.database import get_db
from src.models.invoice import Invoice, InvoiceStatus
from src.models.company import Company
from src.models.user import User
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from services.erp import ERPIntegrationService
from services.dynamics_gp_integration import DynamicsGPIntegration

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class AutomationRule(Enum):
    AUTO_SYNC_ON_APPROVAL = "auto_sync_on_approval"
    SCHEDULED_SYNC = "scheduled_sync"
    REAL_TIME_MONITORING = "real_time_monitoring"
    ERROR_AUTO_RECOVERY = "error_auto_recovery"
    DUPLICATE_DETECTION = "duplicate_detection"
    VENDOR_AUTO_MAPPING = "vendor_auto_mapping"

class ERPAutomationService:
    """Fully automated ERP integration service"""
    
    def __init__(self):
        self.erp_service = ERPIntegrationService()
        self.dynamics_gp = DynamicsGPIntegration()
        self.sync_queue = []
        self.monitoring_active = True
        self.automation_rules = {
            AutomationRule.AUTO_SYNC_ON_APPROVAL: True,
            AutomationRule.SCHEDULED_SYNC: True,
            AutomationRule.REAL_TIME_MONITORING: True,
            AutomationRule.ERROR_AUTO_RECOVERY: True,
            AutomationRule.DUPLICATE_DETECTION: True,
            AutomationRule.VENDOR_AUTO_MAPPING: True
        }
        
    async def start_automation_engine(self):
        """Start the automation engine with all automated processes"""
        logger.info("🚀 Starting ERP Automation Engine...")
        
        # Start all automation tasks concurrently
        tasks = [
            self._scheduled_sync_worker(),
            self._real_time_monitor(),
            self._error_recovery_worker(),
            self._duplicate_detection_worker(),
            self._vendor_mapping_worker(),
            self._health_monitor()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def auto_sync_on_approval(self, invoice_id: str, company_id: str, db: Session) -> Dict[str, Any]:
        """Automatically sync invoice to ERP when approved"""
        if not self.automation_rules[AutomationRule.AUTO_SYNC_ON_APPROVAL]:
            return {"status": "disabled", "message": "Auto-sync on approval is disabled"}
        
        try:
            logger.info(f"🔄 Auto-syncing approved invoice {invoice_id} to ERP...")
            
            # Get invoice
            invoice = db.query(Invoice).filter(
                and_(Invoice.id == invoice_id, Invoice.company_id == company_id)
            ).first()
            
            if not invoice:
                return {"status": "error", "message": "Invoice not found"}
            
            if invoice.status != InvoiceStatus.APPROVED:
                return {"status": "error", "message": "Invoice not approved"}
            
            # Get company ERP configuration
            company = db.query(Company).filter(Company.id == company_id).first()
            erp_config = self._get_erp_config(company)
            
            if not erp_config:
                return {"status": "error", "message": "No ERP configuration found"}
            
            # Determine ERP system and sync
            sync_results = {}
            
            # Dynamics GP Integration
            if erp_config.get("dynamics_gp_enabled"):
                gp_result = await self._sync_to_dynamics_gp(invoice, erp_config["dynamics_gp"])
                sync_results["dynamics_gp"] = gp_result
            
            # SAP Integration
            if erp_config.get("sap_enabled"):
                sap_result = await self._sync_to_sap(invoice, erp_config["sap"])
                sync_results["sap"] = sap_result
            
            # QuickBooks Integration
            if erp_config.get("quickbooks_enabled"):
                qb_result = await self._sync_to_quickbooks(invoice, erp_config["quickbooks"])
                sync_results["quickbooks"] = qb_result
            
            # Xero Integration
            if erp_config.get("xero_enabled"):
                xero_result = await self._sync_to_xero(invoice, erp_config["xero"])
                sync_results["xero"] = xero_result
            
            # Update invoice with ERP sync status
            await self._update_invoice_erp_status(invoice, sync_results, db)
            
            # Create audit log
            self._create_audit_log(
                db, invoice.approved_by_id, company_id,
                AuditAction.CREATE, AuditResourceType.INVOICE,
                str(invoice.id), f"Invoice auto-synced to ERP systems: {list(sync_results.keys())}"
            )
            
            return {
                "status": "success",
                "message": f"Invoice automatically synced to {len(sync_results)} ERP systems",
                "sync_results": sync_results,
                "synced_at": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Auto-sync failed for invoice {invoice_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Auto-sync failed: {str(e)}",
                "invoice_id": invoice_id
            }
    
    async def _scheduled_sync_worker(self):
        """Background worker for scheduled ERP synchronization"""
        logger.info("📅 Starting scheduled sync worker...")
        
        while self.monitoring_active:
            try:
                if self.automation_rules[AutomationRule.SCHEDULED_SYNC]:
                    await self._run_scheduled_sync()
                
                # Run every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Scheduled sync worker error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _run_scheduled_sync(self):
        """Run scheduled synchronization for all companies"""
        logger.info("🔄 Running scheduled ERP sync...")
        
        # Get database session
        db = next(get_db())
        
        try:
            # Get all companies with ERP integrations
            companies = db.query(Company).filter(
                or_(
                    Company.erp_dynamics_gp_enabled == True,
                    Company.erp_sap_enabled == True,
                    Company.erp_quickbooks_enabled == True,
                    Company.erp_xero_enabled == True
                )
            ).all()
            
            for company in companies:
                await self._sync_company_data(company, db)
                
        except Exception as e:
            logger.error(f"Scheduled sync failed: {str(e)}")
        finally:
            db.close()
    
    async def _sync_company_data(self, company: Company, db: Session):
        """Sync all pending data for a company"""
        try:
            # Get approved invoices not yet synced to ERP
            pending_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.company_id == company.id,
                    Invoice.status == InvoiceStatus.APPROVED,
                    Invoice.erp_sync_status.in_(["pending", "failed"])
                )
            ).all()
            
            logger.info(f"📋 Syncing {len(pending_invoices)} invoices for company {company.name}")
            
            for invoice in pending_invoices:
                sync_result = await self.auto_sync_on_approval(
                    str(invoice.id), str(company.id), db
                )
                
                if sync_result["status"] == "success":
                    logger.info(f"✅ Invoice {invoice.invoice_number} synced successfully")
                else:
                    logger.warning(f"⚠️ Invoice {invoice.invoice_number} sync failed: {sync_result.get('message')}")
                
                # Small delay between syncs to avoid overwhelming ERP systems
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Company sync failed for {company.name}: {str(e)}")
    
    async def _real_time_monitor(self):
        """Real-time monitoring of ERP system health and sync status"""
        logger.info("📡 Starting real-time ERP monitor...")
        
        while self.monitoring_active:
            try:
                if self.automation_rules[AutomationRule.REAL_TIME_MONITORING]:
                    await self._check_erp_health()
                    await self._monitor_sync_queues()
                
                # Monitor every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Real-time monitor error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_erp_health(self):
        """Check health of all configured ERP systems"""
        db = next(get_db())
        
        try:
            companies = db.query(Company).filter(
                or_(
                    Company.erp_dynamics_gp_enabled == True,
                    Company.erp_sap_enabled == True,
                    Company.erp_quickbooks_enabled == True,
                    Company.erp_xero_enabled == True
                )
            ).all()
            
            for company in companies:
                erp_config = self._get_erp_config(company)
                
                # Check each enabled ERP system
                if erp_config.get("dynamics_gp_enabled"):
                    health = await self.dynamics_gp.health_check(erp_config["dynamics_gp"]["company_db"])
                    await self._log_health_status("Dynamics GP", company.id, health)
                
                if erp_config.get("sap_enabled"):
                    health = await self.erp_service.health_check("sap")
                    await self._log_health_status("SAP", company.id, health)
                
                if erp_config.get("quickbooks_enabled"):
                    health = await self.erp_service.health_check("quickbooks")
                    await self._log_health_status("QuickBooks", company.id, health)
                
                if erp_config.get("xero_enabled"):
                    health = await self.erp_service.health_check("xero")
                    await self._log_health_status("Xero", company.id, health)
                    
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
        finally:
            db.close()
    
    async def _error_recovery_worker(self):
        """Automated error recovery for failed ERP operations"""
        logger.info("🔧 Starting error recovery worker...")
        
        while self.monitoring_active:
            try:
                if self.automation_rules[AutomationRule.ERROR_AUTO_RECOVERY]:
                    await self._retry_failed_syncs()
                
                # Run every 10 minutes
                await asyncio.sleep(600)
                
            except Exception as e:
                logger.error(f"Error recovery worker failed: {str(e)}")
                await asyncio.sleep(300)
    
    async def _retry_failed_syncs(self):
        """Automatically retry failed ERP synchronizations"""
        db = next(get_db())
        
        try:
            # Get invoices with failed ERP sync that are eligible for retry
            failed_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.erp_sync_status == "failed",
                    Invoice.erp_retry_count < 3,
                    Invoice.approved_at > datetime.now(UTC) - timedelta(hours=24)
                )
            ).all()
            
            logger.info(f"🔄 Retrying {len(failed_invoices)} failed ERP syncs...")
            
            for invoice in failed_invoices:
                # Increment retry count
                invoice.erp_retry_count = (invoice.erp_retry_count or 0) + 1
                db.commit()
                
                # Retry sync
                retry_result = await self.auto_sync_on_approval(
                    str(invoice.id), str(invoice.company_id), db
                )
                
                if retry_result["status"] == "success":
                    logger.info(f"✅ Retry successful for invoice {invoice.invoice_number}")
                    invoice.erp_sync_status = "completed"
                else:
                    logger.warning(f"⚠️ Retry failed for invoice {invoice.invoice_number}")
                    if invoice.erp_retry_count >= 3:
                        invoice.erp_sync_status = "failed_final"
                        # Send notification to admin
                        await self._notify_admin_of_failure(invoice, retry_result)
                
                db.commit()
                await asyncio.sleep(2)  # Delay between retries
                
        except Exception as e:
            logger.error(f"Error recovery failed: {str(e)}")
        finally:
            db.close()
    
    async def _duplicate_detection_worker(self):
        """Automated duplicate invoice detection across ERP systems"""
        logger.info("🔍 Starting duplicate detection worker...")
        
        while self.monitoring_active:
            try:
                if self.automation_rules[AutomationRule.DUPLICATE_DETECTION]:
                    await self._detect_duplicates()
                
                # Run every 15 minutes
                await asyncio.sleep(900)
                
            except Exception as e:
                logger.error(f"Duplicate detection worker failed: {str(e)}")
                await asyncio.sleep(300)
    
    async def _vendor_mapping_worker(self):
        """Automated vendor mapping and standardization"""
        logger.info("🏢 Starting vendor mapping worker...")
        
        while self.monitoring_active:
            try:
                if self.automation_rules[AutomationRule.VENDOR_AUTO_MAPPING]:
                    await self._auto_map_vendors()
                
                # Run every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Vendor mapping worker failed: {str(e)}")
                await asyncio.sleep(600)
    
    async def _health_monitor(self):
        """Continuous health monitoring of all ERP systems"""
        logger.info("💓 Starting ERP health monitor...")
        
        while self.monitoring_active:
            try:
                await self._comprehensive_health_check()
                
                # Monitor every 2 minutes
                await asyncio.sleep(120)
                
            except Exception as e:
                logger.error(f"Health monitor failed: {str(e)}")
                await asyncio.sleep(300)
    
    async def _sync_to_dynamics_gp(self, invoice: Invoice, gp_config: Dict[str, Any]) -> Dict[str, Any]:
        """Automated sync to Dynamics GP with 2-way and 3-way matching"""
        try:
            logger.info(f"🔄 Auto-syncing invoice {invoice.invoice_number} to Dynamics GP...")
            
            # Determine matching strategy based on invoice data
            if invoice.po_number:
                # 3-way matching (Invoice + PO + Receipt)
                result = await self.dynamics_gp.perform_three_way_match(
                    invoice_id=str(invoice.id),
                    company_db=gp_config["company_db"],
                    po_number=invoice.po_number,
                    include_all_shipments=True
                )
                
                if result["match_status"] == "matched":
                    # Auto-post to Payables Management
                    post_result = await self.dynamics_gp.post_to_payables_management(
                        invoice_data=result["matched_data"],
                        company_db=gp_config["company_db"]
                    )
                    
                    return {
                        "status": "success",
                        "method": "3-way_match_auto_post",
                        "match_result": result,
                        "post_result": post_result,
                        "erp_doc_id": post_result.get("voucher_number"),
                        "message": "Invoice automatically matched and posted to GP"
                    }
                else:
                    # Partial match - flag for manual review
                    return {
                        "status": "partial_match",
                        "method": "3-way_match_manual_review",
                        "match_result": result,
                        "message": "Invoice requires manual review for matching discrepancies"
                    }
            else:
                # 2-way matching (Invoice + PO) or direct posting
                result = await self.dynamics_gp.perform_two_way_match(
                    invoice_id=str(invoice.id),
                    company_db=gp_config["company_db"]
                )
                
                if result["match_status"] == "matched" or not invoice.po_number:
                    # Auto-post to Payables Management
                    post_result = await self.dynamics_gp.post_to_payables_management(
                        invoice_data=result.get("matched_data", self._transform_invoice_to_gp_format(invoice)),
                        company_db=gp_config["company_db"]
                    )
                    
                    return {
                        "status": "success",
                        "method": "2-way_match_auto_post" if invoice.po_number else "direct_post",
                        "match_result": result if invoice.po_number else None,
                        "post_result": post_result,
                        "erp_doc_id": post_result.get("voucher_number"),
                        "message": "Invoice automatically posted to GP Payables Management"
                    }
                else:
                    return {
                        "status": "match_failed",
                        "method": "2-way_match_failed",
                        "match_result": result,
                        "message": "Invoice matching failed - manual intervention required"
                    }
                    
        except Exception as e:
            logger.error(f"Dynamics GP sync failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Dynamics GP sync failed: {str(e)}"
            }
    
    async def _sync_to_sap(self, invoice: Invoice, sap_config: Dict[str, Any]) -> Dict[str, Any]:
        """Automated sync to SAP with intelligent document matching"""
        try:
            logger.info(f"🔄 Auto-syncing invoice {invoice.invoice_number} to SAP...")
            
            # Use SAP adapter for automated posting
            adapter = self.erp_service.get_adapter("sap")
            if not adapter:
                return {"status": "error", "message": "SAP adapter not configured"}
            
            # Transform invoice data to SAP format
            sap_data = self._transform_invoice_to_sap_format(invoice, sap_config)
            
            # Post to SAP
            result = await adapter.post_invoice(invoice, sap_config)
            
            return {
                "status": "success" if result["status"] == "success" else "error",
                "method": "sap_auto_post",
                "erp_doc_id": result.get("erp_doc_id"),
                "sap_data": sap_data,
                "message": result.get("message", "SAP sync completed")
            }
            
        except Exception as e:
            logger.error(f"SAP sync failed: {str(e)}")
            return {
                "status": "error",
                "message": f"SAP sync failed: {str(e)}"
            }
    
    async def _sync_to_quickbooks(self, invoice: Invoice, qb_config: Dict[str, Any]) -> Dict[str, Any]:
        """Automated sync to QuickBooks with vendor matching"""
        try:
            logger.info(f"🔄 Auto-syncing invoice {invoice.invoice_number} to QuickBooks...")
            
            adapter = self.erp_service.get_adapter("quickbooks")
            if not adapter:
                return {"status": "error", "message": "QuickBooks adapter not configured"}
            
            # Auto-map vendor
            vendor_ref = await self._auto_map_vendor_quickbooks(invoice.supplier_name, qb_config)
            
            # Post invoice as bill
            result = await adapter.post_invoice(invoice, {**qb_config, "vendor_ref": vendor_ref})
            
            return {
                "status": "success" if result["status"] == "success" else "error",
                "method": "quickbooks_auto_post",
                "vendor_ref": vendor_ref,
                "erp_doc_id": result.get("erp_doc_id"),
                "message": result.get("message", "QuickBooks sync completed")
            }
            
        except Exception as e:
            logger.error(f"QuickBooks sync failed: {str(e)}")
            return {
                "status": "error",
                "message": f"QuickBooks sync failed: {str(e)}"
            }
    
    async def _sync_to_xero(self, invoice: Invoice, xero_config: Dict[str, Any]) -> Dict[str, Any]:
        """Automated sync to Xero with intelligent categorization"""
        try:
            logger.info(f"🔄 Auto-syncing invoice {invoice.invoice_number} to Xero...")
            
            adapter = self.erp_service.get_adapter("xero")
            if not adapter:
                return {"status": "error", "message": "Xero adapter not configured"}
            
            # Auto-categorize invoice
            category = await self._auto_categorize_invoice(invoice)
            
            # Post to Xero
            result = await adapter.post_invoice(invoice, {**xero_config, "category": category})
            
            return {
                "status": "success" if result["status"] == "success" else "error",
                "method": "xero_auto_post",
                "category": category,
                "erp_doc_id": result.get("erp_doc_id"),
                "message": result.get("message", "Xero sync completed")
            }
            
        except Exception as e:
            logger.error(f"Xero sync failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Xero sync failed: {str(e)}"
            }
    
    def _get_erp_config(self, company: Company) -> Dict[str, Any]:
        """Get ERP configuration for a company"""
        config = {}
        
        if company.erp_dynamics_gp_enabled:
            config["dynamics_gp_enabled"] = True
            config["dynamics_gp"] = {
                "server": company.erp_dynamics_gp_server,
                "company_db": company.erp_dynamics_gp_database,
                "username": company.erp_dynamics_gp_username,
                "password": company.erp_dynamics_gp_password
            }
        
        if company.erp_sap_enabled:
            config["sap_enabled"] = True
            config["sap"] = {
                "base_url": company.erp_sap_base_url,
                "username": company.erp_sap_username,
                "password": company.erp_sap_password,
                "client": company.erp_sap_client
            }
        
        if company.erp_quickbooks_enabled:
            config["quickbooks_enabled"] = True
            config["quickbooks"] = {
                "company_id": company.erp_quickbooks_company_id,
                "access_token": company.erp_quickbooks_access_token,
                "refresh_token": company.erp_quickbooks_refresh_token
            }
        
        if company.erp_xero_enabled:
            config["xero_enabled"] = True
            config["xero"] = {
                "tenant_id": company.erp_xero_tenant_id,
                "access_token": company.erp_xero_access_token,
                "refresh_token": company.erp_xero_refresh_token
            }
        
        return config
    
    async def _update_invoice_erp_status(self, invoice: Invoice, sync_results: Dict[str, Any], db: Session):
        """Update invoice with ERP sync status"""
        try:
            # Determine overall sync status
            all_success = all(result.get("status") == "success" for result in sync_results.values())
            any_success = any(result.get("status") == "success" for result in sync_results.values())
            
            if all_success:
                invoice.erp_sync_status = "completed"
            elif any_success:
                invoice.erp_sync_status = "partial"
            else:
                invoice.erp_sync_status = "failed"
            
            # Store sync results
            invoice.erp_sync_results = json.dumps(sync_results)
            invoice.erp_synced_at = datetime.now(UTC)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update invoice ERP status: {str(e)}")
            db.rollback()
    
    def _create_audit_log(self, db: Session, user_id: str, company_id: str, 
                         action: AuditAction, resource_type: AuditResourceType, 
                         resource_id: str, details: str):
        """Create audit log entry"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                company_id=company_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                timestamp=datetime.now(UTC)
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
    
    async def _notify_admin_of_failure(self, invoice: Invoice, error_result: Dict[str, Any]):
        """Notify admin of persistent ERP sync failures"""
        # In production, this would send email/Slack notification
        logger.error(f"🚨 ADMIN ALERT: Invoice {invoice.invoice_number} failed ERP sync after 3 retries")
        logger.error(f"Error details: {error_result}")
    
    def _transform_invoice_to_gp_format(self, invoice: Invoice) -> Dict[str, Any]:
        """Transform invoice to Dynamics GP format"""
        return {
            "vendor_id": invoice.supplier_name,
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "total_amount": float(invoice.total_amount),
            "description": invoice.description,
            "purchase_order": invoice.po_number
        }
    
    def _transform_invoice_to_sap_format(self, invoice: Invoice, sap_config: Dict[str, Any]) -> Dict[str, Any]:
        """Transform invoice to SAP format"""
        return {
            "DocumentType": "KR",  # Vendor Invoice
            "CompanyCode": sap_config.get("company_code", "1000"),
            "DocumentDate": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            "PostingDate": datetime.now(UTC).isoformat(),
            "DocumentHeaderText": invoice.description,
            "Reference": invoice.invoice_number,
            "BusinessPartner": invoice.supplier_name,
            "DocumentCurrency": invoice.currency or "USD",
            "GrossAmount": float(invoice.total_amount)
        }
    
    async def _auto_map_vendor_quickbooks(self, vendor_name: str, qb_config: Dict[str, Any]) -> str:
        """Automatically map vendor to QuickBooks vendor ID"""
        # In production, this would query QB API for existing vendors
        # and create new ones if needed
        return "1"  # Default vendor ref
    
    async def _auto_categorize_invoice(self, invoice: Invoice) -> str:
        """Automatically categorize invoice for proper GL coding"""
        # Simple categorization based on description
        description = (invoice.description or "").lower()
        
        if any(word in description for word in ["software", "license", "subscription"]):
            return "Software & Technology"
        elif any(word in description for word in ["office", "supplies", "equipment"]):
            return "Office Expenses"
        elif any(word in description for word in ["marketing", "advertising", "promotion"]):
            return "Marketing & Advertising"
        elif any(word in description for word in ["travel", "hotel", "flight", "transportation"]):
            return "Travel & Entertainment"
        elif any(word in description for word in ["consulting", "professional", "service"]):
            return "Professional Services"
        else:
            return "General Expenses"

# Global automation service instance
erp_automation = ERPAutomationService()

async def start_erp_automation():
    """Start the ERP automation engine"""
    await erp_automation.start_automation_engine()

