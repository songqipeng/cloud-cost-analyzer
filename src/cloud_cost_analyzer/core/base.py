"""
基础接口和抽象类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from datetime import date
import pandas as pd


class CloudProviderClient(ABC):
    """云服务提供商客户端基础接口"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化客户端"""
        self.config = config or {}
        self.provider_name = self._get_provider_name()
        self.region = self._get_default_region()
        
    @abstractmethod
    def _get_provider_name(self) -> str:
        """获取云服务提供商名称"""
        pass
    
    @abstractmethod
    def _get_default_region(self) -> str:
        """获取默认区域"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接"""
        pass
    
    @abstractmethod
    def get_cost_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """获取费用数据"""
        pass
    
    @abstractmethod
    def process_cost_data(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """处理费用数据"""
        pass
    
    def analyze(self, start_date: Optional[date] = None, 
                end_date: Optional[date] = None) -> Dict[str, Any]:
        """分析费用数据"""
        # 默认实现：获取数据 -> 处理数据 -> 分析结果
        raw_data = self.get_cost_data(start_date, end_date)
        processed_data = self.process_cost_data(raw_data)
        return self._analyze_processed_data(processed_data)
    
    def _analyze_processed_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析处理后的数据"""
        if df.empty:
            return {
                'summary': {
                    'total_cost': 0.0,
                    'currency': 'USD',
                    'days': 0,
                    'average_daily_cost': 0.0
                },
                'by_service': pd.DataFrame(),
                'by_region': pd.DataFrame()
            }
        
        # 计算摘要信息
        total_cost = df['Cost'].sum()
        currency = df['Currency'].iloc[0] if 'Currency' in df.columns else 'USD'
        unique_dates = df['Date'].nunique() if 'Date' in df.columns else 1
        avg_daily = total_cost / max(unique_dates, 1)
        
        # 按服务分组
        by_service = df.groupby('Service').agg({
            'Cost': ['sum', 'mean', 'count']
        }).round(2)
        by_service.columns = ['Cost', 'AvgCost', 'Count']
        by_service = by_service.sort_values('Cost', ascending=False).reset_index()
        
        # 按区域分组（如果有区域信息）
        by_region = pd.DataFrame()
        if 'Region' in df.columns:
            by_region = df.groupby('Region').agg({
                'Cost': ['sum', 'count']
            }).round(2)
            by_region.columns = ['Cost', 'Count']
            by_region = by_region.sort_values('Cost', ascending=False).reset_index()
        
        return {
            'summary': {
                'total_cost': round(total_cost, 2),
                'currency': currency,
                'days': unique_dates,
                'average_daily_cost': round(avg_daily, 2)
            },
            'by_service': by_service,
            'by_region': by_region
        }
    
    def _format_service_name(self, service_name: str) -> str:
        """格式化服务名称（子类可重写）"""
        return service_name
    
    def _format_region_name(self, region_name: str) -> str:
        """格式化区域名称（子类可重写）"""
        return region_name


class CostAnalyzer(ABC):
    """费用分析器基础接口"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化分析器"""
        self.config = config or {}
        
    @abstractmethod
    def analyze(self, start_date: Optional[date] = None, 
                end_date: Optional[date] = None, **kwargs) -> Dict[str, Any]:
        """执行费用分析"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接状态"""
        pass
    
    def _validate_date_range(self, start_date: date, end_date: date) -> None:
        """验证日期范围"""
        from cloud_cost_analyzer.utils.validators import DataValidator
        DataValidator.validate_date_range(start_date, end_date)
    
    def _filter_by_threshold(self, df: pd.DataFrame, cost_column: str) -> pd.DataFrame:
        """按费用阈值过滤数据"""
        threshold = self.config.get('cost_threshold', 0.01)
        if threshold > 0:
            return df[df[cost_column] >= threshold]
        return df


class NotificationProvider(ABC):
    """通知提供商基础接口"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化通知提供商"""
        self.config = config
        self.enabled = config.get('enabled', False)
        
    @abstractmethod
    def send_notification(self, title: str, content: str, 
                         attachments: Optional[List[str]] = None) -> bool:
        """发送通知"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接"""
        pass
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.enabled


class ReportGenerator(ABC):
    """报告生成器基础接口"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化报告生成器"""
        self.config = config
        
    @abstractmethod
    def generate_console_report(self, data: Dict[str, Any]) -> None:
        """生成控制台报告"""
        pass
    
    @abstractmethod
    def generate_file_report(self, data: Dict[str, Any], 
                           output_path: str, format_type: str) -> str:
        """生成文件报告"""
        pass


class CacheProvider(ABC):
    """缓存提供商基础接口"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """清空缓存"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass


class ConfigurationManager(ABC):
    """配置管理器基础接口"""
    
    @abstractmethod
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置"""
        pass
    
    @abstractmethod
    def save_config(self, config: Dict[str, Any], 
                   config_path: Optional[str] = None) -> bool:
        """保存配置"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证配置"""
        pass
    
    @abstractmethod
    def merge_config(self, base_config: Dict[str, Any], 
                    override_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        pass