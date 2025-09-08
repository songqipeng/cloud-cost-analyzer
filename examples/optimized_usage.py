#!/usr/bin/env python3
"""
优化功能使用示例
展示如何使用新的缓存、异步、监控、日志等功能
"""
import asyncio
import json
from datetime import datetime, timedelta

from cloud_cost_analyzer.core.enhanced_async_analyzer import (
    EnhancedAsyncMultiCloudAnalyzer, 
    analyze_multi_cloud_async
)
from cloud_cost_analyzer.cache.tiered_cache import initialize_cache, get_tiered_cache
from cloud_cost_analyzer.utils.secure_logger import get_secure_logger, mask_sensitive_data
from cloud_cost_analyzer.utils.retry import retry_manager
from cloud_cost_analyzer.monitoring import initialize_metrics, get_metrics_collector


async def main():
    """主函数演示各种优化功能"""
    
    # 1. 初始化安全日志系统
    logger = get_secure_logger('optimized_example')
    logger.info("Starting optimized cloud cost analysis example")
    
    # 2. 加载配置
    with open('config.optimized.json', 'r') as f:
        config = json.load(f)
    
    # 3. 初始化缓存系统
    cache = initialize_cache(config)
    logger.info("Tiered cache system initialized")
    
    # 4. 初始化监控系统
    metrics = initialize_metrics(config.get('monitoring', {}))
    logger.info("Metrics collection started")
    
    # 5. 演示敏感数据脱敏
    sensitive_data = {
        'aws_access_key': 'AKIAIOSFODNN7EXAMPLE',
        'aws_secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        'user_info': {
            'email': 'user@example.com',
            'phone': '13812345678'
        }
    }
    
    masked_data = mask_sensitive_data(sensitive_data)
    logger.info(f"Masked sensitive data: {masked_data}")
    
    # 6. 演示异步多云分析
    logger.info("Starting async multi-cloud analysis")
    
    try:
        # 使用上下文管理器确保资源正确清理
        async with EnhancedAsyncMultiCloudAnalyzer(config=config) as analyzer:
            
            # 记录分析操作指标
            with metrics.time_operation('multi_cloud_analysis', {'method': 'async'}):
                result = await analyzer.analyze_multi_cloud_async(
                    providers=['aws', 'aliyun', 'tencent'],
                    start_date='2024-01-01',
                    end_date='2024-01-31'
                )
            
            logger.info("Multi-cloud analysis completed successfully")
            
            # 记录业务指标
            metrics.business_collector.record_cost_analysis(
                provider='multi',
                total_cost=result['summary']['total_cost'],
                service_count=result['summary']['provider_count'],
                analysis_duration=result['summary']['analysis_duration']
            )
            
            # 7. 演示缓存统计
            cache_stats = cache.get_stats()
            logger.info(f"Cache statistics: {cache_stats}")
            
            # 8. 演示连接状态测试
            logger.info("Testing all provider connections")
            connections = await analyzer.test_all_connections_async()
            for provider, (status, message) in connections.items():
                logger.info(f"{provider}: {'✅' if status else '❌'} {message}")
                
                # 记录连接测试指标
                metrics.business_collector.record_api_call(
                    provider=provider,
                    operation='connection_test',
                    duration=0.2,  # 模拟耗时
                    success=status
                )
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        metrics.error_collector.record_error(
            error_type=type(e).__name__,
            context='multi_cloud_analysis'
        )
    
    # 9. 演示重试机制
    logger.info("Demonstrating retry mechanism")
    
    @retry_manager.retry_with_strategy('cloud_api')
    def unreliable_operation():
        import random
        if random.random() < 0.7:  # 70% 失败率
            raise ConnectionError("Simulated connection failure")
        return "Operation successful"
    
    try:
        result = unreliable_operation()
        logger.info(f"Retry operation result: {result}")
    except Exception as e:
        logger.error(f"Retry operation failed: {e}")
    
    # 10. 演示批量分析
    logger.info("Demonstrating batch analysis")
    
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
        }
    ]
    
    # 使用便捷函数进行批量分析
    from cloud_cost_analyzer.core.enhanced_async_analyzer import batch_analyze_async
    
    try:
        batch_results = await batch_analyze_async(batch_requests, config)
        logger.info(f"Batch analysis completed: {len(batch_results)} results")
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
    
    # 11. 展示监控和健康状态
    logger.info("Getting system health status")
    health = metrics.get_health_status()
    logger.info(f"System health: {health['status']}")
    
    for check_name, check_result in health['checks'].items():
        status_emoji = '✅' if check_result['status'] == 'ok' else '⚠️' if check_result['status'] == 'warning' else '❌'
        logger.info(f"{check_name}: {status_emoji} {check_result['value']}")
    
    # 12. 导出指标
    logger.info("Exporting metrics to file")
    metrics.export_metrics_to_file('metrics_export.json')
    
    # 13. 展示最终统计
    final_stats = {
        'cache_stats': cache.get_stats(),
        'metrics_summary': metrics.get_metrics_summary(),
        'health_status': health
    }
    
    logger.info("=== Final Statistics ===")
    logger.info(f"Cache hit rate: {final_stats['cache_stats']['hit_rate']:.2%}")
    logger.info(f"Total metrics collected: {sum(final_stats['metrics_summary']['metrics_count'].values())}")
    logger.info(f"Overall system health: {final_stats['health_status']['status']}")
    
    # 14. 清理资源
    logger.info("Cleaning up resources")
    metrics.stop()
    logger.info("Optimization example completed successfully")


# 同步版本示例
def sync_example():
    """同步版本的优化功能示例"""
    logger = get_secure_logger('sync_example')
    
    # 使用熔断器保护
    from cloud_cost_analyzer.utils.retry import CircuitBreaker
    
    circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=60)
    
    for i in range(5):
        try:
            with circuit_breaker:
                logger.info(f"Attempt {i + 1}")
                # 模拟可能失败的操作
                import random
                if random.random() < 0.8:  # 80% 失败率
                    raise ConnectionError(f"Connection failed on attempt {i + 1}")
                logger.info("Operation succeeded")
                break
        except Exception as e:
            logger.warning(f"Attempt {i + 1} failed: {e}")


if __name__ == '__main__':
    print("🚀 Cloud Cost Analyzer Optimization Demo")
    print("=" * 50)
    
    # 运行异步示例
    print("\n📊 Running async optimization example...")
    asyncio.run(main())
    
    print("\n🔄 Running sync optimization example...")
    sync_example()
    
    print("\n✅ All examples completed!")
    print("\nFiles generated:")
    print("- metrics_export.json (监控指标导出)")
    print("- logs/ (日志文件)")
    print("- .cache/ (缓存文件)")