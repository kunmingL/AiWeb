import os
from typing import List, Tuple
from fastapi import UploadFile
import magic  # 用于文件类型检测
from config import settings

class FileUtils:
    """文件处理工具类"""
    
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'ppt', 'pptx', 
        'xls', 'xlsx', 'png', 'jpg', 'jpeg'
    }
    
    @staticmethod
    async def validate_files(files: List[UploadFile]) -> Tuple[bool, str]:
        """
        验证上传的文件
        检查文件类型和大小
        """
        for file in files:
            # 检查文件扩展名
            ext = file.filename.split('.')[-1].lower()
            if ext not in FileUtils.ALLOWED_EXTENSIONS:
                return False, f"不支持的文件类型: {ext}"
            
            # 检查文件大小
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                return False, f"文件大小超过限制: {file.filename}"
            
            # 重置文件指针
            await file.seek(0)
            
            # 验证文件类型
            mime = magic.from_buffer(content, mime=True)
            if not FileUtils.is_valid_mime_type(mime):
                return False, f"文件类型不合法: {file.filename}"
        
        return True, ""

    @staticmethod
    def is_valid_mime_type(mime_type: str) -> bool:
        """验证MIME类型"""
        valid_mimes = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'image/png',
            'image/jpeg'
        }
        return mime_type in valid_mimes

    @staticmethod
    def save_file(file_content: bytes, filename: str, directory: str) -> str:
        """保存文件到指定目录"""
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        return file_path 