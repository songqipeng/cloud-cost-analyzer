"""
安全日志模块
实现敏感信息脱敏和安全日志记录
"""
import logging
import sys
import re
import json
import hashlib
import os
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pathlib import Path


class SensitiveDataMasker:
    """敏感数据脱敏器"""
    
    def __init__(self):
        # 敏感信息匹配模式
        self.patterns = {
            # AWS 凭证
            'aws_access_key': re.compile(r'AKIA[0-9A-Z]{16}', re.IGNORECASE),
            'aws_secret_key': re.compile(r'[A-Za-z0-9/+=]{40}'),
            
            # 阿里云凭证
            'aliyun_access_key': re.compile(r'LTAI[0-9A-Za-z]{16,}', re.IGNORECASE),
            'aliyun_secret_key': re.compile(r'[A-Za-z0-9]{30,}'),
            
            # 腾讯云凭证
            'tencent_secret_id': re.compile(r'AKID[A-Za-z0-9]{32}', re.IGNORECASE),
            'tencent_secret_key': re.compile(r'[A-Za-z0-9]{32}'),
            
            # 火山云凭证
            'volcengine_access_key': re.compile(r'AKLT[A-Za-z0-9]{32}', re.IGNORECASE),
            'volcengine_secret_key': re.compile(r'[A-Za-z0-9/+=]{40,}'),
            
            # 通用敏感信息
            'email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            'phone': re.compile(r'1[3-9]\d{9}'),
            'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            'password': re.compile(r'(?i)(password|passwd|pwd|secret)[\s:=]+[^\s\n]{6,}'),
            'token': re.compile(r'(?i)(token|jwt|bearer)[\s:=]+[A-Za-z0-9._-]{20,}'),
            'url_with_auth': re.compile(r'https?://[^:]+:[^@]+@[^\s]+'),
            
            # 银行卡和身份证（中国）
            'bank_card': re.compile(r'\b[0-9]{16,19}\b'),
            'id_card': re.compile(r'\b[1-9]\d{5}[1-2]\d{3}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]\b'),
        }
        
        # 特殊字段名匹配（用于JSON/dict脱敏）
        self.sensitive_fields = {
            'access_key', 'access_key_id', 'secret_key', 'secret_access_key',
            'password', 'passwd', 'pwd', 'token', 'jwt', 'auth', 'authorization',
            'secret', 'credential', 'credentials', 'api_key', 'apikey',
            'session_token', 'private_key', 'cert', 'certificate'
        }
    
    def mask_text(self, text: str) -> str:
        """
        脱敏文本中的敏感信息
        
        Args:
            text: 原始文本
            
        Returns:
            脱敏后的文本
        """
        if not isinstance(text, str):
            text = str(text)
        
        # 对每种模式进行脱敏
        for pattern_name, pattern in self.patterns.items():
            text = pattern.sub(self._create_mask, text)
        
        return text
    
    def mask_dict(self, data: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
        """
        脱敏字典中的敏感信息
        
        Args:
            data: 原始字典
            max_depth: 最大递归深度
            
        Returns:
            脱敏后的字典
        """
        if max_depth <= 0:
            return data
        
        if not isinstance(data, dict):
            return data
        
        masked_data = {}
        
        for key, value in data.items():
            key_lower = str(key).lower()
            
            # 检查字段名是否为敏感字段
            if any(sensitive_field in key_lower for sensitive_field in self.sensitive_fields):
                masked_data[key] = self._mask_value(value)
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value, max_depth - 1)
            elif isinstance(value, list):
                masked_data[key] = [
                    self.mask_dict(item, max_depth - 1) if isinstance(item, dict)
                    else self._mask_value(item) if self._is_sensitive_value(str(item))
                    else item
                    for item in value
                ]
            elif isinstance(value, str) and self._is_sensitive_value(value):
                masked_data[key] = self._mask_value(value)
            else:
                masked_data[key] = value
        
        return masked_data
    
    def _create_mask(self, match) -> str:
        """创建掩码字符串"""
        matched_text = match.group(0)
        if len(matched_text) <= 4:
            return '*' * len(matched_text)
        else:
            # 显示前2个和后2个字符，中间用*替换
            return matched_text[:2] + '*' * (len(matched_text) - 4) + matched_text[-2:]
    
    def _mask_value(self, value: Any) -> str:
        """脱敏单个值"""
        if value is None:
            return None
        
        str_value = str(value)
        
        if len(str_value) <= 4:
            return '*' * len(str_value)
        elif len(str_value) <= 8:
            return str_value[:2] + '*' * (len(str_value) - 2)
        else:
            return str_value[:3] + '*' * (len(str_value) - 6) + str_value[-3:]
    
    def _is_sensitive_value(self, value: str) -> bool:
        """判断值是否为敏感信息"""
        for pattern in self.patterns.values():
            if pattern.search(value):
                return True
        return False


class SecureFormatter(logging.Formatter):
    """安全日志格式化器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.masker = SensitiveDataMasker()
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录，自动脱敏敏感信息"""
        # 脱敏日志消息
        if hasattr(record, 'msg') and record.msg:
            if isinstance(record.msg, str):
                record.msg = self.masker.mask_text(record.msg)
            elif isinstance(record.msg, dict):
                record.msg = self.masker.mask_dict(record.msg)
        
        # 脱敏参数
        if hasattr(record, 'args') and record.args:
            masked_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    masked_args.append(self.masker.mask_text(arg))
                elif isinstance(arg, dict):
                    masked_args.append(self.masker.mask_dict(arg))
                else:
                    masked_args.append(arg)
            record.args = tuple(masked_args)
        
        return super().format(record)


class SecureLogger:
    """安全日志管理器"""
    
    def __init__(self, name: str = 'cloud_cost_analyzer', 
                 log_level: int = logging.INFO,
                 enable_file_logging: bool = True,
                 log_dir: str = 'logs',
                 max_log_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        """
        初始化安全日志器
        
        Args:
            name: 日志器名称
            log_level: 日志级别
            enable_file_logging: 是否启用文件日志
            log_dir: 日志目录
            max_log_size: 单个日志文件最大大小（字节）
            backup_count: 备份文件数量
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.masker = SensitiveDataMasker()
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers(enable_file_logging, log_dir, max_log_size, backup_count)
    
    def _setup_handlers(self, enable_file_logging: bool, log_dir: str,
                       max_log_size: int, backup_count: int):
        """设置日志处理器"""
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 安全格式化器
        secure_formatter = SecureFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(secure_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if enable_file_logging:
            try:
                from logging.handlers import RotatingFileHandler
                
                # 创建日志目录
                log_path = Path(log_dir)
                log_path.mkdir(exist_ok=True)
                
                # 应用日志文件
                app_log_file = log_path / 'app.log'
                app_handler = RotatingFileHandler(
                    app_log_file,
                    maxBytes=max_log_size,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                app_handler.setLevel(logging.DEBUG)
                app_handler.setFormatter(secure_formatter)
                self.logger.addHandler(app_handler)
                
                # 错误日志文件
                error_log_file = log_path / 'error.log'
                error_handler = RotatingFileHandler(
                    error_log_file,
                    maxBytes=max_log_size,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(secure_formatter)
                self.logger.addHandler(error_handler)
                
                # 审计日志文件（记录重要操作）
                audit_log_file = log_path / 'audit.log'
                audit_handler = RotatingFileHandler(
                    audit_log_file,
                    maxBytes=max_log_size,
                    backupCount=backup_count * 2,  # 审计日志保留更久
                    encoding='utf-8'
                )
                audit_handler.setLevel(logging.INFO)
                audit_formatter = SecureFormatter(
                    '%(asctime)s - AUDIT - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                audit_handler.setFormatter(audit_formatter)
                
                # 创建审计日志器
                self.audit_logger = logging.getLogger(f'{self.logger.name}.audit')
                self.audit_logger.setLevel(logging.INFO)
                self.audit_logger.addHandler(audit_handler)
                
            except Exception as e:
                self.logger.warning(f"Failed to setup file logging: {e}")
    
    def debug(self, message: Union[str, Dict], *args, **kwargs):
        """记录调试日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: Union[str, Dict], *args, **kwargs):
        """记录信息日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: Union[str, Dict], *args, **kwargs):
        """记录警告日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: Union[str, Dict], *args, **kwargs):
        """记录错误日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: Union[str, Dict], *args, **kwargs):
        """记录严重错误日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def audit(self, action: str, details: Dict[str, Any] = None, 
             user_id: str = None, result: str = 'SUCCESS'):
        """
        记录审计日志
        
        Args:
            action: 操作类型
            details: 操作详情
            user_id: 用户ID
            result: 操作结果
        """
        if hasattr(self, 'audit_logger'):
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'user_id': user_id or 'system',
                'result': result,
                'details': self.masker.mask_dict(details or {})
            }
            
            self.audit_logger.info(json.dumps(audit_entry, ensure_ascii=False, default=str))
    
    def log_api_call(self, provider: str, operation: str, 
                    duration: float = None, success: bool = True, 
                    error_message: str = None):
        """
        记录API调用日志
        
        Args:
            provider: 云服务提供商
            operation: 操作类型
            duration: 耗时（秒）
            success: 是否成功
            error_message: 错误信息
        """
        log_data = {
            'provider': provider,
            'operation': operation,
            'duration_ms': round(duration * 1000, 2) if duration else None,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if error_message:
            log_data['error'] = self.masker.mask_text(error_message)
        
        if success:
            self.info(f"API call successful: {json.dumps(log_data, default=str)}")
        else:
            self.error(f"API call failed: {json.dumps(log_data, default=str)}")
        
        # 记录审计日志
        self.audit(
            action=f"api_call_{provider}_{operation}",
            details=log_data,
            result='SUCCESS' if success else 'FAILURE'
        )
    
    def log_cost_analysis(self, provider: str, date_range: str, 
                         total_cost: float, service_count: int):
        """
        记录成本分析日志
        
        Args:
            provider: 云服务提供商
            date_range: 日期范围
            total_cost: 总费用
            service_count: 服务数量
        """
        analysis_data = {
            'provider': provider,
            'date_range': date_range,
            'total_cost': total_cost,
            'service_count': service_count,
            'timestamp': datetime.now().isoformat()
        }
        
        self.info(f"Cost analysis completed: {json.dumps(analysis_data)}")
        self.audit(
            action=f"cost_analysis_{provider}",
            details=analysis_data,
            result='SUCCESS'
        )
    
    def get_log_stats(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        stats = {
            'logger_name': self.logger.name,
            'log_level': self.logger.level,
            'handlers_count': len(self.logger.handlers),
            'handlers': []
        }
        
        for handler in self.logger.handlers:
            handler_info = {
                'type': type(handler).__name__,
                'level': handler.level,
                'formatter': type(handler.formatter).__name__ if handler.formatter else None
            }
            
            if hasattr(handler, 'baseFilename'):
                handler_info['file'] = handler.baseFilename
            
            stats['handlers'].append(handler_info)
        
        return stats


# 全局安全日志器实例
_secure_logger: Optional[SecureLogger] = None


def get_secure_logger(name: str = 'cloud_cost_analyzer', **kwargs) -> SecureLogger:
    """
    获取全局安全日志器实例
    
    Args:
        name: 日志器名称
        **kwargs: 其他初始化参数
        
    Returns:
        安全日志器实例
    """
    global _secure_logger
    
    if _secure_logger is None:
        # 从环境变量读取配置
        log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        
        enable_file_logging = os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true'
        log_dir = os.getenv('LOG_DIR', 'logs')
        
        _secure_logger = SecureLogger(
            name=name,
            log_level=log_level,
            enable_file_logging=enable_file_logging,
            log_dir=log_dir,
            **kwargs
        )
    
    return _secure_logger


# 便捷函数
def get_logger() -> SecureLogger:
    """获取默认安全日志器"""
    return get_secure_logger()


# 向后兼容
def mask_sensitive_data(data: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
    """
    脱敏敏感数据的便捷函数
    
    Args:
        data: 要脱敏的数据
        
    Returns:
        脱敏后的数据
    """
    masker = SensitiveDataMasker()
    
    if isinstance(data, str):
        return masker.mask_text(data)
    elif isinstance(data, dict):
        return masker.mask_dict(data)
    else:
        return data