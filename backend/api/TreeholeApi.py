from fastapi import APIRouter, Depends, Query, Body
from uuid import UUID

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.services import get_treehole_service
from backend.entity.schemas import TreeholeCreateRequest
from backend.service.TreeholeService import TreeholeService

treehole_router = APIRouter(prefix="/api/v1/treehole", tags=["Treehole"])


@treehole_router.post("", response_model=AR)
async def create_treehole(
    payload: TreeholeCreateRequest,
    service: TreeholeService = Depends(get_treehole_service),
):
    try:
        data = await service.create_treehole(
            payload.author_id,
            payload.content,
            payload.is_anonymous,
        )
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@treehole_router.get("/stream", response_model=AR)
async def list_treeholes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_ai: bool = False,
    service: TreeholeService = Depends(get_treehole_service),
):
    try:
        data = await service.list_treeholes(limit=limit, offset=offset, include_ai=include_ai)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))


@treehole_router.post("/{treehole_id}/ai_reply", response_model=AR)
async def create_ai_reply(
    treehole_id: UUID,
    content: str = Body(..., embed=True),
    service: TreeholeService = Depends(get_treehole_service),
):
    try:
        data = await service.create_ai_reply(treehole_id, content)
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
