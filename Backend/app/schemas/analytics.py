from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DailyTrendPoint(BaseModel):
    date: str
    count: int


class SectionCount(BaseModel):
    section_id: Optional[int] = None
    section_name: Optional[str] = None
    count: int


class EquipmentCount(BaseModel):
    equipment_id: Optional[int] = None
    equipment_name: Optional[str] = None
    count: int


class StatusDistribution(BaseModel):
    DRAFT: int = 0
    SUBMITTED: int = 0
    UNDER_REVIEW: int = 0
    APPROVED: int = 0
    REJECTED: int = 0


class RecentActivityItem(BaseModel):
    checksheet_id: int
    event: str
    at: datetime
    actor_name: Optional[str] = None
    actor_role: Optional[str] = None
    locomotive_number: Optional[str] = None
    equipment_name: Optional[str] = None
    section_name: Optional[str] = None


class ChecksheetAnalyticsSummary(BaseModel):
    total_locomotives: int
    total_equipment: int
    total_technicians: int
    total_supervisors: int
    today_submitted: int
    pending_review: int
    signed: int
    rejected: int
    needs_correction: int
    daily_trend: List[DailyTrendPoint]
    by_section: List[SectionCount]
    by_equipment: List[EquipmentCount]
    status_distribution: StatusDistribution
    recent_activity: List[RecentActivityItem]
