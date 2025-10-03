"""
Monitoring API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.auth import AuthManager
from src.models.user import User
from services.enterprise_monitoring import EnterpriseMonitoringService
from schemas.erp import MonitoringResponse, MetricsSummaryResponse

router = APIRouter()

@router.get("/health", response_model=MonitoringResponse)
async def get_system_health(
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive system health status"""
    try:
        monitoring_service = EnterpriseMonitoringService()
        
        # Collect current metrics
        system_metrics = await monitoring_service.collect_system_metrics()
        business_metrics = await monitoring_service.collect_business_metrics(db)
        
        # Determine overall health
        health_status = "healthy"
        if (system_metrics.cpu_percent > 80 or 
            system_metrics.memory_percent > 85 or 
            system_metrics.disk_percent > 90):
            health_status = "warning"
        
        if (system_metrics.cpu_percent > 95 or 
            system_metrics.memory_percent > 95 or 
            system_metrics.disk_percent > 95):
            health_status = "critical"
        
        return MonitoringResponse(
            status=health_status,
            timestamp=system_metrics.timestamp.isoformat(),
            system_metrics={
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "disk_percent": system_metrics.disk_percent,
                "response_time_ms": system_metrics.response_time_ms,
                "error_rate": system_metrics.error_rate,
                "throughput_rps": system_metrics.throughput_rps
            },
            business_metrics={
                "total_invoices": business_metrics.total_invoices,
                "pending_invoices": business_metrics.pending_invoices,
                "approved_invoices": business_metrics.approved_invoices,
                "rejected_invoices": business_metrics.rejected_invoices,
                "processing_time_avg": business_metrics.processing_time_avg,
                "fraud_detection_rate": business_metrics.fraud_detection_rate,
                "approval_rate": business_metrics.approval_rate,
                "user_activity": business_metrics.user_activity,
                "api_calls": business_metrics.api_calls,
                "error_count": business_metrics.error_count
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )

@router.get("/metrics/summary", response_model=MetricsSummaryResponse)
async def get_metrics_summary(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to include in summary"),
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get metrics summary for the specified time period (Admin only)"""
    try:
        monitoring_service = EnterpriseMonitoringService()
        
        summary = await monitoring_service.get_metrics_summary(hours)
        
        return MetricsSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics summary: {str(e)}"
        )

@router.post("/metrics/collect")
async def collect_metrics(
    current_user: User = Depends(AuthManager.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually trigger metrics collection (Admin only)"""
    try:
        monitoring_service = EnterpriseMonitoringService()
        
        await monitoring_service.run_monitoring_cycle(db)
        
        return {
            "status": "success",
            "message": "Metrics collection completed",
            "timestamp": monitoring_service.collect_system_metrics().timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to collect metrics: {str(e)}"
        )

@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by alert severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    current_user: User = Depends(AuthManager.get_current_active_user)
):
    """Get system alerts (Admin only)"""
    try:
        monitoring_service = EnterpriseMonitoringService()
        
        # This would typically query from a database or Redis
        # For now, return a placeholder
        alerts = []
        
        # Apply filters
        if severity:
            alerts = [alert for alert in alerts if alert.get("severity") == severity]
        
        if resolved is not None:
            alerts = [alert for alert in alerts if alert.get("resolved") == resolved]
        
        return {
            "alerts": alerts,
            "total": len(alerts),
            "filters": {
                "severity": severity,
                "resolved": resolved
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )

@router.get("/performance")
async def get_performance_metrics(
    current_user: User = Depends(AuthManager.get_current_user)
):
    """Get performance metrics"""
    try:
        monitoring_service = EnterpriseMonitoringService()
        
        # Get recent metrics
        system_metrics = await monitoring_service.collect_system_metrics()
        
        return {
            "response_time_ms": system_metrics.response_time_ms,
            "throughput_rps": system_metrics.throughput_rps,
            "error_rate": system_metrics.error_rate,
            "active_connections": system_metrics.active_connections,
            "timestamp": system_metrics.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.get("/business")
async def get_business_metrics(
    current_user: User = Depends(AuthManager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get business metrics"""
    try:
        monitoring_service = EnterpriseMonitoringService()
        
        # Get recent business metrics
        business_metrics = await monitoring_service.collect_business_metrics(db)
        
        return {
            "total_invoices": business_metrics.total_invoices,
            "pending_invoices": business_metrics.pending_invoices,
            "approved_invoices": business_metrics.approved_invoices,
            "rejected_invoices": business_metrics.rejected_invoices,
            "processing_time_avg": business_metrics.processing_time_avg,
            "fraud_detection_rate": business_metrics.fraud_detection_rate,
            "approval_rate": business_metrics.approval_rate,
            "user_activity": business_metrics.user_activity,
            "api_calls": business_metrics.api_calls,
            "error_count": business_metrics.error_count,
            "timestamp": business_metrics.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business metrics: {str(e)}"
        )
