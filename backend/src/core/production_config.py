"""
Production Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class ProductionSettings(BaseSettings):
    """Production configuration settings"""
    
    # Application
    APP_NAME: str = "AI ERP SaaS"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_POOL_SIZE: int = 10
    
    # OCR Service
    OCR_SERVICE_URL: str = "http://ocr-service:8001"
    OCR_SERVICE_TIMEOUT: int = 30
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = []
    ALLOWED_HOSTS: List[str] = []
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SENTRY_DSN: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "/app/uploads"
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    
    # Azure Integration
    AZURE_FORM_RECOGNIZER_ENDPOINT: Optional[str] = None
    AZURE_FORM_RECOGNIZER_KEY: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    
    # ERP Integration
    ERP_SYSTEM: str = "none"  # none, dynamics_gp, sage, quickbooks
    ERP_API_URL: Optional[str] = None
    ERP_API_KEY: Optional[str] = None
    
    # Performance
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 300  # 5 minutes
    ENABLE_COMPRESSION: bool = True
    
    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    
            model_config = ConfigDict(

    
                env_file=".env" case_sensitive=True

    
            )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as list"""
        if isinstance(self.ALLOWED_HOSTS, str):
            return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
        return self.ALLOWED_HOSTS
    
    @property
    def database_config(self) -> dict:
        """Get database configuration"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_recycle": self.DATABASE_POOL_RECYCLE,
            "echo": self.DEBUG
        }
    
    @property
    def redis_config(self) -> dict:
        """Get Redis configuration"""
        return {
            "url": self.REDIS_URL,
            "pool_size": self.REDIS_POOL_SIZE,
            "decode_responses": True
        }
    
    @property
    def security_config(self) -> dict:
        """Get security configuration"""
        return {
            "secret_key": self.SECRET_KEY,
            "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": self.REFRESH_TOKEN_EXPIRE_DAYS,
            "algorithm": self.ALGORITHM
        }
    
    @property
    def monitoring_config(self) -> dict:
        """Get monitoring configuration"""
        return {
            "enable_metrics": self.ENABLE_METRICS,
            "metrics_port": self.METRICS_PORT,
            "log_level": self.LOG_LEVEL,
            "log_format": self.LOG_FORMAT,
            "sentry_dsn": self.SENTRY_DSN
        }

# Global settings instance
settings = ProductionSettings()

# Environment-specific configurations
def get_environment_config():
    """Get environment-specific configuration"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return {
            "debug": False,
            "log_level": "INFO",
            "cors_origins": settings.cors_origins_list,
            "allowed_hosts": settings.allowed_hosts_list,
            "enable_metrics": True,
            "enable_compression": True,
            "enable_caching": True
        }
    elif env == "staging":
        return {
            "debug": False,
            "log_level": "DEBUG",
            "cors_origins": ["*"],
            "allowed_hosts": ["*"],
            "enable_metrics": True,
            "enable_compression": True,
            "enable_caching": True
        }
    else:  # development
        return {
            "debug": True,
            "log_level": "DEBUG",
            "cors_origins": ["*"],
            "allowed_hosts": ["*"],
            "enable_metrics": False,
            "enable_compression": False,
            "enable_caching": False
        }









