from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.all_schemas import LedgerBlockResponse, LedgerVerificationResult
from ..services.ledger_service import LedgerService
from ..models.all_models import LedgerBlock

router = APIRouter(prefix="/ledger", tags=["Blockchain Audit Ledger"])

@router.get("/blocks", response_model=List[LedgerBlockResponse])
def get_ledger_blocks(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve chronologically linked cryptographic SHA-256 blocks from the immutable audit ledger."""
    return db.query(LedgerBlock).order_by(LedgerBlock.block_height.desc()).limit(limit).all()

@router.post("/verify", response_model=LedgerVerificationResult)
def verify_audit_ledger(db: Session = Depends(get_db)):
    """
    Run cryptographic hash recalculation on every block in the ledger chain.
    Confirms zero tampering, valid previous hashes, and immutable proof of operational integrity.
    """
    return LedgerService.verify_chain(db)
