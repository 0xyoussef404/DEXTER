"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(str, Enum):
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


class ScanType(str, Enum):
    RECON = "recon"
    VULN = "vuln"
    FULL = "full"


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Target schemas
class TargetBase(BaseModel):
    url: str
    domain: Optional[str] = None
    ip_address: Optional[str] = None


class TargetCreate(TargetBase):
    pass


class Target(TargetBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Scan Configuration
class ReconConfig(BaseModel):
    """Reconnaissance scan configuration"""
    subdomain_enumeration: bool = True
    passive_sources: bool = True
    active_enumeration: bool = True
    subdomain_takeover: bool = True
    dns_analysis: bool = True
    port_scanning: bool = True
    top_ports: bool = True
    full_port_scan: bool = False
    service_detection: bool = True
    tech_detection: bool = True
    web_crawling: bool = True
    crawl_depth: int = Field(default=3, ge=1, le=10)
    javascript_analysis: bool = True
    content_discovery: bool = True
    wordlist_level: str = Field(default="standard", pattern="^(quick|standard|deep)$")
    api_discovery: bool = True
    parameter_discovery: bool = True


class VulnConfig(BaseModel):
    """Vulnerability scanning configuration"""
    xss_detection: bool = True
    xss_contexts: List[str] = ["html", "attribute", "javascript", "url"]
    sqli_detection: bool = True
    sqli_level: int = Field(default=3, ge=1, le=5)
    sqli_risk: int = Field(default=2, ge=1, le=3)
    ssrf_detection: bool = True
    command_injection: bool = True
    xxe_detection: bool = True
    path_traversal: bool = True
    ssti_detection: bool = True
    fuzzing_enabled: bool = True
    fuzzing_threads: int = Field(default=50, ge=1, le=200)
    custom_payloads: Optional[List[str]] = None
    waf_bypass: bool = True


class ScanConfig(BaseModel):
    """Complete scan configuration"""
    scan_type: ScanType
    recon: Optional[ReconConfig] = None
    vuln: Optional[VulnConfig] = None
    timeout_hours: int = Field(default=24, ge=1, le=72)
    max_threads: int = Field(default=10, ge=1, le=100)
    rate_limit: Optional[int] = None  # Requests per second
    user_agent: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    proxy: Optional[str] = None


# Scan schemas
class ScanBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_id: int
    config: ScanConfig


class ScanCreate(ScanBase):
    pass


class ScanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ScanStatus] = None


class ScanSummary(BaseModel):
    """Scan summary for list views"""
    id: int
    name: str
    status: ScanStatus
    progress: float
    target_url: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    
    model_config = ConfigDict(from_attributes=True)


class Scan(ScanBase):
    id: int
    status: ScanStatus
    progress: float
    current_phase: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    task_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Finding schemas
class FindingBase(BaseModel):
    title: str
    description: Optional[str] = None
    vulnerability_type: VulnerabilityType
    severity: SeverityLevel
    confidence: float = Field(ge=0.0, le=1.0)
    url: str
    parameter: Optional[str] = None
    method: Optional[str] = None
    payload: Optional[str] = None
    request: Optional[str] = None
    response: Optional[str] = None
    proof: Optional[Dict[str, Any]] = None
    cvss_score: Optional[float] = None
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = None


class FindingCreate(FindingBase):
    scan_id: int


class FindingUpdate(BaseModel):
    is_false_positive: Optional[bool] = None
    is_verified: Optional[bool] = None
    notes: Optional[str] = None


class Finding(FindingBase):
    id: int
    scan_id: int
    is_false_positive: bool
    is_verified: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Recon Result schemas
class ReconResultBase(BaseModel):
    recon_type: str
    data: Dict[str, Any]
    raw_data: Optional[str] = None
    source: str
    confidence: Optional[float] = None


class ReconResultCreate(ReconResultBase):
    scan_id: int


class ReconResult(ReconResultBase):
    id: int
    scan_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    username: Optional[str] = None


# Response schemas
class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
    error: Optional[str] = None
