from uuid import UUID

from fastapi import APIRouter, Body, Depends

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.services import get_notification_service
from backend.entity.schemas import NotificationCreateRequest, NotificationReadRequest
from backend.service.NotificationService import NotificationService

notification_router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@notification_router.post("", response_model=AR)
async def create_notification(
    payload: NotificationCreateRequest,
    service: NotificationService = Depends(get_notification_service),
):
    try:
        data = await service.create_notification(
            user_id=payload.user_id,
            n_type=payload.type,
            content=payload.content,
            ref_type=payload.ref_type,
            ref_id=payload.ref_id,
        )
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@notification_router.get("", response_model=AR)
async def list_notifications(
    user_id: UUID,
    unread_only: bool = False,
    limit: int = 20,
    service: NotificationService = Depends(get_notification_service),
):
    try:
        data = await service.list_notifications(user_id, unread_only, limit)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@notification_router.post("/read", response_model=AR)
async def mark_notifications_read(
    payload: NotificationReadRequest,
    service: NotificationService = Depends(get_notification_service),
):
    try:
        data = await service.mark_read(payload.user_id, payload.notification_ids)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@notification_router.post("/read_all", response_model=AR)
async def mark_all_read(
    user_id: UUID = Body(..., embed=True),
    service: NotificationService = Depends(get_notification_service),
):
    try:
        data = await service.mark_all_read(user_id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
