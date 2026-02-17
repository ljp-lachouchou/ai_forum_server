from uuid import UUID

from fastapi import APIRouter, Body, Depends

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.deps import require_auth, is_same_user, AuthContext
from backend.api.services import get_notification_service
from backend.entity.schemas import NotificationCreateRequest, NotificationReadRequest
from backend.service.NotificationService import NotificationService

notification_router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@notification_router.post("", response_model=AR)
async def create_notification(
    payload: NotificationCreateRequest,
    current_user: AuthContext = Depends(require_auth),
    service: NotificationService = Depends(get_notification_service),
):
    try:
        if not is_same_user(current_user, payload.user_id):
            return AR.error(code=403, msg="not allowed to create notification for another user")
        data = await service.create_notification(
            user_id=payload.user_id,
            n_type=payload.type,
            content=payload.content,
            ref_type=payload.ref_type,
            ref_id=payload.ref_id,
            token=current_user.token,
        )
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@notification_router.get("", response_model=AR)
async def list_notifications(
    user_id: UUID,
    unread_only: bool = False,
    limit: int = 20,
    current_user: AuthContext = Depends(require_auth),
    service: NotificationService = Depends(get_notification_service),
):
    try:
        if not is_same_user(current_user, user_id):
            return AR.error(code=403, msg="not allowed to list another user's notifications")
        data = await service.list_notifications(user_id, unread_only, limit, token=current_user.token)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@notification_router.post("/read", response_model=AR)
async def mark_notifications_read(
    payload: NotificationReadRequest,
    current_user: AuthContext = Depends(require_auth),
    service: NotificationService = Depends(get_notification_service),
):
    try:
        if not is_same_user(current_user, payload.user_id):
            return AR.error(code=403, msg="not allowed to modify another user's notifications")
        data = await service.mark_read(payload.user_id, payload.notification_ids, token=current_user.token)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@notification_router.post("/read_all", response_model=AR)
async def mark_all_read(
    user_id: UUID = Body(..., embed=True),
    current_user: AuthContext = Depends(require_auth),
    service: NotificationService = Depends(get_notification_service),
):
    try:
        if not is_same_user(current_user, user_id):
            return AR.error(code=403, msg="not allowed to modify another user's notifications")
        data = await service.mark_all_read(user_id, token=current_user.token)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
