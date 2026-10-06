from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import RailwayNodeResponse, RailwayNodeDetailResponse
from ..models.all_models import RailwayNode, Corridor, TelemetryRecord, ThreatEvent

router = APIRouter(prefix="/nodes", tags=["Railway Nodes"])

@router.get("", response_model=List[RailwayNodeResponse])
def list_nodes(
    status: Optional[str] = Query(None, description="Filter by status (Normal, Caution, Alert)"),
    db: Session = Depends(get_db)
):
    """Retrieve all railway nodes / interlocking stations."""
    query = db.query(RailwayNode)
    if status:
        query = query.filter(RailwayNode.status == status)
    return query.all()

@router.get("/{node_id}", response_model=RailwayNodeDetailResponse)
def get_node_details(node_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed operational dossier for a specific railway node."""
    node = db.query(RailwayNode).filter(RailwayNode.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    
    corridors = db.query(Corridor).filter((Corridor.from_node == node_id) | (Corridor.to_node == node_id)).all()
    connected = [c.name for c in corridors]
    
    latest_tel = (
        db.query(TelemetryRecord)
        .filter(TelemetryRecord.node_id == node_id)
        .order_by(TelemetryRecord.timestamp.desc())
        .first()
    )
    
    threats = (
        db.query(ThreatEvent)
        .filter(ThreatEvent.location.ilike(f"%{node_id}%"))
        .order_by(ThreatEvent.timestamp.desc())
        .limit(5)
        .all()
    )
    recent_events = [f"{t.severity}: {t.event}" for t in threats]
    
    return RailwayNodeDetailResponse(
        node_id=node.node_id,
        name=node.name,
        zone=node.zone,
        latitude=node.latitude,
        longitude=node.longitude,
        status=node.status,
        corridor_id=connected[0] if connected else None,
        threat_level="ELEVATED" if node.status == "Alert" else "NORMAL",
        cpu_load=latest_tel.cpu if latest_tel else 35.0,
        temperature=latest_tel.temperature if latest_tel else 26.5,
        vibration=latest_tel.vibration if latest_tel else 0.25,
        connected_corridors=connected,
        last_telemetry=latest_tel.timestamp if latest_tel else node.last_heartbeat,
        recent_events=recent_events,
        active_devices=12
    )
