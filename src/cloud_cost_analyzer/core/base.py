"""
基础抽象类和接口定义
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date
import asyncio
from dataclasses import dataclass

from ..models.cost_models import (
    CloudProvider, CostData, CostAnalysisRequest, 
    CostAnalysisResponse, CostSummary, ServiceCost, RegionCost
)
from ..utils.security import SecurityManager
from ..utils.logger import get_logger

logger = get_logger()


@dataclass
class ProviderConfig:
    """云服务提供商配置"""
    provider: CloudProvider
    enabled: bool = True
    region: str = "us-east-1"
    credentials: Dict[str, str] = None
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        if self.credentials is None:
            self.credentials = {}


class CloudProviderClient(ABC):
    """云服务提供商客户端抽象基类"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.security_manager = SecurityManager()
        self.logger = logger
    
    @abstractmethod
    async def test_connection(self) -> Tuple[bool, str]:
        """测试连接"""
        pass
    
    @abstractmethod
    async def get_cost_data(self, start_date: str, end_date: str, 
                          granularity: str = 'MONTHLY') -> Optional[Dict[str, Any]]:
        """获取费用数据"""
        pass
    
    @abstractmethod
    async def get_resource_details(self, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """获取资源详细信息"""
        pass
    
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        return self.config.provider.value
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.config.enabled


class DataProcessor(ABC):
    """数据处理器抽象基类"""
    
    def __init__(self, cost_threshold: float = 0.01):
        self.cost_threshold = cost_threshold
        self.security_manager = SecurityManager()
        self.logger = logger
    
    @abstractmethod
    def parse_cost_data(self, raw_data: Dict[str, Any]) -> List[CostData]:
        """解析原始费用数据"""
        pass
    
    @abstractmethod
    def analyze_costs_by_service(self, cost_data: List[CostData]) -> List[ServiceCost]:
        """按服务分析费用"""
        pass
    
    @abstractmethod
    def analyze_costs_by_region(self, cost_data: List[CostData]) -> List[RegionCost]:
        """按区域分析费用"""
        pass
    
    @abstractmethod
    def get_cost_summary(self, cost_data: List[CostData]) -> CostSummary:
        """获取费用摘要"""
        pass
    
    def filter_by_threshold(self, cost_data: List[CostData]) -> List[CostData]:
        """按阈值过滤费用数据"""
        return [data for data in cost_data if data.cost >= self.cost_threshold]


class CostAnalyzer(ABC):
    """成本分析器抽象基类"""
    
    def __init__(self, client: CloudProviderClient, processor: DataProcessor):
        self.client = client
        self.processor = processor
        self.security_manager = SecurityManager()
        self.logger = logger
    
    @abstractmethod
    async def analyze_costs(self, request: CostAnalysisRequest) -> CostAnalysisResponse:
        """分析费用"""
        pass
    
    @abstractmethod
    async def detect_anomalies(self, cost_data: List[CostData]) -> List[Dict[str, Any]]:
        """检测费用异常"""
        pass
    
    @abstractmethod
    async def generate_optimization_recommendations(self, cost_data: List[CostData]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        pass


class ReportGenerator(ABC):
    """报告生成器抽象基类"""
    
    def __init__(self):
        self.security_manager = SecurityManager()
        self.logger = logger
    
    @abstractmethod
    async def generate_text_report(self, response: CostAnalysisResponse, output_path: str) -> bool:
        """生成文本报告"""
        pass
    
    @abstractmethod
    async def generate_html_report(self, response: CostAnalysisResponse, output_path: str) -> bool:
        """生成HTML报告"""
        pass
    
    @abstractmethod
    async def generate_json_report(self, response: CostAnalysisResponse, output_path: str) -> bool:
        """生成JSON报告"""
        pass


class NotificationService(ABC):
    """通知服务抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.security_manager = SecurityManager()
        self.logger = logger
    
    @abstractmethod
    async def send_notification(self, message: str, subject: str = "") -> bool:
        """发送通知"""
        pass
    
    @abstractmethod
    async def send_cost_report(self, response: CostAnalysisResponse) -> bool:
        """发送费用报告"""
        pass


class CloudProviderFactory:
    """云服务提供商工厂类"""
    
    _clients = {}
    _processors = {}
    _analyzers = {}
    
    @classmethod
    def register_client(cls, provider: CloudProvider, client_class):
        """注册客户端类"""
        cls._clients[provider] = client_class
    
    @classmethod
    def register_processor(cls, provider: CloudProvider, processor_class):
        """注册数据处理器类"""
        cls._processors[provider] = processor_class
    
    @classmethod
    def register_analyzer(cls, provider: CloudProvider, analyzer_class):
        """注册分析器类"""
        cls._analyzers[provider] = analyzer_class
    
    @classmethod
    def create_client(cls, provider: CloudProvider, config: ProviderConfig) -> CloudProviderClient:
        """创建客户端实例"""
        if provider not in cls._clients:
            raise ValueError(f"未注册的云服务提供商: {provider}")
        
        client_class = cls._clients[provider]
        return client_class(config)
    
    @classmethod
    def create_processor(cls, provider: CloudProvider, cost_threshold: float = 0.01) -> DataProcessor:
        """创建数据处理器实例"""
        if provider not in cls._processors:
            raise ValueError(f"未注册的数据处理器: {provider}")
        
        processor_class = cls._processors[provider]
        return processor_class(cost_threshold)
    
    @classmethod
    def create_analyzer(cls, provider: CloudProvider, config: ProviderConfig, 
                       cost_threshold: float = 0.01) -> CostAnalyzer:
        """创建分析器实例"""
        if provider not in cls._analyzers:
            raise ValueError(f"未注册的分析器: {provider}")
        
        client = cls.create_client(provider, config)
        processor = cls.create_processor(provider, cost_threshold)
        
        analyzer_class = cls._analyzers[provider]
        return analyzer_class(client, processor)
    
    @classmethod
    def get_supported_providers(cls) -> List[CloudProvider]:
        """获取支持的云服务提供商列表"""
        return list(cls._clients.keys())


class MultiCloudAnalyzer:
    """多云分析器"""
    
    def __init__(self, configs: List[ProviderConfig]):
        self.configs = configs
        self.analyzers = {}
        self.security_manager = SecurityManager()
        self.logger = logger
        
        # 创建各提供商的分析器
        for config in configs:
            if config.enabled:
                try:
                    analyzer = CloudProviderFactory.create_analyzer(config.provider, config)
                    self.analyzers[config.provider] = analyzer
                except Exception as e:
                    self.logger.error(f"创建 {config.provider} 分析器失败: {e}")
    
    async def test_all_connections(self) -> Dict[CloudProvider, Tuple[bool, str]]:
        """测试所有云服务连接"""
        tasks = []
        providers = []
        
        for provider, analyzer in self.analyzers.items():
            tasks.append(analyzer.client.test_connection())
            providers.append(provider)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        connection_results = {}
        for provider, result in zip(providers, results):
            if isinstance(result, Exception):
                connection_results[provider] = (False, str(result))
            else:
                connection_results[provider] = result
        
        return connection_results
    
    async def analyze_multi_cloud_costs(self, request: CostAnalysisRequest) -> CostAnalysisResponse:
        """分析多云费用"""
        start_time = datetime.now()
        
        # 过滤启用的提供商
        enabled_providers = [p for p in request.providers if p in self.analyzers]
        
        if not enabled_providers:
            raise ValueError("没有可用的云服务提供商")
        
        # 并发分析各提供商
        tasks = []
        for provider in enabled_providers:
            analyzer = self.analyzers[provider]
            # 创建单个提供商的请求
            single_provider_request = CostAnalysisRequest(
                providers=[provider],
                start_date=request.start_date,
                end_date=request.end_date,
                granularity=request.granularity,
                include_resource_details=request.include_resource_details,
                enable_optimization_analysis=request.enable_optimization_analysis,
                cost_threshold=request.cost_threshold
            )
            tasks.append(analyzer.analyze_costs(single_provider_request))
        
        # 等待所有分析完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        combined_response = self._combine_analysis_results(results, enabled_providers, request)
        
        # 计算处理时间
        processing_time = (datetime.now() - start_time).total_seconds()
        combined_response.processing_time = processing_time
        
        return combined_response
    
    def _combine_analysis_results(self, results: List[Any], providers: List[CloudProvider], 
                                 request: CostAnalysisRequest) -> CostAnalysisResponse:
        """合并分析结果"""
        # 这里应该实现结果合并逻辑
        # 由于篇幅限制，这里提供简化实现
        
        cost_summary = {}
        service_costs = {}
        region_costs = {}
        all_anomalies = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"提供商 {providers[i]} 分析失败: {result}")
                continue
            
            provider = providers[i]
            cost_summary[provider] = result.cost_summary.get(provider, {})
            service_costs[provider] = result.service_costs.get(provider, [])
            region_costs[provider] = result.region_costs.get(provider, [])
            all_anomalies.extend(result.anomalies)
        
        return CostAnalysisResponse(
            request_id=f"multi_cloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            providers=providers,
            analysis_period={"start": request.start_date, "end": request.end_date},
            cost_summary=cost_summary,
            service_costs=service_costs,
            region_costs=region_costs,
            anomalies=all_anomalies,
            processing_time=0.0  # 将在调用处设置
        )