from typing import List, Dict, Optional
from uuid import UUID

from backend.Sql.SClient import SupabaseClient
from backend.Sql.enums import WordStatus, WordEventType


class WordService:
    """
    纯业务层：
    - 不处理 HTTP
    - 不处理 JWT
    - 不关心 Supabase SDK 细节
    """

    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    # =========================
    # 基础 CRUD
    # =========================

    async def create_word(
            self,
            author_id: UUID,
            word_url: str,
            category: str,
            tags: List[str],
            word_name: Optional[str] = None,
    ) -> Dict:
        word = await self.sb.insert_async("words", {
            "author_id": str(author_id),
            "word_url": word_url,
            "category": category,
            "tags": tags,
            "word_name": word_name,
            "status": WordStatus.DRAFT.value,
        })

        word_id = word[0]["word_id"]

        await self._write_event(
            word_id=word_id,
            event_type=WordEventType.CREATE,
            actor_type="user",
            actor_id=author_id,
        )

        return word[0]

    async def get_words_by_ids(
            self,
            word_ids: List[UUID],
    ) -> List[dict]:
        """
        根据 word_id 批量获取 words 记录
        """
        if not word_ids:
            return []

        res = (
            self.sb._client
            .table("words")
            .select("word_id, word_url, status")
            .in_("word_id", [str(wid) for wid in word_ids])
            .eq("status", "published")  # ✅ 状态过滤
            .execute()
        )

        return res.data or []

    async def update_word(
            self,
            word_id: UUID,
            author_id: UUID,
            payload: Dict,
    ) -> None:
        word = await self._get_word_or_raise(word_id)

        if word["author_id"] != str(author_id):
            raise PermissionError("Not the author")

        current_status = WordStatus(word["status"])
        if current_status not in (WordStatus.DRAFT, WordStatus.REJECTED):
            raise ValueError("Word cannot be updated in current status")

        await self.sb.update_async(
            "words",
            payload,
            {"word_id": str(word_id)},
        )

        await self._write_event(
            word_id=word_id,
            event_type=WordEventType.UPDATE,
            actor_type="user",
            actor_id=author_id,
            payload={"fields": list(payload.keys())},
        )

    async def get_word(self, word_id: UUID) -> Dict:
        return await self._get_word_or_raise(word_id)

    async def list_words(
            self,
            status: Optional[WordStatus] = None,
            category: Optional[str] = None,
    ):
        filters = {}
        if status:
            filters["status"] = status.value
        if category:
            filters["category"] = category

        return await self.sb.select_async("words", filters=filters)

    async def list_feed(
        self,
        mode: str = "latest",
        category: Optional[str] = None,
        user_id: Optional[UUID] = None,
        limit: int = 20,
    ) -> List[dict]:
        query = (
            self.sb._client
            .table("words")
            .select("*")
            .eq("status", WordStatus.PUBLISHED.value)
        )
        if category:
            query = query.eq("category", category)

        if mode == "latest":
            query = query.order("created_at", desc=True)
        elif mode == "recommend":
            # TODO: replace with real recommendation ranking logic.
            query = query.order("updated_at", desc=True)
        elif mode == "follow":
            # TODO: replace follow lookup with dedicated follow service when ready.
            if not user_id:
                return []
            follow_rows = (
                self.sb._client
                .table("follows")
                .select("follow_id")
                .eq("user_id", str(user_id))
                .execute()
            )
            follow_ids = [row["follow_id"] for row in (follow_rows.data or [])]
            if not follow_ids:
                return []
            query = query.in_("author_id", follow_ids).order("created_at", desc=True)
        else:
            raise ValueError("Invalid feed mode")

        res = query.limit(limit).execute()
        return res.data or []

    async def list_words_by_ids(self, tar_in_column: str,
                                ids: list, status: Optional[WordStatus] = WordStatus.PUBLISHED):
        filters = {}
        if status:
            filters["status"] = status.value
        return await self.sb.mutil_select_async("words",
                                                filters=filters,
                                                in_s=ids,
                                                tar_in_column=tar_in_column)

    # =========================
    # 状态流转（核心业务）
    # =========================

    async def submit_review(self, word_id: UUID, author_id: UUID) -> None:
        await self._update_status(
            word_id,
            WordStatus.PENDING,
            WordEventType.SUBMIT_REVIEW,
            actor_type="user",
            actor_id=author_id,
        )

    async def publish(self, word_id: UUID, admin_id: UUID) -> None:
        await self._update_status(
            word_id,
            WordStatus.PUBLISHED,
            WordEventType.PUBLISH,
            actor_type="admin",
            actor_id=admin_id,
        )

    async def reject(
            self,
            word_id: UUID,
            admin_id: UUID,
            reason: str,
    ) -> None:
        await self._update_status(
            word_id,
            WordStatus.REJECTED,
            WordEventType.REJECT,
            actor_type="admin",
            actor_id=admin_id,
            payload={"reason": reason},
        )

    async def revise(self, word_id: UUID, author_id: UUID) -> None:
        await self._update_status(
            word_id,
            WordStatus.DRAFT,
            WordEventType.REVISE,
            actor_type="user",
            actor_id=author_id,
        )

    async def archive(self, word_id: UUID, admin_id: UUID) -> None:
        await self._update_status(
            word_id,
            WordStatus.ARCHIVED,
            WordEventType.ARCHIVE,
            actor_type="admin",
            actor_id=admin_id,
        )

    # =========================
    # 事件流
    # =========================

    async def get_events(self, word_id: UUID):
        return await self.sb.select_async(
            "word_events",
            filters={"word_id": str(word_id)},
        )

    async def get_latest_reject_reason(self, word_id: UUID) -> Optional[str]:
        res = (
            self.sb._client
            .table("word_events")
            .select("payload")
            .eq("word_id", str(word_id))
            .eq("event_type", WordEventType.REJECT.value)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        data = res.data or []
        if not data:
            return None
        payload = data[0].get("payload") or {}
        if isinstance(payload, dict):
            return payload.get("reason")
        return None

    # =========================
    # 内部工具方法（核心价值）
    # =========================

    async def _get_word_or_raise(self, word_id: UUID) -> Dict:
        return await self.sb.select_async(
            "words",
            filters={"word_id": str(word_id)},
            single=True,
        )

    async def _update_status(
            self,
            word_id: UUID,
            new_status: WordStatus,
            event_type: WordEventType,
            actor_type: str,
            actor_id: UUID,
            payload: Optional[Dict] = None,
    ) -> None:
        """
        所有状态变化唯一入口
        """
        await self.sb.update_async(
            "words",
            {"status": new_status.value},
            {"word_id": str(word_id)},
        )

        await self._write_event(
            word_id=word_id,
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            payload=payload,
        )

    async def _write_event(
            self,
            word_id: UUID,
            event_type: WordEventType,
            actor_type: str,
            actor_id: UUID,
            payload: Optional[Dict] = None,
    ) -> None:
        await self.sb.insert_async("word_events", {
            "word_id": str(word_id),
            "event_type": event_type.value,
            "actor_type": actor_type,
            "actor_id": str(actor_id),
            "payload": payload,
        })

    def filter_published_ids(
            self,
            ids: List[UUID],
    ) -> List[UUID]:
        """
        只返回 status = published 的文档 ID
        """
        rows = self.sb._client.table("words") \
            .select("word_id") \
            .in_("word_id", [str(i) for i in ids]) \
            .eq("status", "published") \
            .execute()

        return [UUID(r["word_id"]) for r in rows.data]
