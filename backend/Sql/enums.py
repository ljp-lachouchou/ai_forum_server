from enum import Enum


class WordStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class WordEventType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    SUBMIT_REVIEW = "submit_review"
    AI_REVIEW = "ai_review"
    PUBLISH = "publish"
    REJECT = "reject"
    REVISE = "revise"
    ARCHIVE = "archive"
