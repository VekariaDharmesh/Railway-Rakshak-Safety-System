from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.all_models import EnvironmentalZone

class EnvironmentalService:
    @staticmethod
    def get_all_zones(db: Session) -> List[EnvironmentalZone]:
        return db.query(EnvironmentalZone).all()

    @staticmethod
    def get_zone(db: Session, zone_id_or_name: str) -> Optional[EnvironmentalZone]:
        return db.query(EnvironmentalZone).filter(
            (EnvironmentalZone.zone_name.ilike(f"%{zone_id_or_name}%")) | 
            (EnvironmentalZone.id == (int(zone_id_or_name) if zone_id_or_name.isdigit() else -1))
        ).first()

    get_environmental_hazards = get_all_zones
