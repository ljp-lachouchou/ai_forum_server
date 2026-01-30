from typing import List, Optional
from uuid import UUID

from backend.Sql.SClient import SupabaseClient


class NotificationService:
    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    async def create_notification(
        self,
        user_id: UUID,
        n_type: str,
        content: str,
        ref_type: Optional[str] = None,
        ref_id: Optional[UUID] = None,
    ):
        payload = {
            "user_id": str(user_id),
            "type": n_type,
            "content": content,
            "is_read": False,
        }
        if ref_type:
            payload["ref_type"] = ref_type
        if ref_id:
            payload["ref_id"] = str(ref_id)
        return await self.sb.insert_async("notifications", payload)

    async def list_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 20,
    ) -> List[dict]:
        query = (
            self.sb._client
            .table("notifications")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(limit)
        )
        if unread_only:
            query = query.eq("is_read", False)
        res = query.execute()
        return res.data or []

    async def mark_read(self, user_id: UUID, notification_ids: List[UUID]) -> List[dict]:
        if not notification_ids:
            return []
        res = (
            self.sb._client
            .table("notifications")
            .update({"is_read": True})
            .eq("user_id", str(user_id))
            .in_("id", [str(nid) for nid in notification_ids])
            .execute()
        )
        return res.data or []

    async def mark_all_read(self, user_id: UUID) -> List[dict]:
        res = (
            self.sb._client
            .table("notifications")
            .update({"is_read": True})
            .eq("user_id", str(user_id))
            .execute()
        )
        return res.data or []
