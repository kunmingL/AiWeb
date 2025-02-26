from pydantic import BaseModel
from typing import Optional, Any

class CommonRespDataDto(BaseModel):
    """
    通用响应数据传输对象
    用于统一API响应格式
    """
    code: str                # 响应码：0-成功，其他值表示失败
    message: str            # 响应消息，成功或错误描述
    data: Optional[Any] = None  # 响应数据，可以是任意类型，允许为空 