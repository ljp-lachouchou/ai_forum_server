import asyncio

from langchain_text_splitters import MarkdownHeaderTextSplitter
from milvus_model.hybrid import BGEM3EmbeddingFunction

from ai.client.ClientBuilder import ClientBuilder, ClientType
from ai.db.DBClient import DBClient
from ai.rag.RagConfiguration import RagConfigurationBuilder
from ai.rag.RagManager import MilvusRagRetriever
from backend.Sql.SClient import SupabaseClient
from backend.service.HybridSearchService import HybridSearchService
from backend.service.LLMService import  DeepSeekLLMService
from backend.service.RagQueryService import RagQueryService
from backend.service.WordService import WordService

if __name__ == "__main__":
    word_service = WordService(SupabaseClient().client)
    rag_retriever = MilvusRagRetriever(DBClient.get_client(),
                                       RagConfigurationBuilder(
                                           bge_model=BGEM3EmbeddingFunction(
                                               model_name="C:\\Users\\ljp\\PycharmProjects\\Forum\\model\\bge-m3",
                                               use_fp16=False, device="cpu"),
                                           splitter=MarkdownHeaderTextSplitter(headers_to_split_on=[
                                               ("#", "Header 1"),
                                               ("##", "Header 2"),
                                               ("###", "Header 3"),
                                           ]),
                                           content_loader=None,
                                           db_instance=DBClient.get_client()
                                       ))
    search_service = HybridSearchService(
        rag_retriever,
        word_service
    )
    model_client = ClientBuilder(ClientType.DeepSeek).build()
    llm_service = DeepSeekLLMService(model_client)
    async def a():
        rq_service = RagQueryService(search_service, llm_service)
        resp = await rq_service.query('BGE-M3 支持哪些检索方式？为什么适合用在 RAG 系统中？')
        return resp
    res = asyncio.run(a())
    print(f"哈哈哈哈\n{res.answer},{res.word_ids}")