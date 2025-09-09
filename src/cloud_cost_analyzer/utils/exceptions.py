"""
异常定义模块
"""
from typing import Optional, Dict, Any
import traceback
import logging


class CloudCostAnalyzerError(Exception):
    """云费用分析器基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 provider: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            provider: 云服务提供商
            details: 附加详细信息
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.provider = provider
        self.details = details or {}
        self.timestamp = None
        
        # 记录异常堆栈信息
        self.traceback_str = traceback.format_exc()
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'provider': self.provider,
            'details': self.details,
            'timestamp': self.timestamp,
            'traceback': self.traceback_str if self.details.get('include_traceback') else None
        }
    
    def log_error(self, logger: Optional[logging.Logger] = None) -> None:
        """记录错误日志"""
        if logger is None:
            logger = logging.getLogger(__name__)
        
        logger.error(f"[{self.__class__.__name__}] {self.message}", 
                    extra={
                        'error_code': self.error_code,
                        'provider': self.provider,
                        'details': self.details
                    })


# 连接相关异常
class ConnectionError(CloudCostAnalyzerError):
    """连接异常基类"""
    pass


class AWSConnectionError(ConnectionError):
    """AWS连接异常"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 aws_error: Optional[Exception] = None):
        super().__init__(message, error_code, 'aws')
        if aws_error:
            self.details['aws_error'] = str(aws_error)
            self.details['aws_error_type'] = aws_error.__class__.__name__


class AliyunConnectionError(ConnectionError):
    """阿里云连接异常"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code, 'aliyun')


class TencentConnectionError(ConnectionError):
    """腾讯云连接异常"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code, 'tencent')


class VolcengineConnectionError(ConnectionError):
    """火山云连接异常"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code, 'volcengine')


# 配置相关异常
class ConfigurationError(CloudCostAnalyzerError):
    """配置异常"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                 config_value: Optional[Any] = None):
        super().__init__(message, 'CONFIG_ERROR')
        self.details['config_key'] = config_key
        self.details['config_value'] = config_value


class CredentialError(ConfigurationError):
    """凭证配置异常"""
    
    def __init__(self, message: str, provider: str, credential_type: Optional[str] = None):
        super().__init__(message, 'CREDENTIAL_ERROR')
        self.provider = provider
        self.details['credential_type'] = credential_type


# 数据处理相关异常
class DataValidationError(CloudCostAnalyzerError):
    """数据验证异常"""
    
    def __init__(self, message: str, field_name: Optional[str] = None, 
                 field_value: Optional[Any] = None):
        super().__init__(message, 'VALIDATION_ERROR')
        self.details['field_name'] = field_name
        self.details['field_value'] = field_value


class DataProcessingError(CloudCostAnalyzerError):
    """数据处理异常"""
    
    def __init__(self, message: str, processing_step: Optional[str] = None, 
                 data_sample: Optional[Any] = None):
        super().__init__(message, 'PROCESSING_ERROR')
        self.details['processing_step'] = processing_step
        self.details['data_sample'] = data_sample


# 分析相关异常
class AnalysisError(CloudCostAnalyzerError):
    """分析异常"""
    
    def __init__(self, message: str, provider: Optional[str] = None, 
                 analysis_type: Optional[str] = None):
        super().__init__(message, 'ANALYSIS_ERROR', provider)
        self.details['analysis_type'] = analysis_type


# API相关异常
class APIError(CloudCostAnalyzerError):
    """API调用异常"""
    
    def __init__(self, message: str, api_endpoint: Optional[str] = None, 
                 status_code: Optional[int] = None, response_data: Optional[Any] = None):
        super().__init__(message, 'API_ERROR')
        self.details['api_endpoint'] = api_endpoint
        self.details['status_code'] = status_code
        self.details['response_data'] = response_data


class RateLimitError(APIError):
    """API限流异常"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, error_code='RATE_LIMIT_ERROR')
        self.details['retry_after'] = retry_after


# 报告生成相关异常
class ReportGenerationError(CloudCostAnalyzerError):
    """报告生成异常"""
    
    def __init__(self, message: str, report_type: Optional[str] = None, 
                 output_path: Optional[str] = None):
        super().__init__(message, 'REPORT_ERROR')
        self.details['report_type'] = report_type
        self.details['output_path'] = output_path


# 通知相关异常
class NotificationError(CloudCostAnalyzerError):
    """通知发送异常"""
    
    def __init__(self, message: str, notification_type: Optional[str] = None, 
                 recipient: Optional[str] = None):
        super().__init__(message, 'NOTIFICATION_ERROR')
        self.details['notification_type'] = notification_type
        self.details['recipient'] = recipient


# 缓存相关异常
class CacheError(CloudCostAnalyzerError):
    """缓存异常"""
    
    def __init__(self, message: str, cache_key: Optional[str] = None, 
                 cache_operation: Optional[str] = None):
        super().__init__(message, 'CACHE_ERROR')
        self.details['cache_key'] = cache_key
        self.details['cache_operation'] = cache_operation


# 异常处理工具函数
def handle_provider_error(provider: str, original_error: Exception) -> CloudCostAnalyzerError:
    """
    统一处理不同云服务提供商的异常
    
    Args:
        provider: 云服务提供商名称
        original_error: 原始异常
        
    Returns:
        转换后的统一异常
    """
    error_message = str(original_error)
    
    # 根据提供商类型选择对应的异常类
    error_classes = {
        'aws': AWSConnectionError,
        'aliyun': AliyunConnectionError,
        'tencent': TencentConnectionError,
        'volcengine': VolcengineConnectionError
    }
    
    error_class = error_classes.get(provider, CloudCostAnalyzerError)
    
    # 尝试提取错误代码
    error_code = None
    if hasattr(original_error, 'response'):
        error_code = getattr(original_error.response.get('Error', {}), 'Code', None)
    elif hasattr(original_error, 'code'):
        error_code = original_error.code
    
    return error_class(error_message, error_code)


def log_and_reraise(logger: logging.Logger, error: Exception, 
                    context: Optional[str] = None) -> None:
    """
    记录错误并重新抛出
    
    Args:
        logger: 日志记录器
        error: 异常对象
        context: 上下文信息
    """
    if isinstance(error, CloudCostAnalyzerError):
        error.log_error(logger)
    else:
        logger.error(f"Unexpected error{' in ' + context if context else ''}: {error}", 
                    exc_info=True)
    
    raise error


# 异常重试装饰器
def retry_on_exception(max_retries: int = 3, backoff_factor: float = 1.0, 
                      exceptions: tuple = (CloudCostAnalyzerError,)):
    """
    异常重试装饰器
    
    Args:
        max_retries: 最大重试次数
        backoff_factor: 退避因子
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        import time
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        time.sleep(wait_time)
                        continue
                    break
                except Exception as e:
                    # 对于不在重试范围内的异常，直接抛出
                    raise e
            
            # 如果所有重试都失败，抛出最后一个异常
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


# 通用云服务提供商异常
class CloudProviderError(CloudCostAnalyzerError):
    """云服务提供商通用异常"""
    pass


# 兼容性别名（保持向后兼容）
AWSAnalyzerError = AnalysisError  # 向后兼容
AWSConfigError = ConfigurationError  # 向后兼容
