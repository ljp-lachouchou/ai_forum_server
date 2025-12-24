"""
Rag的整个流程
提供规范
"""
import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Union

import aiohttp
from langchain_core.documents import Document

from ai.db.DBClient import DBClient
from ai.rag.RagConfiguration import RagConfigurationBuilder
from backend.entity.MDword import MDWord


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
    async def as_vector(self, chunks: List[Document]) -> dict:
        """将块内容转为向量列表"""
        pass
    @abstractmethod
    async def insert_records(self, collection_name: str, records: List[dict]) -> bool:
        """
        保存方法
        :param collection_name:
        :param records:
        :return:
        """
        pass

    @abstractmethod
    async def save_generic(self, collection_name: str, chunks: List[Document],
                           vector_dict: dict, mapper_func,word_model:MDWord) -> bool:
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

    async def as_vector(self, chunks: List[Document]) -> dict:
        config = self.config_builder.build()
        docs = [page.page_content for page in chunks]
        vectors = await asyncio.to_thread(config.bge_model, docs)
        dense_data = vectors["dense"]
        if hasattr(dense_data, "tolist"):
            dense_list = dense_data.tolist()
        else:
            dense_list = dense_data  # 已经是 list 了
        sparse_list = vectors["sparse"]

        return {
            "dense": dense_list,
            "sparse": sparse_list
        }

    async def insert_records(self, collection_name: str, records: List[dict]) -> bool:
        """
        最底层的通用插入方法，只负责异步 IO
        """
        client = DBClient.get_client()
        try:
            await asyncio.to_thread(
                client.insert,
                collection_name=collection_name,
                data=records
            )
            return True
        except Exception as e:
            print(f"Milvus Insert Error: {e}")
            return False

    def _format_sparse_row(self, sparse_vectors, i):
        """
        提取并格式化稀疏向量的通用逻辑
        """
        try:
            row = sparse_vectors.getrow(i)
            return {int(k): float(v) for k, v in zip(row.indices, row.data)}
        except AttributeError:
            raw = sparse_vectors[i]
            return raw if isinstance(raw, dict) else raw

    async def save_generic(self, collection_name: str, chunks: List[Document],
                           vector_dict: dict, mapper_func,word_model:MDWord) -> bool:
        """
        通用的保存逻辑，接受一个 mapper 函数来构造每条记录
        """
        dense_vectors = vector_dict.get("dense")
        sparse_vectors = vector_dict.get("sparse")

        insert_data = []
        for i, chunk in enumerate(chunks):
            # 获取基础向量数据
            dense_vec = dense_vectors[i]
            sparse_vec = self._format_sparse_row(sparse_vectors, i)

            # 调用传入的 mapper 构造最终的 record 字典
            record = mapper_func(chunk, dense_vec, sparse_vec,word_model)
            insert_data.append(record)

        return await self.insert_records(collection_name, insert_data)