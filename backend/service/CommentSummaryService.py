from typing import Protocol, List, Optional


class CommentStore(Protocol):
    async def list_comments(self, post_id) -> List[dict]:
        ...


class TextGenerator(Protocol):
    async def generate(self, prompt: str) -> str:
        ...


class CommentSummaryService:
    def __init__(
        self,
        comment_store: CommentStore,
        llm_service: TextGenerator,
        max_comments: int = 50,
    ):
        self.comment_store = comment_store
        self.llm_service = llm_service
        self.max_comments = max_comments

    async def summarize_comments(self, post_id, limit: Optional[int] = None) -> dict:
        comments = await self.comment_store.list_comments(post_id)
        if not comments:
            return {"summary": None, "comment_count": 0}

        contents = [c.get("content", "").strip() for c in comments if c.get("content")]
        if not contents:
            return {"summary": None, "comment_count": len(comments)}

        max_items = limit if limit is not None else self.max_comments
        content_block = "\n".join(f"{idx + 1}. {text}" for idx, text in enumerate(contents[:max_items]))
        prompt = (
            "请基于以下评论内容，总结主要观点与分歧点，输出简洁中文总结：\n\n"
            f"{content_block}"
        )
        summary = await self.llm_service.generate(prompt)
        return {"summary": summary, "comment_count": len(comments)}
