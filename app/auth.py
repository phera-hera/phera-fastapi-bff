from __future__ import annotations

import json
import time
import urllib.request
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

from .config import ZITADEL_AUDIENCE, ZITADEL_ISSUER, DEV_JWT_SECRET

security = HTTPBearer(auto_error=False)
ALGORITHMS = ["RS256"]


class _JwksCache:
    def __init__(self, issuer: str, ttl_seconds: int = 300):
        self.issuer = issuer.rstrip("/")
        self.ttl_seconds = ttl_seconds
        self._jwks_uri: Optional[str] = None
        self._jwks: Optional[Dict[str, Any]] = None
        self._expires_at: float = 0.0

    def _http_get_json(self, url: str) -> Dict[str, Any]:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)

    def _ensure_discovery(self) -> None:
        if self._jwks_uri:
            return
        discovery_url = f"{self.issuer}/.well-known/openid-configuration"
        discovery = self._http_get_json(discovery_url)
        jwks_uri = discovery.get("jwks_uri")
        if not jwks_uri:
            raise RuntimeError("jwks_uri not found in OIDC discovery")
        self._jwks_uri = jwks_uri

    def get_jwks(self) -> Dict[str, Any]:
        now = time.time()
        if self._jwks and now < self._expires_at:
            return self._jwks

        self._ensure_discovery()
        assert self._jwks_uri is not None
        self._jwks = self._http_get_json(self._jwks_uri)
        self._expires_at = now + self.ttl_seconds
        return self._jwks

    def force_refresh(self) -> None:
        self._expires_at = 0.0


_jwks_cache = _JwksCache(ZITADEL_ISSUER)


def verify_token(token: str) -> Dict[str, Any]:
    """Verify a Zitadel access token (RS256) using JWKS from OIDC discovery."""
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Token header missing kid")

        jwks = _jwks_cache.get_jwks()
        keys = jwks.get("keys", [])
        key = next((k for k in keys if k.get("kid") == kid), None)

        if not key:
            # Key rotation: refresh once and retry
            _jwks_cache.force_refresh()
            jwks = _jwks_cache.get_jwks()
            keys = jwks.get("keys", [])
            key = next((k for k in keys if k.get("kid") == kid), None)

        if not key:
            raise HTTPException(status_code=401, detail="JWKS key not found")

        decode_kwargs: Dict[str, Any] = {
            "key": key,
            "algorithms": ALGORITHMS,
            "issuer": ZITADEL_ISSUER,
            "options": {"verify_aud": bool(ZITADEL_AUDIENCE)},
        }
        if ZITADEL_AUDIENCE:
            decode_kwargs["audience"] = ZITADEL_AUDIENCE

        return jwt.decode(token, **decode_kwargs)

    except HTTPException:
        raise
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Zitadel token",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Zitadel token",
        )


def sign_dev_token(payload: Dict[str, Any]) -> str:
    """Dev-only token (HS256). Used by /auth/dev-token for local testing."""
    return jwt.encode(payload, DEV_JWT_SECRET, algorithm="HS256")


def get_token_from_bearer(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    return credentials.credentials


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> Dict[str, Any]:
    token = get_token_from_bearer(credentials)
    return verify_token(token)
