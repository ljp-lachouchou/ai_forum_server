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

    async def add_like(self, user_id: UUID, post_id: UUID, token: str = None):
        return await self.sb.insert_async(
            "likes",
            {
                "user_id": str(user_id),
                "post_id": str(post_id),
            },
            token=token,
        )

    async def remove_like(self, user_id: UUID, post_id: UUID, token: str = None) -> None:
        await self.sb.delete_async(
            "likes",
            {
                "user_id": str(user_id),
                "post_id": str(post_id),
            },
            token=token,
        )

    async def is_liked(self, user_id: UUID, post_id: UUID, token: str = None) -> bool:
        data = await self.sb.select_async(
            "likes",
            filters={
                "user_id": str(user_id),
                "post_id": str(post_id),
            },
            token=token,
        )
        return len(data) > 0

    async def toggle_like(self, user_id: UUID, post_id: UUID, token: str = None) -> bool:
        if await self.is_liked(user_id, post_id, token=token):
            await self.remove_like(user_id, post_id, token=token)
            return False
        await self.add_like(user_id, post_id, token=token)
        return True

    async def list_user_likes(self, user_id: UUID, token: str = None) -> List[dict]:
        return await self.sb.select_async(
            "likes",
            filters={"user_id": str(user_id)},
            token=token,
        )
