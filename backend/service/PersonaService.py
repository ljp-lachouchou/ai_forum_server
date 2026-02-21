import json
from uuid import UUID
from typing import List, Dict, Any, Tuple
import re
from backend.Sql.SClient import SupabaseClient
from backend.service.LLMService import LLMService


class PersonaService:
    def __init__(self, supabase_client: SupabaseClient, llm_service: LLMService):
        self.client = supabase_client
        self.llm = llm_service

    @staticmethod
    def _default_persona_data(u_id: UUID) -> Dict[str, Any]:
        return {
            "id": str(u_id),
            "stats": {},
            "behavioral_tags": [],
            "bio_summary": "",
        }

    async def _get_data_and_stats(self, u_id: UUID) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """获得这条数据"""
        rows = await self.client.select_async("user_personas", {
            "id": str(u_id)
        })

        if isinstance(rows, list) and rows:
            data = rows[0]
        elif isinstance(rows, dict):
            data = rows
        else:
            data = self._default_persona_data(u_id)

        stats = data.get("stats") or {}
        return data, stats

    def _build_tags_context(self, stats: dict):
        return f"""
        你是一个全能型用户行为分析专家。请分析下方的用户点击与时长数据，并提炼用户画像。
        数据： {stats}
        画像提炼规则：
        核心领域：基于 clicks 和 tags 找出用户最关注的 1-2 个话题领域。
        参与程度：结合 dwell_time 判断。如果时长很高，标签应体现“深度研究/热爱”；如果时长极短且点击多，体现“信息快报/快速扫读”。
        标签风格：生成 4-5 个语义化的短标签。描述出用户的生活方式、专业爱好或学习状态等等...。
        输出限制：严格只返回 Python 字符串数组。
        示例参考：
        如果数据是美食类： ["资深吃货", "川菜深度研究者", "追求效率的烹饪者"]
        如果数据是文学类： ["硬核史学爱好者", "深度长文读者", "偏好近现代史"]"""

    async def update_persona_stats_background(
            self,
            user_id: UUID,
            category: str,
            tags: List[str],
            duration: int = 0
    ):
        """
        这个函数将被作为后台任务执行
        更新用户行为
        """
        return await self.client.rpc_async("track_user_with_tags", {
            "u_id": str(user_id),
            "cat_name": category,
            "tag_list": tags,
            "duration_inc": duration
        })

    async def generate_behavioral_tags(self, u_id: UUID):
        """
        使用ai获取这个标签
        :return:
        """
        _, stats = await self._get_data_and_stats(u_id)
        prompt = self._build_tags_context(stats)
        answer = await self.llm.generate(prompt)
        match = re.search(r'\[.*]', answer)
        if match:
            tags_array = json.loads(match.group())
            # 4. 更新到数据库的 behavioral_tags 字段
            return await self.client.update_async("user_personas", {
                "behavioral_tags": tags_array,
                "bio_summary": f"该用户近期侧重于 {', '.join(tags_array)} 的学习。"  # 顺便更新摘要
            }, {"id": str(u_id)})
        return None
