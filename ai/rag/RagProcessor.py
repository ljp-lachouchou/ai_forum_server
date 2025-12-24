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
    async def save(self, chunks: List[Document], vector_dict: dict, word_model: MDWord,collection_name = "md_word_mixed_collection",) -> bool:
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

    async def save(self, chunks: List[Document], vector_dict: dict, word_model: MDWord,
             collection_name="md_word_mixed_collection", ) -> bool:
        client = DBClient.get_client()

        try:
            insert_data = []
            dense_vectors = vector_dict.get("dense")
            sparse_vectors = vector_dict.get("sparse")

            for i, chunk in enumerate(chunks):
                # --- 关键修复：正确从 Scipy 矩阵提取单行并转为字典 ---
                try:
                    row = sparse_vectors.getrow(i)
                    formatted_sparse = {
                        int(index): float(value)
                        for index, value in zip(row.indices, row.data)
                    }
                except AttributeError:
                    raw_sparse = sparse_vectors[i]
                    formatted_sparse = raw_sparse if isinstance(raw_sparse, dict) else raw_sparse

                record = {
                    "word_id": str(word_model.id),
                    "raw_text": chunk.page_content,
                    "dense_vector": dense_vectors[i],
                    "sparse_vector": formatted_sparse,
                    "entity_info": {
                        "word_name": word_model.word_name,
                        "author_id": word_model.author_id,
                        "category": word_model.category,
                        "create_time": word_model.create_time,
                        "tags": [tag.id for tag in word_model.word_tags],
                        "is_delete": word_model.is_delete
                    }
                }
                insert_data.append(record)

            await asyncio.to_thread(
                client.insert,
                collection_name=collection_name,
                data=insert_data
            )
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Milvus Save Error: {e}")
            return False