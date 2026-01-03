from uuid import UUID
from typing import List

from backend.Sql.SClient import SupabaseClient


class BookmarkService:
    """
    收藏服务（关系型次级资源）
    - bookmarks 表 = 是否存在
    """

    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    # =========================
    # 添加收藏
    # =========================

    async def add_bookmark(
        self,
        user_id: UUID,
        post_id: UUID,
    ):
        """
        添加收藏
        - 复合主键会天然防止重复收藏
        """
        return await self.sb.insert_async(
            "bookmarks",
            {
                "user_id": str(user_id),
                "post_id": str(post_id),
            },
        )

    # =========================
    # 取消收藏
    # =========================

    async def remove_bookmark(
        self,
        user_id: UUID,
        post_id: UUID,
    ) -> None:
        """
        取消收藏
        """
        await self.sb.delete_async(
            "bookmarks",
            {
                "user_id": str(user_id),
                "post_id": str(post_id),
            },
        )

    # =========================
    # 判断是否已收藏
    # =========================

    async def is_bookmarked(
        self,
        user_id: UUID,
        post_id: UUID,
    ) -> bool:
        """
        是否已收藏
        """
        data = await self.sb.select_async(
            "bookmarks",
            filters={
                "user_id": str(user_id),
                "post_id": str(post_id),
            },
        )
        return len(data) > 0

    # =========================
    # 获取用户收藏列表
    # =========================

    async def list_user_bookmarks(
        self,
        user_id: UUID,
    ) -> List[dict]:
        """
        获取用户收藏的所有 post
        """
        return await self.sb.select_async(
            "bookmarks",
            filters={"user_id": str(user_id)},
        )
