from typing import List, Optional
from uuid import UUID

from backend.Sql.SClient import SupabaseClient


class TreeholeService:
    """
    树洞服务
    - treeholes 表
    - treehole_ai_replies 表（可选）
    """

    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    async def create_treehole(
        self,
        author_id: UUID,
        content: str,
        is_anonymous: bool = True,
        mood: str = "平常",
        token: str = None,
    ):
        return await self.sb.insert_async(
            "treeholes",
            {
                "author_id": str(author_id),
                "content": content,
                "is_anonymous": is_anonymous,
                "mood": mood,
            },
            token=token,
        )

    async def list_treeholes(
        self,
        limit: int = 20,
        offset: int = 0,
        include_ai: bool = False,
    ) -> List[dict]:
        rows = await self.sb.select_async(
            "treeholes",
            order_by="created_at",
            desc=True,
        )
        rows = rows or []
        sliced = rows[offset: offset + limit]

        if not include_ai or not sliced:
            return sliced

        ids = [row.get("id") for row in sliced if row.get("id")]
        if not ids:
            return sliced

        replies = await self.sb.mutil_select_async(
            "treehole_ai_replies",
            tar_in_column="treehole_id",
            in_s=ids,
            filters={},
        )

        reply_map = {}
        for reply in replies or []:
            tid = reply.get("treehole_id")
            if tid not in reply_map:
                reply_map[tid] = []
            reply_map[tid].append(reply)

        for row in sliced:
            row["ai_replies"] = reply_map.get(row.get("id"), [])

        return sliced

    async def create_ai_reply(self, treehole_id: UUID, content: str, token: str = None):
        return await self.sb.insert_async(
            "treehole_ai_replies",
            {
                "treehole_id": str(treehole_id),
                "content": content,
            },
            token=token,
        )
