from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import PredictionReportResponse
from ..services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Predictive AI"])

@router.get("", response_model=List[PredictionReportResponse])
def get_prediction_reports(
    risk_level: str = Query(None, description="Filter by risk (CRITICAL, HIGH, MEDIUM, LOW)"),
    db: Session = Depends(get_db)
):
    """Retrieve predictive AI corridor risk reports with failure probabilities and actionable recommendations."""
    return PredictionService.get_corridor_predictions(db, risk_level=risk_level)

@router.post("/recompute")
def trigger_prediction_recomputation(db: Session = Depends(get_db)):
    """Run model inference cycle across all corridors using latest telemetry metrics."""
    return PredictionService.recompute_all(db)
