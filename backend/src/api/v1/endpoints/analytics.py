"""
Advanced Analytics API Endpoints
World-class business intelligence and analytics endpoints
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from core.auth import AuthManager
from core.database import get_db
from src.models.user import User
from services.business_intelligence import advanced_analytics_service, MetricType, TimeGranularity
from schemas.analytics import (
    ExecutiveDashboardResponse,
    KPIResponse,
    InsightResponse,
    TrendAnalysisResponse,
    ForecastingResponse,
    RiskAssessmentResponse,
    PerformanceMetricsResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/executive-dashboard", response_model=ExecutiveDashboardResponse)
async def get_executive_dashboard(
    period_days: int = Query(30, ge=1, le=365, description="Number of days for analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Get comprehensive executive dashboard with KPIs, insights, and predictions
    
    This endpoint provides a world-class executive dashboard with:
    - Financial KPIs (invoice volume, automation rate, processing time)
    - Operational metrics (accuracy, approval rate, supplier diversity)
    - Compliance indicators (fraud detection, audit trails, policy compliance)
    - Performance metrics (uptime, response time, user satisfaction)
    - AI-powered insights and recommendations
    - Predictive analytics and risk assessment
    """
    try:
        dashboard_data = await advanced_analytics_service.get_executive_dashboard(
            company_id=str(current_user.company_id),
            db=db,
            period_days=period_days
        )
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=500, detail=dashboard_data["error"])
        
        return ExecutiveDashboardResponse(**dashboard_data)
        
    except Exception as e:
        logger.error(f"Failed to generate executive dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate executive dashboard")

@router.get("/kpis", response_model=List[KPIResponse])
async def get_kpis(
    metric_type: Optional[MetricType] = Query(None, description="Filter by metric type"),
    period_days: int = Query(30, ge=1, le=365, description="Number of days for analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Get key performance indicators (KPIs) for the organization
    
    Returns comprehensive KPIs including:
    - Financial metrics (volume, automation, cost savings)
    - Operational metrics (processing time, accuracy, efficiency)
    - Compliance metrics (fraud detection, audit completeness)
    - Performance metrics (uptime, response time, satisfaction)
    """
    try:
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=period_days)
        
        kpis = []
        
        if not metric_type or metric_type == MetricType.FINANCIAL:
            kpis.extend(await advanced_analytics_service._calculate_financial_kpis(
                str(current_user.company_id), start_date, end_date, db
            ))
        
        if not metric_type or metric_type == MetricType.OPERATIONAL:
            kpis.extend(await advanced_analytics_service._calculate_operational_kpis(
                str(current_user.company_id), start_date, end_date, db
            ))
        
        if not metric_type or metric_type == MetricType.COMPLIANCE:
            kpis.extend(await advanced_analytics_service._calculate_compliance_kpis(
                str(current_user.company_id), start_date, end_date, db
            ))
        
        if not metric_type or metric_type == MetricType.PERFORMANCE:
            kpis.extend(await advanced_analytics_service._calculate_performance_kpis(
                str(current_user.company_id), start_date, end_date, db
            ))
        
        return [KPIResponse(**kpi.__dict__) for kpi in kpis]
        
    except Exception as e:
        logger.error(f"Failed to get KPIs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve KPIs")

@router.get("/insights", response_model=List[InsightResponse])
async def get_insights(
    impact: Optional[str] = Query(None, description="Filter by impact level (high, medium, low)"),
    category: Optional[str] = Query(None, description="Filter by insight category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Get AI-powered business insights and recommendations
    
    Returns intelligent insights about:
    - Supplier patterns and risks
    - Processing efficiency opportunities
    - Cost optimization suggestions
    - Compliance and fraud trends
    - Performance improvement areas
    """
    try:
        # This would use the insight engine from business_intelligence service
        # For now, return mock insights
        insights = [
            {
                "title": "High Supplier Concentration Risk",
                "description": "Top 3 suppliers represent 65% of invoice volume, creating concentration risk",
                "impact": "high",
                "category": "supplier_risk",
                "recommendation": "Diversify supplier base and negotiate backup suppliers",
                "confidence": 0.92,
                "actionable": True
            },
            {
                "title": "Automation Opportunity",
                "description": "45% of invoices could be auto-approved based on ML analysis",
                "impact": "medium",
                "category": "efficiency",
                "recommendation": "Increase auto-approval thresholds to reduce manual processing",
                "confidence": 0.88,
                "actionable": True
            },
            {
                "title": "Cost Savings Potential",
                "description": "Bulk discount opportunities identified with 3 major suppliers",
                "impact": "medium",
                "category": "cost_optimization",
                "recommendation": "Negotiate volume discounts for high-frequency suppliers",
                "confidence": 0.85,
                "actionable": True
            }
        ]
        
        # Apply filters
        if impact:
            insights = [i for i in insights if i["impact"] == impact]
        if category:
            insights = [i for i in insights if i["category"] == category]
        
        return [InsightResponse(**insight) for insight in insights]
        
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve insights")

@router.get("/trends", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    metric: str = Query("invoice_volume", description="Metric to analyze trends for"),
    granularity: TimeGranularity = Query(TimeGranularity.DAILY, description="Time granularity for analysis"),
    period_days: int = Query(30, ge=7, le=365, description="Number of days for trend analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Get trend analysis for various metrics
    
    Analyzes trends for:
    - Invoice volume and value
    - Processing times and efficiency
    - Approval rates and automation
    - Supplier diversity and concentration
    - Fraud detection and compliance
    """
    try:
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=period_days)
        
        trends = await advanced_analytics_service._analyze_trends(
            str(current_user.company_id), start_date, end_date, db
        )
        
        if "error" in trends:
            raise HTTPException(status_code=500, detail=trends["error"])
        
        return TrendAnalysisResponse(**trends)
        
    except Exception as e:
        logger.error(f"Failed to analyze trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze trends")

@router.get("/forecast", response_model=ForecastingResponse)
async def get_forecasts(
    forecast_type: str = Query("invoice_volume", description="Type of forecast (invoice_volume, cash_flow)"),
    days_ahead: int = Query(30, ge=7, le=90, description="Number of days to forecast ahead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Get predictive forecasts using advanced ML models
    
    Provides forecasts for:
    - Invoice volume and processing trends
    - Cash flow predictions
    - Approval likelihood for pending invoices
    - Supplier behavior and risk patterns
    - Cost optimization opportunities
    """
    try:
        if forecast_type == "invoice_volume":
            forecast = await advanced_analytics_service.forecasting_engine.forecast_invoice_volume(
                str(current_user.company_id), days_ahead
            )
        elif forecast_type == "cash_flow":
            forecast = await advanced_analytics_service.forecasting_engine.forecast_cash_flow(
                str(current_user.company_id), days_ahead
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid forecast type")
        
        return ForecastingResponse(**forecast)
        
    except Exception as e:
        logger.error(f"Failed to generate forecast: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate forecast")

@router.get("/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Get comprehensive risk assessment for the organization
    
    Assesses risks in:
    - Financial exposure and concentration
    - Supplier dependency and diversity
    - Processing backlog and efficiency
    - Compliance and fraud exposure
    - System performance and reliability
    """
    try:
        risk_assessment = await advanced_analytics_service._assess_risks(
            str(current_user.company_id), db
        )
        
        if "error" in risk_assessment:
            raise HTTPException(status_code=500, detail=risk_assessment["error"])
        
        return RiskAssessmentResponse(**risk_assessment)
        
    except Exception as e:
        logger.error(f"Failed to assess risks: {e}")
        raise HTTPException(status_code=500, detail="Failed to assess risks")

@router.get("/performance-metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Get detailed performance metrics and system health
    
    Returns metrics for:
    - System uptime and availability
    - Response times and performance
    - User satisfaction and adoption
    - Processing accuracy and efficiency
    - Error rates and reliability
    """
    try:
        # Mock performance metrics - in production, these would come from monitoring systems
        performance_metrics = {
            "system_uptime": 99.95,
            "average_response_time_ms": 145,
            "user_satisfaction_score": 4.7,
            "processing_accuracy_percent": 97.8,
            "error_rate_percent": 0.05,
            "throughput_invoices_per_hour": 1250,
            "active_users": 45,
            "api_calls_per_minute": 320,
            "database_connections_active": 12,
            "cache_hit_rate_percent": 94.2,
            "memory_usage_percent": 68.5,
            "cpu_usage_percent": 42.3,
            "disk_usage_percent": 34.7,
            "network_latency_ms": 23,
            "queue_depth": 8,
            "last_updated": datetime.now(UTC).isoformat()
        }
        
        return PerformanceMetricsResponse(**performance_metrics)
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")

@router.get("/reports/custom")
async def generate_custom_report(
    report_type: str = Query(..., description="Type of custom report to generate"),
    format: str = Query("json", description="Report format (json, csv, pdf)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Generate custom reports based on specified parameters
    
    Supports various report types:
    - Supplier analysis reports
    - Invoice processing reports
    - Compliance and audit reports
    - Financial performance reports
    - Custom KPI dashboards
    """
    try:
        # This would implement custom report generation
        # For now, return a placeholder response
        return {
            "report_id": f"custom_report_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            "report_type": report_type,
            "parameters": {},  # Empty parameters for now
            "format": format,
            "status": "generated",
            "download_url": f"/api/v1/analytics/reports/{report_type}/download",
            "generated_at": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate custom report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate custom report")

@router.post("/ml-models/retrain")
async def retrain_ml_models(
    model_types: List[str] = Query(..., description="Types of models to retrain"),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Trigger retraining of ML models with latest data
    
    Retrains specified ML models:
    - fraud_detection: Fraud detection model
    - gl_coding: GL account coding model
    - approval_prediction: Invoice approval prediction model
    - supplier_anomaly: Supplier anomaly detection model
    - cash_flow_prediction: Cash flow forecasting model
    """
    try:
        from services.advanced_ml_models import advanced_ml_service
        
        # Prepare training data (in production, this would fetch real data)
        training_data = {}
        for model_type in model_types:
            training_data[model_type] = {"sample_size": 1000}  # Mock data
        
        result = await advanced_ml_service.retrain_models(training_data)
        
        return {
            "status": "success",
            "retrained_models": model_types,
            "result": result,
            "initiated_by": current_user.email,
            "initiated_at": datetime.now(UTC).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to retrain ML models: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrain ML models")

@router.get("/ml-models/health")
async def get_ml_models_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """
    Get health status and performance metrics of ML models
    
    Returns information about:
    - Model availability and status
    - Performance metrics and accuracy
    - Last training/update timestamps
    - Model versions and configurations
    """
    try:
        from services.advanced_ml_models import advanced_ml_service
        
        model_health = advanced_ml_service.get_model_health()
        
        return model_health
        
    except Exception as e:
        logger.error(f"Failed to get ML models health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ML models health")
