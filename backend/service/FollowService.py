from uuid import UUID
from typing import List

from backend.Sql.SClient import SupabaseClient


class FollowService:
    """
    Follow service for follows table.
    """

    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    async def follow(self, user_id: UUID, follow_id: UUID):
        return await self.sb.insert_async(
            "follows",
            {
                "user_id": str(user_id),
                "follow_id": str(follow_id),
            },
        )

    async def unfollow(self, user_id: UUID, follow_id: UUID) -> None:
        await self.sb.delete_async(
            "follows",
            {
                "user_id": str(user_id),
                "follow_id": str(follow_id),
            },
        )

    async def list_following(self, user_id: UUID) -> List[dict]:
        return await self.sb.select_async(
            "follows",
            filters={"user_id": str(user_id)},
        )
