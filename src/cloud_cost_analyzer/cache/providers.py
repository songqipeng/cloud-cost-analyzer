"""
缓存提供商实现
"""
import json
import os
import pickle
import hashlib
import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from cloud_cost_analyzer.core.base import CacheProvider
from cloud_cost_analyzer.utils.exceptions import CacheError
from cloud_cost_analyzer.utils.logger import get_logger

logger = get_logger()


class MemoryCache(CacheProvider):
    """内存缓存提供商"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认TTL（秒）
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # 检查是否过期
            if entry['expires_at'] and time.time() > entry['expires_at']:
                del self._cache[key]
                return None
            
            # 更新访问时间
            entry['accessed_at'] = time.time()
            
            return entry['value']
        except Exception as e:
            logger.warning(f"Failed to get cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            # 如果缓存已满，移除最久未访问的条目
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl if ttl > 0 else None
            
            self._cache[key] = {
                'value': value,
                'created_at': time.time(),
                'accessed_at': time.time(),
                'expires_at': expires_at,
                'ttl': ttl
            }
            
            return True
        except Exception as e:
            logger.warning(f"Failed to set cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to delete cache key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            self._cache.clear()
            return True
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self.get(key) is not None
    
    def _evict_lru(self) -> None:
        """移除最久未访问的条目"""
        if not self._cache:
            return
        
        # 找到访问时间最早的条目
        lru_key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k]['accessed_at'])
        del self._cache[lru_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'default_ttl': self.default_ttl
        }


class FileCache(CacheProvider):
    """文件缓存提供商"""
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: int = 3600):
        """
        初始化文件缓存
        
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认TTL（秒）
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        
        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            cache_file = self._get_cache_file(key)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'rb') as f:
                entry = pickle.load(f)
            
            # 检查是否过期
            if entry['expires_at'] and time.time() > entry['expires_at']:
                os.remove(cache_file)
                return None
            
            return entry['value']
        except Exception as e:
            logger.warning(f"Failed to get cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            cache_file = self._get_cache_file(key)
            
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl if ttl > 0 else None
            
            entry = {
                'value': value,
                'created_at': time.time(),
                'expires_at': expires_at,
                'ttl': ttl
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
            
            return True
        except Exception as e:
            logger.warning(f"Failed to set cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to delete cache key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, filename))
            return True
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self.get(key) is not None
    
    def _get_cache_file(self, key: str) -> str:
        """获取缓存文件路径"""
        # 使用MD5哈希作为文件名，避免特殊字符问题
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.cache")
    
    def cleanup_expired(self) -> int:
        """清理过期的缓存文件"""
        cleaned = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.cache'):
                    continue
                
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'rb') as f:
                        entry = pickle.load(f)
                    
                    if entry['expires_at'] and time.time() > entry['expires_at']:
                        os.remove(filepath)
                        cleaned += 1
                except Exception:
                    # 如果文件损坏，也删除
                    os.remove(filepath)
                    cleaned += 1
        except Exception as e:
            logger.warning(f"Failed to cleanup expired cache: {e}")
        
        return cleaned


class RedisCache(CacheProvider):
    """Redis缓存提供商"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None, 
                 default_ttl: int = 3600, key_prefix: str = 'cloud_cost:'):
        """
        初始化Redis缓存
        
        Args:
            host: Redis主机
            port: Redis端口
            db: Redis数据库编号
            password: Redis密码
            default_ttl: 默认TTL（秒）
            key_prefix: 键前缀
        """
        if not REDIS_AVAILABLE:
            raise CacheError("Redis not available. Please install redis-py: pip install redis")
        
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,  # 保持bytes格式以支持pickle
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=30
            )
            
            # 测试连接
            self.client.ping()
        except Exception as e:
            raise CacheError(f"Failed to connect to Redis: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            full_key = self._get_full_key(key)
            data = self.client.get(full_key)
            
            if data is None:
                return None
            
            return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Failed to get cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            full_key = self._get_full_key(key)
            data = pickle.dumps(value)
            ttl = ttl or self.default_ttl
            
            if ttl > 0:
                return self.client.setex(full_key, ttl, data)
            else:
                return self.client.set(full_key, data)
        except Exception as e:
            logger.warning(f"Failed to set cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            full_key = self._get_full_key(key)
            return self.client.delete(full_key) > 0
        except Exception as e:
            logger.warning(f"Failed to delete cache key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """清空缓存（仅清空带前缀的键）"""
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys) > 0
            return True
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            full_key = self._get_full_key(key)
            return self.client.exists(full_key) > 0
        except Exception as e:
            logger.warning(f"Failed to check cache key {key}: {e}")
            return False
    
    def _get_full_key(self, key: str) -> str:
        """获取完整键名"""
        return f"{self.key_prefix}{key}"
    
    def get_info(self) -> Dict[str, Any]:
        """获取Redis信息"""
        try:
            return self.client.info()
        except Exception as e:
            logger.warning(f"Failed to get Redis info: {e}")
            return {}


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化缓存管理器
        
        Args:
            config: 缓存配置
        """
        self.config = config
        self.provider = self._create_provider()
        
    def _create_provider(self) -> CacheProvider:
        """创建缓存提供商"""
        cache_config = self.config.get('cache', {})
        provider_type = cache_config.get('type', 'memory').lower()
        
        if provider_type == 'redis' and REDIS_AVAILABLE:
            redis_config = cache_config.get('redis', {})
            return RedisCache(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                password=redis_config.get('password'),
                default_ttl=cache_config.get('default_ttl', 3600),
                key_prefix=redis_config.get('key_prefix', 'cloud_cost:')
            )
        elif provider_type == 'file':
            file_config = cache_config.get('file', {})
            return FileCache(
                cache_dir=file_config.get('cache_dir', '.cache'),
                default_ttl=cache_config.get('default_ttl', 3600)
            )
        else:
            # 默认使用内存缓存
            memory_config = cache_config.get('memory', {})
            return MemoryCache(
                max_size=memory_config.get('max_size', 1000),
                default_ttl=cache_config.get('default_ttl', 3600)
            )
    
    def generate_cache_key(self, provider: str, operation: str, 
                          params: Dict[str, Any]) -> str:
        """
        生成缓存键
        
        Args:
            provider: 云服务提供商
            operation: 操作类型
            params: 参数字典
            
        Returns:
            缓存键
        """
        # 对参数进行排序以确保一致性
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        
        # 生成哈希值
        content = f"{provider}:{operation}:{sorted_params}"
        hash_value = hashlib.md5(content.encode()).hexdigest()
        
        return f"{provider}:{operation}:{hash_value}"
    
    def get_cost_data(self, provider: str, start_date: str, end_date: str) -> Optional[Any]:
        """获取费用数据缓存"""
        cache_key = self.generate_cache_key(provider, 'cost_data', {
            'start_date': start_date,
            'end_date': end_date
        })
        return self.provider.get(cache_key)
    
    def set_cost_data(self, provider: str, start_date: str, end_date: str, 
                     data: Any, ttl: Optional[int] = None) -> bool:
        """设置费用数据缓存"""
        cache_key = self.generate_cache_key(provider, 'cost_data', {
            'start_date': start_date,
            'end_date': end_date
        })
        
        # 对于费用数据，默认缓存6小时
        ttl = ttl or 21600
        return self.provider.set(cache_key, data, ttl)
    
    def get_analysis_result(self, provider: str, analysis_params: Dict[str, Any]) -> Optional[Any]:
        """获取分析结果缓存"""
        cache_key = self.generate_cache_key(provider, 'analysis', analysis_params)
        return self.provider.get(cache_key)
    
    def set_analysis_result(self, provider: str, analysis_params: Dict[str, Any], 
                           result: Any, ttl: Optional[int] = None) -> bool:
        """设置分析结果缓存"""
        cache_key = self.generate_cache_key(provider, 'analysis', analysis_params)
        
        # 对于分析结果，默认缓存1小时
        ttl = ttl or 3600
        return self.provider.set(cache_key, result, ttl)
    
    def clear_provider_cache(self, provider: str) -> bool:
        """清空特定提供商的缓存"""
        # 注意：这个实现比较简单，实际使用中可能需要更复杂的模式匹配
        return self.provider.clear()
    
    def is_enabled(self) -> bool:
        """检查缓存是否启用"""
        return self.config.get('cache', {}).get('enabled', True)