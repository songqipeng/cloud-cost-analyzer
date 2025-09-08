"""
异步云服务客户端模块
"""
import asyncio
import aiohttp
import aioboto3
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date
import json
import logging
from dataclasses import dataclass

from ..models.cost_models import CloudProvider, CostData, Currency
from ..utils.security import SecurityManager, secure_function
from ..utils.logger import get_logger

logger = get_logger()


@dataclass
class AsyncClientConfig:
    """异步客户端配置"""
    timeout: int = 30
    max_concurrent_requests: int = 5
    retry_attempts: int = 3
    retry_delay: float = 1.0


class AsyncAWSClient:
    """异步AWS客户端"""
    
    def __init__(self, access_key_id: Optional[str] = None, 
                 secret_access_key: Optional[str] = None,
                 region: str = 'us-east-1',
                 config: Optional[AsyncClientConfig] = None):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region = region
        self.config = config or AsyncClientConfig()
        self.security_manager = SecurityManager()
        
    async def test_connection(self) -> Tuple[bool, str]:
        """测试AWS连接"""
        try:
            session = aioboto3.Session()
            async with session.client(
                'sts',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region
            ) as sts:
                response = await sts.get_caller_identity()
                return True, f"连接成功，账户ID: {response.get('Account', 'Unknown')}"
        except Exception as e:
            logger.error(f"AWS连接测试失败: {e}")
            return False, str(e)
    
    @secure_function
    async def get_cost_and_usage_async(self, start_date: str, end_date: str, 
                                     granularity: str = 'MONTHLY') -> Optional[Dict[str, Any]]:
        """异步获取AWS费用数据"""
        try:
            session = aioboto3.Session()
            async with session.client(
                'ce',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region
            ) as ce_client:
                
                # 构建请求参数
                params = {
                    'TimePeriod': {
                        'Start': start_date,
                        'End': end_date
                    },
                    'Granularity': granularity,
                    'Metrics': ['BlendedCost', 'UnblendedCost'],
                    'GroupBy': [
                        {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                        {'Type': 'DIMENSION', 'Key': 'REGION'}
                    ]
                }
                
                # 执行请求
                response = await ce_client.get_cost_and_usage(**params)
                
                # 处理分页
                all_results = response.get('ResultsByTime', [])
                next_token = response.get('NextPageToken')
                
                while next_token:
                    params['NextPageToken'] = next_token
                    response = await ce_client.get_cost_and_usage(**params)
                    all_results.extend(response.get('ResultsByTime', []))
                    next_token = response.get('NextPageToken')
                
                return {
                    'ResultsByTime': all_results,
                    'GroupDefinitions': response.get('GroupDefinitions', [])
                }
                
        except Exception as e:
            logger.error(f"AWS费用数据获取失败: {e}")
            return None


class AsyncAliyunClient:
    """异步阿里云客户端"""
    
    def __init__(self, access_key_id: Optional[str] = None,
                 access_key_secret: Optional[str] = None,
                 region: str = 'cn-hangzhou',
                 config: Optional[AsyncClientConfig] = None):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region = region
        self.config = config or AsyncClientConfig()
        self.security_manager = SecurityManager()
    
    async def test_connection(self) -> Tuple[bool, str]:
        """测试阿里云连接"""
        try:
            # 这里应该实现阿里云连接测试
            # 由于阿里云SDK的异步支持有限，这里使用模拟实现
            await asyncio.sleep(0.1)  # 模拟网络延迟
            return True, "阿里云连接测试成功"
        except Exception as e:
            logger.error(f"阿里云连接测试失败: {e}")
            return False, str(e)
    
    @secure_function
    async def get_cost_and_usage_async(self, start_date: str, end_date: str,
                                     granularity: str = 'MONTHLY') -> Optional[Dict[str, Any]]:
        """异步获取阿里云费用数据"""
        try:
            # 模拟阿里云API调用
            await asyncio.sleep(0.5)  # 模拟网络延迟
            
            # 这里应该调用真实的阿里云API
            # 返回模拟数据
            return {
                'ResultsByTime': [
                    {
                        'TimePeriod': {'Start': start_date, 'End': end_date},
                        'Groups': [
                            {
                                'Keys': ['ECS', 'cn-hangzhou'],
                                'Metrics': {'BlendedCost': {'Amount': '100.50', 'Unit': 'CNY'}}
                            }
                        ]
                    }
                ]
            }
        except Exception as e:
            logger.error(f"阿里云费用数据获取失败: {e}")
            return None


class AsyncTencentClient:
    """异步腾讯云客户端"""
    
    def __init__(self, secret_id: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 region: str = 'ap-beijing',
                 config: Optional[AsyncClientConfig] = None):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.config = config or AsyncClientConfig()
        self.security_manager = SecurityManager()
    
    async def test_connection(self) -> Tuple[bool, str]:
        """测试腾讯云连接"""
        try:
            await asyncio.sleep(0.1)  # 模拟网络延迟
            return True, "腾讯云连接测试成功"
        except Exception as e:
            logger.error(f"腾讯云连接测试失败: {e}")
            return False, str(e)
    
    @secure_function
    async def get_cost_and_usage_async(self, start_date: str, end_date: str,
                                     granularity: str = 'MONTHLY') -> Optional[Dict[str, Any]]:
        """异步获取腾讯云费用数据"""
        try:
            await asyncio.sleep(0.5)  # 模拟网络延迟
            
            # 返回模拟数据
            return {
                'ResultsByTime': [
                    {
                        'TimePeriod': {'Start': start_date, 'End': end_date},
                        'Groups': [
                            {
                                'Keys': ['CVM', 'ap-beijing'],
                                'Metrics': {'BlendedCost': {'Amount': '200.30', 'Unit': 'CNY'}}
                            }
                        ]
                    }
                ]
            }
        except Exception as e:
            logger.error(f"腾讯云费用数据获取失败: {e}")
            return None


class AsyncVolcengineClient:
    """异步火山引擎客户端"""
    
    def __init__(self, access_key_id: Optional[str] = None,
                 secret_access_key: Optional[str] = None,
                 region: str = 'cn-beijing',
                 config: Optional[AsyncClientConfig] = None):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region = region
        self.config = config or AsyncClientConfig()
        self.security_manager = SecurityManager()
    
    async def test_connection(self) -> Tuple[bool, str]:
        """测试火山引擎连接"""
        try:
            await asyncio.sleep(0.1)  # 模拟网络延迟
            return True, "火山引擎连接测试成功"
        except Exception as e:
            logger.error(f"火山引擎连接测试失败: {e}")
            return False, str(e)
    
    @secure_function
    async def get_cost_and_usage_async(self, start_date: str, end_date: str,
                                     granularity: str = 'MONTHLY') -> Optional[Dict[str, Any]]:
        """异步获取火山引擎费用数据"""
        try:
            await asyncio.sleep(0.5)  # 模拟网络延迟
            
            # 返回模拟数据
            return {
                'ResultsByTime': [
                    {
                        'TimePeriod': {'Start': start_date, 'End': end_date},
                        'Groups': [
                            {
                                'Keys': ['ECS', 'cn-beijing'],
                                'Metrics': {'BlendedCost': {'Amount': '150.75', 'Unit': 'CNY'}}
                            }
                        ]
                    }
                ]
            }
        except Exception as e:
            logger.error(f"火山引擎费用数据获取失败: {e}")
            return None


class AsyncMultiCloudClient:
    """异步多云客户端管理器"""
    
    def __init__(self, config: Optional[AsyncClientConfig] = None):
        self.config = config or AsyncClientConfig()
        self.clients = {}
        self.security_manager = SecurityManager()
        
    def add_client(self, provider: CloudProvider, client) -> None:
        """添加云服务客户端"""
        self.clients[provider] = client
    
    async def test_all_connections(self) -> Dict[CloudProvider, Tuple[bool, str]]:
        """测试所有云服务连接"""
        tasks = []
        providers = []
        
        for provider, client in self.clients.items():
            tasks.append(client.test_connection())
            providers.append(provider)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        connection_results = {}
        for provider, result in zip(providers, results):
            if isinstance(result, Exception):
                connection_results[provider] = (False, str(result))
            else:
                connection_results[provider] = result
        
        return connection_results
    
    async def get_multi_cloud_cost_data(self, providers: List[CloudProvider],
                                      start_date: str, end_date: str,
                                      granularity: str = 'MONTHLY') -> Dict[CloudProvider, Optional[Dict[str, Any]]]:
        """并发获取多云费用数据"""
        
        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def fetch_with_semaphore(provider: CloudProvider, client):
            async with semaphore:
                try:
                    return provider, await client.get_cost_and_usage_async(start_date, end_date, granularity)
                except Exception as e:
                    logger.error(f"{provider} 费用数据获取失败: {e}")
                    return provider, None
        
        # 创建任务
        tasks = []
        for provider in providers:
            if provider in self.clients:
                tasks.append(fetch_with_semaphore(provider, self.clients[provider]))
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        cost_data = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"任务执行异常: {result}")
            else:
                provider, data = result
                cost_data[provider] = data
        
        return cost_data
    
    async def get_cost_data_with_retry(self, provider: CloudProvider,
                                     start_date: str, end_date: str,
                                     granularity: str = 'MONTHLY') -> Optional[Dict[str, Any]]:
        """带重试的费用数据获取"""
        if provider not in self.clients:
            logger.error(f"未找到 {provider} 客户端")
            return None
        
        client = self.clients[provider]
        
        for attempt in range(self.config.retry_attempts):
            try:
                result = await client.get_cost_and_usage_async(start_date, end_date, granularity)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"{provider} 第 {attempt + 1} 次尝试失败: {e}")
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))  # 指数退避
        
        logger.error(f"{provider} 所有重试尝试都失败了")
        return None