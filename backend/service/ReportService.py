from typing import Optional
from uuid import UUID

from backend.Sql.SClient import SupabaseClient


class ReportService:
    """
    举报服务
    - reports 表
    """

    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    async def create_report(
        self,
        reporter_id: Optional[UUID],
        target_type: str,
        target_id: UUID,
        reason: str,
    ):
        return await self.sb.insert_async(
            "reports",
            {
                "reporter_id": str(reporter_id) if reporter_id else None,
                "target_type": target_type,
                "target_id": str(target_id),
                "reason": reason,
            },
        )
