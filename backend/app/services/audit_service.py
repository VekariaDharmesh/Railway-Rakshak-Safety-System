from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
from typing import Optional, Dict, Any
from app.models.all_models import AuditLog

class AuditService:
    @staticmethod
    def log(
        db: Session,
        user: Optional[str] = None,
        user_email: Optional[str] = None,
        action: str = "ACTION",
        resource: str = "SYSTEM",
        resource_id: Optional[Any] = None,
        ip_address: str = "127.0.0.1",
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        effective_user = user or user_email or "SYSTEM_OPERATOR"
        data_dict = details or metadata or {}
        audit_entry = AuditLog(
            user_email=effective_user,
            action=action.upper(),
            resource=resource.upper(),
            resource_id=str(resource_id) if resource_id is not None else None,
            ip_address=ip_address,
            metadata_json=json.dumps(data_dict, default=str),
            timestamp=datetime.now(timezone.utc)
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry
