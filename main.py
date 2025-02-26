from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import os
from models.api_response import ApiResponse
from services.token_counter import TokenCounter
from services.ai_processor import AIProcessor
from utils.logger import setup_logger
from utils.speech_utils import SpeechUtils
from pydantic import BaseModel
import base64
from typing import List
from models.response_model import StandardResponse

logger = setup_logger("main")

# 创建FastAPI应用实例
app = FastAPI(title="AI Processing Service")

# 定义请求体模型
# 定义 MessageDto 对应的 Python 模型
class MessageDto(BaseModel):
    role: str
    content: str

class SpeechRequest(BaseModel):
    """语音请求模型"""
    #当前提示词
    prompt_template: str
    # 历史对话
    history: List[MessageDto]

class fileRequest(BaseModel):
    """文件请求模型"""
    #当前提示词
    prompt_template: str
    # 文件
    filePath: List[str]

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"请求处理失败: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ApiResponse.error(str(e)).__dict__
        )

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 允许所有来源
    allow_credentials=True,  # 允许携带认证信息
    allow_methods=["*"],     # 允许所有HTTP方法
    allow_headers=["*"],     # 允许所有HTTP头
)

# 初始化服务实例
token_counter = TokenCounter()
ai_processor = AIProcessor(token_counter)

@app.post("/changjiang/elearn/process/file")
async def process_file_request(request: fileRequest) -> StandardResponse:
    """文件处理接口"""
    try:
        return await ai_processor.process_request(
            role="file_processor",
            prompt_template=request.prompt_template,
            file_path=request.filePath
        )
    except Exception as e:
        logger.error(f"文件处理请求失败: {str(e)}", exc_info=True)
        return StandardResponse.error(msg=str(e))

@app.post("/changjiang/elearn/process/speech")
async def process_speech_request(request: SpeechRequest) -> StandardResponse:
    """语音对话处理接口"""
    try:
        response = await ai_processor.process_request(
            role="speech_assistant",
            prompt_template=request.prompt_template,
            history=request.history
        )

        if response.code == "0":
            # 生成语音
            audio_bytes, content_type = await SpeechUtils.generate_voice_bytes(
                response.data["response"]
            )

            # 构造返回数据
            result_data = {
                "fileBase64": base64.b64encode(audio_bytes).decode("utf-8"),
                "fileText": response.data["response"],
                "fileName": ""
            }

            return StandardResponse.success(data=result_data)
        else:
            return response

    except Exception as e:
        logger.error(f"语音处理请求失败: {str(e)}", exc_info=True)
        return StandardResponse.error(msg=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8010)