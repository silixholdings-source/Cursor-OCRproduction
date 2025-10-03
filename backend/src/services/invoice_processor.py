"""
Invoice Processing Service - Core Business Logic
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, UTC
from decimal import Decimal
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
from src.models.user import User, UserRole
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from services.ocr import MockOCRService, AzureOCRService
from services.simple_ocr import SimpleOCRService
from services.workflow_engine import workflow_engine, WorkflowStatus
from services.erp import ERPIntegrationService
from core.config import settings

logger = logging.getLogger(__name__)

class InvoiceProcessor:
    """Core invoice processing service with business logic"""
    
    def __init__(self):
        # Use simple OCR service for immediate functionality
        self.ocr_service = SimpleOCRService()
        self.erp_service = ERPIntegrationService()
        
        # Business rules configuration
        self.business_rules = {
            "duplicate_threshold": 0.95,  # 95% similarity for duplicate detection
            "fraud_threshold": 0.8,       # 80% confidence for fraud detection
            "auto_approval_limit": 1000.0, # Auto-approve invoices under $1000
            "max_processing_time": 48,     # Max processing time in hours
            "retry_attempts": 3,           # Max retry attempts for ERP posting
            "batch_size": 100              # Batch size for bulk operations
        }
        
        # Initialize ML service (mock for now)
        try:
            from services.advanced_ml_models import advanced_ml_service
            self.ml_service = advanced_ml_service
        except ImportError:
            logger.warning("Advanced ML service not available, using basic processing")
            self.ml_service = None
    
    async def process_invoice(self, file_path: str, company_id: str, user_id: str, db: Session) -> Dict[str, Any]:
        """Main invoice processing workflow"""
        try:
            logger.info(f"Starting invoice processing for file: {file_path}")
            
            # Step 1: Advanced OCR Extraction
            ocr_result = await self.ocr_service.extract_invoice(file_path, company_id)
            
            # Step 2: Validate extracted data
            validation_result = self._validate_invoice_data(ocr_result)
            if not validation_result["is_valid"]:
                return {
                    "status": "error",
                    "message": "Invoice data validation failed",
                    "errors": validation_result["errors"]
                }
            
            # Step 3: Create invoice record
            invoice = self._create_invoice_from_ocr(ocr_result, company_id, user_id, file_path)
            db.add(invoice)
            db.commit()
            db.refresh(invoice)
            
            # Step 4: Check for duplicates
            duplicate_check = await self._check_for_duplicates(invoice, company_id, db)
            if duplicate_check["is_duplicate"]:
                invoice.status = InvoiceStatus.REJECTED
                invoice.rejection_reason = f"Duplicate invoice detected: {duplicate_check['duplicate_id']}"
                db.commit()
                
                return {
                    "status": "duplicate",
                    "message": "Duplicate invoice detected",
                    "invoice_id": str(invoice.id),
                    "duplicate_id": duplicate_check["duplicate_id"]
                }
            
            # Step 5: Advanced AI Analysis
            ai_analysis = await self._run_ai_analysis(invoice, company_id, db)
            
            # Step 6: Create approval workflow
            workflow = await self._create_approval_workflow(invoice, company_id, ai_analysis)
            
            # Step 7: Determine next action based on analysis
            next_action = self._determine_next_action(invoice, ai_analysis)
            
            # Update invoice with analysis results
            invoice.ml_analysis = ai_analysis
            workflow_id = workflow.get("workflow_id") if isinstance(workflow, dict) else workflow.workflow_id
            invoice.workflow_id = workflow_id
            invoice.status = InvoiceStatus.PENDING_APPROVAL if next_action == "approval_required" else InvoiceStatus.APPROVED
            db.commit()
            
            return {
                "status": "success",
                "invoice_id": str(invoice.id),
                "workflow_id": workflow_id,
                "ai_analysis": ai_analysis,
                "next_action": next_action,
                "processing_stage": "analysis_complete"
            }
            
        except Exception as e:
            logger.error(f"Invoice processing failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}"
            }
    
    async def _run_ai_analysis(self, invoice: Invoice, company_id: str, db: Session) -> Dict[str, Any]:
        """Run comprehensive AI analysis on invoice"""
        try:
            if self.ml_service and hasattr(self.ml_service, 'analyze_invoice'):
                # Get historical data for comparison
                historical_invoices = db.query(Invoice).filter(
                    Invoice.company_id == company_id,
                    Invoice.id != invoice.id
                ).limit(100).all()
                
                # Get company settings
                from src.models.company import Company
                company = db.query(Company).filter(Company.id == company_id).first()
                
                # Run ML analysis
                ai_analysis = await self.ml_service.analyze_invoice(
                    invoice, company, historical_invoices
                )
                
                return ai_analysis
            else:
                # Return basic analysis if ML service not available
                return {
                    "invoice_id": str(invoice.id),
                    "analysis_timestamp": datetime.now(UTC).isoformat(),
                    "overall_risk_score": 0.3,
                    "recommendations": ["Basic analysis - ML service not available"]
                }
                
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return {
                "invoice_id": str(invoice.id),
                "analysis_timestamp": datetime.now(UTC).isoformat(),
                "error": str(e),
                "overall_risk_score": 0.5
            }
    
    async def _create_approval_workflow(self, invoice: Invoice, company_id: str, ai_analysis: Dict[str, Any]) -> Any:
        """Create approval workflow for invoice"""
        try:
            # Get company settings for workflow configuration
            company_settings = {
                "manager_approval_threshold": 1000,
                "director_approval_threshold": 5000,
                "cfo_approval_threshold": 25000
            }
            
            # Create workflow
            workflow = workflow_engine.create_workflow(
                invoice_id=str(invoice.id),
                company_id=company_id,
                invoice_amount=float(invoice.total_amount),
                company_settings=company_settings
            )
            
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create approval workflow: {str(e)}")
            raise
    
    def _determine_next_action(self, invoice: Invoice, ai_analysis: Dict[str, Any]) -> str:
        """Determine next action based on AI analysis"""
        try:
            # Check for high risk indicators
            risk_score = ai_analysis.get("overall_risk_score", 0.5)
            
            if risk_score > 0.8:
                return "manual_review_required"
            elif risk_score > 0.6:
                return "additional_verification"
            elif float(invoice.total_amount) <= self.business_rules["auto_approval_limit"]:
                return "auto_approve"
            else:
                return "approval_required"
                
        except Exception as e:
            logger.error(f"Failed to determine next action: {str(e)}")
            return "approval_required"
    
    def _validate_invoice_data(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted invoice data"""
        errors = []
        
        # Required fields validation
        required_fields = ["supplier_name", "invoice_number", "total_amount", "invoice_date"]
        for field in required_fields:
            if not ocr_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Amount validation
        if ocr_data.get("total_amount"):
            try:
                amount = float(ocr_data["total_amount"])
                if amount <= 0:
                    errors.append("Total amount must be greater than 0")
                if amount > 1000000:  # $1M limit
                    errors.append("Total amount exceeds maximum limit")
            except (ValueError, TypeError):
                errors.append("Invalid total amount format")
        
        # Date validation
        if ocr_data.get("invoice_date"):
            try:
                invoice_date = datetime.strptime(ocr_data["invoice_date"], "%Y-%m-%d")
                if invoice_date > datetime.now():
                    errors.append("Invoice date cannot be in the future")
                if invoice_date < datetime.now() - timedelta(days=365):
                    errors.append("Invoice date is too old (more than 1 year)")
            except ValueError:
                errors.append("Invalid invoice date format")
        
        # Line items validation
        if ocr_data.get("line_items"):
            for i, item in enumerate(ocr_data["line_items"]):
                if not item.get("description"):
                    errors.append(f"Line item {i+1} missing description")
                if not item.get("total") or float(item.get("total", 0)) <= 0:
                    errors.append(f"Line item {i+1} has invalid total amount")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def _create_invoice_from_ocr(self, ocr_data: Dict[str, Any], company_id: str, user_id: str, file_path: str) -> Invoice:
        """Create invoice record from OCR data"""
        invoice = Invoice(
            invoice_number=ocr_data["invoice_number"],
            supplier_name=ocr_data["supplier_name"],
            supplier_email=ocr_data.get("supplier_email"),
            supplier_phone=ocr_data.get("supplier_phone"),
            supplier_address=ocr_data.get("supplier_address"),
            supplier_tax_id=ocr_data.get("supplier_tax_id"),
            invoice_date=datetime.strptime(ocr_data["invoice_date"], "%Y-%m-%d").date(),
            due_date=datetime.strptime(ocr_data.get("due_date", ocr_data["invoice_date"]), "%Y-%m-%d").date() if ocr_data.get("due_date") else None,
            total_amount=Decimal(str(ocr_data["total_amount"])),
            currency=ocr_data.get("currency", "USD"),
            tax_amount=Decimal(str(ocr_data.get("tax_amount", 0))),
            tax_rate=Decimal(str(ocr_data.get("tax_rate", 0))),
            subtotal=Decimal(str(ocr_data.get("subtotal", ocr_data["total_amount"]))),
            total_with_tax=Decimal(str(ocr_data.get("total_with_tax", ocr_data["total_amount"]))),
            po_number=ocr_data.get("po_number"),
            receipt_number=ocr_data.get("receipt_number"),
            department=ocr_data.get("department"),
            cost_center=ocr_data.get("cost_center"),
            project_code=ocr_data.get("project_code"),
            notes=ocr_data.get("notes"),
            original_file_path=file_path,
            file_size_bytes=ocr_data.get("processing_metadata", {}).get("file_size_bytes"),
            company_id=company_id,
            created_by_id=user_id
        )
        
        return invoice
    
    async def _check_for_duplicates(self, invoice: Invoice, company_id: str, db: Session) -> Dict[str, Any]:
        """Check for duplicate invoices"""
        # Check for exact invoice number match
        existing_invoice = db.query(Invoice).filter(
            and_(
                Invoice.invoice_number == invoice.invoice_number,
                Invoice.supplier_name == invoice.supplier_name,
                Invoice.company_id == company_id,
                Invoice.id != invoice.id
            )
        ).first()
        
        if existing_invoice:
            return {
                "is_duplicate": True,
                "duplicate_id": str(existing_invoice.id),
                "confidence": 1.0,
                "reason": "Exact invoice number and supplier match"
            }
        
        # Check for similar invoices (amount, supplier, date)
        similar_invoices = db.query(Invoice).filter(
            and_(
                Invoice.supplier_name == invoice.supplier_name,
                Invoice.company_id == company_id,
                Invoice.id != invoice.id,
                Invoice.total_amount == invoice.total_amount,
                Invoice.invoice_date == invoice.invoice_date
            )
        ).all()
        
        if similar_invoices:
            return {
                "is_duplicate": True,
                "duplicate_id": str(similar_invoices[0].id),
                "confidence": 0.9,
                "reason": "Similar invoice with same amount, supplier, and date"
            }
        
        return {
            "is_duplicate": False,
            "confidence": 0.0
        }
    
    async def _detect_fraud(self, invoice: Invoice, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential fraud in invoice"""
        fraud_indicators = []
        fraud_score = 0.0
        
        # Check for unusual amounts
        if invoice.total_amount > 50000:  # High-value invoice
            fraud_indicators.append("High-value invoice")
            fraud_score += 0.2
        
        # Check for round numbers (suspicious)
        if invoice.total_amount % 1000 == 0:
            fraud_indicators.append("Round number amount")
            fraud_score += 0.1
        
        # Check for unusual supplier patterns
        if invoice.supplier_name.lower() in ["test", "demo", "sample"]:
            fraud_indicators.append("Test supplier name")
            fraud_score += 0.3
        
        # Check for unusual dates
        if invoice.invoice_date.weekday() in [5, 6]:  # Weekend
            fraud_indicators.append("Weekend invoice date")
            fraud_score += 0.1
        
        # Check for missing tax information
        if invoice.tax_amount == 0 and invoice.total_amount > 1000:
            fraud_indicators.append("Missing tax on high-value invoice")
            fraud_score += 0.2
        
        # Calculate confidence based on OCR quality
        confidence_scores = ocr_data.get("confidence_scores", {})
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.8
        
        return {
            "fraud_score": min(fraud_score, 1.0),
            "confidence_score": avg_confidence,
            "fraud_indicators": fraud_indicators,
            "risk_level": "high" if fraud_score > 0.6 else "medium" if fraud_score > 0.3 else "low"
        }
    
    async def _ai_gl_coding(self, invoice: Invoice, company_id: str) -> Dict[str, Any]:
        """AI-powered GL coding for invoice line items"""
        # This would integrate with an AI service for GL coding
        # For now, return mock GL coding based on line item descriptions
        
        gl_coding = {
            "line_items": [],
            "confidence": 0.85,
            "ai_model": "mock-gl-coder-v1",
            "processing_time_ms": 150
        }
        
        # Mock GL coding logic
        # Note: This assumes line_items relationship exists
        # In production, you would query the actual line items
        line_items = invoice.line_items if hasattr(invoice, 'line_items') else []
        for line in line_items:
            description = line.description.lower()
            
            if any(word in description for word in ["software", "license", "subscription"]):
                gl_account = "6000"  # Software expenses
            elif any(word in description for word in ["service", "consulting", "implementation"]):
                gl_account = "6500"  # Professional services
            elif any(word in description for word in ["hardware", "equipment", "computer"]):
                gl_account = "6100"  # Hardware expenses
            elif any(word in description for word in ["travel", "flight", "hotel"]):
                gl_account = "6600"  # Travel expenses
            else:
                gl_account = "6900"  # Other expenses
            
            gl_coding["line_items"].append({
                "line_id": str(line.id),
                "description": line.description,
                "suggested_gl_account": gl_account,
                "confidence": 0.8,
                "reasoning": f"Based on description keywords: {description}"
            })
        
        return gl_coding
    
    def _should_auto_approve(self, invoice: Invoice) -> bool:
        """Determine if invoice should be auto-approved"""
        # Check amount threshold
        if invoice.total_amount <= self.business_rules["auto_approval_limit"]:
            return True
        
        # Check if it's a recurring invoice from known supplier
        if invoice.type == InvoiceType.RECURRING:
            return True
        
        # Check if it's a PO-backed invoice
        if invoice.po_number:
            return True
        
        return False
    
    async def _should_post_to_erp(self, company_id: str) -> bool:
        """Check if company has ERP integration configured"""
        adapter = self.erp_service.get_adapter("mock")
        return adapter is not None
    
    async def _post_to_erp(self, invoice: Invoice, company_id: str, db: Session) -> Dict[str, Any]:
        """Post approved invoice to ERP system"""
        try:
            # Get company settings
            company_settings = self._get_company_settings(company_id, db)
            
            # Post to ERP
            result = await self.erp_service.post_invoice("mock", invoice, company_settings)
            
            if result["status"] == "success":
                # Create audit log
                self._create_audit_log(
                    db, invoice.approved_by_id, company_id,
                    AuditAction.UPDATE, AuditResourceType.INVOICE,
                    str(invoice.id), f"Invoice posted to ERP: {result['erp_doc_id']}"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"ERP posting failed: {str(e)}")
            return {
                "status": "error",
                "message": f"ERP posting failed: {str(e)}"
            }
    
    async def _perform_ai_analysis(self, invoice: Invoice, ocr_result: Dict[str, Any], company_id: str) -> Dict[str, Any]:
        """Perform comprehensive AI analysis on invoice"""
        try:
            # Heuristic fraud check and confidence estimation without external ML dependency
            basic_fraud = await self._detect_fraud(invoice, ocr_result)

            # Heuristic GL coding suggestions (placeholder until ML is wired)
            gl_coding_result = await self._ai_gl_coding(invoice, company_id)

            # Derive overall confidence from OCR confidence and GL coding confidence
            confidence_scores = ocr_result.get("confidence_scores", {})
            ocr_overall_confidence = (
                sum(confidence_scores.values()) / len(confidence_scores)
                if confidence_scores else 0.8
            )
            gl_confidence = gl_coding_result.get("confidence", 0.0)
            overall_confidence = (ocr_overall_confidence + gl_confidence) / 2.0

            fraud_result = {
                "fraud_probability": basic_fraud.get("fraud_score", 0.0),
                "risk_level": basic_fraud.get("risk_level", "low").upper(),
                "recommendations": basic_fraud.get("fraud_indicators", []),
                "confidence": basic_fraud.get("confidence_score", 0.8)
            }

            anomaly_result = {
                "is_anomalous": basic_fraud.get("risk_level", "low") == "high",
                "anomaly_score": basic_fraud.get("fraud_score", 0.0),
                "anomaly_types": basic_fraud.get("fraud_indicators", []),
                "recommendations": []
            }

            return {
                "fraud_score": fraud_result.get("fraud_probability", 0.0),
                "fraud_risk_level": fraud_result.get("risk_level", "LOW"),
                "fraud_recommendations": fraud_result.get("recommendations", []),
                "gl_coding": gl_coding_result.get("line_items", []),
                "gl_confidence": gl_confidence,
                "supplier_anomaly": anomaly_result.get("is_anomalous", False),
                "anomaly_score": anomaly_result.get("anomaly_score", 0.0),
                "anomaly_types": anomaly_result.get("anomaly_types", []),
                "anomaly_recommendations": anomaly_result.get("recommendations", []),
                "overall_confidence": overall_confidence,
                "ai_insights": self._generate_ai_insights(fraud_result, {"overall_confidence": gl_confidence}, anomaly_result),
                "processing_metadata": {
                    "models_used": ["heuristic_fraud", "heuristic_gl_coding"],
                    "analysis_timestamp": datetime.now(UTC).isoformat(),
                    "model_versions": self._get_model_versions()
                }
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                "fraud_score": 0.0,
                "fraud_risk_level": "UNKNOWN",
                "fraud_recommendations": ["AI analysis unavailable"],
                "gl_coding": [],
                "gl_confidence": 0.0,
                "supplier_anomaly": False,
                "anomaly_score": 0.0,
                "anomaly_types": [],
                "anomaly_recommendations": [],
                "overall_confidence": 0.0,
                "ai_insights": ["AI analysis failed - manual review recommended"],
                "processing_metadata": {
                    "error": str(e),
                    "analysis_timestamp": datetime.now(UTC).isoformat()
                }
            }
    
    def _get_supplier_age(self, supplier_name: str, company_id: str) -> int:
        """Get supplier age in days"""
        # In production, this would query the database
        # For now, return a mock value
        return 365
    
    def _calculate_payment_terms(self, invoice_date, due_date) -> int:
        """Calculate payment terms in days"""
        if invoice_date and due_date:
            return (due_date - invoice_date).days
        return 30  # Default
    
    def _get_invoice_frequency(self, supplier_name: str, company_id: str) -> int:
        """Get invoice frequency per month for supplier"""
        # In production, this would query the database
        return 5  # Default
    
    def _is_weekend_submission(self, created_at) -> int:
        """Check if invoice was submitted on weekend"""
        if created_at:
            return 1 if created_at.weekday() >= 5 else 0
        return 0
    
    def _calculate_amount_deviation(self, invoice: Invoice) -> float:
        """Calculate deviation from supplier's average invoice amount"""
        # In production, this would calculate actual deviation
        return 0.0  # Default
    
    def _calculate_pattern_score(self, invoice_number: str) -> float:
        """Calculate pattern score for invoice number"""
        # Simple pattern detection
        if invoice_number and invoice_number.isdigit():
            return 0.8  # Sequential numbers
        return 0.3  # Random/alphanumeric
    
    def _get_location_risk(self, supplier_name: str) -> float:
        """Get location risk score for supplier"""
        # In production, this would use geolocation data
        return 0.3  # Default low risk
    
    def _get_time_since_last_invoice(self, supplier_name: str, company_id: str) -> int:
        """Get hours since last invoice from this supplier"""
        # In production, this would query the database
        return 72  # Default 3 days
    
    def _get_avg_invoice_amount(self, supplier_name: str, company_id: str) -> float:
        """Get average invoice amount for supplier"""
        # In production, this would query the database
        return 1000.0  # Default
    
    def _get_payment_score(self, supplier_name: str, company_id: str) -> float:
        """Get payment behavior score for supplier"""
        # In production, this would calculate from payment history
        return 0.8  # Default good score
    
    def _get_credit_rating(self, supplier_name: str) -> int:
        """Get credit rating for supplier"""
        # In production, this would query credit agencies
        return 700  # Default good rating
    
    def _generate_ai_insights(self, fraud_result: Dict, gl_coding_result: Dict, anomaly_result: Dict) -> List[str]:
        """Generate AI insights from analysis results"""
        insights = []
        
        # Fraud insights
        fraud_prob = fraud_result.get("fraud_probability", 0.0)
        if fraud_prob > 0.7:
            insights.append("🚨 High fraud risk detected - immediate review required")
        elif fraud_prob > 0.4:
            insights.append("⚠️ Medium fraud risk - enhanced verification recommended")
        
        # GL coding insights
        gl_confidence = gl_coding_result.get("overall_confidence", 0.0)
        if gl_confidence > 0.9:
            insights.append("✅ High confidence GL coding predictions available")
        elif gl_confidence < 0.6:
            insights.append("❓ Low confidence GL coding - manual review suggested")
        
        # Anomaly insights
        if anomaly_result.get("is_anomalous", False):
            insights.append("🔍 Supplier behavior anomaly detected")
        
        # Overall insights
        if len(insights) == 0:
            insights.append("✅ No significant issues detected by AI analysis")
        
        return insights
    
    def _get_model_versions(self) -> Dict[str, str]:
        """Get current model versions"""
        return {
            "fraud_detection": "v1.2.0",
            "gl_coding": "v1.1.0",
            "supplier_anomaly": "v1.0.0"
        }
    
    def _get_company_settings(self, company_id: str, db: Session) -> Dict[str, Any]:
        """Get company ERP settings"""
        # This would fetch from company configuration
        # For now, return default settings
        return {
            "erp_type": "dynamics_gp",
            "company_id": company_id,
            "default_currency": "USD",
            "tax_calculation": "automatic",
            "approval_workflow": "standard"
        }
    
    def _create_audit_log(self, db: Session, user_id: str, company_id: str, 
                          action: AuditAction, resource_type: AuditResourceType, 
                          resource_id: str, description: str):
        """Create audit log entry"""
        audit_log = AuditLog(
            user_id=user_id,
            company_id=company_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"description": description},
            ip_address="127.0.0.1",  # Would come from request context
            user_agent="InvoiceProcessor"
        )
        db.add(audit_log)
        # Don't commit here - let the calling method handle the commit
    
    async def batch_process_invoices(self, file_paths: List[str], company_id: str, 
                                   user_id: str, db: Session) -> Dict[str, Any]:
        """Process multiple invoices in batch"""
        results = []
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            try:
                result = await self.process_invoice(file_path, company_id, user_id, db)
                results.append({
                    "file_path": file_path,
                    "result": result
                })
                
                if result["status"] == "success":
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Batch processing failed for {file_path}: {str(e)}")
                results.append({
                    "file_path": file_path,
                    "result": {
                        "status": "error",
                        "message": str(e)
                    }
                })
                failed += 1
        
        return {
            "status": "completed",
            "total": len(file_paths),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    async def reprocess_invoice(self, invoice_id: str, company_id: str, user_id: str, db: Session) -> Dict[str, Any]:
        """Reprocess an existing invoice"""
        try:
            # Get existing invoice
            invoice = db.query(Invoice).filter(
                and_(
                    Invoice.id == invoice_id,
                    Invoice.company_id == company_id
                )
            ).first()
            
            if not invoice:
                return {
                    "status": "error",
                    "message": "Invoice not found"
                }
            
            # Reset status and reprocess
            invoice.status = InvoiceStatus.DRAFT
            invoice.erp_error_message = None
            db.commit()
            
            # Reprocess
            result = await self.process_invoice(
                invoice.original_file_path, company_id, user_id, db
            )
            
            # Add reprocess message if successful
            if result.get("status") == "success":
                result["message"] = "Invoice successfully reprocessed"
            
            return result
            
        except Exception as e:
            logger.error(f"Invoice reprocessing failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Invoice reprocessing failed: {str(e)}"
            }












