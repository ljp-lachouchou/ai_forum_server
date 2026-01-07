from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    # EmailStr 会自动验证邮箱格式是否正确
    email: EmailStr = Field(..., description="用户邮箱")
    # min_length=1 自动替代了你代码中的 len(pwd) == 0 校验
    password: str = Field(..., min_length=6, description="用户密码")


class LoginData(BaseModel):
    access_token: str
    email: str
    user_id: str


RegisterRequest = LoginRequest


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    access_token: Optional[str]  # 注册后直接给 token


class ProfileBase(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: str = "user"


class ProfileUpdate(BaseModel):
    """用于更新个人信息的模型，所有字段可选"""
    id: UUID
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class GetProfileRequest(BaseModel):
    id: UUID


class ProfileResponse(ProfileBase):
    """用于返回给前端的模型"""
    created_at: datetime
    profile_account: Optional[str]

    class Config:
        from_attributes = True


class PersonaUpdateStatsRequest(BaseModel):
    user_id: UUID
    category: str
    tags: List[str]
    duration: int = 0


PersonaUpdateAvailableRequest = GetProfileRequest

class AISearch(BaseModel):
    u_id:UUID
    query:str
