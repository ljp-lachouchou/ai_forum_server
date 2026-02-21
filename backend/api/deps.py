from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException

from backend.api.services import get_redis_client
from backend.Sql.cache.RedisCacheClient import RedisCacheClient


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    token: str


def _decode_jwt_payload(token: str) -> Optional[dict]:
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        raw = base64.urlsafe_b64decode(payload.encode("utf-8"))
        parsed = json.loads(raw.decode("utf-8"))
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def _is_project_api_key(token: str) -> bool:
    payload = _decode_jwt_payload(token)
    if not payload:
        return False
    role = payload.get("role")
    sub = payload.get("sub")
    issuer = payload.get("iss")
    return issuer == "supabase" and role in {"anon", "service_role"} and not sub


def _is_claim_expired(payload: Optional[dict]) -> bool:
    if not payload:
        return False
    exp = payload.get("exp")
    if exp is None:
        return False
    try:
        return int(exp) <= int(time.time())
    except Exception:
        return False


def _normalize_cached_token(value: Optional[object]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    return str(value).strip().strip('"').strip("'")


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    raw = authorization.strip()
    if not raw:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = raw.split(None, 1)
    if len(parts) == 2 and parts[0].lower() in {"bearer", "token", "jwt"}:
        raw = parts[1].strip()
    return raw.strip().strip('"').strip("'")


async def require_auth(
    authorization: Optional[str] = Header(default=None),
    redis_client: RedisCacheClient = Depends(get_redis_client),
) -> AuthContext:
    token = _extract_token(authorization)
    payload = _decode_jwt_payload(token)
    if _is_project_api_key(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid token: expected user access token, got project API key",
        )
    if _is_claim_expired(payload):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id_from_claim = _normalize_cached_token((payload or {}).get("sub"))
    if not user_id_from_claim:
        raise HTTPException(status_code=401, detail="Invalid token")

    redis_hit = await redis_client.is_token_valid(token)
    if redis_hit:
        cached_user_id = _normalize_cached_token(
            await redis_client.get_value(f"auth:token:{token}")
        )
        if cached_user_id:
            if user_id_from_claim != cached_user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            return AuthContext(user_id=cached_user_id, token=token)

    # Recover from partial eviction using per-user active token mapping.
    active_token = _normalize_cached_token(
        await redis_client.get_value(f"user:active_token:{user_id_from_claim}")
    )
    if active_token != token:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Redis may lose auth:token mapping after restart/eviction. Rebuild cache.
    try:
        await redis_client.set_token_with_single_login(token, user_id_from_claim)
    except Exception:
        # Cache recovery failure should not block a valid JWT request.
        pass

    return AuthContext(user_id=user_id_from_claim, token=token)


def is_same_user(ctx: AuthContext, target_id) -> bool:
    if target_id is None:
        return False
    return str(target_id) == ctx.user_id
