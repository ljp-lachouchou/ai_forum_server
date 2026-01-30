from uuid import UUID
from typing import List

from backend.Sql.SClient import SupabaseClient


class LikeService:
    """
    点赞服务（关系型次级资源）
    - likes 表 = 是否存在
    """

    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    async def add_like(self, user_id: UUID, post_id: UUID):
        return await self.sb.insert_async(
            "likes",
            {
                "user_id": str(user_id),
                "post_id": str(post_id),
            },
        )

    async def remove_like(self, user_id: UUID, post_id: UUID) -> None:
        await self.sb.delete_async(
            "likes",
            {
                "user_id": str(user_id),
                "post_id": str(post_id),
            },
        )

    async def is_liked(self, user_id: UUID, post_id: UUID) -> bool:
        data = await self.sb.select_async(
            "likes",
            filters={
                "user_id": str(user_id),
                "post_id": str(post_id),
            },
        )
        return len(data) > 0

    async def toggle_like(self, user_id: UUID, post_id: UUID) -> bool:
        if await self.is_liked(user_id, post_id):
            await self.remove_like(user_id, post_id)
            return False
        await self.add_like(user_id, post_id)
        return True

    async def list_user_likes(self, user_id: UUID) -> List[dict]:
        return await self.sb.select_async(
            "likes",
            filters={"user_id": str(user_id)},
        )
