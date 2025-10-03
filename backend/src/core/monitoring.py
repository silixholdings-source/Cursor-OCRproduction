"""
Advanced Monitoring and Observability System
Provides comprehensive monitoring, metrics, and alerting capabilities
"""
import time
import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, UTC, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import redis.asyncio as redis
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    tags: Dict[str, str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    level: AlertLevel
    message: str
    metric_name: str
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MetricsCollector:
    """Advanced metrics collection system"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.metrics: Dict[str, List[Metric]] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self._setup_default_alert_rules()
    
    def _setup_default_alert_rules(self):
        """Setup default alerting rules"""
        self.alert_rules = [
            {
                "metric": "system.cpu.usage",
                "threshold": 80.0,
                "level": AlertLevel.WARNING,
                "message": "High CPU usage detected"
            },
            {
                "metric": "system.cpu.usage",
                "threshold": 95.0,
                "level": AlertLevel.CRITICAL,
                "message": "Critical CPU usage detected"
            },
            {
                "metric": "system.memory.usage",
                "threshold": 85.0,
                "level": AlertLevel.WARNING,
                "message": "High memory usage detected"
            },
            {
                "metric": "system.memory.usage",
                "threshold": 95.0,
                "level": AlertLevel.CRITICAL,
                "message": "Critical memory usage detected"
            },
            {
                "metric": "system.disk.usage",
                "threshold": 90.0,
                "level": AlertLevel.WARNING,
                "message": "High disk usage detected"
            },
            {
                "metric": "api.response_time",
                "threshold": 5000.0,  # 5 seconds
                "level": AlertLevel.WARNING,
                "message": "Slow API response time detected"
            },
            {
                "metric": "api.error_rate",
                "threshold": 10.0,  # 10%
                "level": AlertLevel.WARNING,
                "message": "High API error rate detected"
            },
            {
                "metric": "database.connection_pool.usage",
                "threshold": 80.0,
                "level": AlertLevel.WARNING,
                "message": "High database connection pool usage"
            }
        ]
    
    def add_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None
    ):
        """Add a metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            tags=tags or {},
            timestamp=datetime.now(UTC)
        )
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(metric)
        
        # Keep only last 1000 metrics per name
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
        
        # Check alert rules
        self._check_alert_rules(metric)
        
        # Store in Redis if available
        if self.redis_client:
            asyncio.create_task(self._store_metric_redis(metric))
    
    def _check_alert_rules(self, metric: Metric):
        """Check if metric triggers any alert rules"""
        for rule in self.alert_rules:
            if rule["metric"] == metric.name:
                if metric.value >= rule["threshold"]:
                    alert = Alert(
                        id=f"{metric.name}_{rule['threshold']}_{int(metric.timestamp.timestamp())}",
                        level=rule["level"],
                        message=rule["message"],
                        metric_name=metric.name,
                        threshold=rule["threshold"],
                        current_value=metric.value,
                        timestamp=datetime.now(UTC)
                    )
                    
                    # Trigger alert callbacks
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            logger.error(f"Error in alert callback: {e}")
    
    async def _store_metric_redis(self, metric: Metric):
        """Store metric in Redis"""
        try:
            key = f"metrics:{metric.name}"
            value = json.dumps(metric.to_dict(), default=str)
            await self.redis_client.lpush(key, value)
            await self.redis_client.ltrim(key, 0, 999)  # Keep last 1000 metrics
            await self.redis_client.expire(key, 86400)  # Expire after 24 hours
        except Exception as e:
            logger.error(f"Failed to store metric in Redis: {e}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def get_metrics(
        self,
        name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Metric]:
        """Get metrics with optional filtering"""
        if name:
            metrics = self.metrics.get(name, [])
        else:
            metrics = []
            for metric_list in self.metrics.values():
                metrics.extend(metric_list)
        
        # Filter by time range
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        
        # Sort by timestamp and limit
        metrics.sort(key=lambda x: x.timestamp, reverse=True)
        return metrics[:limit]
    
    def get_metric_summary(self, name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """Get metric summary for a time window"""
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(minutes=window_minutes)
        
        metrics = self.get_metrics(name, start_time, end_time)
        
        if not metrics:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "sum": 0}
        
        values = [m.value for m in metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
            "window_minutes": window_minutes
        }

class SystemMonitor:
    """System monitoring and metrics collection"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.monitoring_task = None
        self.is_monitoring = False
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start system monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )
        logger.info("System monitoring started")
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("System monitoring stopped")
    
    async def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def _collect_system_metrics(self):
        """Collect system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_collector.add_metric(
                "system.cpu.usage",
                cpu_percent,
                MetricType.GAUGE,
                {"host": "server"}
            )
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.metrics_collector.add_metric(
                "system.memory.usage",
                memory.percent,
                MetricType.GAUGE,
                {"host": "server"}
            )
            
            self.metrics_collector.add_metric(
                "system.memory.available",
                memory.available,
                MetricType.GAUGE,
                {"host": "server"}
            )
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics_collector.add_metric(
                "system.disk.usage",
                disk_percent,
                MetricType.GAUGE,
                {"host": "server", "mount": "/"}
            )
            
            self.metrics_collector.add_metric(
                "system.disk.free",
                disk.free,
                MetricType.GAUGE,
                {"host": "server", "mount": "/"}
            )
            
            # Network metrics
            network = psutil.net_io_counters()
            self.metrics_collector.add_metric(
                "system.network.bytes_sent",
                network.bytes_sent,
                MetricType.COUNTER,
                {"host": "server"}
            )
            
            self.metrics_collector.add_metric(
                "system.network.bytes_recv",
                network.bytes_recv,
                MetricType.COUNTER,
                {"host": "server"}
            )
            
            # Process metrics
            process = psutil.Process()
            self.metrics_collector.add_metric(
                "system.process.cpu_percent",
                process.cpu_percent(),
                MetricType.GAUGE,
                {"host": "server", "process": "app"}
            )
            
            self.metrics_collector.add_metric(
                "system.process.memory_mb",
                process.memory_info().rss / 1024 / 1024,
                MetricType.GAUGE,
                {"host": "server", "process": "app"}
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

class APIMonitor:
    """API monitoring and performance tracking"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.request_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}
        self.response_times: Dict[str, List[float]] = {}
    
    def track_request(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time_ms: float
    ):
        """Track API request metrics"""
        endpoint = f"{method} {path}"
        
        # Track request count
        self.request_counts[endpoint] = self.request_counts.get(endpoint, 0) + 1
        self.metrics_collector.add_metric(
            "api.requests.total",
            1,
            MetricType.COUNTER,
            {"method": method, "path": path, "status": str(status_code)}
        )
        
        # Track response time
        if endpoint not in self.response_times:
            self.response_times[endpoint] = []
        
        self.response_times[endpoint].append(response_time_ms)
        self.metrics_collector.add_metric(
            "api.response_time",
            response_time_ms,
            MetricType.HISTOGRAM,
            {"method": method, "path": path}
        )
        
        # Track errors
        if status_code >= 400:
            self.error_counts[endpoint] = self.error_counts.get(endpoint, 0) + 1
            self.metrics_collector.add_metric(
                "api.errors.total",
                1,
                MetricType.COUNTER,
                {"method": method, "path": path, "status": str(status_code)}
            )
        
        # Calculate and track error rate
        total_requests = self.request_counts.get(endpoint, 0)
        total_errors = self.error_counts.get(endpoint, 0)
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            self.metrics_collector.add_metric(
                "api.error_rate",
                error_rate,
                MetricType.GAUGE,
                {"method": method, "path": path}
            )

class DatabaseMonitor:
    """Database monitoring and connection tracking"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
    
    def track_connection_pool(self, pool_stats: Dict[str, Any]):
        """Track database connection pool metrics"""
        pool_usage = (pool_stats["checked_out"] / pool_stats["size"]) * 100
        
        self.metrics_collector.add_metric(
            "database.connection_pool.usage",
            pool_usage,
            MetricType.GAUGE,
            {"pool": "main"}
        )
        
        self.metrics_collector.add_metric(
            "database.connection_pool.size",
            pool_stats["size"],
            MetricType.GAUGE,
            {"pool": "main"}
        )
        
        self.metrics_collector.add_metric(
            "database.connection_pool.checked_out",
            pool_stats["checked_out"],
            MetricType.GAUGE,
            {"pool": "main"}
        )
    
    def track_query_performance(self, query: str, execution_time_ms: float):
        """Track database query performance"""
        self.metrics_collector.add_metric(
            "database.query_time",
            execution_time_ms,
            MetricType.HISTOGRAM,
            {"query_type": self._get_query_type(query)}
        )
    
    def _get_query_type(self, query: str) -> str:
        """Determine query type from SQL"""
        query_upper = query.upper().strip()
        if query_upper.startswith("SELECT"):
            return "SELECT"
        elif query_upper.startswith("INSERT"):
            return "INSERT"
        elif query_upper.startswith("UPDATE"):
            return "UPDATE"
        elif query_upper.startswith("DELETE"):
            return "DELETE"
        else:
            return "OTHER"

# Global monitoring instances
metrics_collector = MetricsCollector()
system_monitor = SystemMonitor(metrics_collector)
api_monitor = APIMonitor(metrics_collector)
database_monitor = DatabaseMonitor(metrics_collector)

def setup_monitoring(redis_client: Optional[redis.Redis] = None):
    """Setup global monitoring system"""
    global metrics_collector, system_monitor, api_monitor, database_monitor
    
    metrics_collector = MetricsCollector(redis_client)
    system_monitor = SystemMonitor(metrics_collector)
    api_monitor = APIMonitor(metrics_collector)
    database_monitor = DatabaseMonitor(metrics_collector)

@asynccontextmanager
async def track_api_request(method: str, path: str):
    """Context manager for tracking API requests"""
    start_time = time.time()
    status_code = 200
    
    try:
        yield
    except Exception as e:
        status_code = 500
        raise
    finally:
        response_time_ms = (time.time() - start_time) * 1000
        api_monitor.track_request(method, path, status_code, response_time_ms)