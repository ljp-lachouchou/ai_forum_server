"""
将‘流程者‘和’配置‘组合在一起
他更像是对于RagProcessor的代理
"""
from typing import Type, TypeVar, Generic, Optional, Any

from ai.rag.RagConfiguration import  RagConfigurationBuilder
from ai.rag.RagProcessor import BaseRagProcessor
from backend.entity.MDword import MDWord

C = TypeVar("C", bound=RagConfigurationBuilder)
P = TypeVar("P", bound=BaseRagProcessor)

class RagManager(Generic[C,P]):
    def __init__(self, configurationBuilder_cls:Type[C],processor_cls:Type[P]):
        self.configurationBuilder_cls = configurationBuilder_cls
        self.processor_cls = processor_cls
        self.actual_processor: Optional[P] = None

    def build(self, **kwargs):
        # 实例化配置和处理器
        config_builder = self.configurationBuilder_cls(**kwargs)
        self.actual_processor = self.processor_cls(config_builder)

    async def start_process(self, md_word: MDWord):
        if not self.actual_processor:
            raise RuntimeError("请先调用 build()")

        # 代理模式：驱动流水线
        doc = await self.actual_processor.upload_document(md_word.word_url)
        chunks = self.actual_processor.split_document(doc)
        vecs = await self.actual_processor.as_vector(chunks)
        await self.actual_processor.save(chunks, vecs,md_word)