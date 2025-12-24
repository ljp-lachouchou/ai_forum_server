import asyncio
import os

from langchain_text_splitters import MarkdownHeaderTextSplitter
from milvus_model.hybrid import BGEM3EmbeddingFunction

from ai.db.DBClient import DBClient
from ai.rag import RagConfiguration
from ai.rag.RagConfiguration import RagConfigurationBuilder
from ai.rag.RagManager import RagManager
from ai.rag.RagProcessor import MDMilvusRagProcessor
from backend.entity.MDword import MDWord
from backend.entity.WordTag import WordTag


async def test():

    manager = RagManager(RagConfigurationBuilder,MDMilvusRagProcessor)
    manager.build(bge_model = BGEM3EmbeddingFunction(model_name = "C:\\Users\\ljp\\PycharmProjects\\Forum\\model\\bge-m3",use_fp16=False, device="cpu"),
            splitter = MarkdownHeaderTextSplitter(headers_to_split_on = [
                                    ("#", "Header 1"),
                                    ("##", "Header 2"),
                                    ("###", "Header 3"),
                                ]),
            content_loader = None,
            db_instance = DBClient.get_client())
    tags = [
        WordTag(id="tag_001", display_content="Python"),
        WordTag(id="tag_002", display_content="向量数据库")
    ]

    # 2. 创建文档对象
    example_word = MDWord(
        id="doc_2025_001",
        word_name="如何使用 Milvus 实现混合检索",
        author_id="user_ljp_99",
        word_url="https://hf-mirror.com/api/resolve-cache/models/BAAI/bge-m3/5617a9f61b028005a4858fdac845db406aefb181/README.md?download=true&etag=%22e5a320176edd6ee1cfb256e68ee5ac0004de9447%22",
        word_tags=tags,
        likes=128,
        views=1024,
        category="AI教程",
        is_delete=False,
    )
    await manager.start_process(example_word)
