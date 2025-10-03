"""
Advanced Fraud Detection Service
World-class fraud detection using multiple ML models and business rules
"""
import logging
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.models.invoice import Invoice, InvoiceStatus
from src.models.user import User
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from core.config import settings

logger = logging.getLogger(__name__)

class FraudRiskLevel(Enum):
    """Fraud risk levels"""
    LOW = "low"           # 0-30% risk
    MEDIUM = "medium"     # 31-60% risk
    HIGH = "high"         # 61-80% risk
    CRITICAL = "critical" # 81-100% risk

class FraudIndicator(Enum):
    """Types of fraud indicators"""
    AMOUNT_ANOMALY = "amount_anomaly"
    SUPPLIER_ANOMALY = "supplier_anomaly"
    TIMING_ANOMALY = "timing_anomaly"
    PATTERN_ANOMALY = "pattern_anomaly"
    DUPLICATE_SUSPECT = "duplicate_suspect"
    VENDOR_RISK = "vendor_risk"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"

@dataclass
class FraudAnalysisResult:
    """Result of fraud analysis"""
    risk_level: FraudRiskLevel
    risk_score: float
    confidence: float
    indicators: List[Dict[str, Any]]
    recommendations: List[str]
    requires_manual_review: bool
    auto_approve: bool
    auto_reject: bool
    investigation_priority: int  # 1-10, 10 being highest

@dataclass
class FraudIndicator:
    """Individual fraud indicator"""
    type: FraudIndicator
    severity: float  # 0-1
    description: str
    evidence: Dict[str, Any]
    confidence: float

class FraudDetectionService:
    """Advanced fraud detection service using ML and business rules"""
    
    def __init__(self):
        self.risk_thresholds = {
            FraudRiskLevel.LOW: 0.3,
            FraudRiskLevel.MEDIUM: 0.6,
            FraudRiskLevel.HIGH: 0.8,
            FraudRiskLevel.CRITICAL: 1.0
        }
        
        # Business rules for fraud detection
        self.business_rules = {
            "max_amount_single_invoice": 100000,  # $100k
            "max_daily_amount_per_supplier": 500000,  # $500k
            "max_monthly_amount_per_supplier": 2000000,  # $2M
            "suspicious_amount_threshold": 10000,  # $10k
            "duplicate_time_window_hours": 24,
            "new_supplier_risk_threshold": 0.7,
            "weekend_invoice_risk_multiplier": 1.5,
            "after_hours_risk_multiplier": 1.3
        }
    
    async def analyze_fraud_risk(
        self, 
        invoice: Invoice, 
        db: Session,
        historical_data: Optional[List[Invoice]] = None
    ) -> FraudAnalysisResult:
        """
        Perform comprehensive fraud risk analysis on an invoice
        
        Args:
            invoice: Invoice to analyze
            db: Database session
            historical_data: Optional historical invoice data for context
            
        Returns:
            FraudAnalysisResult with detailed analysis
        """
        try:
            logger.info(f"Starting fraud analysis for invoice {invoice.invoice_number}")
            
            # Get historical data if not provided
            if not historical_data:
                historical_data = await self._get_historical_data(invoice, db)
            
            # Run all fraud detection checks
            indicators = []
            
            # Amount-based checks
            amount_indicators = await self._check_amount_anomalies(invoice, historical_data, db)
            indicators.extend(amount_indicators)
            
            # Supplier-based checks
            supplier_indicators = await self._check_supplier_anomalies(invoice, historical_data, db)
            indicators.extend(supplier_indicators)
            
            # Timing-based checks
            timing_indicators = await self._check_timing_anomalies(invoice, historical_data, db)
            indicators.extend(timing_indicators)
            
            # Pattern-based checks
            pattern_indicators = await self._check_pattern_anomalies(invoice, historical_data, db)
            indicators.extend(pattern_indicators)
            
            # Duplicate detection
            duplicate_indicators = await self._check_duplicate_suspects(invoice, historical_data, db)
            indicators.extend(duplicate_indicators)
            
            # Vendor risk assessment
            vendor_indicators = await self._check_vendor_risk(invoice, db)
            indicators.extend(vendor_indicators)
            
            # Behavioral analysis
            behavioral_indicators = await self._check_behavioral_anomalies(invoice, historical_data, db)
            indicators.extend(behavioral_indicators)
            
            # Calculate overall risk score
            risk_score, confidence = self._calculate_risk_score(indicators)
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_level, indicators)
            
            # Determine actions
            requires_manual_review = risk_score > 0.6 or len(indicators) > 3
            auto_approve = risk_score < 0.3 and len(indicators) == 0
            auto_reject = risk_score > 0.9 or any(ind['severity'] > 0.9 for ind in indicators)
            
            # Calculate investigation priority
            investigation_priority = self._calculate_investigation_priority(risk_score, indicators)
            
            result = FraudAnalysisResult(
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=confidence,
                indicators=indicators,
                recommendations=recommendations,
                requires_manual_review=requires_manual_review,
                auto_approve=auto_approve,
                auto_reject=auto_reject,
                investigation_priority=investigation_priority
            )
            
            # Log fraud analysis
            await self._log_fraud_analysis(invoice, result, db)
            
            logger.info(f"Fraud analysis completed for invoice {invoice.invoice_number}: {risk_level.value} risk")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in fraud analysis: {str(e)}")
            raise
    
    async def _get_historical_data(self, invoice: Invoice, db: Session) -> List[Invoice]:
        """Get historical invoice data for analysis"""
        # Get invoices from the same supplier in the last 90 days
        cutoff_date = datetime.now(UTC) - timedelta(days=90)
        
        return db.query(Invoice).filter(
            and_(
                Invoice.company_id == invoice.company_id,
                Invoice.supplier_name == invoice.supplier_name,
                Invoice.created_at >= cutoff_date,
                Invoice.id != invoice.id
            )
        ).all()
    
    async def _check_amount_anomalies(
        self, 
        invoice: Invoice, 
        historical_data: List[Invoice], 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Check for amount-based fraud indicators"""
        indicators = []
        
        # Check for unusually high amounts
        if invoice.total_amount and invoice.total_amount > self.business_rules["max_amount_single_invoice"]:
            indicators.append({
                "type": FraudIndicator.AMOUNT_ANOMALY.value,
                "severity": 0.8,
                "description": f"Unusually high invoice amount: ${invoice.total_amount:,.2f}",
                "evidence": {"amount": float(invoice.total_amount), "threshold": self.business_rules["max_amount_single_invoice"]},
                "confidence": 0.9
            })
        
        # Check for round number amounts (suspicious)
        if invoice.total_amount and invoice.total_amount % 1000 == 0:
            indicators.append({
                "type": FraudIndicator.AMOUNT_ANOMALY.value,
                "severity": 0.3,
                "description": f"Round number amount: ${invoice.total_amount:,.2f}",
                "evidence": {"amount": float(invoice.total_amount)},
                "confidence": 0.6
            })
        
        # Check against historical amounts
        if historical_data and invoice.total_amount:
            historical_amounts = [inv.total_amount for inv in historical_data if inv.total_amount]
            if historical_amounts:
                avg_amount = sum(historical_amounts) / len(historical_amounts)
                std_amount = np.std(historical_amounts)
                
                # Check if amount is significantly higher than historical average
                if invoice.total_amount > avg_amount + (3 * std_amount):
                    indicators.append({
                        "type": FraudIndicator.AMOUNT_ANOMALY.value,
                        "severity": 0.7,
                        "description": f"Amount significantly higher than historical average",
                        "evidence": {
                            "current_amount": float(invoice.total_amount),
                            "historical_avg": float(avg_amount),
                            "standard_deviation": float(std_amount)
                        },
                        "confidence": 0.8
                    })
        
        return indicators
    
    async def _check_supplier_anomalies(
        self, 
        invoice: Invoice, 
        historical_data: List[Invoice], 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Check for supplier-based fraud indicators"""
        indicators = []
        
        # Check for new supplier
        if not historical_data:
            indicators.append({
                "type": FraudIndicator.SUPPLIER_ANOMALY.value,
                "severity": 0.6,
                "description": f"New supplier: {invoice.supplier_name}",
                "evidence": {"supplier_name": invoice.supplier_name},
                "confidence": 0.9
            })
        
        # Check daily amount limits per supplier
        if invoice.total_amount:
            today = invoice.invoice_date.date() if invoice.invoice_date else datetime.now(UTC).date()
            daily_amount = db.query(func.sum(Invoice.total_amount)).filter(
                and_(
                    Invoice.company_id == invoice.company_id,
                    Invoice.supplier_name == invoice.supplier_name,
                    func.date(Invoice.invoice_date) == today
                )
            ).scalar() or 0
            
            if daily_amount + invoice.total_amount > self.business_rules["max_daily_amount_per_supplier"]:
                indicators.append({
                    "type": FraudIndicator.SUPPLIER_ANOMALY.value,
                    "severity": 0.8,
                    "description": f"Exceeds daily amount limit for supplier",
                    "evidence": {
                        "daily_amount": float(daily_amount),
                        "invoice_amount": float(invoice.total_amount),
                        "limit": self.business_rules["max_daily_amount_per_supplier"]
                    },
                    "confidence": 0.9
                })
        
        return indicators
    
    async def _check_timing_anomalies(
        self, 
        invoice: Invoice, 
        historical_data: List[Invoice], 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Check for timing-based fraud indicators"""
        indicators = []
        
        if not invoice.invoice_date:
            return indicators
        
        # Check for weekend invoices
        if invoice.invoice_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            indicators.append({
                "type": FraudIndicator.TIMING_ANOMALY.value,
                "severity": 0.4,
                "description": f"Weekend invoice: {invoice.invoice_date.strftime('%A')}",
                "evidence": {"invoice_date": invoice.invoice_date.isoformat()},
                "confidence": 0.8
            })
        
        # Check for after-hours invoices (after 6 PM or before 8 AM)
        hour = invoice.invoice_date.hour
        if hour < 8 or hour > 18:
            indicators.append({
                "type": FraudIndicator.TIMING_ANOMALY.value,
                "severity": 0.3,
                "description": f"After-hours invoice: {hour:02d}:00",
                "evidence": {"invoice_date": invoice.invoice_date.isoformat(), "hour": hour},
                "confidence": 0.7
            })
        
        return indicators
    
    async def _check_pattern_anomalies(
        self, 
        invoice: Invoice, 
        historical_data: List[Invoice], 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Check for pattern-based fraud indicators"""
        indicators = []
        
        # Check for sequential invoice numbers (suspicious)
        if invoice.invoice_number and historical_data:
            recent_invoices = sorted(historical_data, key=lambda x: x.invoice_date or datetime.min, reverse=True)[:5]
            recent_numbers = [inv.invoice_number for inv in recent_invoices if inv.invoice_number]
            
            if recent_numbers and invoice.invoice_number in recent_numbers:
                indicators.append({
                    "type": FraudIndicator.PATTERN_ANOMALY.value,
                    "severity": 0.8,
                    "description": f"Duplicate invoice number: {invoice.invoice_number}",
                    "evidence": {"invoice_number": invoice.invoice_number, "recent_numbers": recent_numbers},
                    "confidence": 0.9
                })
        
        return indicators
    
    async def _check_duplicate_suspects(
        self, 
        invoice: Invoice, 
        historical_data: List[Invoice], 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Check for potential duplicate invoices"""
        indicators = []
        
        if not historical_data:
            return indicators
        
        # Check for similar amounts within time window
        time_window = timedelta(hours=self.business_rules["duplicate_time_window_hours"])
        similar_amounts = []
        
        for hist_invoice in historical_data:
            if (hist_invoice.total_amount and invoice.total_amount and
                abs(hist_invoice.total_amount - invoice.total_amount) < 1.0 and  # Within $1
                hist_invoice.invoice_date and invoice.invoice_date and
                abs((hist_invoice.invoice_date - invoice.invoice_date).total_seconds()) < time_window.total_seconds()):
                similar_amounts.append(hist_invoice)
        
        if similar_amounts:
            indicators.append({
                "type": FraudIndicator.DUPLICATE_SUSPECT.value,
                "severity": 0.7,
                "description": f"Potential duplicate: {len(similar_amounts)} similar invoices found",
                "evidence": {
                    "similar_count": len(similar_amounts),
                    "similar_invoices": [str(inv.id) for inv in similar_amounts]
                },
                "confidence": 0.8
            })
        
        return indicators
    
    async def _check_vendor_risk(self, invoice: Invoice, db: Session) -> List[Dict[str, Any]]:
        """Check vendor risk factors"""
        indicators = []
        
        # This would typically check against a vendor risk database
        # For now, implement basic checks
        
        # Check for suspicious supplier names
        suspicious_patterns = ["test", "demo", "sample", "fake", "dummy"]
        if any(pattern in invoice.supplier_name.lower() for pattern in suspicious_patterns):
            indicators.append({
                "type": FraudIndicator.VENDOR_RISK.value,
                "severity": 0.9,
                "description": f"Suspicious supplier name: {invoice.supplier_name}",
                "evidence": {"supplier_name": invoice.supplier_name},
                "confidence": 0.9
            })
        
        return indicators
    
    async def _check_behavioral_anomalies(
        self, 
        invoice: Invoice, 
        historical_data: List[Invoice], 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Check for behavioral anomalies"""
        indicators = []
        
        # Check for unusual approval patterns
        if invoice.created_by_id:
            user_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.created_by_id == invoice.created_by_id,
                    Invoice.company_id == invoice.company_id,
                    Invoice.created_at >= datetime.now(UTC) - timedelta(days=30)
                )
            ).all()
            
            if len(user_invoices) > 50:  # More than 50 invoices in 30 days
                indicators.append({
                    "type": FraudIndicator.BEHAVIORAL_ANOMALY.value,
                    "severity": 0.6,
                    "description": f"High volume of invoices from user: {len(user_invoices)} in 30 days",
                    "evidence": {"invoice_count": len(user_invoices)},
                    "confidence": 0.8
                })
        
        return indicators
    
    def _calculate_risk_score(self, indicators: List[Dict[str, Any]]) -> Tuple[float, float]:
        """Calculate overall risk score and confidence"""
        if not indicators:
            return 0.0, 1.0
        
        # Weighted average of indicator severities
        total_weight = 0.0
        weighted_sum = 0.0
        confidence_sum = 0.0
        
        for indicator in indicators:
            severity = indicator["severity"]
            confidence = indicator["confidence"]
            
            # Weight by confidence
            weight = confidence
            total_weight += weight
            weighted_sum += severity * weight
            confidence_sum += confidence
        
        risk_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        avg_confidence = confidence_sum / len(indicators) if indicators else 1.0
        
        return min(1.0, risk_score), avg_confidence
    
    def _determine_risk_level(self, risk_score: float) -> FraudRiskLevel:
        """Determine risk level based on score"""
        if risk_score >= self.risk_thresholds[FraudRiskLevel.CRITICAL]:
            return FraudRiskLevel.CRITICAL
        elif risk_score >= self.risk_thresholds[FraudRiskLevel.HIGH]:
            return FraudRiskLevel.HIGH
        elif risk_score >= self.risk_thresholds[FraudRiskLevel.MEDIUM]:
            return FraudRiskLevel.MEDIUM
        else:
            return FraudRiskLevel.LOW
    
    def _generate_recommendations(
        self, 
        risk_level: FraudRiskLevel, 
        indicators: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on risk level and indicators"""
        recommendations = []
        
        if risk_level == FraudRiskLevel.CRITICAL:
            recommendations.extend([
                "IMMEDIATE MANUAL REVIEW REQUIRED",
                "Contact supplier to verify invoice authenticity",
                "Review all recent invoices from this supplier",
                "Consider suspending supplier account"
            ])
        elif risk_level == FraudRiskLevel.HIGH:
            recommendations.extend([
                "Manual review recommended",
                "Verify supplier details and invoice authenticity",
                "Check for duplicate payments"
            ])
        elif risk_level == FraudRiskLevel.MEDIUM:
            recommendations.extend([
                "Additional verification recommended",
                "Review invoice details carefully"
            ])
        else:
            recommendations.append("Low risk - standard processing")
        
        # Add specific recommendations based on indicators
        indicator_types = [ind["type"] for ind in indicators]
        
        if FraudIndicator.AMOUNT_ANOMALY.value in indicator_types:
            recommendations.append("Verify invoice amount with supplier")
        
        if FraudIndicator.DUPLICATE_SUSPECT.value in indicator_types:
            recommendations.append("Check for duplicate payments")
        
        if FraudIndicator.SUPPLIER_ANOMALY.value in indicator_types:
            recommendations.append("Verify supplier information")
        
        return recommendations
    
    def _calculate_investigation_priority(
        self, 
        risk_score: float, 
        indicators: List[Dict[str, Any]]
    ) -> int:
        """Calculate investigation priority (1-10)"""
        base_priority = int(risk_score * 10)
        
        # Increase priority for critical indicators
        critical_indicators = [ind for ind in indicators if ind["severity"] > 0.8]
        priority_boost = len(critical_indicators) * 2
        
        return min(10, base_priority + priority_boost)
    
    async def _log_fraud_analysis(
        self, 
        invoice: Invoice, 
        result: FraudAnalysisResult, 
        db: Session
    ):
        """Log fraud analysis results"""
        try:
            audit_log = AuditLog(
                company_id=invoice.company_id,
                user_id=invoice.created_by_id,
                action=AuditAction.FRAUD_ANALYSIS,
                resource_type=AuditResourceType.INVOICE,
                resource_id=invoice.id,
                details={
                    "risk_level": result.risk_level.value,
                    "risk_score": result.risk_score,
                    "confidence": result.confidence,
                    "indicators_count": len(result.indicators),
                    "requires_manual_review": result.requires_manual_review,
                    "auto_approve": result.auto_approve,
                    "auto_reject": result.auto_reject,
                    "investigation_priority": result.investigation_priority
                }
            )
            
            db.add(audit_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log fraud analysis: {str(e)}")
    
    async def get_fraud_analytics(self, company_id: str, db: Session) -> Dict[str, Any]:
        """Get fraud analytics for a company"""
        try:
            # Get fraud analysis data from audit logs
            fraud_logs = db.query(AuditLog).filter(
                and_(
                    AuditLog.company_id == company_id,
                    AuditLog.action == AuditAction.FRAUD_ANALYSIS,
                    AuditLog.created_at >= datetime.now(UTC) - timedelta(days=30)
                )
            ).all()
            
            if not fraud_logs:
                return {
                    "total_analyses": 0,
                    "risk_distribution": {},
                    "common_indicators": [],
                    "trends": []
                }
            
            # Analyze risk distribution
            risk_levels = [log.details.get("risk_level") for log in fraud_logs if log.details]
            risk_distribution = {}
            for level in risk_levels:
                risk_distribution[level] = risk_distribution.get(level, 0) + 1
            
            # Calculate average risk score
            risk_scores = [log.details.get("risk_score", 0) for log in fraud_logs if log.details]
            avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            return {
                "total_analyses": len(fraud_logs),
                "risk_distribution": risk_distribution,
                "average_risk_score": avg_risk_score,
                "high_risk_count": sum(1 for score in risk_scores if score > 0.6),
                "critical_risk_count": sum(1 for score in risk_scores if score > 0.8),
                "manual_review_count": sum(1 for log in fraud_logs if log.details.get("requires_manual_review", False))
            }
            
        except Exception as e:
            logger.error(f"Failed to get fraud analytics: {str(e)}")
            return {"error": str(e)}
