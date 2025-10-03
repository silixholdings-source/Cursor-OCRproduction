"""
Enterprise Monitoring and Alerting System
Comprehensive monitoring for production-grade AI ERP SaaS platform
"""
import logging
import asyncio
import time
import psutil
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import redis
import httpx

from core.config import settings
from core.database import get_db
from src.models.invoice import Invoice, InvoiceStatus
from src.models.user import User
from src.models.audit import AuditLog, AuditAction

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    """Types of alerts"""
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE = "performance"
    BUSINESS_METRICS = "business_metrics"
    SECURITY = "security"
    INTEGRATION = "integration"
    USER_ACTIVITY = "user_activity"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    active_connections: int
    response_time_ms: float
    error_rate: float
    throughput_rps: float

@dataclass
class BusinessMetrics:
    """Business-specific metrics"""
    timestamp: datetime
    total_invoices: int
    pending_invoices: int
    approved_invoices: int
    rejected_invoices: int
    processing_time_avg: float
    fraud_detection_rate: float
    approval_rate: float
    user_activity: int
    api_calls: int
    error_count: int

class EnterpriseMonitoringService:
    """Enterprise-grade monitoring and alerting service"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.alert_channels = self._setup_alert_channels()
        self.metrics_history = []
        self.alert_history = []
        
        # Thresholds for alerting
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time_ms": 5000.0,
            "error_rate": 0.05,  # 5%
            "processing_time_avg": 300.0,  # 5 minutes
            "fraud_detection_rate": 0.1,  # 10%
            "approval_rate": 0.8,  # 80%
            "active_users": 1000
        }
    
    def _setup_alert_channels(self) -> Dict[str, Any]:
        """Setup alert notification channels"""
        return {
            "email": {
                "enabled": getattr(settings, 'EMAIL_ALERTS_ENABLED', False),
                "recipients": getattr(settings, 'ALERT_EMAIL_RECIPIENTS', [])
            },
            "slack": {
                "enabled": getattr(settings, 'SLACK_ALERTS_ENABLED', False),
                "webhook_url": getattr(settings, 'SLACK_WEBHOOK_URL', '')
            },
            "webhook": {
                "enabled": getattr(settings, 'WEBHOOK_ALERTS_ENABLED', False),
                "url": getattr(settings, 'ALERT_WEBHOOK_URL', '')
            }
        }
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network_io = psutil.net_io_counters()._asdict()
            
            # Active connections (approximate)
            active_connections = len(psutil.net_connections())
            
            # Application-specific metrics
            response_time = await self._measure_response_time()
            error_rate = await self._calculate_error_rate()
            throughput = await self._calculate_throughput()
            
            return SystemMetrics(
                timestamp=datetime.now(UTC),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_io=network_io,
                active_connections=active_connections,
                response_time_ms=response_time,
                error_rate=error_rate,
                throughput_rps=throughput
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            raise
    
    async def collect_business_metrics(self, db: Session) -> BusinessMetrics:
        """Collect business-specific metrics"""
        try:
            # Time range for metrics (last 24 hours)
            end_time = datetime.now(UTC)
            start_time = end_time - timedelta(hours=24)
            
            # Invoice metrics
            total_invoices = db.query(Invoice).filter(
                Invoice.created_at >= start_time
            ).count()
            
            pending_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.created_at >= start_time,
                    Invoice.status == InvoiceStatus.PENDING
                )
            ).count()
            
            approved_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.created_at >= start_time,
                    Invoice.status == InvoiceStatus.APPROVED
                )
            ).count()
            
            rejected_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.created_at >= start_time,
                    Invoice.status == InvoiceStatus.REJECTED
                )
            ).count()
            
            # Processing time (average)
            processing_times = db.query(Invoice).filter(
                and_(
                    Invoice.created_at >= start_time,
                    Invoice.approved_at.isnot(None)
                )
            ).all()
            
            if processing_times:
                avg_processing_time = sum([
                    (inv.approved_at - inv.created_at).total_seconds() / 60
                    for inv in processing_times
                ]) / len(processing_times)
            else:
                avg_processing_time = 0.0
            
            # Fraud detection rate
            fraud_logs = db.query(AuditLog).filter(
                and_(
                    AuditLog.created_at >= start_time,
                    AuditLog.action == AuditAction.FRAUD_ANALYSIS
                )
            ).count()
            
            fraud_detection_rate = fraud_logs / total_invoices if total_invoices > 0 else 0.0
            
            # Approval rate
            approval_rate = approved_invoices / total_invoices if total_invoices > 0 else 0.0
            
            # User activity
            user_activity = db.query(User).filter(
                User.last_login >= start_time
            ).count()
            
            # API calls (from audit logs)
            api_calls = db.query(AuditLog).filter(
                and_(
                    AuditLog.created_at >= start_time,
                    AuditLog.action.in_([
                        AuditAction.CREATE, AuditAction.READ, 
                        AuditAction.UPDATE, AuditAction.DELETE
                    ])
                )
            ).count()
            
            # Error count
            error_count = db.query(AuditLog).filter(
                and_(
                    AuditLog.created_at >= start_time,
                    AuditLog.action == AuditAction.ERROR
                )
            ).count()
            
            return BusinessMetrics(
                timestamp=datetime.now(UTC),
                total_invoices=total_invoices,
                pending_invoices=pending_invoices,
                approved_invoices=approved_invoices,
                rejected_invoices=rejected_invoices,
                processing_time_avg=avg_processing_time,
                fraud_detection_rate=fraud_detection_rate,
                approval_rate=approval_rate,
                user_activity=user_activity,
                api_calls=api_calls,
                error_count=error_count
            )
            
        except Exception as e:
            logger.error(f"Failed to collect business metrics: {e}")
            raise
    
    async def _measure_response_time(self) -> float:
        """Measure average API response time"""
        try:
            # This would typically ping your health endpoint
            start_time = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{getattr(settings, 'API_BASE_URL', 'http://localhost:8000')}/health")
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to milliseconds
        except:
            return 0.0
    
    async def _calculate_error_rate(self) -> float:
        """Calculate error rate from recent requests"""
        try:
            # This would typically query your logs or metrics store
            # For now, return a placeholder
            return 0.0
        except:
            return 0.0
    
    async def _calculate_throughput(self) -> float:
        """Calculate requests per second"""
        try:
            # This would typically query your metrics store
            # For now, return a placeholder
            return 0.0
        except:
            return 0.0
    
    async def run_monitoring_cycle(self, db: Session) -> None:
        """Run a complete monitoring cycle"""
        try:
            logger.info("Starting monitoring cycle")
            
            # Collect metrics
            system_metrics = await self.collect_system_metrics()
            business_metrics = await self.collect_business_metrics(db)
            
            # Store metrics
            await self._store_metrics(system_metrics, business_metrics)
            
            logger.info("Monitoring cycle completed")
            
        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}")
            raise
    
    async def _store_metrics(self, system_metrics: SystemMetrics, business_metrics: BusinessMetrics) -> None:
        """Store metrics in Redis"""
        try:
            timestamp = datetime.now(UTC).isoformat()
            
            # Store system metrics
            system_key = f"metrics:system:{timestamp}"
            self.redis_client.setex(
                system_key,
                86400 * 30,  # 30 days TTL
                json.dumps(asdict(system_metrics))
            )
            
            # Store business metrics
            business_key = f"metrics:business:{timestamp}"
            self.redis_client.setex(
                business_key,
                86400 * 30,  # 30 days TTL
                json.dumps(asdict(business_metrics))
            )
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        try:
            end_time = datetime.now(UTC)
            start_time = end_time - timedelta(hours=hours)
            
            # Get system metrics
            system_keys = self.redis_client.keys("metrics:system:*")
            system_metrics = []
            
            for key in system_keys:
                data = self.redis_client.get(key)
                if data:
                    metric = json.loads(data)
                    metric_time = datetime.fromisoformat(metric["timestamp"])
                    if start_time <= metric_time <= end_time:
                        system_metrics.append(metric)
            
            # Get business metrics
            business_keys = self.redis_client.keys("metrics:business:*")
            business_metrics = []
            
            for key in business_keys:
                data = self.redis_client.get(key)
                if data:
                    metric = json.loads(data)
                    metric_time = datetime.fromisoformat(metric["timestamp"])
                    if start_time <= metric_time <= end_time:
                        business_metrics.append(metric)
            
            # Calculate averages
            if system_metrics:
                avg_cpu = sum(m["cpu_percent"] for m in system_metrics) / len(system_metrics)
                avg_memory = sum(m["memory_percent"] for m in system_metrics) / len(system_metrics)
                avg_response_time = sum(m["response_time_ms"] for m in system_metrics) / len(system_metrics)
            else:
                avg_cpu = avg_memory = avg_response_time = 0.0
            
            if business_metrics:
                total_invoices = sum(m["total_invoices"] for m in business_metrics)
                avg_processing_time = sum(m["processing_time_avg"] for m in business_metrics) / len(business_metrics)
                avg_approval_rate = sum(m["approval_rate"] for m in business_metrics) / len(business_metrics)
            else:
                total_invoices = 0
                avg_processing_time = avg_approval_rate = 0.0
            
            return {
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours": hours
                },
                "system_metrics": {
                    "avg_cpu_percent": avg_cpu,
                    "avg_memory_percent": avg_memory,
                    "avg_response_time_ms": avg_response_time,
                    "data_points": len(system_metrics)
                },
                "business_metrics": {
                    "total_invoices": total_invoices,
                    "avg_processing_time_minutes": avg_processing_time,
                    "avg_approval_rate": avg_approval_rate,
                    "data_points": len(business_metrics)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}