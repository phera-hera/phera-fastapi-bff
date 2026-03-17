from fastapi import APIRouter
from . import __init__  # noqa
from ..schemas import DevTokenRequest, TokenResponse
from ..auth import sign_dev_token
import hashlib

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/dev-token", response_model=TokenResponse)
def dev_token(req: DevTokenRequest):
    # For local testing only. Later replaced by Zitadel login.
    sub = req.sub or ("dev-" + hashlib.sha256(req.email.encode("utf-8")).hexdigest()[:16])
    token = sign_dev_token({"sub": sub, "email": req.email})
    return TokenResponse(access_token=token)
