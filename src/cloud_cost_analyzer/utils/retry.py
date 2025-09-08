"""
改进的错误处理和重试机制
支持指数退避、熔断器、限流等功能
"""
import asyncio
import time
import random
from typing import Any, Callable, Dict, List, Optional, Type, Union
from functools import wraps
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor

import backoff
from cloud_cost_analyzer.utils.logger import get_logger
from cloud_cost_analyzer.utils.exceptions import (
    AWSConnectionError, AWSAnalyzerError, CloudProviderError, CacheError
)

logger = get_logger()


class CircuitBreakerError(Exception):
    """熔断器错误"""
    pass


class RateLimitError(Exception):
    """限流错误"""
    pass


class CircuitBreaker:
    """
    熔断器实现
    
    当错误率达到阈值时，暂时阻止请求以保护下游服务
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, 
                 expected_exception: Type[Exception] = Exception):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 失败次数阈值
            timeout: 熔断超时时间（秒）
            expected_exception: 预期异常类型
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def __enter__(self):
        """进入熔断器上下文"""
        with self._lock:
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                    logger.info("Circuit breaker state: HALF_OPEN")
                else:
                    raise CircuitBreakerError(f"Circuit breaker is OPEN, timeout: {self.timeout}s")
            
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出熔断器上下文"""
        with self._lock:
            if exc_type and issubclass(exc_type, self.expected_exception):
                # 记录失败
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                    logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
                elif self.state == 'HALF_OPEN':
                    self.state = 'OPEN'
                    logger.warning("Circuit breaker re-opened during half-open state")
            else:
                # 记录成功
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                    logger.info("Circuit breaker closed after successful attempt")
    
    def _should_attempt_reset(self) -> bool:
        """判断是否应该尝试重置"""
        if not self.last_failure_time:
            return True
        return time.time() - self.last_failure_time >= self.timeout


class RateLimiter:
    """
    速率限制器
    
    使用令牌桶算法限制请求频率
    """
    
    def __init__(self, rate: float, burst: int = 1):
        """
        初始化速率限制器
        
        Args:
            rate: 每秒允许的请求数
            burst: 突发请求数（令牌桶容量）
        """
        self.rate = rate
        self.burst = burst
        
        self.tokens = burst
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    def acquire(self, timeout: float = 1.0) -> bool:
        """
        获取令牌
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            是否成功获取令牌
        """
        deadline = time.time() + timeout
        
        while time.time() < deadline:
            with self._lock:
                now = time.time()
                
                # 根据时间流逝补充令牌
                time_passed = now - self.last_update
                self.tokens = min(self.burst, self.tokens + time_passed * self.rate)
                self.last_update = now
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
            
            # 短暂等待后重试
            time.sleep(0.01)
        
        return False
    
    def __enter__(self):
        """进入速率限制器上下文"""
        if not self.acquire():
            raise RateLimitError("Rate limit exceeded")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出速率限制器上下文"""
        pass


def retry_with_backoff(
    max_tries: int = 3,
    backoff_type: str = 'exponential',
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    带指数退避的重试装饰器
    
    Args:
        max_tries: 最大重试次数
        backoff_type: 退避类型 ('exponential', 'linear', 'constant')
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        jitter: 是否添加随机抖动
        exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_tries - 1:
                        # 最后一次尝试，不再重试
                        break
                    
                    # 计算延迟时间
                    if backoff_type == 'exponential':
                        delay = min(base_delay * (2 ** attempt), max_delay)
                    elif backoff_type == 'linear':
                        delay = min(base_delay * (attempt + 1), max_delay)
                    else:  # constant
                        delay = base_delay
                    
                    # 添加随机抖动
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            
            # 所有重试都失败，抛出最后的异常
            raise last_exception
        
        return wrapper
    return decorator


def async_retry_with_backoff(
    max_tries: int = 3,
    backoff_type: str = 'exponential',
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    异步版本的带指数退避的重试装饰器
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_tries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_tries - 1:
                        break
                    
                    if backoff_type == 'exponential':
                        delay = min(base_delay * (2 ** attempt), max_delay)
                    elif backoff_type == 'linear':
                        delay = min(base_delay * (attempt + 1), max_delay)
                    else:
                        delay = base_delay
                    
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Async attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


class RetryManager:
    """
    重试管理器
    
    集中管理不同类型请求的重试策略
    """
    
    def __init__(self):
        self.strategies = {
            'aws_api': {
                'max_tries': 3,
                'base_delay': 1.0,
                'max_delay': 16.0,
                'exceptions': (AWSConnectionError, ConnectionError, TimeoutError)
            },
            'cloud_api': {
                'max_tries': 3,
                'base_delay': 2.0,
                'max_delay': 32.0,
                'exceptions': (CloudProviderError, ConnectionError, TimeoutError)
            },
            'cache_operation': {
                'max_tries': 2,
                'base_delay': 0.5,
                'max_delay': 2.0,
                'exceptions': (CacheError, ConnectionError)
            },
            'file_operation': {
                'max_tries': 2,
                'base_delay': 0.1,
                'max_delay': 1.0,
                'exceptions': (IOError, OSError)
            }
        }
        
        # 熔断器实例
        self.circuit_breakers = {}
        
        # 速率限制器实例
        self.rate_limiters = {}
    
    def get_circuit_breaker(self, key: str, failure_threshold: int = 5, 
                          timeout: int = 60) -> CircuitBreaker:
        """获取熔断器实例"""
        if key not in self.circuit_breakers:
            self.circuit_breakers[key] = CircuitBreaker(
                failure_threshold=failure_threshold,
                timeout=timeout
            )
        return self.circuit_breakers[key]
    
    def get_rate_limiter(self, key: str, rate: float = 10.0, 
                        burst: int = 5) -> RateLimiter:
        """获取速率限制器实例"""
        if key not in self.rate_limiters:
            self.rate_limiters[key] = RateLimiter(rate=rate, burst=burst)
        return self.rate_limiters[key]
    
    def retry_with_strategy(self, strategy_name: str):
        """使用预定义策略的重试装饰器"""
        strategy = self.strategies.get(strategy_name, self.strategies['cloud_api'])
        
        return retry_with_backoff(
            max_tries=strategy['max_tries'],
            base_delay=strategy['base_delay'],
            max_delay=strategy['max_delay'],
            exceptions=strategy['exceptions']
        )
    
    def execute_with_protection(self, func: Callable, strategy_name: str = 'cloud_api',
                              circuit_breaker_key: Optional[str] = None,
                              rate_limiter_key: Optional[str] = None,
                              *args, **kwargs) -> Any:
        """
        使用保护机制执行函数
        
        Args:
            func: 要执行的函数
            strategy_name: 重试策略名称
            circuit_breaker_key: 熔断器键名
            rate_limiter_key: 速率限制器键名
            
        Returns:
            函数执行结果
        """
        # 应用速率限制
        if rate_limiter_key:
            rate_limiter = self.get_rate_limiter(rate_limiter_key)
            with rate_limiter:
                pass
        
        # 应用熔断器
        if circuit_breaker_key:
            circuit_breaker = self.get_circuit_breaker(circuit_breaker_key)
            with circuit_breaker:
                # 应用重试策略
                decorated_func = self.retry_with_strategy(strategy_name)(func)
                return decorated_func(*args, **kwargs)
        else:
            # 仅应用重试策略
            decorated_func = self.retry_with_strategy(strategy_name)(func)
            return decorated_func(*args, **kwargs)


# 全局重试管理器实例
retry_manager = RetryManager()


class ErrorHandler:
    """
    错误处理器
    
    提供统一的错误处理和上报机制
    """
    
    def __init__(self):
        self.error_counts = {}
        self.last_errors = {}
        self._lock = threading.Lock()
    
    def handle_error(self, error: Exception, context: str = "", 
                    notify: bool = False) -> Dict[str, Any]:
        """
        处理错误
        
        Args:
            error: 异常对象
            context: 错误上下文
            notify: 是否发送通知
            
        Returns:
            错误处理结果
        """
        error_type = type(error).__name__
        error_key = f"{context}:{error_type}"
        
        with self._lock:
            # 统计错误次数
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            self.last_errors[error_key] = {
                'timestamp': datetime.now(),
                'message': str(error),
                'count': self.error_counts[error_key]
            }
        
        # 记录日志
        if self.error_counts[error_key] == 1:
            logger.error(f"[{context}] {error_type}: {error}")
        elif self.error_counts[error_key] % 10 == 0:
            logger.error(f"[{context}] {error_type} occurred {self.error_counts[error_key]} times: {error}")
        
        # 根据错误类型提供处理建议
        suggestion = self._get_error_suggestion(error)
        
        result = {
            'error_type': error_type,
            'message': str(error),
            'context': context,
            'count': self.error_counts[error_key],
            'suggestion': suggestion,
            'timestamp': datetime.now().isoformat()
        }
        
        # TODO: 如果notify=True，发送通知
        
        return result
    
    def _get_error_suggestion(self, error: Exception) -> str:
        """根据错误类型提供处理建议"""
        error_suggestions = {
            'AWSConnectionError': '请检查AWS凭证配置和网络连接',
            'ConnectionError': '请检查网络连接和服务状态',
            'TimeoutError': '请检查网络连接或增加超时时间',
            'CacheError': '请检查缓存服务状态',
            'RateLimitError': '请求频率过高，建议降低请求频率',
            'CircuitBreakerError': '服务暂时不可用，请稍后重试'
        }
        
        error_type = type(error).__name__
        return error_suggestions.get(error_type, '请检查错误详情并联系技术支持')
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        with self._lock:
            return {
                'total_error_types': len(self.error_counts),
                'error_counts': self.error_counts.copy(),
                'recent_errors': {
                    k: v for k, v in self.last_errors.items()
                    if (datetime.now() - v['timestamp']).seconds < 3600  # 最近1小时
                }
            }


# 全局错误处理器实例
error_handler = ErrorHandler()