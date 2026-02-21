import base64
import json
import sys
import types
import unittest
from pathlib import Path

from fastapi import HTTPException

_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

_services_module = types.ModuleType("backend.api.services")
_services_module.get_redis_client = lambda: None
sys.modules.setdefault("backend.api.services", _services_module)

_redis_module = types.ModuleType("backend.Sql.cache.RedisCacheClient")


class _RedisClientType:
    pass


_redis_module.RedisCacheClient = _RedisClientType
sys.modules.setdefault("backend.Sql.cache.RedisCacheClient", _redis_module)

from backend.api.deps import require_auth


class _StubRedisClient:
    def __init__(self, valid=False, kv=None):
        self.valid = valid
        self.kv = kv or {}
        self.set_calls = []

    async def is_token_valid(self, token):
        return self.valid

    async def get_value(self, key):
        return self.kv.get(key)

    async def set_token_with_single_login(self, token, user_id, ex=None):
        self.set_calls.append((token, user_id, ex))
        self.kv[f"auth:token:{token}"] = user_id
        self.kv[f"user:active_token:{user_id}"] = token
        return True


def _jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}

    def _encode(data: dict) -> str:
        raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    return f"{_encode(header)}.{_encode(payload)}.sig"


class AuthDepsTests(unittest.IsolatedAsyncioTestCase):
    async def test_require_auth_allows_cached_mapping(self):
        token = _jwt({"iss": "x", "role": "authenticated", "sub": "u-1", "exp": 4102444800})
        redis = _StubRedisClient(valid=True, kv={f"auth:token:{token}": "u-1"})

        ctx = await require_auth(f"Bearer {token}", redis)

        self.assertEqual(ctx.user_id, "u-1")
        self.assertEqual(ctx.token, token)
        self.assertEqual(redis.set_calls, [])

    async def test_require_auth_rejects_cached_user_mismatch(self):
        token = _jwt({"iss": "x", "role": "authenticated", "sub": "u-1", "exp": 4102444800})
        redis = _StubRedisClient(valid=True, kv={f"auth:token:{token}": "u-2"})

        with self.assertRaises(HTTPException) as ex:
            await require_auth(f"Bearer {token}", redis)

        self.assertEqual(ex.exception.status_code, 401)
        self.assertEqual(ex.exception.detail, "Invalid token")

    async def test_require_auth_recovers_when_mapping_missing_but_active_token_matches(self):
        token = _jwt({"iss": "x", "role": "authenticated", "sub": "u-3", "exp": 4102444800})
        redis = _StubRedisClient(
            valid=True,
            kv={f"user:active_token:u-3": token},
        )

        ctx = await require_auth(f"Bearer {token}", redis)

        self.assertEqual(ctx.user_id, "u-3")
        self.assertEqual(redis.set_calls, [(token, "u-3", None)])

    async def test_require_auth_recovers_on_redis_miss_with_active_token(self):
        token = _jwt({"iss": "x", "role": "authenticated", "sub": "u-4", "exp": 4102444800})
        redis = _StubRedisClient(
            valid=False,
            kv={f"user:active_token:u-4": token},
        )

        ctx = await require_auth(f"Bearer {token}", redis)

        self.assertEqual(ctx.user_id, "u-4")
        self.assertEqual(redis.set_calls, [(token, "u-4", None)])

    async def test_require_auth_rejects_when_active_token_differs(self):
        token = _jwt({"iss": "x", "role": "authenticated", "sub": "u-5", "exp": 4102444800})
        redis = _StubRedisClient(
            valid=False,
            kv={f"user:active_token:u-5": "token-new"},
        )

        with self.assertRaises(HTTPException) as ex:
            await require_auth(f"Bearer {token}", redis)

        self.assertEqual(ex.exception.status_code, 401)
        self.assertEqual(ex.exception.detail, "Invalid token")

    async def test_require_auth_rejects_supabase_project_api_key(self):
        api_key_like = _jwt({"iss": "supabase", "role": "anon", "ref": "demo"})
        redis = _StubRedisClient(valid=True)

        with self.assertRaises(HTTPException) as ex:
            await require_auth(f"Bearer {api_key_like}", redis)

        self.assertEqual(ex.exception.status_code, 401)
        self.assertEqual(
            ex.exception.detail,
            "Invalid token: expected user access token, got project API key",
        )

    async def test_require_auth_strips_wrapping_quotes(self):
        token = _jwt({"iss": "x", "role": "authenticated", "sub": "u-6", "exp": 4102444800})
        redis = _StubRedisClient(
            valid=False,
            kv={f"user:active_token:u-6": token},
        )

        ctx = await require_auth(f"Bearer \"{token}\"", redis)

        self.assertEqual(ctx.token, token)
        self.assertEqual(ctx.user_id, "u-6")

    async def test_require_auth_rejects_expired_token_claim(self):
        expired = _jwt({"iss": "x", "role": "authenticated", "sub": "u-8", "exp": 1})
        redis = _StubRedisClient(valid=True)

        with self.assertRaises(HTTPException) as ex:
            await require_auth(f"Bearer {expired}", redis)

        self.assertEqual(ex.exception.status_code, 401)
        self.assertEqual(ex.exception.detail, "Invalid or expired token")

    async def test_require_auth_rejects_missing_sub(self):
        token = _jwt({"iss": "x", "role": "authenticated", "exp": 4102444800})
        redis = _StubRedisClient(valid=True)

        with self.assertRaises(HTTPException) as ex:
            await require_auth(f"Bearer {token}", redis)

        self.assertEqual(ex.exception.status_code, 401)
        self.assertEqual(ex.exception.detail, "Invalid token")


if __name__ == "__main__":
    unittest.main()
