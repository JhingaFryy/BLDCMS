from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    SUPERVISOR = "Supervisor"
    TECHNICIAN = "Technician"

class UserBase(BaseModel):
    employee_id: str
    name: str
    mobile: str
    email: Optional[str] = None
    role: UserRole
    is_active: bool = True
    section_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    section_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    section_name: Optional[str] = None

    class Config:
        from_attributes = True


class PaginatedUsersResponse(BaseModel):
    items: list[UserResponse]
    total: int

    class Config:
        from_attributes = True
