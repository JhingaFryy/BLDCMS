from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class ChecksheetValue(Base):
    __tablename__ = "checksheet_value"

    id = Column(Integer, primary_key=True, index=True)

    checksheet_id = Column(
        Integer,
        ForeignKey("checksheet_header.id"),
        nullable=False
    )

    field_id = Column(
        Integer,
        ForeignKey("template_fields.id"),
        nullable=False
    )

    field_value = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    header = relationship(
        "ChecksheetHeader",
        back_populates="values"
    )

    field = relationship("TemplateField")
