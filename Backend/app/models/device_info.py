from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class DeviceInfo(Base):
    """Module 44: one row per physical Android device (keyed on the device's stable
    ANDROID_ID, reported at login/OTP-verify time), giving the System Administration CLI a
    device registry to read. Deliberately separate from UserSession (which already tracks
    device_type/device_name/device_id per login) rather than adding these columns there, so the
    security-critical session table's shape is untouched - this table is pure operational
    metadata, upserted on every successful login, never read by any authentication/authorization
    code path.

    All device attributes are optional and reflect the state *as of the last login*, not
    real-time telemetry - there is no persistent connection or push channel to the device."""
    __tablename__ = "device_info"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    manufacturer = Column(String(100), nullable=True)
    device_model = Column(String(100), nullable=True)
    os_version = Column(String(50), nullable=True)
    app_version = Column(String(50), nullable=True)

    battery_level = Column(Integer, nullable=True)
    network_type = Column(String(20), nullable=True)
    storage_free_mb = Column(Integer, nullable=True)
    storage_total_mb = Column(Integer, nullable=True)

    # Module 44: real, disclosed device-management notice - set when the technician
    # acknowledges the in-app notice explaining what IT can see/manage on this device. Never
    # inferred or defaulted to "acknowledged" - stays NULL until the user actually dismisses it.
    disclosure_acknowledged_at = Column(DateTime, nullable=True)

    # Module 44: a CLI-issued command awaiting the device's next contact with the backend (e.g.
    # "CLEAR_APP_DATA"). Cleared automatically once a new session is created for this device_id
    # after the command was issued, since that proves the device re-authenticated post-command -
    # see device_info_service.clear_pending_command_if_stale().
    pending_command = Column(String(50), nullable=True)
    pending_command_issued_at = Column(DateTime, nullable=True)

    last_seen_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User")
