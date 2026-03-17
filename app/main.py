from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .config import CORS_ORIGINS, DEPLOYMENT_MODE

from .routers.health import router as health_router
from .routers.auth_dev import router as auth_router
from .routers.scans import router as scans_router
from .routers.history import router as history_router
from .routers.trends import router as trends_router
from .routers.bff import router as bff_router

from .deps import get_current_user
from . import models

app = FastAPI(title="pHera Backend MVP")

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Always available
app.include_router(health_router)
app.include_router(bff_router)

# MVP-only features
if DEPLOYMENT_MODE == "mvp":
    Base.metadata.create_all(bind=engine)

    app.include_router(auth_router)
    app.include_router(scans_router)
    app.include_router(history_router)
    app.include_router(trends_router)

    @app.get("/api/me", tags=["auth"])
    def api_me(user: models.User = Depends(get_current_user)):
        return {"id": user.id, "sub": user.sub, "email": user.email}