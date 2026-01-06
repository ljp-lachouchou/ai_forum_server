from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class ProfileSchema(BaseModel):
    # id 是主键，类型为 uuid
    id: UUID

    # username, avatar_url, bio 在图中没有勾选必填，建议设为 Optional
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

    # role 有默认值 'user'
    role: str = "user"

    # created_at 有默认值 now()
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        # 允许从 ORM 对象（如 SQLAlchemy）中读取数据
        from_attributes = True

