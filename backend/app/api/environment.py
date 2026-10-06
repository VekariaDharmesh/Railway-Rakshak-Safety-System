from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import EnvironmentalZoneResponse
from ..services.environmental_service import EnvironmentalService

router = APIRouter(prefix="/environment", tags=["Environmental Risk"])

@router.get("/zones", response_model=List[EnvironmentalZoneResponse])
def get_environmental_zones(db: Session = Depends(get_db)):
    """Retrieve environmental risk telemetry, track buckling alerts, landslide, and flood risks."""
    return EnvironmentalService.get_all_zones(db)

@router.get("/zones/{zone_id}", response_model=EnvironmentalZoneResponse)
def get_zone_details(zone_id: str, db: Session = Depends(get_db)):
    """Retrieve specific environmental risk zone conditions."""
    zone = EnvironmentalService.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone
