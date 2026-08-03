from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class ChecksheetHeader(Base):
    __tablename__ = "checksheet_header"

    id = Column(Integer, primary_key=True, index=True)

    locomotive_id = Column(Integer, ForeignKey("locomotives.id"), nullable=False)

    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)

    # Module 36: nullable as of migration 012 - sections with no equipment at all (M6-HR) submit
    # checksheets with equipment_id NULL, against a template that is itself equipment_id NULL
    # (see checksheet_templates.equipment_id's own Module 29.5 comment). Every other section's
    # checksheets continue to always set this, unchanged.
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)

    template_id = Column(Integer, ForeignKey("checksheet_templates.id"), nullable=False)

    technician_mobile = Column(String(15), nullable=False)

    work_type = Column(String(20))

    # Module 32: which of the locomotive's 6 physical traction motors this checksheet covers
    # (e.g. "TM-1".."TM-6"), and which template variant (e.g. "GC"/"OVERHAUL") was used to fill it
    # in. Both NULL for every equipment other than Traction Motor. Neither participates in the
    # status state machine or any other business logic - pure metadata, stored and displayed the
    # same way work_type already is.
    traction_motor_number = Column(String(20), nullable=True)
    maintenance_type = Column(String(20), nullable=True)

    status = Column(String(20), default="DRAFT")

    submitted_at = Column(DateTime)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    approved_at = Column(DateTime)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    rejected_at = Column(DateTime)
    rejected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text)

    last_modified_at = Column(DateTime)
    last_modified_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    pdf_path = Column(String)

    created_at = Column(DateTime, server_default=func.now())

    locomotive = relationship("Locomotive")
    section = relationship("Section")
    equipment = relationship("Equipment")
    template = relationship("ChecksheetTemplate")
    submitted_by_user = relationship("User", foreign_keys=[submitted_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    rejected_by_user = relationship("User", foreign_keys=[rejected_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    # technician_mobile is not a real FK (the mobile-OTP login flow identifies technicians by
    # mobile number, not user id) - this read-only relationship lets the service layer resolve
    # the technician's name via a single LEFT JOIN instead of a per-row lookup (N+1).
    technician = relationship(
        "User",
        primaryjoin="foreign(ChecksheetHeader.technician_mobile) == User.mobile",
        viewonly=True,
        uselist=False
    )

    values = relationship(
        "ChecksheetValue",
        back_populates="header",
        cascade="all, delete-orphan"
    )
