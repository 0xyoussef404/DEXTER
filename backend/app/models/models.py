"""
Database models for BugHunterX
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.session import Base


class ScanStatus(str, enum.Enum):
    """Scan status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityLevel(str, enum.Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(str, enum.Enum):
    """Types of vulnerabilities"""
    XSS = "xss"
    SQLI = "sqli"
    SSRF = "ssrf"
    COMMAND_INJECTION = "command_injection"
    XXE = "xxe"
    LFI = "lfi"
    RFI = "rfi"
    OPEN_REDIRECT = "open_redirect"
    CSRF = "csrf"
    CORS = "cors"
    SSTI = "ssti"
    DESERIALIZATION = "deserialization"
    INFO_DISCLOSURE = "info_disclosure"
    SUBDOMAIN_TAKEOVER = "subdomain_takeover"
    BROKEN_AUTH = "broken_auth"
    SENSITIVE_DATA = "sensitive_data"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    OTHER = "other"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    api_key = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")


class Target(Base):
    """Target model - represents a scan target"""
    __tablename__ = "targets"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False)
    domain = Column(String(255), index=True)
    ip_address = Column(String(45))  # IPv6 compatible
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scans = relationship("Scan", back_populates="target")


class Scan(Base):
    """Scan model - represents a security scan"""
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    target_id = Column(Integer, ForeignKey("targets.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Scan configuration
    scan_type = Column(String(50))  # recon, vuln, full
    config = Column(JSON)  # Scan configuration options
    
    # Scan status
    status = Column(SQLEnum(ScanStatus), default=ScanStatus.PENDING, index=True)
    progress = Column(Float, default=0.0)  # 0-100
    current_phase = Column(String(100))
    
    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Results summary
    total_findings = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)
    
    # Celery task ID
    task_id = Column(String(255), unique=True, index=True)
    
    # Relationships
    target = relationship("Target", back_populates="scans")
    user = relationship("User", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
    recon_results = relationship("ReconResult", back_populates="scan", cascade="all, delete-orphan")


class Finding(Base):
    """Finding model - represents a discovered vulnerability"""
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)
    
    # Vulnerability details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    vulnerability_type = Column(SQLEnum(VulnerabilityType), index=True)
    severity = Column(SQLEnum(SeverityLevel), index=True)
    confidence = Column(Float)  # 0.0-1.0
    
    # Location
    url = Column(String(2048))
    parameter = Column(String(255))
    method = Column(String(10))  # GET, POST, etc.
    
    # Evidence
    payload = Column(Text)
    request = Column(Text)
    response = Column(Text)
    proof = Column(JSON)  # Screenshots, specific proof data
    
    # Additional data
    cvss_score = Column(Float)
    cwe_id = Column(String(20))
    owasp_category = Column(String(100))
    remediation = Column(Text)
    references = Column(JSON)  # List of reference URLs
    
    # Status
    is_false_positive = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scan = relationship("Scan", back_populates="findings")


class ReconResult(Base):
    """Reconnaissance results model"""
    __tablename__ = "recon_results"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)
    
    # Recon type
    recon_type = Column(String(50), index=True)  # subdomain, port, tech, etc.
    
    # Data
    data = Column(JSON, nullable=False)
    raw_data = Column(Text)
    
    # Metadata
    source = Column(String(100))  # Tool/source that generated this
    confidence = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scan = relationship("Scan", back_populates="recon_results")
