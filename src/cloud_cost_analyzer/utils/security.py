"""
安全工具模块 - 敏感信息保护和输入验证
"""
import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet
import json
import os
from functools import wraps


class SecureLogger:
    """安全日志记录器 - 自动脱敏敏感信息"""
    
    SENSITIVE_KEYS = [
        'password', 'secret', 'key', 'token', 'credential', 
        'access_key', 'secret_key', 'api_key', 'auth', 'private'
    ]
    
    SENSITIVE_PATTERNS = [
        r'[A-Za-z0-9+/]{40,}={0,2}',  # Base64编码的密钥
        r'AKIA[0-9A-Z]{16}',  # AWS Access Key ID
        r'[0-9a-f]{40}',  # SHA1哈希
        r'[0-9a-f]{64}',  # SHA256哈希
    ]
    
    def __init__(self, logger_name: str = 'secure_logger'):
        self.logger = logging.getLogger(logger_name)
    
    def log_safe(self, message: str, data: Optional[Dict[str, Any]] = None, level: int = logging.INFO):
        """安全记录日志，自动脱敏敏感信息"""
        safe_message = self._mask_sensitive_data(message)
        safe_data = self._mask_sensitive_data(data) if data else None
        
        if safe_data:
            self.logger.log(level, f"{safe_message} | Data: {safe_data}")
        else:
            self.logger.log(level, safe_message)
    
    def _mask_sensitive_data(self, data: Any) -> Any:
        """递归脱敏数据结构中的敏感信息"""
        if isinstance(data, str):
            return self._mask_string(data)
        elif isinstance(data, dict):
            return {k: self._mask_sensitive_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        else:
            return data
    
    def _mask_string(self, text: str) -> str:
        """脱敏字符串中的敏感信息"""
        if not text:
            return text
        
        # 检查是否包含敏感键名
        text_lower = text.lower()
        for sensitive_key in self.SENSITIVE_KEYS:
            if sensitive_key in text_lower:
                return "***MASKED***"
        
        # 检查是否匹配敏感模式
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, text):
                return "***MASKED***"
        
        return text


class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """验证日期格式"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """验证日期范围"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 检查开始日期不能晚于结束日期
            if start > end:
                return False
            
            # 检查不能是未来日期
            if end > datetime.now():
                return False
            
            # 检查日期范围不能超过2年
            if (end - start).days > 730:
                return False
            
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_provider(provider: str) -> bool:
        """验证云服务提供商"""
        valid_providers = ['aws', 'aliyun', 'tencent', 'volcengine']
        return provider.lower() in valid_providers
    
    @staticmethod
    def validate_region(region: str, provider: str) -> bool:
        """验证区域"""
        # 简化的区域验证，实际项目中应该有完整的区域列表
        if not region or len(region) < 3:
            return False
        
        # 基本格式检查
        if provider == 'aws':
            return re.match(r'^[a-z]{2}-[a-z]+-\d+$', region)
        elif provider in ['aliyun', 'tencent', 'volcengine']:
            return re.match(r'^cn-[a-z]+$', region)
        
        return True
    
    @staticmethod
    def validate_granularity(granularity: str) -> bool:
        """验证数据粒度"""
        valid_granularities = ['DAILY', 'MONTHLY', 'HOURLY']
        return granularity.upper() in valid_granularities


class ConfigEncryption:
    """配置文件加密工具"""
    
    def __init__(self, key_file: str = '.encryption_key'):
        self.key_file = key_file
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """获取或创建加密密钥"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # 设置文件权限为仅所有者可读
            os.chmod(self.key_file, 0o600)
            return key
    
    def encrypt_config(self, config: Dict[str, Any], output_file: str) -> bool:
        """加密配置文件"""
        try:
            config_json = json.dumps(config, ensure_ascii=False, indent=2)
            encrypted_data = self.cipher.encrypt(config_json.encode('utf-8'))
            
            with open(output_file, 'wb') as f:
                f.write(encrypted_data)
            
            # 设置文件权限
            os.chmod(output_file, 0o600)
            return True
        except Exception as e:
            logging.error(f"配置文件加密失败: {e}")
            return False
    
    def decrypt_config(self, encrypted_file: str) -> Optional[Dict[str, Any]]:
        """解密配置文件"""
        try:
            with open(encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            logging.error(f"配置文件解密失败: {e}")
            return None


def secure_function(func):
    """安全函数装饰器 - 自动记录和验证"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        secure_logger = SecureLogger()
        
        # 记录函数调用
        secure_logger.log_safe(
            f"调用函数: {func.__name__}",
            {"args_count": len(args), "kwargs_keys": list(kwargs.keys())}
        )
        
        try:
            result = func(*args, **kwargs)
            secure_logger.log_safe(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            secure_logger.log_safe(f"函数 {func.__name__} 执行失败: {str(e)}", level=logging.ERROR)
            raise
    
    return wrapper


class SecurityManager:
    """安全管理器 - 统一管理安全相关功能"""
    
    def __init__(self):
        self.secure_logger = SecureLogger()
        self.validator = InputValidator()
        self.encryption = ConfigEncryption()
    
    def validate_analysis_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证分析请求"""
        errors = []
        
        # 验证日期
        if 'start_date' in request_data:
            if not self.validator.validate_date_format(request_data['start_date']):
                errors.append("开始日期格式无效，应为YYYY-MM-DD")
        
        if 'end_date' in request_data:
            if not self.validator.validate_date_format(request_data['end_date']):
                errors.append("结束日期格式无效，应为YYYY-MM-DD")
        
        if 'start_date' in request_data and 'end_date' in request_data:
            if not self.validator.validate_date_range(request_data['start_date'], request_data['end_date']):
                errors.append("日期范围无效")
        
        # 验证提供商
        if 'providers' in request_data:
            for provider in request_data['providers']:
                if not self.validator.validate_provider(provider):
                    errors.append(f"不支持的云服务提供商: {provider}")
        
        # 验证粒度
        if 'granularity' in request_data:
            if not self.validator.validate_granularity(request_data['granularity']):
                errors.append("无效的数据粒度")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def sanitize_output(self, data: Any) -> Any:
        """清理输出数据中的敏感信息"""
        return self.secure_logger._mask_sensitive_data(data)
