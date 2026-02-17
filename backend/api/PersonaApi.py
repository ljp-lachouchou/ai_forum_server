from fastapi import APIRouter, Depends

from backend.Sql.SClient import SupabaseClient
from backend.api.ApiResponse import ApiResponse as AR
from backend.api.deps import require_auth, is_same_user, AuthContext
from backend.api.services import get_persona_service
from backend.entity.schemas import PersonaUpdateStatsRequest, PersonaUpdateAvailableRequest
from backend.service.PersonaService import PersonaService

persona_router = APIRouter(prefix='/api/v1/persona', tags=['persona'])





@persona_router.put('/update_stats', response_model=AR)
async def update_stats(payload: PersonaUpdateStatsRequest,
                       current_user: AuthContext = Depends(require_auth),
                       persona_service: PersonaService = Depends(get_persona_service)):
    try:
        if not is_same_user(current_user, payload.user_id):
            return AR.error(code=403, msg="not allowed to update another user's stats")
        response = await persona_service.update_persona_stats_background(payload.user_id, payload.category,
                                                                         payload.tags, payload.duration)
    except Exception as e:
        return AR.error(msg=f"[系统错误] 更新画像错误：{e}")
    return AR.success(response)


@persona_router.post('/update_available',response_model=AR)
async def update_available(payload:PersonaUpdateAvailableRequest,
                           current_user: AuthContext = Depends(require_auth),
                           persona_service: PersonaService = Depends(get_persona_service)):
    try:
        if not is_same_user(current_user, payload.id):
            return AR.error(code=403, msg="not allowed to update another user's persona")
        res = await persona_service.generate_behavioral_tags(payload.id)
    except Exception as e:
        return AR.error(msg=f'[系统错误] 更新用户可用画像错误: {e}')
    if not res:
        return AR.controllableError(msg=f'不符合python数组语法')
    if len(res) == 0:
        return AR.controllableError(msg='未能返回数据')
    return AR.success(res[0])
