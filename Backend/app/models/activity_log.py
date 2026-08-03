from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(String(50), nullable=False, index=True)

    entity_type = Column(String(50), nullable=True, index=True)
    entity_id = Column(Integer, nullable=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True, index=True)

    description = Column(Text, nullable=True)

    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)

    # Named "activity_metadata", not "metadata" - SQLAlchemy's Declarative Base reserves the
    # `metadata` attribute name on every model for its MetaData instance.
    activity_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User")
    section = relationship("Section")
