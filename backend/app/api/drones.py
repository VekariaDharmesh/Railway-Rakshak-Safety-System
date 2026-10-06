from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import DroneAssetResponse, DroneMissionAssignRequest, DroneTelemetryUpdate
from ..services.drone_service import DroneService
from ..models.all_models import DroneAsset, User
from ..services.auth_service import require_roles

router = APIRouter(prefix="/drones", tags=["Drone Fleet & Computer Vision"])

@router.get("", response_model=List[DroneAssetResponse])
def list_drones(
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, PATROLLING, CHARGING, OFFLINE)"),
    db: Session = Depends(get_db)
):
    """Retrieve full drone fleet status, battery, coordinates, and active missions."""
    return DroneService.get_fleet(db, status=status)

@router.get("/summary")
def get_fleet_summary(db: Session = Depends(get_db)):
    """Fleet status count summary (active, available, offline, patrolling)."""
    return DroneService.get_summary(db)

@router.get("/{drone_id}", response_model=DroneAssetResponse)
def get_drone(drone_id: str, db: Session = Depends(get_db)):
    """Retrieve specific drone real-time status and sensor feed telemetry."""
    drone = db.query(DroneAsset).filter(DroneAsset.drone_id == drone_id).first()
    if not drone:
        raise HTTPException(status_code=404, detail=f"Drone {drone_id} not found")
    return drone

@router.post("/{drone_id}/mission", response_model=DroneAssetResponse)
async def assign_mission(
    drone_id: str,
    req: DroneMissionAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER", "OPERATOR"]))
):
    """Assign an aerial patrol or CV inspection mission to a drone."""
    return await DroneService.assign_mission(db, drone_id, req.mission, req.corridor_id)

@router.post("/{drone_id}/telemetry")
async def update_drone_telemetry(
    drone_id: str,
    req: DroneTelemetryUpdate,
    db: Session = Depends(get_db)
):
    """Simulated or live telemetry ingestion from drone flight controller."""
    return await DroneService.update_telemetry(db, drone_id, req.dict())

@router.post("/cv/inspect-frame")
async def inspect_drone_frame(file: UploadFile = File(...)):
    """
    Run Computer Vision inspection on uploaded aerial camera frame or infrared snapshot.
    Detects track structural cracks, trespassers, obstacles, and fire/smoke anomalies.
    """
    contents = await file.read()
    return DroneService.inspect_frame_bytes(contents)
