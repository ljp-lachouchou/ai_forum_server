from dataclasses import dataclass
from typing import List
from uuid import UUID


from ai.rag.RagManager import MilvusRagRetriever


@dataclass
class RetrievedChunk:
    word_id: UUID
    raw_text: str

class HybridSearchService:
    def __init__(
        self,
        retriever: MilvusRagRetriever,
        word_service,
    ):
        """
        :param retriever: MilvusRagRetriever
        :param word_service: Supabase word service（状态 / 权限）
        """
        self.retriever = retriever
        self.words = word_service

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> List[RetrievedChunk]:
        """
        语义搜索入口：
        1. query -> vector（retriever）
        2. Milvus 向量召回（retriever）
        3. Supabase 状态 / 权限过滤
        """

        # 1️⃣ query → 向量
        query_vector = await self.retriever.query_as_vector(query)

        # 2️⃣ Milvus chunk 召回
        milvus_hits = await self.retriever.search(
            collection_name="md_word_mixed_collection",
            query_vector=query_vector,
            limit=limit * 3,  # 给过滤留余量
        )
        if not milvus_hits:
            return []

        # 3️⃣ 提取 word_id → Supabase 过滤
        word_ids = [hit["word_id"] for hit in milvus_hits]
        valid_word_ids = set(
            self.words.filter_published_ids(word_ids)
        )

        # 4️⃣ 构造最终 chunk 结果
        chunks: List[RetrievedChunk] = []
        for hit in milvus_hits:
            wid = UUID(hit["word_id"])
            if wid in valid_word_ids:
                chunks.append(
                    RetrievedChunk(
                        word_id=wid,
                        raw_text=hit["raw_text"],
                    )
                )
            if len(chunks) >= limit:
                break

        return chunks
