from typing import Optional
from uuid import UUID

from backend.Sql.SClient import SupabaseClient


class AIPostReviewService:
    """
    Service for ai_post_reviews table.
    """

    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    async def create_review(self, post_id: UUID, result: str, reason: Optional[str] = None):
        return await self.sb.insert_async(
            "ai_post_reviews",
            {
                "post_id": str(post_id),
                "result": result,
                "reason": reason,
            },
        )
