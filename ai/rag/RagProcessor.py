"""
Rag的整个流程
提供规范
"""
from abc import ABC, abstractmethod
from typing import Any, List

from ai.rag.RagConfiguration import RagConfigurationBuilder


class RagProcessor(ABC):
    @abstractmethod
    def upload_documents(self, source: Any) -> List[Any]:
        """加载原始文档"""
        pass

    @abstractmethod
    def split_documents(self, documents: List[Any]) -> List[Any]:
        """将文档分割成块 (Chunks)"""
        pass

    @abstractmethod
    def as_vector(self, chunks: List[Any]) -> List[List[float]]:
        """将块内容转为向量列表"""
        pass

    @abstractmethod
    def save(self, chunks: List[Any], vectors: List[List[float]]) -> bool:
        """保存到向量数据库 (如 Milvus)"""
        pass
class BaseRagProcessor(RagProcessor,ABC):
    def __init__(self,config_builder:RagConfigurationBuilder):
        self.config_builder = config_builder

