from uuid import UUID

from fastapi import APIRouter, Depends, Body

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.deps import require_auth, is_same_user, AuthContext
from backend.api.services import get_comment_service, get_comment_summary_service
from backend.entity.schemas import CommentCreateRequest
from backend.service.CommentService import CommentService
from backend.service.CommentSummaryService import CommentSummaryService

comment_router = APIRouter(prefix="/api/v1", tags=["Comments"])


@comment_router.post("/posts/{post_id}/comments", response_model=AR)
async def create_comment(
    post_id: UUID,
    payload: CommentCreateRequest,
    current_user: AuthContext = Depends(require_auth),
    service: CommentService = Depends(get_comment_service),
):
    try:
        if not is_same_user(current_user, payload.author_id):
            return AR.error(code=403, msg="not allowed to create comment for another user")
        data = await service.create_comment(post_id, payload.author_id, payload.content, token=current_user.token)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@comment_router.get("/posts/{post_id}/comments", response_model=AR)
async def list_comments(
    post_id: UUID,
    service: CommentService = Depends(get_comment_service),
):
    try:
        data = await service.list_comments(post_id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@comment_router.delete("/comments/{comment_id}", response_model=AR)
async def delete_comment(
    comment_id: UUID,
    author_id: UUID = Body(..., embed=True),
    current_user: AuthContext = Depends(require_auth),
    service: CommentService = Depends(get_comment_service),
):
    try:
        if not is_same_user(current_user, author_id):
            return AR.error(code=403, msg="not allowed to delete comment for another user")
        await service.delete_comment(comment_id, author_id, token=current_user.token)
        return AR.success(msg="comment deleted")
    except PermissionError:
        return AR.error(code=403, msg="not allowed to delete this comment")
    except Exception as e:
        return AR.error(msg=str(e))


@comment_router.get("/posts/{post_id}/comments/summary", response_model=AR)
async def get_comment_summary(
    post_id: UUID,
    service: CommentSummaryService = Depends(get_comment_summary_service),
):
    try:
        data = await service.summarize_comments(post_id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
