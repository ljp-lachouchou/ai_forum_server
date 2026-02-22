import sys
import types
import unittest
from pathlib import Path
from uuid import uuid4

_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    # Allow running this file directly from IDEs.
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

from backend.service.TreeholeService import TreeholeService


class _StubSupabaseClient:
    def __init__(self):
        self.insert_calls = []
        self.select_calls = []
        self.mutil_calls = []
        self.select_return = []
        self.mutil_return = []

    async def insert_async(self, table, data, token=None):
        self.insert_calls.append((table, data, token))
        return [{"id": str(uuid4())}]

    async def select_async(self, table, filters=None, single=False, order_by=None, desc=False):
        self.select_calls.append((table, filters, single, order_by, desc))
        return self.select_return

    async def mutil_select_async(self, table, tar_in_column, in_s, filters):
        self.mutil_calls.append((table, tar_in_column, in_s, filters))
        return self.mutil_return


class TreeholeServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_treehole(self):
        sb = _StubSupabaseClient()
        service = TreeholeService(sb)
        author_id = uuid4()

        result = await service.create_treehole(author_id, "hello", True)

        table, data, token = sb.insert_calls[0]
        self.assertEqual(table, "treeholes")
        self.assertEqual(data["author_id"], str(author_id))
        self.assertEqual(data["content"], "hello")
        self.assertTrue(data["is_anonymous"])
        self.assertEqual(data["mood"], "平常")
        self.assertIsNone(token)
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)

    async def test_list_treeholes_slices(self):
        sb = _StubSupabaseClient()
        sb.select_return = [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
        ]
        service = TreeholeService(sb)

        result = await service.list_treeholes(limit=2, offset=1)

        self.assertEqual(result, [{"id": "2"}, {"id": "3"}])
        table, _, _, order_by, desc = sb.select_calls[0]
        self.assertEqual(table, "treeholes")
        self.assertEqual(order_by, "created_at")
        self.assertTrue(desc)

    async def test_list_treeholes_include_ai(self):
        sb = _StubSupabaseClient()
        sb.select_return = [{"id": "t1"}]
        sb.mutil_return = [{"treehole_id": "t1", "content": "hi"}]
        service = TreeholeService(sb)

        result = await service.list_treeholes(include_ai=True)

        self.assertEqual(result[0]["ai_replies"], sb.mutil_return)
        self.assertEqual(len(sb.mutil_calls), 1)


if __name__ == "__main__":
    unittest.main()
