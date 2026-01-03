from langchain_core.messages import SystemMessage, HumanMessage
from langchain_deepseek import ChatDeepSeek



class LLMService:
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError


from openai import AsyncOpenAI


class DeepSeekLLMService(LLMService):
    def __init__(self,modelClient:ChatDeepSeek):
        self.modelClient = modelClient
    async def generate(self, prompt: str) -> str:
        messages = [
            SystemMessage(content="你是一个严谨的知识总结助手"),
            HumanMessage(content=prompt)
        ]
        resp  = await self.modelClient.ainvoke(messages)
        return resp.content.strip()


