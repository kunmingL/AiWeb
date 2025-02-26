from fastapi import UploadFile
from models.api_response import ApiResponse
from typing import List, Dict, Any
from utils.file_utils import FileUtils
from services.ai_service import AIService
from utils.logger import setup_logger
import PyPDF2
import docx
import io

logger = setup_logger("file_service")

class FileService:
    """
    文件服务类
    处理文件上传和内容提取
    """
    def __init__(self, ai_service: AIService):
        """
        初始化文件服务
        Args:
            ai_service: AI服务实例，用于处理文件内容
        """
        self.ai_service = ai_service

    async def process_files(self, files: List[UploadFile]) -> ApiResponse[Dict[str, Any]]:
        """
        处理上传的文件
        Args:
            files: 上传的文件列表
        Returns:
            ApiResponse: 包含处理结果的响应对象
        """
        try:
            # 验证文件
            is_valid, error_msg = await FileUtils.validate_files(files)
            if not is_valid:
                return ApiResponse.error(error_msg)

            # 提取所有文件的文本内容
            all_content = []
            for file in files:
                content = await self._extract_file_content(file)
                if content:
                    all_content.append(content)

            if not all_content:
                return ApiResponse.error("未能从文件中提取到有效内容")

            # 将所有内容合并并发送给AI处理
            combined_content = "\n".join(all_content)
            ai_response = await self.ai_service.process_chat("deepseek", 
                f"请分析以下文本内容并提取所有英文单词的数量：\n{combined_content}")

            return ApiResponse.success(
                data={
                    "content": combined_content,  # 原始文本内容
                    "ai_analysis": ai_response.data  # AI分析结果
                }
            )

        except Exception as e:
            logger.error(f"文件处理失败: {str(e)}", exc_info=True)
            return ApiResponse.error(str(e))

    async def _extract_file_content(self, file: UploadFile) -> str:
        """
        从文件中提取文本内容
        Args:
            file: 上传的文件
        Returns:
            str: 提取的文本内容
        """
        try:
            content = await file.read()
            text_content = ""
            
            # 根据文件类型选择不同的提取方法
            if file.filename.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text_content = "\n".join(page.extract_text() for page in pdf_reader.pages)
            
            elif file.filename.endswith(('.doc', '.docx')):
                doc = docx.Document(io.BytesIO(content))
                text_content = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            
            elif file.filename.endswith(('.txt')):
                text_content = content.decode('utf-8')
            
            else:
                # 对于其他类型的文件，直接返回二进制内容供AI处理
                text_content = str(content)

            await file.seek(0)  # 重置文件指针
            return text_content

        except Exception as e:
            logger.error(f"文件内容提取失败: {str(e)}", exc_info=True)
            return "" 