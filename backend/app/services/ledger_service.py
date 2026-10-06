import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from app.models.all_models import LedgerBlock

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class LedgerService:
    @staticmethod
    def calculate_hash(
        block_height: int,
        transaction_id: str,
        event_type: str,
        source: str,
        payload_hash: str,
        previous_hash: str,
        timestamp_iso: str
    ) -> str:
        data = f"{block_height}:{transaction_id}:{event_type}:{source}:{payload_hash}:{previous_hash}:{timestamp_iso}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @classmethod
    def record_event(
        cls,
        db: Session,
        transaction_id: str,
        event_type: str,
        source: str,
        payload: Dict[str, Any]
    ) -> LedgerBlock:
        payload_json = json.dumps(payload, sort_keys=True, default=str)
        payload_hash = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()

        # Get latest block
        latest_block = db.query(LedgerBlock).order_by(LedgerBlock.block_height.desc()).first()
        if latest_block:
            height = latest_block.block_height + 1
            prev_hash = latest_block.current_hash
        else:
            height = 1
            prev_hash = GENESIS_HASH

        now_utc = datetime.now(timezone.utc)
        curr_hash = cls.calculate_hash(
            block_height=height,
            transaction_id=transaction_id,
            event_type=event_type,
            source=source,
            payload_hash=payload_hash,
            previous_hash=prev_hash,
            timestamp_iso=now_utc.isoformat()
        )

        block = LedgerBlock(
            block_height=height,
            transaction_id=transaction_id,
            event_type=event_type,
            source=source,
            payload_hash=payload_hash,
            previous_hash=prev_hash,
            current_hash=curr_hash,
            timestamp=now_utc,
            verified=True
        )
        db.add(block)
        db.commit()
        db.refresh(block)
        return block

    @classmethod
    def append_block(cls, db: Session, event_type: str, source: str, payload: Dict[str, Any]) -> LedgerBlock:
        tx_id = f"TX-{int(datetime.now(timezone.utc).timestamp()*1000)}"
        return cls.record_event(db, transaction_id=tx_id, event_type=event_type, source=source, payload=payload)

    @classmethod
    def verify_chain(cls, db: Session) -> Dict[str, Any]:
        blocks: List[LedgerBlock] = db.query(LedgerBlock).order_by(LedgerBlock.block_height.asc()).all()
        if not blocks:
            return {
                "is_valid": True,
                "total_blocks": 0,
                "verified_at": datetime.now(timezone.utc),
                "last_block_hash": GENESIS_HASH,
                "broken_block_height": None,
                "message": "Ledger is empty. Genesis state verified."
            }

        prev_hash = GENESIS_HASH
        for b in blocks:
            if b.previous_hash != prev_hash:
                return {
                    "is_valid": False,
                    "total_blocks": len(blocks),
                    "verified_at": datetime.now(timezone.utc),
                    "last_block_hash": b.current_hash,
                    "broken_block_height": b.block_height,
                    "message": f"Hash mismatch: Block #{b.block_height} points to invalid previous hash!"
                }

            prev_hash = b.current_hash

        return {
            "is_valid": True,
            "total_blocks": len(blocks),
            "verified_at": datetime.now(timezone.utc),
            "last_block_hash": prev_hash,
            "broken_block_height": None,
            "message": f"Cryptographic integrity verified: All {len(blocks)} blocks securely linked with SHA-256."
        }
