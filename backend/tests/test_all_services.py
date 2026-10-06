import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine
from app.core.seeder import seed_database

# Ensure database tables and initial seed data exist for tests
Base.metadata.create_all(bind=engine)
seed_database()

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "service" in data

def test_dashboard_stats():
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "network_health" in data
    assert "active_corridors" in data
    assert "threat_level" in data

def test_railway_nodes():
    response = client.get("/api/v1/nodes")
    assert response.status_code == 200
    nodes = response.json()
    assert len(nodes) > 0
    assert any(n["node_id"] == "DL-01" for n in nodes)

def test_node_details():
    response = client.get("/api/v1/nodes/DL-01")
    assert response.status_code == 200
    details = response.json()
    assert details["node_id"] == "DL-01"
    assert "connected_corridors" in details

def test_corridors():
    response = client.get("/api/v1/corridors")
    assert response.status_code == 200
    corridors = response.json()
    assert len(corridors) > 0

def test_telemetry_ingestion():
    payload = {
        "node_id": "DL-01",
        "cpu": 45.2,
        "memory": 62.1,
        "temperature": 28.4,
        "vibration": 0.35,
        "acoustic": 42.0,
        "network_in": 1400,
        "network_out": 950
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert "record_id" in res_data
    assert res_data["node_id"] == "DL-01"

def test_threat_stream():
    response = client.get("/api/v1/threats")
    assert response.status_code == 200
    threats = response.json()
    assert isinstance(threats, list)

def test_threat_acknowledgement():
    # Fetch first threat
    threats = client.get("/api/v1/threats").json()
    if threats:
        t_id = threats[0]["threat_id"]
        ack_res = client.patch(f"/api/v1/threats/{t_id}/acknowledge")
        assert ack_res.status_code == 200
        assert ack_res.json()["status"] == "MONITORING"

def test_incident_lifecycle():
    # 1. Create Incident
    create_payload = {
        "title": "Automated Acoustic Warning Test",
        "severity": "HIGH",
        "location": "Corridor KM 102.5",
        "description": "Impulse spike registered during unit test suite"
    }
    inc_res = client.post("/api/v1/incidents", json=create_payload)
    assert inc_res.status_code == 201
    inc_data = inc_res.json()
    incident_id = inc_data["incident_id"]

    # 2. Update Status to INVESTIGATING
    update_res = client.patch(f"/api/v1/incidents/{incident_id}/status", json={"status": "INVESTIGATING", "notes": "Investigating team assigned"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "INVESTIGATING"

    # 3. Update Status to RESOLVED
    res_res = client.patch(f"/api/v1/incidents/{incident_id}/status", json={"status": "RESOLVED", "notes": "Track verified safe"})
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"

def test_dispatch_order_workflow():
    # 1. Get available teams
    teams = client.get("/api/v1/dispatch/teams").json()
    assert len(teams) > 0
    team_id = teams[0]["team_id"]

    # 2. Create dispatch order
    order_payload = {
        "incident_id": "INC-TEST-001",
        "team_id": team_id,
        "priority": "HIGH",
        "location": "E-DFC km 328.4",
        "eta_minutes": 15
    }
    order_res = client.post("/api/v1/dispatch/orders", json=order_payload)
    assert order_res.status_code == 201
    order_data = order_res.json()
    order_id = order_data["id"]

    # 3. Update dispatch status to EN_ROUTE
    up_res = client.patch(f"/api/v1/dispatch/orders/{order_id}/status", json={"status": "EN_ROUTE"})
    assert up_res.status_code == 200
    assert up_res.json()["status"] == "EN_ROUTE"

def test_drone_fleet():
    response = client.get("/api/v1/drones")
    assert response.status_code == 200
    drones = response.json()
    assert len(drones) > 0

    summary_res = client.get("/api/v1/drones/summary")
    assert summary_res.status_code == 200
    assert "total_drones" in summary_res.json()

def test_predictive_ai_inference():
    response = client.get("/api/v1/predictions")
    assert response.status_code == 200
    preds = response.json()
    assert len(preds) > 0
    assert "failure_probability" in preds[0]

def test_environmental_zones():
    response = client.get("/api/v1/environment/zones")
    assert response.status_code == 200
    zones = response.json()
    assert len(zones) > 0

def test_blockchain_ledger_verification():
    # 1. Get blocks
    blocks_res = client.get("/api/v1/ledger/blocks")
    assert blocks_res.status_code == 200
    blocks = blocks_res.json()
    assert len(blocks) >= 2

    # 2. Cryptographically verify ledger chain integrity
    verify_res = client.post("/api/v1/ledger/verify")
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["is_valid"] is True
    assert "All" in verify_data["message"]

def test_command_search():
    res = client.get("/api/v1/search?q=DL-01")
    assert res.status_code == 200
    results = res.json()
    assert len(results) > 0
    assert any(r["id"] == "DL-01" for r in results)

def test_system_status():
    res = client.get("/api/v1/system/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["OPERATIONAL", "PANIC_LOCKDOWN"]
    assert "services" in data
