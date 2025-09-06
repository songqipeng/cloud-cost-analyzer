"""
异步分析器模块
"""
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from .multi_cloud_analyzer import MultiCloudAnalyzer
from ..utils.progress import CloudAnalysisProgress
from ..utils.logger import get_logger

logger = get_logger()


class AsyncMultiCloudAnalyzer(MultiCloudAnalyzer):
    """异步多云分析器"""
    
    def __init__(self, max_concurrent: int = 4, **kwargs):
        super().__init__(**kwargs)
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
    
    async def analyze_multi_cloud_costs_async(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """异步分析多云费用"""
        if not start_date or not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 获取启用的云平台
        enabled_providers = self._get_enabled_providers()
        
        # 创建异步任务
        tasks = []
        for provider in enabled_providers:
            task = self._analyze_provider_async(provider, start_date, end_date)
            tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        return self._process_async_results(results, enabled_providers)
    
    async def _analyze_provider_async(
        self, 
        provider: str, 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """异步分析单个云平台"""
        try:
            # 在线程池中执行同步操作
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._analyze_provider_sync,
                provider,
                start_date,
                end_date
            )
            return result
        except Exception as e:
            logger.error(f"异步分析 {provider} 失败: {e}")
            return {"provider": provider, "error": str(e)}
    
    def _analyze_provider_sync(
        self, 
        provider: str, 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """同步分析单个云平台（在线程池中执行）"""
        try:
            if provider == 'aws':
                return self._analyze_aws_costs(start_date, end_date)
            elif provider == 'aliyun':
                return self._analyze_aliyun_costs(start_date, end_date)
            elif provider == 'tencent':
                return self._analyze_tencent_costs(start_date, end_date)
            elif provider == 'volcengine':
                return self._analyze_volcengine_costs(start_date, end_date)
            else:
                raise ValueError(f"不支持的云平台: {provider}")
        except Exception as e:
            logger.error(f"分析 {provider} 失败: {e}")
            return {"provider": provider, "error": str(e)}
    
    def _get_enabled_providers(self) -> List[str]:
        """获取启用的云平台列表"""
        providers = []
        
        # 检查AWS
        try:
            if self.aws_client.test_connection()[0]:
                providers.append('aws')
        except:
            pass
        
        # 检查阿里云
        try:
            if self.aliyun_client.test_connection()[0]:
                providers.append('aliyun')
        except:
            pass
        
        # 检查腾讯云
        try:
            if self.tencent_client.test_connection()[0]:
                providers.append('tencent')
        except:
            pass
        
        # 检查火山云
        try:
            if self.volcengine_client.test_connection()[0]:
                providers.append('volcengine')
        except:
            pass
        
        return providers
    
    def _process_async_results(
        self, 
        results: List[Any], 
        providers: List[str]
    ) -> Dict[str, Any]:
        """处理异步结果"""
        processed_results = {
            "raw_data": [],
            "service_costs": {},
            "region_costs": {},
            "summary": {},
            "errors": []
        }
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results["errors"].append({
                    "provider": providers[i],
                    "error": str(result)
                })
            elif isinstance(result, dict) and "error" in result:
                processed_results["errors"].append(result)
            else:
                # 合并成功的结果
                if "raw_data" in result:
                    processed_results["raw_data"].extend(result["raw_data"])
                if "service_costs" in result:
                    processed_results["service_costs"].update(result["service_costs"])
                if "region_costs" in result:
                    processed_results["region_costs"].update(result["region_costs"])
        
        return processed_results
    
    async def test_connections_async(self) -> Dict[str, tuple[bool, str]]:
        """异步测试连接"""
        tasks = []
        
        # 创建连接测试任务
        tasks.append(self._test_connection_async('aws', self.aws_client))
        tasks.append(self._test_connection_async('aliyun', self.aliyun_client))
        tasks.append(self._test_connection_async('tencent', self.tencent_client))
        tasks.append(self._test_connection_async('volcengine', self.volcengine_client))
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        connections = {}
        provider_names = ['aws', 'aliyun', 'tencent', 'volcengine']
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                connections[provider_names[i]] = (False, str(result))
            else:
                connections[provider_names[i]] = result
        
        return connections
    
    async def _test_connection_async(
        self, 
        provider: str, 
        client: Any
    ) -> tuple[bool, str]:
        """异步测试单个连接"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                client.test_connection
            )
            return result
        except Exception as e:
            return (False, str(e))
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
