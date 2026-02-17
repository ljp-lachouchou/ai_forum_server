from fastapi import APIRouter, Depends
from uuid import UUID

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.deps import require_auth, is_same_user, AuthContext
from backend.api.services import get_follow_service
from backend.entity.schemas import FollowRequest
from backend.service.FollowService import FollowService

follow_router = APIRouter(prefix="/api/v1/follows", tags=["Follows"])


@follow_router.post("", response_model=AR)
async def follow_user(
    payload: FollowRequest,
    current_user: AuthContext = Depends(require_auth),
    service: FollowService = Depends(get_follow_service),
):
    try:
        if not is_same_user(current_user, payload.user_id):
            return AR.error(code=403, msg="not allowed to follow for another user")
        data = await service.follow(payload.user_id, payload.follow_id, token=current_user.token)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@follow_router.delete("", response_model=AR)
async def unfollow_user(
    payload: FollowRequest,
    current_user: AuthContext = Depends(require_auth),
    service: FollowService = Depends(get_follow_service),
):
    try:
        if not is_same_user(current_user, payload.user_id):
            return AR.error(code=403, msg="not allowed to unfollow for another user")
        await service.unfollow(payload.user_id, payload.follow_id, token=current_user.token)
        return AR.success(msg="unfollowed")
    except Exception as e:
        return AR.error(msg=str(e))


@follow_router.get("", response_model=AR)
async def list_following(
    user_id: UUID,
    current_user: AuthContext = Depends(require_auth),
    service: FollowService = Depends(get_follow_service),
):
    try:
        if not is_same_user(current_user, user_id):
            return AR.error(code=403, msg="not allowed to list another user's follows")
        data = await service.list_following(user_id, token=current_user.token)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
