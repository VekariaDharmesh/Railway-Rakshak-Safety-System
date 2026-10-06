from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import (
    IncidentResponse, IncidentCreateRequest, IncidentStatusUpdateRequest, IncidentAssignRequest
)
from ..models.all_models import Incident, User
from ..services.auth_service import get_current_user, require_roles
from ..services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidents Lifecycle"])

@router.get("", response_model=List[IncidentResponse])
def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status (NEW, ACKNOWLEDGED, INVESTIGATING, DISPATCHED, IN_PROGRESS, RESOLVED, CLOSED)"),
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    db: Session = Depends(get_db)
):
    """Retrieve all operational incidents."""
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    return query.order_by(Incident.reported_at.desc()).all()

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve full incident details."""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident

@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(
    req: IncidentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER", "OPERATOR", "SECURITY_ANALYST"]))
):
    uname = getattr(current_user, 'username', None) or current_user.email
    return await IncidentService.create_incident(
        db,
        title=req.title,
        severity=req.severity,
        location=req.location,
        node_id=req.node_id,
        corridor_id=req.corridor_id,
        description=req.description,
        username=uname
    )

@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: str,
    status_in: IncidentStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER", "OPERATOR", "SECURITY_ANALYST", "DISPATCHER"]))
):
    """Advance or update incident lifecycle status (creates audit log and ledger block if resolved)."""
    uname = getattr(current_user, 'username', None) or current_user.email
    return await IncidentService.update_incident_status(
        db,
        incident_id=incident_id,
        new_status=status_in.status,
        username=uname,
        notes=status_in.notes
    )

@router.patch("/{incident_id}/assign", response_model=IncidentResponse)
async def assign_incident(
    incident_id: str,
    assign_in: IncidentAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER", "OPERATOR", "DISPATCHER"]))
):
    """Assign incident to an operator or specialized response team."""
    return await IncidentService.assign_incident(
        db,
        incident_id=incident_id,
        assigned_to=assign_in.assigned_to,
        username=current_user.username
    )
