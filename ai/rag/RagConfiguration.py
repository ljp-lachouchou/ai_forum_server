"""
完成整个rag流程所需要的一些配置
"""
from dataclasses import dataclass
from typing import Optional

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.vectorstores import VectorStore

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import TextSplitter, MarkdownHeaderTextSplitter


class RagConfigurationBuilder:
    """
    embedding_model: 转为向量的模型
    splitter: 文档分割者
    content_loader: 内容加载器
    db_instance: 数据库连接实例
    """
    def __init__(self,embedding_model,splitter,content_loader,db_instance):
        self.embedding_model = embedding_model
        self.splitter = splitter
        self.content_loader = content_loader
        self.db_instance = db_instance
        self.__config : Optional[RagConfiguration] = None

    def set_embedding_model(self,em):
        self.embedding_model = em
        return self

    def set_splitter(self,sp):
        self.splitter = sp
        return self

    def set_content_loader(self,cl):
        self.content_loader = cl
        return self

    def set_db_instance(self,di):
        self.db_instance = di
        return self

    def build(self):
        if self.__config is None:
            self.__config = RagConfiguration(
            self.embedding_model,
            self.splitter,
            self.content_loader,
            self.db_instance
        )
        return self.__config
@dataclass(frozen=True)
class RagConfiguration:
    embedding_model:OpenAIEmbeddings
    splitter:MarkdownHeaderTextSplitter | TextSplitter
    content_loader:UnstructuredMarkdownLoader
    db_instance:VectorStore
