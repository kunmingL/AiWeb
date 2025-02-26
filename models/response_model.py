from typing import Optional, Any
from pydantic import BaseModel

class StandardResponse(BaseModel):
    """标准响应模型"""
    code: str                 # 响应码：200-成功，其他值表示失败
    msg: str                  # 响应信息，包含成功信息或错误描述
    data: Optional[Any] = None  # 响应数据，可以是任意类型，允许为空

    @classmethod
    def success(cls, data: Any = None, msg: str = "success"):
        """成功响应"""
        return cls(
            code="200",
            msg=msg,
            data=data
        )

    @classmethod
    def error(cls, msg: str, code: str = "1"):
        """错误响应"""
        return cls(
            code=code,
            msg=msg,
            data=None
        ) 