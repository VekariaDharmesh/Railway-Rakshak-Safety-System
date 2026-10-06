import asyncio
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, BackgroundTasks, Request, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import numpy as np
import os

from ml.anomaly_detection import EnsembleAnomalyDetector
from ml.vision import analyze_track_image

app = FastAPI(title="Railway Rakshak Cyber-NOC Defense System API", version="4.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
clients: List[asyncio.Queue] = []
recent_alerts: List[Dict[str, Any]] = []
track_data: Dict[str, Any] = {}
blockchain_tickets: List[Dict[str, Any]] = []

# Initial Threat Stream (as seen in Cyber-NOC design)
threat_stream: List[Dict[str, Any]] = [
    {
        "id": "THR-001",
        "severity": "HIGH",
        "time": "13:37:22",
        "location": "E-DFC (DL-01) km 328.4",
        "event": "Unusual device communication - Anomalous outbound traffic detected",
        "category": "SECURITY"
    },
    {
        "id": "THR-002",
        "severity": "MEDIUM",
        "time": "13:24:10",
        "location": "Mumbai Node CTRL-SRV-07",
        "event": "Multiple failed login attempts - Possible credential stuffing",
        "category": "SECURITY"
    },
    {
        "id": "THR-003",
        "severity": "LOW",
        "time": "13:12:45",
        "location": "Kolkata Corridor Node KB-03",
        "event": "CPU usage anomaly - Process behavior deviation",
        "category": "SYSTEM"
    },
    {
        "id": "THR-004",
        "severity": "MEDIUM",
        "time": "12:58:33",
        "location": "Ahmedabad Node NW-EDGE-12",
        "event": "Unusual data transfer volume - Higher than baseline (3x)",
        "category": "SECURITY"
    },
    {
        "id": "THR-005",
        "severity": "LOW",
        "time": "12:41:19",
        "location": "Chennai Corridor km 612.0",
        "event": "New device detected - Unregistered IoT device",
        "category": "SECURITY"
    },
    {
        "id": "THR-006",
        "severity": "LOW",
        "time": "12:18:04",
        "location": "Nagpur Node APP-SRV-01",
        "event": "Configuration change - Firewall rule updated",
        "category": "SYSTEM"
    },
    {
        "id": "THR-007",
        "severity": "MEDIUM",
        "time": "11:53:27",
        "location": "Delhi Node SEC-GW-02",
        "event": "Suspicious port scan - Multiple source IPs",
        "category": "SECURITY"
    },
    {
        "id": "THR-008",
        "severity": "LOW",
        "time": "11:26:11",
        "location": "Hyderabad Corridor km 421.7",
        "event": "Service restart detected - Non-critical service",
        "category": "OPERATION"
    }
]

# Initial Operational Status & System Events
system_events: List[Dict[str, Any]] = [
    {
        "id": "EVT-001",
        "time": "13:40:12",
        "category": "SYSTEM",
        "source": "NOC CORE",
        "description": "Telemetry synced from 412 nodes across 25 corridors",
        "status": "SUCCESS",
        "tab": "live"
    },
    {
        "id": "EVT-002",
        "time": "13:38:47",
        "category": "SECURITY",
        "source": "E-DFC (DL-01)",
        "description": "Network traffic normalized after anomaly mitigation",
        "status": "RESOLVED",
        "tab": "live"
    },
    {
        "id": "EVT-003",
        "time": "13:36:21",
        "category": "OPERATION",
        "source": "DISPATCH",
        "description": "Patrol drone deployed to E-DFC (DL-01) [Auto]",
        "status": "ACTIVE",
        "tab": "dispatches"
    },
    {
        "id": "EVT-004",
        "time": "13:31:05",
        "category": "SYSTEM",
        "source": "MAP INTEL",
        "description": "GIS data refreshed - all corridors",
        "status": "SUCCESS",
        "tab": "updates"
    },
    {
        "id": "EVT-005",
        "time": "13:27:44",
        "category": "SECURITY",
        "source": "MUMBAI NODE",
        "description": "Multiple failed login attempts detected",
        "status": "MONITORING",
        "tab": "live"
    }
]

# Corridor Intelligence Nodes (25 nodes across key routes)
corridor_nodes: Dict[str, Any] = {
    "SRINAGAR": {"lat": 34.0837, "lng": 74.7973, "status": "Normal", "type": "Hub"},
    "DELHI": {"lat": 28.6139, "lng": 77.2090, "status": "Normal", "type": "Central_Hub"},
    "AHMEDABAD": {"lat": 23.0225, "lng": 72.5714, "status": "Caution", "type": "Freight_Hub"},
    "MUMBAI": {"lat": 19.0760, "lng": 72.8777, "status": "Normal", "type": "Terminal"},
    "NAGPUR": {"lat": 21.1458, "lng": 79.0882, "status": "Normal", "type": "Transit_Jct"},
    "HYDERABAD": {"lat": 17.3850, "lng": 78.4867, "status": "Normal", "type": "Zonal_Hub"},
    "BENGALURU": {"lat": 12.9716, "lng": 77.5946, "status": "Caution", "type": "Tech_Corridor"},
    "CHENNAI": {"lat": 13.0827, "lng": 80.2707, "status": "Normal", "type": "Coastal_Hub"},
    "KOLKATA": {"lat": 22.5726, "lng": 88.3639, "status": "Normal", "type": "Eastern_Terminal"}
}

# Real-time System Statistics
system_stats: Dict[str, Any] = {
    "network_health": 98.4,
    "health_delta": "+0.2%",
    "active_corridors": 25,
    "total_corridors": 25,
    "freight_trains": 2840,
    "express_trains": 412,
    "unresolved_anomalies": 0,
    "mean_response_time": "4.2m",
    "response_delta": "-18%",
    "auto_dispatch_ms": 140,
    "uptime": "99.991%",
    "nodes_online": 412,
    "total_nodes": 412,
    "telemetry_latency_ms": 12,
    "tunnel_protocol": "AES-256 GCM",
    "threat_level": "NORMAL",
    "pkts_per_sec": 1240
}

detector = EnsembleAnomalyDetector()

# Pydantic Schemas
class SensorData(BaseModel):
    sensor_id: str
    timestamp: float
    values: Dict[str, Any]
    health: str
    location: Optional[Dict[str, float]] = None

class TicketRequest(BaseModel):
    sensor_id: str
    location: str

class ThreatItem(BaseModel):
    severity: str
    location: str
    event: str
    category: Optional[str] = "SECURITY"

class SystemEventItem(BaseModel):
    category: str
    source: str
    description: str
    status: str
    tab: Optional[str] = "live"

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

async def broadcast_event(event_type: str, data: Any):
    message = json.dumps({"type": event_type, "data": data})
    for client in clients:
        await client.put(message)

# Process Sensor Ingestion
async def process_sensor_data(data: SensorData):
    vals = data.values
    vibration_features = np.array([
        vals.get("peak_freq", 200),
        vals.get("rms_accel", 0.3),
        vals.get("crest_factor", 2.5),
        vals.get("band1", 0.1),
        vals.get("band2", 0.1),
        vals.get("band3", 0.1)
    ])
    
    acoustic_features = np.array([
        vals.get("acoustic_peak", 1.0),
        vals.get("acoustic_rms", 0.5)
    ])
    
    current_temp = vals.get("temp", 25.0)
    baseline_temp = 25.0
    
    result = detector.predict(vibration_features, acoustic_features, current_temp, baseline_temp)
    
    track_data[data.sensor_id] = {
        "last_update": data.timestamp,
        "score": result["final_score"],
        "status": "NORMAL" if result["final_score"] < 60 else "ALERT",
        "location": data.location,
        "weather": {
            "temp": vals.get("temp", 25.0),
            "condition": vals.get("weather_condition", "Clear"),
            "humidity": vals.get("humidity", 50.0)
        },
        "forecast_7_day": result.get("forecast_7_day", 0.0),
        "forecast_30_day": result.get("forecast_30_day", 0.0)
    }
    
    if result["final_score"] > 60:
        alert = {
            "id": f"ALT-{int(data.timestamp * 1000)}",
            "timestamp": datetime.fromtimestamp(data.timestamp).isoformat(),
            "sensor_id": data.sensor_id,
            "location": f"KM {np.random.randint(100, 200)}.{np.random.randint(0, 9)}",
            "severity": "EMERGENCY" if result["final_score"] > 80 else "SCHEDULE_INSPECTION",
            "score": result["final_score"],
            "details": result
        }
        recent_alerts.insert(0, alert)
        if len(recent_alerts) > 50:
            recent_alerts.pop()
            
        system_stats["unresolved_anomalies"] = len([a for a in recent_alerts if a.get("severity") == "EMERGENCY"])
        system_stats["threat_level"] = "ELEVATED" if system_stats["unresolved_anomalies"] > 0 else "NORMAL"
        
        # Also create a threat stream item
        new_threat = {
            "id": f"THR-{int(time.time() * 1000)}",
            "severity": "HIGH" if result["final_score"] > 80 else "MEDIUM",
            "time": datetime.now().strftime("%H:%M:%S"),
            "location": f"{data.sensor_id} ({alert['location']})",
            "event": f"Micro-fracture detected - Vibration score {result['final_score']:.1f}",
            "category": "PHYSICAL_DEFECT"
        }
        threat_stream.insert(0, new_threat)
        if len(threat_stream) > 40:
            threat_stream.pop()

        await broadcast_event("new_alert", alert)
        await broadcast_event("new_threat", new_threat)
        await broadcast_event("stats_update", system_stats)
        
    await broadcast_event("track_update", track_data)

@app.post("/api/v1/sensor-data")
async def receive_sensor_data(data: SensorData, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_sensor_data, data)
    return {"status": "accepted"}

# REST Endpoints for UI Components

@app.get("/api/v1/system-stats")
async def get_system_stats():
    system_stats["unresolved_anomalies"] = len([a for a in recent_alerts if a.get("severity") == "EMERGENCY"])
    return system_stats

@app.get("/api/v1/threats")
async def get_threats(severity: Optional[str] = None):
    if severity and severity.upper() != "ALL":
        return [t for t in threat_stream if t["severity"].upper() == severity.upper()]
    return threat_stream

@app.post("/api/v1/threats")
async def add_threat(item: ThreatItem):
    new_t = {
        "id": f"THR-{int(time.time()*1000)}",
        "severity": item.severity.upper(),
        "time": datetime.now().strftime("%H:%M:%S"),
        "location": item.location,
        "event": item.event,
        "category": item.category or "SECURITY"
    }
    threat_stream.insert(0, new_t)
    await broadcast_event("new_threat", new_t)
    return new_t

@app.get("/api/v1/events")
async def get_system_events(
    tab: Optional[str] = None,
    category: Optional[str] = None
):
    results = system_events
    if tab and tab.lower() != "all":
        results = [e for e in results if e.get("tab") == tab.lower()]
    if category and category.upper() != "ALL":
        results = [e for e in results if e.get("category") == category.upper()]
    return results

@app.post("/api/v1/events")
async def log_system_event(item: SystemEventItem):
    new_evt = {
        "id": f"EVT-{int(time.time()*1000)}",
        "time": datetime.now().strftime("%H:%M:%S"),
        "category": item.category.upper(),
        "source": item.source,
        "description": item.description,
        "status": item.status.upper(),
        "tab": item.tab or "live"
    }
    system_events.insert(0, new_evt)
    if len(system_events) > 50:
        system_events.pop()
    await broadcast_event("new_system_event", new_evt)
    return new_evt

@app.post("/api/v1/panic")
async def trigger_panic_protocol():
    system_stats["threat_level"] = "CRITICAL"
    timestamp = datetime.now().strftime("%H:%M:%S")
    panic_event = {
        "id": f"EVT-PANIC-{int(time.time()*1000)}",
        "time": timestamp,
        "category": "SECURITY",
        "source": "COMMANDER EMERGENCY",
        "description": "PANIC PROTOCOL ENGAGED: Emergency speed limit 30 km/h applied across national network",
        "status": "ACTIVE",
        "tab": "live"
    }
    system_events.insert(0, panic_event)
    
    panic_threat = {
        "id": f"THR-PANIC-{int(time.time()*1000)}",
        "severity": "HIGH",
        "time": timestamp,
        "location": "ALL NATIONAL CORRIDORS",
        "event": "Manual panic protocol executed by Command Center",
        "category": "EMERGENCY"
    }
    threat_stream.insert(0, panic_threat)
    
    await broadcast_event("panic_triggered", {
        "message": "Emergency response active. Speed limit 30 km/h enforced.",
        "stats": system_stats,
        "event": panic_event,
        "threat": panic_threat
    })
    return {"status": "panic_engaged", "threat_level": "CRITICAL", "event": panic_event}

@app.get("/api/v1/corridors")
async def get_corridors():
    return {
        "nodes": corridor_nodes,
        "routes": [
            {"from": "DELHI", "to": "SRINAGAR", "type": "Express"},
            {"from": "DELHI", "to": "AHMEDABAD", "type": "Freight"},
            {"from": "AHMEDABAD", "to": "MUMBAI", "type": "Express"},
            {"from": "DELHI", "to": "KOLKATA", "type": "Express"},
            {"from": "DELHI", "to": "NAGPUR", "type": "Freight"},
            {"from": "NAGPUR", "to": "HYDERABAD", "type": "Freight"},
            {"from": "HYDERABAD", "to": "BENGALURU", "type": "Express"},
            {"from": "BENGALURU", "to": "CHENNAI", "type": "Express"},
            {"from": "MUMBAI", "to": "NAGPUR", "type": "Freight"},
            {"from": "KOLKATA", "to": "CHENNAI", "type": "Freight"}
        ]
    }

@app.post("/api/v1/tickets")
async def create_ticket(req: TicketRequest):
    ticket_id = f"TKT-{int(time.time() * 1000)}"
    timestamp = datetime.now().isoformat()
    
    prev_hash = blockchain_tickets[0]["hash"] if blockchain_tickets else "0000000000000000000000000000000000000000000000000000000000000000"
    
    data_to_hash = f"{ticket_id}{req.sensor_id}{req.location}{timestamp}{prev_hash}"
    current_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
    
    ticket = {
        "id": ticket_id,
        "sensor_id": req.sensor_id,
        "location": req.location,
        "timestamp": timestamp,
        "status": "Dispatched",
        "prev_hash": prev_hash,
        "hash": current_hash
    }
    
    blockchain_tickets.insert(0, ticket)
    
    # Also log in system events
    evt = {
        "id": f"EVT-DISP-{int(time.time()*1000)}",
        "time": datetime.now().strftime("%H:%M:%S"),
        "category": "OPERATION",
        "source": "RAPID SQUAD DISPATCH",
        "description": f"Field inspection crew dispatched to {req.location} (Ticket {ticket_id})",
        "status": "ACTIVE",
        "tab": "dispatches"
    }
    system_events.insert(0, evt)
    
    await broadcast_event("new_ticket", ticket)
    await broadcast_event("new_system_event", evt)
    return ticket

@app.post("/api/v1/analyze-image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    result = analyze_track_image(contents)
    return result

# Real-time Server-Sent Events (SSE) Stream
@app.get("/api/v1/stream")
async def message_stream(request: Request):
    queue = asyncio.Queue()
    clients.append(queue)
    
    async def event_generator():
        try:
            # Send initial full payload
            yield {
                "event": "message",
                "data": json.dumps({
                    "type": "init", 
                    "data": {
                        "stats": system_stats,
                        "tracks": track_data, 
                        "alerts": recent_alerts,
                        "threats": threat_stream,
                        "events": system_events,
                        "corridors": corridor_nodes,
                        "tickets": blockchain_tickets
                    }
                })
            }
            while True:
                if await request.is_disconnected():
                    break
                message = await queue.get()
                yield {
                    "event": "message",
                    "data": message
                }
        finally:
            if queue in clients:
                clients.remove(queue)
            
    return EventSourceResponse(event_generator())
