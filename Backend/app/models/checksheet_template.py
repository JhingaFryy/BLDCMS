from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class ChecksheetTemplate(Base):
    __tablename__ = "checksheet_templates"
    __table_args__ = (
        UniqueConstraint('template_code', 'version', name='uq_template_code_version'),
    )

    id = Column(Integer, primary_key=True, index=True)

    template_code = Column(String(50), nullable=False, index=True)

    version = Column(Integer, nullable=False, default=1)

    # Nullable as of Module 29.5: a template with equipment_id set is an ordinary
    # equipment-specific template (unchanged behavior); a template with equipment_id NULL and
    # section_id set is a section-wide "common page" template (e.g. the M35-Aux common auxiliary
    # info page) that gets prepended ahead of every equipment template in that section - see
    # checksheet_template_service.get_template_detail's compose logic.
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)

    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)

    technology = Column(String(20), nullable=False)

    # Module 32: disambiguates multiple active templates that would otherwise share the same
    # (equipment_id, technology) - e.g. Traction Motor's GC vs Overhaul checksheets. NULL for
    # every template that doesn't need this (the overwhelming majority - resolution there is
    # unchanged: equipment_id + technology alone is enough).
    maintenance_type = Column(String(20), nullable=True)

    template_name = Column(String(100), nullable=False)

    description = Column(Text)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())

    equipment = relationship("Equipment")
    section = relationship("Section")

    fields = relationship(
        "TemplateField",
        back_populates="template",
        cascade="all, delete-orphan"
    )
