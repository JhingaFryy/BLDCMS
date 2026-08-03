from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    jti = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    refresh_token_hash = Column(String(255), nullable=True)
    device_type = Column(String(20), nullable=False, default="WEB")
    device_name = Column(String(100), nullable=True)
    device_id = Column(String(100), nullable=True, index=True)
    app_version = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_activity = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String(255), nullable=True)

    user = relationship("User", back_populates="sessions")
