import httpx
from typing import List
from uuid import UUID


class WordContentService:
    """
    根据 word_id -> word_url -> 拉取 md 内容
    """

    def __init__(self, word_service):
        self.words = word_service

    async def get_contents(self, word_ids: List[UUID]) -> List[str]:
        """
        批量获取 md 内容
        """
        # 1️⃣ 查 word_url
        words = await self.words.get_words_by_ids(word_ids)

        urls = [
            w["word_url"]
            for w in words
            if w.get("word_url")
        ]

        if not urls:
            return []

        # 2️⃣ 拉 md 内容
        contents: List[str] = []

        async with httpx.AsyncClient(timeout=10) as client:
            for url in urls:
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    contents.append(resp.text)
                except Exception as e:
                    # ⚠️ 单个失败不影响整体
                    contents.append("")

        return contents
