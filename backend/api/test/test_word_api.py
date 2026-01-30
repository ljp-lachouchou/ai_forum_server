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

_ai_module = types.ModuleType("ai")
_ai_rag_module = types.ModuleType("ai.rag")
_ai_rag_manager_module = types.ModuleType("ai.rag.RagManager")
_ai_rag_wrapper_module = types.ModuleType("ai.rag.rag_wrapper")
_ai_db_module = types.ModuleType("ai.db")
_ai_collection_module = types.ModuleType("ai.db.collection_names")


class _DummyRagManager:
    pass


def _dummy_content_mapper(*args, **kwargs):
    return {}


_ai_rag_manager_module.RagManager = _DummyRagManager
_ai_rag_manager_module.MilvusRagRetriever = _DummyRagManager
_ai_rag_wrapper_module.content_mapper = _dummy_content_mapper
_ai_collection_module.word_collection_name = "words"

sys.modules.setdefault("ai", _ai_module)
sys.modules.setdefault("ai.rag", _ai_rag_module)
sys.modules.setdefault("ai.rag.RagManager", _ai_rag_manager_module)
sys.modules.setdefault("ai.rag.rag_wrapper", _ai_rag_wrapper_module)
sys.modules.setdefault("ai.db", _ai_db_module)
sys.modules.setdefault("ai.db.collection_names", _ai_collection_module)

_persona_api_module = types.ModuleType("backend.api.PersonaApi")


def _stub_persona_get_service():
    raise RuntimeError("unused")


_persona_api_module.get_persona_service = _stub_persona_get_service
sys.modules.setdefault("backend.api.PersonaApi", _persona_api_module)

_persona_service_module = types.ModuleType("backend.service.PersonaService")


class _DummyPersonaService:
    pass


_persona_service_module.PersonaService = _DummyPersonaService
sys.modules.setdefault("backend.service.PersonaService", _persona_service_module)

_llm_service_module = types.ModuleType("backend.service.LLMService")


class _DummyLLMService:
    pass


_llm_service_module.LLMService = _DummyLLMService
sys.modules.setdefault("backend.service.LLMService", _llm_service_module)

_rag_summary_module = types.ModuleType("backend.service.RagSummaryService")


class _DummyRagSummaryService:
    pass


_rag_summary_module.RagSummaryService = _DummyRagSummaryService
sys.modules.setdefault("backend.service.RagSummaryService", _rag_summary_module)

_services_module = types.ModuleType("backend.api.services")


def _stub_get_word_service():
    raise RuntimeError("dependency override not set")


def _stub_get_report_service():
    raise RuntimeError("dependency override not set")


def _stub_get_rag_query_service():
    raise RuntimeError("unused")


def _stub_get_rag_manager():
    raise RuntimeError("unused")


def _stub_get_rag_summary_service():
    raise RuntimeError("unused")


def _stub_get_persona_service():
    raise RuntimeError("unused")


def _stub_get_llm_service():
    raise RuntimeError("dependency override not set")


_services_module.get_word_service = _stub_get_word_service
_services_module.get_report_service = _stub_get_report_service
_services_module.get_rag_query_service = _stub_get_rag_query_service
_services_module.get_rag_manager = _stub_get_rag_manager
_services_module.get_rag_summary_service = _stub_get_rag_summary_service
_services_module.get_persona_service = _stub_get_persona_service
_services_module.get_llm_service = _stub_get_llm_service
sys.modules.setdefault("backend.api.services", _services_module)

import backend.api.WordApi as word_api


class _StubWordService:
    def __init__(self):
        self.reject_calls = []
        self.reject_should_raise = None
        self.list_feed_calls = []
        self.list_feed_return = [{"id": "1"}]
        self.list_feed_should_raise = None

    async def reject(self, word_id, admin_id, reason):
        self.reject_calls.append((word_id, admin_id, reason))
        if self.reject_should_raise:
            raise self.reject_should_raise

    async def list_feed(self, mode="latest", category=None, user_id=None, limit=20):
        self.list_feed_calls.append((mode, category, user_id, limit))
        if self.list_feed_should_raise:
            raise self.list_feed_should_raise
        return self.list_feed_return


class _StubReportService:
    def __init__(self):
        self.create_calls = []

    async def create_report(self, reporter_id, target_type, target_id, reason):
        self.create_calls.append((reporter_id, target_type, target_id, reason))


class _StubLLMService:
    def __init__(self):
        self.response = ""

    async def generate(self, prompt: str) -> str:
        return self.response


class WordApiRejectTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.word_stub = _StubWordService()
        self.report_stub = _StubReportService()
        self.app.include_router(word_api.word_router)
        self.app.dependency_overrides[word_api.get_word_service] = lambda: self.word_stub
        self.app.dependency_overrides[word_api.get_report_service] = (
            lambda: self.report_stub
        )
        self.llm_stub = _StubLLMService()
        self.app.dependency_overrides[word_api.get_llm_service] = (
            lambda: self.llm_stub
        )
        self.client = TestClient(self.app)

    def tearDown(self):
        self.app.dependency_overrides = {}

    def test_reject_word(self):
        word_id = uuid4()
        admin_id = uuid4()
        reason = "bad content"

        resp = self.client.post(
            f"/api/v1/words/{word_id}/reject",
            params={"admin_id": str(admin_id), "reson": reason},
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(len(self.word_stub.reject_calls), 1)
        called_word_id, called_admin_id, called_reason = self.word_stub.reject_calls[0]
        self.assertEqual(str(called_word_id), str(word_id))
        self.assertEqual(str(called_admin_id), str(admin_id))
        self.assertEqual(called_reason, reason)
        self.assertEqual(len(self.report_stub.create_calls), 1)
        report_call = self.report_stub.create_calls[0]
        self.assertEqual(str(report_call[0]), str(admin_id))
        self.assertEqual(report_call[1], "word")
        self.assertEqual(str(report_call[2]), str(word_id))
        self.assertEqual(report_call[3], reason)

    def test_reject_word_failure(self):
        word_id = uuid4()
        admin_id = uuid4()
        self.word_stub.reject_should_raise = RuntimeError("fail")

        resp = self.client.post(
            f"/api/v1/words/{word_id}/reject",
            params={"admin_id": str(admin_id), "reson": "bad"},
        )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 500)
        self.assertEqual(len(self.report_stub.create_calls), 0)

    def test_list_feed_latest(self):
        resp = self.client.get("/api/v1/words/feeds?mode=latest&limit=10")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"], self.word_stub.list_feed_return)
        self.assertEqual(self.word_stub.list_feed_calls[0][0], "latest")

    def test_list_feed_invalid_mode(self):
        self.word_stub.list_feed_should_raise = ValueError("Invalid feed mode")

        resp = self.client.get("/api/v1/words/feeds?mode=bad")

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 400)

    def test_ai_assist_post_parses_json(self):
        self.llm_stub.response = "{\"titles\":[\"t1\",\"t2\"],\"tags\":[\"a\"]}"

        resp = self.client.post("/api/v1/ai/assist/post", json={"content": "hello"})

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertEqual(body["data"]["suggested_titles"], ["t1", "t2"])
        self.assertEqual(body["data"]["suggested_tags"], ["a"])

    def test_ai_assist_post_fallback(self):
        self.llm_stub.response = "not json"

        resp = self.client.post("/api/v1/ai/assist/post", json={"content": "hello world"})

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["code"], 200)
        self.assertTrue(body["data"]["suggested_titles"])


if __name__ == "__main__":
    unittest.main()
