from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from datetime import datetime

class DevTokenRequest(BaseModel):
    email: str = Field(..., examples=["test@example.com"])
    sub: str | None = Field(default=None, description="Optional stable subject; if not provided, derived from email")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ScanCreate(BaseModel):
    ph: str = Field(..., examples=["7.35"])
    details: Dict[str, Any] = Field(default_factory=dict)

class ScanOut(BaseModel):
    id: int
    ph: str
    details: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class HistoryOut(BaseModel):
    items: List[ScanOut]
