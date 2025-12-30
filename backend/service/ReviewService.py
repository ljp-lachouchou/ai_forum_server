from uuid import UUID
from typing import Dict

from backend.Sql.enums import WordStatus, WordEventType
from backend.service.WordService import WordService

from uuid import UUID

AI_ACTOR_ID = UUID("00000000-0000-0000-0000-000000000001")
class ReviewService:
    """
    决策层：
    - 决定“是否允许状态变化”
    - 不直接操作数据库
    """

    def __init__(self, word_service: WordService):
        self.word_service = word_service

    # =========================
    # AI 审核
    # =========================

    async def ai_review(
        self,
        word_id: UUID,
        ai_result: Dict,
    ) -> None:
        """
        AI 只写事件，不改变状态
        """
        #  读取当前 word
        word = await self.word_service.get_word(word_id)

        current_status = WordStatus(word["status"])
        if current_status != WordStatus.PENDING:
            raise ValueError("AI review only allowed when status is pending")

        # 记录 AI 审核事件
        await self.word_service._write_event(
            word_id=word_id,
            event_type=WordEventType.AI_REVIEW,
            actor_type="ai",
            actor_id=AI_ACTOR_ID,
            payload=ai_result,
        )

    # =========================
    # 管理员审核（通过）
    # =========================

    async def approve(
        self,
        word_id: UUID,
        admin_id: UUID,
        ai_required: bool = True,
    ) -> None:
        """
        管理员发布前的统一入口
        """
        word = await self.word_service.get_word(word_id)
        current_status = WordStatus(word["status"])

        if current_status != WordStatus.PENDING:
            raise ValueError("Only pending word can be approved")

        if ai_required:
            await self._ensure_ai_reviewed(word_id)

        # 真正的状态变化交给 WordService
        await self.word_service.publish(word_id, admin_id)

    # =========================
    # 管理员审核（拒绝）
    # =========================

    async def reject(
        self,
        word_id: UUID,
        admin_id: UUID,
        reason: str,
    ) -> None:
        word = await self.word_service.get_word(word_id)
        if WordStatus(word["status"]) != WordStatus.PENDING:
            raise ValueError("Only pending word can be rejected")

        await self.word_service.reject(word_id, admin_id, reason)

    # =========================
    # 内部校验
    # =========================

    async def _ensure_ai_reviewed(self, word_id: UUID) -> None:
        """
        确保已经有 AI_REVIEW 事件
        """
        events = await self.word_service.get_events(word_id)

        for e in events:
            if e["event_type"] == WordEventType.AI_REVIEW.value:
                return

        raise ValueError("AI review required before publish")
