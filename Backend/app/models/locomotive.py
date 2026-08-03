from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.database.base import Base

class Locomotive(Base):
	__tablename__ = "locomotives"

	id = Column(Integer, primary_key=True, index=True)
	loco_number = Column(String(10), unique=True, nullable=False)
	loco_model = Column(String(20), nullable=False)
	technology = Column(String(20), nullable=False)
	is_active = Column(Boolean, default=True)
	created_at = Column(DateTime, server_default=func.now())
