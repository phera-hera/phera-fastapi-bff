from fastapi import Header, HTTPException, status

from .config import DEPLOYMENT_MODE


def get_db():
    # Database sessions are only needed for authenticated / persistent MVP routes.
    if DEPLOYMENT_MODE != "mvp":
        yield None
        return

    from .database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str | None = Header(default=None),
    db= None,
):
    if DEPLOYMENT_MODE != "mvp":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is disabled in beta mode",
        )

    from .auth import verify_token
    from . import models

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    payload = verify_token(token)

    sub = payload.get("sub")
    email = payload.get("email")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing 'sub'")

    if db is None:
        raise HTTPException(status_code=500, detail="Database session is not available")

    user = db.query(models.User).filter(models.User.sub == sub).first()
    if not user:
        user = models.User(sub=sub, email=email or "")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db=None,
):
    if DEPLOYMENT_MODE != "mvp":
        return None

    from .auth import verify_token
    from . import models

    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    try:
        token = authorization.split(" ", 1)[1].strip()
        payload = verify_token(token)
        sub = payload.get("sub")
        email = payload.get("email")
        if not sub or db is None:
            return None
        user = db.query(models.User).filter(models.User.sub == sub).first()
        if not user:
            user = models.User(sub=sub, email=email or "")
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    except Exception:
        return None
