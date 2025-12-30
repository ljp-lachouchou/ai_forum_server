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
    ) -> Dict:
        word = await self.sb.insert_async("words", {
            "author_id": str(author_id),
            "word_url": word_url,
            "category": category,
            "tags": tags,
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
