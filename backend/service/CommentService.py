from uuid import UUID
from typing import List

from backend.Sql.SClient import SupabaseClient


class CommentService:
    """
    评论服务（次级领域对象）
    - 只负责 comments 表
    - 不影响 word / post 状态
    """

    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    # =========================
    # 创建评论
    # =========================

    async def create_comment(
        self,
        post_id: UUID,
        author_id: UUID,
        content: str,
    ):
        """
        创建评论
        """
        return await self.sb.insert_async(
            "comments",
            {
                "post_id": str(post_id),
                "author_id": str(author_id),
                "content": content,
            },
        )

    # =========================
    # 查询某个 post 下的评论
    # =========================

    async def list_comments(
        self,
        post_id: UUID,
    ) -> List[dict]:
        """
        获取某个 post 的全部评论（按时间升序）
        """
        return await self.sb.select_async(
            "comments",
            filters={"post_id": str(post_id)},
            order_by="created_at",
        )

    # =========================
    # 删除评论（仅作者本人）
    # =========================

    async def delete_comment(
        self,
        comment_id: UUID,
        author_id: UUID,
    ) -> None:
        """
        仅允许作者删除自己的评论
        """
        comment = await self.sb.select_async(
            "comments",
            filters={"id": str(comment_id)},
            single=True,
        )

        if comment["author_id"] != str(author_id):
            raise PermissionError("Cannot delete others' comments")
        await self.sb.delete_async(
            "comments",
            {"id": str(comment_id)},
        )
