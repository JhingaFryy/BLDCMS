from typing import List, Optional

from pydantic import BaseModel


class SearchResultItem(BaseModel):
    id: int
    label: str
    subtitle: Optional[str] = None
    # Opaque key used by the Dashboard to deep-link back into that entity's existing page (numeric
    # id as a string for most entities; employee_id for Users, since the existing /users/ list
    # endpoint searches by employee_id, not numeric id).
    nav_key: str


class GlobalSearchResponse(BaseModel):
    locomotives: List[SearchResultItem]
    equipment: List[SearchResultItem]
    sections: List[SearchResultItem]
    users: List[SearchResultItem]
    checksheets: List[SearchResultItem]
    templates: List[SearchResultItem]
