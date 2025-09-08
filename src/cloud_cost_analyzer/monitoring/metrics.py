"""
监控指标收集模块
"""
import time
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import logging
from pathlib import Path

try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    prometheus_client = None

from ..utils.logger import get_logger
from ..models.cost_models import CloudProvider

logger = get_logger()


@dataclass
class MetricPoint:
    """指标数据点"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """健康状态"""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    last_check: datetime
    details: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, enable_prometheus: bool = True, metrics_file: str = "metrics.json"):
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.metrics_file = Path(metrics_file)
        self.metrics_data = defaultdict(list)
        self.start_time = datetime.now()
        
        # 初始化Prometheus指标
        if self.enable_prometheus:
            self._init_prometheus_metrics()
        
        # 自定义指标
        self._init_custom_metrics()
    
    def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        self.registry = CollectorRegistry()
        
        # 请求指标
        self.cost_analysis_requests = Counter(
            'cost_analysis_requests_total',
            'Total cost analysis requests',
            ['provider', 'status'],
            registry=self.registry
        )
        
        self.analysis_duration = Histogram(
            'cost_analysis_duration_seconds',
            'Cost analysis duration in seconds',
            ['provider'],
            registry=self.registry
        )
        
        # 连接指标
        self.active_connections = Gauge(
            'active_cloud_connections',
            'Active cloud provider connections',
            ['provider'],
            registry=self.registry
        )
        
        self.connection_errors = Counter(
            'cloud_connection_errors_total',
            'Total cloud connection errors',
            ['provider', 'error_type'],
            registry=self.registry
        )
        
        # 缓存指标
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_level'],
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_level'],
            registry=self.registry
        )
        
        # 成本指标
        self.total_cost_analyzed = Counter(
            'total_cost_analyzed',
            'Total cost analyzed',
            ['provider', 'currency'],
            registry=self.registry
        )
        
        # 系统信息
        self.system_info = Info(
            'system_info',
            'System information',
            registry=self.registry
        )
        
        self.system_info.info({
            'version': '2.0.0',
            'start_time': self.start_time.isoformat()
        })
    
    def _init_custom_metrics(self):
        """初始化自定义指标"""
        self.custom_metrics = {
            'request_count': 0,
            'error_count': 0,
            'total_processing_time': 0.0,
            'provider_stats': defaultdict(lambda: {
                'requests': 0,
                'errors': 0,
                'total_cost': 0.0,
                'last_success': None,
                'last_error': None
            })
        }
    
    def record_analysis_request(self, provider: CloudProvider, duration: float, 
                              status: str = "success", cost: float = 0.0, 
                              currency: str = "USD"):
        """记录分析请求"""
        timestamp = datetime.now()
        
        # 更新自定义指标
        self.custom_metrics['request_count'] += 1
        self.custom_metrics['total_processing_time'] += duration
        
        provider_stats = self.custom_metrics['provider_stats'][provider.value]
        provider_stats['requests'] += 1
        provider_stats['total_cost'] += cost
        
        if status == "success":
            provider_stats['last_success'] = timestamp
        else:
            provider_stats['last_error'] = timestamp
            self.custom_metrics['error_count'] += 1
        
        # 更新Prometheus指标
        if self.enable_prometheus:
            self.cost_analysis_requests.labels(
                provider=provider.value, 
                status=status
            ).inc()
            
            self.analysis_duration.labels(provider=provider.value).observe(duration)
            
            if cost > 0:
                self.total_cost_analyzed.labels(
                    provider=provider.value,
                    currency=currency
                ).inc(cost)
        
        # 记录到时间序列数据
        self._record_metric_point('analysis_duration', duration, {
            'provider': provider.value,
            'status': status
        })
    
    def record_connection_status(self, provider: CloudProvider, status: str, 
                               error_type: Optional[str] = None):
        """记录连接状态"""
        if self.enable_prometheus:
            if status == "success":
                self.active_connections.labels(provider=provider.value).set(1)
            else:
                self.active_connections.labels(provider=provider.value).set(0)
                if error_type:
                    self.connection_errors.labels(
                        provider=provider.value,
                        error_type=error_type
                    ).inc()
    
    def record_cache_event(self, cache_level: str, hit: bool):
        """记录缓存事件"""
        if self.enable_prometheus:
            if hit:
                self.cache_hits.labels(cache_level=cache_level).inc()
            else:
                self.cache_misses.labels(cache_level=cache_level).inc()
    
    def _record_metric_point(self, metric_name: str, value: float, labels: Dict[str, str]):
        """记录指标数据点"""
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            labels=labels
        )
        self.metrics_data[metric_name].append(point)
        
        # 保持最近1000个数据点
        if len(self.metrics_data[metric_name]) > 1000:
            self.metrics_data[metric_name] = self.metrics_data[metric_name][-1000:]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            'uptime_seconds': uptime,
            'uptime_human': str(timedelta(seconds=int(uptime))),
            'request_count': self.custom_metrics['request_count'],
            'error_count': self.custom_metrics['error_count'],
            'error_rate': (
                self.custom_metrics['error_count'] / max(self.custom_metrics['request_count'], 1)
            ) * 100,
            'avg_processing_time': (
                self.custom_metrics['total_processing_time'] / 
                max(self.custom_metrics['request_count'], 1)
            ),
            'provider_stats': dict(self.custom_metrics['provider_stats']),
            'prometheus_enabled': self.enable_prometheus
        }
        
        return summary
    
    def get_metrics_data(self, metric_name: str, 
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> List[MetricPoint]:
        """获取指标数据"""
        if metric_name not in self.metrics_data:
            return []
        
        data = self.metrics_data[metric_name]
        
        if start_time:
            data = [point for point in data if point.timestamp >= start_time]
        
        if end_time:
            data = [point for point in data if point.timestamp <= end_time]
        
        return data
    
    def export_metrics(self, output_file: Optional[str] = None) -> str:
        """导出指标数据"""
        if output_file:
            output_path = Path(output_file)
        else:
            output_path = self.metrics_file
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'summary': self.get_metrics_summary(),
            'metrics_data': {
                name: [
                    {
                        'timestamp': point.timestamp.isoformat(),
                        'value': point.value,
                        'labels': point.labels
                    }
                    for point in points
                ]
                for name, points in self.metrics_data.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"指标数据已导出到: {output_path}")
        return str(output_path)
    
    def get_prometheus_metrics(self) -> str:
        """获取Prometheus格式的指标"""
        if not self.enable_prometheus:
            return "# Prometheus metrics not available"
        
        from prometheus_client import generate_latest
        return generate_latest(self.registry).decode('utf-8')


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics_collector = metrics_collector
        self.health_checks = {}
        self.last_checks = {}
        self.logger = logger
    
    def register_health_check(self, name: str, check_func: Callable[[], bool], 
                            interval: int = 60):
        """注册健康检查"""
        self.health_checks[name] = {
            'function': check_func,
            'interval': interval,
            'last_check': None,
            'last_status': None
        }
    
    async def check_all(self) -> Dict[str, HealthStatus]:
        """执行所有健康检查"""
        results = {}
        
        for name, check_info in self.health_checks.items():
            try:
                # 检查是否需要执行
                now = datetime.now()
                last_check = check_info['last_check']
                
                if last_check and (now - last_check).seconds < check_info['interval']:
                    # 使用上次结果
                    if check_info['last_status']:
                        results[name] = check_info['last_status']
                    continue
                
                # 执行健康检查
                is_healthy = await self._run_health_check(check_info['function'])
                
                status = "healthy" if is_healthy else "unhealthy"
                message = f"{name} 健康检查 {'通过' if is_healthy else '失败'}"
                
                health_status = HealthStatus(
                    component=name,
                    status=status,
                    message=message,
                    last_check=now
                )
                
                # 更新缓存
                check_info['last_check'] = now
                check_info['last_status'] = health_status
                
                results[name] = health_status
                
            except Exception as e:
                health_status = HealthStatus(
                    component=name,
                    status="unhealthy",
                    message=f"健康检查异常: {str(e)}",
                    last_check=datetime.now()
                )
                results[name] = health_status
                self.logger.error(f"健康检查 {name} 失败: {e}")
        
        return results
    
    async def _run_health_check(self, check_func: Callable[[], bool]) -> bool:
        """运行健康检查函数"""
        if asyncio.iscoroutinefunction(check_func):
            return await check_func()
        else:
            return check_func()
    
    async def check_cloud_connections(self, providers: List[CloudProvider]) -> Dict[str, HealthStatus]:
        """检查云服务连接"""
        results = {}
        
        for provider in providers:
            try:
                # 这里应该调用实际的连接测试
                # 由于这是示例，我们使用模拟实现
                await asyncio.sleep(0.1)  # 模拟网络延迟
                
                # 模拟连接测试结果
                is_connected = True  # 实际应该调用真实的连接测试
                
                results[provider.value] = HealthStatus(
                    component=f"cloud_connection_{provider.value}",
                    status="healthy" if is_connected else "unhealthy",
                    message=f"{provider.value} 连接 {'正常' if is_connected else '异常'}",
                    last_check=datetime.now()
                )
                
            except Exception as e:
                results[provider.value] = HealthStatus(
                    component=f"cloud_connection_{provider.value}",
                    status="unhealthy",
                    message=f"{provider.value} 连接检查失败: {str(e)}",
                    last_check=datetime.now()
                )
        
        return results
    
    async def check_dependencies(self) -> Dict[str, HealthStatus]:
        """检查依赖服务"""
        results = {}
        
        # 检查Redis连接
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            results['redis'] = HealthStatus(
                component="redis",
                status="healthy",
                message="Redis连接正常",
                last_check=datetime.now()
            )
        except Exception as e:
            results['redis'] = HealthStatus(
                component="redis",
                status="unhealthy",
                message=f"Redis连接失败: {str(e)}",
                last_check=datetime.now()
            )
        
        # 检查存储空间
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100
            
            if free_percent > 10:
                status = "healthy"
                message = f"存储空间充足: {free_percent:.1f}% 可用"
            else:
                status = "degraded"
                message = f"存储空间不足: {free_percent:.1f}% 可用"
            
            results['storage'] = HealthStatus(
                component="storage",
                status=status,
                message=message,
                last_check=datetime.now(),
                details={
                    'total_gb': total / (1024**3),
                    'free_gb': free / (1024**3),
                    'free_percent': free_percent
                }
            )
        except Exception as e:
            results['storage'] = HealthStatus(
                component="storage",
                status="unhealthy",
                message=f"存储检查失败: {str(e)}",
                last_check=datetime.now()
            )
        
        return results
    
    def get_overall_health(self, health_results: Dict[str, HealthStatus]) -> str:
        """获取整体健康状态"""
        if not health_results:
            return "unknown"
        
        statuses = [status.status for status in health_results.values()]
        
        if "unhealthy" in statuses:
            return "unhealthy"
        elif "degraded" in statuses:
            return "degraded"
        else:
            return "healthy"
    
    def get_health_summary(self, health_results: Dict[str, HealthStatus]) -> Dict[str, Any]:
        """获取健康状态摘要"""
        overall_health = self.get_overall_health(health_results)
        
        summary = {
            'overall_status': overall_health,
            'total_components': len(health_results),
            'healthy_components': sum(1 for s in health_results.values() if s.status == "healthy"),
            'degraded_components': sum(1 for s in health_results.values() if s.status == "degraded"),
            'unhealthy_components': sum(1 for s in health_results.values() if s.status == "unhealthy"),
            'last_check': max(s.last_check for s in health_results.values()) if health_results else None,
            'components': {
                name: {
                    'status': status.status,
                    'message': status.message,
                    'last_check': status.last_check.isoformat(),
                    'details': status.details
                }
                for name, status in health_results.items()
            }
        }
        
        return summary
