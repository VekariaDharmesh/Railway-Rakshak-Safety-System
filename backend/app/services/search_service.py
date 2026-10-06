from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.all_models import RailwayNode, Corridor, Incident, ThreatEvent, DroneAsset

class SearchService:
    @staticmethod
    def query(db: Session, term: str) -> List[Dict[str, Any]]:
        q = term.strip().lower()
        if not q:
            return []

        results = []

        # 1. Search Railway Nodes
        nodes = db.query(RailwayNode).all()
        for n in nodes:
            if q in n.node_id.lower() or q in n.name.lower() or (n.zone and q in n.zone.lower()):
                results.append({
                    "type": "NODE",
                    "id": n.node_id,
                    "title": f"Node {n.node_id} ({n.name})",
                    "subtitle": f"Zone: {n.zone} • Lat/Lng: {n.latitude:.2f}, {n.longitude:.2f}",
                    "status": n.status,
                    "meta": {"lat": n.latitude, "lng": n.longitude, "health": n.health_score}
                })

        # 2. Search Corridors
        corridors = db.query(Corridor).all()
        for c in corridors:
            if q in c.corridor_id.lower() or q in c.name.lower():
                results.append({
                    "type": "CORRIDOR",
                    "id": c.corridor_id,
                    "title": f"Corridor {c.corridor_id}",
                    "subtitle": f"{c.name} ({c.from_node} ➔ {c.to_node})",
                    "status": c.status,
                    "meta": {"length_km": c.length_km, "risk": c.risk_level}
                })

        # 3. Search Incidents
        incidents = db.query(Incident).all()
        for inc in incidents:
            if q in inc.incident_id.lower() or q in inc.title.lower() or q in inc.location.lower() or q in inc.severity.lower():
                results.append({
                    "type": "INCIDENT",
                    "id": inc.incident_id,
                    "title": f"{inc.incident_id}: {inc.title}",
                    "subtitle": f"Location: {inc.location} • Severity: {inc.severity}",
                    "status": inc.status,
                    "meta": {"severity": inc.severity, "assigned_team": inc.assigned_team_id}
                })

        # 4. Search Threats
        threats = db.query(ThreatEvent).all()
        for t in threats:
            t_event = t.event or t.description or "Threat"
            if q in t.threat_id.lower() or q in t_event.lower() or q in t.location.lower() or q in t.severity.lower():
                results.append({
                    "type": "THREAT",
                    "id": t.threat_id,
                    "title": f"{t.threat_id} [{t.severity}]",
                    "subtitle": f"{t_event} @ {t.location}",
                    "status": t.status,
                    "meta": {"score": t.score, "time": t.time_str}
                })

        # 5. Search Drones
        drones = db.query(DroneAsset).all()
        for d in drones:
            if q in d.drone_id.lower() or q in d.callsign.lower() or q in d.location.lower() or q in d.mission.lower():
                results.append({
                    "type": "DRONE",
                    "id": d.drone_id,
                    "title": f"UAV {d.drone_id} ({d.callsign})",
                    "subtitle": f"{d.location} • Battery: {d.battery_pct}% • Mission: {d.mission}",
                    "status": d.status,
                    "meta": {"battery": d.battery_pct, "altitude": d.altitude_m}
                })

        return results

    @staticmethod
    def search(db: Session, query_str: str, limit: int = 20) -> List[Dict[str, Any]]:
        return SearchService.query(db, query_str)[:limit]
