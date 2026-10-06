from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import CorridorResponse
from ..models.all_models import Corridor

router = APIRouter(prefix="/corridors", tags=["Corridors"])

@router.get("", response_model=List[CorridorResponse])
def list_corridors(db: Session = Depends(get_db)):
    """Retrieve all operational corridors (Dedicated Freight Corridors, Golden Quadrilateral, High Speed)."""
    return db.query(Corridor).all()

@router.get("/{corridor_id}", response_model=CorridorResponse)
def get_corridor(corridor_id: str, db: Session = Depends(get_db)):
    """Retrieve corridor information by ID."""
    corr = db.query(Corridor).filter(Corridor.corridor_id == corridor_id).first()
    if not corr:
        raise HTTPException(status_code=404, detail=f"Corridor {corridor_id} not found")
    return corr
