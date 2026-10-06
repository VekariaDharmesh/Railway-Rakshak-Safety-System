from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    COMMANDER = "COMMANDER"
    OPERATOR = "OPERATOR"
    SECURITY_ANALYST = "SECURITY_ANALYST"
    DISPATCHER = "DISPATCHER"
    VIEWER = "VIEWER"

class IncidentStatus(str, enum.Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    DISPATCHED = "DISPATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.OPERATOR.value, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class RailwayNode(Base):
    __tablename__ = "railway_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g. DL-01, MUM-01
    name = Column(String(100), nullable=False)
    zone = Column(String(50), nullable=False)  # Northern, Western, etc.
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), default="Normal")  # Normal, Caution, Alert
    health_score = Column(Float, default=98.5)
    last_heartbeat = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Corridor(Base):
    __tablename__ = "corridors"
    
    id = Column(Integer, primary_key=True, index=True)
    corridor_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    from_node = Column(String(50), nullable=False)
    to_node = Column(String(50), nullable=False)
    length_km = Column(Float, default=150.0)
    corridor_type = Column(String(50), default="Express")  # Express, Freight, High-Speed
    status = Column(String(20), default="Operational")
    risk_level = Column(String(20), default="LOW")

class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), index=True, nullable=False)
    cpu = Column(Float, default=35.0)
    memory = Column(Float, default=55.0)
    temperature = Column(Float, default=26.5)
    vibration = Column(Float, default=0.25)
    acoustic = Column(Float, default=45.0)
    network_in = Column(Integer, default=1200)
    network_out = Column(Integer, default=850)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class ThreatEvent(Base):
    __tablename__ = "threat_events"
    
    id = Column(Integer, primary_key=True, index=True)
    threat_id = Column(String(50), unique=True, index=True, nullable=False)
    severity = Column(String(20), default="LOW", index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    location = Column(String(100), nullable=False)
    corridor_id = Column(String(50), index=True, nullable=True)
    event = Column(String(255), nullable=False)
    category = Column(String(50), default="SECURITY")  # SECURITY, SYSTEM, OPERATION, PHYSICAL_DEFECT
    status = Column(String(30), default="ACTIVE")  # ACTIVE, MONITORING, RESOLVED
    score = Column(Float, default=75.0)
    time_str = Column(String(20), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    acknowledged_by = Column(String(100), nullable=True)

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    severity = Column(String(20), default="MEDIUM", index=True)
    status = Column(String(30), default="NEW", index=True)
    location = Column(String(100), nullable=False)
    corridor_id = Column(String(50), nullable=True)
    reported_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)
    assigned_team_id = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)

class ResponseTeam(Base):
    __tablename__ = "response_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    base_location = Column(String(100), nullable=False)
    current_status = Column(String(30), default="AVAILABLE")  # AVAILABLE, DISPATCHED, ON_SITE, OFF_DUTY
    contact = Column(String(50), default="Radio Ch-04")
    active_mission = Column(String(200), nullable=True)
    eta_minutes = Column(Integer, default=15)

class DispatchOrder(Base):
    __tablename__ = "dispatch_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(String(50), unique=True, index=True, nullable=False)
    incident_id = Column(String(50), index=True, nullable=False)
    team_id = Column(String(50), nullable=False)
    priority = Column(String(20), default="HIGH")
    location = Column(String(100), nullable=False)
    dispatched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    eta_minutes = Column(Integer, default=20)
    status = Column(String(30), default="DISPATCHED")  # DISPATCHED, EN_ROUTE, ON_SITE, RESOLVED, CANCELLED
    resolution_notes = Column(Text, nullable=True)

class DroneAsset(Base):
    __tablename__ = "drone_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    drone_id = Column(String(50), unique=True, index=True, nullable=False)
    callsign = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude_m = Column(Float, default=45.0)
    speed_kmh = Column(Float, default=32.0)
    battery_pct = Column(Integer, default=85)
    signal_pct = Column(Integer, default=95)
    mission = Column(String(100), default="Track Inspection")
    camera_type = Column(String(50), default="Thermal + RGB")
    status = Column(String(30), default="ACTIVE")  # ACTIVE, STANDBY, MISSION, OFFLINE

class PredictionReport(Base):
    __tablename__ = "prediction_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    corridor_id = Column(String(50), index=True, nullable=False)
    corridor_name = Column(String(100), nullable=False)
    risk_level = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    failure_probability = Column(Float, default=0.45)
    reasoning = Column(Text, nullable=False)
    signals_json = Column(Text, nullable=True)
    recommended_action = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class EnvironmentalZone(Base):
    __tablename__ = "environmental_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_name = Column(String(100), unique=True, index=True, nullable=False)
    temp_celsius = Column(Float, default=32.0)
    rainfall_mm = Column(Float, default=5.0)
    flood_risk = Column(String(20), default="LOW")
    landslide_risk = Column(String(20), default="LOW")
    wind_kmh = Column(Float, default=18.0)
    visibility_m = Column(Integer, default=1200)
    track_buckling_index = Column(Float, default=12.0)
    soil_saturation_pct = Column(Float, default=35.0)
    affected_corridors_count = Column(Integer, default=1)
    recommended_action = Column(String(255), default="Routine monitoring")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class LedgerBlock(Base):
    __tablename__ = "ledger_blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    block_height = Column(Integer, unique=True, index=True, nullable=False)
    transaction_id = Column(String(64), unique=True, index=True, nullable=False)
    event_type = Column(String(50), nullable=False)
    source = Column(String(100), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    verified = Column(Boolean, default=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=False)
    action = Column(String(50), index=True, nullable=False)
    resource = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    metadata_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class SystemEvent(Base):
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, index=True)
    time_str = Column(String(20), nullable=False)
    category = Column(String(30), default="SYSTEM")  # SYSTEM, SECURITY, OPERATION
    source = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    status = Column(String(30), default="SUCCESS")  # SUCCESS, RESOLVED, ACTIVE, MONITORING
    tab = Column(String(20), default="live")  # live, updates, dispatches
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
