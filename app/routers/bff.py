from typing import Any

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException

from .. import config
from ..deps import get_current_user_optional

router = APIRouter(prefix="/api", tags=["bff"])


@router.post("/analyze")
async def analyze(
    payload: dict[str, Any] = Body(...),
    user=Depends(get_current_user_optional),
):
    headers: dict[str, str] = {}

    if config.DEPLOYMENT_MODE == "mvp":
        if not config.RAG_API_KEY:
            raise HTTPException(status_code=500, detail="RAG_API_KEY not configured")
        headers["X-API-Key"] = config.RAG_API_KEY
        if user:
            headers["X-User-Id"] = user.sub

    rag_url = f"{config.RAG_BASE_URL.rstrip('/')}/api/v1/query"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(rag_url, json=payload, headers=headers)
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to reach RAG backend: {exc}")
