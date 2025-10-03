"""
System Management Schemas
Pydantic models for system administration and monitoring
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class SystemInfoResponse(BaseModel):
    """System information response"""
    platform: str
    platform_version: str
    architecture: str
    processor: str
    python_version: str
    app_version: str
    environment: str
    uptime: int
    timestamp: datetime

class SystemMetricsResponse(BaseModel):
    """System performance metrics response"""
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    network: Dict[str, Any]
    timestamp: datetime

class DatabaseStatsResponse(BaseModel):
    """Database statistics response"""
    table_counts: Dict[str, int]
    database_size_bytes: int
    connection_pool: Dict[str, int]
    timestamp: datetime

class CacheStatsResponse(BaseModel):
    """Cache statistics response"""
    redis_connected: bool
    memory_usage: int
    key_count: int
    hit_rate: float
    miss_rate: float
    timestamp: datetime

class LogLevelRequest(BaseModel):
    """Log level change request"""
    level: str = Field(..., description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")

class SystemConfigResponse(BaseModel):
    """System configuration response"""
    app_name: str
    app_version: str
    environment: str
    debug: bool
    api_v1_str: str
    project_name: str
    database_pool_size: int
    database_max_overflow: int
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    cors_origins: List[str]
    allowed_hosts: List[str]
    timestamp: datetime

class MaintenanceTaskResponse(BaseModel):
    """Maintenance task response"""
    message: str
    tasks: List[str]
    timestamp: datetime

