import asyncio
import random
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models.all_models import RailwayNode, DroneAsset, EnvironmentalZone
from ..services.telemetry_service import TelemetryService
from ..schemas.all_schemas import TelemetryIngestRequest

logger = logging.getLogger(__name__)

class TelemetrySimulator:
    def __init__(self, interval_seconds: float = 3.0):
        self.interval = interval_seconds
        self.is_running = False

    async def run(self):
        self.is_running = True
        logger.info("Railway Rakshak Telemetry Simulator started.")
        while self.is_running:
            try:
                db: Session = SessionLocal()
                try:
                    # 1. Simulate Node Telemetry
                    nodes = db.query(RailwayNode).all()
                    for node in nodes:
                        is_spike = random.random() < 0.03
                        
                        cpu = random.uniform(85.0, 98.0) if is_spike else random.uniform(22.0, 58.0)
                        temp = random.uniform(55.0, 72.0) if is_spike else random.uniform(32.0, 48.0)
                        vib = random.uniform(4.5, 9.2) if is_spike else random.uniform(0.8, 2.6)
                        net_in = random.randint(4500, 15000) if is_spike else random.randint(400, 1800)
                        net_out = random.randint(3000, 12000) if is_spike else random.randint(300, 1200)

                        packet = TelemetryIngestRequest(
                            node_id=node.node_id,
                            cpu=round(cpu, 1),
                            memory=round(random.uniform(40.0, 75.0), 1),
                            temperature=round(temp, 1),
                            vibration=round(vib, 2),
                            network_in=net_in,
                            network_out=net_out,
                            timestamp=datetime.now(timezone.utc)
                        )
                        await TelemetryService.ingest_packet(db, packet)

                    # 2. Simulate Drone Flight Movements & Battery Drain
                    drones = db.query(DroneAsset).filter(DroneAsset.status.in_(["ACTIVE", "PATROLLING"])).all()
                    for drone in drones:
                        drone.latitude += random.uniform(-0.001, 0.001)
                        drone.longitude += random.uniform(-0.001, 0.001)
                        drone.speed_kmh = round(random.uniform(35.0, 65.0), 1)
                        drone.altitude_m = round(random.uniform(90.0, 150.0), 1)
                        if drone.battery_pct > 5:
                            drone.battery_pct = max(5, drone.battery_pct - (1 if random.random() < 0.05 else 0))
                        db.commit()

                    # 3. Simulate Weather fluctuation
                    zones = db.query(EnvironmentalZone).all()
                    for zone in zones:
                        zone.temp_celsius = round(max(15.0, zone.temp_celsius + random.uniform(-0.2, 0.2)), 1)
                        zone.rainfall_mm = max(0.0, zone.rainfall_mm + round(random.uniform(-0.1, 0.1), 1))
                        db.commit()

                finally:
                    db.close()

            except Exception as e:
                logger.error(f"Error in telemetry simulator loop: {e}")

            await asyncio.sleep(self.interval)

    def stop(self):
        self.is_running = False
        logger.info("Railway Rakshak Telemetry Simulator stopped.")

simulator_instance = TelemetrySimulator()
