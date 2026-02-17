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


class CommentCreateRequest(BaseModel):
    author_id: UUID
    content: str


class UserActionRequest(BaseModel):
    user_id: UUID


class TreeholeCreateRequest(BaseModel):
    author_id: UUID
    content: str
    is_anonymous: bool = True
    mood: str = "平常"


class NotificationCreateRequest(BaseModel):
    user_id: UUID
    type: str
    content: str
    ref_type: Optional[str] = None
    ref_id: Optional[UUID] = None


class NotificationReadRequest(BaseModel):
    user_id: UUID
    notification_ids: List[UUID]


class SyncIdsRequest(BaseModel):
    ids: List[UUID]


class SyncIdsWithUserRequest(BaseModel):
    user_id: UUID
    ids: List[UUID]


class SyncIdsWithOptionalUserRequest(BaseModel):
    user_id: Optional[UUID] = None
    ids: List[UUID]


class FollowRequest(BaseModel):
    user_id: UUID
    follow_id: UUID


class ReportCreateRequest(BaseModel):
    reporter_id: Optional[UUID] = None
    target_type: str
    target_id: UUID
    reason: str


class StorageUrlRequest(BaseModel):
    bucket: str
    path: str
    operation: str = "download"
    expires_in: int = 3600
