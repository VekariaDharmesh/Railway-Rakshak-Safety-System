from sqlalchemy.orm import Session
from datetime import datetime, timezone
import hashlib
from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.all_models import (
    User, UserRole, RailwayNode, Corridor, ThreatEvent, Incident,
    ResponseTeam, DispatchOrder, DroneAsset, PredictionReport,
    EnvironmentalZone, LedgerBlock, SystemEvent
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # 1. Seed Users
        if db.query(User).count() == 0:
            users = [
                User(
                    username="admin",
                    email="admin@railrakshak.gov.in",
                    hashed_password=get_password_hash("Admin@Railway2026"),
                    full_name="National NOC Administrator",
                    role=UserRole.SUPER_ADMIN.value
                ),
                User(
                    username="cmdr.verma",
                    email="cmdr.verma@railrakshak.gov.in",
                    hashed_password=get_password_hash("Commander@2026"),
                    full_name="Cmdr. Rajesh Verma",
                    role=UserRole.COMMANDER.value
                ),
                User(
                    username="operator",
                    email="operator@railrakshak.gov.in",
                    hashed_password=get_password_hash("Operator@2026"),
                    full_name="Operations Duty Officer",
                    role=UserRole.OPERATOR.value
                ),
                User(
                    username="analyst",
                    email="analyst@railrakshak.gov.in",
                    hashed_password=get_password_hash("Analyst@2026"),
                    full_name="Cyber Threat Analyst",
                    role=UserRole.SECURITY_ANALYST.value
                )
            ]
            db.add_all(users)
            db.commit()

        # 2. Seed Railway Nodes (from reference schematic)
        if db.query(RailwayNode).count() == 0:
            nodes = [
                RailwayNode(node_id="SXR-01", name="Srinagar", zone="Northern", latitude=34.0837, longitude=74.7973, status="Normal", health_score=99.0),
                RailwayNode(node_id="DL-01", name="Delhi Central Hub", zone="Northern", latitude=28.6139, longitude=77.2090, status="Normal", health_score=98.5),
                RailwayNode(node_id="AMD-01", name="Ahmedabad", zone="Western", latitude=23.0225, longitude=72.5714, status="Caution", health_score=91.0),
                RailwayNode(node_id="MUM-01", name="Mumbai Central", zone="Western", latitude=19.0760, longitude=72.8777, status="Normal", health_score=98.0),
                RailwayNode(node_id="NGP-01", name="Nagpur Transit Hub", zone="Central", latitude=21.1458, longitude=79.0882, status="Normal", health_score=97.5),
                RailwayNode(node_id="HYD-01", name="Hyderabad", zone="South-Central", latitude=17.3850, longitude=78.4867, status="Normal", health_score=99.0),
                RailwayNode(node_id="BLR-01", name="Bengaluru Corridor", zone="South-Western", latitude=12.9716, longitude=77.5946, status="Caution", health_score=92.5),
                RailwayNode(node_id="MAS-01", name="Chennai", zone="Southern", latitude=13.0827, longitude=80.2707, status="Normal", health_score=98.2),
                RailwayNode(node_id="KOL-02", name="Kolkata", zone="Eastern", latitude=22.5726, longitude=88.3639, status="Normal", health_score=96.0)
            ]
            db.add_all(nodes)
            db.commit()

        # 3. Seed Corridors
        if db.query(Corridor).count() == 0:
            corridors = [
                Corridor(corridor_id="COR-01", name="Delhi - Srinagar Express", from_node="DL-01", to_node="SXR-01", length_km=840.0, corridor_type="Express"),
                Corridor(corridor_id="COR-02", name="Western DFC (Dadri - JNPT)", from_node="DL-01", to_node="MUM-01", length_km=1483.0, corridor_type="Freight"),
                Corridor(corridor_id="COR-03", name="Eastern DFC (Ludhiana - Dankuni)", from_node="DL-01", to_node="KOL-02", length_km=1856.0, corridor_type="Freight"),
                Corridor(corridor_id="COR-04", name="Golden Quad (Delhi - Mumbai)", from_node="DL-01", to_node="MUM-01", length_km=1384.0, corridor_type="Express"),
                Corridor(corridor_id="COR-05", name="Golden Quad (Mumbai - Chennai)", from_node="MUM-01", to_node="MAS-01", length_km=1281.0, corridor_type="Express"),
                Corridor(corridor_id="COR-06", name="Central Transverse (Mumbai - Nagpur)", from_node="MUM-01", to_node="NGP-01", length_km=830.0, corridor_type="Express"),
                Corridor(corridor_id="COR-07", name="Southern Link (Bengaluru - Chennai)", from_node="BLR-01", to_node="MAS-01", length_km=360.0, corridor_type="Express")
            ]
            db.add_all(corridors)
            db.commit()

        # 4. Seed Response Teams
        if db.query(ResponseTeam).count() == 0:
            teams = [
                ResponseTeam(team_id="SQUAD-01", name="Northern Rapid Engineering Squad", base_location="Delhi Hub", current_status="AVAILABLE", contact="Radio Ch-01", eta_minutes=12),
                ResponseTeam(team_id="SQUAD-02", name="Western DFC Track Inspection Team", base_location="Surat Bypass", current_status="AVAILABLE", contact="Radio Ch-02", eta_minutes=15),
                ResponseTeam(team_id="SQUAD-03", name="Central Joint Shear Emergency Crew", base_location="Nagpur Division", current_status="AVAILABLE", contact="Radio Ch-03", eta_minutes=18),
                ResponseTeam(team_id="SQUAD-04", name="Eastern Corridor Fast Repair Unit", base_location="Kanpur Central", current_status="AVAILABLE", contact="Radio Ch-04", eta_minutes=10)
            ]
            db.add_all(teams)
            db.commit()

        # 5. Seed Drone Fleet
        if db.query(DroneAsset).count() == 0:
            drones = [
                DroneAsset(drone_id="DR-021", callsign="UAV-RAKSHAK-01", location="Ahmedabad", latitude=23.0225, longitude=72.5714, battery_pct=84, signal_pct=98, mission="Track Inspection", camera_type="Thermal + RGB", status="ACTIVE"),
                DroneAsset(drone_id="DR-004", callsign="UAV-RAKSHAK-04", location="Delhi Central", latitude=28.6139, longitude=77.2090, battery_pct=87, signal_pct=95, mission="Acoustic Joint Patrol", camera_type="Optical Zoom 40x", status="ACTIVE"),
                DroneAsset(drone_id="DR-007", callsign="UAV-RAKSHAK-07", location="Nagpur Corridor", latitude=21.1458, longitude=79.0882, battery_pct=92, signal_pct=90, mission="Embankment Soil Sweep", camera_type="Thermal LiDAR", status="STANDBY"),
                DroneAsset(drone_id="DR-015", callsign="UAV-RAKSHAK-15", location="Kanpur km 418", latitude=26.4499, longitude=80.3319, battery_pct=76, signal_pct=94, mission="Crack Verification", camera_type="Thermal + RGB", status="MISSION")
            ]
            db.add_all(drones)
            db.commit()

        # 6. Seed Threats (Matching user screenshot)
        if db.query(ThreatEvent).count() == 0:
            threats = [
                ThreatEvent(threat_id="THR-101", severity="HIGH", location="E-DFC (DL-01) km 328.4", event="Unusual device communication - Anomalous outbound traffic detected", category="SECURITY", status="ACTIVE", score=88.0, time_str="13:37:22"),
                ThreatEvent(threat_id="THR-102", severity="MEDIUM", location="Mumbai Node CTRL-SRV-07", event="Multiple failed login attempts - Possible credential stuffing", category="SECURITY", status="MONITORING", score=72.0, time_str="13:24:10"),
                ThreatEvent(threat_id="THR-103", severity="LOW", location="Kolkata Corridor Node KB-03", event="CPU usage anomaly - Process behavior deviation", category="SYSTEM", status="RESOLVED", score=35.0, time_str="13:12:45"),
                ThreatEvent(threat_id="THR-104", severity="MEDIUM", location="Ahmedabad Node NW-EDGE-12", event="Unusual data transfer volume - Higher than baseline (3x)", category="SECURITY", status="MONITORING", score=65.0, time_str="12:58:33"),
                ThreatEvent(threat_id="THR-105", severity="LOW", location="Chennai Corridor km 612.0", event="New device detected - Unregistered IoT device", category="SECURITY", status="ACTIVE", score=40.0, time_str="12:41:19"),
                ThreatEvent(threat_id="THR-106", severity="LOW", location="Nagpur Node APP-SRV-01", event="Configuration change - Firewall rule updated", category="SYSTEM", status="RESOLVED", score=28.0, time_str="12:18:04"),
                ThreatEvent(threat_id="THR-107", severity="MEDIUM", location="Delhi Node SEC-GW-02", event="Suspicious port scan - Multiple source IPs", category="SECURITY", status="ACTIVE", score=68.0, time_str="11:53:27"),
                ThreatEvent(threat_id="THR-108", severity="LOW", location="Hyderabad Corridor km 421.7", event="Service restart detected - Non-critical service", category="OPERATION", status="RESOLVED", score=22.0, time_str="11:26:11")
            ]
            db.add_all(threats)
            db.commit()

        # 7. Seed Incidents
        if db.query(Incident).count() == 0:
            incidents = [
                Incident(
                    incident_id="INC-1042",
                    title="Anomalous Outbound Traffic on Interlocking RTU",
                    severity="HIGH",
                    status="INVESTIGATING",
                    location="E-DFC (DL-01) km 328.4",
                    corridor_id="COR-03",
                    assigned_team_id="SQUAD-01",
                    notes="Automated alert triggered by isolation forest anomaly detector. Packet burst of 14,200/s."
                ),
                Incident(
                    incident_id="INC-1041",
                    title="Vibration Harmonic Spike on Rail Joint",
                    severity="MEDIUM",
                    status="DISPATCHED",
                    location="Mumbai Western Sub-division km 42.1",
                    corridor_id="COR-04",
                    assigned_team_id="SQUAD-02",
                    notes="Acoustic sensor flagged impulse frequency deviation at 1.4kHz."
                )
            ]
            db.add_all(incidents)
            db.commit()

        # 8. Seed Dispatches
        if db.query(DispatchOrder).count() == 0:
            dispatches = [
                DispatchOrder(
                    dispatch_id="DSP-1042",
                    incident_id="INC-1042",
                    team_id="SQUAD-01",
                    priority="HIGH",
                    location="E-DFC (DL-01) km 328.4",
                    eta_minutes=12,
                    status="EN_ROUTE"
                ),
                DispatchOrder(
                    dispatch_id="DSP-1041",
                    incident_id="INC-1041",
                    team_id="SQUAD-02",
                    priority="MEDIUM",
                    location="Mumbai Western Sub-division km 42.1",
                    eta_minutes=15,
                    status="DISPATCHED"
                )
            ]
            db.add_all(dispatches)
            db.commit()

        # 9. Seed Predictions
        if db.query(PredictionReport).count() == 0:
            preds = [
                PredictionReport(
                    corridor_id="E-DFC / DL-01",
                    corridor_name="Eastern Dedicated Freight Corridor",
                    risk_level="HIGH",
                    failure_probability=0.82,
                    reasoning="Abnormal harmonic vibration (3.8g) + acoustic deviation (+18kHz) detected on joint KM 328.4",
                    recommended_action="Inspect within 2 hours"
                ),
                PredictionReport(
                    corridor_id="W-DFC / AD-12",
                    corridor_name="Western Freight - Surat to Ahmedabad",
                    risk_level="MEDIUM",
                    failure_probability=0.58,
                    reasoning="Thermal expansion gradient +14.2°C approaching rail head buckling threshold",
                    recommended_action="Schedule night inspection"
                ),
                PredictionReport(
                    corridor_id="G-QUAD / MAS-01",
                    corridor_name="Golden Quad - Chennai to Bengaluru",
                    risk_level="LOW",
                    failure_probability=0.18,
                    reasoning="Telemetry within standard baseline bounds",
                    recommended_action="Routine automated patrol"
                )
            ]
            db.add_all(preds)
            db.commit()

        # 10. Seed System Events (Matching user screenshot)
        if db.query(SystemEvent).count() == 0:
            events = [
                SystemEvent(time_str="13:40:12", category="SYSTEM", source="NOC CORE", description="Telemetry synced from 412 nodes across 25 corridors", status="SUCCESS", tab="live"),
                SystemEvent(time_str="13:38:47", category="SECURITY", source="E-DFC (DL-01)", description="Network traffic normalized after anomaly mitigation", status="RESOLVED", tab="live"),
                SystemEvent(time_str="13:36:21", category="OPERATION", source="DISPATCH", description="Patrol drone deployed to E-DFC (DL-01) [Auto]", status="ACTIVE", tab="dispatches"),
                SystemEvent(time_str="13:31:05", category="SYSTEM", source="MAP INTEL", description="GIS data refreshed - all corridors", status="SUCCESS", tab="updates"),
                SystemEvent(time_str="13:27:44", category="SECURITY", source="MUMBAI NODE", description="Multiple failed login attempts detected", status="MONITORING", tab="live")
            ]
            db.add_all(events)
            db.commit()

        # 11. Seed Environmental Zones
        if db.query(EnvironmentalZone).count() == 0:
            env_zones = [
                EnvironmentalZone(zone_name="NORTHERN ZONE", temp_celsius=32.5, rainfall_mm=2.0, flood_risk="LOW", landslide_risk="NONE", wind_kmh=14.0, visibility_m=1250, track_buckling_index=12.0, soil_saturation_pct=28.0, affected_corridors_count=0, recommended_action="Standard continuous monitoring"),
                EnvironmentalZone(zone_name="WESTERN ZONE", temp_celsius=29.0, rainfall_mm=48.0, flood_risk="HIGH", landslide_risk="MODERATE", wind_kmh=35.0, visibility_m=850, track_buckling_index=22.0, soil_saturation_pct=74.0, affected_corridors_count=3, recommended_action="Increase drainage inspection frequency"),
                EnvironmentalZone(zone_name="EASTERN ZONE", temp_celsius=31.0, rainfall_mm=18.0, flood_risk="MODERATE", landslide_risk="LOW", wind_kmh=22.0, visibility_m=1100, track_buckling_index=18.0, soil_saturation_pct=52.0, affected_corridors_count=1, recommended_action="Maintain optical track sensor sweeps")
            ]
            db.add_all(env_zones)
            db.commit()

        # 12. Seed Genesis Blockchain Blocks
        if db.query(LedgerBlock).count() == 0:
            genesis_hash = "0000000000000000000000000000000000000000000000000000000000000000"
            b1_hash = hashlib.sha256(f"1:TX-GENESIS:INITIALIZE_CORE:GENESIS:{genesis_hash}".encode('utf-8')).hexdigest()
            b2_hash = hashlib.sha256(f"2:TX-SENSORS:GRID_ARMED:NOC_CORE:{b1_hash}".encode('utf-8')).hexdigest()
            
            blocks = [
                LedgerBlock(block_height=1, transaction_id="TX-GENESIS-001", event_type="GENESIS_BLOCK", source="NOC_BOOTSTRAP", payload_hash=hashlib.sha256(b"init").hexdigest(), previous_hash=genesis_hash, current_hash=b1_hash, verified=True),
                LedgerBlock(block_height=2, transaction_id="TX-INITIAL-GRID-002", event_type="SENSOR_GRID_ARMED", source="NOC_CORE", payload_hash=hashlib.sha256(b"sensors_ok").hexdigest(), previous_hash=b1_hash, current_hash=b2_hash, verified=True)
            ]
            db.add_all(blocks)
            db.commit()

    finally:
        db.close()
