from fastapi import HTTPException, UploadFile
from typing import Dict, Any, Optional, Union, List
from models.api_response import ApiResponse
from utils.decorators import async_retry
from utils.logger import setup_logger
from services.token_counter import TokenCounter
from config import settings
import dashscope
import base64
import io
from pathlib import Path
import os
import PyPDF2

import pandas as pd
from PIL import Image
import pytesseract
from models.response_model import StandardResponse

logger = setup_logger("ai_processor")

class AIProcessor:
    """
    统一的AI处理服务
    支持不同角色的AI处理能力
    """
    def __init__(self, token_counter: TokenCounter):
        self.token_counter = token_counter
        self.default_model = "qwen-max"  # 默认使用通义千问max模型
        self.file_model = "qwen-long"    # 长文本处理使用qwen-long模型
        self.api_key = os.getenv("DASHSCOPE_API_KEY") or settings.DASHSCOPE_API_KEY

    @async_retry()
    async def process_request(
        self, 
        role: str,
        prompt_template: str,
        content: Optional[Union[str, bytes]] = None,
        content_type: Optional[str] = None,
        history: Optional[List[str]] = None,
        file_path: Optional[List[str]] = None
    ) -> StandardResponse:
        """
        统一处理请求
        Args:
            role: AI角色('file_processor'或'speech_assistant')
            prompt_template: 提示词模板
            content: 需要处理的内容
            content_type: 内容类型
            history: 历史对话内容
            file_path: 文件路径（用于长文本处理）
        Returns:
            StandardResponse: 处理结果
        """
        try:
            if role == "file_processor":
                return await self._handle_file_processing(
                    prompt_template, 
                    file_path
                )
            elif role == "speech_assistant":
                return await self._handle_speech_processing(
                    prompt_template,
                    history or []
                )
            else:
                return StandardResponse.error(msg="不支持的AI角色类型")

        except Exception as e:
            logger.error(f"AI处理失败: {str(e)}", exc_info=True)
            return StandardResponse.error(msg=str(e))

    async def _handle_file_processing(
        self,
        prompt_template: str,
        file_paths: List[str]
    ) -> StandardResponse:
        """
        处理多个文件内容提取请求
        Args:
            prompt_template: AI处理指令
            file_paths: 文件路径列表
        Returns:
            StandardResponse: 处理结果
        """
        try:
            # 存储所有文件内容
            all_contents = []
            
            # 读取所有文件内容
            for file_path in file_paths:
                try:
                    file_ext = Path(file_path).suffix.lower()
                    content = await self._extract_file_content(file_path, file_ext)
                    if content:
                        all_contents.append(f"文件 {Path(file_path).name} 内容:\n{content}\n")
                except Exception as e:
                    logger.error(f"文件 {file_path} 读取失败: {str(e)}")
                    continue

            if not all_contents:
                return StandardResponse.error(msg="没有成功读取任何文件内容")

            # 合并所有文件内容
            combined_content = "\n---\n".join(all_contents)

            # 构建消息列表
            messages = [
                {
                    'role': 'system', 
                    'content': '你是专业的文件处理助手，需要按照用户的指令处理文件内容并返回结果'
                },
                {
                    'role': 'user',
                    'content': f"以下是文件内容：\n\n{combined_content}\n\n请按照以下指令处理：\n{prompt_template}"
                }
            ]

            # 调用AI模型处理
            response = dashscope.Generation.call(
                model=self.file_model,
                messages=messages,
                api_key=self.api_key,
                result_format='message',
                max_tokens=2000
            )

            # 构造返回数据
            result_data = {
                "response": response.output.choices[0].message.content
            }

            return StandardResponse.success(data=result_data)

        except Exception as e:
            logger.error(f"文件处理失败: {str(e)}", exc_info=True)
            return StandardResponse.error(msg=str(e))

    async def _extract_file_content(self, file_path: str, file_ext: str) -> Optional[str]:
        """
        根据文件类型提取内容
        Args:
            file_path: 文件路径
            file_ext: 文件扩展名
        Returns:
            Optional[str]: 提取的文本内容
        """
        try:
            # PDF文件处理
            if file_ext == '.pdf':
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = []
                    for page in pdf_reader.pages:
                        text.append(page.extract_text())
                    return '\n'.join(text)

            # # Word文件处理
            # elif file_ext in ['.doc', '.docx']:
            #     doc = Document(file_path)
            #     return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            #
            # # PowerPoint文件处理
            # elif file_ext in ['.ppt', '.pptx']:
            #     prs = Presentation(file_path)
            #     text = []
            #     for slide in prs.slides:
            #         for shape in slide.shapes:
            #             if hasattr(shape, "text"):
            #                 text.append(shape.text)
            #     return '\n'.join(text)

            # Excel文件处理
            elif file_ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
                return df.to_string()

            # 文本文件处理
            elif file_ext == '.txt':
                # 尝试不同的编码方式
                encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            return file.read()
                    except UnicodeDecodeError:
                        continue
                raise Exception("无法识别文件编码")

            # 图片文件处理
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                image = Image.open(file_path)
                # 使用OCR提取图片中的文字
                text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                return text if text.strip() else "图片中未检测到文字内容"

            else:
                return f"不支持的文件类型: {file_ext}"

        except Exception as e:
            logger.error(f"文件内容提取失败: {str(e)}")
            return f"文件内容提取失败: {str(e)}"

    async def _handle_speech_processing(
        self,
        prompt_template: str,
        history: List[str],
        max_history_length: int = 5  # 限制历史对话的最大长度
    ) -> StandardResponse:
        """处理语音对话请求"""
        try:
            # 限制历史对话的长度
            if history and len(history) > max_history_length * 2:
                history = history[-(max_history_length * 2):]

            # 构建消息列表
            messages = []
            
            # 添加系统提示
            messages.append({
                'role': 'system',
                'content': '你是专业的语音对话助手，需要用自然、流畅的方式回答问题'
            })

            # 添加历史对话
            if history:
                for i in range(0, len(history), 2):
                    if i < len(history):
                        messages.append({
                            'role': 'user',
                            'content': str(history[i])  # 确保内容是字符串
                        })
                    if i + 1 < len(history):
                        messages.append({
                            'role': 'assistant',
                            'content': str(history[i + 1])  # 确保内容是字符串
                        })

            # 添加当前用户输入
            messages.append({
                'role': 'user',
                'content': str(prompt_template)  # 确保内容是字符串
            })

            # 调用通义千问max模型进行对话处理
            response = dashscope.Generation.call(
                model=self.default_model,
                messages=messages,
                api_key=self.api_key,
                result_format='message',
                max_tokens=200
            )

            # 构造返回数据
            result_data = {
                "response": response.output.choices[0].message.content,
                "used_model": self.default_model
            }

            return StandardResponse.success(data=result_data)

        except Exception as e:
            logger.error(f"语音处理失败: {str(e)}", exc_info=True)
            return StandardResponse.error(msg=str(e))

    @staticmethod
    def compress_history(history: List[Dict[str, str]]) -> str:
        """将历史对话压缩为简短的摘要"""
        summary = []
        for item in history:
            role = item['role']
            content = item['content']
            summary.append(f"{role}: {content[:50]}...")  # 只保留前50个字符
        return "\n".join(summary)