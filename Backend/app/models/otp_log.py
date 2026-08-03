from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class OTPLog(Base):
    __tablename__ = "otp_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    otp = Column(String(64), nullable=False)
    # Plaintext OTP, kept separate from the hash above (which remains the only value ever used
    # for verification) - only ever populated in DEBUG=True mode (see otp_service.request_otp),
    # so the OTP Logs Dashboard page can show it directly instead of requiring a real SMS gateway.
    plain_otp = Column(String(10), nullable=True)
    attempts = Column(Integer, default=0, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship(
        "User",
        back_populates="otp_logs"
    )
