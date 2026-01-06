from typing import TypeVar, Generic, Optional, Any

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "success"
    data: Optional[T] = None

    # 修复方法：去掉 -> "ApiResponse"，或者改为 -> Any
    @classmethod
    def success(cls, data: Any = None, msg: str = "success"):
        return cls(code=200, msg=msg, data=data)

    @classmethod
    def error(cls, code: int = 500, msg: str = "error"):
        return cls(code=code, msg=msg, data=None)

    @classmethod
    def cacheError(cls, code: int = 466, msg: str = "redis存储失败"):
        return cls(code=code, msg=msg, data=None)

    @classmethod
    def controllableError(cls, msg: str, code: int = 521):
        return cls(code=code, msg=msg, data=None)
