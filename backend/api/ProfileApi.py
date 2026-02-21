from fastapi import APIRouter, Depends
from pydantic_core import ValidationError

from backend.api.AuthApi import get_profile_service
from backend.entity.schemas import GetProfileRequest, ProfileResponse, ProfileUpdate
from backend.service.ProfileService import ProfileService
from backend.api.ApiResponse import ApiResponse as AR
from backend.api.deps import require_auth, is_same_user, AuthContext

profile_router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


# 查看profile
@profile_router.get("/get_profile", response_model=AR)
async def get_profile(pamaras: GetProfileRequest = Depends(),
                      current_user: AuthContext = Depends(require_auth),
                      profile_service: ProfileService = Depends(get_profile_service)):
    try:
        if not is_same_user(current_user, pamaras.id):
            return AR.error(code=403, msg="not allowed to access another user's profile")
        data = await profile_service.get_profile(pamaras.id, token=current_user.token)
    except ValidationError as ve:
        return AR.controllableError(f"获取个人信息错误： {ve}")
    except Exception as e:
        return AR.error(msg=f"[系统错误] 获取个人信息错误： {e}")
    response = ProfileResponse.model_validate(data)
    return AR.success(response)



# 更新 profile
@profile_router.put("/update_profile",response_model=AR)
async def update_profile(payload:ProfileUpdate,
                         current_user: AuthContext = Depends(require_auth),
                         profile_service:ProfileService = Depends(get_profile_service)):
    try:
        if not is_same_user(current_user, payload.id):
            return AR.error(code=403, msg="not allowed to update another user's profile")
        update_data = payload.model_dump(mode="json", exclude_none=True)
        update_data.pop("id", None)
        if not update_data:
            return AR.success(msg="no fields to update")
        data = await profile_service.update_profile(payload.id, update_data, token=current_user.token)
    except Exception as e:
        return AR.error(msg=f"[系统错误] 更新个人信息: {e}")
    return AR.success(data)
