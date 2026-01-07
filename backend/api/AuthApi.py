from fastapi import APIRouter, Depends
from gotrue.errors import AuthApiError


from backend.api.ApiResponse import ApiResponse as AR
from backend.api.services import get_auth_service, get_redis_client, get_profile_service

from backend.entity.schemas import LoginRequest, LoginData, RegisterRequest, RegisterResponse
from backend.service.AuthService import AuthService
from backend.Sql.cache.RedisCacheClient import RedisCacheClient
from backend.service.ProfileService import ProfileService

auth_router = APIRouter(prefix="/api/v1", tags=["auth"])





@auth_router.post("/login", response_model=AR[LoginData])
async def login(payload: LoginRequest,
                auth_service: AuthService = Depends(get_auth_service),
                profile_service: ProfileService = Depends(get_profile_service),
                redis_client: RedisCacheClient = Depends(get_redis_client)):
    auth_service.check_pwd(payload.password)
    try:
        token = await auth_service.login(payload.email, payload.password)
    except AuthApiError as ae:
        return AR.controllableError(msg=f"邮箱未认证 {ae}")
    except Exception as e:
        return AR.error(msg=f"登录失败,系统错误 {e}")
    profile_service.set_auth(token)
    user = await auth_service.get_current_user(token)
    result_data = LoginData(
        access_token=token,
        email=payload.email,
        user_id=user.user.id
    )
    if not await redis_client.set_token_with_single_login(token, user.user.id):
        return AR.cacheError()
    return AR.success(data=result_data)


@auth_router.post("/register", response_model=AR[RegisterResponse])
async def register(payload: RegisterRequest,
                   profile_service: ProfileService = Depends(get_profile_service),
                   auth_service: AuthService = Depends(get_auth_service),
                   redis_client: RedisCacheClient = Depends(get_redis_client)):
    profile = await profile_service.get_profile_by_profile_account(payload.email)
    print(profile)
    if profile:
        return AR.controllableError("已存在该账号")
    auth_service.check_pwd(payload.password)
    try:
        res = await auth_service.register(payload.email, payload.password)
    except AuthApiError as ae:
        return AR.controllableError(msg=f"此邮箱不可用 {ae}")
    except Exception as e:
        return AR.error(msg=f"注册失败,系统错误 {e}")
    reg_result = RegisterResponse(
        user_id=res.user.id,
        email=res.user.email,
        access_token=res.session.access_token if res.session else None
    )
    if reg_result.access_token:
        if not await redis_client.set_token_with_single_login(reg_result.access_token, res.user.id):
            return AR.cacheError()

    return AR.success(msg="注册成功，请查收邮件激活", data=reg_result)
