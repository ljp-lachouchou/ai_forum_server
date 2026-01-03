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
            async with session.get(str(url), timeout=10) as response:
                response.raise_for_status()
                return await response.text()

    def split_document(self, document: Any) -> List[Any]:  # 假设 Document 类型
        config = self.config_builder.build()
        return config.splitter.split_text(document)

    async def as_vector(self, chunks: List[Any]) -> dict:
        config = self.config_builder.build()
        docs = [page.page_content for page in chunks]

        # 核心：在线程池中运行 BGE-M3 推理
        # 注意：BGE-M3 的输出通常包含 'dense_vecs', 'lexical_weights', 'colbert_vecs'
        # 这里假设你的 config.bge_model 返回的是 FlagModel 包装后的结果
        vectors = await asyncio.to_thread(config.bge_model, docs)

        # 处理稠密向量
        dense_data = vectors.get("dense")
        if hasattr(dense_data, "tolist"):
            dense_list = dense_data.tolist()
        else:
            dense_list = dense_data

        # 处理稀疏向量（BGE-M3 的词汇权重）
        sparse_data = vectors.get("sparse")

        return {
            "dense": dense_list,
            "sparse": sparse_data
        }

    async def insert_records(self, collection_name: str, records: List[dict]) -> bool:
        client = DBClient.get_client()
        try:
            # Milvus 批量插入
            await asyncio.to_thread(
                client.insert,
                collection_name=collection_name,
                data=records
            )
            return True
        except Exception as e:
            # 这里的 e 会包含 ParamError 信息，现在我们已经通过格式化规避了它
            print(f"Milvus Insert Error: {e}")
            return False

    def _format_sparse_row(self, sparse_vectors, i):
        """
        终极修复：确保返回 Milvus 要求的纯字典格式 {int: float}
        """
        try:
            if hasattr(sparse_vectors, "getrow"):
                row = sparse_vectors.getrow(i)
                return {int(k): float(v) for k, v in zip(row.indices, row.data)}

            row_data = sparse_vectors[i]

            while isinstance(row_data, list) and len(row_data) > 0:
                row_data = row_data[0]

            if isinstance(row_data, dict):
                formatted = {int(k): float(v) for k, v in row_data.items()}
                return formatted

            # 5. 如果剥离后不是字典，返回空字典以防崩溃
            return {}

        except Exception as e:
            print(f"[_format_sparse_row] Error at index {i}: {e}")
            return {}

    async def save_generic(self, collection_name: str, chunks: List[Document],
                           vector_dict: dict, mapper_func, word_model: MDWord) -> bool:
        dense_vectors = vector_dict.get("dense")
        sparse_vectors = vector_dict.get("sparse")

        insert_data = []
        for i, chunk in enumerate(chunks):
            dense_vec = dense_vectors[i]
            sparse_vec = self._format_sparse_row(sparse_vectors, i)

            if isinstance(sparse_vec, list):
                print(f"WARNING: sparse_vec is still a list at index {i}: {sparse_vec}")
                if len(sparse_vec) > 0: sparse_vec = sparse_vec[0]

            record = mapper_func(chunk, dense_vec, sparse_vec, word_model)
            insert_data.append(record)

        return await self.insert_records(collection_name, insert_data)