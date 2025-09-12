"""
Configuration management for Enterprise Cloud Cost Analyzer
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Enterprise Cloud Cost Analyzer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://localhost/cloud_cost_analyzer_enterprise"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # ClickHouse (for analytics)
    CLICKHOUSE_URL: str = "clickhouse://localhost:9000"
    CLICKHOUSE_DATABASE: str = "cost_analytics"
    
    # ElasticSearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "cost_analyzer"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:8080"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Cloud Providers
    AWS_DEFAULT_REGION: str = "us-east-1"
    AZURE_DEFAULT_REGION: str = "East US"
    GCP_DEFAULT_REGION: str = "us-central1"
    
    # Encryption
    ENCRYPTION_KEY: str = "your-encryption-key-change-in-production"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Cache TTL (seconds)
    CACHE_TTL_SHORT: int = 300      # 5 minutes
    CACHE_TTL_MEDIUM: int = 1800    # 30 minutes
    CACHE_TTL_LONG: int = 3600      # 1 hour
    CACHE_TTL_VERY_LONG: int = 86400  # 24 hours
    
    # Cost Data
    COST_DATA_RETENTION_DAYS: int = 1095  # 3 years
    COST_SYNC_BATCH_SIZE: int = 1000
    MAX_CONCURRENT_SYNC_JOBS: int = 5
    
    # Business Intelligence
    BI_REFRESH_INTERVAL_MINUTES: int = 60
    FORECAST_MAX_HORIZON_MONTHS: int = 24
    ANOMALY_DETECTION_ENABLED: bool = True
    
    # Email (for notifications)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    
    # Notifications
    SLACK_WEBHOOK_URL: Optional[str] = None
    TEAMS_WEBHOOK_URL: Optional[str] = None
    DISCORD_WEBHOOK_URL: Optional[str] = None
    
    # File Storage
    STORAGE_TYPE: str = "local"  # local, s3, azure, gcp
    STORAGE_BUCKET: Optional[str] = None
    STORAGE_REGION: Optional[str] = None
    LOCAL_STORAGE_PATH: str = "./storage"
    
    # Security
    ENABLE_HTTPS_REDIRECT: bool = False
    TRUSTED_PROXIES: List[str] = []
    SESSION_TIMEOUT_MINUTES: int = 480  # 8 hours
    
    # Feature Flags
    ENABLE_UNIT_ECONOMICS: bool = True
    ENABLE_FORECASTING: bool = True
    ENABLE_ANOMALY_DETECTION: bool = True
    ENABLE_AUTOMATED_OPTIMIZATION: bool = True
    ENABLE_KUBERNETES_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Environment-specific settings
def get_database_url() -> str:
    """Get database URL with fallback"""
    settings = get_settings()
    if settings.ENVIRONMENT == "test":
        return "postgresql://localhost/cloud_cost_analyzer_test"
    return settings.DATABASE_URL

def get_log_config() -> dict:
    """Get logging configuration"""
    settings = get_settings()
    
    if settings.LOG_FORMAT == "json":
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": settings.LOG_LEVEL
                }
            },
            "root": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console"]
            }
        }
    else:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": settings.LOG_LEVEL
                }
            },
            "root": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console"]
            }
        }