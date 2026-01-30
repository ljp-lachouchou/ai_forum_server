from fastapi import APIRouter, Depends
from uuid import UUID

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.services import get_follow_service
from backend.entity.schemas import FollowRequest
from backend.service.FollowService import FollowService

follow_router = APIRouter(prefix="/api/v1/follows", tags=["Follows"])


@follow_router.post("", response_model=AR)
async def follow_user(
    payload: FollowRequest,
    service: FollowService = Depends(get_follow_service),
):
    try:
        data = await service.follow(payload.user_id, payload.follow_id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@follow_router.delete("", response_model=AR)
async def unfollow_user(
    payload: FollowRequest,
    service: FollowService = Depends(get_follow_service),
):
    try:
        await service.unfollow(payload.user_id, payload.follow_id)
        return AR.success(msg="unfollowed")
    except Exception as e:
        return AR.error(msg=str(e))


@follow_router.get("", response_model=AR)
async def list_following(
    user_id: UUID,
    service: FollowService = Depends(get_follow_service),
):
    try:
        data = await service.list_following(user_id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
