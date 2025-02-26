from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """
    统一的API响应格式
    支持泛型，可以处理不同类型的响应数据
    """
    code: str
    message: str
    data: Optional[T] = None
    alerts: Optional[dict] = None  # 用于存放告警信息

    @classmethod
    def success(cls, data: Any = None, message: str = "success", alerts: dict = None):
        return cls(
            code="0",
            message=message,
            data=data,
            alerts=alerts
        )

    @classmethod
    def error(cls, message: str, code: str = "1"):
        return cls(
            code=code,
            message=message
        ) 