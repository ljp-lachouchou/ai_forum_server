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

from backend.service.CommentService import CommentService


class _StubSupabaseClient:
    def __init__(self):
        self.insert_calls = []
        self.select_calls = []
        self.delete_calls = []
        self.select_return = None

    async def insert_async(self, table, data, token=None):
        self.insert_calls.append((table, data, token))
        return [{"id": str(uuid4())}]

    async def select_async(
        self,
        table,
        filters=None,
        single=False,
        order_by=None,
        desc=False,
        token=None,
    ):
        self.select_calls.append((table, filters, single, order_by, desc, token))
        return self.select_return

    async def delete_async(self, table, filters, token=None):
        self.delete_calls.append((table, filters, token))


class CommentServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_comment_calls_insert(self):
        sb = _StubSupabaseClient()
        service = CommentService(sb)
        post_id = uuid4()
        author_id = uuid4()

        result = await service.create_comment(post_id, author_id, "hello")

        self.assertTrue(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(sb.insert_calls), 1)
        table, data, token = sb.insert_calls[0]
        self.assertEqual(table, "comments")
        self.assertEqual(data["post_id"], str(post_id))
        self.assertEqual(data["author_id"], str(author_id))
        self.assertEqual(data["content"], "hello")
        self.assertIsNone(token)

    async def test_list_comments_orders_by_created_at(self):
        sb = _StubSupabaseClient()
        sb.select_return = [{"id": str(uuid4())}]
        service = CommentService(sb)
        post_id = uuid4()

        result = await service.list_comments(post_id)

        self.assertEqual(result, sb.select_return)
        self.assertEqual(len(sb.select_calls), 1)
        table, filters, single, order_by, desc, token = sb.select_calls[0]
        self.assertEqual(table, "comments")
        self.assertEqual(filters, {"post_id": str(post_id)})
        self.assertFalse(single)
        self.assertEqual(order_by, "created_at")
        self.assertFalse(desc)
        self.assertIsNone(token)

    async def test_delete_comment_rejects_other_author(self):
        sb = _StubSupabaseClient()
        service = CommentService(sb)
        comment_id = uuid4()
        author_id = uuid4()
        sb.select_return = {"id": str(comment_id), "author_id": str(uuid4())}

        with self.assertRaises(PermissionError):
            await service.delete_comment(comment_id, author_id)

        self.assertEqual(len(sb.delete_calls), 0)

    async def test_delete_comment_deletes_when_author_matches(self):
        sb = _StubSupabaseClient()
        service = CommentService(sb)
        comment_id = uuid4()
        author_id = uuid4()
        sb.select_return = {"id": str(comment_id), "author_id": str(author_id)}

        await service.delete_comment(comment_id, author_id)

        self.assertEqual(len(sb.delete_calls), 1)
        table, filters, token = sb.delete_calls[0]
        self.assertEqual(table, "comments")
        self.assertEqual(filters, {"id": str(comment_id)})
        self.assertIsNone(token)


if __name__ == "__main__":
    unittest.main()
