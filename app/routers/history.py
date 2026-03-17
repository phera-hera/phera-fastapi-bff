from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from .. import models
from ..schemas import HistoryOut, ScanOut

router = APIRouter(prefix="/history", tags=["history"])

@router.get("", response_model=HistoryOut)
def list_history(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    scans = (
        db.query(models.Scan)
        .filter(models.Scan.user_id == user.id)
        .order_by(models.Scan.created_at.desc())
        .all()
    )
    return {"items": scans}
