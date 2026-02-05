from uuid import UUID

from fastapi import APIRouter, Depends

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.services import get_sync_service
from backend.entity.schemas import (
    SyncIdsRequest,
    SyncIdsWithUserRequest,
    SyncIdsWithOptionalUserRequest,
)
from backend.service.SyncService import SyncService

sync_router = APIRouter(prefix="/api/v1/sync", tags=["Sync"])


@sync_router.get("/changelog", response_model=AR)
async def get_changelog(
    since: int = 0,
    limit: int = 500,
    service: SyncService = Depends(get_sync_service),
):
    try:
        data = await service.get_changelog(since, limit)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@sync_router.post("/words", response_model=AR)
async def sync_words(
    payload: SyncIdsRequest,
    service: SyncService = Depends(get_sync_service),
):
    try:
        data = await service.get_words(payload.ids)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@sync_router.post("/comments", response_model=AR)
async def sync_comments(
    payload: SyncIdsRequest,
    service: SyncService = Depends(get_sync_service),
):
    try:
        data = await service.get_comments(payload.ids)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@sync_router.post("/treeholes", response_model=AR)
async def sync_treeholes(
    payload: SyncIdsRequest,
    service: SyncService = Depends(get_sync_service),
):
    try:
        data = await service.get_treeholes(payload.ids)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@sync_router.post("/profiles", response_model=AR)
async def sync_profiles(
    payload: SyncIdsRequest,
    service: SyncService = Depends(get_sync_service),
):
    try:
        data = await service.get_profiles(payload.ids)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@sync_router.post("/notifications", response_model=AR)
async def sync_notifications(
    payload: SyncIdsWithUserRequest,
    service: SyncService = Depends(get_sync_service),
):
    try:
        data = await service.get_notifications(payload.user_id, payload.ids)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@sync_router.post("/likes", response_model=AR)
async def sync_likes(
    payload: SyncIdsWithOptionalUserRequest,
    service: SyncService = Depends(get_sync_service),
):
    try:
        data = await service.get_likes(payload.ids, payload.user_id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@sync_router.post("/bookmarks", response_model=AR)
async def sync_bookmarks(
    payload: SyncIdsWithOptionalUserRequest,
    service: SyncService = Depends(get_sync_service),
):
    try:
        data = await service.get_bookmarks(payload.ids, payload.user_id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@sync_router.post("/follows", response_model=AR)
async def sync_follows(
    payload: SyncIdsWithOptionalUserRequest,
    service: SyncService = Depends(get_sync_service),
):
    try:
        data = await service.get_follows(payload.ids, payload.user_id)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
