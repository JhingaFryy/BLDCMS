from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.base import Base

class Section(Base):
	__tablename__ = "sections"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String(100), unique=True, nullable=False)
	created_at = Column(DateTime, server_default=func.now())
