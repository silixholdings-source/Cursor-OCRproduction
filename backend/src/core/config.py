"""
Configuration management for the AI ERP SaaS application
"""
import os
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI ERP SaaS Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, json_schema_extra={"env": "DEBUG"})
    ENVIRONMENT: str = Field(default="development", json_schema_extra={"env": "ENVIRONMENT"})
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI ERP SaaS"
    
    # Security
    # CRITICAL: These MUST be set in production via environment variables
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", json_schema_extra={"env": "SECRET_KEY"})
    JWT_SECRET: str = Field(default="dev-jwt-secret-change-in-production", json_schema_extra={"env": "JWT_SECRET"})
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    # Default to local SQLite in development to avoid external dependencies
    # Use a stable subdirectory to avoid permission/path issues
    DATABASE_URL: str = Field(default="sqlite:///./data/app.db", json_schema_extra={"env": "DATABASE_URL"})
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    # Redis is optional in development; features depending on it will degrade gracefully
    REDIS_URL: str = Field(default="redis://localhost:6379/0", json_schema_extra={"env": "REDIS_URL"})
    REDIS_POOL_SIZE: int = 10
    
    # CORS
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8000",
        env="BACKEND_CORS_ORIGINS"
    )
    
    # Allowed Hosts - CRITICAL: Restrict in production!
    ALLOWED_HOSTS: str = Field(
        default="localhost,127.0.0.1",
        env="ALLOWED_HOSTS"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [i.strip() for i in self.BACKEND_CORS_ORIGINS.split(",")]
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as a list"""
        return [i.strip() for i in self.ALLOWED_HOSTS.split(",")]
    
    # Paystack Integration (South African Payment Provider)
    PAYSTACK_SECRET_KEY: Optional[str] = Field(default=None, json_schema_extra={"env": "PAYSTACK_SECRET_KEY"})
    PAYSTACK_PUBLIC_KEY: Optional[str] = Field(default=None, json_schema_extra={"env": "PAYSTACK_PUBLIC_KEY"})
    PAYSTACK_WEBHOOK_SECRET: Optional[str] = Field(default=None, json_schema_extra={"env": "PAYSTACK_WEBHOOK_SECRET"})
    
    # Stripe Integration (Legacy/Alternative)
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, json_schema_extra={"env": "STRIPE_SECRET_KEY"})
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, json_schema_extra={"env": "STRIPE_PUBLISHABLE_KEY"})
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, json_schema_extra={"env": "STRIPE_WEBHOOK_SECRET"})
    STRIPE_WEBHOOK_TOLERANCE: int = Field(default=300, json_schema_extra={"env": "STRIPE_WEBHOOK_TOLERANCE"})
    
    # Email
    SMTP_HOST: Optional[str] = Field(default=None, json_schema_extra={"env": "SMTP_HOST"})
    SMTP_PORT: int = Field(default=587, json_schema_extra={"env": "SMTP_PORT"})
    SMTP_USER: Optional[str] = Field(default=None, json_schema_extra={"env": "SMTP_USER"})
    SMTP_PASSWORD: Optional[str] = Field(default=None, json_schema_extra={"env": "SMTP_PASSWORD"})
    SMTP_TLS: bool = Field(default=True, json_schema_extra={"env": "SMTP_TLS"})
    SMTP_SSL: bool = Field(default=False, json_schema_extra={"env": "SMTP_SSL"})
    
    # OCR Configuration
    OCR_PROVIDER: str = Field(default="advanced", json_schema_extra={"env": "OCR_PROVIDER"})
    OCR_CONFIDENCE_THRESHOLD: float = Field(default=0.8, json_schema_extra={"env": "OCR_CONFIDENCE_THRESHOLD"})
    OCR_SUPPORTED_LANGUAGES: List[str] = Field(
        default=["en", "es", "fr", "de", "zh", "ja", "pt", "it", "nl", "ru", "ar", "ko"],
        env="OCR_SUPPORTED_LANGUAGES"
    )
    
    # Internationalization
    DEFAULT_LOCALE: str = Field(default="en", json_schema_extra={"env": "DEFAULT_LOCALE"})
    SUPPORTED_LOCALES: List[str] = Field(
        default=["en", "es", "fr", "de", "zh", "ja", "pt", "it"],
        env="SUPPORTED_LOCALES"
    )
    
    # Currency Configuration
    DEFAULT_CURRENCY: str = Field(default="USD", json_schema_extra={"env": "DEFAULT_CURRENCY"})
    SUPPORTED_CURRENCIES: List[str] = Field(
        default=["USD", "EUR", "GBP", "JPY", "CNY", "CAD", "AUD", "CHF", "SEK", "NOK", "INR", "BRL", "MXN", "KRW", "SGD", "ZAR"],
        env="SUPPORTED_CURRENCIES"
    )
    CURRENCY_API_KEY: Optional[str] = Field(default=None, json_schema_extra={"env": "CURRENCY_API_KEY"})
    CURRENCY_API_PROVIDER: str = Field(default="exchangerate-api", json_schema_extra={"env": "CURRENCY_API_PROVIDER"})
    
    # Azure AD / Office 365 Authentication
    AZURE_CLIENT_ID: Optional[str] = Field(default=None, json_schema_extra={"env": "AZURE_CLIENT_ID"})
    AZURE_CLIENT_SECRET: Optional[str] = Field(default=None, json_schema_extra={"env": "AZURE_CLIENT_SECRET"})
    AZURE_TENANT_ID: Optional[str] = Field(default=None, json_schema_extra={"env": "AZURE_TENANT_ID"})
    AZURE_REDIRECT_URI: str = Field(default="http://localhost:3000/auth/azure/callback", json_schema_extra={"env": "AZURE_REDIRECT_URI"})
    
    # Active Directory LDAP
    LDAP_SERVER: Optional[str] = Field(default=None, json_schema_extra={"env": "LDAP_SERVER"})
    LDAP_BASE_DN: Optional[str] = Field(default=None, json_schema_extra={"env": "LDAP_BASE_DN"})
    LDAP_BIND_USER: Optional[str] = Field(default=None, json_schema_extra={"env": "LDAP_BIND_USER"})
    LDAP_BIND_PASSWORD: Optional[str] = Field(default=None, json_schema_extra={"env": "LDAP_BIND_PASSWORD"})
    LDAP_USER_FILTER: Optional[str] = Field(default="(sAMAccountName={username})", env="LDAP_USER_FILTER")
    
    # SAML 2.0 Configuration
    SAML_ENTITY_ID: Optional[str] = Field(default=None, json_schema_extra={"env": "SAML_ENTITY_ID"})
    SAML_SSO_URL: Optional[str] = Field(default=None, json_schema_extra={"env": "SAML_SSO_URL"})
    SAML_ACS_URL: str = Field(default="http://localhost:3000/auth/saml/acs", json_schema_extra={"env": "SAML_ACS_URL"})
    SAML_X509_CERT: Optional[str] = Field(default=None, json_schema_extra={"env": "SAML_X509_CERT"})
    SAML_PRIVATE_KEY: Optional[str] = Field(default=None, json_schema_extra={"env": "SAML_PRIVATE_KEY"})
    
    # SSO Configuration
    ENABLE_SSO: bool = Field(default=False, json_schema_extra={"env": "ENABLE_SSO"})
    SSO_AUTO_PROVISION: bool = Field(default=True, json_schema_extra={"env": "SSO_AUTO_PROVISION"})
    SSO_DEFAULT_ROLE: str = Field(default="user", json_schema_extra={"env": "SSO_DEFAULT_ROLE"})
    
    # Azure Form Recognizer
    AZURE_FORM_RECOGNIZER_ENDPOINT: Optional[str] = Field(default=None, json_schema_extra={"env": "AZURE_FORM_RECOGNIZER_ENDPOINT"})
    AZURE_FORM_RECOGNIZER_KEY: Optional[str] = Field(default=None, json_schema_extra={"env": "AZURE_FORM_RECOGNIZER_KEY"})
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, json_schema_extra={"env": "AWS_ACCESS_KEY_ID"})
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, json_schema_extra={"env": "AWS_SECRET_ACCESS_KEY"})
    AWS_REGION: str = Field(default="us-east-1", json_schema_extra={"env": "AWS_REGION"})
    AWS_S3_BUCKET: Optional[str] = Field(default=None, json_schema_extra={"env": "AWS_S3_BUCKET"})
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: Optional[str] = Field(default=None, json_schema_extra={"env": "GOOGLE_CLOUD_PROJECT"})
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(default=None, json_schema_extra={"env": "GOOGLE_APPLICATION_CREDENTIALS"})
    
    # File Upload
    MAX_FILE_SIZE_MB: int = Field(default=10, json_schema_extra={"env": "MAX_FILE_SIZE_MB"})
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[".pdf", ".jpg", ".jpeg", ".png", ".tiff"],
        env="ALLOWED_FILE_TYPES"
    )
    UPLOAD_DIR: str = Field(default="uploads", json_schema_extra={"env": "UPLOAD_DIR"})
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, json_schema_extra={"env": "RATE_LIMIT_PER_MINUTE"})
    RATE_LIMIT_BURST: int = Field(default=200, json_schema_extra={"env": "RATE_LIMIT_BURST"})
    
    # Monitoring
    ENABLE_MONITORING: bool = Field(default=True, json_schema_extra={"env": "ENABLE_MONITORING"})
    SENTRY_DSN: Optional[str] = Field(default=None, json_schema_extra={"env": "SENTRY_DSN"})
    OTEL_ENDPOINT: Optional[str] = Field(default=None, json_schema_extra={"env": "OTEL_ENDPOINT"})
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", json_schema_extra={"env": "LOG_LEVEL"})
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    # ML Configuration
    ML_MODELS_DIR: str = Field(default="models", json_schema_extra={"env": "ML_MODELS_DIR"})
    ML_TRAINING_ENABLED: bool = Field(default=True, json_schema_extra={"env": "ML_TRAINING_ENABLED"})
    ML_RETRAIN_FREQUENCY_HOURS: int = Field(default=24, json_schema_extra={"env": "ML_RETRAIN_FREQUENCY_HOURS"})
    
    # Email Processing
    EMAIL_PROCESSING_ENABLED: bool = Field(default=True, json_schema_extra={"env": "EMAIL_PROCESSING_ENABLED"})
    EMAIL_CHECK_INTERVAL_MINUTES: int = Field(default=5, json_schema_extra={"env": "EMAIL_CHECK_INTERVAL_MINUTES"})
    EMAIL_MAX_ATTACHMENT_SIZE_MB: int = Field(default=10, json_schema_extra={"env": "EMAIL_MAX_ATTACHMENT_SIZE_MB"})
    
    # Business Rules
    AUTO_APPROVAL_LIMIT: float = Field(default=1000.0, json_schema_extra={"env": "AUTO_APPROVAL_LIMIT"})
    DUPLICATE_THRESHOLD: float = Field(default=0.95, json_schema_extra={"env": "DUPLICATE_THRESHOLD"})
    FRAUD_THRESHOLD: float = Field(default=0.8, json_schema_extra={"env": "FRAUD_THRESHOLD"})
    MAX_PROCESSING_TIME_HOURS: int = Field(default=48, json_schema_extra={"env": "MAX_PROCESSING_TIME_HOURS"})
    
    # ERP Integration
    ERP_SYNC_ENABLED: bool = Field(default=True, json_schema_extra={"env": "ERP_SYNC_ENABLED"})
    ERP_SYNC_INTERVAL_MINUTES: int = Field(default=30, json_schema_extra={"env": "ERP_SYNC_INTERVAL_MINUTES"})
    ERP_RETRY_ATTEMPTS: int = Field(default=3, json_schema_extra={"env": "ERP_RETRY_ATTEMPTS"})
    
    # ERP System Configurations
    DYNAMICS_GP_CONFIG: Dict[str, Any] = Field(default={}, json_schema_extra={"env": "DYNAMICS_GP_CONFIG"})
    DYNAMICS_365_BC_CONFIG: Dict[str, Any] = Field(default={}, json_schema_extra={"env": "DYNAMICS_365_BC_CONFIG"})
    XERO_CONFIG: Dict[str, Any] = Field(default={}, json_schema_extra={"env": "XERO_CONFIG"})
    QUICKBOOKS_CONFIG: Dict[str, Any] = Field(default={}, json_schema_extra={"env": "QUICKBOOKS_CONFIG"})
    SAGE_CONFIG: Dict[str, Any] = Field(default={}, json_schema_extra={"env": "SAGE_CONFIG"})
    SAP_CONFIG: Dict[str, Any] = Field(default={}, json_schema_extra={"env": "SAP_CONFIG"})
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = Field(default=3600, json_schema_extra={"env": "CACHE_TTL_SECONDS"})
    CACHE_MAX_SIZE: int = Field(default=1000, json_schema_extra={"env": "CACHE_MAX_SIZE"})
    
    # Performance
    MAX_WORKERS: int = Field(default=4, json_schema_extra={"env": "MAX_WORKERS"})
    WORKER_TIMEOUT: int = Field(default=300, json_schema_extra={"env": "WORKER_TIMEOUT"})
    
    # Security Headers
    ENABLE_SECURITY_HEADERS: bool = Field(default=True, json_schema_extra={"env": "ENABLE_SECURITY_HEADERS"})
    CSP_POLICY: str = Field(
        default="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        env="CSP_POLICY"
    )
    
    # API Documentation
    ENABLE_API_DOCS: bool = Field(default=True, json_schema_extra={"env": "ENABLE_API_DOCS"})
    API_DOCS_URL: str = Field(default="/docs", json_schema_extra={"env": "API_DOCS_URL"})
    
    # Health Checks
    HEALTH_CHECK_INTERVAL_SECONDS: int = Field(default=30, json_schema_extra={"env": "HEALTH_CHECK_INTERVAL_SECONDS"})
    HEALTH_CHECK_TIMEOUT_SECONDS: int = Field(default=5, json_schema_extra={"env": "HEALTH_CHECK_TIMEOUT_SECONDS"})
    
    # Backup Configuration
    BACKUP_ENABLED: bool = Field(default=False, json_schema_extra={"env": "BACKUP_ENABLED"})
    BACKUP_SCHEDULE: str = Field(default="0 2 * * *", json_schema_extra={"env": "BACKUP_SCHEDULE"})  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = Field(default=30, json_schema_extra={"env": "BACKUP_RETENTION_DAYS"})
    
    # Multi-tenancy
    ENABLE_MULTI_TENANCY: bool = Field(default=True, json_schema_extra={"env": "ENABLE_MULTI_TENANCY"})
    TENANT_ISOLATION_LEVEL: str = Field(default="database", json_schema_extra={"env": "TENANT_ISOLATION_LEVEL"})  # database, schema, row
    
    # Feature Flags
    ENABLE_AI_INSIGHTS: bool = Field(default=True, json_schema_extra={"env": "ENABLE_AI_INSIGHTS"})
    ENABLE_REAL_TIME_DASHBOARD: bool = Field(default=True, json_schema_extra={"env": "ENABLE_REAL_TIME_DASHBOARD"})
    ENABLE_ADVANCED_ANALYTICS: bool = Field(default=True, json_schema_extra={"env": "ENABLE_ADVANCED_ANALYTICS"})
    ENABLE_AUTOMATED_WORKFLOWS: bool = Field(default=True, json_schema_extra={"env": "ENABLE_AUTOMATED_WORKFLOWS"})
    
    # Notification
    NOTIFICATION_ENABLED: bool = Field(default=True, json_schema_extra={"env": "NOTIFICATION_ENABLED"})
    NOTIFICATION_EMAIL_FROM: Optional[str] = Field(default=None, json_schema_extra={"env": "NOTIFICATION_EMAIL_FROM"})
    NOTIFICATION_SMS_ENABLED: bool = Field(default=False, json_schema_extra={"env": "NOTIFICATION_SMS_ENABLED"})
    
    # Compliance
    ENABLE_AUDIT_LOGGING: bool = Field(default=True, json_schema_extra={"env": "ENABLE_AUDIT_LOGGING"})
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=365, json_schema_extra={"env": "AUDIT_LOG_RETENTION_DAYS"})
    ENABLE_GDPR_COMPLIANCE: bool = Field(default=True, json_schema_extra={"env": "ENABLE_GDPR_COMPLIANCE"})
    
    # Performance Monitoring
    ENABLE_PERFORMANCE_MONITORING: bool = Field(default=True, json_schema_extra={"env": "ENABLE_PERFORMANCE_MONITORING"})
    PERFORMANCE_METRICS_INTERVAL_SECONDS: int = Field(default=60, json_schema_extra={"env": "PERFORMANCE_METRICS_INTERVAL_SECONDS"})
    
    # Error Handling
    ENABLE_ERROR_REPORTING: bool = Field(default=True, json_schema_extra={"env": "ENABLE_ERROR_REPORTING"})
    ERROR_REPORTING_EMAIL: Optional[str] = Field(default=None, json_schema_extra={"env": "ERROR_REPORTING_EMAIL"})
    
    # Development
    ENABLE_DEBUG_TOOLBAR: bool = Field(default=False, json_schema_extra={"env": "ENABLE_DEBUG_TOOLBAR"})
    ENABLE_SQL_LOGGING: bool = Field(default=False, json_schema_extra={"env": "ENABLE_SQL_LOGGING"})
    
    model_config = ConfigDict(

    
        env_file=".env", case_sensitive=True, extra="ignore"

    
    )

@lru_cache()
def get_settings() -> Settings:
    """Get application settings"""
    return Settings()

# Global settings instance
settings = get_settings()