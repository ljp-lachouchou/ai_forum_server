from fastapi import APIRouter, Depends

from backend.api.ApiResponse import ApiResponse as AR
from backend.api.services import get_report_service
from backend.entity.schemas import ReportCreateRequest
from backend.service.ReportService import ReportService

report_router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@report_router.post("", response_model=AR)
async def create_report(
    payload: ReportCreateRequest,
    service: ReportService = Depends(get_report_service),
):
    try:
        data = await service.create_report(
            payload.reporter_id,
            payload.target_type,
            payload.target_id,
            payload.reason,
        )
        return AR.success(data)
    except Exception as e:
        return AR.error(msg=str(e))
