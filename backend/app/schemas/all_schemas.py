from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Standard API Envelope
class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Auth Schemas
class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

UserLoginRequest = LoginRequest

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserCreate(BaseModel):
    email: str
    username: Optional[str] = None
    password: str
    full_name: str
    role: Optional[str] = "OPERATOR"

class UserResponse(BaseModel):
    id: int
    username: Optional[str] = None
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Railway Node Schemas
class RailwayNodeResponse(BaseModel):
    id: int
    node_id: str
    name: str
    zone: str
    latitude: float
    longitude: float
    status: str
    health_score: float = 98.5
    last_heartbeat: Optional[datetime] = None

    class Config:
        from_attributes = True

class RailwayNodeDetailResponse(BaseModel):
    node_id: str
    name: str
    zone: str
    latitude: float
    longitude: float
    status: str
    corridor_id: Optional[str] = None
    threat_level: str = "NORMAL"
    cpu_load: float = 35.0
    temperature: float = 26.5
    vibration: float = 0.25
    connected_corridors: List[str] = []
    last_telemetry: Optional[datetime] = None
    recent_events: List[str] = []
    active_devices: int = 12

class CorridorResponse(BaseModel):
    id: int
    corridor_id: str
    name: str
    from_node: str
    to_node: str
    length_km: float
    corridor_type: str
    status: str
    risk_level: str

    class Config:
        from_attributes = True

# Telemetry Schemas
class TelemetryIngest(BaseModel):
    node_id: str
    cpu: Optional[float] = 35.0
    memory: Optional[float] = 55.0
    temperature: Optional[float] = 26.5
    vibration: Optional[float] = 0.25
    acoustic: Optional[float] = 45.0
    network_in: Optional[int] = 1200
    network_out: Optional[int] = 850
    timestamp: Optional[datetime] = None

TelemetryIngestRequest = TelemetryIngest

class TelemetryRecordResponse(BaseModel):
    id: int
    node_id: str
    cpu: float
    memory: float
    temperature: float
    vibration: float
    acoustic: Optional[float] = 45.0
    network_in: int
    network_out: int
    timestamp: datetime

    class Config:
        from_attributes = True

class SystemStatsResponse(BaseModel):
    network_health: float
    health_delta: str
    active_corridors: int
    total_corridors: int
    freight_trains: int
    express_trains: int
    unresolved_anomalies: int
    mean_response_time: str
    response_delta: str
    auto_dispatch_ms: int
    uptime: str
    nodes_online: int
    total_nodes: int
    telemetry_latency_ms: int
    tunnel_protocol: str
    threat_level: str
    pkts_per_sec: int

DashboardStatsResponse = SystemStatsResponse

# Incident Schemas
class IncidentCreate(BaseModel):
    title: str
    severity: str = "MEDIUM"
    location: str
    node_id: Optional[str] = None
    corridor_id: Optional[str] = None
    description: Optional[str] = None
    assigned_team_id: Optional[str] = None
    notes: Optional[str] = None

IncidentCreateRequest = IncidentCreate

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    assigned_team_id: Optional[str] = None
    notes: Optional[str] = None

IncidentStatusUpdateRequest = IncidentUpdate

class IncidentAssignRequest(BaseModel):
    assigned_to: str

class IncidentResponse(BaseModel):
    id: int
    incident_id: str
    title: str
    severity: str
    status: str
    location: str
    corridor_id: Optional[str] = None
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    assigned_team_id: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# Dispatch Schemas
class DispatchCreate(BaseModel):
    incident_id: str
    team_id: str
    priority: Optional[str] = "HIGH"
    location: str
    eta_minutes: Optional[int] = 20

DispatchCreateRequest = DispatchCreate

class DispatchUpdate(BaseModel):
    status: str
    resolution_notes: Optional[str] = None

DispatchStatusUpdateRequest = DispatchUpdate

class DispatchOrderResponse(BaseModel):
    id: int
    dispatch_id: str
    incident_id: str
    team_id: str
    priority: str
    location: str
    dispatched_at: datetime
    eta_minutes: int
    status: str
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True

class ResponseTeamResponse(BaseModel):
    id: int
    team_id: str
    name: str
    base_location: str
    current_status: str
    contact: str
    active_mission: Optional[str] = None
    eta_minutes: int

    class Config:
        from_attributes = True

# Threat Schemas
class ThreatCreate(BaseModel):
    event_type: Optional[str] = "ANOMALY"
    severity: str = "MEDIUM"
    node_id: Optional[str] = None
    corridor_id: Optional[str] = None
    location: Optional[str] = "Railway Corridor"
    event: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = "SECURITY"
    score: Optional[float] = 75.0

ThreatEventCreateRequest = ThreatCreate

class ThreatResponse(BaseModel):
    id: int
    threat_id: str
    severity: str
    location: str
    corridor_id: Optional[str] = None
    event: str
    category: str
    status: str
    score: float
    time_str: str
    timestamp: datetime
    acknowledged_by: Optional[str] = None

    class Config:
        from_attributes = True

ThreatEventResponse = ThreatResponse

# Drone Schemas
class DroneMissionAssignRequest(BaseModel):
    mission: str
    corridor_id: Optional[str] = None

class DroneTelemetryUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    battery: Optional[int] = None

class DroneAssetResponse(BaseModel):
    id: int
    drone_id: str
    callsign: str
    location: str
    latitude: float
    longitude: float
    altitude_m: float
    speed_kmh: float
    battery_pct: int
    signal_pct: int
    mission: str
    camera_type: str
    status: str

    class Config:
        from_attributes = True

# Predictive Schemas
class PredictionReportResponse(BaseModel):
    id: int
    corridor_id: str
    corridor_name: str
    risk_level: str
    failure_probability: float
    reasoning: str
    signals_json: Optional[str] = None
    recommended_action: str
    created_at: datetime

    class Config:
        from_attributes = True

# Environmental Schemas
class EnvironmentalZoneResponse(BaseModel):
    id: int
    zone_name: str
    temp_celsius: float
    rainfall_mm: float
    flood_risk: str
    landslide_risk: str
    wind_kmh: float
    visibility_m: int
    track_buckling_index: float
    soil_saturation_pct: float
    affected_corridors_count: int
    recommended_action: str
    updated_at: datetime

    class Config:
        from_attributes = True

# Ledger Schemas
class LedgerBlockResponse(BaseModel):
    id: int
    block_height: int
    transaction_id: str
    event_type: str
    source: str
    payload_hash: str
    previous_hash: str
    current_hash: str
    timestamp: datetime
    verified: bool

    class Config:
        from_attributes = True

class LedgerVerificationResult(BaseModel):
    is_valid: bool
    total_blocks: int
    verified_at: datetime
    last_block_hash: str
    broken_block_height: Optional[int] = None
    message: str

# System Event Schemas
class SystemEventCreate(BaseModel):
    category: str
    source: str
    description: str
    status: str = "SUCCESS"
    tab: Optional[str] = "live"

class SystemEventResponse(BaseModel):
    id: int
    time_str: str
    category: str
    source: str
    description: str
    status: str
    tab: str
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    user: str
    action: str
    resource: str
    resource_id: Optional[int] = None
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class PanicProtocolRequest(BaseModel):
    emergency_code: str
    reason: str

# Search Result
class SearchResultItem(BaseModel):
    type: str  # NODE, CORRIDOR, INCIDENT, THREAT, DRONE
    id: str
    title: str
    subtitle: str
    status: str
    meta: Dict[str, Any] = {}

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]
