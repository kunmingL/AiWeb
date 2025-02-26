from pydantic import BaseModel

class FileObject(BaseModel):
    """
    文件对象数据模型
    用于处理文件上传和下载的数据结构
    """
    fileName: str       # 文件名，包含扩展名
    fileContent: bytes  # 文件二进制内容 