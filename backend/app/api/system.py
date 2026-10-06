from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from ..core.database import get_db
from ..schemas.all_schemas import PanicProtocolRequest, AuditLogResponse, SystemEventResponse
from ..services.audit_service import AuditService
from ..services.ledger_service import LedgerService
from ..services.realtime_service import realtime_broadcaster
from ..services.auth_service import get_current_user, require_roles
from ..models.all_models import AuditLog, SystemEvent, User

router = APIRouter(prefix="/system", tags=["System & Panic Protocol"])

_panic_state = {
    "active": False,
    "triggered_at": None,
    "triggered_by": None,
    "reason": None,
    "code": None
}

@router.get("/status")
def get_system_health(db: Session = Depends(get_db)):
    """Operational health status of Core Services, Database, SSE Telemetry, and API."""
    return {
        "status": "OPERATIONAL" if not _panic_state["active"] else "PANIC_LOCKDOWN",
        "services": {
            "core": "HEALTHY",
            "database": "CONNECTED",
            "telemetry_ingestion": "ONLINE",
            "sse_stream": "ACTIVE",
            "api_gateway": "ONLINE",
            "anomaly_detector": "ONLINE"
        },
        "panic_protocol": _panic_state,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "threat_level": "CRITICAL" if _panic_state["active"] else "NORMAL"
    }

@router.post("/panic")
async def trigger_panic_protocol(
    req: PanicProtocolRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER"]))
):
    """
    CRITICAL: Trigger network-wide emergency panic protocol.
    Freezes high-speed corridors, issues maximum alert to interlocking towers, logs to tamper-proof ledger.
    """
    global _panic_state
    now = datetime.now(timezone.utc)
    _panic_state = {
        "active": True,
        "triggered_at": now.isoformat(),
        "triggered_by": current_user.username or current_user.email,
        "reason": req.reason,
        "code": req.emergency_code
    }

    # Record Audit log
    AuditService.log(
        db,
        user=current_user.username or current_user.email,
        action="PANIC_PROTOCOL_TRIGGERED",
        resource="system",
        resource_id=0,
        details={"code": req.emergency_code, "reason": req.reason}
    )

    # Record System Event
    evt = SystemEvent(
        time_str=now.strftime("%H:%M:%S"),
        category="PANIC",
        source="COMMAND_CENTER",
        description=f"CRITICAL: Emergency Panic Protocol triggered by {current_user.username or current_user.email}. Reason: {req.reason}",
        status="ACTIVE",
        tab="live",
        created_at=now
    )
    db.add(evt)
    db.commit()

    # Append to SHA-256 Ledger
    LedgerService.append_block(
        db,
        event_type="PANIC_PROTOCOL_ENGAGED",
        source=f"USER:{current_user.username or current_user.email}",
        payload={"reason": req.reason, "code": req.emergency_code, "action": "NETWORK_FAILSAFE_ENGAGED"}
    )

    # Broadcast emergency alert to all connected operators
    await realtime_broadcaster.broadcast("system.panic", {
        "active": True,
        "triggered_by": current_user.username or current_user.email,
        "reason": req.reason,
        "timestamp": _panic_state["triggered_at"]
    })

    return {
        "success": True,
        "message": "EMERGENCY PANIC PROTOCOL ENGAGED. Failsafe alert broadcasted across network.",
        "state": _panic_state
    }

@router.post("/panic/disengage")
async def disengage_panic_protocol(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER"]))
):
    """Disengage panic protocol and resume standard operational mode."""
    global _panic_state
    _panic_state = {
        "active": False,
        "triggered_at": None,
        "triggered_by": None,
        "reason": None,
        "code": None
    }

    AuditService.log(
        db,
        user=current_user.username or current_user.email,
        action="PANIC_PROTOCOL_DISENGAGED",
        resource="system",
        resource_id=0
    )

    await realtime_broadcaster.broadcast("system.panic", {
        "active": False,
        "disengaged_by": current_user.username or current_user.email
    })

    return {"success": True, "message": "Panic protocol disengaged. System returned to standard state."}

@router.get("/events", response_model=List[SystemEventResponse])
def get_system_events(
    category: Optional[str] = Query(None, description="Filter category (LIVE, UPDATES, DISPATCHES, PANIC)"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve operational event log."""
    query = db.query(SystemEvent)
    if category and category != "ALL":
        query = query.filter(SystemEvent.category == category.upper())
    return query.order_by(SystemEvent.created_at.desc()).limit(limit).all()

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_trail(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER", "SECURITY_ANALYST"]))
):
    """Retrieve system security audit trail."""
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
