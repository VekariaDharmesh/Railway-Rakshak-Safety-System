from typing import List, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import TelemetryIngestRequest, TelemetryRecordResponse
from ..services.telemetry_service import TelemetryService
from ..models.all_models import TelemetryRecord

router = APIRouter(prefix="/telemetry", tags=["Telemetry Ingestion"])

@router.post("", status_code=201)
async def ingest_telemetry(payload: TelemetryIngestRequest, db: Session = Depends(get_db)):
    """
    Ingest live telemetry packet from interlocking nodes, wayside RTUs, or axle counters.
    Triggers anomaly scoring pipeline and broadcasts updates via SSE/WebSocket.
    """
    return await TelemetryService.ingest_packet(db, payload)

@router.get("/history", response_model=List[TelemetryRecordResponse])
def get_telemetry_history(
    node_id: Optional[str] = Query(None, description="Filter by node ID"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Retrieve historical telemetry records for auditing or operational review."""
    query = db.query(TelemetryRecord)
    if node_id:
        query = query.filter(TelemetryRecord.node_id == node_id)
    return query.order_by(TelemetryRecord.timestamp.desc()).limit(limit).all()
