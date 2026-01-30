from uuid import UUID

from fastapi import APIRouter, Depends

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.services import get_bookmark_service, get_like_service
from backend.entity.schemas import UserActionRequest
from backend.service.BookmarksService import BookmarkService
from backend.service.LikeService import LikeService

interaction_router = APIRouter(prefix="/api/v1", tags=["Interactions"])


@interaction_router.post("/posts/{post_id}/like", response_model=AR)
async def toggle_like(
    post_id: UUID,
    payload: UserActionRequest,
    service: LikeService = Depends(get_like_service),
):
    try:
        liked = await service.toggle_like(payload.user_id, post_id)
        return AR.success(data={"liked": liked})
    except Exception as e:
        return AR.error(msg=str(e))


@interaction_router.post("/posts/{post_id}/collect", response_model=AR)
async def toggle_collect(
    post_id: UUID,
    payload: UserActionRequest,
    service: BookmarkService = Depends(get_bookmark_service),
):
    try:
        if await service.is_bookmarked(payload.user_id, post_id):
            await service.remove_bookmark(payload.user_id, post_id)
            return AR.success(data={"collected": False})
        await service.add_bookmark(payload.user_id, post_id)
        return AR.success(data={"collected": True})
    except Exception as e:
        return AR.error(msg=str(e))


@interaction_router.get("/user/likes", response_model=AR)
async def list_user_likes(
    user_id: UUID,
    service: LikeService = Depends(get_like_service),
):
    try:
        data = await service.list_user_likes(user_id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
