from fastapi import APIRouter, Depends

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.deps import require_auth, AuthContext
from backend.api.services import get_storage_service
from backend.entity.schemas import StorageUrlRequest
from backend.service.StorageService import StorageService

storage_router = APIRouter(prefix="/api/v1/storage", tags=["Storage"])


@storage_router.post("/url", response_model=AR)
async def create_storage_url(
    payload: StorageUrlRequest,
    current_user: AuthContext = Depends(require_auth),
    service: StorageService = Depends(get_storage_service),
):
    try:
        data = await service.create_url(
            bucket=payload.bucket,
            path=payload.path,
            operation=payload.operation,
            expires_in=payload.expires_in,
        )
        return AR.success(data)
    except ValueError as e:
        return AR.error(code=400, msg=str(e))
    except Exception as e:
        return AR.error(msg=str(e))
