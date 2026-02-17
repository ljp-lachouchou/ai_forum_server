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


def _stub_get_treehole_service():
    raise RuntimeError("dependency override not set")


_services_module.get_treehole_service = _stub_get_treehole_service
sys.modules.setdefault("backend.api.services", _services_module)

import backend.api.TreeholeApi as treehole_api


class _StubTreeholeService:
    def __init__(self):
        self.create_calls = []
        self.list_calls = []
        self.create_return = [{"id": "1"}]
        self.list_return = [{"id": "1"}]

    async def create_treehole(self, author_id, content, is_anonymous, mood="平常"):
        self.create_calls.append((author_id, content, is_anonymous, mood))
        return self.create_return

    async def list_treeholes(self, limit=20, offset=0, include_ai=False):
        self.list_calls.append((limit, offset, include_ai))
        return self.list_return


class TreeholeApiTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.stub = _StubTreeholeService()
        self.app.include_router(treehole_api.treehole_router)
        self.app.dependency_overrides[treehole_api.get_treehole_service] = lambda: self.stub
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides = {}

    def test_create_treehole(self):
        payload = {
            "author_id": str(uuid4()),
            "content": "hello",
            "is_anonymous": True,
        }

        resp = self.client.post("/api/v1/treehole", json=payload)

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(len(self.stub.create_calls), 1)
        _, _, _, mood = self.stub.create_calls[0]
        self.assertEqual(mood, "平常")

    def test_list_treeholes_stream(self):
        resp = self.client.get("/api/v1/treehole/stream?limit=10&offset=0&include_ai=true")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"], self.stub.list_return)
        self.assertEqual(self.stub.list_calls, [(10, 0, True)])


if __name__ == "__main__":
    unittest.main()
