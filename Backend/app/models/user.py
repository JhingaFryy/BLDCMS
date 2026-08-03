from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String(20), unique=True, nullable=False)

    name = Column(String(100), nullable=False)

    mobile = Column(String(15), unique=True, nullable=False)

    email = Column(String(100))

    password_hash = Column(String(255), nullable=True)

    role = Column(String(20), nullable=False)

    is_active = Column(Boolean, default=True)

    # New: optional section assignment
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    otp_logs = relationship(
        "OTPLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # relationship to Section for convenience (used in responses)
    section = relationship("Section")

    @property
    def section_name(self):
        return self.section.name if self.section else None
