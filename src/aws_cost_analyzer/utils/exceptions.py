"""
异常定义模块
"""
from typing import Optional


class AWSAnalyzerError(Exception):
    """AWS费用分析器基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class AWSConnectionError(AWSAnalyzerError):
    """AWS连接异常"""
    pass


class AWSConfigError(AWSAnalyzerError):
    """AWS配置异常"""
    pass


class DataValidationError(AWSAnalyzerError):
    """数据验证异常"""
    pass


class NotificationError(AWSAnalyzerError):
    """通知发送异常"""
    pass


class ReportGenerationError(AWSAnalyzerError):
    """报告生成异常"""
    pass


class ConfigurationError(AWSAnalyzerError):
    """配置异常"""
    pass
