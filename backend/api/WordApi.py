import traceback
from typing import Optional, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, Body
from langchain_text_splitters import MarkdownHeaderTextSplitter
from milvus_model.hybrid import BGEM3EmbeddingFunction


from ai.client.ClientBuilder import ClientBuilder, ClientType
from ai.db.DBClient import DBClient
from ai.db.collection_names import word_collection_name
from ai.rag.RagConfiguration import RagConfigurationBuilder
from ai.rag.RagManager import RagManager, MilvusRagRetriever
from ai.rag.RagProcessor import MDMilvusRagProcessor
from ai.rag.rag_wrapper import content_mapper
from backend.Sql.SClient import SupabaseClient
from backend.Sql.enums import WordStatus
from backend.api.ApiResponse import ApiResponse as AR

from backend.entity.MDword import MDWord
from backend.service.HybridSearchService import HybridSearchService
from backend.service.LLMService import DeepSeekLLMService
from backend.service.RagQueryService import RagQueryService
from backend.service.WordService import WordService

word_router = APIRouter(prefix="/api/v1", tags=["Words"])


def get_word_service():
    return WordService(SupabaseClient())


def get_rag_manager():
    manager = RagManager(RagConfigurationBuilder, MDMilvusRagProcessor)
    return manager.build(bge_model=BGEM3EmbeddingFunction(model_name="../model/bge-m3",
                                                          use_fp16=False, device="cpu"),
                         splitter=MarkdownHeaderTextSplitter(headers_to_split_on=[
                             ("#", "Header 1"),
                             ("##", "Header 2"),
                             ("###", "Header 3"),
                         ]),
                         content_loader=None,
                         db_instance=DBClient.get_client())


def get_search_service():
    word_service = get_word_service()
    rag_retriever = MilvusRagRetriever(DBClient.get_client(),
                                       RagConfigurationBuilder(
                                           bge_model=BGEM3EmbeddingFunction(
                                               model_name="../model/bge-m3",
                                               use_fp16=False, device="cpu"),
                                           splitter=MarkdownHeaderTextSplitter(headers_to_split_on=[
                                               ("#", "Header 1"),
                                               ("##", "Header 2"),
                                               ("###", "Header 3"),
                                           ]),
                                           content_loader=None,
                                           db_instance=DBClient.get_client()
                                       ))
    return HybridSearchService(
        rag_retriever,
        word_service
    )


def get_llm_service():
    model_client = ClientBuilder(ClientType.DeepSeek).build()
    return DeepSeekLLMService(model_client)


def get_rag_query_service():
    return RagQueryService(get_search_service(), get_llm_service())


@word_router.post("/words", response_model=AR)
async def create_word(payload: dict, service: WordService = Depends(get_word_service)):
    """发布新帖 (F04)"""
    try:
        data = await service.create_word(
            author_id=payload["author_id"],
            word_url=payload["word_url"],
            category=payload["category"],
            tags=payload.get("tags", [])
        )
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@word_router.put("/words/{id}", response_model=AR)
async def update_word(id: UUID, author_id: UUID,
                      payload: dict,
                      service: WordService = Depends(get_word_service)):
    """编辑内容 (UPDATE)"""
    try:
        await service.update_word(id, author_id, payload)
        return AR.success(msg="更新成功")
    except PermissionError:
        # ✅ 处理没权限的情况
        return AR.error(code=403, msg="对不起，你不是作者，没有权限修改")
    except Exception as e:
        return AR.error(msg=str(e))


@word_router.post("/words/{id}/submit", response_model=AR)
async def submit_review(id: UUID, author_id: UUID, service: WordService = Depends(get_word_service)):
    """提交审核 (F09)"""
    await service.submit_review(id, author_id)
    # TODO ai审查
    return AR.success(msg="已提交 AI 审核")


@word_router.post("/words/{id}/publish", response_model=AR)
async def publish(id: UUID, admin_id: UUID,
                  service: WordService = Depends(get_word_service),
                  rag_manager: RagManager = Depends(get_rag_manager)):
    """管理员发布"""
    word_data = await service.get_word(id)
    author_id = word_data["author_id"]
    try:
        await service.publish(id, admin_id)
        # 推入rag
        word = MDWord(
            id=word_data['word_id'],
            word_name=word_data['word_name'],
            author_id=word_data['author_id'],
            word_url=word_data['word_url'],
            word_tags=word_data['tags'],
            likes=0,
            views=0,
            category=word_data['category'],
            is_delete=False,
        )
        await rag_manager.start_process(word_collection_name, word, content_mapper)
    except Exception as e:
        # 失败就让其回到submit_review
        await service.submit_review(id, author_id)
        return AR.error(msg=str(e))
    return AR.success(msg="发布成功，已进入 RAG 检索库")


@word_router.post("/words/{id}/reject", response_model=AR)
async def reject(id: UUID, admin_id: UUID, reson: str, service: WordService = Depends(get_word_service)):
    """拒绝发布"""
    await service.reject(id, admin_id, reson)
    # TODO 推回给作者端处理
    return AR.success(msg="文章已被拒绝发布，退回给作者")


@word_router.get("/words/feeds", response_model=AR)
async def list_published_words(
        category: Optional[str] = None,
        service: WordService = Depends(get_word_service)
):
    """首页信息流 (F02)：支持按分类筛选已发布的文章"""
    try:
        data = await service.list_words(status=WordStatus.PUBLISHED, category=category)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))

# 成功
@word_router.get("/words/{id}", response_model=AR)
async def get_word_detail(id: UUID, service: WordService = Depends(get_word_service)):
    """获取文章详情 (关联 profiles 信息)"""
    try:
        data = await service.get_word(id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=f"未找到该文章: {str(e)}")


@word_router.post("/words/{id}/archive", response_model=AR)
async def archive_word(
        id: UUID,
        admin_id: UUID = Body(..., embed=True),
        service: WordService = Depends(get_word_service)
):
    """归档文章 (ARCHIVE)：从 RAG 检索中屏蔽"""
    try:
        await service.archive(id, admin_id)
        # TODO: 调用 Milvus SDK 根据 word_id 删除或更新索引状态
        return AR.success(msg="文章已归档，已从搜索库中屏蔽")
    except Exception as e:
        return AR.error(msg=str(e))


@word_router.delete("/words/{id}", response_model=AR)
async def delete_word(id: UUID, service: WordService = Depends(get_word_service)):
    """软删除文章：更新 is_delete=true"""
    try:
        # TODO 假设 service 中有对应的软删除逻辑，或者直接调用 update_word
        await service.sb.update_async("words", {"is_delete": True}, {"word_id": str(id)})
        return AR.success(msg="文章已成功删除")
    except Exception as e:
        return AR.error(msg=str(e))

# 成功
@word_router.post("/ai/search", response_model=AR[Dict])
async def ai_rag_search(
        query: str = Body(..., embed=True),
        service: WordService = Depends(get_word_service),
        rq_service:RagQueryService = Depends(get_rag_query_service)
):
    """AI 智能搜索 (F06)：触发 RAG 流程"""
    try:
        result = await rq_service.query(query)
        ids = result.word_ids
        word_datas = await service.list_words_by_ids("word_id",ids)

        return AR.success(data={
            "answer":result.answer,
            "reference_words":word_datas
        })
    except Exception as e:
        traceback.print_exc()
        return AR.error(msg=f"AI 搜索失败: {str(e)}")


@word_router.post("/ai/review", response_model=AR)
async def ai_auto_review(id: UUID, service: WordService = Depends(get_word_service)):
    """智能内容审核 (F09)：拦截违规内容"""
    try:
        word = await service.get_word(id)
        content = word.get("raw_text", "")

        # 调用 Moderation API (如阿里云、百度或 LLM 自检)
        is_safe = True  # 模拟审核结果

        if is_safe:
            # 审核通过，保持 PENDING 或进入待人工审核
            return AR.success(msg="AI 审核通过")
        else:
            # 违规则直接调用 reject 变更为 REJECTED 状态
            await service.reject(id, admin_id=UUID("0000..."), reason="AI 自动审核未通过：发现违规内容")
            return AR.error(code=400, msg="内容违规，已被系统拦截")
    except Exception as e:
        return AR.error(msg=f"审核服务异常: {str(e)}")


@word_router.post("/ai/assist/post", response_model=AR)
async def ai_assist_post(content: str = Body(..., embed=True)):
    """辅助发帖 (F07)：自动生成吸睛标题和标签"""
    try:
        # 调用 LLM 处理正文并提取关键词
        # suggestions = llm.generate_suggestions(content)
        data = {
            "suggested_titles": ["标题 1", "标题 2"],
            "suggested_tags": ["标签 A", "标签 B"]
        }
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
