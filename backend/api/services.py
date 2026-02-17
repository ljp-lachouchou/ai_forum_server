import os
from functools import lru_cache
from pathlib import Path

from ai.client.ClientBuilder import ClientBuilder, ClientType
from ai.db.DBClient import DBClient
from ai.rag.RagConfiguration import RagConfigurationBuilder
from ai.rag.RagManager import MilvusRagRetriever, RagManager
from ai.rag.RagProcessor import MDMilvusRagProcessor
from backend.Sql.SClient import SupabaseClient
from backend.Sql.cache.RedisCacheClient import RedisCacheClient
from backend.service.AuthService import AuthService
from backend.service.BookmarksService import BookmarkService
from backend.service.CommentService import CommentService
from backend.service.CommentSummaryService import CommentSummaryService
from backend.service.HybridSearchService import HybridSearchService
from backend.service.LikeService import LikeService
from backend.service.FollowService import FollowService
from backend.service.AIPostReviewService import AIPostReviewService
from backend.service.NotificationService import NotificationService
from backend.service.ReportService import ReportService
from backend.service.StorageService import StorageService
from backend.service.TreeholeService import TreeholeService
from backend.service.SyncService import SyncService
from backend.service.LLMService import DeepSeekLLMService
from backend.service.PersonaService import PersonaService
from backend.service.ProfileService import ProfileService
from backend.service.RagQueryService import RagQueryService
from backend.service.RagSummaryService import RagSummaryService
from backend.service.WordService import WordService
from common.env import load_env
from langchain_text_splitters import MarkdownHeaderTextSplitter
from milvus_model.hybrid import BGEM3EmbeddingFunction

_MODEL_ENV_KEY = "BGE_MODEL_PATH"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _get_model_path() -> str:
    load_env()
    model_path = os.environ.get(_MODEL_ENV_KEY)
    if model_path:
        return model_path
    return str(_project_root() / "model" / "bge-m3")


@lru_cache(maxsize=1)
def _get_splitter():
    return MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ])


@lru_cache(maxsize=1)
def _get_bge_model():
    return BGEM3EmbeddingFunction(
        model_name=_get_model_path(),
        use_fp16=False,
        device="cpu",
    )


@lru_cache(maxsize=1)
def _get_db_client():
    return DBClient.get_client()


def _get_rag_config_kwargs():
    return {
        "bge_model": _get_bge_model(),
        "splitter": _get_splitter(),
        "content_loader": None,
        "db_instance": _get_db_client(),
    }


@lru_cache(maxsize=1)
def get_word_service():
    return WordService(SupabaseClient())


@lru_cache(maxsize=1)
def get_rag_manager():
    manager = RagManager(RagConfigurationBuilder, MDMilvusRagProcessor)
    manager.build(**_get_rag_config_kwargs())
    return manager


@lru_cache(maxsize=1)
def get_search_service():
    rag_retriever = MilvusRagRetriever(
        _get_db_client(),
        RagConfigurationBuilder(**_get_rag_config_kwargs()),
    )
    return HybridSearchService(
        rag_retriever,
        get_word_service(),
    )


@lru_cache(maxsize=1)
def get_llm_service():
    model_client = ClientBuilder(ClientType.DeepSeek).build()
    return DeepSeekLLMService(model_client)


@lru_cache(maxsize=1)
def get_rag_query_service():
    return RagQueryService(get_search_service(), get_llm_service())


@lru_cache(maxsize=1)
def get_auth_service():
    return AuthService()


@lru_cache(maxsize=1)
def get_redis_client():
    return RedisCacheClient()


@lru_cache(maxsize=1)
def get_profile_service():
    return ProfileService(SupabaseClient())


@lru_cache(maxsize=1)
def get_persona_service():
    return PersonaService(SupabaseClient(), get_llm_service())


@lru_cache(maxsize=1)
def get_rag_summary_service():
    return RagSummaryService(SupabaseClient(), _get_bge_model())


@lru_cache(maxsize=1)
def get_comment_service():
    return CommentService(SupabaseClient())


@lru_cache(maxsize=1)
def get_comment_summary_service():
    return CommentSummaryService(get_comment_service(), get_llm_service())


@lru_cache(maxsize=1)
def get_like_service():
    return LikeService(SupabaseClient())


@lru_cache(maxsize=1)
def get_bookmark_service():
    return BookmarkService(SupabaseClient())


@lru_cache(maxsize=1)
def get_treehole_service():
    return TreeholeService(SupabaseClient())


@lru_cache(maxsize=1)
def get_report_service():
    return ReportService(SupabaseClient())


@lru_cache(maxsize=1)
def get_sync_service():
    return SyncService(SupabaseClient())


@lru_cache(maxsize=1)
def get_notification_service():
    return NotificationService(SupabaseClient())


@lru_cache(maxsize=1)
def get_follow_service():
    return FollowService(SupabaseClient())


@lru_cache(maxsize=1)
def get_ai_post_review_service():
    return AIPostReviewService(SupabaseClient())


@lru_cache(maxsize=1)
def get_storage_service():
    return StorageService(SupabaseClient())
