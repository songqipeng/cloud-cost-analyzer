"""
智能缓存管理器
"""
import json
import hashlib
import pickle
import asyncio
import aiofiles
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..utils.logger import get_logger
from ..utils.security import SecurityManager

logger = get_logger()


class CacheLevel(Enum):
    """缓存级别"""
    MEMORY = "memory"
    REDIS = "redis"
    FILE = "file"


@dataclass
class CacheConfig:
    """缓存配置"""
    memory_ttl: int = 300  # 内存缓存5分钟
    redis_ttl: int = 3600  # Redis缓存1小时
    file_ttl: int = 86400  # 文件缓存24小时
    max_memory_size: int = 100  # 最大内存缓存条目数
    cache_dir: str = ".cache"
    redis_url: Optional[str] = None
    enable_compression: bool = True


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.now() > self.expires_at
    
    def touch(self) -> None:
        """更新访问时间"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class MemoryCache:
    """内存缓存"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.security_manager = SecurityManager()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        if entry.is_expired():
            del self.cache[key]
            return None
        
        entry.touch()
        return entry.value
    
    def set(self, key: str, value: Any, ttl: int) -> None:
        """设置缓存值"""
        # 检查缓存大小限制
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
        
        expires_at = datetime.now() + timedelta(seconds=ttl)
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        self.cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
    
    def _evict_lru(self) -> None:
        """淘汰最近最少使用的条目"""
        if not self.cache:
            return
        
        # 找到最近最少使用的条目
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed)
        del self.cache[lru_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "max_size": self.max_size,
            "usage_percentage": (total_entries / self.max_size) * 100
        }


class FileCache:
    """文件缓存"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.security_manager = SecurityManager()
    
    def _get_file_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用哈希避免文件名冲突
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            return None
        
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                data = await f.read()
            
            entry = pickle.loads(data)
            
            if entry.is_expired():
                file_path.unlink()  # 删除过期文件
                return None
            
            entry.touch()
            
            # 更新文件中的访问信息
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(pickle.dumps(entry))
            
            return entry.value
            
        except Exception as e:
            logger.error(f"文件缓存读取失败 {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int) -> None:
        """设置缓存值"""
        file_path = self._get_file_path(key)
        
        try:
            expires_at = datetime.now() + timedelta(seconds=ttl)
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at
            )
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(pickle.dumps(entry))
                
        except Exception as e:
            logger.error(f"文件缓存写入失败 {key}: {e}")
    
    async def delete(self, key: str) -> bool:
        """删除缓存条目"""
        file_path = self._get_file_path(key)
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    async def clear(self) -> None:
        """清空缓存"""
        for file_path in self.cache_dir.glob("*.cache"):
            file_path.unlink()
    
    async def cleanup_expired(self) -> int:
        """清理过期文件"""
        cleaned_count = 0
        
        for file_path in self.cache_dir.glob("*.cache"):
            try:
                async with aiofiles.open(file_path, 'rb') as f:
                    data = await f.read()
                
                entry = pickle.loads(data)
                
                if entry.is_expired():
                    file_path.unlink()
                    cleaned_count += 1
                    
            except Exception as e:
                logger.error(f"清理过期缓存文件失败 {file_path}: {e}")
                # 删除损坏的文件
                file_path.unlink()
                cleaned_count += 1
        
        return cleaned_count


class RedisCache:
    """Redis缓存"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis不可用，请安装redis包")
        
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.security_manager = SecurityManager()
    
    async def connect(self) -> None:
        """连接Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=False)
            await self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.redis_client = None
    
    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(key)
            if data is None:
                return None
            
            entry = pickle.loads(data)
            
            if entry.is_expired():
                await self.redis_client.delete(key)
                return None
            
            entry.touch()
            
            # 更新访问信息
            await self.redis_client.set(key, pickle.dumps(entry), ex=entry.expires_at)
            
            return entry.value
            
        except Exception as e:
            logger.error(f"Redis缓存读取失败 {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int) -> None:
        """设置缓存值"""
        if not self.redis_client:
            return
        
        try:
            expires_at = datetime.now() + timedelta(seconds=ttl)
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at
            )
            
            await self.redis_client.set(key, pickle.dumps(entry), ex=ttl)
            
        except Exception as e:
            logger.error(f"Redis缓存写入失败 {key}: {e}")
    
    async def delete(self, key: str) -> bool:
        """删除缓存条目"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis缓存删除失败 {key}: {e}")
            return False
    
    async def clear(self) -> None:
        """清空缓存"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Redis缓存清空失败: {e}")


class CacheManager:
    """智能缓存管理器"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.memory_cache = MemoryCache(self.config.max_memory_size)
        self.file_cache = FileCache(self.config.cache_dir)
        self.redis_cache = None
        
        if REDIS_AVAILABLE and self.config.redis_url:
            self.redis_cache = RedisCache(self.config.redis_url)
        
        self.security_manager = SecurityManager()
    
    async def initialize(self) -> None:
        """初始化缓存管理器"""
        if self.redis_cache:
            await self.redis_cache.connect()
        
        # 启动定期清理任务
        asyncio.create_task(self._periodic_cleanup())
    
    async def shutdown(self) -> None:
        """关闭缓存管理器"""
        if self.redis_cache:
            await self.redis_cache.disconnect()
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数序列化为字符串
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str, level: Optional[CacheLevel] = None) -> Optional[Any]:
        """获取缓存值"""
        # 如果指定了缓存级别，只从该级别获取
        if level:
            return await self._get_from_level(key, level)
        
        # 否则按优先级获取：内存 -> Redis -> 文件
        for cache_level in [CacheLevel.MEMORY, CacheLevel.REDIS, CacheLevel.FILE]:
            value = await self._get_from_level(key, cache_level)
            if value is not None:
                # 将值提升到更高级别的缓存
                await self._promote_to_higher_levels(key, value, cache_level)
                return value
        
        return None
    
    async def _get_from_level(self, key: str, level: CacheLevel) -> Optional[Any]:
        """从指定级别获取缓存"""
        if level == CacheLevel.MEMORY:
            return self.memory_cache.get(key)
        elif level == CacheLevel.REDIS and self.redis_cache:
            return await self.redis_cache.get(key)
        elif level == CacheLevel.FILE:
            return await self.file_cache.get(key)
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                 level: Optional[CacheLevel] = None) -> None:
        """设置缓存值"""
        if level:
            # 设置到指定级别
            await self._set_to_level(key, value, ttl, level)
        else:
            # 设置到所有级别
            for cache_level in [CacheLevel.MEMORY, CacheLevel.REDIS, CacheLevel.FILE]:
                await self._set_to_level(key, value, ttl, cache_level)
    
    async def _set_to_level(self, key: str, value: Any, ttl: Optional[int], level: CacheLevel) -> None:
        """设置到指定级别"""
        if ttl is None:
            ttl = self._get_default_ttl(level)
        
        if level == CacheLevel.MEMORY:
            self.memory_cache.set(key, value, ttl)
        elif level == CacheLevel.REDIS and self.redis_cache:
            await self.redis_cache.set(key, value, ttl)
        elif level == CacheLevel.FILE:
            await self.file_cache.set(key, value, ttl)
    
    def _get_default_ttl(self, level: CacheLevel) -> int:
        """获取默认TTL"""
        if level == CacheLevel.MEMORY:
            return self.config.memory_ttl
        elif level == CacheLevel.REDIS:
            return self.config.redis_ttl
        elif level == CacheLevel.FILE:
            return self.config.file_ttl
        return 3600
    
    async def _promote_to_higher_levels(self, key: str, value: Any, current_level: CacheLevel) -> None:
        """将缓存值提升到更高级别"""
        if current_level == CacheLevel.FILE:
            # 从文件提升到Redis和内存
            if self.redis_cache:
                await self.redis_cache.set(key, value, self.config.redis_ttl)
            self.memory_cache.set(key, value, self.config.memory_ttl)
        elif current_level == CacheLevel.REDIS:
            # 从Redis提升到内存
            self.memory_cache.set(key, value, self.config.memory_ttl)
    
    async def delete(self, key: str) -> bool:
        """删除缓存条目"""
        deleted = False
        
        # 从所有级别删除
        if self.memory_cache.delete(key):
            deleted = True
        
        if self.redis_cache and await self.redis_cache.delete(key):
            deleted = True
        
        if await self.file_cache.delete(key):
            deleted = True
        
        return deleted
    
    async def clear(self) -> None:
        """清空所有缓存"""
        self.memory_cache.clear()
        
        if self.redis_cache:
            await self.redis_cache.clear()
        
        await self.file_cache.clear()
    
    async def get_or_set(self, key: str, fetch_func, ttl: Optional[int] = None, 
                        level: Optional[CacheLevel] = None) -> Any:
        """获取缓存值，如果不存在则调用函数获取并缓存"""
        # 尝试从缓存获取
        cached_value = await self.get(key, level)
        if cached_value is not None:
            return cached_value
        
        # 缓存未命中，调用函数获取
        try:
            if asyncio.iscoroutinefunction(fetch_func):
                value = await fetch_func()
            else:
                value = fetch_func()
            
            # 缓存结果
            await self.set(key, value, ttl, level)
            return value
            
        except Exception as e:
            logger.error(f"获取缓存值失败 {key}: {e}")
            raise
    
    async def _periodic_cleanup(self) -> None:
        """定期清理过期缓存"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时清理一次
                
                # 清理文件缓存
                cleaned_files = await self.file_cache.cleanup_expired()
                if cleaned_files > 0:
                    logger.info(f"清理了 {cleaned_files} 个过期文件缓存")
                
            except Exception as e:
                logger.error(f"定期清理任务失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            "memory": self.memory_cache.get_stats(),
            "file": {"cache_dir": str(self.file_cache.cache_dir)},
            "redis": {"available": self.redis_cache is not None}
        }
        
        if self.redis_cache:
            stats["redis"]["connected"] = self.redis_cache.redis_client is not None
        
        return stats
