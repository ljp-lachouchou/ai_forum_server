import os
from typing import Optional

from dotenv import load_dotenv
from pymilvus import MilvusClient, DataType
class DBClient:
    __client : Optional[MilvusClient] = None
    @classmethod
    def _create_uri(cls):
        load_dotenv()
        host = os.environ.get('MILVUS_DB_HOST')
        port = os.environ.get('MILVUS_DB_PORT')
        return host,port
    @classmethod
    def get_client(cls):
        if cls.__client is None:
            host,port = cls._create_uri()
            try:
                cl = MilvusClient(uri=f"{host}:{port}",timeout=10)
                cls.__client = cl
            except Exception as e:
                print(f"创建Milvus客户端失败,{e}")
        return cls.__client
def create_title_collection():
    client = DBClient.get_client()
    collection_name = "article_title_collection"

    # 1. 如果已存在则删除 (注意：会清空数据)
    if client.has_collection(collection_name):
        client.drop_collection(collection_name)

    # 2. 定义 Schema
    schema = client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
        description="文章标题混合检索集合"
    )

    # 主键
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    # 关联 ID
    schema.add_field(field_name="word_id", datatype=DataType.VARCHAR, max_length=100)
    # 标题原始文本
    schema.add_field(field_name="title", datatype=DataType.VARCHAR, max_length=500)
    # 稠密向量 (BGE-M3 维度 1024)
    schema.add_field(field_name="title_dense", datatype=DataType.FLOAT_VECTOR, dim=1024)
    # 稀疏向量 (用于关键词精确匹配)
    schema.add_field(field_name="title_sparse", datatype=DataType.SPARSE_FLOAT_VECTOR)

    # 3. 设置索引参数
    index_params = client.prepare_index_params()

    # 稠密向量索引 (使用内积 IP 适合 BGE 模型)
    index_params.add_index(
        field_name="title_dense",
        index_type="IVF_FLAT",
        metric_type="IP",
        params={"nlist": 128}
    )

    # 稀疏向量索引
    index_params.add_index(
        field_name="title_sparse",
        index_type="SPARSE_INVERTED_INDEX",
        metric_type="IP"
    )

    # 4. 正式创建
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params
    )
    print(f"集合 {collection_name} 创建成功！维度: 1024")

if __name__ == "__main__":
    create_title_collection()
def init_collection():
    # 1. 初始化客户端
    load_dotenv()
    host = os.environ.get('MILVUS_DB_HOST')
    port = os.environ.get('MILVUS_DB_PORT')
    client = MilvusClient(uri=f"{host}:{port}")
    collection_name = "md_word_mixed_collection"

    # 2. 如果已存在，先删除（用于测试）
    if client.has_collection(collection_name):
        print(f"{collection_name} 已经被创建")
        return

    # 3. 定义 Schema
    schema = client.create_schema(auto_id=True, enable_dynamic_field=True)

    # 主键
    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
    # 字符串 ID
    schema.add_field(field_name="word_id", datatype=DataType.VARCHAR, max_length=100)
    # 原始文本
    schema.add_field(field_name="raw_text", datatype=DataType.VARCHAR, max_length=65535)

    # --- 注意这里 ---
    # 稠密向量：必须有 dim
    schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=1024)

    # 稀疏向量：千万不能加 dim 参数
    schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
    # ----------------

    # 元数据 JSON
    schema.add_field(field_name="entity_info", datatype=DataType.JSON)

    # 4. 配置索引参数
    index_params = client.prepare_index_params()

    # 稠密向量索引
    index_params.add_index(
        field_name="dense_vector",
        index_type="HNSW",
        metric_type="COSINE",
        params={"M": 16, "efConstruction": 64}
    )

    # 稀疏向量索引
    index_params.add_index(
        field_name="sparse_vector",
        index_type="SPARSE_INVERTED_INDEX",  # 稀疏向量专用索引
        metric_type="IP"  # 稀疏向量目前仅支持 IP (内积)
    )

    # 5. 正式创建
    client.create_collection(
        collection_name=collection_name,
        schema=schema,
        index_params=index_params
    )

    print(f"Collection {collection_name} 已成功创建！")
