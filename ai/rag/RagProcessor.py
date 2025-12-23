"""
Rag的整个流程
提供规范
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Union

import aiohttp
from langchain_core.documents import Document

from ai.rag.RagConfiguration import RagConfigurationBuilder


class RagProcessor(ABC):
    @abstractmethod
    async def upload_document(self, source:  Union[str, Path]) -> str:
        """加载原始文档"""
        pass

    @abstractmethod
    def split_document(self, document: Any) -> List[Document]:
        """将文档分割成块 (Chunks)"""
        pass

    @abstractmethod
    def as_vector(self, chunks: List[Document]) -> List[List[float]]:
        """将块内容转为向量列表"""
        pass

    @abstractmethod
    def save(self, chunks: List[Document], vectors: List[List[float]]) -> bool:
        """保存到向量数据库 (如 Milvus)"""
        pass
class BaseRagProcessor(RagProcessor,ABC):
    def __init__(self,config_builder:RagConfigurationBuilder):
        self.config_builder = config_builder

class MDMilvusRagProcessor(BaseRagProcessor):
    async def upload_document(self, url: Union[str, Path]) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.text()

    def split_document(self, document: Any) -> List[Document]:
        config = self.config_builder.build()
        return config.splitter.split_text(document)

    def as_vector(self, chunks: List[Document]) -> List[List[float]]:
        config = self.config_builder.build()
        docs = [page.page_content for page in chunks]
        return config.embedding_model.embed_documents(docs)

    def save(self, chunks: List[Document], vectors: List[List[float]]) -> bool:
        data = [
            vectors,  # Field: vector
            [doc.page_content for doc in chunks],  # Field: text
            [doc.metadata for doc in chunks]  # Field: metadata (JSON 格式)
        ]