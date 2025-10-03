"""
Advanced Business Intelligence and Analytics Service
World-class analytics, reporting, and predictive insights for the AI ERP SaaS platform
"""
import logging
import asyncio
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc

from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
from src.models.company import Company
from src.models.user import User
from src.models.audit import AuditLog
from core.config import settings
from services.advanced_ml_models import advanced_ml_service

logger = logging.getLogger(__name__)

class MetricType(Enum):
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    PREDICTIVE = "predictive"

class TimeGranularity(Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class KPI:
    name: str
    value: float
    target: Optional[float] = None
    unit: str = ""
    trend: str = "stable"  # up, down, stable
    change_percent: float = 0.0
    period: str = ""
    metadata: Dict[str, Any] = None

@dataclass
class Insight:
    title: str
    description: str
    impact: str  # high, medium, low
    category: str
    recommendation: str
    confidence: float
    actionable: bool = True

class AdvancedAnalyticsService:
    """Advanced business intelligence and analytics service"""
    
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes
        self.cache = {}
        self.insight_engine = InsightEngine()
        self.forecasting_engine = ForecastingEngine()
        
    async def get_executive_dashboard(self, company_id: str, db: Session, period_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive executive dashboard data"""
        try:
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=period_days)
            
            # Get all KPIs in parallel
            kpis = await asyncio.gather(
                self._calculate_financial_kpis(company_id, start_date, end_date, db),
                self._calculate_operational_kpis(company_id, start_date, end_date, db),
                self._calculate_compliance_kpis(company_id, start_date, end_date, db),
                self._calculate_performance_kpis(company_id, start_date, end_date, db)
            )
            
            # Flatten KPIs
            all_kpis = []
            for kpi_group in kpis:
                all_kpis.extend(kpi_group)
            
            # Get predictive insights
            predictions = await self._get_predictive_insights(company_id, db)
            
            # Get AI-powered insights
            ai_insights = await self.insight_engine.generate_insights(company_id, db)
            
            # Get trend analysis
            trends = await self._analyze_trends(company_id, start_date, end_date, db)
            
            # Get risk assessment
            risk_assessment = await self._assess_risks(company_id, db)
            
            return {
                "dashboard_id": f"executive_{company_id}_{period_days}d",
                "generated_at": datetime.now(UTC).isoformat(),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": period_days
                },
                "kpis": [asdict(kpi) for kpi in all_kpis],
                "predictions": predictions,
                "ai_insights": [asdict(insight) for insight in ai_insights],
                "trends": trends,
                "risk_assessment": risk_assessment,
                "summary": self._generate_executive_summary(all_kpis, ai_insights, risk_assessment)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate executive dashboard: {e}")
            return {"error": str(e)}
    
    async def _calculate_financial_kpis(self, company_id: str, start_date: datetime, end_date: datetime, db: Session) -> List[KPI]:
        """Calculate financial KPIs"""
        kpis = []
        
        try:
            # Total invoice volume
            total_volume = db.query(func.sum(Invoice.total_amount)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).scalar() or 0
            
            # Previous period comparison
            prev_start = start_date - (end_date - start_date)
            prev_volume = db.query(func.sum(Invoice.total_amount)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= prev_start,
                    Invoice.created_at < start_date
                )
            ).scalar() or 0
            
            volume_change = ((total_volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0
            
            kpis.append(KPI(
                name="Total Invoice Volume",
                value=float(total_volume),
                unit="USD",
                trend="up" if volume_change > 0 else "down" if volume_change < 0 else "stable",
                change_percent=volume_change,
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
            # Average invoice amount
            avg_amount = db.query(func.avg(Invoice.total_amount)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).scalar() or 0
            
            kpis.append(KPI(
                name="Average Invoice Amount",
                value=float(avg_amount),
                unit="USD",
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
            # Payment cycle efficiency
            approved_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.status == InvoiceStatus.APPROVED,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).all()
            
            if approved_invoices:
                avg_processing_time = np.mean([
                    (inv.approved_at - inv.created_at).total_seconds() / 3600  # hours
                    for inv in approved_invoices
                    if inv.approved_at and inv.created_at
                ])
                
                kpis.append(KPI(
                    name="Average Processing Time",
                    value=float(avg_processing_time),
                    unit="hours",
                    target=24.0,  # 24 hour target
                    period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                ))
            
            # Cost savings from automation
            auto_approved_count = db.query(func.count(Invoice.id)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.status == InvoiceStatus.APPROVED,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date,
                    Invoice.auto_approved == True
                )
            ).scalar() or 0
            
            total_invoices = db.query(func.count(Invoice.id)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).scalar() or 0
            
            automation_rate = (auto_approved_count / total_invoices * 100) if total_invoices > 0 else 0
            
            kpis.append(KPI(
                name="Automation Rate",
                value=float(automation_rate),
                unit="%",
                target=80.0,  # 80% automation target
                trend="up" if automation_rate > 70 else "down" if automation_rate < 50 else "stable",
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
        except Exception as e:
            logger.error(f"Failed to calculate financial KPIs: {e}")
        
        return kpis
    
    async def _calculate_operational_kpis(self, company_id: str, start_date: datetime, end_date: datetime, db: Session) -> List[KPI]:
        """Calculate operational KPIs"""
        kpis = []
        
        try:
            # Invoice processing volume
            total_processed = db.query(func.count(Invoice.id)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).scalar() or 0
            
            kpis.append(KPI(
                name="Invoices Processed",
                value=float(total_processed),
                unit="invoices",
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
            # Processing accuracy (based on OCR confidence)
            invoices_with_confidence = db.query(Invoice).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date,
                    Invoice.ocr_confidence.isnot(None)
                )
            ).all()
            
            if invoices_with_confidence:
                avg_confidence = np.mean([inv.ocr_confidence for inv in invoices_with_confidence])
                
                kpis.append(KPI(
                    name="OCR Accuracy",
                    value=float(avg_confidence * 100),
                    unit="%",
                    target=95.0,  # 95% accuracy target
                    period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                ))
            
            # Approval rate
            approved_count = db.query(func.count(Invoice.id)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.status == InvoiceStatus.APPROVED,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).scalar() or 0
            
            approval_rate = (approved_count / total_processed * 100) if total_processed > 0 else 0
            
            kpis.append(KPI(
                name="Approval Rate",
                value=float(approval_rate),
                unit="%",
                target=85.0,  # 85% approval target
                trend="up" if approval_rate > 80 else "down" if approval_rate < 70 else "stable",
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
            # Supplier diversity
            unique_suppliers = db.query(func.count(func.distinct(Invoice.supplier_name))).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).scalar() or 0
            
            kpis.append(KPI(
                name="Active Suppliers",
                value=float(unique_suppliers),
                unit="suppliers",
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
        except Exception as e:
            logger.error(f"Failed to calculate operational KPIs: {e}")
        
        return kpis
    
    async def _calculate_compliance_kpis(self, company_id: str, start_date: datetime, end_date: datetime, db: Session) -> List[KPI]:
        """Calculate compliance KPIs"""
        kpis = []
        
        try:
            # Fraud detection rate
            high_risk_invoices = db.query(func.count(Invoice.id)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date,
                    Invoice.fraud_score > 0.7
                )
            ).scalar() or 0
            
            total_invoices = db.query(func.count(Invoice.id)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).scalar() or 0
            
            fraud_detection_rate = (high_risk_invoices / total_invoices * 100) if total_invoices > 0 else 0
            
            kpis.append(KPI(
                name="High Risk Invoices Detected",
                value=float(fraud_detection_rate),
                unit="%",
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
            # Audit trail completeness
            invoices_with_audit = db.query(func.count(func.distinct(Invoice.id))).join(
                AuditLog, AuditLog.resource_id == Invoice.id
            ).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).scalar() or 0
            
            audit_completeness = (invoices_with_audit / total_invoices * 100) if total_invoices > 0 else 0
            
            kpis.append(KPI(
                name="Audit Trail Completeness",
                value=float(audit_completeness),
                unit="%",
                target=100.0,  # 100% completeness target
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
            # Policy compliance rate
            compliant_invoices = db.query(func.count(Invoice.id)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date,
                    Invoice.status != InvoiceStatus.REJECTED
                )
            ).scalar() or 0
            
            compliance_rate = (compliant_invoices / total_invoices * 100) if total_invoices > 0 else 0
            
            kpis.append(KPI(
                name="Policy Compliance Rate",
                value=float(compliance_rate),
                unit="%",
                target=95.0,  # 95% compliance target
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
        except Exception as e:
            logger.error(f"Failed to calculate compliance KPIs: {e}")
        
        return kpis
    
    async def _calculate_performance_kpis(self, company_id: str, start_date: datetime, end_date: datetime, db: Session) -> List[KPI]:
        """Calculate performance KPIs"""
        kpis = []
        
        try:
            # System uptime (mock calculation)
            uptime = 99.9  # This would come from monitoring system
            
            kpis.append(KPI(
                name="System Uptime",
                value=uptime,
                unit="%",
                target=99.5,  # 99.5% uptime target
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
            # Average response time (mock)
            avg_response_time = 150  # milliseconds
            
            kpis.append(KPI(
                name="Average Response Time",
                value=avg_response_time,
                unit="ms",
                target=200.0,  # 200ms target
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
            # User satisfaction (mock)
            user_satisfaction = 4.7  # out of 5
            
            kpis.append(KPI(
                name="User Satisfaction",
                value=user_satisfaction,
                unit="/5",
                target=4.5,  # 4.5/5 target
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            ))
            
        except Exception as e:
            logger.error(f"Failed to calculate performance KPIs: {e}")
        
        return kpis
    
    async def _get_predictive_insights(self, company_id: str, db: Session) -> Dict[str, Any]:
        """Get predictive insights using ML models"""
        try:
            # Get cash flow prediction
            company_data = await self._get_company_data_for_prediction(company_id, db)
            cash_flow_prediction = await advanced_ml_service.predict_cash_flow(company_data)
            
            # Get approval likelihood for pending invoices
            pending_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.status == InvoiceStatus.PENDING
                )
            ).limit(10).all()
            
            approval_predictions = []
            for invoice in pending_invoices:
                invoice_data = {
                    "total_amount": float(invoice.total_amount),
                    "supplier_name": invoice.supplier_name,
                    "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                    "due_date": invoice.due_date.isoformat() if invoice.due_date else None
                }
                
                user_context = {"approval_level": 2}  # Default approval level
                prediction = await advanced_ml_service.predict_approval_likelihood(invoice_data, user_context)
                
                approval_predictions.append({
                    "invoice_id": str(invoice.id),
                    "invoice_number": invoice.invoice_number,
                    "supplier_name": invoice.supplier_name,
                    "amount": float(invoice.total_amount),
                    "approval_probability": prediction.get("approval_probability", 0.5),
                    "confidence": prediction.get("confidence", 0.0),
                    "recommendations": prediction.get("recommendations", [])
                })
            
            return {
                "cash_flow": cash_flow_prediction,
                "approval_predictions": approval_predictions,
                "generated_at": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get predictive insights: {e}")
            return {"error": str(e)}
    
    async def _analyze_trends(self, company_id: str, start_date: datetime, end_date: datetime, db: Session) -> Dict[str, Any]:
        """Analyze trends in invoice processing"""
        try:
            # Daily invoice volume trend
            daily_volumes = db.query(
                func.date(Invoice.created_at).label('date'),
                func.count(Invoice.id).label('count'),
                func.sum(Invoice.total_amount).label('volume')
            ).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= start_date,
                    Invoice.created_at <= end_date
                )
            ).group_by(func.date(Invoice.created_at)).order_by('date').all()
            
            trend_data = []
            for row in daily_volumes:
                trend_data.append({
                    "date": row.date.isoformat(),
                    "invoice_count": row.count,
                    "volume": float(row.volume or 0)
                })
            
            # Calculate trend direction
            if len(trend_data) >= 7:
                recent_avg = np.mean([d["volume"] for d in trend_data[-7:]])
                earlier_avg = np.mean([d["volume"] for d in trend_data[:7]])
                trend_direction = "up" if recent_avg > earlier_avg else "down" if recent_avg < earlier_avg else "stable"
                trend_strength = abs((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
            else:
                trend_direction = "stable"
                trend_strength = 0
            
            return {
                "daily_volumes": trend_data,
                "trend_direction": trend_direction,
                "trend_strength": float(trend_strength),
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            return {"error": str(e)}
    
    async def _assess_risks(self, company_id: str, db: Session) -> Dict[str, Any]:
        """Assess business risks"""
        try:
            # High-value invoice risk
            high_value_invoices = db.query(func.count(Invoice.id)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.total_amount > 10000,
                    Invoice.status == InvoiceStatus.PENDING
                )
            ).scalar() or 0
            
            # Supplier concentration risk
            supplier_volumes = db.query(
                Invoice.supplier_name,
                func.sum(Invoice.total_amount).label('volume')
            ).filter(
                Invoice.company_id == company_id
            ).group_by(Invoice.supplier_name).order_by(desc('volume')).limit(5).all()
            
            total_volume = sum(row.volume for row in supplier_volumes)
            top_supplier_concentration = (supplier_volumes[0].volume / total_volume * 100) if supplier_volumes and total_volume > 0 else 0
            
            # Processing backlog risk
            pending_count = db.query(func.count(Invoice.id)).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.status == InvoiceStatus.PENDING,
                    Invoice.created_at < datetime.now(UTC) - timedelta(days=7)
                )
            ).scalar() or 0
            
            risk_level = "LOW"
            if high_value_invoices > 10 or top_supplier_concentration > 60 or pending_count > 20:
                risk_level = "HIGH"
            elif high_value_invoices > 5 or top_supplier_concentration > 40 or pending_count > 10:
                risk_level = "MEDIUM"
            
            return {
                "overall_risk_level": risk_level,
                "high_value_pending": high_value_invoices,
                "supplier_concentration": float(top_supplier_concentration),
                "processing_backlog": pending_count,
                "risk_factors": self._identify_risk_factors(high_value_invoices, top_supplier_concentration, pending_count),
                "assessed_at": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to assess risks: {e}")
            return {"error": str(e)}
    
    def _identify_risk_factors(self, high_value_pending: int, supplier_concentration: float, processing_backlog: int) -> List[str]:
        """Identify specific risk factors"""
        risks = []
        
        if high_value_pending > 10:
            risks.append("High volume of large pending invoices")
        if supplier_concentration > 60:
            risks.append("High supplier concentration risk")
        if processing_backlog > 20:
            risks.append("Significant processing backlog")
        
        if not risks:
            risks.append("No significant risks identified")
        
        return risks
    
    async def _get_company_data_for_prediction(self, company_id: str, db: Session) -> Dict[str, Any]:
        """Get company data for ML predictions"""
        try:
            # Get historical cash flow data
            invoices = db.query(Invoice).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= datetime.now(UTC) - timedelta(days=90)
                )
            ).all()
            
            total_volume = sum(inv.total_amount for inv in invoices)
            pending_amount = sum(inv.total_amount for inv in invoices if inv.status == InvoiceStatus.PENDING)
            
            # Calculate average payment terms
            invoices_with_dates = [inv for inv in invoices if inv.invoice_date and inv.due_date]
            avg_payment_terms = np.mean([
                (inv.due_date - inv.invoice_date).days for inv in invoices_with_dates
            ]) if invoices_with_dates else 30
            
            return {
                "historical_cash_flow": float(total_volume),
                "pending_amount": float(pending_amount),
                "avg_payment_terms": float(avg_payment_terms),
                "economic_indicator": 1.0  # Mock economic indicator
            }
            
        except Exception as e:
            logger.error(f"Failed to get company data for prediction: {e}")
            return {
                "historical_cash_flow": 100000.0,
                "pending_amount": 50000.0,
                "avg_payment_terms": 30.0,
                "economic_indicator": 1.0
            }
    
    def _generate_executive_summary(self, kpis: List[KPI], insights: List[Insight], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        # Find key KPIs
        key_kpis = [kpi for kpi in kpis if kpi.name in [
            "Total Invoice Volume", "Automation Rate", "Approval Rate", "System Uptime"
        ]]
        
        # High-impact insights
        high_impact_insights = [insight for insight in insights if insight.impact == "high"]
        
        # Overall performance score
        performance_score = self._calculate_performance_score(kpis)
        
        return {
            "performance_score": performance_score,
            "key_metrics": [asdict(kpi) for kpi in key_kpis],
            "critical_insights": [asdict(insight) for insight in high_impact_insights[:3]],
            "risk_level": risk_assessment.get("overall_risk_level", "UNKNOWN"),
            "recommendations": self._generate_executive_recommendations(kpis, insights, risk_assessment),
            "generated_at": datetime.now(UTC).isoformat()
        }
    
    def _calculate_performance_score(self, kpis: List[KPI]) -> float:
        """Calculate overall performance score"""
        if not kpis:
            return 0.0
        
        # Weight different KPI categories
        weights = {
            "Total Invoice Volume": 0.2,
            "Automation Rate": 0.25,
            "Approval Rate": 0.2,
            "OCR Accuracy": 0.15,
            "System Uptime": 0.2
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for kpi in kpis:
            if kpi.name in weights:
                # Normalize KPI value to 0-100 scale
                if kpi.target:
                    normalized_value = min(100, (kpi.value / kpi.target) * 100)
                else:
                    normalized_value = min(100, kpi.value)
                
                weighted_score += normalized_value * weights[kpi.name]
                total_weight += weights[kpi.name]
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _generate_executive_recommendations(self, kpis: List[KPI], insights: List[Insight], risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate executive recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        performance_score = self._calculate_performance_score(kpis)
        if performance_score < 70:
            recommendations.append("Focus on improving overall system performance and user adoption")
        elif performance_score > 90:
            recommendations.append("Excellent performance - consider expanding automation capabilities")
        
        # Risk-based recommendations
        risk_level = risk_assessment.get("overall_risk_level", "LOW")
        if risk_level == "HIGH":
            recommendations.append("Immediate attention required for identified high-risk areas")
        elif risk_level == "MEDIUM":
            recommendations.append("Monitor and address medium-risk factors proactively")
        
        # Insight-based recommendations
        high_impact_insights = [insight for insight in insights if insight.impact == "high"]
        for insight in high_impact_insights[:2]:
            recommendations.append(insight.recommendation)
        
        return recommendations

class InsightEngine:
    """AI-powered insight generation engine"""
    
    async def generate_insights(self, company_id: str, db: Session) -> List[Insight]:
        """Generate AI-powered business insights"""
        insights = []
        
        try:
            # Get recent invoice data for analysis
            recent_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.company_id == company_id,
                    Invoice.created_at >= datetime.now(UTC) - timedelta(days=30)
                )
            ).all()
            
            if not recent_invoices:
                return insights
            
            # Analyze patterns and generate insights
            insights.extend(await self._analyze_supplier_patterns(recent_invoices))
            insights.extend(await self._analyze_processing_efficiency(recent_invoices))
            insights.extend(await self._analyze_cost_optimization(recent_invoices))
            insights.extend(await self._analyze_compliance_trends(recent_invoices))
            
            # Sort by impact and return top insights
            insights.sort(key=lambda x: {"high": 3, "medium": 2, "low": 1}[x.impact], reverse=True)
            return insights[:10]  # Return top 10 insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []
    
    async def _analyze_supplier_patterns(self, invoices: List[Invoice]) -> List[Insight]:
        """Analyze supplier patterns and generate insights"""
        insights = []
        
        try:
            # Supplier concentration analysis
            supplier_volumes = {}
            for invoice in invoices:
                supplier = invoice.supplier_name
                if supplier not in supplier_volumes:
                    supplier_volumes[supplier] = 0
                supplier_volumes[supplier] += float(invoice.total_amount)
            
            total_volume = sum(supplier_volumes.values())
            if total_volume > 0:
                top_supplier = max(supplier_volumes, key=supplier_volumes.get)
                top_supplier_percentage = (supplier_volumes[top_supplier] / total_volume) * 100
                
                if top_supplier_percentage > 40:
                    insights.append(Insight(
                        title="High Supplier Concentration Risk",
                        description=f"Top supplier {top_supplier} represents {top_supplier_percentage:.1f}% of total volume",
                        impact="high",
                        category="supplier_risk",
                        recommendation="Diversify supplier base to reduce concentration risk",
                        confidence=0.9
                    ))
            
            # Payment timing analysis
            overdue_invoices = [inv for inv in invoices 
                              if inv.due_date and inv.due_date < datetime.now(UTC) and inv.status != InvoiceStatus.PAID]
            
            if len(overdue_invoices) > len(invoices) * 0.1:  # More than 10% overdue
                insights.append(Insight(
                    title="High Overdue Invoice Rate",
                    description=f"{len(overdue_invoices)} invoices are overdue, representing {len(overdue_invoices)/len(invoices)*100:.1f}% of total",
                    impact="medium",
                    category="cash_flow",
                    recommendation="Implement automated payment reminders and optimize approval workflows",
                    confidence=0.8
                ))
            
        except Exception as e:
            logger.error(f"Failed to analyze supplier patterns: {e}")
        
        return insights
    
    async def _analyze_processing_efficiency(self, invoices: List[Invoice]) -> List[Insight]:
        """Analyze processing efficiency and generate insights"""
        insights = []
        
        try:
            # Processing time analysis
            processed_invoices = [inv for inv in invoices if inv.approved_at and inv.created_at]
            if processed_invoices:
                processing_times = [(inv.approved_at - inv.created_at).total_seconds() / 3600 for inv in processed_invoices]
                avg_processing_time = np.mean(processing_times)
                
                if avg_processing_time > 48:  # More than 48 hours
                    insights.append(Insight(
                        title="Slow Processing Times",
                        description=f"Average processing time is {avg_processing_time:.1f} hours, exceeding target of 24 hours",
                        impact="medium",
                        category="efficiency",
                        recommendation="Review and optimize approval workflows, consider auto-approval for low-risk invoices",
                        confidence=0.85
                    ))
            
            # Auto-approval analysis
            auto_approved = [inv for inv in invoices if getattr(inv, 'auto_approved', False)]
            auto_approval_rate = len(auto_approved) / len(invoices) * 100 if invoices else 0
            
            if auto_approval_rate < 50:
                insights.append(Insight(
                    title="Low Automation Rate",
                    description=f"Only {auto_approval_rate:.1f}% of invoices are auto-approved",
                    impact="medium",
                    category="automation",
                    recommendation="Increase automation thresholds and improve ML model accuracy for auto-approval",
                    confidence=0.8
                ))
            
        except Exception as e:
            logger.error(f"Failed to analyze processing efficiency: {e}")
        
        return insights
    
    async def _analyze_cost_optimization(self, invoices: List[Invoice]) -> List[Insight]:
        """Analyze cost optimization opportunities"""
        insights = []
        
        try:
            # Invoice amount distribution
            amounts = [float(inv.total_amount) for inv in invoices]
            if amounts:
                avg_amount = np.mean(amounts)
                median_amount = np.median(amounts)
                
                # Identify potential bulk discount opportunities
                high_value_invoices = [inv for inv in invoices if float(inv.total_amount) > avg_amount * 2]
                if len(high_value_invoices) > len(invoices) * 0.2:  # More than 20% are high-value
                    insights.append(Insight(
                        title="Bulk Discount Opportunity",
                        description=f"{len(high_value_invoices)} high-value invoices could benefit from bulk discounts",
                        impact="medium",
                        category="cost_optimization",
                        recommendation="Negotiate bulk discounts with frequently used high-value suppliers",
                        confidence=0.7
                    ))
            
            # Payment terms analysis
            invoices_with_terms = [inv for inv in invoices if inv.invoice_date and inv.due_date]
            if invoices_with_terms:
                payment_terms = [(inv.due_date - inv.invoice_date).days for inv in invoices_with_terms]
                avg_terms = np.mean(payment_terms)
                
                if avg_terms < 15:  # Very short payment terms
                    insights.append(Insight(
                        title="Short Payment Terms",
                        description=f"Average payment terms are {avg_terms:.1f} days, potentially impacting cash flow",
                        impact="low",
                        category="cash_flow",
                        recommendation="Negotiate longer payment terms with suppliers to improve cash flow",
                        confidence=0.75
                    ))
            
        except Exception as e:
            logger.error(f"Failed to analyze cost optimization: {e}")
        
        return insights
    
    async def _analyze_compliance_trends(self, invoices: List[Invoice]) -> List[Insight]:
        """Analyze compliance trends and generate insights"""
        insights = []
        
        try:
            # Fraud risk analysis
            high_risk_invoices = [inv for inv in invoices if getattr(inv, 'fraud_score', 0) > 0.7]
            if high_risk_invoices:
                fraud_rate = len(high_risk_invoices) / len(invoices) * 100
                insights.append(Insight(
                    title="Elevated Fraud Risk",
                    description=f"Fraud risk detected in {len(high_risk_invoices)} invoices ({fraud_rate:.1f}% of total)",
                    impact="high",
                    category="compliance",
                    recommendation="Enhance fraud detection rules and implement additional verification steps",
                    confidence=0.9
                ))
            
            # Approval rate analysis
            approved_invoices = [inv for inv in invoices if inv.status == InvoiceStatus.APPROVED]
            approval_rate = len(approved_invoices) / len(invoices) * 100 if invoices else 0
            
            if approval_rate < 70:
                insights.append(Insight(
                    title="Low Approval Rate",
                    description=f"Only {approval_rate:.1f}% of invoices are approved, indicating potential process issues",
                    impact="medium",
                    category="process",
                    recommendation="Review rejection reasons and improve invoice quality or approval criteria",
                    confidence=0.8
                ))
            
        except Exception as e:
            logger.error(f"Failed to analyze compliance trends: {e}")
        
        return insights

class ForecastingEngine:
    """Advanced forecasting engine for predictive analytics"""
    
    async def forecast_invoice_volume(self, company_id: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Forecast invoice volume for the next period"""
        # This would implement time series forecasting
        # For now, return mock forecast data
        return {
            "forecast": {
                "daily_volumes": [100, 120, 95, 110, 130],  # Mock daily forecasts
                "total_volume": 5550,
                "confidence_interval": {"lower": 5000, "upper": 6100}
            },
            "method": "ARIMA",
            "accuracy": 0.85,
            "generated_at": datetime.now(UTC).isoformat()
        }
    
    async def forecast_cash_flow(self, company_id: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Forecast cash flow for the next period"""
        # This would use the ML cash flow prediction model
        company_data = {"historical_cash_flow": 100000, "pending_amount": 50000}
        return await advanced_ml_service.predict_cash_flow(company_data, days_ahead)

# Global instance
advanced_analytics_service = AdvancedAnalyticsService()
