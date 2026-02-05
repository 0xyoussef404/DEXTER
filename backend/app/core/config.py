"""
Configuration settings for BugHunterX
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Project Info
    PROJECT_NAME: str = "BugHunterX"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Enterprise Web Application Security Testing Platform"
    DEBUG: bool = True
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Database URLs
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://bughunterx:bughunterx_secure_pass@localhost:5432/bughunterx"
    )
    MONGO_URL: str = os.getenv(
        "MONGO_URL",
        "mongodb://bughunterx:bughunterx_secure_pass@localhost:27017/"
    )
    MONGO_DB_NAME: str = "bughunterx"
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://:bughunterx_secure_pass@localhost:6379/0"
    )
    ELASTICSEARCH_URL: str = os.getenv(
        "ELASTICSEARCH_URL",
        "http://localhost:9200"
    )
    
    # Celery Settings
    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL",
        "amqp://bughunterx:bughunterx_secure_pass@localhost:5672/"
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://:bughunterx_secure_pass@localhost:6379/1"
    )
    
    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-super-secret-key-change-this-in-production-min-32-chars-long"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Scan Settings
    MAX_CONCURRENT_SCANS: int = 10
    SCAN_TIMEOUT_HOURS: int = 24
    MAX_TARGETS_PER_SCAN: int = 100
    
    # Recon Settings
    SUBDOMAIN_ENUMERATION_TIMEOUT: int = 3600  # 1 hour
    PORT_SCAN_TIMEOUT: int = 1800  # 30 minutes
    CRAWL_TIMEOUT: int = 3600  # 1 hour
    MAX_CRAWL_DEPTH: int = 5
    MAX_PAGES_PER_DOMAIN: int = 1000
    
    # Fuzzing Settings
    FUZZING_THREADS: int = 50
    FUZZING_TIMEOUT_PER_REQUEST: int = 30
    MAX_PAYLOADS_PER_PARAMETER: int = 1000
    BASELINE_REQUESTS: int = 10
    
    # ML Settings
    ML_MODEL_PATH: str = "./models"
    ML_CONFIDENCE_THRESHOLD: float = 0.8
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    WORDLISTS_DIR: str = "./wordlists"
    REPORTS_DIR: str = "./reports"
    
    # External APIs (optional - for enhanced features)
    VIRUSTOTAL_API_KEY: Optional[str] = os.getenv("VIRUSTOTAL_API_KEY")
    SHODAN_API_KEY: Optional[str] = os.getenv("SHODAN_API_KEY")
    CENSYS_API_ID: Optional[str] = os.getenv("CENSYS_API_ID")
    CENSYS_API_SECRET: Optional[str] = os.getenv("CENSYS_API_SECRET")
    SECURITYTRAILS_API_KEY: Optional[str] = os.getenv("SECURITYTRAILS_API_KEY")
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()
