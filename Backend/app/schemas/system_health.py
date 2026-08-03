from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    name: str
    status: str  # "Online" | "Offline"
    response_time_ms: float
    last_checked: datetime
    detail: Optional[str] = None


class ServerInfo(BaseModel):
    cpu_usage_percent: float
    memory_usage_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    uptime: str
    python_version: str
    fastapi_version: str
    postgresql_version: Optional[str] = None
    operating_system: str


class ApplicationInfo(BaseModel):
    backend_version: str
    android_version: Optional[str] = None
    build_date: Optional[datetime] = None


class DatabaseStats(BaseModel):
    total_users: int
    total_technicians: int
    total_supervisors: int
    total_locomotives: int
    total_equipment: int
    total_checksheets: int
    pending_reviews: int
    approved: int
    rejected: int


class ActiveUser(BaseModel):
    employee_id: str
    name: str
    role: str
    login_time: datetime
    last_activity: datetime


class DailyCounts(BaseModel):
    date: str
    signature_count: int
    checksheet_submission_count: int
    approval_count: int


class SlowestEndpoint(BaseModel):
    endpoint: str
    avg_duration_ms: float
    count: int


class FrequentEndpoint(BaseModel):
    endpoint: str
    count: int


class FailedRequest(BaseModel):
    timestamp: datetime
    method: str
    endpoint: str
    status_code: int
    duration_ms: float


class RecentException(BaseModel):
    timestamp: datetime
    method: str
    endpoint: str
    duration_ms: float


class RequestMetrics(BaseModel):
    avg_response_time_ms: Optional[float] = None
    slowest_endpoints: List[SlowestEndpoint] = []
    most_frequent_endpoints: List[FrequentEndpoint] = []
    recent_failed_requests: List[FailedRequest] = []
    recent_exceptions: List[RecentException] = []


class DigitalSignatureStatus(BaseModel):
    recent_success_count: int
    recent_failure_count: int
    last_signature_at: Optional[datetime] = None


class PdfGenerationStats(BaseModel):
    average_duration_ms: Optional[float] = None
    count_today: int


class DatabaseConnectionInfo(BaseModel):
    checked_out: int
    pool_size: int


class SystemHealthOverview(BaseModel):
    service_status: List[ServiceStatus]
    server_info: ServerInfo
    application_info: ApplicationInfo
    database_stats: DatabaseStats
    active_users: List[ActiveUser]
    daily_counts: DailyCounts
    request_metrics: RequestMetrics
    digital_signature_status: DigitalSignatureStatus
    pdf_generation_stats: PdfGenerationStats
    database_connection_info: DatabaseConnectionInfo


class LogFileInfo(BaseModel):
    key: str
    label: str
    exists: bool
    size_bytes: int
    last_modified: Optional[datetime] = None


class LogTailResponse(BaseModel):
    key: str
    label: str
    lines: List[str]


class ViteLogEventCreate(BaseModel):
    """Module 33.1: a single Dashboard<->Backend connectivity event reported by the Dashboard
    (axios interceptors, main.tsx on load, vite.config.ts's dev-server plugin, HMR listeners).
    Deliberately small and tightly constrained (Literal severity/source, capped message length) -
    this endpoint accepts no auth (see app/api/system_health.py), so it must never accept
    free-form/oversized input."""
    severity: Literal["INFO", "WARNING", "ERROR"]
    source: Literal["Vite", "Dashboard"]
    message: str = Field(min_length=1, max_length=300)
