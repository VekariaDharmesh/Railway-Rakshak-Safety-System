from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.models.all_models import Incident, ThreatEvent
from app.services.audit_service import AuditService
from app.services.ledger_service import LedgerService
from app.services.realtime_service import realtime_broadcaster

class IncidentService:
    @staticmethod
    async def create_incident(
        db: Session,
        title: str,
        severity: str = "MEDIUM",
        location: str = "Corridor",
        node_id: Optional[str] = None,
        corridor_id: Optional[str] = None,
        description: Optional[str] = None,
        username: str = "OPERATOR_ADMIN",
        assigned_team_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Incident:
        now_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
        inc_id = f"INC-{now_ts}"
        
        incident = Incident(
            incident_id=inc_id,
            title=title,
            severity=severity.upper(),
            status="NEW",
            location=location,
            corridor_id=corridor_id,
            reported_at=datetime.now(timezone.utc),
            assigned_team_id=assigned_team_id,
            notes=notes or description
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)

        # Audit Log
        AuditService.log(
            db=db,
            user=username,
            action="INCIDENT_CREATED",
            resource="incidents",
            resource_id=incident.id,
            details={"title": title, "severity": severity, "location": location}
        )

        # Ledger Block
        LedgerService.append_block(
            db=db,
            event_type="INCIDENT_CREATED",
            source=f"USER:{username}",
            payload={"incident_id": inc_id, "severity": severity, "location": location}
        )

        # Realtime Broadcast
        await realtime_broadcaster.broadcast("incident.created", {
            "incident_id": incident.incident_id,
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status,
            "location": incident.location
        })

        return incident

    @staticmethod
    async def update_incident_status(
        db: Session,
        incident_id: str,
        new_status: str,
        username: str = "OPERATOR_ADMIN",
        notes: Optional[str] = None
    ) -> Incident:
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        old_status = incident.status
        incident.status = new_status.upper()
        if notes:
            incident.notes = (incident.notes or "") + f"\n[{datetime.now().strftime('%H:%M:%S')}] {notes}"

        if new_status.upper() in ["RESOLVED", "CLOSED"] and not incident.resolved_at:
            incident.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(incident)

        AuditService.log(
            db=db,
            user=username,
            action="INCIDENT_STATUS_CHANGED",
            resource="incidents",
            resource_id=incident.id,
            details={"from_status": old_status, "to_status": new_status}
        )

        LedgerService.append_block(
            db=db,
            event_type="INCIDENT_STATUS_UPDATE",
            source=f"USER:{username}",
            payload={"incident_id": incident_id, "new_status": new_status}
        )

        await realtime_broadcaster.broadcast("incident.updated", {
            "incident_id": incident.incident_id,
            "status": incident.status
        })

        return incident

    transition_status = update_incident_status

    @staticmethod
    async def assign_incident(
        db: Session,
        incident_id: str,
        assigned_to: str,
        username: str = "OPERATOR_ADMIN"
    ) -> Incident:
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        incident.assigned_team_id = assigned_to
        incident.status = "DISPATCHED"
        db.commit()
        db.refresh(incident)

        AuditService.log(
            db=db,
            user=username,
            action="INCIDENT_ASSIGNED",
            resource="incidents",
            resource_id=incident.id,
            details={"assigned_to": assigned_to}
        )

        await realtime_broadcaster.broadcast("incident.updated", {
            "incident_id": incident.incident_id,
            "status": incident.status,
            "assigned_team_id": assigned_to
        })
        return incident

    assign_team = assign_incident

    @staticmethod
    async def create_incident_from_threat(db: Session, threat: ThreatEvent, username: str) -> Incident:
        ev_title = threat.event or "Operational Threat"
        return await IncidentService.create_incident(
            db=db,
            title=f"Escalated Threat: {ev_title}",
            severity=threat.severity,
            location=threat.location,
            corridor_id=threat.corridor_id,
            description=f"Escalated from threat {threat.threat_id}. Score: {threat.score}",
            username=username
        )
