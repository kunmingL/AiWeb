from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
    """
    应用程序配置类
    使用pydantic_settings的BaseSettings来管理环境变量和配置
    """
    # API密钥配置
    DASHSCOPE_API_KEY: str = ""    # 通义千问API密钥
    
    # Token使用量告警阈值
    TOKEN_ALERT_THRESHOLD: int = 10000  # 当剩余token小于此值时触发告警
    
    # 文件存储配置
    TEMP_FILE_PATH: str = "temp"  # 临时文件存储目录
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 服务配置
    SERVICE_TIMEOUT: int = 30  # 服务调用超时时间（秒）
    MAX_RETRIES: int = 3      # 最大重试次数
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        """pydantic配置类"""
        env_file = ".env"  # 指定环境变量文件路径

# 创建全局配置实例
settings = Settings() 