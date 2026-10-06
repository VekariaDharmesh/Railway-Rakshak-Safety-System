from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import SearchResultItem
from ..services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Global Command Search"])

@router.get("", response_model=List[SearchResultItem])
def search_system(
    q: str = Query(..., min_length=1, description="Search query string (e.g. DL-01, Mumbai, INC-1042, DR-021, HIGH)"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Unified command search across Railway Nodes, Corridors, Incidents, Threats, and Drones.
    Used by top command bar and Ctrl+K shortcut.
    """
    return SearchService.search(db, query_str=q, limit=limit)
