import asyncio
from functools import wraps
from config import settings
from fastapi import HTTPException

def async_retry(max_retries: int = None):
    """
    异步重试装饰器
    处理临时性故障
    """
    max_retries = max_retries or settings.MAX_RETRIES

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # 指数退避
                    continue
            raise HTTPException(
                status_code=500,
                detail=f"服务调用失败，重试{max_retries}次后仍然失败: {str(last_exception)}"
            )
        return wrapper
    return decorator 