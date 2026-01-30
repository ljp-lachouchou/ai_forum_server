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

from backend.service.BookmarksService import BookmarkService


class _StubSupabaseClient:
    def __init__(self):
        self.insert_calls = []
        self.delete_calls = []
        self.select_calls = []
        self.select_return = []

    async def insert_async(self, table, data):
        self.insert_calls.append((table, data))
        return [{"id": str(uuid4())}]

    async def delete_async(self, table, filters):
        self.delete_calls.append((table, filters))

    async def select_async(self, table, filters=None, single=False, order_by=None, desc=False):
        self.select_calls.append((table, filters, single, order_by, desc))
        return self.select_return


class BookmarkServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_add_bookmark(self):
        sb = _StubSupabaseClient()
        service = BookmarkService(sb)
        user_id = uuid4()
        post_id = uuid4()

        await service.add_bookmark(user_id, post_id)

        self.assertEqual(len(sb.insert_calls), 1)
        table, data = sb.insert_calls[0]
        self.assertEqual(table, "bookmarks")
        self.assertEqual(data["user_id"], str(user_id))
        self.assertEqual(data["post_id"], str(post_id))

    async def test_remove_bookmark(self):
        sb = _StubSupabaseClient()
        service = BookmarkService(sb)
        user_id = uuid4()
        post_id = uuid4()

        await service.remove_bookmark(user_id, post_id)

        self.assertEqual(len(sb.delete_calls), 1)
        table, filters = sb.delete_calls[0]
        self.assertEqual(table, "bookmarks")
        self.assertEqual(filters["user_id"], str(user_id))
        self.assertEqual(filters["post_id"], str(post_id))

    async def test_is_bookmarked_true(self):
        sb = _StubSupabaseClient()
        sb.select_return = [{"id": "1"}]
        service = BookmarkService(sb)
        user_id = uuid4()
        post_id = uuid4()

        result = await service.is_bookmarked(user_id, post_id)

        self.assertTrue(result)
        table, filters, *_ = sb.select_calls[0]
        self.assertEqual(table, "bookmarks")
        self.assertEqual(filters["user_id"], str(user_id))
        self.assertEqual(filters["post_id"], str(post_id))

    async def test_list_user_bookmarks(self):
        sb = _StubSupabaseClient()
        sb.select_return = [{"post_id": "1"}]
        service = BookmarkService(sb)
        user_id = uuid4()

        result = await service.list_user_bookmarks(user_id)

        self.assertEqual(result, sb.select_return)
        table, filters, *_ = sb.select_calls[0]
        self.assertEqual(table, "bookmarks")
        self.assertEqual(filters["user_id"], str(user_id))


if __name__ == "__main__":
    unittest.main()
