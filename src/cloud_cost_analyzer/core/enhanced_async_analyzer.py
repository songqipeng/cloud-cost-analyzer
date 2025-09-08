"""
增强的异步多云分析器
提供更高效的并发处理、连接池管理、批处理等功能
"""
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import asynccontextmanager
import weakref

from cloud_cost_analyzer.utils.secure_logger import get_secure_logger
from cloud_cost_analyzer.utils.retry import async_retry_with_backoff, CircuitBreaker
from cloud_cost_analyzer.cache.tiered_cache import get_tiered_cache, CacheKeyGenerator
from cloud_cost_analyzer.utils.exceptions import CloudProviderError, AWSConnectionError

logger = get_secure_logger()


class AsyncConnectionPool:
    """异步连接池管理器"""
    
    def __init__(self, max_connections: int = 100, max_connections_per_host: int = 10,
                 timeout: int = 30, keepalive_timeout: int = 60):
        """
        初始化连接池
        
        Args:
            max_connections: 最大连接数
            max_connections_per_host: 每个主机的最大连接数
            timeout: 连接超时时间（秒）
            keepalive_timeout: 连接保持活跃时间（秒）
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=max_connections_per_host,
            keepalive_timeout=keepalive_timeout,
            enable_cleanup_closed=True,
            ttl_dns_cache=300,  # DNS缓存5分钟
            use_dns_cache=True
        )
        self._session: Optional[aiohttp.ClientSession] = None
        self._closed = False
    
    @asynccontextmanager
    async def get_session(self):
        """获取HTTP会话"""
        if self._closed:
            raise RuntimeError("Connection pool is closed")
        
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=self.timeout,
                headers={'User-Agent': 'CloudCostAnalyzer/2.0'}
            )
        
        try:
            yield self._session
        except Exception:
            # 如果出现错误，关闭会话以防止连接泄露
            if self._session and not self._session.closed:
                await self._session.close()
            self._session = None
            raise
    
    async def close(self):
        """关闭连接池"""
        self._closed = True
        if self._session and not self._session.closed:
            await self._session.close()
        await self.connector.close()


class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_concurrent_tasks: int = 10, task_timeout: int = 300):
        """
        初始化任务管理器
        
        Args:
            max_concurrent_tasks: 最大并发任务数
            task_timeout: 任务超时时间（秒）
        """
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.task_timeout = task_timeout
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, Any] = {}
        self.task_errors: Dict[str, Exception] = {}
    
    async def execute_task(self, task_id: str, coro: Callable, 
                          priority: int = 0) -> Any:
        """
        执行异步任务
        
        Args:
            task_id: 任务ID
            coro: 协程函数
            priority: 任务优先级（数字越小优先级越高）
            
        Returns:
            任务执行结果
        """
        async with self.semaphore:
            try:
                logger.debug(f"Starting task {task_id}")
                start_time = time.time()
                
                # 设置任务超时
                task = asyncio.create_task(coro)
                self.active_tasks[task_id] = task
                
                result = await asyncio.wait_for(task, timeout=self.task_timeout)
                
                duration = time.time() - start_time
                logger.debug(f"Task {task_id} completed in {duration:.2f}s")
                
                self.task_results[task_id] = result
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"Task {task_id} timed out after {self.task_timeout}s")
                self.task_errors[task_id] = TimeoutError(f"Task {task_id} timed out")
                raise
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                self.task_errors[task_id] = e
                raise
            finally:
                self.active_tasks.pop(task_id, None)
    
    async def execute_batch(self, tasks: Dict[str, Callable], 
                          return_exceptions: bool = True) -> Dict[str, Any]:
        """
        批量执行任务
        
        Args:
            tasks: 任务字典 {task_id: coroutine}
            return_exceptions: 是否返回异常而非抛出
            
        Returns:
            任务结果字典
        """
        task_coroutines = [
            self.execute_task(task_id, coro) 
            for task_id, coro in tasks.items()
        ]
        
        results = await asyncio.gather(*task_coroutines, return_exceptions=return_exceptions)
        
        return {
            task_id: result 
            for task_id, result in zip(tasks.keys(), results)
        }
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        return {
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.task_results),
            'failed_tasks': len(self.task_errors),
            'max_concurrent': self.semaphore._initial_value,
            'available_slots': self.semaphore._value
        }


class EnhancedAsyncMultiCloudAnalyzer:
    """增强的异步多云分析器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 max_concurrent_providers: int = 4,
                 max_concurrent_per_provider: int = 3,
                 connection_pool_size: int = 50,
                 enable_caching: bool = True,
                 cache_ttl: int = 3600):
        """
        初始化增强异步分析器
        
        Args:
            config: 配置字典
            max_concurrent_providers: 最大并发云服务商数量
            max_concurrent_per_provider: 每个云服务商的最大并发任务数
            connection_pool_size: 连接池大小
            enable_caching: 是否启用缓存
            cache_ttl: 缓存TTL（秒）
        """
        self.config = config or {}
        self.max_concurrent_providers = max_concurrent_providers
        self.max_concurrent_per_provider = max_concurrent_per_provider
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        
        # 初始化组件
        self.connection_pool = AsyncConnectionPool(max_connections=connection_pool_size)
        self.task_manager = AsyncTaskManager(max_concurrent_tasks=max_concurrent_providers)
        
        if enable_caching:
            self.cache = get_tiered_cache(config)
        else:
            self.cache = None
        
        # 熔断器管理
        self.circuit_breakers = {}
        
        # 统计信息
        self.stats = {
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'total_duration': 0.0,
            'provider_durations': {}
        }
        
        self._cleanup_tasks: List[asyncio.Task] = []
    
    def _get_circuit_breaker(self, provider: str) -> CircuitBreaker:
        """获取云服务商的熔断器"""
        if provider not in self.circuit_breakers:
            self.circuit_breakers[provider] = CircuitBreaker(
                failure_threshold=3,
                timeout=60,
                expected_exception=CloudProviderError
            )
        return self.circuit_breakers[provider]
    
    @async_retry_with_backoff(
        max_tries=3,
        base_delay=1.0,
        exceptions=(CloudProviderError, asyncio.TimeoutError, aiohttp.ClientError)
    )
    async def _fetch_provider_data(self, provider: str, start_date: str, 
                                  end_date: str) -> Optional[Dict[str, Any]]:
        """
        异步获取单个云服务商的费用数据
        
        Args:
            provider: 云服务商名称
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            费用数据或None
        """
        # 检查缓存
        if self.cache:
            cache_key = CacheKeyGenerator.generate_cost_data_key(
                provider, start_date, end_date
            )
            cached_data = self.cache.get(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                logger.debug(f"Cache hit for {provider} data")
                return cached_data
            else:
                self.stats['cache_misses'] += 1
        
        start_time = time.time()
        
        try:
            with self._get_circuit_breaker(provider):
                # 根据不同的云服务商调用相应的API
                if provider == 'aws':
                    data = await self._fetch_aws_data(start_date, end_date)
                elif provider == 'aliyun':
                    data = await self._fetch_aliyun_data(start_date, end_date)
                elif provider == 'tencent':
                    data = await self._fetch_tencent_data(start_date, end_date)
                elif provider == 'volcengine':
                    data = await self._fetch_volcengine_data(start_date, end_date)
                else:
                    raise ValueError(f"Unsupported provider: {provider}")
                
                # 缓存数据
                if self.cache and data:
                    cache_key = CacheKeyGenerator.generate_cost_data_key(
                        provider, start_date, end_date
                    )
                    self.cache.set(cache_key, data, ttl=self.cache_ttl)
                
                duration = time.time() - start_time
                self.stats['provider_durations'][provider] = duration
                self.stats['api_calls'] += 1
                
                logger.info(f"Successfully fetched {provider} data in {duration:.2f}s")
                return data
                
        except Exception as e:
            duration = time.time() - start_time
            self.stats['errors'] += 1
            logger.error(f"Failed to fetch {provider} data after {duration:.2f}s: {e}")
            raise CloudProviderError(f"Failed to fetch {provider} data: {e}")
    
    async def _fetch_aws_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取AWS费用数据"""
        # 这里应该实现真正的AWS API调用
        # 为了演示，使用模拟数据
        await asyncio.sleep(0.5)  # 模拟API延迟
        return {
            'provider': 'aws',
            'start_date': start_date,
            'end_date': end_date,
            'total_cost': 123.45,
            'services': ['EC2', 'S3', 'RDS'],
            'timestamp': datetime.now().isoformat()
        }
    
    async def _fetch_aliyun_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取阿里云费用数据"""
        await asyncio.sleep(0.7)  # 模拟API延迟
        return {
            'provider': 'aliyun',
            'start_date': start_date,
            'end_date': end_date,
            'total_cost': 89.67,
            'services': ['ECS', 'OSS', 'RDS'],
            'timestamp': datetime.now().isoformat()
        }
    
    async def _fetch_tencent_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取腾讯云费用数据"""
        await asyncio.sleep(0.6)  # 模拟API延迟
        return {
            'provider': 'tencent',
            'start_date': start_date,
            'end_date': end_date,
            'total_cost': 67.89,
            'services': ['CVM', 'COS', 'TencentDB'],
            'timestamp': datetime.now().isoformat()
        }
    
    async def _fetch_volcengine_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取火山云费用数据"""
        await asyncio.sleep(0.8)  # 模拟API延迟
        return {
            'provider': 'volcengine',
            'start_date': start_date,
            'end_date': end_date,
            'total_cost': 45.23,
            'services': ['ECS', 'TOS', 'VeDB'],
            'timestamp': datetime.now().isoformat()
        }
    
    async def analyze_multi_cloud_async(self, 
                                       providers: Optional[List[str]] = None,
                                       start_date: Optional[str] = None,
                                       end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        异步分析多云费用
        
        Args:
            providers: 要分析的云服务商列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            分析结果字典
        """
        # 设置默认值
        if providers is None:
            providers = ['aws', 'aliyun', 'tencent', 'volcengine']
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Starting async multi-cloud analysis for {len(providers)} providers")
        analysis_start = time.time()
        
        # 创建任务
        tasks = {
            provider: self._fetch_provider_data(provider, start_date, end_date)
            for provider in providers
        }
        
        # 批量执行任务
        results = await self.task_manager.execute_batch(tasks, return_exceptions=True)
        
        # 处理结果
        successful_results = {}
        failed_providers = []
        
        for provider, result in results.items():
            if isinstance(result, Exception):
                logger.error(f"Provider {provider} failed: {result}")
                failed_providers.append(provider)
            else:
                successful_results[provider] = result
        
        # 计算总计
        total_cost = sum(
            data.get('total_cost', 0) 
            for data in successful_results.values()
            if isinstance(data, dict)
        )
        
        analysis_duration = time.time() - analysis_start
        self.stats['total_duration'] = analysis_duration
        
        # 构建分析结果
        analysis_result = {
            'analysis_id': f"async_analysis_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'providers': {
                'requested': providers,
                'successful': list(successful_results.keys()),
                'failed': failed_providers
            },
            'summary': {
                'total_cost': total_cost,
                'provider_count': len(successful_results),
                'analysis_duration': analysis_duration,
                'cache_hit_rate': self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses']) if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 else 0
            },
            'provider_data': successful_results,
            'performance_stats': self.get_performance_stats()
        }
        
        logger.info(f"Multi-cloud analysis completed in {analysis_duration:.2f}s")
        return analysis_result
    
    async def test_all_connections_async(self) -> Dict[str, Tuple[bool, str]]:
        """异步测试所有云服务商连接"""
        providers = ['aws', 'aliyun', 'tencent', 'volcengine']
        
        tasks = {
            provider: self._test_provider_connection(provider)
            for provider in providers
        }
        
        results = await self.task_manager.execute_batch(tasks, return_exceptions=True)
        
        connection_results = {}
        for provider, result in results.items():
            if isinstance(result, Exception):
                connection_results[provider] = (False, str(result))
            else:
                connection_results[provider] = result
        
        return connection_results
    
    async def _test_provider_connection(self, provider: str) -> Tuple[bool, str]:
        """测试单个云服务商连接"""
        try:
            # 这里应该实现真正的连接测试
            await asyncio.sleep(0.2)  # 模拟连接测试延迟
            return (True, f"{provider} connection successful")
        except Exception as e:
            return (False, f"{provider} connection failed: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        task_stats = self.task_manager.get_task_statistics()
        
        return {
            'api_calls': self.stats['api_calls'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'errors': self.stats['errors'],
            'total_duration': self.stats['total_duration'],
            'provider_durations': self.stats['provider_durations'],
            'task_manager': task_stats,
            'circuit_breakers': {
                provider: cb.state 
                for provider, cb in self.circuit_breakers.items()
            }
        }
    
    async def cleanup(self):
        """清理资源"""
        logger.info("Cleaning up async analyzer resources...")
        
        # 等待所有清理任务完成
        if self._cleanup_tasks:
            await asyncio.gather(*self._cleanup_tasks, return_exceptions=True)
        
        # 关闭连接池
        await self.connection_pool.close()
        
        # 清理缓存
        if self.cache:
            # 异步清理过期缓存
            try:
                self.cache.cleanup_expired()
            except Exception as e:
                logger.warning(f"Cache cleanup error: {e}")
        
        logger.info("Async analyzer cleanup completed")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()


# 便捷函数
async def analyze_multi_cloud_async(providers: Optional[List[str]] = None,
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None,
                                   config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    便捷的异步多云分析函数
    
    Args:
        providers: 要分析的云服务商列表
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        config: 配置字典
        
    Returns:
        分析结果字典
    """
    async with EnhancedAsyncMultiCloudAnalyzer(config=config) as analyzer:
        return await analyzer.analyze_multi_cloud_async(
            providers=providers,
            start_date=start_date,
            end_date=end_date
        )


# 批处理分析
async def batch_analyze_async(analysis_requests: List[Dict[str, Any]],
                             config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    批量异步分析
    
    Args:
        analysis_requests: 分析请求列表
        config: 配置字典
        
    Returns:
        分析结果列表
    """
    async with EnhancedAsyncMultiCloudAnalyzer(config=config) as analyzer:
        tasks = []
        
        for i, request in enumerate(analysis_requests):
            task = analyzer.analyze_multi_cloud_async(
                providers=request.get('providers'),
                start_date=request.get('start_date'),
                end_date=request.get('end_date')
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'error': True,
                    'message': str(result),
                    'request_index': i
                })
            else:
                processed_results.append(result)
        
        return processed_results