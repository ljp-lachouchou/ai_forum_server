from typing import List, Dict, Optional
from uuid import UUID

from backend.Sql.SClient import SupabaseClient


class SyncService:
    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    async def get_changelog(self, since: int, limit: int = 500) -> Dict:
        changes = (
            self.sb._client
            .table("change_log")
            .select("entity_type, entity_id, change_type, version, changed_at")
            .gt("version", since)
            .order("version", desc=False)
            .limit(limit)
            .execute()
        ).data or []

        version_row = (
            self.sb._client
            .table("change_version")
            .select("version")
            .eq("id", 1)
            .single()
            .execute()
        ).data or {}

        latest_version = version_row.get("version", since)
        return {"latest_version": latest_version, "changes": changes}

    async def get_words(self, ids: List[UUID]) -> List[dict]:
        if not ids:
            return []
        res = (
            self.sb._client
            .table("words")
            .select("*")
            .in_("word_id", [str(i) for i in ids])
            .execute()
        )
        return res.data or []

    async def get_comments(self, ids: List[UUID]) -> List[dict]:
        if not ids:
            return []
        res = (
            self.sb._client
            .table("comments")
            .select("*")
            .in_("id", [str(i) for i in ids])
            .execute()
        )
        return res.data or []

    async def get_treeholes(self, ids: List[UUID]) -> List[dict]:
        if not ids:
            return []
        res = (
            self.sb._client
            .table("treeholes")
            .select("*")
            .in_("id", [str(i) for i in ids])
            .execute()
        )
        return res.data or []

    async def get_profiles(self, ids: List[UUID]) -> List[dict]:
        if not ids:
            return []
        res = (
            self.sb._client
            .table("profiles")
            .select("*")
            .in_("id", [str(i) for i in ids])
            .execute()
        )
        return res.data or []

    async def get_notifications(self, user_id: UUID, ids: List[UUID]) -> List[dict]:
        if not ids:
            return []
        res = (
            self.sb._client
            .table("notifications")
            .select("*")
            .eq("user_id", str(user_id))
            .in_("id", [str(i) for i in ids])
            .execute()
        )
        return res.data or []

    async def get_likes(self, ids: List[UUID], user_id: Optional[UUID] = None) -> List[dict]:
        if not ids:
            return []
        query = (
            self.sb._client
            .table("likes")
            .select("*")
            .in_("id", [str(i) for i in ids])
        )
        if user_id:
            query = query.eq("user_id", str(user_id))
        res = query.execute()
        return res.data or []

    async def get_bookmarks(self, ids: List[UUID], user_id: Optional[UUID] = None) -> List[dict]:
        if not ids:
            return []
        query = (
            self.sb._client
            .table("bookmarks")
            .select("*")
            .in_("id", [str(i) for i in ids])
        )
        if user_id:
            query = query.eq("user_id", str(user_id))
        res = query.execute()
        return res.data or []

    async def get_follows(self, ids: List[UUID], user_id: Optional[UUID] = None) -> List[dict]:
        if not ids:
            return []
        query = (
            self.sb._client
            .table("follows")
            .select("*")
            .in_("id", [str(i) for i in ids])
        )
        if user_id:
            query = query.eq("user_id", str(user_id))
        res = query.execute()
        return res.data or []
