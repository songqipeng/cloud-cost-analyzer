#!/usr/bin/env python3
"""
测试重试机制和熔断器功能
"""
import sys
import os
import time
import random
from typing import Dict, Any

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cloud_cost_analyzer.utils.retry import (
    retry_with_backoff,
    CircuitBreaker, 
    RateLimiter,
    retry_manager,
    ErrorHandler
)

def test_retry_decorator():
    """测试重试装饰器"""
    print("🔄 测试重试装饰器...")
    
    # 模拟不稳定的服务
    class UnstableService:
        def __init__(self, success_rate=0.3):
            self.success_rate = success_rate
            self.call_count = 0
        
        @retry_with_backoff(max_tries=3, base_delay=0.1, jitter=False)
        def unstable_operation(self):
            self.call_count += 1
            print(f"   第{self.call_count}次调用...")
            
            if random.random() < self.success_rate:
                return f"成功! (第{self.call_count}次尝试)"
            else:
                raise ConnectionError(f"连接失败 (第{self.call_count}次尝试)")
    
    print("\n1. 基本重试功能测试")
    service = UnstableService(success_rate=0.6)  # 60%成功率
    
    try:
        result = service.unstable_operation()
        print(f"   ✅ 操作成功: {result}")
    except Exception as e:
        print(f"   ❌ 操作失败: {e}")
    
    print(f"   总调用次数: {service.call_count}")
    
    # 测试不同的重试策略
    print("\n2. 不同重试策略测试")
    
    @retry_with_backoff(max_tries=3, backoff_type='exponential', base_delay=0.1)
    def exponential_retry():
        if random.random() < 0.7:  # 70%失败率
            raise ValueError("指数退避测试失败")
        return "指数退避成功"
    
    @retry_with_backoff(max_tries=3, backoff_type='linear', base_delay=0.1)
    def linear_retry():
        if random.random() < 0.7:
            raise ValueError("线性退避测试失败") 
        return "线性退避成功"
    
    strategies = [
        ("指数退避", exponential_retry),
        ("线性退避", linear_retry)
    ]
    
    for name, func in strategies:
        try:
            start_time = time.time()
            result = func()
            duration = time.time() - start_time
            print(f"   ✅ {name}: {result} (耗时: {duration:.2f}s)")
        except Exception as e:
            duration = time.time() - start_time
            print(f"   ❌ {name}: {e} (耗时: {duration:.2f}s)")

def test_circuit_breaker():
    """测试熔断器功能"""
    print("\n⚡ 测试熔断器功能...")
    
    circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        timeout=2,  # 2秒超时
        expected_exception=ConnectionError
    )
    
    # 模拟故障服务
    def failing_service():
        raise ConnectionError("服务不可用")
    
    def working_service():
        return "服务正常"
    
    print("\n1. 熔断器状态变化测试")
    
    # 测试正常状态 -> 熔断状态
    for i in range(6):
        try:
            with circuit_breaker:
                if i < 3:  # 前3次失败
                    print(f"   调用{i+1}: 模拟失败...")
                    failing_service()
                else:  # 后续尝试调用
                    print(f"   调用{i+1}: 尝试服务...")
                    working_service()
                print(f"   调用{i+1}: 成功")
        except Exception as e:
            print(f"   调用{i+1}: {type(e).__name__} - {e}")
        
        time.sleep(0.1)  # 短暂延迟
    
    print(f"   最终熔断器状态: {circuit_breaker.state}")
    
    # 等待熔断器恢复
    print(f"\n2. 等待熔断器恢复 ({circuit_breaker.timeout}秒)...")
    time.sleep(circuit_breaker.timeout + 0.1)
    
    # 测试恢复后的调用
    print("3. 熔断器恢复后测试")
    try:
        with circuit_breaker:
            result = working_service()
        print(f"   ✅ 服务恢复: {result}")
        print(f"   熔断器状态: {circuit_breaker.state}")
    except Exception as e:
        print(f"   ❌ 服务仍然失败: {e}")

def test_rate_limiter():
    """测试限流器功能"""
    print("\n🚦 测试限流器功能...")
    
    # 创建限流器：每秒2个请求，突发容量3
    rate_limiter = RateLimiter(rate=2.0, burst=3)
    
    print("\n1. 基本限流测试")
    
    # 快速发送请求测试限流
    success_count = 0
    failed_count = 0
    
    for i in range(6):
        try:
            with rate_limiter:
                print(f"   请求{i+1}: 通过")
                success_count += 1
        except Exception as e:
            print(f"   请求{i+1}: 被限流 - {e}")
            failed_count += 1
        
        time.sleep(0.1)  # 短暂延迟
    
    print(f"\n   成功请求: {success_count}")
    print(f"   被限流: {failed_count}")
    
    # 等待一段时间让令牌恢复
    print("\n2. 等待令牌恢复...")
    time.sleep(2)
    
    # 再次测试
    print("3. 令牌恢复后测试")
    try:
        with rate_limiter:
            print("   ✅ 请求成功")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

def test_retry_manager():
    """测试重试管理器"""
    print("\n🎯 测试重试管理器...")
    
    print("\n1. 预定义策略测试")
    
    # 测试AWS API重试策略
    @retry_manager.retry_with_strategy('aws_api')
    def aws_api_call():
        if random.random() < 0.6:  # 60%失败率
            raise ConnectionError("AWS API 调用失败")
        return "AWS API 调用成功"
    
    try:
        result = aws_api_call()
        print(f"   ✅ AWS API: {result}")
    except Exception as e:
        print(f"   ❌ AWS API: {e}")
    
    # 测试缓存操作重试策略
    @retry_manager.retry_with_strategy('cache_operation')
    def cache_operation():
        if random.random() < 0.5:  # 50%失败率
            raise IOError("缓存操作失败")
        return "缓存操作成功"
    
    try:
        result = cache_operation()
        print(f"   ✅ 缓存操作: {result}")
    except Exception as e:
        print(f"   ❌ 缓存操作: {e}")
    
    print("\n2. 保护机制组合测试")
    
    # 使用组合保护机制
    def protected_operation():
        if random.random() < 0.7:
            raise ConnectionError("受保护的操作失败")
        return "受保护的操作成功"
    
    try:
        result = retry_manager.execute_with_protection(
            protected_operation,
            strategy_name='cloud_api',
            circuit_breaker_key='test_service',
            rate_limiter_key='test_api'
        )
        print(f"   ✅ 保护机制测试: {result}")
    except Exception as e:
        print(f"   ❌ 保护机制测试: {e}")

def test_error_handler():
    """测试错误处理器"""
    print("\n🔍 测试错误处理器...")
    
    error_handler = ErrorHandler()
    
    print("\n1. 错误处理和统计")
    
    # 模拟各种错误
    errors = [
        (ConnectionError("网络连接失败"), "api_call"),
        (TimeoutError("请求超时"), "api_call"),
        (ValueError("参数错误"), "data_processing"),
        (ConnectionError("网络连接失败"), "api_call"),  # 重复错误
        (IOError("文件读取失败"), "file_operation")
    ]
    
    for error, context in errors:
        result = error_handler.handle_error(error, context)
        print(f"   错误处理: {result['error_type']} ({result['count']}次)")
        print(f"     建议: {result['suggestion']}")
    
    print("\n2. 错误统计信息")
    stats = error_handler.get_error_statistics()
    
    print(f"   错误类型总数: {stats['total_error_types']}")
    print("   错误计数:")
    for error_key, count in stats['error_counts'].items():
        print(f"     {error_key}: {count}次")
    
    print("   最近错误:")
    for error_key, error_info in stats['recent_errors'].items():
        print(f"     {error_key}: {error_info['message'][:50]}...")

def test_performance():
    """测试性能"""
    print("\n⚡ 性能测试...")
    
    # 测试重试性能
    print("\n1. 重试机制性能")
    
    @retry_with_backoff(max_tries=1, base_delay=0.001)  # 最小延迟
    def fast_operation():
        return "快速操作"
    
    start_time = time.time()
    iterations = 1000
    
    for _ in range(iterations):
        fast_operation()
    
    duration = time.time() - start_time
    print(f"   {iterations}次快速重试操作")
    print(f"   总耗时: {duration:.4f}秒") 
    print(f"   平均耗时: {duration/iterations*1000:.2f}毫秒/次")
    print(f"   处理速度: {iterations/duration:.0f}次/秒")
    
    # 测试熔断器性能
    print("\n2. 熔断器性能")
    circuit_breaker = CircuitBreaker(failure_threshold=1000, timeout=60)
    
    start_time = time.time()
    
    for _ in range(iterations):
        try:
            with circuit_breaker:
                pass  # 空操作
        except:
            pass
    
    duration = time.time() - start_time
    print(f"   {iterations}次熔断器检查")
    print(f"   总耗时: {duration:.4f}秒")
    print(f"   平均耗时: {duration/iterations*1000:.2f}毫秒/次")

if __name__ == '__main__':
    try:
        print("🔄 重试机制和熔断器测试")
        print("=" * 50)
        
        test_retry_decorator()
        test_circuit_breaker()
        test_rate_limiter()
        test_retry_manager()
        test_error_handler()
        test_performance()
        
        print("\n✅ 重试机制测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()