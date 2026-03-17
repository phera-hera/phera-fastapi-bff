from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from .. import models

router = APIRouter(prefix="/trends", tags=["trends"])

@router.get("")
def trends(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # MVP stub: return simple stats.
    scans = db.query(models.Scan).filter(models.Scan.user_id == user.id).all()
    values = []
    for s in scans:
        try:
            values.append(float(s.ph))
        except Exception:
            pass
    if not values:
        return {"count": 0, "avg": None, "min": None, "max": None}
    return {"count": len(values), "avg": sum(values)/len(values), "min": min(values), "max": max(values)}
