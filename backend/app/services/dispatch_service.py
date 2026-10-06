from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
from app.models.all_models import DispatchOrder, ResponseTeam, Incident
from app.services.audit_service import AuditService
from app.services.ledger_service import LedgerService
from app.services.realtime_service import realtime_broadcaster

class DispatchService:
    @staticmethod
    async def create_dispatch(
        db: Session,
        incident_id: str,
        team_id: str,
        location: str,
        priority: str = "HIGH",
        eta_minutes: int = 20,
        username: str = "COMMANDER"
    ) -> DispatchOrder:
        now_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
        disp_id = f"DSP-{now_ts}"

        # Update Team Status
        team = db.query(ResponseTeam).filter(ResponseTeam.team_id == team_id).first()
        if team:
            team.current_status = "DISPATCHED"
            team.active_mission = f"Incident {incident_id} @ {location}"
            team.eta_minutes = eta_minutes

        # Create Dispatch Order
        order = DispatchOrder(
            dispatch_id=disp_id,
            incident_id=incident_id,
            team_id=team_id,
            priority=priority.upper(),
            location=location,
            dispatched_at=datetime.now(timezone.utc),
            eta_minutes=eta_minutes,
            status="DISPATCHED"
        )
        db.add(order)

        # Update Incident Status to DISPATCHED
        inc = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if inc:
            inc.status = "DISPATCHED"
            inc.assigned_team_id = team_id

        db.commit()
        db.refresh(order)

        AuditService.log(
            db=db,
            user=username,
            action="DISPATCH_ORDER_CREATED",
            resource="dispatches",
            resource_id=order.id,
            details={"incident_id": incident_id, "team_id": team_id, "eta": eta_minutes}
        )

        LedgerService.append_block(
            db=db,
            event_type="DISPATCH_EXECUTED",
            source=f"USER:{username}",
            payload={"dispatch_id": disp_id, "incident_id": incident_id, "team_id": team_id}
        )

        await realtime_broadcaster.broadcast("dispatch.updated", {
            "dispatch_id": order.dispatch_id,
            "incident_id": order.incident_id,
            "team_id": order.team_id,
            "status": order.status,
            "priority": order.priority
        })

        return order

    @staticmethod
    async def update_status(
        db: Session,
        order_id: Union[int, str],
        new_status: str,
        username: str = "COMMANDER",
        notes: Optional[str] = None
    ) -> DispatchOrder:
        query = db.query(DispatchOrder)
        if isinstance(order_id, int) or (isinstance(order_id, str) and order_id.isdigit()):
            order = query.filter(DispatchOrder.id == int(order_id)).first()
        else:
            order = query.filter(DispatchOrder.dispatch_id == str(order_id)).first()

        if not order:
            raise ValueError(f"Dispatch order {order_id} not found")

        old_status = order.status
        order.status = new_status.upper()
        if notes:
            order.resolution_notes = (order.resolution_notes or "") + f"\n[{datetime.now().strftime('%H:%M:%S')}] {notes}"

        # If resolved, free the team and close incident
        if new_status.upper() in ["RESOLVED", "CANCELLED"]:
            team = db.query(ResponseTeam).filter(ResponseTeam.team_id == order.team_id).first()
            if team:
                team.current_status = "AVAILABLE"
                team.active_mission = None

            inc = db.query(Incident).filter(Incident.incident_id == order.incident_id).first()
            if inc and new_status.upper() == "RESOLVED":
                inc.status = "RESOLVED"
                inc.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(order)

        AuditService.log(
            db=db,
            user=username,
            action="DISPATCH_STATUS_UPDATED",
            resource="dispatches",
            resource_id=order.id,
            details={"from": old_status, "to": new_status}
        )

        await realtime_broadcaster.broadcast("dispatch.updated", {
            "dispatch_id": order.dispatch_id,
            "status": order.status
        })

        return order

    update_dispatch_status = update_status
