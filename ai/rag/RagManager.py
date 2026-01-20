"""
将‘流程者‘和’配置‘组合在一起
他更像是对于RagProcessor的代理
"""
import asyncio
from typing import Type, TypeVar, Generic, Optional, Any

from pymilvus import MilvusClient

from ai.rag.RagConfiguration import RagConfigurationBuilder
from ai.rag.RagProcessor import BaseRagProcessor
from ai.rag.types import WordModelLike

C = TypeVar("C", bound=RagConfigurationBuilder)
P = TypeVar("P", bound=BaseRagProcessor)


class RagManager(Generic[C, P]):
    def __init__(self, configurationBuilder_cls: Type[C], processor_cls: Type[P]):
        self.configurationBuilder_cls = configurationBuilder_cls
        self.processor_cls = processor_cls
        self.actual_processor: Optional[P] = None

    def build(self, **kwargs):
        # 实例化配置和处理器
        config_builder = self.configurationBuilder_cls(**kwargs)
        self.actual_processor = self.processor_cls(config_builder)

    async def start_process(self, collection_name: str, md_word: WordModelLike, mapper_func):
        if not self.actual_processor:
            raise RuntimeError("请先调用 build()")

        # 代理模式：驱动流水线
        doc = await self.actual_processor.upload_document(md_word.word_url)
        chunks = self.actual_processor.split_document(doc)
        vecs = await self.actual_processor.as_vector(chunks)
        await self.actual_processor.save_generic(collection_name, chunks, vecs, mapper_func, md_word)


from abc import ABC, abstractmethod
from typing import List, Dict


class RagRetriever(ABC):
    @abstractmethod
    async def query_as_vector(self, query: str) -> dict:
        """
        Query -> 向量（必须与 as_vector 同模型）
        """
        pass

    @abstractmethod
    async def search(
            self,
            collection_name: str,
            query_vector: dict,
            limit: int = 10,
    ) -> List[dict]:
        """
        向量召回
        """
        pass


class MilvusRagRetriever(RagRetriever):
    """
    基于 Milvus 的 RAG Retriever
    与 content_mapper 定义的表结构严格一致
    """

    def __init__(
            self,
            milvus_client: MilvusClient,
            config_builder: RagConfigurationBuilder,
            anns_field: str = "dense_vector",
    ):
        """
        :param milvus_client: 你已有的 Milvus client
        :param config_builder: 构建 bge_model（与索引阶段一致）
        :param anns_field: Milvus 中的主向量字段
        """
        self.milvus = milvus_client
        self.config_builder = config_builder
        self.anns_field = anns_field

    # -------------------------
    # 1️⃣ Query → 混合向量
    # -------------------------
    async def query_as_vector(self, query: str) -> Dict:
        """
        Query → dense_vector + sparse_vector
        （必须与 RagProcessor.as_vector 使用同一模型）
        """
        config = self.config_builder.build()

        vectors = await asyncio.to_thread(
            config.bge_model,
            [query],
        )

        dense = vectors["dense"]
        if hasattr(dense, "tolist"):
            dense = dense.tolist()

        sparse = vectors["sparse"]

        return {
            "dense_vector": dense[0],
            "sparse_vector": sparse[0],
        }

    # -------------------------
    # 2️⃣ Milvus 向量召回
    # -------------------------
    async def search(
            self,
            collection_name: str,
            query_vector: Dict,
            limit: int = 10,
    ) -> List[Dict]:
        results = await asyncio.to_thread(
            lambda: self.milvus.search(
                collection_name=collection_name,
                data=[query_vector[self.anns_field]],
                anns_field=self.anns_field,
                limit=limit,
                output_fields=["word_id", "raw_text", "entity_info"]
            )
        )

        return results[0]
