from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String(255), nullable=False)

    message = Column(Text, nullable=False)

    type = Column(String(50), nullable=False, default="SYSTEM")

    checksheet_id = Column(Integer, ForeignKey("checksheet_header.id"), nullable=True)

    is_read = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    checksheet = relationship("ChecksheetHeader")
