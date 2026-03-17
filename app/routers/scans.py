from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from .. import models
from ..schemas import ScanCreate, ScanOut

router = APIRouter(prefix="/scans", tags=["scans"])

@router.post("", response_model=ScanOut)
def create_scan(
    payload: ScanCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    scan = models.Scan(user_id=user.id, ph=payload.ph, details=payload.details)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan
