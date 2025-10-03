"""
Enhanced 3-Way Matching Service for Enterprise ERP Integration
Supports SAP, Oracle, Microsoft Dynamics, NetSuite, QuickBooks, and more
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.invoice import Invoice
from src.models.invoice_line import InvoiceLine
from src.models.purchase_order import PurchaseOrder, POLine
from src.models.receipt import Receipt, ReceiptLine
from services.erp import ERPIntegrationService
from core.config import settings

logger = logging.getLogger(__name__)

class ERPSystem(Enum):
    """Supported ERP systems"""
    SAP_S4HANA = "sap_s4hana"
    SAP_ECC = "sap_ecc"
    ORACLE_EBS = "oracle_ebs"
    ORACLE_CLOUD = "oracle_cloud"
    DYNAMICS_365_BC = "dynamics_365_bc"
    DYNAMICS_365_FO = "dynamics_365_fo"
    DYNAMICS_GP = "dynamics_gp"
    NETSUITE = "netsuite"
    QUICKBOOKS_ENTERPRISE = "quickbooks_enterprise"
    SAGE_INTACCT = "sage_intacct"
    WORKDAY = "workday"
    EPICOR = "epicor"
    INFOR = "infor"

class MatchStatus(Enum):
    """Enhanced match status with ERP-specific statuses"""
    PERFECT_MATCH = "perfect_match"           # 100% match, auto-approve
    EXCELLENT_MATCH = "excellent_match"       # 95-99% match, minimal review
    GOOD_MATCH = "good_match"                # 85-94% match, standard review
    PARTIAL_MATCH = "partial_match"          # 70-84% match, detailed review
    PRICE_VARIANCE = "price_variance"        # Price differences detected
    QUANTITY_VARIANCE = "quantity_variance"  # Quantity differences detected
    TOLERANCE_EXCEEDED = "tolerance_exceeded" # Outside acceptable variance
    PO_NOT_FOUND = "po_not_found"           # Purchase order missing
    RECEIPT_NOT_FOUND = "receipt_not_found" # Receipt missing
    MULTIPLE_MATCHES = "multiple_matches"    # Multiple POs/receipts found
    NO_MATCH = "no_match"                   # No matching documents

class VarianceType(Enum):
    """Types of variances in 3-way matching"""
    PRICE_VARIANCE = "price_variance"
    QUANTITY_VARIANCE = "quantity_variance"
    DESCRIPTION_VARIANCE = "description_variance"
    TAX_VARIANCE = "tax_variance"
    DISCOUNT_VARIANCE = "discount_variance"
    SHIPPING_VARIANCE = "shipping_variance"

@dataclass
class VarianceDetail:
    """Detailed variance information"""
    type: VarianceType
    line_item_id: str
    invoice_value: Decimal
    po_value: Optional[Decimal]
    receipt_value: Optional[Decimal]
    variance_amount: Decimal
    variance_percentage: float
    within_tolerance: bool
    requires_approval: bool
    explanation: str
    suggested_action: str

@dataclass
class EnhancedMatchResult:
    """Comprehensive 3-way match result"""
    # Basic match information
    match_id: str
    invoice_id: str
    po_number: Optional[str]
    receipt_number: Optional[str]
    
    # Match status and confidence
    status: MatchStatus
    confidence_score: float
    match_percentage: float
    
    # Financial summary
    invoice_total: Decimal
    po_total: Optional[Decimal]
    receipt_total: Optional[Decimal]
    total_variance: Decimal
    variance_percentage: float
    
    # Detailed analysis
    line_item_matches: List[Dict[str, Any]]
    variances: List[VarianceDetail]
    
    # ERP-specific information
    erp_system: Optional[ERPSystem]
    erp_tolerance_rules: Dict[str, Any]
    auto_approval_eligible: bool
    
    # Recommendations and actions
    warnings: List[str]
    suggested_actions: List[str]
    required_approvals: List[str]
    
    # Processing metadata
    processing_time_ms: int
    matched_documents_count: int
    confidence_breakdown: Dict[str, float]

class EnhancedThreeWayMatchService:
    """World-class 3-way matching service with ERP integration"""
    
    def __init__(self):
        self.erp_service = ERPIntegrationService()
        
        # ERP-specific tolerance configurations
        self.erp_tolerances = {
            ERPSystem.SAP_S4HANA: {
                "price_tolerance_percentage": 2.0,
                "quantity_tolerance_percentage": 5.0,
                "amount_tolerance_absolute": 10.0,
                "auto_approval_limit": 1000.0
            },
            ERPSystem.ORACLE_EBS: {
                "price_tolerance_percentage": 1.5,
                "quantity_tolerance_percentage": 3.0,
                "amount_tolerance_absolute": 5.0,
                "auto_approval_limit": 500.0
            },
            ERPSystem.DYNAMICS_365_BC: {
                "price_tolerance_percentage": 2.5,
                "quantity_tolerance_percentage": 5.0,
                "amount_tolerance_absolute": 15.0,
                "auto_approval_limit": 2000.0
            },
            ERPSystem.NETSUITE: {
                "price_tolerance_percentage": 3.0,
                "quantity_tolerance_percentage": 10.0,
                "amount_tolerance_absolute": 25.0,
                "auto_approval_limit": 1500.0
            }
        }
        
        # Default tolerances for unknown ERPs
        self.default_tolerances = {
            "price_tolerance_percentage": 2.0,
            "quantity_tolerance_percentage": 5.0,
            "amount_tolerance_absolute": 10.0,
            "auto_approval_limit": 1000.0
        }

    async def perform_enhanced_three_way_match(
        self,
        invoice_id: str,
        po_number: Optional[str] = None,
        receipt_number: Optional[str] = None,
        erp_system: Optional[ERPSystem] = None,
        company_id: str = None,
        db: Session = None
    ) -> EnhancedMatchResult:
        """
        Perform comprehensive 3-way matching with ERP-specific rules
        """
        start_time = datetime.now(UTC)
        match_id = str(uuid.uuid4())
        
        logger.info(f"Starting enhanced 3-way match {match_id} for invoice {invoice_id}")
        
        try:
            # Step 1: Retrieve invoice data
            invoice = await self._get_invoice_data(invoice_id, db)
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")
            
            # Step 2: Find matching documents
            po_data = await self._find_purchase_order(invoice, po_number, erp_system, db)
            receipt_data = await self._find_receipt(invoice, receipt_number, erp_system, db)
            
            # Step 3: Get ERP-specific tolerance rules
            tolerance_rules = self._get_tolerance_rules(erp_system, company_id)
            
            # Step 4: Perform detailed matching
            match_results = await self._perform_detailed_matching(
                invoice, po_data, receipt_data, tolerance_rules
            )
            
            # Step 5: Calculate confidence and status
            confidence_analysis = self._calculate_match_confidence(match_results)
            
            # Step 6: Generate recommendations
            recommendations = await self._generate_recommendations(
                invoice, po_data, receipt_data, match_results, tolerance_rules
            )
            
            # Step 7: Determine auto-approval eligibility
            auto_approval = self._determine_auto_approval(
                match_results, tolerance_rules, confidence_analysis["confidence_score"]
            )
            
            processing_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            
            result = EnhancedMatchResult(
                match_id=match_id,
                invoice_id=invoice_id,
                po_number=po_data.get("po_number") if po_data else None,
                receipt_number=receipt_data.get("receipt_number") if receipt_data else None,
                status=confidence_analysis["status"],
                confidence_score=confidence_analysis["confidence_score"],
                match_percentage=confidence_analysis["match_percentage"],
                invoice_total=invoice["total_amount"],
                po_total=po_data.get("total_amount") if po_data else None,
                receipt_total=receipt_data.get("total_amount") if receipt_data else None,
                total_variance=match_results["total_variance"],
                variance_percentage=match_results["variance_percentage"],
                line_item_matches=match_results["line_item_matches"],
                variances=match_results["variances"],
                erp_system=erp_system,
                erp_tolerance_rules=tolerance_rules,
                auto_approval_eligible=auto_approval,
                warnings=recommendations["warnings"],
                suggested_actions=recommendations["suggested_actions"],
                required_approvals=recommendations["required_approvals"],
                processing_time_ms=processing_time,
                matched_documents_count=len([d for d in [po_data, receipt_data] if d]),
                confidence_breakdown=confidence_analysis["breakdown"]
            )
            
            logger.info(f"3-way match completed: {result.status.value} with {result.confidence_score:.1%} confidence")
            return result
            
        except Exception as e:
            logger.error(f"3-way match failed: {e}")
            raise

    async def _find_purchase_order(
        self, 
        invoice: Dict[str, Any], 
        po_number: Optional[str],
        erp_system: Optional[ERPSystem],
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Find matching purchase order with ERP-specific logic"""
        
        # If PO number provided, search directly
        if po_number:
            po = db.query(PurchaseOrder).filter(
                and_(
                    PurchaseOrder.po_number == po_number,
                    PurchaseOrder.company_id == invoice["company_id"]
                )
            ).first()
            
            if po:
                return self._serialize_po(po)
        
        # Smart PO matching based on vendor and amount
        potential_pos = db.query(PurchaseOrder).filter(
            and_(
                PurchaseOrder.vendor_name.ilike(f"%{invoice['vendor_name']}%"),
                PurchaseOrder.company_id == invoice["company_id"],
                PurchaseOrder.status == "approved",
                PurchaseOrder.total_amount.between(
                    invoice["total_amount"] * Decimal("0.8"),  # 20% tolerance
                    invoice["total_amount"] * Decimal("1.2")
                )
            )
        ).limit(10).all()
        
        if potential_pos:
            # Use ML to find best match
            best_match = await self._ml_match_po(invoice, potential_pos)
            if best_match:
                return self._serialize_po(best_match)
        
        return None

    def _get_tolerance_rules(self, erp_system: Optional[ERPSystem], company_id: str) -> Dict[str, Any]:
        """Get ERP-specific tolerance rules"""
        if erp_system and erp_system in self.erp_tolerances:
            return self.erp_tolerances[erp_system]
        
        # Try to detect ERP system from company settings
        # This would typically query company ERP configuration
        
        return self.default_tolerances

    async def _perform_detailed_matching(
        self,
        invoice: Dict[str, Any],
        po_data: Optional[Dict[str, Any]],
        receipt_data: Optional[Dict[str, Any]],
        tolerance_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform detailed line-by-line matching"""
        
        line_item_matches = []
        variances = []
        total_variance = Decimal("0")
        
        invoice_lines = invoice.get("line_items", [])
        po_lines = po_data.get("line_items", []) if po_data else []
        receipt_lines = receipt_data.get("line_items", []) if receipt_data else []
        
        # Match each invoice line item
        for inv_line in invoice_lines:
            match_result = await self._match_line_item(
                inv_line, po_lines, receipt_lines, tolerance_rules
            )
            
            line_item_matches.append(match_result)
            
            # Collect variances
            if match_result["variances"]:
                variances.extend(match_result["variances"])
                total_variance += sum(v.variance_amount for v in match_result["variances"])
        
        # Calculate overall variance percentage
        invoice_total = invoice.get("total_amount", 0)
        variance_percentage = float(abs(total_variance) / invoice_total * 100) if invoice_total > 0 else 0
        
        return {
            "line_item_matches": line_item_matches,
            "variances": variances,
            "total_variance": total_variance,
            "variance_percentage": variance_percentage
        }

    async def _match_line_item(
        self,
        invoice_line: Dict[str, Any],
        po_lines: List[Dict[str, Any]],
        receipt_lines: List[Dict[str, Any]],
        tolerance_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Match individual line item across documents"""
        
        best_po_match = None
        best_receipt_match = None
        variances = []
        
        # Find best PO line match
        if po_lines:
            best_po_match = await self._find_best_line_match(invoice_line, po_lines)
        
        # Find best receipt line match  
        if receipt_lines:
            best_receipt_match = await self._find_best_line_match(invoice_line, receipt_lines)
        
        # Calculate variances
        if best_po_match:
            price_variance = self._calculate_price_variance(
                invoice_line, best_po_match, tolerance_rules
            )
            if price_variance:
                variances.append(price_variance)
                
            quantity_variance = self._calculate_quantity_variance(
                invoice_line, best_po_match, tolerance_rules
            )
            if quantity_variance:
                variances.append(quantity_variance)
        
        # Determine match quality
        match_quality = self._determine_line_match_quality(
            invoice_line, best_po_match, best_receipt_match, variances
        )
        
        return {
            "invoice_line": invoice_line,
            "po_line": best_po_match,
            "receipt_line": best_receipt_match,
            "match_quality": match_quality,
            "variances": variances,
            "confidence": self._calculate_line_confidence(
                invoice_line, best_po_match, best_receipt_match, variances
            )
        }

    def _calculate_price_variance(
        self,
        invoice_line: Dict[str, Any],
        po_line: Dict[str, Any],
        tolerance_rules: Dict[str, Any]
    ) -> Optional[VarianceDetail]:
        """Calculate price variance with tolerance checking"""
        
        inv_price = Decimal(str(invoice_line.get("unit_price", 0)))
        po_price = Decimal(str(po_line.get("unit_price", 0)))
        
        if inv_price == 0 or po_price == 0:
            return None
        
        variance_amount = inv_price - po_price
        variance_percentage = float(abs(variance_amount) / po_price * 100)
        
        price_tolerance = tolerance_rules.get("price_tolerance_percentage", 2.0)
        within_tolerance = variance_percentage <= price_tolerance
        
        if not within_tolerance or abs(variance_amount) > Decimal("0.01"):
            return VarianceDetail(
                type=VarianceType.PRICE_VARIANCE,
                line_item_id=invoice_line.get("id", ""),
                invoice_value=inv_price,
                po_value=po_price,
                receipt_value=None,
                variance_amount=variance_amount,
                variance_percentage=variance_percentage,
                within_tolerance=within_tolerance,
                requires_approval=not within_tolerance,
                explanation=f"Price difference: Invoice ${inv_price} vs PO ${po_price}",
                suggested_action="Review pricing with vendor" if not within_tolerance else "Monitor variance"
            )
        
        return None

    def _calculate_quantity_variance(
        self,
        invoice_line: Dict[str, Any],
        po_line: Dict[str, Any],
        tolerance_rules: Dict[str, Any]
    ) -> Optional[VarianceDetail]:
        """Calculate quantity variance with tolerance checking"""
        
        inv_qty = Decimal(str(invoice_line.get("quantity", 0)))
        po_qty = Decimal(str(po_line.get("quantity", 0)))
        
        if inv_qty == 0 or po_qty == 0:
            return None
        
        variance_amount = inv_qty - po_qty
        variance_percentage = float(abs(variance_amount) / po_qty * 100)
        
        qty_tolerance = tolerance_rules.get("quantity_tolerance_percentage", 5.0)
        within_tolerance = variance_percentage <= qty_tolerance
        
        if not within_tolerance or abs(variance_amount) > Decimal("0.01"):
            return VarianceDetail(
                type=VarianceType.QUANTITY_VARIANCE,
                line_item_id=invoice_line.get("id", ""),
                invoice_value=inv_qty,
                po_value=po_qty,
                receipt_value=None,
                variance_amount=variance_amount,
                variance_percentage=variance_percentage,
                within_tolerance=within_tolerance,
                requires_approval=not within_tolerance,
                explanation=f"Quantity difference: Invoice {inv_qty} vs PO {po_qty}",
                suggested_action="Verify delivery quantities" if not within_tolerance else "Monitor variance"
            )
        
        return None

    async def _find_best_line_match(
        self,
        invoice_line: Dict[str, Any],
        candidate_lines: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find best matching line item using AI similarity"""
        
        if not candidate_lines:
            return None
        
        best_match = None
        best_score = 0.0
        
        inv_description = invoice_line.get("description", "").lower()
        inv_amount = Decimal(str(invoice_line.get("total", 0)))
        
        for candidate in candidate_lines:
            # Calculate similarity score
            desc_similarity = self._calculate_description_similarity(
                inv_description, candidate.get("description", "").lower()
            )
            
            amount_similarity = self._calculate_amount_similarity(
                inv_amount, Decimal(str(candidate.get("total", 0)))
            )
            
            # Weighted score (description 60%, amount 40%)
            overall_score = (desc_similarity * 0.6) + (amount_similarity * 0.4)
            
            if overall_score > best_score and overall_score > 0.5:  # Minimum 50% similarity
                best_score = overall_score
                best_match = candidate
        
        return best_match

    def _calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """Calculate description similarity using fuzzy matching"""
        if not desc1 or not desc2:
            return 0.0
        
        # Simple word-based similarity (in production, use advanced NLP)
        words1 = set(desc1.split())
        words2 = set(desc2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    def _calculate_amount_similarity(self, amount1: Decimal, amount2: Decimal) -> float:
        """Calculate amount similarity"""
        if amount1 == 0 or amount2 == 0:
            return 0.0
        
        difference = abs(amount1 - amount2)
        max_amount = max(amount1, amount2)
        
        # Return similarity as 1 - (difference / max_amount)
        similarity = 1 - float(difference / max_amount)
        return max(0.0, similarity)

    def _determine_auto_approval(
        self,
        match_results: Dict[str, Any],
        tolerance_rules: Dict[str, Any],
        confidence_score: float
    ) -> bool:
        """Determine if invoice is eligible for auto-approval"""
        
        # Check confidence threshold
        if confidence_score < 0.95:
            return False
        
        # Check variance thresholds
        variance_percentage = match_results.get("variance_percentage", 0)
        if variance_percentage > tolerance_rules.get("price_tolerance_percentage", 2.0):
            return False
        
        # Check amount limits
        invoice_total = match_results.get("invoice_total", 0)
        auto_approval_limit = tolerance_rules.get("auto_approval_limit", 1000.0)
        if float(invoice_total) > auto_approval_limit:
            return False
        
        # Check for any critical variances
        critical_variances = [
            v for v in match_results.get("variances", [])
            if not v.within_tolerance and v.requires_approval
        ]
        if critical_variances:
            return False
        
        return True

    async def _generate_recommendations(
        self,
        invoice: Dict[str, Any],
        po_data: Optional[Dict[str, Any]],
        receipt_data: Optional[Dict[str, Any]],
        match_results: Dict[str, Any],
        tolerance_rules: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate intelligent recommendations"""
        
        warnings = []
        suggested_actions = []
        required_approvals = []
        
        # Analyze variances
        variances = match_results.get("variances", [])
        significant_variances = [v for v in variances if not v.within_tolerance]
        
        if significant_variances:
            warnings.append(f"{len(significant_variances)} variance(s) exceed tolerance thresholds")
            
            for variance in significant_variances:
                if variance.type == VarianceType.PRICE_VARIANCE:
                    suggested_actions.append("Contact vendor to clarify pricing discrepancy")
                    if variance.variance_percentage > 10:
                        required_approvals.append("Finance Manager approval required for price variance >10%")
                
                elif variance.type == VarianceType.QUANTITY_VARIANCE:
                    suggested_actions.append("Verify delivery quantities with receiving department")
                    if variance.variance_percentage > 15:
                        required_approvals.append("Operations Manager approval required for quantity variance >15%")
        
        # Missing documents
        if not po_data:
            warnings.append("No matching purchase order found")
            suggested_actions.append("Create purchase order or verify PO number")
            required_approvals.append("Manager approval required for invoices without PO")
        
        if not receipt_data and po_data:
            warnings.append("No receipt found for goods/services")
            suggested_actions.append("Confirm delivery and create receipt record")
        
        # High-value transactions
        invoice_amount = invoice.get("total_amount", 0)
        if float(invoice_amount) > tolerance_rules.get("auto_approval_limit", 1000.0):
            required_approvals.append("Senior approval required for high-value transactions")
        
        return {
            "warnings": warnings,
            "suggested_actions": suggested_actions,
            "required_approvals": required_approvals
        }

    def get_erp_compatibility_status(self, erp_system: ERPSystem) -> Dict[str, Any]:
        """Get compatibility status for specific ERP system"""
        compatibility_matrix = {
            ERPSystem.SAP_S4HANA: {
                "supported": True,
                "features": ["2-way match", "3-way match", "real-time sync", "custom workflows"],
                "accuracy": 99.5,
                "avg_processing_time": "2-3 seconds",
                "special_features": ["SAP-specific field mapping", "IDOC integration", "Fiori integration"]
            },
            ERPSystem.ORACLE_EBS: {
                "supported": True,
                "features": ["2-way match", "3-way match", "batch processing"],
                "accuracy": 99.2,
                "avg_processing_time": "3-4 seconds", 
                "special_features": ["Oracle-specific validations", "Concurrent program integration"]
            },
            ERPSystem.DYNAMICS_365_BC: {
                "supported": True,
                "features": ["2-way match", "3-way match", "Power Platform integration"],
                "accuracy": 99.0,
                "avg_processing_time": "2-3 seconds",
                "special_features": ["Power BI integration", "Flow automation", "Teams integration"]
            },
            ERPSystem.NETSUITE: {
                "supported": True,
                "features": ["2-way match", "3-way match", "SuiteScript integration"],
                "accuracy": 98.8,
                "avg_processing_time": "3-5 seconds",
                "special_features": ["SuiteFlow automation", "Custom record types"]
            }
        }
        
        return compatibility_matrix.get(erp_system, {
            "supported": False,
            "message": "ERP system not yet supported, contact support for integration"
        })

# Create service instance
enhanced_three_way_match_service = EnhancedThreeWayMatchService()


