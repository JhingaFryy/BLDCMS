from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database.base import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)

    equipment_code = Column(String(20), unique=True, nullable=False)

    equipment_name = Column(String(100), nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
