"""
3-Way Match Service - Core Business Logic for PO/Invoice/Receipt Matching
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.invoice import Invoice, InvoiceLine
from src.models.purchase_order import PurchaseOrder, POLine
from src.models.receipt import Receipt, ReceiptLine
from core.config import settings

logger = logging.getLogger(__name__)

class MatchStatus(Enum):
    """3-way match status enumeration"""
    PERFECT_MATCH = "perfect_match"
    PARTIAL_MATCH = "partial_match"
    PRICE_MISMATCH = "price_mismatch"
    QUANTITY_MISMATCH = "quantity_mismatch"
    PO_NOT_FOUND = "po_not_found"
    RECEIPT_NOT_FOUND = "receipt_not_found"
    NO_MATCH = "no_match"

class MatchConfidence(Enum):
    """Match confidence levels"""
    HIGH = "high"      # 90%+ confidence
    MEDIUM = "medium"  # 70-89% confidence
    LOW = "low"        # 50-69% confidence
    VERY_LOW = "very_low"  # <50% confidence

@dataclass
class MatchResult:
    """Result of 3-way matching process"""
    status: MatchStatus
    confidence: MatchConfidence
    confidence_score: float
    matches: List[Dict[str, Any]]
    mismatches: List[Dict[str, Any]]
    warnings: List[str]
    suggested_actions: List[str]
    total_invoice_amount: Decimal
    total_po_amount: Decimal
    total_receipt_amount: Decimal
    variance_amount: Decimal
    variance_percentage: float

@dataclass
class LineItemMatch:
    """Individual line item match result"""
    invoice_line_id: str
    po_line_id: Optional[str]
    receipt_line_id: Optional[str]
    match_status: MatchStatus
    confidence_score: float
    price_variance: Decimal
    quantity_variance: Decimal
    description_match: bool
    unit_price_match: bool
    quantity_match: bool
    total_amount_match: bool

class ThreeWayMatchService:
    """Service for performing 3-way matching between invoices, POs, and receipts"""
    
    def __init__(self):
        # Matching thresholds
        self.price_tolerance = Decimal("0.01")  # 1 cent tolerance
        self.quantity_tolerance = Decimal("0.01")  # 1% quantity tolerance
        self.description_similarity_threshold = 0.85  # 85% similarity for descriptions
        self.confidence_thresholds = {
            MatchConfidence.HIGH: 0.90,
            MatchConfidence.MEDIUM: 0.70,
            MatchConfidence.LOW: 0.50
        }
    
    async def perform_three_way_match(
        self, 
        invoice_id: str, 
        po_number: Optional[str] = None,
        receipt_number: Optional[str] = None,
        db: Session = None
    ) -> MatchResult:
        """
        Perform 3-way matching between invoice, PO, and receipt
        
        Args:
            invoice_id: ID of the invoice to match
            po_number: Optional PO number to match against
            receipt_number: Optional receipt number to match against
            db: Database session
            
        Returns:
            MatchResult object with detailed matching information
        """
        try:
            logger.info(f"Starting 3-way match for invoice {invoice_id}")
            
            # Get invoice
            invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")
            
            # Get PO (by number or auto-detect)
            po = await self._get_purchase_order(invoice, po_number, db)
            
            # Get Receipt (by number or auto-detect)
            receipt = await self._get_receipt(invoice, receipt_number, db)
            
            # Perform matching
            if not po and not receipt:
                return self._create_no_match_result(invoice, "No PO or receipt found")
            
            if not po:
                return self._create_no_match_result(invoice, "No matching PO found")
            
            if not receipt:
                return self._create_no_match_result(invoice, "No matching receipt found")
            
            # Perform detailed matching
            return await self._perform_detailed_matching(invoice, po, receipt, db)
            
        except Exception as e:
            logger.error(f"Error in 3-way match: {str(e)}")
            raise
    
    async def _get_purchase_order(
        self, 
        invoice: Invoice, 
        po_number: Optional[str], 
        db: Session
    ) -> Optional[PurchaseOrder]:
        """Get purchase order for matching"""
        if po_number:
            return db.query(PurchaseOrder).filter(
                PurchaseOrder.po_number == po_number,
                PurchaseOrder.company_id == invoice.company_id
            ).first()
        
        # Auto-detect PO by supplier and amount
        return db.query(PurchaseOrder).filter(
            and_(
                PurchaseOrder.supplier_name == invoice.supplier_name,
                PurchaseOrder.company_id == invoice.company_id,
                PurchaseOrder.status.in_(["open", "partially_received"])
            )
        ).first()
    
    async def _get_receipt(
        self, 
        invoice: Invoice, 
        receipt_number: Optional[str], 
        db: Session
    ) -> Optional[Receipt]:
        """Get receipt for matching"""
        if receipt_number:
            return db.query(Receipt).filter(
                Receipt.receipt_number == receipt_number,
                Receipt.company_id == invoice.company_id
            ).first()
        
        # Auto-detect receipt by supplier and amount
        return db.query(Receipt).filter(
            and_(
                Receipt.supplier_name == invoice.supplier_name,
                Receipt.company_id == invoice.company_id,
                Receipt.status == "received"
            )
        ).first()
    
    async def _perform_detailed_matching(
        self, 
        invoice: Invoice, 
        po: PurchaseOrder, 
        receipt: Receipt, 
        db: Session
    ) -> MatchResult:
        """Perform detailed line-by-line matching"""
        
        # Get line items
        invoice_lines = db.query(InvoiceLine).filter(
            InvoiceLine.invoice_id == invoice.id
        ).all()
        
        po_lines = db.query(POLine).filter(
            POLine.po_id == po.id
        ).all()
        
        receipt_lines = db.query(ReceiptLine).filter(
            ReceiptLine.receipt_id == receipt.id
        ).all()
        
        # Perform line item matching
        line_matches = []
        total_confidence = 0.0
        
        for invoice_line in invoice_lines:
            line_match = await self._match_line_item(
                invoice_line, po_lines, receipt_lines
            )
            line_matches.append(line_match)
            total_confidence += line_match.confidence_score
        
        # Calculate overall confidence
        overall_confidence = total_confidence / len(invoice_lines) if invoice_lines else 0.0
        
        # Determine match status
        match_status = self._determine_match_status(line_matches)
        confidence_level = self._determine_confidence_level(overall_confidence)
        
        # Calculate amounts
        total_invoice_amount = sum(line.total_amount for line in invoice_lines)
        total_po_amount = sum(line.total_amount for line in po_lines)
        total_receipt_amount = sum(line.total_amount for line in receipt_lines)
        
        variance_amount = total_invoice_amount - total_po_amount
        variance_percentage = (variance_amount / total_po_amount * 100) if total_po_amount > 0 else 0
        
        # Generate matches and mismatches
        matches, mismatches = self._categorize_matches(line_matches)
        
        # Generate warnings and suggestions
        warnings = self._generate_warnings(line_matches, variance_amount, variance_percentage)
        suggestions = self._generate_suggestions(match_status, line_matches, warnings)
        
        return MatchResult(
            status=match_status,
            confidence=confidence_level,
            confidence_score=overall_confidence,
            matches=matches,
            mismatches=mismatches,
            warnings=warnings,
            suggested_actions=suggestions,
            total_invoice_amount=total_invoice_amount,
            total_po_amount=total_po_amount,
            total_receipt_amount=total_receipt_amount,
            variance_amount=variance_amount,
            variance_percentage=variance_percentage
        )
    
    async def _match_line_item(
        self, 
        invoice_line: InvoiceLine, 
        po_lines: List[POLine], 
        receipt_lines: List[ReceiptLine]
    ) -> LineItemMatch:
        """Match a single invoice line item with PO and receipt lines"""
        
        # Find best matching PO line
        best_po_match = None
        best_po_score = 0.0
        
        for po_line in po_lines:
            score = self._calculate_line_similarity(invoice_line, po_line)
            if score > best_po_score:
                best_po_score = score
                best_po_match = po_line
        
        # Find best matching receipt line
        best_receipt_match = None
        best_receipt_score = 0.0
        
        for receipt_line in receipt_lines:
            score = self._calculate_line_similarity(invoice_line, receipt_line)
            if score > best_receipt_score:
                best_receipt_score = score
                best_receipt_match = receipt_line
        
        # Calculate match details
        po_line = best_po_match
        receipt_line = best_receipt_match
        
        # Calculate variances
        price_variance = Decimal("0")
        quantity_variance = Decimal("0")
        
        if po_line:
            price_variance = invoice_line.unit_price - po_line.unit_price
            quantity_variance = invoice_line.quantity - po_line.quantity
        
        # Determine match status
        match_status = self._determine_line_match_status(
            invoice_line, po_line, receipt_line, price_variance, quantity_variance
        )
        
        # Calculate confidence score
        confidence_score = (best_po_score + best_receipt_score) / 2
        
        # Check individual match criteria
        description_match = best_po_score > self.description_similarity_threshold
        unit_price_match = abs(price_variance) <= self.price_tolerance
        quantity_match = abs(quantity_variance) <= self.quantity_tolerance
        total_amount_match = abs(invoice_line.total_amount - (po_line.total_amount if po_line else 0)) <= self.price_tolerance
        
        return LineItemMatch(
            invoice_line_id=str(invoice_line.id),
            po_line_id=str(po_line.id) if po_line else None,
            receipt_line_id=str(receipt_line.id) if receipt_line else None,
            match_status=match_status,
            confidence_score=confidence_score,
            price_variance=price_variance,
            quantity_variance=quantity_variance,
            description_match=description_match,
            unit_price_match=unit_price_match,
            quantity_match=quantity_match,
            total_amount_match=total_amount_match
        )
    
    def _calculate_line_similarity(
        self, 
        invoice_line: InvoiceLine, 
        other_line: Any
    ) -> float:
        """Calculate similarity score between two line items"""
        score = 0.0
        
        # Description similarity (40% weight)
        if hasattr(other_line, 'description') and other_line.description:
            desc_similarity = self._calculate_text_similarity(
                invoice_line.description, other_line.description
            )
            score += desc_similarity * 0.4
        
        # Unit price similarity (30% weight)
        if hasattr(other_line, 'unit_price') and other_line.unit_price:
            price_diff = abs(invoice_line.unit_price - other_line.unit_price)
            price_similarity = max(0, 1 - (price_diff / invoice_line.unit_price))
            score += price_similarity * 0.3
        
        # Quantity similarity (20% weight)
        if hasattr(other_line, 'quantity') and other_line.quantity:
            qty_diff = abs(invoice_line.quantity - other_line.quantity)
            qty_similarity = max(0, 1 - (qty_diff / invoice_line.quantity))
            score += qty_similarity * 0.2
        
        # Item code similarity (10% weight)
        if (hasattr(other_line, 'item_code') and other_line.item_code and 
            hasattr(invoice_line, 'item_code') and invoice_line.item_code):
            if invoice_line.item_code == other_line.item_code:
                score += 0.1
        
        return min(1.0, score)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple word matching"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _determine_line_match_status(
        self, 
        invoice_line: InvoiceLine, 
        po_line: Optional[POLine], 
        receipt_line: Optional[ReceiptLine],
        price_variance: Decimal,
        quantity_variance: Decimal
    ) -> MatchStatus:
        """Determine match status for a line item"""
        
        if not po_line:
            return MatchStatus.PO_NOT_FOUND
        
        if not receipt_line:
            return MatchStatus.RECEIPT_NOT_FOUND
        
        # Check for perfect match
        if (abs(price_variance) <= self.price_tolerance and 
            abs(quantity_variance) <= self.quantity_tolerance):
            return MatchStatus.PERFECT_MATCH
        
        # Check for price mismatch
        if abs(price_variance) > self.price_tolerance:
            return MatchStatus.PRICE_MISMATCH
        
        # Check for quantity mismatch
        if abs(quantity_variance) > self.quantity_tolerance:
            return MatchStatus.QUANTITY_MISMATCH
        
        return MatchStatus.PARTIAL_MATCH
    
    def _determine_match_status(self, line_matches: List[LineItemMatch]) -> MatchStatus:
        """Determine overall match status"""
        if not line_matches:
            return MatchStatus.NO_MATCH
        
        perfect_matches = sum(1 for match in line_matches if match.match_status == MatchStatus.PERFECT_MATCH)
        total_matches = len(line_matches)
        
        if perfect_matches == total_matches:
            return MatchStatus.PERFECT_MATCH
        
        if perfect_matches > total_matches * 0.8:  # 80% perfect matches
            return MatchStatus.PARTIAL_MATCH
        
        # Check for specific mismatch types
        price_mismatches = sum(1 for match in line_matches if match.match_status == MatchStatus.PRICE_MISMATCH)
        qty_mismatches = sum(1 for match in line_matches if match.match_status == MatchStatus.QUANTITY_MISMATCH)
        
        if price_mismatches > 0:
            return MatchStatus.PRICE_MISMATCH
        
        if qty_mismatches > 0:
            return MatchStatus.QUANTITY_MISMATCH
        
        return MatchStatus.PARTIAL_MATCH
    
    def _determine_confidence_level(self, confidence_score: float) -> MatchConfidence:
        """Determine confidence level based on score"""
        if confidence_score >= self.confidence_thresholds[MatchConfidence.HIGH]:
            return MatchConfidence.HIGH
        elif confidence_score >= self.confidence_thresholds[MatchConfidence.MEDIUM]:
            return MatchConfidence.MEDIUM
        elif confidence_score >= self.confidence_thresholds[MatchConfidence.LOW]:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.VERY_LOW
    
    def _categorize_matches(self, line_matches: List[LineItemMatch]) -> Tuple[List[Dict], List[Dict]]:
        """Categorize matches into successful matches and mismatches"""
        matches = []
        mismatches = []
        
        for match in line_matches:
            match_data = {
                "invoice_line_id": match.invoice_line_id,
                "po_line_id": match.po_line_id,
                "receipt_line_id": match.receipt_line_id,
                "status": match.match_status.value,
                "confidence_score": match.confidence_score,
                "price_variance": float(match.price_variance),
                "quantity_variance": float(match.quantity_variance)
            }
            
            if match.match_status == MatchStatus.PERFECT_MATCH:
                matches.append(match_data)
            else:
                mismatches.append(match_data)
        
        return matches, mismatches
    
    def _generate_warnings(
        self, 
        line_matches: List[LineItemMatch], 
        variance_amount: Decimal, 
        variance_percentage: float
    ) -> List[str]:
        """Generate warnings based on match results"""
        warnings = []
        
        # Amount variance warnings
        if abs(variance_percentage) > 5:  # 5% variance threshold
            warnings.append(f"Significant amount variance: {variance_percentage:.2f}%")
        
        # Line item warnings
        for match in line_matches:
            if match.match_status == MatchStatus.PRICE_MISMATCH:
                warnings.append(f"Price mismatch on line {match.invoice_line_id}: ${match.price_variance}")
            
            if match.match_status == MatchStatus.QUANTITY_MISMATCH:
                warnings.append(f"Quantity mismatch on line {match.invoice_line_id}: {match.quantity_variance}")
            
            if not match.description_match:
                warnings.append(f"Description mismatch on line {match.invoice_line_id}")
        
        return warnings
    
    def _generate_suggestions(
        self, 
        match_status: MatchStatus, 
        line_matches: List[LineItemMatch], 
        warnings: List[str]
    ) -> List[str]:
        """Generate suggested actions based on match results"""
        suggestions = []
        
        if match_status == MatchStatus.PERFECT_MATCH:
            suggestions.append("Perfect match - approve invoice")
        
        elif match_status == MatchStatus.PARTIAL_MATCH:
            suggestions.append("Partial match - review mismatched items")
            suggestions.append("Consider manual approval for minor variances")
        
        elif match_status == MatchStatus.PRICE_MISMATCH:
            suggestions.append("Price mismatch detected - investigate with supplier")
            suggestions.append("Verify PO pricing and invoice accuracy")
        
        elif match_status == MatchStatus.QUANTITY_MISMATCH:
            suggestions.append("Quantity mismatch detected - verify receipt quantities")
            suggestions.append("Check for partial deliveries or over-shipments")
        
        else:
            suggestions.append("No match found - manual review required")
            suggestions.append("Verify PO and receipt numbers")
        
        # Add specific suggestions based on warnings
        if any("Price mismatch" in warning for warning in warnings):
            suggestions.append("Contact supplier to resolve pricing discrepancies")
        
        if any("Quantity mismatch" in warning for warning in warnings):
            suggestions.append("Verify physical receipt of goods")
        
        return suggestions
    
    def _create_no_match_result(self, invoice: Invoice, reason: str) -> MatchResult:
        """Create a no-match result"""
        return MatchResult(
            status=MatchStatus.NO_MATCH,
            confidence=MatchConfidence.VERY_LOW,
            confidence_score=0.0,
            matches=[],
            mismatches=[],
            warnings=[reason],
            suggested_actions=["Manual review required", "Verify PO and receipt information"],
            total_invoice_amount=invoice.total_amount or Decimal("0"),
            total_po_amount=Decimal("0"),
            total_receipt_amount=Decimal("0"),
            variance_amount=Decimal("0"),
            variance_percentage=0.0
        )
