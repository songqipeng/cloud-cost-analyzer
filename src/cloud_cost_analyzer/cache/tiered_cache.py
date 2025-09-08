"""
分层缓存系统
提供内存、文件、Redis三级缓存机制以优化性能
"""
import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor

from cloud_cost_analyzer.core.base import CacheProvider
from cloud_cost_analyzer.cache.providers import MemoryCache, FileCache, RedisCache
from cloud_cost_analyzer.utils.logger import get_logger
from cloud_cost_analyzer.utils.exceptions import CacheError

logger = get_logger()


class TieredCache:
    """
    分层缓存管理器
    
    实现三级缓存策略:
    1. L1 - 内存缓存: 最快，容量有限，优先查找
    2. L2 - 文件缓存: 中等速度，持久化存储
    3. L3 - Redis缓存: 网络访问，支持分布式
    
    查找策略: L1 -> L2 -> L3
    写入策略: 同时写入所有可用层级
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化分层缓存
        
        Args:
            config: 缓存配置
        """
        self.config = config
        self.cache_config = config.get('cache', {})
        
        # 初始化各层缓存
        self.l1_cache = None  # 内存缓存
        self.l2_cache = None  # 文件缓存  
        self.l3_cache = None  # Redis缓存
        
        # 统计信息
        self.stats = {
            'l1_hits': 0,
            'l2_hits': 0, 
            'l3_hits': 0,
            'misses': 0,
            'writes': 0,
            'errors': 0
        }
        
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="cache")
        
        self._initialize_caches()
        
    def _initialize_caches(self):
        """初始化各级缓存"""
        try:
            # L1: 内存缓存 (默认启用)
            if self.cache_config.get('l1_enabled', True):
                l1_config = self.cache_config.get('l1', {})
                self.l1_cache = MemoryCache(
                    max_size=l1_config.get('max_size', 500),
                    default_ttl=l1_config.get('default_ttl', 300)  # 5分钟
                )
                logger.info("L1 (Memory) cache initialized")
            
            # L2: 文件缓存 (默认启用)
            if self.cache_config.get('l2_enabled', True):
                l2_config = self.cache_config.get('l2', {})
                self.l2_cache = FileCache(
                    cache_dir=l2_config.get('cache_dir', '.cache'),
                    default_ttl=l2_config.get('default_ttl', 3600)  # 1小时
                )
                logger.info("L2 (File) cache initialized")
            
            # L3: Redis缓存 (可选)
            if self.cache_config.get('l3_enabled', False):
                try:
                    l3_config = self.cache_config.get('l3', {})
                    self.l3_cache = RedisCache(
                        host=l3_config.get('host', 'localhost'),
                        port=l3_config.get('port', 6379),
                        db=l3_config.get('db', 0),
                        password=l3_config.get('password'),
                        default_ttl=l3_config.get('default_ttl', 7200),  # 2小时
                        key_prefix=l3_config.get('key_prefix', 'cloud_cost:')
                    )
                    logger.info("L3 (Redis) cache initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize L3 (Redis) cache: {e}")
                    
        except Exception as e:
            logger.error(f"Cache initialization error: {e}")
            
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值 (L1 -> L2 -> L3)
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值或None
        """
        with self._lock:
            # L1: 内存缓存
            if self.l1_cache:
                value = self.l1_cache.get(key)
                if value is not None:
                    self.stats['l1_hits'] += 1
                    logger.debug(f"L1 cache hit for key: {key[:50]}...")
                    return value
            
            # L2: 文件缓存
            if self.l2_cache:
                value = self.l2_cache.get(key)
                if value is not None:
                    self.stats['l2_hits'] += 1
                    logger.debug(f"L2 cache hit for key: {key[:50]}...")
                    # 回写到L1
                    if self.l1_cache:
                        self.l1_cache.set(key, value, ttl=300)
                    return value
            
            # L3: Redis缓存
            if self.l3_cache:
                try:
                    value = self.l3_cache.get(key)
                    if value is not None:
                        self.stats['l3_hits'] += 1
                        logger.debug(f"L3 cache hit for key: {key[:50]}...")
                        # 回写到L1和L2
                        self._write_back_to_upper_tiers(key, value)
                        return value
                except Exception as e:
                    logger.warning(f"L3 cache get error for key {key}: {e}")
                    self.stats['errors'] += 1
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值 (写入所有可用层级)
        
        Args:
            key: 缓存键
            value: 缓存值  
            ttl: 生存时间（秒）
            
        Returns:
            是否成功
        """
        success = True
        
        with self._lock:
            self.stats['writes'] += 1
            
            # 为不同层级设置不同的TTL
            l1_ttl = min(ttl or 300, 300) if ttl else 300  # L1最多5分钟
            l2_ttl = ttl or 3600  # L2默认1小时
            l3_ttl = ttl or 7200  # L3默认2小时
            
            # L1: 内存缓存
            if self.l1_cache:
                try:
                    if not self.l1_cache.set(key, value, l1_ttl):
                        success = False
                except Exception as e:
                    logger.warning(f"L1 cache set error for key {key}: {e}")
                    self.stats['errors'] += 1
                    success = False
            
            # L2: 文件缓存 (异步写入)
            if self.l2_cache:
                try:
                    self._executor.submit(self._set_l2_async, key, value, l2_ttl)
                except Exception as e:
                    logger.warning(f"L2 cache async set error for key {key}: {e}")
                    self.stats['errors'] += 1
            
            # L3: Redis缓存 (异步写入)
            if self.l3_cache:
                try:
                    self._executor.submit(self._set_l3_async, key, value, l3_ttl)
                except Exception as e:
                    logger.warning(f"L3 cache async set error for key {key}: {e}")
                    self.stats['errors'] += 1
            
        return success
    
    def delete(self, key: str) -> bool:
        """
        删除缓存值 (所有层级)
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功
        """
        success = True
        
        with self._lock:
            # 删除所有层级的缓存
            for cache, name in [(self.l1_cache, 'L1'), (self.l2_cache, 'L2'), (self.l3_cache, 'L3')]:
                if cache:
                    try:
                        cache.delete(key)
                    except Exception as e:
                        logger.warning(f"{name} cache delete error for key {key}: {e}")
                        self.stats['errors'] += 1
                        success = False
        
        return success
    
    def clear(self, provider: Optional[str] = None) -> bool:
        """
        清空缓存
        
        Args:
            provider: 指定云服务提供商，如果为None则清空所有缓存
            
        Returns:
            是否成功
        """
        success = True
        
        with self._lock:
            for cache, name in [(self.l1_cache, 'L1'), (self.l2_cache, 'L2'), (self.l3_cache, 'L3')]:
                if cache:
                    try:
                        if provider:
                            # 只清除特定提供商的缓存（简化实现）
                            logger.info(f"Provider-specific clear not implemented for {name}")
                        else:
                            cache.clear()
                        logger.info(f"{name} cache cleared")
                    except Exception as e:
                        logger.warning(f"{name} cache clear error: {e}")
                        self.stats['errors'] += 1
                        success = False
        
        return success
    
    def _write_back_to_upper_tiers(self, key: str, value: Any):
        """将值回写到上层缓存"""
        try:
            if self.l2_cache:
                self.l2_cache.set(key, value, ttl=3600)
            if self.l1_cache:
                self.l1_cache.set(key, value, ttl=300)
        except Exception as e:
            logger.warning(f"Write-back error for key {key}: {e}")
    
    def _set_l2_async(self, key: str, value: Any, ttl: int):
        """异步设置L2缓存"""
        try:
            self.l2_cache.set(key, value, ttl)
        except Exception as e:
            logger.warning(f"L2 async set error for key {key}: {e}")
            self.stats['errors'] += 1
    
    def _set_l3_async(self, key: str, value: Any, ttl: int):
        """异步设置L3缓存"""
        try:
            self.l3_cache.set(key, value, ttl)
        except Exception as e:
            logger.warning(f"L3 async set error for key {key}: {e}")
            self.stats['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        with self._lock:
            total_requests = sum([
                self.stats['l1_hits'], 
                self.stats['l2_hits'], 
                self.stats['l3_hits'], 
                self.stats['misses']
            ])
            
            hit_rate = 0.0
            if total_requests > 0:
                hit_rate = (self.stats['l1_hits'] + self.stats['l2_hits'] + self.stats['l3_hits']) / total_requests
            
            stats = {
                'total_requests': total_requests,
                'hit_rate': hit_rate,
                'l1_hit_rate': self.stats['l1_hits'] / total_requests if total_requests > 0 else 0,
                'l2_hit_rate': self.stats['l2_hits'] / total_requests if total_requests > 0 else 0,
                'l3_hit_rate': self.stats['l3_hits'] / total_requests if total_requests > 0 else 0,
                'miss_rate': self.stats['misses'] / total_requests if total_requests > 0 else 0,
                'writes': self.stats['writes'],
                'errors': self.stats['errors'],
                'caches_available': {
                    'l1_memory': self.l1_cache is not None,
                    'l2_file': self.l2_cache is not None,
                    'l3_redis': self.l3_cache is not None
                }
            }
            
            return stats
    
    def cleanup_expired(self) -> Dict[str, int]:
        """
        清理过期缓存
        
        Returns:
            各级缓存清理的条目数
        """
        results = {}
        
        try:
            # L2文件缓存支持过期清理
            if self.l2_cache and hasattr(self.l2_cache, 'cleanup_expired'):
                results['l2_cleaned'] = self.l2_cache.cleanup_expired()
                logger.info(f"L2 cache cleaned: {results['l2_cleaned']} items")
        except Exception as e:
            logger.warning(f"L2 cache cleanup error: {e}")
            results['l2_cleaned'] = 0
        
        return results
    
    def is_healthy(self) -> Dict[str, bool]:
        """
        检查各级缓存健康状态
        
        Returns:
            各级缓存的健康状态
        """
        health = {}
        
        # L1健康检查
        if self.l1_cache:
            try:
                test_key = f"_health_check_{int(time.time())}"
                self.l1_cache.set(test_key, "test", ttl=1)
                health['l1_healthy'] = self.l1_cache.get(test_key) == "test"
                self.l1_cache.delete(test_key)
            except Exception:
                health['l1_healthy'] = False
        else:
            health['l1_healthy'] = None
        
        # L2健康检查
        if self.l2_cache:
            try:
                test_key = f"_health_check_{int(time.time())}"
                self.l2_cache.set(test_key, "test", ttl=1)
                health['l2_healthy'] = self.l2_cache.get(test_key) == "test"
                self.l2_cache.delete(test_key)
            except Exception:
                health['l2_healthy'] = False
        else:
            health['l2_healthy'] = None
        
        # L3健康检查
        if self.l3_cache:
            try:
                test_key = f"_health_check_{int(time.time())}"
                self.l3_cache.set(test_key, "test", ttl=1)
                health['l3_healthy'] = self.l3_cache.get(test_key) == "test"
                self.l3_cache.delete(test_key)
            except Exception:
                health['l3_healthy'] = False
        else:
            health['l3_healthy'] = None
        
        return health
    
    def shutdown(self):
        """关闭缓存管理器"""
        try:
            self._executor.shutdown(wait=True, timeout=5)
        except Exception as e:
            logger.warning(f"Cache shutdown error: {e}")


class CacheKeyGenerator:
    """缓存键生成器"""
    
    @staticmethod
    def generate_cost_data_key(provider: str, start_date: str, end_date: str, 
                             service: Optional[str] = None, region: Optional[str] = None) -> str:
        """
        生成费用数据缓存键
        
        Args:
            provider: 云服务提供商
            start_date: 开始日期
            end_date: 结束日期
            service: 服务名称（可选）
            region: 地区（可选）
            
        Returns:
            缓存键
        """
        parts = ['cost_data', provider, start_date, end_date]
        
        if service:
            parts.append(f"service_{service}")
        if region:
            parts.append(f"region_{region}")
            
        return ":".join(parts)
    
    @staticmethod
    def generate_analysis_key(provider: str, analysis_type: str, 
                            params: Dict[str, Any]) -> str:
        """
        生成分析结果缓存键
        
        Args:
            provider: 云服务提供商
            analysis_type: 分析类型
            params: 分析参数
            
        Returns:
            缓存键
        """
        # 对参数进行排序以确保一致性
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        import hashlib
        params_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:8]
        
        return f"analysis:{provider}:{analysis_type}:{params_hash}"
    
    @staticmethod
    def generate_connection_status_key(provider: str) -> str:
        """
        生成连接状态缓存键
        
        Args:
            provider: 云服务提供商
            
        Returns:
            缓存键
        """
        return f"connection_status:{provider}"


# 全局分层缓存实例
_tiered_cache: Optional[TieredCache] = None


def get_tiered_cache(config: Optional[Dict[str, Any]] = None) -> TieredCache:
    """
    获取全局分层缓存实例
    
    Args:
        config: 缓存配置
        
    Returns:
        分层缓存实例
    """
    global _tiered_cache
    
    if _tiered_cache is None:
        if config is None:
            config = {'cache': {'l1_enabled': True, 'l2_enabled': True}}
        _tiered_cache = TieredCache(config)
    
    return _tiered_cache


def initialize_cache(config: Dict[str, Any]) -> TieredCache:
    """
    初始化全局缓存
    
    Args:
        config: 缓存配置
        
    Returns:
        分层缓存实例
    """
    global _tiered_cache
    _tiered_cache = TieredCache(config)
    return _tiered_cache