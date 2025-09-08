"""
监控和指标收集模块
提供系统性能、业务指标、错误监控等功能
"""
import time
import threading
import asyncio
import psutil
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from contextlib import contextmanager
import json
import os

from cloud_cost_analyzer.utils.secure_logger import get_secure_logger

logger = get_secure_logger()


@dataclass
class MetricPoint:
    """指标数据点"""
    name: str
    value: Union[int, float]
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: str = 'gauge'  # gauge, counter, histogram, summary


@dataclass
class PerformanceMetrics:
    """性能指标"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    timestamp: float


class MetricsRegistry:
    """指标注册表"""
    
    def __init__(self, max_history: int = 1000):
        """
        初始化指标注册表
        
        Args:
            max_history: 最大历史记录数量
        """
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.summaries: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        self._lock = threading.RLock()
        
    def record_metric(self, metric: MetricPoint):
        """记录指标"""
        with self._lock:
            # 添加到历史记录
            self.metrics[metric.name].append(metric)
            
            # 根据指标类型更新相应的存储
            if metric.metric_type == 'counter':
                self.counters[metric.name] += metric.value
            elif metric.metric_type == 'gauge':
                self.gauges[metric.name] = metric.value
            elif metric.metric_type == 'histogram':
                self.histograms[metric.name].append(metric.value)
                # 保持直方图大小合理
                if len(self.histograms[metric.name]) > 1000:
                    self.histograms[metric.name] = self.histograms[metric.name][-1000:]
            elif metric.metric_type == 'summary':
                if metric.name not in self.summaries:
                    self.summaries[metric.name] = {
                        'count': 0,
                        'sum': 0.0,
                        'min': float('inf'),
                        'max': float('-inf')
                    }
                
                summary = self.summaries[metric.name]
                summary['count'] += 1
                summary['sum'] += metric.value
                summary['min'] = min(summary['min'], metric.value)
                summary['max'] = max(summary['max'], metric.value)
                summary['avg'] = summary['sum'] / summary['count']
    
    def get_metric_history(self, metric_name: str, limit: Optional[int] = None) -> List[MetricPoint]:
        """获取指标历史"""
        with self._lock:
            history = list(self.metrics.get(metric_name, []))
            if limit:
                history = history[-limit:]
            return history
    
    def get_current_values(self) -> Dict[str, Any]:
        """获取当前所有指标值"""
        with self._lock:
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {
                    name: {
                        'count': len(values),
                        'min': min(values) if values else 0,
                        'max': max(values) if values else 0,
                        'avg': sum(values) / len(values) if values else 0,
                        'p50': self._percentile(values, 50) if values else 0,
                        'p95': self._percentile(values, 95) if values else 0,
                        'p99': self._percentile(values, 99) if values else 0
                    }
                    for name, values in self.histograms.items()
                },
                'summaries': dict(self.summaries)
            }
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def clear_metrics(self, metric_name: Optional[str] = None):
        """清除指标"""
        with self._lock:
            if metric_name:
                self.metrics.pop(metric_name, None)
                self.counters.pop(metric_name, None)
                self.gauges.pop(metric_name, None)
                self.histograms.pop(metric_name, None)
                self.summaries.pop(metric_name, None)
            else:
                self.metrics.clear()
                self.counters.clear()
                self.gauges.clear()
                self.histograms.clear()
                self.summaries.clear()


class SystemMetricsCollector:
    """系统指标收集器"""
    
    def __init__(self, registry: MetricsRegistry, collection_interval: int = 5):
        """
        初始化系统指标收集器
        
        Args:
            registry: 指标注册表
            collection_interval: 收集间隔（秒）
        """
        self.registry = registry
        self.collection_interval = collection_interval
        self.running = False
        self.collection_thread: Optional[threading.Thread] = None
        
        # 网络统计基准
        self._last_network_stats = psutil.net_io_counters()
        self._last_network_time = time.time()
    
    def start(self):
        """开始收集系统指标"""
        if not self.running:
            self.running = True
            self.collection_thread = threading.Thread(
                target=self._collection_loop,
                daemon=True,
                name="system-metrics-collector"
            )
            self.collection_thread.start()
            logger.info("System metrics collection started")
    
    def stop(self):
        """停止收集系统指标"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("System metrics collection stopped")
    
    def _collection_loop(self):
        """指标收集循环"""
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self):
        """收集系统指标"""
        timestamp = time.time()
        
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            self.registry.record_metric(MetricPoint(
                name='system.cpu.percent',
                value=cpu_percent,
                timestamp=timestamp,
                metric_type='gauge'
            ))
            
            # 内存使用率
            memory = psutil.virtual_memory()
            self.registry.record_metric(MetricPoint(
                name='system.memory.percent',
                value=memory.percent,
                timestamp=timestamp,
                metric_type='gauge'
            ))
            
            self.registry.record_metric(MetricPoint(
                name='system.memory.used_mb',
                value=memory.used / 1024 / 1024,
                timestamp=timestamp,
                metric_type='gauge'
            ))
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.registry.record_metric(MetricPoint(
                name='system.disk.percent',
                value=disk_percent,
                timestamp=timestamp,
                metric_type='gauge'
            ))
            
            # 网络IO
            current_network = psutil.net_io_counters()
            current_time = time.time()
            
            if hasattr(self, '_last_network_stats'):
                time_delta = current_time - self._last_network_time
                bytes_sent_rate = (current_network.bytes_sent - self._last_network_stats.bytes_sent) / time_delta
                bytes_recv_rate = (current_network.bytes_recv - self._last_network_stats.bytes_recv) / time_delta
                
                self.registry.record_metric(MetricPoint(
                    name='system.network.bytes_sent_rate',
                    value=bytes_sent_rate,
                    timestamp=timestamp,
                    metric_type='gauge'
                ))
                
                self.registry.record_metric(MetricPoint(
                    name='system.network.bytes_recv_rate',
                    value=bytes_recv_rate,
                    timestamp=timestamp,
                    metric_type='gauge'
                ))
            
            self._last_network_stats = current_network
            self._last_network_time = current_time
            
        except Exception as e:
            logger.error(f"Error in system metrics collection: {e}")


class BusinessMetricsCollector:
    """业务指标收集器"""
    
    def __init__(self, registry: MetricsRegistry):
        """
        初始化业务指标收集器
        
        Args:
            registry: 指标注册表
        """
        self.registry = registry
        
    def record_api_call(self, provider: str, operation: str, 
                       duration: float, success: bool = True):
        """
        记录API调用指标
        
        Args:
            provider: 云服务提供商
            operation: 操作类型
            duration: 调用耗时（秒）
            success: 是否成功
        """
        timestamp = time.time()
        labels = {'provider': provider, 'operation': operation}
        
        # API调用计数
        self.registry.record_metric(MetricPoint(
            name='api.calls.total',
            value=1,
            timestamp=timestamp,
            labels=labels,
            metric_type='counter'
        ))
        
        # 成功/失败计数
        result_labels = {**labels, 'result': 'success' if success else 'failure'}
        self.registry.record_metric(MetricPoint(
            name='api.calls.by_result',
            value=1,
            timestamp=timestamp,
            labels=result_labels,
            metric_type='counter'
        ))
        
        # API调用耗时
        if success:
            self.registry.record_metric(MetricPoint(
                name='api.duration.seconds',
                value=duration,
                timestamp=timestamp,
                labels=labels,
                metric_type='histogram'
            ))
    
    def record_cost_analysis(self, provider: str, total_cost: float, 
                           service_count: int, analysis_duration: float):
        """
        记录成本分析指标
        
        Args:
            provider: 云服务提供商
            total_cost: 总成本
            service_count: 服务数量
            analysis_duration: 分析耗时
        """
        timestamp = time.time()
        labels = {'provider': provider}
        
        # 总成本
        self.registry.record_metric(MetricPoint(
            name='cost.total',
            value=total_cost,
            timestamp=timestamp,
            labels=labels,
            metric_type='gauge'
        ))
        
        # 服务数量
        self.registry.record_metric(MetricPoint(
            name='cost.services.count',
            value=service_count,
            timestamp=timestamp,
            labels=labels,
            metric_type='gauge'
        ))
        
        # 分析耗时
        self.registry.record_metric(MetricPoint(
            name='cost.analysis.duration.seconds',
            value=analysis_duration,
            timestamp=timestamp,
            labels=labels,
            metric_type='histogram'
        ))
        
        # 分析完成计数
        self.registry.record_metric(MetricPoint(
            name='cost.analysis.completed.total',
            value=1,
            timestamp=timestamp,
            labels=labels,
            metric_type='counter'
        ))
    
    def record_cache_operation(self, operation: str, hit: bool, 
                             cache_level: Optional[str] = None):
        """
        记录缓存操作指标
        
        Args:
            operation: 操作类型 (get, set, delete)
            hit: 是否命中缓存
            cache_level: 缓存级别 (l1, l2, l3)
        """
        timestamp = time.time()
        
        labels = {'operation': operation}
        if cache_level:
            labels['level'] = cache_level
        
        # 缓存操作计数
        self.registry.record_metric(MetricPoint(
            name='cache.operations.total',
            value=1,
            timestamp=timestamp,
            labels=labels,
            metric_type='counter'
        ))
        
        # 缓存命中/未命中
        if operation == 'get':
            hit_labels = {**labels, 'result': 'hit' if hit else 'miss'}
            self.registry.record_metric(MetricPoint(
                name='cache.get.by_result',
                value=1,
                timestamp=timestamp,
                labels=hit_labels,
                metric_type='counter'
            ))


class ErrorMetricsCollector:
    """错误指标收集器"""
    
    def __init__(self, registry: MetricsRegistry):
        """
        初始化错误指标收集器
        
        Args:
            registry: 指标注册表
        """
        self.registry = registry
    
    def record_error(self, error_type: str, context: str, 
                    provider: Optional[str] = None):
        """
        记录错误指标
        
        Args:
            error_type: 错误类型
            context: 错误上下文
            provider: 云服务提供商（可选）
        """
        timestamp = time.time()
        
        labels = {
            'error_type': error_type,
            'context': context
        }
        
        if provider:
            labels['provider'] = provider
        
        # 错误总计数
        self.registry.record_metric(MetricPoint(
            name='errors.total',
            value=1,
            timestamp=timestamp,
            labels=labels,
            metric_type='counter'
        ))
        
        # 按类型计数
        self.registry.record_metric(MetricPoint(
            name='errors.by_type',
            value=1,
            timestamp=timestamp,
            labels={'error_type': error_type},
            metric_type='counter'
        ))


class MetricsCollector:
    """主指标收集器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化指标收集器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.registry = MetricsRegistry(
            max_history=self.config.get('max_history', 1000)
        )
        
        # 初始化各种收集器
        self.system_collector = SystemMetricsCollector(
            self.registry,
            collection_interval=self.config.get('system_collection_interval', 5)
        )
        self.business_collector = BusinessMetricsCollector(self.registry)
        self.error_collector = ErrorMetricsCollector(self.registry)
        
        # 启动标志
        self.started = False
    
    def start(self):
        """启动指标收集"""
        if not self.started:
            self.system_collector.start()
            self.started = True
            logger.info("Metrics collection started")
    
    def stop(self):
        """停止指标收集"""
        if self.started:
            self.system_collector.stop()
            self.started = False
            logger.info("Metrics collection stopped")
    
    @contextmanager
    def time_operation(self, operation_name: str, labels: Optional[Dict[str, str]] = None):
        """
        计时上下文管理器
        
        Args:
            operation_name: 操作名称
            labels: 标签字典
        """
        start_time = time.time()
        success = True
        
        try:
            yield
        except Exception:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            
            metric_labels = labels or {}
            metric_labels['result'] = 'success' if success else 'failure'
            
            self.registry.record_metric(MetricPoint(
                name=f'operation.{operation_name}.duration.seconds',
                value=duration,
                timestamp=time.time(),
                labels=metric_labels,
                metric_type='histogram'
            ))
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        current_values = self.registry.get_current_values()
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'collection_started': self.started,
            'metrics_count': {
                'counters': len(current_values['counters']),
                'gauges': len(current_values['gauges']),
                'histograms': len(current_values['histograms']),
                'summaries': len(current_values['summaries'])
            },
            'system_metrics': {
                name: value for name, value in current_values['gauges'].items()
                if name.startswith('system.')
            },
            'api_metrics': {
                name: value for name, value in current_values['counters'].items()
                if name.startswith('api.')
            },
            'error_metrics': {
                name: value for name, value in current_values['counters'].items()
                if name.startswith('errors.')
            },
            'cache_metrics': {
                name: value for name, value in current_values['counters'].items()
                if name.startswith('cache.')
            }
        }
        
        return summary
    
    def export_metrics_to_file(self, file_path: str):
        """导出指标到文件"""
        try:
            metrics_data = {
                'export_timestamp': datetime.now().isoformat(),
                'metrics': self.registry.get_current_values(),
                'summary': self.get_metrics_summary()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, default=str)
            
            logger.info(f"Metrics exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics to file: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        current_values = self.registry.get_current_values()
        
        # 基础健康指标
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # 系统资源检查
        cpu_percent = current_values['gauges'].get('system.cpu.percent', 0)
        memory_percent = current_values['gauges'].get('system.memory.percent', 0)
        disk_percent = current_values['gauges'].get('system.disk.percent', 0)
        
        health['checks']['cpu'] = {
            'status': 'warning' if cpu_percent > 80 else 'ok',
            'value': cpu_percent,
            'threshold': 80
        }
        
        health['checks']['memory'] = {
            'status': 'warning' if memory_percent > 85 else 'ok',
            'value': memory_percent,
            'threshold': 85
        }
        
        health['checks']['disk'] = {
            'status': 'warning' if disk_percent > 90 else 'ok',
            'value': disk_percent,
            'threshold': 90
        }
        
        # 错误率检查
        total_errors = sum(current_values['counters'].get(key, 0) 
                          for key in current_values['counters'] 
                          if key.startswith('errors.'))
        
        total_api_calls = sum(current_values['counters'].get(key, 0) 
                             for key in current_values['counters'] 
                             if key.startswith('api.calls.'))
        
        error_rate = (total_errors / total_api_calls * 100) if total_api_calls > 0 else 0
        
        health['checks']['error_rate'] = {
            'status': 'critical' if error_rate > 10 else 'warning' if error_rate > 5 else 'ok',
            'value': error_rate,
            'thresholds': {'warning': 5, 'critical': 10}
        }
        
        # 总体状态判断
        warning_count = sum(1 for check in health['checks'].values() 
                           if check['status'] == 'warning')
        critical_count = sum(1 for check in health['checks'].values() 
                            if check['status'] == 'critical')
        
        if critical_count > 0:
            health['status'] = 'critical'
        elif warning_count > 0:
            health['status'] = 'warning'
        
        health['summary'] = {
            'total_checks': len(health['checks']),
            'warning_count': warning_count,
            'critical_count': critical_count
        }
        
        return health


# 全局指标收集器实例
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(config: Optional[Dict[str, Any]] = None) -> MetricsCollector:
    """
    获取全局指标收集器实例
    
    Args:
        config: 配置字典
        
    Returns:
        指标收集器实例
    """
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(config)
    
    return _metrics_collector


def initialize_metrics(config: Dict[str, Any]) -> MetricsCollector:
    """
    初始化全局指标收集
    
    Args:
        config: 配置字典
        
    Returns:
        指标收集器实例
    """
    global _metrics_collector
    _metrics_collector = MetricsCollector(config)
    
    # 根据配置决定是否自动启动
    if config.get('auto_start_metrics', True):
        _metrics_collector.start()
    
    return _metrics_collector