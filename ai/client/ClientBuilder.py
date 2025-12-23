import os
from enum import Enum

from langchain_deepseek import ChatDeepSeek
from langchain_openai.chat_models.base import BaseChatOpenAI


class ClientType(Enum):
    DeepSeek = (ChatDeepSeek,)
    def __init__(self, chat_class):
        self.chat_engine_class = chat_class

    def create_instance(self, **kwargs):
        return self.chat_engine_class(**kwargs)


class ClientBuilder:
    def __init__(self,clientType:ClientType,api_key_tag = 'DEEPSEEK_API_KEY',base_url = "https://api.deepseek.com",model = "deepseek-chat"):
        self.api_key = os.environ.get(api_key_tag)
        self.base_url = base_url
        self.model = model
        self.clientType = clientType
    def build(self):
        return self.clientType.create_instance(api_key = self.api_key,
                          base_url = self.base_url,
                          model = self.model)

