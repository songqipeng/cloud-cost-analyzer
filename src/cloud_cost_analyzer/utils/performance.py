"""
性能优化工具
"""
import asyncio
import concurrent.futures
import functools
import time
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable
from datetime import datetime
import threading

from cloud_cost_analyzer.utils.logger import get_logger

logger = get_logger()


class Timer:
    """计时器上下文管理器"""
    
    def __init__(self, description: str = "Operation", log_result: bool = True):
        self.description = description
        self.log_result = log_result
        self.start_time = None
        self.end_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting {self.description}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if self.log_result:
            if duration > 1.0:
                logger.info(f"{self.description} completed in {duration:.2f}s")
            else:
                logger.debug(f"{self.description} completed in {duration*1000:.0f}ms")
    
    @property
    def duration(self) -> Optional[float]:
        """获取持续时间（秒）"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


def timing_decorator(description: Optional[str] = None, log_result: bool = True):
    """
    函数计时装饰器
    
    Args:
        description: 操作描述
        log_result: 是否记录结果
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            desc = description or f"{func.__name__}"
            with Timer(desc, log_result):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class AsyncTimer:
    """异步计时器上下文管理器"""
    
    def __init__(self, description: str = "Async Operation", log_result: bool = True):
        self.description = description
        self.log_result = log_result
        self.start_time = None
        self.end_time = None
        
    async def __aenter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting async {self.description}")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if self.log_result:
            if duration > 1.0:
                logger.info(f"Async {self.description} completed in {duration:.2f}s")
            else:
                logger.debug(f"Async {self.description} completed in {duration*1000:.0f}ms")
    
    @property
    def duration(self) -> Optional[float]:
        """获取持续时间（秒）"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


def async_timing_decorator(description: Optional[str] = None, log_result: bool = True):
    """
    异步函数计时装饰器
    
    Args:
        description: 操作描述
        log_result: 是否记录结果
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            desc = description or f"async {func.__name__}"
            async with AsyncTimer(desc, log_result):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self._operations: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    def record_operation(self, operation_name: str, duration: float):
        """记录操作耗时"""
        with self._lock:
            if operation_name not in self._operations:
                self._operations[operation_name] = []
            self._operations[operation_name].append(duration)
    
    def get_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """获取性能统计信息"""
        with self._lock:
            if operation_name:
                if operation_name not in self._operations:
                    return {}
                
                durations = self._operations[operation_name]
                return self._calculate_stats(operation_name, durations)
            else:
                stats = {}
                for op_name, durations in self._operations.items():
                    stats[op_name] = self._calculate_stats(op_name, durations)
                return stats
    
    def _calculate_stats(self, operation_name: str, durations: List[float]) -> Dict[str, Any]:
        """计算统计信息"""
        if not durations:
            return {}
        
        durations_sorted = sorted(durations)
        count = len(durations)
        total = sum(durations)
        average = total / count
        
        return {
            'operation': operation_name,
            'count': count,
            'total_time': round(total, 3),
            'average_time': round(average, 3),
            'min_time': round(min(durations), 3),
            'max_time': round(max(durations), 3),
            'median_time': round(durations_sorted[count // 2], 3),
            'p95_time': round(durations_sorted[int(count * 0.95)], 3) if count > 1 else round(durations[0], 3),
            'p99_time': round(durations_sorted[int(count * 0.99)], 3) if count > 1 else round(durations[0], 3)
        }
    
    def clear_stats(self, operation_name: Optional[str] = None):
        """清空统计信息"""
        with self._lock:
            if operation_name:
                self._operations.pop(operation_name, None)
            else:
                self._operations.clear()


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def monitored_operation(operation_name: str):
    """
    监控操作装饰器
    
    Args:
        operation_name: 操作名称
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_monitor.record_operation(operation_name, duration)
        return wrapper
    return decorator


class ParallelExecutor:
    """并行执行器"""
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        初始化并行执行器
        
        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
    
    def execute_parallel(self, tasks: List[Callable], timeout: Optional[float] = None) -> List[Any]:
        """
        并行执行任务列表
        
        Args:
            tasks: 任务列表
            timeout: 超时时间（秒）
            
        Returns:
            结果列表
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(task) for task in tasks]
            
            results = []
            for future in concurrent.futures.as_completed(futures, timeout=timeout):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Task failed: {e}")
                    results.append(None)
            
            return results
    
    def execute_parallel_with_args(self, func: Callable, args_list: List[tuple], 
                                  timeout: Optional[float] = None) -> List[Any]:
        """
        使用不同参数并行执行同一函数
        
        Args:
            func: 函数
            args_list: 参数列表
            timeout: 超时时间（秒）
            
        Returns:
            结果列表
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(func, *args) for args in args_list]
            
            results = []
            for i, future in enumerate(concurrent.futures.as_completed(futures, timeout=timeout)):
                try:
                    result = future.result()
                    results.append((i, result))
                except Exception as e:
                    logger.error(f"Task {i} failed: {e}")
                    results.append((i, None))
            
            # 按原始顺序排序
            results.sort(key=lambda x: x[0])
            return [result for _, result in results]


class AsyncParallelExecutor:
    """异步并行执行器"""
    
    def __init__(self, max_concurrent: int = 10):
        """
        初始化异步并行执行器
        
        Args:
            max_concurrent: 最大并发数
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_parallel(self, tasks: List[Awaitable], 
                              timeout: Optional[float] = None) -> List[Any]:
        """
        并行执行异步任务列表
        
        Args:
            tasks: 异步任务列表
            timeout: 超时时间（秒）
            
        Returns:
            结果列表
        """
        async def limited_task(task):
            async with self.semaphore:
                return await task
        
        limited_tasks = [limited_task(task) for task in tasks]
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*limited_tasks, return_exceptions=True),
                timeout=timeout
            )
            return results
        except asyncio.TimeoutError:
            logger.error(f"Async tasks timed out after {timeout}s")
            return [None] * len(tasks)
    
    async def execute_parallel_with_args(self, func: Callable, args_list: List[tuple],
                                        timeout: Optional[float] = None) -> List[Any]:
        """
        使用不同参数并行执行同一异步函数
        
        Args:
            func: 异步函数
            args_list: 参数列表
            timeout: 超时时间（秒）
            
        Returns:
            结果列表
        """
        async def limited_task(args):
            async with self.semaphore:
                return await func(*args)
        
        tasks = [limited_task(args) for args in args_list]
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout
            )
            return results
        except asyncio.TimeoutError:
            logger.error(f"Async tasks timed out after {timeout}s")
            return [None] * len(args_list)


class BatchProcessor:
    """批处理器"""
    
    def __init__(self, batch_size: int = 100, max_workers: Optional[int] = None):
        """
        初始化批处理器
        
        Args:
            batch_size: 批处理大小
            max_workers: 最大工作线程数
        """
        self.batch_size = batch_size
        self.executor = ParallelExecutor(max_workers)
    
    def process_in_batches(self, items: List[Any], processor: Callable,
                          timeout: Optional[float] = None) -> List[Any]:
        """
        分批处理项目列表
        
        Args:
            items: 项目列表
            processor: 处理函数（接受一个批次作为参数）
            timeout: 超时时间（秒）
            
        Returns:
            处理结果列表
        """
        # 分批
        batches = [items[i:i + self.batch_size] 
                  for i in range(0, len(items), self.batch_size)]
        
        # 并行处理批次
        batch_tasks = [lambda batch=b: processor(batch) for b in batches]
        batch_results = self.executor.execute_parallel(batch_tasks, timeout)
        
        # 合并结果
        results = []
        for batch_result in batch_results:
            if batch_result is not None:
                results.extend(batch_result)
        
        return results


def optimize_dataframe_operations(df):
    """
    优化DataFrame操作
    
    Args:
        df: pandas DataFrame
        
    Returns:
        优化后的DataFrame
    """
    import pandas as pd
    
    # 优化数据类型
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                # 尝试转换为数值类型
                df[col] = pd.to_numeric(df[col], downcast='integer')
            except (ValueError, TypeError):
                try:
                    # 尝试转换为category类型（对于重复值多的字符串列）
                    if df[col].nunique() / len(df) < 0.1:  # 如果唯一值少于10%
                        df[col] = df[col].astype('category')
                except (ValueError, TypeError):
                    pass
        elif df[col].dtype in ['int64', 'int32']:
            # 降级整数类型
            df[col] = pd.to_numeric(df[col], downcast='integer')
        elif df[col].dtype in ['float64', 'float32']:
            # 降级浮点类型
            df[col] = pd.to_numeric(df[col], downcast='float')
    
    return df


class MemoryOptimizer:
    """内存优化器"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """获取内存使用情况"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # 物理内存
            'vms_mb': memory_info.vms / 1024 / 1024,  # 虚拟内存
            'percent': process.memory_percent()       # 内存使用百分比
        }
    
    @staticmethod
    def log_memory_usage(description: str = "Current"):
        """记录内存使用情况"""
        try:
            memory_usage = MemoryOptimizer.get_memory_usage()
            logger.info(f"{description} memory usage: "
                       f"RSS={memory_usage['rss_mb']:.1f}MB, "
                       f"VMS={memory_usage['vms_mb']:.1f}MB, "
                       f"Percent={memory_usage['percent']:.1f}%")
        except ImportError:
            logger.warning("psutil not available for memory monitoring")
    
    @staticmethod
    def memory_limit_decorator(max_memory_mb: float):
        """
        内存限制装饰器
        
        Args:
            max_memory_mb: 最大内存限制（MB）
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    memory_before = MemoryOptimizer.get_memory_usage()
                    result = func(*args, **kwargs)
                    memory_after = MemoryOptimizer.get_memory_usage()
                    
                    memory_increase = memory_after['rss_mb'] - memory_before['rss_mb']
                    
                    if memory_increase > max_memory_mb:
                        logger.warning(f"Function {func.__name__} exceeded memory limit: "
                                     f"{memory_increase:.1f}MB > {max_memory_mb}MB")
                    
                    return result
                except ImportError:
                    # 如果psutil不可用，直接执行函数
                    return func(*args, **kwargs)
            return wrapper
        return decorator