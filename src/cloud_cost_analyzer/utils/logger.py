"""
日志管理模块
"""
import logging
import sys
from typing import Optional


class Logger:
    """日志管理器"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self) -> None:
        """设置日志器"""
        self._logger = logging.getLogger('cloud_cost_analyzer')
        self._logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self._logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # 创建格式器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            self._logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """获取日志器实例"""
        return self._logger
    
    @classmethod
    def get_instance(cls) -> 'Logger':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def get_logger() -> logging.Logger:
    """获取日志器实例的便捷函数"""
    return Logger.get_instance().get_logger()


# 创建全局日志器实例
logger = get_logger()
