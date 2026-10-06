from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import (
    DispatchOrderResponse, DispatchCreateRequest, DispatchStatusUpdateRequest, ResponseTeamResponse
)
from ..models.all_models import DispatchOrder, ResponseTeam, User
from ..services.auth_service import get_current_user, require_roles
from ..services.dispatch_service import DispatchService

router = APIRouter(prefix="/dispatch", tags=["Dispatch Center"])

@router.get("/orders", response_model=List[DispatchOrderResponse])
def list_dispatches(
    status: Optional[str] = Query(None, description="Filter by status (PENDING, EN_ROUTE, ON_SITE, RESOLVED, CANCELLED)"),
    db: Session = Depends(get_db)
):
    """List operational dispatch orders with team ETAs and live status."""
    query = db.query(DispatchOrder)
    if status:
        query = query.filter(DispatchOrder.status == status)
    return query.order_by(DispatchOrder.dispatched_at.desc()).all()

@router.post("/orders", response_model=DispatchOrderResponse, status_code=201)
async def create_dispatch_order(
    req: DispatchCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER", "OPERATOR", "DISPATCHER"]))
):
    uname = getattr(current_user, 'username', None) or current_user.email
    return await DispatchService.create_dispatch(
        db,
        incident_id=req.incident_id,
        team_id=req.team_id,
        priority=req.priority,
        location=req.location,
        username=uname,
        eta_minutes=req.eta_minutes
    )

@router.patch("/orders/{order_id}/status", response_model=DispatchOrderResponse)
async def update_dispatch_status(
    order_id: int,
    status_in: DispatchStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "COMMANDER", "OPERATOR", "DISPATCHER"]))
):
    """Update dispatch mission progress (e.g., EN_ROUTE, ON_SITE, RESOLVED)."""
    return await DispatchService.update_status(
        db,
        order_id=order_id,
        new_status=status_in.status,
        username=current_user.username
    )

@router.get("/teams", response_model=List[ResponseTeamResponse])
def list_response_teams(db: Session = Depends(get_db)):
    """Retrieve all available Rapid Response Teams, Cyber Squads, and Track Engineering crews."""
    return db.query(ResponseTeam).all()
