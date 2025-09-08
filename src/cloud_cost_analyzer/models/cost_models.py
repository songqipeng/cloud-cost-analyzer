"""
成本分析数据模型
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator, Field
from enum import Enum


class CloudProvider(str, Enum):
    """云服务提供商枚举"""
    AWS = "aws"
    ALIYUN = "aliyun"
    TENCENT = "tencent"
    VOLCENGINE = "volcengine"


class Currency(str, Enum):
    """货币类型枚举"""
    USD = "USD"
    CNY = "CNY"
    EUR = "EUR"
    JPY = "JPY"


class Granularity(str, Enum):
    """数据粒度枚举"""
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    HOURLY = "HOURLY"


class CostData(BaseModel):
    """成本数据模型"""
    provider: CloudProvider
    date: date
    service: str = Field(..., min_length=1, max_length=100)
    region: str = Field(..., min_length=1, max_length=50)
    cost: float = Field(..., ge=0)
    currency: Currency
    resource_id: Optional[str] = None
    usage_type: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class CostSummary(BaseModel):
    """成本摘要模型"""
    total_cost: float = Field(..., ge=0)
    avg_daily_cost: float = Field(..., ge=0)
    max_daily_cost: float = Field(..., ge=0)
    min_daily_cost: float = Field(..., ge=0)
    record_count: int = Field(..., ge=0)
    date_range: int = Field(..., ge=0)
    currency: Currency
    trend: Optional[str] = None  # "increasing", "decreasing", "stable"


class ServiceCost(BaseModel):
    """服务成本统计模型"""
    service: str = Field(..., min_length=1, max_length=100)
    total_cost: float = Field(..., ge=0)
    avg_cost: float = Field(..., ge=0)
    record_count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0, le=100)


class RegionCost(BaseModel):
    """区域成本统计模型"""
    region: str = Field(..., min_length=1, max_length=50)
    total_cost: float = Field(..., ge=0)
    avg_cost: float = Field(..., ge=0)
    record_count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0, le=100)


class CostAnalysisRequest(BaseModel):
    """成本分析请求模型"""
    providers: List[CloudProvider] = Field(..., min_items=1)
    start_date: date
    end_date: date
    granularity: Granularity = Granularity.MONTHLY
    include_resource_details: bool = False
    enable_optimization_analysis: bool = True
    cost_threshold: float = Field(0.01, ge=0)
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期不能早于开始日期')
        return v
    
    @validator('start_date', 'end_date')
    def validate_not_future(cls, v):
        if v > date.today():
            raise ValueError('日期不能是未来时间')
        return v
    
    @validator('end_date')
    def validate_date_range_limit(cls, v, values):
        if 'start_date' in values:
            days_diff = (v - values['start_date']).days
            if days_diff > 730:  # 2年限制
                raise ValueError('日期范围不能超过2年')
        return v


class OptimizationRecommendation(BaseModel):
    """优化建议模型"""
    type: str = Field(..., min_length=1, max_length=50)
    priority: int = Field(..., ge=0, le=2)  # 0=高, 1=中, 2=低
    description: str = Field(..., min_length=1, max_length=500)
    potential_savings: float = Field(..., ge=0)
    action_required: str = Field(..., min_length=1, max_length=200)
    estimated_effort: str = Field(..., min_length=1, max_length=50)


class CostAnomaly(BaseModel):
    """成本异常模型"""
    date: date
    cost: float = Field(..., ge=0)
    type: str = Field(..., regex="^(high|low)$")
    deviation: float = Field(..., ge=0)
    description: str = Field(..., min_length=1, max_length=200)


class OptimizationReport(BaseModel):
    """优化报告模型"""
    total_potential_savings: float = Field(..., ge=0)
    priority_actions: List[OptimizationRecommendation] = Field(default_factory=list)
    resource_optimizations: List[OptimizationRecommendation] = Field(default_factory=list)
    cost_anomalies: List[CostAnomaly] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)


class CostAnalysisResponse(BaseModel):
    """成本分析响应模型"""
    request_id: str = Field(..., min_length=1, max_length=100)
    providers: List[CloudProvider]
    analysis_period: Dict[str, date]  # {"start": date, "end": date}
    cost_summary: Dict[CloudProvider, CostSummary]
    service_costs: Dict[CloudProvider, List[ServiceCost]]
    region_costs: Dict[CloudProvider, List[RegionCost]]
    optimization_report: Optional[OptimizationReport] = None
    anomalies: List[CostAnomaly] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)
    processing_time: float = Field(..., ge=0)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class CloudProviderConfig(BaseModel):
    """云服务提供商配置模型"""
    provider: CloudProvider
    enabled: bool = True
    region: str = Field(..., min_length=1, max_length=50)
    credentials: Dict[str, str] = Field(default_factory=dict)
    cost_threshold: float = Field(0.01, ge=0)
    custom_settings: Optional[Dict[str, Any]] = None


class AnalysisConfig(BaseModel):
    """分析配置模型"""
    providers: List[CloudProviderConfig] = Field(..., min_items=1)
    default_granularity: Granularity = Granularity.MONTHLY
    default_cost_threshold: float = Field(0.01, ge=0)
    enable_caching: bool = True
    cache_ttl: int = Field(3600, ge=0)  # 缓存生存时间（秒）
    max_concurrent_requests: int = Field(5, ge=1, le=20)
    timeout: int = Field(30, ge=1, le=300)  # 请求超时时间（秒）
