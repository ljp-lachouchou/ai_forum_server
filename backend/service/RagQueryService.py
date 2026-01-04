from typing import List


from backend.service.HybridSearchService import HybridSearchService
from backend.service.LLMService import LLMService

from dataclasses import dataclass
from uuid import UUID



@dataclass
class RagResult:
    answer: str
    word_ids: List[UUID]
    # context_preview: str | None = None

class RagQueryService:
    """
    RAG 的唯一对外入口
    """

    def __init__(
        self,
        search_service:HybridSearchService,        # HybridSearchService
        llm_service:LLMService,
        max_chars: int = 3000,
    ):
        self.search = search_service
        self.llm = llm_service
        self.max_chars = max_chars

    def _build_prompt(self, query: str, context: str) -> str:
        return f"""
    你是一个知识总结助手。

    请严格 **只基于给定资料** 回答问题，不要使用外部知识。

    【资料】
    {context}

    【问题】
    {query}

    【要求】
    - 回答必须来自资料
    - 回答请更加生动形象
    - 若资料中未明确说明，请回答「资料不足，无法确定」
    """

    def _build_context(self, documents: List[str]) -> str:
        """
        拼接文档内容，防止 token 爆炸
        """
        context = ""
        for doc in documents:
            if len(context) + len(doc) > self.max_chars:
                break
            context += f"\n---\n{doc}"

        return context

    async def query(
            self,
            query: str,
            top_k: int = 5,
    ) -> RagResult:

        try:
            chunks = await self.search.search(query=query, limit=top_k)
        except Exception as e:
            print(f'报错啥意思？：{e}')
            return RagResult(
                answer="检索服务暂时不可用。",
                word_ids=[],
            )
        print(f"资料: {chunks}")
        if not chunks:
            return RagResult(
                answer="没有找到相关资料。",
                word_ids=[],
            )

        # 1️⃣ 拼接上下文（来自 Milvus）
        documents = [c.raw_text for c in chunks]
        context = self._build_context(documents)

        # 2️⃣ Prompt
        prompt = self._build_prompt(query, context)

        # 3️⃣ LLM
        answer = await self.llm.generate(prompt)

        return RagResult(
            answer=answer,
            word_ids=list({c.word_id for c in chunks}),
        )

