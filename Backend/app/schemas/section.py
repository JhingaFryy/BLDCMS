from pydantic import BaseModel


class SectionCreate(BaseModel):
    name: str


class SectionUpdate(BaseModel):
    name: str


class SectionResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
