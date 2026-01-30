import traceback
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Depends, Body, BackgroundTasks

from ai.db.collection_names import word_collection_name

from ai.rag.RagManager import RagManager

from ai.rag.rag_wrapper import content_mapper

from backend.Sql.enums import WordStatus
from backend.api.ApiResponse import ApiResponse as AR
from backend.api.PersonaApi import get_persona_service
from backend.api.services import (get_word_service, get_rag_query_service,
                                  get_rag_manager, get_rag_summary_service,
                                  get_report_service, get_llm_service,
                                  get_ai_post_review_service)

from backend.entity.MDword import MDWord
from backend.entity.schemas import AISearch

from backend.service.PersonaService import PersonaService
from backend.service.RagQueryService import RagQueryService, RagResult
from backend.service.RagSummaryService import RagSummaryService
from backend.service.ReportService import ReportService
from backend.service.WordService import WordService
from backend.service.AIPostReviewService import AIPostReviewService
from backend.service.LLMService import LLMService

word_router = APIRouter(prefix="/api/v1", tags=["Words"])
AI_SYSTEM_ADMIN_ID = UUID("00000000-0000-0000-0000-000000000000")


@word_router.post("/words", response_model=AR)
async def create_word(payload: dict, service: WordService = Depends(get_word_service)):
    """发布新帖 (F04)"""
    try:
        data = await service.create_word(
            author_id=payload["author_id"],
            word_url=payload["word_url"],
            category=payload["category"],
            tags=payload.get("tags", []),
            word_name=payload.get("word_name")
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
        return AR.error(code=403, msg="对不起，你不是作者，没有权限修改")
    except Exception as e:
        return AR.error(msg=str(e))


@word_router.post("/words/{id}/submit", response_model=AR)
async def submit_review(
    id: UUID,
    author_id: UUID,
    service: WordService = Depends(get_word_service),
    llm_service: LLMService = Depends(get_llm_service),
    review_service: AIPostReviewService = Depends(get_ai_post_review_service),
):
    """Submit for review (F09)."""
    await service.submit_review(id, author_id)
    try:
        word = await service.get_word(id)
        content = (word.get("raw_text") or word.get("word_url") or "").strip()
        content = await _resolve_review_content(content)
        is_safe, reason = await _ai_auto_review(content, llm_service)
        await review_service.create_review(
            id,
            "approved" if is_safe else "rejected",
            reason or None,
        )
        if not is_safe:
            await service.reject(
                id,
                admin_id=AI_SYSTEM_ADMIN_ID,
                reason=reason or "AI review failed",
            )
            return AR.error(code=400, msg="content rejected by AI review")
    except Exception as e:
        return AR.error(msg=f"review failed: {str(e)}")
    return AR.success(msg="AI review passed")


@word_router.post("/words/{id}/publish", response_model=AR)
async def publish(id: UUID, admin_id: UUID,
                  service: WordService = Depends(get_word_service),
                  rag_manager: RagManager = Depends(get_rag_manager)):
    """管理员发布"""
    word_data = await service.get_word(id)
    author_id = word_data["author_id"]
    try:
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
        await service.publish(id, admin_id)
    except Exception as e:
        try:
            await service.reject(id, admin_id, f"publish failed, returned to author: {str(e)}")
        except Exception:
            pass
        return AR.error(msg=str(e))
    return AR.success(msg="发布成功，已进入 RAG 检索库")


@word_router.post("/words/{id}/reject", response_model=AR)
async def reject(
        id: UUID,
        admin_id: UUID,
        reson: str,
        service: WordService = Depends(get_word_service),
        report_service: ReportService = Depends(get_report_service),
):
    """拒绝发布"""
    try:
        await service.reject(id, admin_id, reson)
        await report_service.create_report(admin_id, "word", id, reson)
    except Exception as e:
        return AR.error(msg=str(e))
    return AR.success(msg="文章已被拒绝发布，退回给作者")


@word_router.get("/words/feeds", response_model=AR)
async def list_published_words(
        category: Optional[str] = None,
        mode: str = "latest",
        user_id: Optional[UUID] = None,
        limit: int = 20,
        service: WordService = Depends(get_word_service)
):
    """Homepage feed (F02): list published words by category"""
    try:
        data = await service.list_feed(
            mode=mode,
            category=category,
            user_id=user_id,
            limit=limit,
        )
        return AR.success(data)
    except ValueError as e:
        return AR.error(code=400, msg=str(e))
    except Exception as e:
        return AR.error(msg=str(e))



# 成功
@word_router.get("/words/{id}", response_model=AR)
async def get_word_detail(id: UUID, service: WordService = Depends(get_word_service)):
    """获取文章详情 (关联 profiles 信息)"""
    try:
        data = await service.get_word(id)
        if data.get("status") == WordStatus.REJECTED.value:
            reject_reason = await service.get_latest_reject_reason(id)
            if reject_reason:
                data["reject_reason"] = reject_reason
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=f"未找到该文章: {str(e)}")


@word_router.get("/words/{id}/events", response_model=AR)
async def get_word_events(id: UUID, service: WordService = Depends(get_word_service)):
    """Get word events."""
    try:
        data = await service.get_events(id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


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


async def _whether_llm(
        catch_data: RagResult,
        service: WordService,
):
    if not catch_data:
        return None
    ids = catch_data.word_ids
    word_datas = await service.list_words_by_ids("word_id", ids)
    if catch_data.answer:
        return {
            "answer": catch_data.answer,
            "reference_words": word_datas
        }
    else:
        return None


# 成功
@word_router.post("/ai/search", response_model=AR[Dict])
async def ai_rag_search(
        background_tasks: BackgroundTasks,
        payload: AISearch,
        service: WordService = Depends(get_word_service),
        rq_service: RagQueryService = Depends(get_rag_query_service),
        persona_service: PersonaService = Depends(get_persona_service),
        rag_summary_service: RagSummaryService = Depends(get_rag_summary_service)
):
    """AI 智能搜索 (F06)：触发 RAG 流程"""
    try:
        # 先进行hash命中
        catch_hash_data = await rag_summary_service.hash_cache(payload.query, payload.u_id)
        rs = await _whether_llm(catch_hash_data, service)
        if rs:
            return AR.success(rs)
        # 在进行语义命中
        catch_data = await rag_summary_service.semantics_cache(payload.query, payload.u_id)
        rs = await _whether_llm(catch_data, service)
        if rs:
            return AR.success(rs)
        # 进行搜索
        data, _ = await persona_service._get_data_and_stats(payload.u_id)
        result = await rq_service.query(payload.query, data)
        ids = result.word_ids
        word_datas = await service.list_words_by_ids("word_id", ids)
        background_tasks.add_task(rag_summary_service.insert_summary, payload.query,
                                  result.answer, ids, payload.u_id)
        return AR.success(data={
            "answer": result.answer,
            "reference_words": word_datas
        })
    except Exception as e:
        traceback.print_exc()
        return AR.error(msg=f"AI 搜索失败: {str(e)}")


@word_router.post("/ai/review", response_model=AR)
async def ai_auto_review(
    id: UUID,
    service: WordService = Depends(get_word_service),
    llm_service: LLMService = Depends(get_llm_service),
    review_service: AIPostReviewService = Depends(get_ai_post_review_service),
):
    """AI content review (F09)."""
    try:
        word = await service.get_word(id)
        content = (word.get("raw_text") or word.get("word_url") or "").strip()
        content = await _resolve_review_content(content)
        is_safe, reason = await _ai_auto_review(content, llm_service)
        await review_service.create_review(
            id,
            "approved" if is_safe else "rejected",
            reason or None,
        )
        if is_safe:
            return AR.success(msg="AI review passed")
        await service.reject(
            id,
            admin_id=AI_SYSTEM_ADMIN_ID,
            reason=reason or "AI review failed",
        )
        return AR.error(code=400, msg="content rejected by AI review")
    except Exception as e:
        return AR.error(msg=f"review failed: {str(e)}")


@word_router.post("/ai/assist/post", response_model=AR)
async def ai_assist_post(
    content: str = Body(..., embed=True),
    llm_service: LLMService = Depends(get_llm_service),
):
    """AI assist post (F07): generate title and tags"""
    try:
        prompt = _build_assist_prompt(content, strict=True)
        raw = await llm_service.generate(prompt)
        data = _parse_assist_response(raw, content)
        if len(data.get("suggested_titles", [])) < 3 or len(data.get("suggested_tags", [])) < 5:
            raw_retry = await llm_service.generate(_build_assist_prompt(content, strict=True, retry=True))
            data = _parse_assist_response(raw_retry, content)

        data = _ensure_assist_minimums(data, content)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


def _parse_assist_response(raw: str, content: str) -> Dict:
    import json
    import re

    try:
        parsed = json.loads(raw)
        titles = parsed.get("titles") or parsed.get("suggested_titles") or []
        tags = parsed.get("tags") or parsed.get("suggested_tags") or []
        if isinstance(titles, list) and isinstance(tags, list):
            return {"suggested_titles": titles, "suggested_tags": tags}
    except Exception:
        match = re.search(r"\{[\s\S]*\}", raw or "")
        if match:
            try:
                parsed = json.loads(match.group(0))
                titles = parsed.get("titles") or parsed.get("suggested_titles") or []
                tags = parsed.get("tags") or parsed.get("suggested_tags") or []
                if isinstance(titles, list) and isinstance(tags, list):
                    return {"suggested_titles": titles, "suggested_tags": tags}
            except Exception:
                pass

    fallback_title = (content or "").strip()[:20] or "Suggested title"
    return {"suggested_titles": [fallback_title], "suggested_tags": []}


def _build_assist_prompt(content: str, strict: bool = True, retry: bool = False) -> str:
    guidance = "Return JSON only. No extra text." if strict else "Return JSON."
    if retry:
        guidance = "Return valid JSON only. Do not include any other text."
    return (
        "You are an assistant that extracts titles and tags from content.\n"
        f"{guidance}\n"
        "JSON schema: {\"titles\": [string, string, string], \"tags\": [string, string, string, string, string]}\n"
        f"Content: {content}"
    )


def _ensure_assist_minimums(data: Dict, content: str) -> Dict:
    titles = data.get("suggested_titles") or []
    tags = data.get("suggested_tags") or []

    titles = [t for t in titles if isinstance(t, str) and t.strip()]
    tags = [t for t in tags if isinstance(t, str) and t.strip()]

    if len(titles) < 3:
        fallback_title = (content or "").strip()[:24] or "Suggested title"
        while len(titles) < 3:
            titles.append(fallback_title if len(titles) == 0 else f"{fallback_title} ({len(titles)+1})")

    if len(tags) < 5:
        tags = _fallback_tags(content, tags)

    return {"suggested_titles": titles[:3], "suggested_tags": tags[:5]}


def _fallback_tags(content: str, existing: list) -> list:
    import re

    tags = list(existing)
    keywords = [
        "IntelliJ IDEA",
        "Continue",
        "DeepSeek",
        "API",
        "插件",
        "AI 编程助手",
        "IDE",
        "配置",
        "教程",
    ]
    for kw in keywords:
        if kw in (content or "") and kw not in tags:
            tags.append(kw)

    if len(tags) < 5:
        words = re.findall(r"[A-Za-z][A-Za-z0-9\\-\\.]{2,}", content or "")
        for w in words:
            if w not in tags:
                tags.append(w)
            if len(tags) >= 5:
                break

    return tags


async def _ai_auto_review(content: str, llm_service: LLMService) -> Tuple[bool, str]:
    import json

    if not content:
        return True, ""

    prompt = (
        "You are a strict content moderator. Decide if the content is safe. "
        "Return JSON only: {\"is_safe\": true/false, \"reason\": \"\"}\n"
        f"Content: {content}"
    )
    raw = await llm_service.generate(prompt)
    try:
        data = json.loads(raw)
        is_safe = bool(data.get("is_safe", True))
        reason = (data.get("reason") or "").strip()
        print(is_safe, reason)
        return is_safe, reason
    except Exception:
        lowered = (raw or "").lower()
        if "unsafe" in lowered or "reject" in lowered or "violation" in lowered:
            return False, (raw or "").strip()[:200]
        return True, ""


async def _resolve_review_content(content: str) -> str:
    content = (content or "").strip()
    if not content:
        return ""

    parsed = urlparse(content)
    if parsed.scheme in ("http", "https"):
        fetched = await _fetch_url_text(content)
        return fetched or content
    return content


async def _fetch_url_text(url: str, max_chars: int = 8000) -> str:
    try:
        import aiohttp
    except Exception:
        return ""

    timeout = aiohttp.ClientTimeout(total=8)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                text = await resp.text(errors="ignore")
                return text.strip()[:max_chars]
    except Exception:
        return ""
