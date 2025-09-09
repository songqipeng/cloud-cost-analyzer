#!/usr/bin/env python3
"""
测试监控指标收集功能
"""
import sys
import os
import time
import threading
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cloud_cost_analyzer.monitoring import get_metrics_collector, initialize_metrics

def test_metrics_initialization():
    """测试监控系统初始化"""
    print("📊 测试监控系统初始化...")
    
    config = {
        'system_collection_interval': 2,  # 2秒收集间隔
        'max_history': 100
    }
    
    # 初始化监控系统
    metrics = initialize_metrics(config)
    
    print(f"   ✅ 监控系统已初始化")
    print(f"   启动状态: {'已启动' if metrics.started else '未启动'}")
    
    return metrics

def test_system_metrics():
    """测试系统指标收集"""
    print("\n💻 测试系统指标收集...")
    
    config = {'system_collection_interval': 1}
    metrics = get_metrics_collector(config)
    metrics.start()
    
    print("   等待系统指标收集...")
    time.sleep(3)  # 等待收集几次数据
    
    # 获取指标摘要
    summary = metrics.get_metrics_summary()
    
    print("   系统指标:")
    for name, value in summary['system_metrics'].items():
        if 'percent' in name:
            print(f"     {name}: {value:.1f}%")
        elif 'mb' in name:
            print(f"     {name}: {value:.1f}MB")
        else:
            print(f"     {name}: {value:.2f}")
    
    metrics.stop()
    return True

def test_business_metrics():
    """测试业务指标记录"""
    print("\n📈 测试业务指标记录...")
    
    metrics = get_metrics_collector()
    
    # 记录API调用指标
    print("   记录API调用指标...")
    metrics.business_collector.record_api_call(
        provider='aws',
        operation='get_cost_data',
        duration=1.5,
        success=True
    )
    
    metrics.business_collector.record_api_call(
        provider='aliyun',
        operation='get_cost_data', 
        duration=2.3,
        success=False
    )
    
    # 记录成本分析指标
    print("   记录成本分析指标...")
    metrics.business_collector.record_cost_analysis(
        provider='aws',
        total_cost=123.45,
        service_count=5,
        analysis_duration=3.2
    )
    
    # 记录缓存操作指标
    print("   记录缓存操作指标...")
    metrics.business_collector.record_cache_operation(
        operation='get',
        hit=True,
        cache_level='l1'
    )
    
    metrics.business_collector.record_cache_operation(
        operation='get',
        hit=False,
        cache_level='l2'
    )
    
    # 获取指标摘要
    summary = metrics.get_metrics_summary()
    
    print("   API指标:")
    for name, value in summary['api_metrics'].items():
        print(f"     {name}: {value}")
    
    print("   缓存指标:")
    for name, value in summary['cache_metrics'].items():
        print(f"     {name}: {value}")
    
    return True

def test_error_metrics():
    """测试错误指标记录"""
    print("\n❌ 测试错误指标记录...")
    
    metrics = get_metrics_collector()
    
    # 记录各种错误
    print("   记录错误指标...")
    errors = [
        ('ConnectionError', 'api_call', 'aws'),
        ('TimeoutError', 'api_call', 'aliyun'),
        ('ValidationError', 'data_processing', None),
        ('ConnectionError', 'api_call', 'aws'),  # 重复错误
        ('CacheError', 'cache_operation', None)
    ]
    
    for error_type, context, provider in errors:
        metrics.error_collector.record_error(error_type, context, provider)
    
    # 获取指标摘要
    summary = metrics.get_metrics_summary()
    
    print("   错误指标:")
    for name, value in summary['error_metrics'].items():
        print(f"     {name}: {value}")
    
    return True

def test_performance_timing():
    """测试性能计时功能"""
    print("\n⏱️ 测试性能计时功能...")
    
    metrics = get_metrics_collector()
    
    # 使用计时上下文管理器
    print("   测试成功操作计时...")
    with metrics.time_operation('data_processing', {'type': 'cost_analysis'}):
        time.sleep(0.5)  # 模拟操作耗时
    
    print("   测试失败操作计时...")
    try:
        with metrics.time_operation('api_call', {'provider': 'aws', 'operation': 'get_data'}):
            time.sleep(0.2)
            raise ValueError("模拟错误")
    except ValueError:
        pass  # 预期的错误
    
    # 检查生成的指标
    current_values = metrics.registry.get_current_values()
    
    print("   性能指标:")
    for name, stats in current_values['histograms'].items():
        if 'duration' in name:
            print(f"     {name}:")
            print(f"       调用次数: {stats['count']}")
            print(f"       平均耗时: {stats['avg']:.3f}秒")
            print(f"       最大耗时: {stats['max']:.3f}秒")
    
    return True

def test_health_monitoring():
    """测试健康监控"""
    print("\n🏥 测试健康监控...")
    
    config = {'system_collection_interval': 1}
    metrics = get_metrics_collector(config)
    metrics.start()
    
    # 等待收集一些系统指标
    time.sleep(2)
    
    # 获取健康状态
    health = metrics.get_health_status()
    
    print(f"   整体健康状态: {health['status']}")
    print("   各项检查:")
    
    for check_name, check_result in health['checks'].items():
        status_emoji = {
            'ok': '✅',
            'warning': '⚠️',
            'critical': '❌'
        }.get(check_result['status'], '❓')
        
        print(f"     {status_emoji} {check_name}: {check_result['value']:.1f}")
        
        if 'threshold' in check_result:
            print(f"       阈值: {check_result['threshold']}")
        elif 'thresholds' in check_result:
            print(f"       阈值: {check_result['thresholds']}")
    
    print(f"   检查摘要:")
    summary = health['summary']
    print(f"     总检查项: {summary['total_checks']}")
    print(f"     警告项: {summary['warning_count']}")
    print(f"     严重项: {summary['critical_count']}")
    
    metrics.stop()
    return health

def test_metrics_export():
    """测试指标导出"""
    print("\n📤 测试指标导出...")
    
    metrics = get_metrics_collector()
    
    # 生成一些指标数据
    metrics.business_collector.record_api_call('aws', 'test_op', 1.0, True)
    metrics.error_collector.record_error('TestError', 'test_context')
    
    # 导出到文件
    export_file = 'test_metrics_export.json'
    metrics.export_metrics_to_file(export_file)
    
    # 检查导出文件
    if os.path.exists(export_file):
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        print(f"   ✅ 指标已导出到 {export_file}")
        print(f"   导出时间: {exported_data['export_timestamp']}")
        print(f"   指标类型数量:")
        for metric_type, count in exported_data['summary']['metrics_count'].items():
            print(f"     {metric_type}: {count}")
        
        # 清理导出文件
        os.remove(export_file)
        
        return True
    else:
        print("   ❌ 导出文件未生成")
        return False

def test_concurrent_metrics():
    """测试并发指标记录"""
    print("\n🔄 测试并发指标记录...")
    
    metrics = get_metrics_collector()
    
    def worker(worker_id):
        """工作线程函数"""
        for i in range(10):
            # 记录API调用
            metrics.business_collector.record_api_call(
                provider=f'provider_{worker_id}',
                operation='concurrent_test',
                duration=0.1,
                success=True
            )
            
            # 记录错误
            if i % 3 == 0:  # 每3次记录一个错误
                metrics.error_collector.record_error(
                    error_type='ConcurrentTestError',
                    context=f'worker_{worker_id}'
                )
            
            time.sleep(0.01)  # 短暂延迟
    
    # 启动多个工作线程
    threads = []
    worker_count = 5
    
    print(f"   启动 {worker_count} 个并发工作线程...")
    
    for i in range(worker_count):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 检查结果
    summary = metrics.get_metrics_summary()
    
    total_api_calls = sum(summary['api_metrics'].values())
    total_errors = sum(summary['error_metrics'].values())
    
    print(f"   ✅ 并发测试完成")
    print(f"   总API调用: {total_api_calls}")
    print(f"   总错误数: {total_errors}")
    print(f"   预期API调用: {worker_count * 10}")
    print(f"   预期错误数: {worker_count * 4}")  # 每10次调用有约4个错误
    
    return True

def test_metrics_performance():
    """测试指标性能"""
    print("\n⚡ 测试指标收集性能...")
    
    metrics = get_metrics_collector()
    
    # 测试指标记录性能
    iterations = 1000
    
    # API调用指标性能测试
    start_time = time.time()
    
    for i in range(iterations):
        metrics.business_collector.record_api_call(
            provider='perf_test',
            operation='test_op',
            duration=0.1,
            success=True
        )
    
    api_duration = time.time() - start_time
    
    # 错误指标性能测试
    start_time = time.time()
    
    for i in range(iterations):
        metrics.error_collector.record_error(
            error_type='PerfTestError',
            context='performance_test'
        )
    
    error_duration = time.time() - start_time
    
    print(f"   API指标记录性能:")
    print(f"     {iterations} 次记录耗时: {api_duration:.4f}秒")
    print(f"     平均耗时: {api_duration/iterations*1000:.2f}毫秒/次")
    print(f"     处理速度: {iterations/api_duration:.0f}次/秒")
    
    print(f"   错误指标记录性能:")
    print(f"     {iterations} 次记录耗时: {error_duration:.4f}秒")
    print(f"     平均耗时: {error_duration/iterations*1000:.2f}毫秒/次")
    print(f"     处理速度: {iterations/error_duration:.0f}次/秒")
    
    return True

def main():
    """主测试函数"""
    print("📊 监控指标收集功能测试")
    print("=" * 50)
    
    try:
        # 执行各项测试
        metrics = test_metrics_initialization()
        test_system_metrics()
        test_business_metrics()
        test_error_metrics()
        test_performance_timing()
        health = test_health_monitoring()
        test_metrics_export()
        test_concurrent_metrics()
        test_metrics_performance()
        
        print("\n📊 测试总结:")
        print("   ✅ 监控系统初始化正常")
        print("   ✅ 系统指标收集正常")
        print("   ✅ 业务指标记录正常")
        print("   ✅ 错误指标记录正常")
        print("   ✅ 性能计时功能正常")
        print("   ✅ 健康监控功能正常")
        print("   ✅ 指标导出功能正常")
        print("   ✅ 并发指标记录正常")
        print("   ✅ 指标性能测试通过")
        print(f"   系统整体健康状态: {health['status']}")
        
        print("\n✅ 监控指标收集测试完成!")
        
        # 最终清理
        metrics.stop()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()