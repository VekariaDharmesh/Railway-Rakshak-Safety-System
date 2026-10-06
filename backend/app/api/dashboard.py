from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import DashboardStatsResponse
from ..services.telemetry_service import TelemetryService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve operational Cyber-NOC KPI stats, system state, and threat summaries."""
    return TelemetryService.get_dashboard_stats(db)
