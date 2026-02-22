import sys
import types
import unittest
from pathlib import Path
from uuid import uuid4

_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

_supabase_module = types.ModuleType("supabase")
_sync_module = types.ModuleType("supabase._sync")
_client_module = types.ModuleType("supabase._sync.client")


class _DummySyncClient:
    pass


def _dummy_create_client(*args, **kwargs):
    return None


_client_module.SyncClient = _DummySyncClient
_supabase_module._sync = _sync_module
_supabase_module.create_client = _dummy_create_client
_sync_module.client = _client_module

sys.modules.setdefault("supabase", _supabase_module)
sys.modules.setdefault("supabase._sync", _sync_module)
sys.modules.setdefault("supabase._sync.client", _client_module)

from backend.service.ProfileService import ProfileService


class _StubResponse:
    def __init__(self, data):
        self.data = data


class _StubUpdateQuery:
    def __init__(self, response_data):
        self.response_data = response_data
        self.update_payload = None
        self.eq_calls = []

    def update(self, data):
        self.update_payload = data
        return self

    def eq(self, key, value):
        self.eq_calls.append((key, value))
        return self

    def execute(self):
        return _StubResponse(self.response_data)


class _StubClient:
    def __init__(self, response_data):
        self.response_data = response_data
        self.table_calls = []
        self.last_query = None

    def table(self, name):
        self.table_calls.append(name)
        self.last_query = _StubUpdateQuery(self.response_data)
        return self.last_query


class _StubSupabaseClient:
    def __init__(self, response_data):
        self.response_data = response_data
        self.auth_tokens = []
        self.client = _StubClient(response_data)

    def get_auth_client(self, token):
        self.auth_tokens.append(token)
        return self.client


class ProfileServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_update_profile_returns_first_object_when_supabase_returns_list(self):
        row = {"id": "u1", "nickname": "alice"}
        sb = _StubSupabaseClient(response_data=[row])
        service = ProfileService(sb)

        result = await service.update_profile(uuid4(), {"nickname": "alice"}, token="t1")

        self.assertEqual(result, row)
        self.assertEqual(sb.auth_tokens, ["t1"])
        self.assertEqual(sb.client.table_calls, ["profiles"])
        self.assertEqual(sb.client.last_query.update_payload, {"nickname": "alice"})

    async def test_update_profile_returns_none_when_supabase_returns_empty_list(self):
        sb = _StubSupabaseClient(response_data=[])
        service = ProfileService(sb)

        result = await service.update_profile(uuid4(), {"nickname": "alice"})

        self.assertIsNone(result)

    async def test_update_profile_keeps_object_when_supabase_returns_object(self):
        row = {"id": "u1", "nickname": "alice"}
        sb = _StubSupabaseClient(response_data=row)
        service = ProfileService(sb)

        result = await service.update_profile(uuid4(), {"nickname": "alice"})

        self.assertEqual(result, row)


if __name__ == "__main__":
    unittest.main()
