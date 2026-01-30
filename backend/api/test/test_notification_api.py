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


def _stub_get_notification_service():
    raise RuntimeError("dependency override not set")


_services_module.get_notification_service = _stub_get_notification_service
sys.modules.setdefault("backend.api.services", _services_module)

import backend.api.NotificationApi as notification_api


class _StubNotificationService:
    def __init__(self):
        self.create_calls = []
        self.list_calls = []
        self.mark_read_calls = []
        self.mark_all_read_calls = []
        self.list_return = [{"id": "1"}]
        self.create_return = [{"id": "1"}]
        self.mark_read_return = [{"id": "1", "is_read": True}]
        self.mark_all_read_return = [{"id": "1", "is_read": True}]

    async def create_notification(self, user_id, n_type, content, ref_type=None, ref_id=None):
        self.create_calls.append((user_id, n_type, content, ref_type, ref_id))
        return self.create_return

    async def list_notifications(self, user_id, unread_only=False, limit=20):
        self.list_calls.append((user_id, unread_only, limit))
        return self.list_return

    async def mark_read(self, user_id, notification_ids):
        self.mark_read_calls.append((user_id, notification_ids))
        return self.mark_read_return

    async def mark_all_read(self, user_id):
        self.mark_all_read_calls.append(user_id)
        return self.mark_all_read_return


class NotificationApiTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.stub = _StubNotificationService()
        self.app.include_router(notification_api.notification_router)
        self.app.dependency_overrides[notification_api.get_notification_service] = (
            lambda: self.stub
        )
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides = {}

    def test_create_notification(self):
        user_id = uuid4()
        payload = {
            "user_id": str(user_id),
            "type": "like",
            "content": "new like",
            "ref_type": "post",
            "ref_id": str(uuid4()),
        }

        resp = self.client.post("/api/v1/notifications", json=payload)

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(self.stub.create_calls[0][0], user_id)

    def test_list_notifications(self):
        user_id = uuid4()

        resp = self.client.get(f"/api/v1/notifications?user_id={user_id}")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"], self.stub.list_return)
        self.assertEqual(self.stub.list_calls[0][0], user_id)

    def test_mark_read(self):
        user_id = uuid4()
        nid = uuid4()
        payload = {"user_id": str(user_id), "notification_ids": [str(nid)]}

        resp = self.client.post("/api/v1/notifications/read", json=payload)

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(self.stub.mark_read_calls[0][0], user_id)

    def test_mark_all_read(self):
        user_id = uuid4()

        resp = self.client.post("/api/v1/notifications/read_all", json={"user_id": str(user_id)})

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(self.stub.mark_all_read_calls[0], user_id)


if __name__ == "__main__":
    unittest.main()
