import os
import uvicorn
from fastapi import Request, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from app.main import app
from app.core.database import SessionLocal
from app.services.telemetry_service import TelemetryService
from app.schemas.all_schemas import TelemetryIngestRequest
from app.services.drone_service import DroneService
from app.models.all_models import ThreatEvent, SystemEvent
from app.services.realtime_service import realtime_broadcaster
from datetime import datetime, timezone

# Backward Compatibility Aliases for Simulator and Legacy Integrations
@app.post("/api/v1/sensor-data")
async def compat_sensor_data(request: Request):
    try:
        body = await request.json()
        vals = body.get("values", {})
        sensor_id = body.get("sensor_id", "DL-01")
        node_id = sensor_id.split("_")[0] if "_" in sensor_id else sensor_id
        
        packet = TelemetryIngestRequest(
            node_id=node_id,
            cpu=float(vals.get("rms_accel", 0.3) * 20),
            memory=float(vals.get("humidity", 50.0)),
            temperature=float(vals.get("temp", 26.0)),
            vibration=float(vals.get("rms_accel", 0.5)),
            acoustic=float(vals.get("acoustic_peak", 1.0)),
            network_in=1200,
            network_out=800,
            timestamp=datetime.now(timezone.utc)
        )
        db = SessionLocal()
        try:
            return await TelemetryService.ingest_packet(db, packet)
        finally:
            db.close()
    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=400)

@app.post("/api/v1/analyze-image")
async def compat_analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    return DroneService.inspect_frame_bytes(contents)

@app.post("/api/v1/events")
async def compat_create_event(request: Request):
    try:
        data = await request.json()
        db = SessionLocal()
        try:
            evt = SystemEvent(
                category=data.get("category", "OPERATION"),
                source=data.get("source", "SIMULATOR"),
                description=data.get("description", "Event recorded"),
                status=data.get("status", "ACTIVE"),
                timestamp=datetime.now(timezone.utc)
            )
            db.add(evt)
            db.commit()
            db.refresh(evt)
            await realtime_broadcaster.broadcast("event.created", {
                "id": evt.id,
                "category": evt.category,
                "source": evt.source,
                "description": evt.description,
                "status": evt.status,
                "time": evt.timestamp.strftime("%H:%M:%S")
            })
            return {"success": True, "id": evt.id}
        finally:
            db.close()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/api/v1/stats")
def compat_stats():
    db = SessionLocal()
    try:
        return TelemetryService.get_dashboard_stats(db)
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
