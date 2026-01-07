from backend.Sql.SClient import SupabaseClient
from backend.Sql.cache.RedisCacheClient import RedisCacheClient
from backend.entity.profile import ProfileSchema
from langchain_text_splitters import MarkdownHeaderTextSplitter
from milvus_model.hybrid import BGEM3EmbeddingFunction
from ai.client.ClientBuilder import ClientBuilder, ClientType
from ai.db.DBClient import DBClient
from ai.rag.RagConfiguration import RagConfigurationBuilder
from ai.rag.RagManager import MilvusRagRetriever, RagManager
from ai.rag.RagProcessor import MDMilvusRagProcessor
from backend.Sql.SClient import SupabaseClient
from ai.rag.RagConfiguration import RagConfigurationBuilder
from backend.service.AuthService import AuthService
from backend.service.HybridSearchService import HybridSearchService
from backend.service.LLMService import DeepSeekLLMService
from backend.service.PersonaService import PersonaService
from backend.service.ProfileService import ProfileService
from backend.service.RagQueryService import RagQueryService
from backend.service.RagSummaryService import RagSummaryService
from backend.service.WordService import WordService


def get_word_service():
    return WordService(SupabaseClient())


def get_rag_manager():
    manager = RagManager(RagConfigurationBuilder, MDMilvusRagProcessor)
    return manager.build(bge_model=BGEM3EmbeddingFunction(model_name="../model/bge-m3",
                                                          use_fp16=False, device="cpu"),
                         splitter=MarkdownHeaderTextSplitter(headers_to_split_on=[
                             ("#", "Header 1"),
                             ("##", "Header 2"),
                             ("###", "Header 3"),
                         ]),
                         content_loader=None,
                         db_instance=DBClient.get_client())


def get_search_service():
    word_service = get_word_service()
    rag_retriever = MilvusRagRetriever(DBClient.get_client(),
                                       RagConfigurationBuilder(
                                           bge_model=BGEM3EmbeddingFunction(
                                               model_name="../model/bge-m3",
                                               use_fp16=False, device="cpu"),
                                           splitter=MarkdownHeaderTextSplitter(headers_to_split_on=[
                                               ("#", "Header 1"),
                                               ("##", "Header 2"),
                                               ("###", "Header 3"),
                                           ]),
                                           content_loader=None,
                                           db_instance=DBClient.get_client()
                                       ))
    return HybridSearchService(
        rag_retriever,
        word_service
    )


def get_llm_service():
    model_client = ClientBuilder(ClientType.DeepSeek).build()
    return DeepSeekLLMService(model_client)


def get_rag_query_service():
    return RagQueryService(get_search_service(), get_llm_service())


def get_auth_service():
    return AuthService()


def get_redis_client():
    return RedisCacheClient()

def get_profile_service():
    return ProfileService(SupabaseClient())

def get_persona_service():
    return PersonaService(SupabaseClient(), get_llm_service())

def get_rag_summary_service():
    return RagSummaryService(SupabaseClient(),BGEM3EmbeddingFunction(
                                               model_name="../model/bge-m3",
                                               use_fp16=False, device="cpu"))