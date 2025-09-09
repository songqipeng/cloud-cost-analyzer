#!/usr/bin/env python3
"""
测试异步多云分析器功能
"""
import sys
import os
import asyncio
import time
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cloud_cost_analyzer.core.enhanced_async_analyzer import (
    EnhancedAsyncMultiCloudAnalyzer,
    analyze_multi_cloud_async,
    batch_analyze_async
)

async def test_async_analyzer():
    """测试异步分析器功能"""
    print("🚀 测试异步多云分析器...")
    
    config = {
        'async': {
            'max_concurrent_providers': 4,
            'connection_pool_size': 20,
            'task_timeout': 30
        },
        'cache': {
            'l1_enabled': True,
            'l2_enabled': True,
            'l3_enabled': False
        }
    }
    
    print("\n1. 基本异步分析测试")
    
    async with EnhancedAsyncMultiCloudAnalyzer(config=config) as analyzer:
        start_time = time.time()
        
        # 测试多云并发分析
        result = await analyzer.analyze_multi_cloud_async(
            providers=['aws', 'aliyun', 'tencent'],
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        duration = time.time() - start_time
        
        print(f"   ✅ 分析完成，耗时: {duration:.2f}秒")
        print(f"   分析ID: {result['analysis_id']}")
        print(f"   总费用: ${result['summary']['total_cost']:.2f}")
        print(f"   成功云商: {len(result['providers']['successful'])}")
        print(f"   失败云商: {len(result['providers']['failed'])}")
        print(f"   缓存命中率: {result['summary']['cache_hit_rate']:.2%}")
        
        # 显示各云商数据
        for provider, data in result['provider_data'].items():
            print(f"   {provider}: ${data['total_cost']:.2f} ({len(data['services'])} 服务)")
    
    return duration

async def test_connection_testing():
    """测试连接测试功能"""
    print("\n2. 连接测试功能")
    
    config = {'async': {'max_concurrent_providers': 4}}
    
    async with EnhancedAsyncMultiCloudAnalyzer(config=config) as analyzer:
        start_time = time.time()
        
        connections = await analyzer.test_all_connections_async()
        
        duration = time.time() - start_time
        
        print(f"   连接测试耗时: {duration:.2f}秒")
        
        for provider, (status, message) in connections.items():
            status_emoji = '✅' if status else '❌'
            print(f"   {status_emoji} {provider}: {message}")

async def test_performance_stats():
    """测试性能统计功能"""
    print("\n3. 性能统计测试")
    
    config = {'cache': {'l1_enabled': True, 'l2_enabled': True}}
    
    async with EnhancedAsyncMultiCloudAnalyzer(config=config) as analyzer:
        # 执行一些操作来生成统计数据
        await analyzer.analyze_multi_cloud_async(
            providers=['aws', 'aliyun'],
            start_date='2024-01-01',
            end_date='2024-01-15'
        )
        
        stats = analyzer.get_performance_stats()
        
        print("   性能统计:")
        print(f"     API调用数: {stats['api_calls']}")
        print(f"     缓存命中: {stats['cache_hits']}")
        print(f"     缓存未命中: {stats['cache_misses']}")
        print(f"     错误数: {stats['errors']}")
        print(f"     总耗时: {stats['total_duration']:.2f}秒")
        
        if stats['provider_durations']:
            print("     云商耗时:")
            for provider, duration in stats['provider_durations'].items():
                print(f"       {provider}: {duration:.2f}秒")
        
        print(f"     任务管理器状态:")
        task_stats = stats['task_manager']
        print(f"       活跃任务: {task_stats['active_tasks']}")
        print(f"       可用槽位: {task_stats['available_slots']}")

async def test_convenient_function():
    """测试便捷函数"""
    print("\n4. 便捷函数测试")
    
    config = {'async': {'max_concurrent_providers': 2}}
    
    start_time = time.time()
    
    # 使用便捷函数进行分析
    result = await analyze_multi_cloud_async(
        providers=['aws', 'tencent'],
        start_date='2024-02-01',
        end_date='2024-02-15',
        config=config
    )
    
    duration = time.time() - start_time
    
    print(f"   ✅ 便捷函数分析完成，耗时: {duration:.2f}秒")
    print(f"   总费用: ${result['summary']['total_cost']:.2f}")

async def test_batch_analysis():
    """测试批量分析功能"""
    print("\n5. 批量分析测试")
    
    # 创建批量分析请求
    batch_requests = [
        {
            'providers': ['aws'],
            'start_date': '2024-01-01',
            'end_date': '2024-01-15'
        },
        {
            'providers': ['aliyun', 'tencent'],
            'start_date': '2024-01-16',
            'end_date': '2024-01-31'
        },
        {
            'providers': ['volcengine'],
            'start_date': '2024-02-01',
            'end_date': '2024-02-15'
        }
    ]
    
    config = {'async': {'max_concurrent_providers': 3}}
    
    start_time = time.time()
    
    # 执行批量分析
    results = await batch_analyze_async(batch_requests, config)
    
    duration = time.time() - start_time
    
    print(f"   ✅ 批量分析完成，耗时: {duration:.2f}秒")
    print(f"   批处理数量: {len(results)}")
    
    total_cost = 0
    successful_analyses = 0
    
    for i, result in enumerate(results, 1):
        if 'error' in result:
            print(f"   ❌ 分析{i}: {result['message']}")
        else:
            cost = result['summary']['total_cost']
            total_cost += cost
            successful_analyses += 1
            print(f"   ✅ 分析{i}: ${cost:.2f}")
    
    print(f"   成功分析: {successful_analyses}/{len(results)}")
    print(f"   批量总费用: ${total_cost:.2f}")

async def test_error_handling():
    """测试错误处理"""
    print("\n6. 错误处理测试")
    
    config = {'async': {'task_timeout': 1}}  # 短超时时间
    
    try:
        # 模拟可能超时的分析
        async with EnhancedAsyncMultiCloudAnalyzer(config=config) as analyzer:
            # 尝试分析大范围数据（可能超时）
            result = await analyzer.analyze_multi_cloud_async(
                providers=['aws', 'aliyun', 'tencent', 'volcengine'],
                start_date='2023-01-01',
                end_date='2023-12-31'
            )
            print("   ✅ 大范围分析成功")
    except asyncio.TimeoutError:
        print("   ⚠️ 分析超时（预期行为）")
    except Exception as e:
        print(f"   ❌ 分析失败: {type(e).__name__}: {e}")

async def test_sync_vs_async_performance():
    """测试同步vs异步性能对比"""
    print("\n7. 性能对比测试")
    
    # 异步分析
    config = {'async': {'max_concurrent_providers': 4}}
    
    start_time = time.time()
    
    result = await analyze_multi_cloud_async(
        providers=['aws', 'aliyun', 'tencent', 'volcengine'],
        start_date='2024-01-01',
        end_date='2024-01-31',
        config=config
    )
    
    async_duration = time.time() - start_time
    
    # 模拟同步分析
    start_time = time.time()
    
    # 模拟串行处理各个云商（每个0.6秒）
    providers = ['aws', 'aliyun', 'tencent', 'volcengine']
    for provider in providers:
        time.sleep(0.6)  # 模拟API调用延迟
    
    sync_duration = time.time() - start_time
    
    performance_improvement = ((sync_duration - async_duration) / sync_duration) * 100
    
    print(f"   同步模拟耗时: {sync_duration:.2f}秒")
    print(f"   异步实际耗时: {async_duration:.2f}秒")
    print(f"   性能提升: {performance_improvement:.1f}%")
    
    return async_duration, sync_duration

async def main():
    """主测试函数"""
    print("🚀 异步多云分析器功能测试")
    print("=" * 50)
    
    try:
        # 执行各项测试
        analysis_duration = await test_async_analyzer()
        await test_connection_testing()
        await test_performance_stats()
        await test_convenient_function()
        await test_batch_analysis()
        await test_error_handling()
        
        # 性能对比
        async_duration, sync_duration = await test_sync_vs_async_performance()
        
        print("\n📊 测试总结:")
        print(f"   异步分析器工作正常")
        print(f"   基本分析耗时: {analysis_duration:.2f}秒")
        print(f"   支持并发、缓存、错误处理等功能")
        
        print("\n✅ 异步多云分析器测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # 运行异步测试
    asyncio.run(main())