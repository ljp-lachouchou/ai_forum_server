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


def _stub_get_like_service():
    raise RuntimeError("dependency override not set")


def _stub_get_bookmark_service():
    raise RuntimeError("dependency override not set")


_services_module.get_like_service = _stub_get_like_service
_services_module.get_bookmark_service = _stub_get_bookmark_service
sys.modules.setdefault("backend.api.services", _services_module)

import backend.api.InteractionApi as interaction_api


class _StubLikeService:
    def __init__(self):
        self.toggle_calls = []
        self.toggle_return = True
        self.list_calls = []
        self.list_return = [{"post_id": "1"}]

    async def toggle_like(self, user_id, post_id):
        self.toggle_calls.append((user_id, post_id))
        return self.toggle_return

    async def list_user_likes(self, user_id):
        self.list_calls.append(user_id)
        return self.list_return


class _StubBookmarkService:
    def __init__(self):
        self.is_calls = []
        self.is_return = False
        self.add_calls = []
        self.remove_calls = []

    async def is_bookmarked(self, user_id, post_id):
        self.is_calls.append((user_id, post_id))
        return self.is_return

    async def add_bookmark(self, user_id, post_id):
        self.add_calls.append((user_id, post_id))

    async def remove_bookmark(self, user_id, post_id):
        self.remove_calls.append((user_id, post_id))


class InteractionApiTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.like_service = _StubLikeService()
        self.bookmark_service = _StubBookmarkService()
        self.app.include_router(interaction_api.interaction_router)
        self.app.dependency_overrides[interaction_api.get_like_service] = lambda: self.like_service
        self.app.dependency_overrides[interaction_api.get_bookmark_service] = lambda: self.bookmark_service
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides = {}

    def test_toggle_like(self):
        post_id = uuid4()
        user_id = uuid4()
        payload = {"user_id": str(user_id)}

        resp = self.client.post(f"/api/v1/posts/{post_id}/like", json=payload)

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"]["liked"], True)
        self.assertEqual(len(self.like_service.toggle_calls), 1)

    def test_toggle_collect_add(self):
        post_id = uuid4()
        user_id = uuid4()
        self.bookmark_service.is_return = False

        resp = self.client.post(
            f"/api/v1/posts/{post_id}/collect",
            json={"user_id": str(user_id)},
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"]["collected"], True)
        self.assertEqual(len(self.bookmark_service.add_calls), 1)
        self.assertEqual(len(self.bookmark_service.remove_calls), 0)

    def test_toggle_collect_remove(self):
        post_id = uuid4()
        user_id = uuid4()
        self.bookmark_service.is_return = True

        resp = self.client.post(
            f"/api/v1/posts/{post_id}/collect",
            json={"user_id": str(user_id)},
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"]["collected"], False)
        self.assertEqual(len(self.bookmark_service.add_calls), 0)
        self.assertEqual(len(self.bookmark_service.remove_calls), 1)

    def test_list_user_likes(self):
        user_id = uuid4()

        resp = self.client.get(f"/api/v1/user/likes?user_id={user_id}")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"], self.like_service.list_return)
        self.assertEqual(self.like_service.list_calls, [user_id])


if __name__ == "__main__":
    unittest.main()
