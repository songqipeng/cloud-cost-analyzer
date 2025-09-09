#!/usr/bin/env python3
"""
测试分层缓存系统
"""
import sys
import os
import time
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cloud_cost_analyzer.cache.tiered_cache import TieredCache, CacheKeyGenerator

def test_tiered_cache():
    """测试分层缓存功能"""
    print("🧪 测试分层缓存系统...")
    
    # 配置缓存
    config = {
        'cache': {
            'l1_enabled': True,
            'l2_enabled': True, 
            'l3_enabled': False,
            'l1': {'max_size': 100, 'default_ttl': 10},
            'l2': {'cache_dir': '.test_cache', 'default_ttl': 60}
        }
    }
    
    cache = TieredCache(config)
    
    # 测试基本缓存操作
    print("\n1. 基本缓存操作测试")
    
    # 写入数据
    test_data = {'provider': 'aws', 'cost': 123.45, 'services': ['EC2', 'S3']}
    cache_key = "test_cost_data_aws_2024-01-01_2024-01-31"
    
    success = cache.set(cache_key, test_data, ttl=30)
    print(f"   ✓ 缓存写入: {'成功' if success else '失败'}")
    
    # 读取数据
    cached_data = cache.get(cache_key)
    print(f"   ✓ 缓存读取: {'成功' if cached_data == test_data else '失败'}")
    print(f"   数据内容: {cached_data}")
    
    # 测试缓存统计
    print("\n2. 缓存统计信息")
    stats = cache.get_stats()
    print(f"   总请求数: {stats['total_requests']}")
    print(f"   缓存命中率: {stats['hit_rate']:.2%}")
    print(f"   L1命中率: {stats['l1_hit_rate']:.2%}")
    print(f"   L2命中率: {stats['l2_hit_rate']:.2%}")
    
    # 测试缓存键生成器
    print("\n3. 缓存键生成测试")
    key1 = CacheKeyGenerator.generate_cost_data_key('aws', '2024-01-01', '2024-01-31')
    key2 = CacheKeyGenerator.generate_analysis_key('aws', 'cost_analysis', {'region': 'us-east-1'})
    print(f"   费用数据键: {key1}")
    print(f"   分析结果键: {key2}")
    
    # 测试健康检查
    print("\n4. 缓存健康检查")
    health = cache.is_healthy()
    for level, status in health.items():
        status_emoji = '✅' if status else '❌' if status is False else '⏸️'
        print(f"   {level}: {status_emoji}")
    
    # 测试批量操作
    print("\n5. 批量缓存操作测试")
    for i in range(5):
        key = f"batch_test_{i}"
        value = {'batch_id': i, 'timestamp': time.time()}
        cache.set(key, value)
    
    # 读取并验证
    success_count = 0
    for i in range(5):
        key = f"batch_test_{i}"
        data = cache.get(key)
        if data and data['batch_id'] == i:
            success_count += 1
    
    print(f"   批量操作成功率: {success_count}/5")
    
    # 最终统计
    final_stats = cache.get_stats()
    print(f"\n📊 最终统计:")
    print(f"   总请求: {final_stats['total_requests']}")
    print(f"   命中率: {final_stats['hit_rate']:.2%}")
    print(f"   L1命中: {final_stats['l1_hits']}")
    print(f"   L2命中: {final_stats['l2_hits']}")
    print(f"   未命中: {final_stats['misses']}")
    
    return True

if __name__ == '__main__':
    try:
        test_tiered_cache()
        print("\n✅ 分层缓存测试完成!")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()