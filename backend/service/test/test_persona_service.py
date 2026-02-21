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

_llm_module = types.ModuleType("backend.service.LLMService")


class _DummyLLMServiceType:
    pass


_llm_module.LLMService = _DummyLLMServiceType
sys.modules.setdefault("backend.service.LLMService", _llm_module)

from backend.service.PersonaService import PersonaService


class _StubSupabaseClient:
    def __init__(self):
        self.select_calls = []
        self.select_return = []

    async def select_async(self, table, filters=None, single=False, order_by=None, desc=False):
        self.select_calls.append((table, filters, single, order_by, desc))
        return self.select_return


class _StubLLMService:
    async def generate(self, prompt):
        return "[]"


class PersonaServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_data_and_stats_returns_default_when_no_row(self):
        sb = _StubSupabaseClient()
        service = PersonaService(sb, _StubLLMService())
        u_id = uuid4()

        data, stats = await service._get_data_and_stats(u_id)

        self.assertEqual(data["id"], str(u_id))
        self.assertEqual(data["stats"], {})
        self.assertEqual(data["behavioral_tags"], [])
        self.assertEqual(data["bio_summary"], "")
        self.assertEqual(stats, {})

        self.assertEqual(len(sb.select_calls), 1)
        table, filters, single, order_by, desc = sb.select_calls[0]
        self.assertEqual(table, "user_personas")
        self.assertEqual(filters, {"id": str(u_id)})
        self.assertFalse(single)
        self.assertIsNone(order_by)
        self.assertFalse(desc)

    async def test_get_data_and_stats_returns_first_row_when_exists(self):
        sb = _StubSupabaseClient()
        service = PersonaService(sb, _StubLLMService())
        u_id = uuid4()
        row = {
            "id": str(u_id),
            "stats": {"clicks": 3},
            "behavioral_tags": ["tag-a"],
            "bio_summary": "summary",
        }
        sb.select_return = [row]

        data, stats = await service._get_data_and_stats(u_id)

        self.assertEqual(data, row)
        self.assertEqual(stats, {"clicks": 3})


if __name__ == "__main__":
    unittest.main()
