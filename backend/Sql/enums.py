from enum import Enum


class WordStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"

"""
create           -- 创建文档
update           -- 编辑内容
submit_review    -- 提交审核
ai_review        -- AI 审核
publish          -- 管理员发布
reject           -- 管理员拒绝
revise           -- 被拒后重新编辑
archive          -- 归档
"""
class WordEventType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    SUBMIT_REVIEW = "submit_review"
    AI_REVIEW = "ai_review"
    PUBLISH = "publish"
    REJECT = "reject"
    REVISE = "revise"
    ARCHIVE = "archive"
