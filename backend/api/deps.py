from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException

from backend.api.services import get_auth_service, get_redis_client, get_profile_service
from backend.service.AuthService import AuthService
from backend.Sql.cache.RedisCacheClient import RedisCacheClient
from backend.service.ProfileService import ProfileService


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    token: str


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    raw = authorization.strip()
    if not raw:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = raw.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return raw


async def require_auth(
    authorization: Optional[str] = Header(default=None),
    auth_service: AuthService = Depends(get_auth_service),
    redis_client: RedisCacheClient = Depends(get_redis_client),
    profile_service: ProfileService = Depends(get_profile_service),
) -> AuthContext:
    token = _extract_token(authorization)
    if not await redis_client.is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await auth_service.get_current_user(token)
    user_id = getattr(getattr(user, "user", None), "id", None) or getattr(user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        profile_service.set_auth(token)
    except Exception:
        pass
    return AuthContext(user_id=str(user_id), token=token)


def is_same_user(ctx: AuthContext, target_id) -> bool:
    if target_id is None:
        return False
    return str(target_id) == ctx.user_id
