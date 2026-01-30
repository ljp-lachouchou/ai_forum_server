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

from backend.service.CommentSummaryService import CommentSummaryService


class _StubCommentService:
    def __init__(self):
        self.calls = []
        self.return_value = []

    async def list_comments(self, post_id):
        self.calls.append(post_id)
        return self.return_value


class _StubLLMService:
    def __init__(self):
        self.prompts = []
        self.return_value = "summary"

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.return_value


class CommentSummaryServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_no_comments_returns_none(self):
        comments = _StubCommentService()
        llm = _StubLLMService()
        service = CommentSummaryService(comments, llm)

        result = await service.summarize_comments(uuid4())

        self.assertEqual(result["summary"], None)
        self.assertEqual(result["comment_count"], 0)
        self.assertEqual(llm.prompts, [])

    async def test_summarizes_comments(self):
        comments = _StubCommentService()
        comments.return_value = [
            {"content": "A"},
            {"content": "B"},
        ]
        llm = _StubLLMService()
        llm.return_value = "ok"
        service = CommentSummaryService(comments, llm)

        result = await service.summarize_comments(uuid4())

        self.assertEqual(result["summary"], "ok")
        self.assertEqual(result["comment_count"], 2)
        self.assertEqual(len(llm.prompts), 1)
        self.assertIn("A", llm.prompts[0])
        self.assertIn("B", llm.prompts[0])

    async def test_respects_limit(self):
        comments = _StubCommentService()
        comments.return_value = [
            {"content": "A"},
            {"content": "B"},
        ]
        llm = _StubLLMService()
        service = CommentSummaryService(comments, llm, max_comments=1)

        await service.summarize_comments(uuid4())

        self.assertEqual(len(llm.prompts), 1)
        self.assertIn("A", llm.prompts[0])
        self.assertNotIn("B", llm.prompts[0])


if __name__ == "__main__":
    unittest.main()
