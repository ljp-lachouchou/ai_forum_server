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

_email_validator_module = types.ModuleType("email_validator")


class EmailNotValidError(Exception):
    pass


class _EmailResult:
    def __init__(self, email: str):
        self.email = email


def validate_email(email, **kwargs):
    return _EmailResult(email)


_email_validator_module.EmailNotValidError = EmailNotValidError
_email_validator_module.validate_email = validate_email
sys.modules.setdefault("email_validator", _email_validator_module)

import importlib.metadata as _importlib_metadata

_original_version = _importlib_metadata.version


def _patched_version(name: str):
    if name == "email-validator":
        return "2.0.0"
    return _original_version(name)


_importlib_metadata.version = _patched_version

from fastapi import FastAPI
from fastapi.testclient import TestClient

_services_module = types.ModuleType("backend.api.services")


def _stub_get_comment_service():
    raise RuntimeError("dependency override not set")


def _stub_get_comment_summary_service():
    raise RuntimeError("dependency override not set")


def _stub_get_redis_client():
    raise RuntimeError("dependency override not set")


_services_module.get_comment_service = _stub_get_comment_service
_services_module.get_comment_summary_service = _stub_get_comment_summary_service
_services_module.get_redis_client = _stub_get_redis_client
sys.modules.setdefault("backend.api.services", _services_module)

_redis_module = types.ModuleType("backend.Sql.cache.RedisCacheClient")


class _RedisClientType:
    pass


_redis_module.RedisCacheClient = _RedisClientType
sys.modules.setdefault("backend.Sql.cache.RedisCacheClient", _redis_module)

import backend.api.CommentApi as comment_api


class _StubCommentService:
    def __init__(self):
        self.create_calls = []
        self.list_calls = []
        self.delete_calls = []
        self.create_return = {"id": "1"}
        self.list_return = [{"id": "1"}]
        self.delete_should_raise = None

    async def create_comment(self, post_id, author_id, content, token=None):
        self.create_calls.append((post_id, author_id, content, token))
        return self.create_return

    async def list_comments(self, post_id):
        self.list_calls.append(post_id)
        return self.list_return

    async def delete_comment(self, comment_id, author_id, token=None):
        self.delete_calls.append((comment_id, author_id, token))
        if self.delete_should_raise:
            raise self.delete_should_raise


class _StubCommentSummaryService:
    def __init__(self):
        self.calls = []
        self.return_value = {"summary": "ok", "comment_count": 2}

    async def summarize_comments(self, post_id):
        self.calls.append(post_id)
        return self.return_value


class CommentApiTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.stub = _StubCommentService()
        self.summary_stub = _StubCommentSummaryService()
        self.current_user_id = str(uuid4())
        self.app.include_router(comment_api.comment_router)
        self.app.dependency_overrides[comment_api.get_comment_service] = lambda: self.stub
        self.app.dependency_overrides[comment_api.get_comment_summary_service] = (
            lambda: self.summary_stub
        )
        self.app.dependency_overrides[comment_api.require_auth] = (
            lambda: comment_api.AuthContext(user_id=self.current_user_id, token="test-token")
        )
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides = {}

    def test_create_comment(self):
        post_id = uuid4()
        author_id = self.current_user_id
        payload = {"author_id": str(author_id), "content": "hello"}

        resp = self.client.post(f"/api/v1/posts/{post_id}/comments", json=payload)

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"], self.stub.create_return)
        self.assertEqual(len(self.stub.create_calls), 1)
        called_post_id, called_author_id, called_content, called_token = self.stub.create_calls[0]
        self.assertEqual(str(called_post_id), str(post_id))
        self.assertEqual(str(called_author_id), str(author_id))
        self.assertEqual(called_content, "hello")
        self.assertEqual(called_token, "test-token")

    def test_list_comments(self):
        post_id = uuid4()

        resp = self.client.get(f"/api/v1/posts/{post_id}/comments")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"], self.stub.list_return)
        self.assertEqual(self.stub.list_calls, [post_id])

    def test_delete_comment(self):
        comment_id = uuid4()
        author_id = self.current_user_id
        payload = {"author_id": str(author_id)}

        resp = self.client.request(
            "DELETE",
            f"/api/v1/comments/{comment_id}",
            json=payload,
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(len(self.stub.delete_calls), 1)
        called_comment_id, called_author_id, called_token = self.stub.delete_calls[0]
        self.assertEqual(str(called_comment_id), str(comment_id))
        self.assertEqual(str(called_author_id), str(author_id))
        self.assertEqual(called_token, "test-token")

    def test_delete_comment_rejects_permission(self):
        comment_id = uuid4()
        author_id = self.current_user_id
        self.stub.delete_should_raise = PermissionError("no")

        resp = self.client.request(
            "DELETE",
            f"/api/v1/comments/{comment_id}",
            json={"author_id": str(author_id)},
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 403)

    def test_get_comment_summary(self):
        post_id = uuid4()

        resp = self.client.get(f"/api/v1/posts/{post_id}/comments/summary")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"], self.summary_stub.return_value)
        self.assertEqual(self.summary_stub.calls, [post_id])


if __name__ == "__main__":
    unittest.main()
