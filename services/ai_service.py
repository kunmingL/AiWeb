import asyncio
import dashscope
from services.token_counter import TokenCounter
from fastapi import HTTPException
from typing import Dict, Any
from utils.decorators import async_retry
from models.api_response import ApiResponse
from config import settings

class AIService:
    """
    AI服务类
    处理与AI模型的交互，包括消息处理和token计数
    支持模型自动切换功能
    """
    def __init__(self, token_counter: TokenCounter):
        """
        初始化AI服务
        Args:
            token_counter: Token计数器实例
        """
        self.token_counter = token_counter
        self.default_model = "deepseek"  # 设置默认模型

    @async_retry()
    async def process_chat(self, model: str, message: str) -> ApiResponse[Dict[str, Any]]:
        """
        处理聊天请求，支持模型自动切换
        Args:
            model: 使用的模型名称（'tongyi'或'deepseek'）
            message: 用户输入的消息
        Returns:
            ApiResponse: 包含API响应、使用的模型信息和token告警信息
        """
        try:
            async with asyncio.timeout(settings.SERVICE_TIMEOUT):
                response = None
                used_model = model or self.default_model
                
                # 首先尝试使用DeepSeek
                if used_model == "deepseek":
                    response = await self._process_deepseek_chat(message)
                    # 检查DeepSeek的token是否不足
                    if self.token_counter.deepseek_tokens < self.token_counter.TOKEN_ALERT_THRESHOLD:
                        # 自动切换到通义千问
                        response = await self._process_tongyi_chat(message)
                        used_model = "tongyi"

                # 如果指定使用通义千问或DeepSeek不可用时
                elif used_model == "tongyi":
                    response = await self._process_tongyi_chat(message)

                # 获取所有模型的告警信息
                alerts = self.token_counter.check_threshold()
                
                return ApiResponse.success(
                    data={
                        "response": response,
                        "used_model": used_model,  # 返回实际使用的模型
                        "model_switch": used_model != model if model else False  # 标识是否发生了模型切换
                    },
                    alerts=alerts
                )
        except asyncio.TimeoutError:
            return ApiResponse.error("服务调用超时", code="2")
        except Exception as e:
            return ApiResponse.error(str(e))

    async def _process_tongyi_chat(self, message: str):
        """
        处理通义千问模型的请求
        Args:
            message: 用户输入的消息
        Returns:
            response: 模型的响应
        Raises:
            HTTPException: 当API调用失败时
        """
        try:
            response = dashscope.Generation.call(
                model="qwen-turbo",
                messages=[{"role": "user", "content": message}]
            )
            self.token_counter.update_tongyi_tokens(response.usage.total_tokens)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"通义千问API调用失败: {str(e)}"
            )

    async def _process_deepseek_chat(self, message: str):
        """
        处理DeepSeek模型的请求
        Args:
            message: 用户输入的消息
        Returns:
            str: 模型的响应
        Raises:
            HTTPException: 当API调用失败时
        """
        try:
            # TODO: 实现实际的DeepSeek API调用
            response = "DeepSeek response"  # 实际实现需要替换
            # 模拟token消耗
            current_tokens = self.token_counter.deepseek_tokens - len(message)
            self.token_counter.update_deepseek_tokens(current_tokens)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"DeepSeek API调用失败: {str(e)}"
            ) 