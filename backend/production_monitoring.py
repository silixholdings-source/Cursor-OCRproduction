#!/usr/bin/env python3
"""
Production Monitoring and Logging for AI ERP SaaS
Integrates Sentry, structured logging, and performance monitoring
"""

import os
import sys
import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import psutil

# Configure structured logging
class ProductionLogger:
    """Production-grade logging configuration"""
    
    def __init__(self):
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        self.environment = os.getenv("ENVIRONMENT", "production")
        
    def setup_logging(self):
        """Configure structured logging for production"""
        
        # Create custom formatter for structured logs
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                # Add exception info if present
                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)
                
                # Add custom fields
                if hasattr(record, 'user_id'):
                    log_entry["user_id"] = record.user_id
                if hasattr(record, 'company_id'):
                    log_entry["company_id"] = record.company_id
                if hasattr(record, 'request_id'):
                    log_entry["request_id"] = record.request_id
                
                return json.dumps(log_entry)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level))
        
        # Remove default handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add structured console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(console_handler)
        
        # Add file handler for persistent logs
        file_handler = logging.FileHandler("logs/app.log")
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
        
        return root_logger
    
    def setup_sentry(self):
        """Configure Sentry for error tracking"""
        if not self.sentry_dsn:
            logging.warning("Sentry DSN not configured - error tracking disabled")
            return
        
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.redis import RedisIntegration
            
            sentry_sdk.init(
                dsn=self.sentry_dsn,
                environment=self.environment,
                integrations=[
                    FastApiIntegration(auto_enabling_integrations=True),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                ],
                traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
                profiles_sample_rate=0.1,  # 10% of transactions for profiling
                attach_stacktrace=True,
                send_default_pii=False,  # Don't send PII for GDPR compliance
                max_breadcrumbs=50,
                before_send=self.filter_sensitive_data
            )
            
            logging.info("Sentry error tracking initialized")
            
        except ImportError:
            logging.warning("Sentry SDK not installed - error tracking disabled")
        except Exception as e:
            logging.error(f"Failed to initialize Sentry: {e}")
    
    def filter_sensitive_data(self, event, hint):
        """Filter sensitive data from Sentry events"""
        # Remove sensitive fields
        if 'request' in event:
            if 'data' in event['request']:
                data = event['request']['data']
                if isinstance(data, dict):
                    # Remove password fields
                    for key in ['password', 'secret', 'token', 'key']:
                        if key in data:
                            data[key] = '[FILTERED]'
        
        return event

class PerformanceMonitor:
    """Production performance monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/' if os.name != 'nt' else 'C:')
            
            return {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_mb": memory.available // 1024 // 1024,
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free // 1024 // 1024 // 1024
                },
                "application": {
                    "uptime_seconds": int(time.time() - self.start_time),
                    "request_count": self.request_count,
                    "error_count": self.error_count,
                    "error_rate": (self.error_count / max(self.request_count, 1)) * 100
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"Failed to get system metrics: {e}")
            return {"error": str(e)}
    
    def record_request(self):
        """Record a successful request"""
        self.request_count += 1
    
    def record_error(self):
        """Record an error"""
        self.error_count += 1

class AuditLogger:
    """Production audit logging"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger("audit")
        
    def log_user_action(self, user_id: str, action: str, resource: str, 
                       details: Optional[Dict] = None, ip_address: Optional[str] = None):
        """Log user action for audit trail"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "ip_address": ip_address,
            "session_id": details.get("session_id") if details else None
        }
        
        self.audit_logger.info(json.dumps(audit_entry))
    
    def log_security_event(self, event_type: str, severity: str, details: Dict):
        """Log security events"""
        security_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "security_event",
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        self.audit_logger.warning(json.dumps(security_entry))

# Global monitoring instances
production_logger = ProductionLogger()
performance_monitor = PerformanceMonitor()
audit_logger = AuditLogger()

def setup_production_monitoring():
    """Initialize all production monitoring"""
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Setup logging
    logger = production_logger.setup_logging()
    
    # Setup Sentry
    production_logger.setup_sentry()
    
    logging.info("Production monitoring initialized successfully")
    
    return {
        "logger": logger,
        "performance_monitor": performance_monitor,
        "audit_logger": audit_logger
    }
