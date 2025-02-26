from config import settings

class TokenCounter:
    """
    Token使用量计数器
    用于监控各AI模型的token使用情况并提供告警功能
    """
    # 定义token告警阈值
    TOKEN_ALERT_THRESHOLD = settings.TOKEN_ALERT_THRESHOLD

    def __init__(self):
        """初始化token计数器"""
        self.tongyi_tokens = 20000    # 通义千问初始token数
        self.deepseek_tokens = 20000  # DeepSeek初始token数

    def check_threshold(self):
        """
        检查token使用量是否达到告警阈值
        返回:
            dict: 需要告警的模型及其消息
        """
        alert = {}
        if self.tongyi_tokens < self.TOKEN_ALERT_THRESHOLD:
            alert["tongyi"] = f"通义千问剩余token不足{self.TOKEN_ALERT_THRESHOLD}"
        if self.deepseek_tokens < self.TOKEN_ALERT_THRESHOLD:
            alert["deepseek"] = f"Deepseek剩余token不足{self.TOKEN_ALERT_THRESHOLD}"
        return alert

    def update_tongyi_tokens(self, tokens: int):
        """
        更新通义千问的token数量
        Args:
            tokens: 新的token数量
        """
        self.tongyi_tokens = tokens

    def update_deepseek_tokens(self, tokens: int):
        """
        更新DeepSeek的token数量
        Args:
            tokens: 新的token数量
        """
        self.deepseek_tokens = tokens

    def get_model_tokens(self, model: str) -> int:
        """
        获取指定模型的剩余token数量
        Args:
            model: 模型名称
        Returns:
            int: 剩余token数量
        """
        if model == "tongyi":
            return self.tongyi_tokens
        elif model == "deepseek":
            return self.deepseek_tokens
        return 0 