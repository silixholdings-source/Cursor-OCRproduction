from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class TimeRange(str, Enum):
    """Time range options for analytics"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"

class MetricType(str, Enum):
    """Metric types for analytics"""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    PERCENTAGE = "percentage"
    RATIO = "ratio"

class KPIResponse(BaseModel):
    """KPI response schema"""
    name: str = Field(..., description="KPI name")
    value: float = Field(..., description="KPI value")
    unit: str = Field(..., description="KPI unit")
    trend: str = Field(..., description="Trend direction")
    change_percentage: float = Field(..., description="Change percentage")
    period: str = Field(..., description="Time period")

class AnalyticsRequest(BaseModel):
    """Analytics request schema"""
    time_range: TimeRange = Field(..., description="Time range for analytics")
    company_id: str = Field(..., description="Company ID")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to include")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

class AnalyticsResponse(BaseModel):
    """Analytics response schema"""
    company_id: str = Field(..., description="Company ID")
    time_range: TimeRange = Field(..., description="Time range")
    generated_at: datetime = Field(..., description="Generation timestamp")
    kpis: List[KPIResponse] = Field(..., description="Key performance indicators")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")

class InvoiceAnalyticsRequest(BaseModel):
    """Invoice analytics request schema"""
    time_range: TimeRange = Field(..., description="Time range")
    company_id: str = Field(..., description="Company ID")
    include_breakdown: bool = Field(default=True, description="Include detailed breakdown")

class InvoiceAnalyticsResponse(BaseModel):
    """Invoice analytics response schema"""
    total_invoices: int = Field(..., description="Total number of invoices")
    total_amount: float = Field(..., description="Total invoice amount")
    average_amount: float = Field(..., description="Average invoice amount")
    processing_time_avg: float = Field(..., description="Average processing time")
    approval_rate: float = Field(..., description="Approval rate percentage")
    supplier_count: int = Field(..., description="Number of unique suppliers")
    breakdown: Optional[Dict[str, Any]] = Field(None, description="Detailed breakdown")

class ProcessingAnalyticsRequest(BaseModel):
    """Processing analytics request schema"""
    time_range: TimeRange = Field(..., description="Time range")
    company_id: str = Field(..., description="Company ID")

class ProcessingAnalyticsResponse(BaseModel):
    """Processing analytics response schema"""
    total_processed: int = Field(..., description="Total invoices processed")
    success_rate: float = Field(..., description="Processing success rate")
    average_processing_time: float = Field(..., description="Average processing time")
    ocr_accuracy: float = Field(..., description="OCR accuracy rate")
    fraud_detection_rate: float = Field(..., description="Fraud detection rate")
    duplicate_detection_rate: float = Field(..., description="Duplicate detection rate")

class TrendAnalysisRequest(BaseModel):
    """Trend analysis request schema"""
    metric: str = Field(..., description="Metric to analyze")
    time_range: TimeRange = Field(..., description="Time range")
    company_id: str = Field(..., description="Company ID")
    granularity: str = Field(default="daily", description="Time granularity")

class TrendDataPoint(BaseModel):
    """Trend data point schema"""
    timestamp: datetime = Field(..., description="Data point timestamp")
    value: float = Field(..., description="Data point value")
    label: Optional[str] = Field(None, description="Data point label")

class TrendAnalysisResponse(BaseModel):
    """Trend analysis response schema"""
    metric: str = Field(..., description="Analyzed metric")
    time_range: TimeRange = Field(..., description="Time range")
    data_points: List[TrendDataPoint] = Field(..., description="Trend data points")
    trend_direction: str = Field(..., description="Overall trend direction")
    trend_strength: float = Field(..., description="Trend strength")
    confidence: float = Field(..., description="Trend confidence")

class InsightType(str, Enum):
    """Insight types"""
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    COST_SAVINGS = "cost_savings"
    RISK = "risk"
    OPPORTUNITY = "opportunity"

class InsightResponse(BaseModel):
    """Insight response schema"""
    type: InsightType = Field(..., description="Insight type")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    impact: str = Field(..., description="Impact level")
    confidence: float = Field(..., description="Confidence score")
    actionable: bool = Field(..., description="Is actionable")
    recommendations: List[str] = Field(default=[], description="Recommendations")

class RiskLevel(str, Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAssessmentResponse(BaseModel):
    """Risk assessment response schema"""
    overall_risk: RiskLevel = Field(..., description="Overall risk level")
    risk_score: float = Field(..., description="Risk score")
    risk_factors: List[Dict[str, Any]] = Field(..., description="Risk factors")
    mitigation_strategies: List[str] = Field(..., description="Mitigation strategies")
    assessed_at: datetime = Field(..., description="Assessment timestamp")

class PredictionInsight(BaseModel):
    """Prediction insight schema"""
    metric: str = Field(..., description="Predicted metric")
    current_value: float = Field(..., description="Current value")
    predicted_value: float = Field(..., description="Predicted value")
    confidence: float = Field(..., description="Prediction confidence")
    time_horizon: str = Field(..., description="Prediction time horizon")
    factors: List[str] = Field(..., description="Key influencing factors")

class CashFlowPrediction(BaseModel):
    """Cash flow prediction schema"""
    current_cash_flow: float = Field(..., description="Current cash flow")
    predicted_cash_flow: float = Field(..., description="Predicted cash flow")
    confidence: float = Field(..., description="Prediction confidence")
    time_period: str = Field(..., description="Prediction time period")
    key_drivers: List[str] = Field(..., description="Key drivers")

class PredictiveInsights(BaseModel):
    """Predictive insights schema"""
    cash_flow: CashFlowPrediction = Field(..., description="Cash flow prediction")
    approval_predictions: List[PredictionInsight] = Field(..., description="Approval predictions")
    generated_at: datetime = Field(..., description="Generation timestamp")

class ExecutiveSummary(BaseModel):
    """Executive summary schema"""
    performance_score: float = Field(..., ge=0.0, le=100.0, description="Performance score")
    key_metrics: List[KPIResponse] = Field(..., description="Key metrics")
    critical_insights: List[InsightResponse] = Field(..., description="Critical insights")
    risk_level: RiskLevel = Field(..., description="Risk level")
    recommendations: List[str] = Field(..., description="Recommendations")
    generated_at: datetime = Field(..., description="Generation timestamp")

class ExecutiveDashboardResponse(BaseModel):
    """Executive dashboard response schema"""
    dashboard_id: str = Field(..., description="Dashboard ID")
    generated_at: datetime = Field(..., description="Generation timestamp")
    period: Dict[str, str] = Field(..., description="Time period")
    kpis: List[KPIResponse] = Field(..., description="KPIs")
    predictions: PredictiveInsights = Field(..., description="Predictions")
    ai_insights: List[InsightResponse] = Field(..., description="AI insights")
    trends: TrendAnalysisResponse = Field(..., description="Trend analysis")
    risk_assessment: RiskAssessmentResponse = Field(..., description="Risk assessment")
    summary: ExecutiveSummary = Field(..., description="Executive summary")

class CustomReportRequest(BaseModel):
    """Custom report request schema"""
    report_type: str = Field(..., description="Report type")
    parameters: Dict[str, Any] = Field(..., description="Report parameters")
    format: str = Field(default="json", description="Report format")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

class CustomReportResponse(BaseModel):
    """Custom report response schema"""
    report_id: str = Field(..., description="Report ID")
    report_type: str = Field(..., description="Report type")
    parameters: Dict[str, Any] = Field(..., description="Report parameters")
    format: str = Field(..., description="Report format")
    status: str = Field(..., description="Report status")
    download_url: Optional[str] = Field(None, description="Download URL")
    generated_at: datetime = Field(..., description="Generation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")

class MLModelHealth(BaseModel):
    """ML model health schema"""
    model_name: str = Field(..., description="Model name")
    status: str = Field(..., description="Model status")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Model accuracy")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    version: Optional[str] = Field(None, description="Model version")

class MLModelsHealthResponse(BaseModel):
    """ML models health response schema"""
    overall_status: str = Field(..., description="Overall status")
    models: Dict[str, MLModelHealth] = Field(..., description="Models health")
    timestamp: datetime = Field(..., description="Check timestamp")

class RetrainModelsRequest(BaseModel):
    """Retrain models request schema"""
    model_types: List[str] = Field(..., description="Model types to retrain")
    force_retrain: bool = Field(default=False, description="Force retraining")
    training_data_source: Optional[str] = Field(None, description="Training data source")

class RetrainModelsResponse(BaseModel):
    """Retrain models response schema"""
    success: bool = Field(..., description="Retraining success")
    message: str = Field(..., description="Response message")
    retrained_models: List[str] = Field(..., description="Retrained models")
    started_at: datetime = Field(..., description="Retraining start timestamp")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion")

class ForecastingResponse(BaseModel):
    """Forecasting response schema"""
    forecast_id: str = Field(..., description="Forecast ID")
    metric: str = Field(..., description="Forecasted metric")
    time_period: str = Field(..., description="Time period")
    predictions: List[Dict[str, Any]] = Field(..., description="Predictions")
    confidence_interval: Dict[str, float] = Field(..., description="Confidence interval")
    generated_at: datetime = Field(..., description="Generation timestamp")

class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response schema"""
    company_id: str = Field(..., description="Company ID")
    time_range: TimeRange = Field(..., description="Time range")
    generated_at: datetime = Field(..., description="Generation timestamp")
    processing_metrics: Dict[str, Any] = Field(..., description="Processing metrics")
    approval_metrics: Dict[str, Any] = Field(..., description="Approval metrics")
    efficiency_metrics: Dict[str, Any] = Field(..., description="Efficiency metrics")
    cost_metrics: Dict[str, Any] = Field(..., description="Cost metrics")
    quality_metrics: Dict[str, Any] = Field(..., description="Quality metrics")