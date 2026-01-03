from typing import List, Optional
from uuid import UUID

from backend.Sql.SClient import SupabaseClient


class RagSummaryService:
    """
    RAG 搜索结果缓存服务（query-level）
    """

    TABLE = "rag_summaries"

    def __init__(self, sb: SupabaseClient):
        self.sb = sb

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

    async def save(
        self,
        query: str,
        query_hash: str,
        summary: str,
        source_post_ids: List[UUID],
    ) -> None:
        """
        保存一次 RAG 搜索总结（不可变）
        """
        await self.sb.insert_async(
            self.TABLE,
            {
                "query": query,
                "query_hash": query_hash,
                "summary": summary,
                "source_post_ids": [str(pid) for pid in source_post_ids],
            },
        )
