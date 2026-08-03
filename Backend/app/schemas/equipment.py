from typing import Optional
from pydantic import BaseModel


class EquipmentCreate(BaseModel):
	equipment_code: str
	equipment_name: str


class EquipmentUpdate(BaseModel):
	equipment_code: str
	equipment_name: str
	is_active: bool = True


class EquipmentResponse(BaseModel):
	id: int
	equipment_code: str
	equipment_name: str
	is_active: bool
	used_in: Optional[str] = None

	class Config:
		from_attributes = True
