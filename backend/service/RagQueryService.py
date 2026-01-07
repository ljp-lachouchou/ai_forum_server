from typing import List, Any, Optional

from backend.service.HybridSearchService import HybridSearchService
from backend.service.LLMService import LLMService

from dataclasses import dataclass
from uuid import UUID



@dataclass
class RagResult:
    answer: Optional[str]
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

    def _build_prompt(self, query: str, context: str,persona:dict = None) -> str:
        persona_context = ""
        if persona:
            tags = persona.get("behavioral_tags", [])
            summary = persona.get("bio_summary", "")
            persona_context = f"""
        【用户画像（请根据此画像调整你的回复语气和侧重点）】
        - 兴趣标签：{', '.join(tags)}
        - 核心特征：{summary}
        """
        return f"""
        你是一个专业且贴心的知识总结助手。
        {persona_context}

        请严格 **只基于给定资料** 回答问题，不要使用外部知识。

        【资料】
        {context}

        【问题】
        {query}

        【要求】
        1. **内容限制**：回答内容必须完全来自资料。若资料未提及，请回答「资料不足，无法确定」。
        2. **风格定制**：请结合【用户画像】中的特征来组织语言。
        3. **语言**：中文。
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
            persona:dict,
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
        prompt = self._build_prompt(query, context,persona)

        # 3️⃣ LLM
        answer = await self.llm.generate(prompt)

        return RagResult(
            answer=answer,
            word_ids=list({c.word_id for c in chunks}),
        )

