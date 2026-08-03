from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.search import GlobalSearchResponse
from app.security.dependencies import require_supervisor
from app.services.search_service import global_search

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.get("/", response_model=GlobalSearchResponse)
def search(
    q: str = Query(..., min_length=2, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_supervisor)
):
    return global_search(db, q, current_user)
