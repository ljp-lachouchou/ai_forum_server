import asyncio
import hashlib
import re
from typing import List, Optional, Union
from uuid import UUID

from milvus_model.hybrid import BGEM3EmbeddingFunction

from backend.Sql.SClient import SupabaseClient
from backend.service.RagQueryService import RagResult


class RagSummaryService:
    """
    RAG 搜索结果缓存服务（query-level）
    """

    TABLE = "rag_summaries"

    def __init__(self, sb: SupabaseClient, bg_model: BGEM3EmbeddingFunction):
        self.sb = sb
        self.bg_model = bg_model

    async def get_by_hash(
            self,
            query_hash: str,
    ) -> Optional[str]:
        """
        根据 query_hash 查询是否已有总结
        """
        data = await self.sb.select_async(
            self.TABLE,
            filters={"query_hash": query_hash},
            single=True,
        )

        if not data:
            return None

        return data["summary"]

    async def _save(
            self,
            query: str,
            query_hash: str,
            summary: str,
            source_post_ids: List[UUID],
            user_id: UUID,
            query_vector
    ) -> None:
        """
        保存一次 RAG 搜索总结（不可变）
        """
        data = {
            "user_id": str(user_id),
            "query": query,
            "query_hash": query_hash,
            "summary": summary,
            "source_post_ids": [str(pid) for pid in source_post_ids],
            "query_embedding": query_vector
        }

        # 3. 异步插入数据库
        await self.sb.insert_async(self.TABLE, data)

    def _get_query_hash(self, query: str) -> str:
        """根据query获取query_hash"""
        text = query.lower()
        # 2. 统一全角字符转半角 (可选)
        # 3. 将连续的多个空格替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        # 4. 去除首尾空格
        text = text.strip()

        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    async def _get_query_embedding(self, query: str):
        """获取query的向量"""
        vector = await asyncio.to_thread(self.bg_model, [query])
        return vector
    def _format_embedding(self,embedding):
        if isinstance(embedding, dict) and 'dense' in embedding:
            dense_list = embedding['dense']
            if len(dense_list) > 0:
                vec = dense_list[0]
                query_embedding = vec.tolist()
            else:
                query_embedding = []
        else:
            query_embedding = []
        return query_embedding
    async def insert_summary(
            self,
            query: str,
            summary: str,
            source_post_ids: List[UUID],
            user_id: UUID
    ):
        query_hash = self._get_query_hash(query)
        query_embedding_raw = await self._get_query_embedding(query)
        query_embedding = self._format_embedding(query_embedding_raw)
        await self._save(
            query=query,
            query_hash=query_hash,
            query_vector=query_embedding,
            summary=summary,
            source_post_ids=source_post_ids,
            user_id=user_id
        )
        print("存储完成")

    async def _catch_hash_and_uid(
            self,
            query_hash: str,
            uid: UUID
    ):
        """命中hash和uid则返回此数据"""
        try:
            data = await self.sb.select_async(
                "rag_summaries",
                {
                    "user_id": str(uid),
                    "query_hash": query_hash
                },
                True
            )
            return data
        except Exception:
            return None

    async def hash_cache(self, query: str, u_id: UUID) -> Union[RagResult, None]:
        """判断此query的hash是否在表中存在"""
        query_hash = self._get_query_hash(query)
        print(query_hash)
        # 命中hash和user_id
        a_data = await self._catch_hash_and_uid(query_hash, u_id)
        if a_data:
            return RagResult(a_data['summary'], a_data['source_post_ids'])
        return None

    async def semantics_cache(self, query: str, u_id: UUID) -> Union[RagResult, None]:
        """判断此query的hash是否在表中存在"""
        query_embedding_raw = await self._get_query_embedding(query)
        query_embedding = self._format_embedding(query_embedding_raw)
        # 命中向量和user_id
        response = await self.sb.rpc_async("get_similar_summary_by_user", {
            "p_user_id": str(u_id),
            "p_embedding": query_embedding,
            "p_threshold": 0.9  # 设定 90% 的相似度阈值
        })
        if response and len(response) > 0:
            print(f"命中了相似缓存！相似度: {response[0]['similarity']}")
            return RagResult(response[0]['summary'], response[0]['source_post_ids'])
        return None
