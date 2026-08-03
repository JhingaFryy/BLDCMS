from pydantic import BaseModel, Field


class LocomotiveCreate(BaseModel):
	loco_number: str = Field(max_length=10)
	loco_model: str = Field(max_length=20)


class LocomotiveUpdate(BaseModel):
	loco_number: str = Field(max_length=10)
	loco_model: str = Field(max_length=20)
	technology: str | None = None
	is_active: bool = True


class LocomotiveResponse(BaseModel):
	id: int
	loco_number: str
	loco_model: str
	technology: str
	is_active: bool

	class Config:
		from_attributes = True
