from fastapi import APIRouter, Depends
from pydantic_core import ValidationError

from backend.api.AuthApi import get_profile_service, get_auth_service
from backend.entity.schemas import GetProfileRequest, ProfileResponse, ProfileUpdate
from backend.service.AuthService import AuthService
from backend.service.ProfileService import ProfileService
from backend.api.ApiResponse import ApiResponse as AR

profile_router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


# 查看profile
@profile_router.get("/get_profile", response_model=AR)
async def get_profile(pamaras: GetProfileRequest = Depends(),
                      profile_service: ProfileService = Depends(get_profile_service)):
    try:
        data = await profile_service.get_profile(pamaras.id)
    except ValidationError as ve:
        return AR.controllableError(f"获取个人信息错误： {ve}")
    except Exception as e:
        return AR.error(msg=f"[系统错误] 获取个人信息错误： {e}")
    response = ProfileResponse.model_validate(data)
    return AR.success(response)



# 更新 profile
@profile_router.put("/update_profile",response_model=AR)
async def update_profile(payload:ProfileUpdate,
                         profile_service:ProfileService = Depends(get_profile_service)):
    try:
        data = await profile_service.update_profile(payload.id,payload.model_dump(mode='json'))
    except Exception as e:
        return AR.error(msg=f"[系统错误] 更新个人信息: {e}")
    return AR.success(data)