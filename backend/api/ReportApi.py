from fastapi import APIRouter, Depends

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.deps import require_auth, is_same_user, AuthContext
from backend.api.services import get_report_service
from backend.entity.schemas import ReportCreateRequest
from backend.service.ReportService import ReportService

report_router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@report_router.post("", response_model=AR)
async def create_report(
    payload: ReportCreateRequest,
    current_user: AuthContext = Depends(require_auth),
    service: ReportService = Depends(get_report_service),
):
    try:
        if not is_same_user(current_user, payload.reporter_id):
            return AR.error(code=403, msg="not allowed to report as another user")
        data = await service.create_report(
            payload.reporter_id,
            payload.target_type,
            payload.target_id,
            payload.reason,
            token=current_user.token,
        )
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
