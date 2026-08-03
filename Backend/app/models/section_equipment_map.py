from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class SectionEquipmentMap(Base):
    __tablename__ = "section_equipment_map"

    id = Column(Integer, primary_key=True, index=True)

    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)

    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)

    technology = Column(String(20), nullable=False)

    is_active = Column(Boolean, default=True)

    section = relationship("Section")
    equipment = relationship("Equipment")

    @property
    def section_name(self):
        return self.section.name if self.section else None

    @property
    def equipment_name(self):
        return self.equipment.equipment_name if self.equipment else None
