import edge_tts
import io
from langdetect import detect
from typing import Dict, Tuple
import asyncio

class SpeechUtils:
    """语音处理工具类"""
    
    # 语言和语音模型映射
    LANGUAGE_SPEAKER: Dict[str, str] = {
        "ja": "ja-JP-NanamiNeural",
        "fr": "fr-FR-DeniseNeural",
        "es": "ca-ES-JoanaNeural",
        "de": "de-DE-KatjaNeural",
        "zh-cn": "zh-CN-XiaoyiNeural",
        "en": "en-US-AnaNeural",
    }

    @staticmethod
    async def generate_voice_bytes(text: str) -> Tuple[bytes, str]:
        """
        生成语音字节数组
        Args:
            text: 需要转换的文本
        Returns:
            Tuple[bytes, str]: (音频字节数组, 音频格式)
        """
        try:
            # 检测文本语言
            language = detect(text)
            # 如果检测到的语言不在支持列表中，默认使用英语
            if language not in SpeechUtils.LANGUAGE_SPEAKER:
                language = "en"

            # 创建通信对象
            communicate = edge_tts.Communicate(
                text, 
                SpeechUtils.LANGUAGE_SPEAKER[language]
            )

            # 创建内存缓冲区
            audio_buffer = io.BytesIO()
            
            # 使用stream方法获取音频数据
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
                
            # 获取音频字节数组
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.getvalue()
            
            return audio_bytes, "audio/mp3"

        except Exception as e:
            raise Exception(f"语音生成失败: {str(e)}") 