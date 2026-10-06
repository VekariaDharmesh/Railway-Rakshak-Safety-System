from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import ThreatEventResponse, ThreatEventCreateRequest
from ..models.all_models import ThreatEvent, User
from ..services.auth_service import get_current_user, require_roles
from ..services.audit_service import AuditService
from ..services.realtime_service import realtime_broadcaster
from ..services.incident_service import IncidentService
from datetime import datetime, timezone

router = APIRouter(prefix="/threats", tags=["Threats & Anomalies"])

@router.get("", response_model=List[ThreatEventResponse])
def list_threats(
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, MONITORING, RESOLVED)"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve operational threat & anomaly stream."""
    query = db.query(ThreatEvent)
    if severity:
        query = query.filter(ThreatEvent.severity == severity.upper())
    if status:
        query = query.filter(ThreatEvent.status == status.upper())
    return query.order_by(ThreatEvent.timestamp.desc()).limit(limit).all()

@router.post("", response_model=ThreatEventResponse, status_code=201)
async def create_threat(
    threat_in: ThreatEventCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER", "SECURITY_ANALYST"]))
):
    """Manually flag or log a threat event from Cyber-NOC intelligence feeds."""
    now = datetime.now(timezone.utc)
    threat_id = f"THR-{int(now.timestamp()*1000)}"
    ev_desc = threat_in.event or threat_in.description or "Operational anomaly flagged"
    loc = threat_in.location or (f"Node {threat_in.node_id}" if threat_in.node_id else "Network Corridor")

    threat = ThreatEvent(
        threat_id=threat_id,
        severity=threat_in.severity.upper(),
        location=loc,
        corridor_id=threat_in.corridor_id,
        event=ev_desc,
        category=threat_in.category or "SECURITY",
        status="ACTIVE",
        score=threat_in.score or 75.0,
        time_str=now.strftime("%H:%M:%S"),
        timestamp=now
    )
    db.add(threat)
    db.commit()
    db.refresh(threat)

    AuditService.log(
        db,
        user=current_user.username,
        action="THREAT_MANUALLY_CREATED",
        resource="threat_events",
        resource_id=threat.id,
        details={"severity": threat.severity, "threat_id": threat.threat_id}
    )

    await realtime_broadcaster.broadcast("threat.created", {
        "id": threat.id,
        "threat_id": threat.threat_id,
        "severity": threat.severity,
        "location": threat.location,
        "event": threat.event,
        "category": threat.category,
        "status": threat.status,
        "time": threat.time_str,
        "timestamp": threat.timestamp.isoformat()
    })

    return threat

@router.patch("/{threat_id}/acknowledge", response_model=ThreatEventResponse)
async def acknowledge_threat(
    threat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge an active threat and switch status to MONITORING."""
    threat = db.query(ThreatEvent).filter((ThreatEvent.threat_id == threat_id) | (ThreatEvent.id == (int(threat_id) if threat_id.isdigit() else -1))).first()
    if not threat:
        raise HTTPException(status_code=404, detail=f"Threat {threat_id} not found")

    uname = getattr(current_user, 'username', None) or current_user.email
    threat.status = "MONITORING"
    threat.acknowledged_by = uname
    db.commit()
    db.refresh(threat)

    AuditService.log(
        db,
        user=uname,
        action="THREAT_ACKNOWLEDGED",
        resource="threat_events",
        resource_id=threat.id
    )

    await realtime_broadcaster.broadcast("threat.updated", {
        "threat_id": threat.threat_id,
        "status": threat.status
    })

    return threat

@router.post("/{threat_id}/escalate-to-incident")
async def escalate_threat(
    threat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER", "OPERATOR", "SECURITY_ANALYST"]))
):
    """Escalate a confirmed threat into a managed operational Incident."""
    threat = db.query(ThreatEvent).filter((ThreatEvent.threat_id == threat_id) | (ThreatEvent.id == (int(threat_id) if threat_id.isdigit() else -1))).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")

    incident = await IncidentService.create_incident_from_threat(db, threat, current_user.username)
    return {"message": "Threat escalated to incident", "incident_id": incident.incident_id}
