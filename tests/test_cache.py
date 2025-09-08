"""
缓存模块测试
"""
import pytest
import asyncio
import tempfile
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from cloud_cost_analyzer.cache.manager import (
    CacheConfig, CacheEntry, MemoryCache, FileCache, 
    RedisCache, CacheManager, CacheLevel
)


class TestCacheConfig:
    """缓存配置测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = CacheConfig()
        
        assert config.memory_ttl == 300
        assert config.redis_ttl == 3600
        assert config.file_ttl == 86400
        assert config.max_memory_size == 100
        assert config.cache_dir == ".cache"
        assert config.redis_url is None
        assert config.enable_compression is True
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = CacheConfig(
            memory_ttl=600,
            redis_ttl=7200,
            file_ttl=172800,
            max_memory_size=200,
            cache_dir="/tmp/cache",
            redis_url="redis://localhost:6379/1",
            enable_compression=False
        )
        
        assert config.memory_ttl == 600
        assert config.redis_ttl == 7200
        assert config.file_ttl == 172800
        assert config.max_memory_size == 200
        assert config.cache_dir == "/tmp/cache"
        assert config.redis_url == "redis://localhost:6379/1"
        assert config.enable_compression is False


class TestCacheEntry:
    """缓存条目测试"""
    
    def test_cache_entry_creation(self):
        """测试缓存条目创建"""
        now = datetime.now()
        expires_at = now + timedelta(seconds=300)
        
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=now,
            expires_at=expires_at
        )
        
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.created_at == now
        assert entry.expires_at == expires_at
        assert entry.access_count == 0
        assert entry.last_accessed == now
    
    def test_cache_entry_expired(self):
        """测试缓存条目过期"""
        now = datetime.now()
        past_time = now - timedelta(seconds=300)
        
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=past_time,
            expires_at=past_time + timedelta(seconds=100)
        )
        
        assert entry.is_expired() is True
    
    def test_cache_entry_not_expired(self):
        """测试缓存条目未过期"""
        now = datetime.now()
        future_time = now + timedelta(seconds=300)
        
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=now,
            expires_at=future_time
        )
        
        assert entry.is_expired() is False
    
    def test_cache_entry_touch(self):
        """测试缓存条目访问更新"""
        now = datetime.now()
        expires_at = now + timedelta(seconds=300)
        
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=now,
            expires_at=expires_at
        )
        
        initial_access_count = entry.access_count
        initial_last_accessed = entry.last_accessed
        
        entry.touch()
        
        assert entry.access_count == initial_access_count + 1
        assert entry.last_accessed > initial_last_accessed


class TestMemoryCache:
    """内存缓存测试"""
    
    def test_memory_cache_get_set(self):
        """测试内存缓存获取和设置"""
        cache = MemoryCache(max_size=10)
        
        # 设置缓存
        cache.set("key1", "value1", 300)
        cache.set("key2", "value2", 300)
        
        # 获取缓存
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("nonexistent") is None
    
    def test_memory_cache_expiration(self):
        """测试内存缓存过期"""
        cache = MemoryCache(max_size=10)
        
        # 设置短期缓存
        cache.set("key1", "value1", 0)  # 立即过期
        
        # 获取过期缓存
        assert cache.get("key1") is None
    
    def test_memory_cache_lru_eviction(self):
        """测试内存缓存LRU淘汰"""
        cache = MemoryCache(max_size=2)
        
        # 填满缓存
        cache.set("key1", "value1", 300)
        cache.set("key2", "value2", 300)
        
        # 访问key1，使其成为最近使用的
        cache.get("key1")
        
        # 添加新条目，应该淘汰key2
        cache.set("key3", "value3", 300)
        
        assert cache.get("key1") == "value1"  # 应该还在
        assert cache.get("key2") is None      # 应该被淘汰
        assert cache.get("key3") == "value3"  # 应该存在
    
    def test_memory_cache_delete(self):
        """测试内存缓存删除"""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1", 300)
        assert cache.get("key1") == "value1"
        
        # 删除缓存
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.delete("nonexistent") is False
    
    def test_memory_cache_clear(self):
        """测试内存缓存清空"""
        cache = MemoryCache(max_size=10)
        
        cache.set("key1", "value1", 300)
        cache.set("key2", "value2", 300)
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_memory_cache_stats(self):
        """测试内存缓存统计"""
        cache = MemoryCache(max_size=10)
        
        # 添加一些缓存条目
        cache.set("key1", "value1", 300)
        cache.set("key2", "value2", 0)  # 过期条目
        
        stats = cache.get_stats()
        
        assert stats["total_entries"] == 2
        assert stats["expired_entries"] == 1
        assert stats["active_entries"] == 1
        assert stats["max_size"] == 10
        assert stats["usage_percentage"] == 20.0


class TestFileCache:
    """文件缓存测试"""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """创建临时缓存目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.mark.asyncio
    async def test_file_cache_get_set(self, temp_cache_dir):
        """测试文件缓存获取和设置"""
        cache = FileCache(temp_cache_dir)
        
        # 设置缓存
        await cache.set("key1", "value1", 300)
        await cache.set("key2", {"nested": "value"}, 300)
        
        # 获取缓存
        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") == {"nested": "value"}
        assert await cache.get("nonexistent") is None
    
    @pytest.mark.asyncio
    async def test_file_cache_expiration(self, temp_cache_dir):
        """测试文件缓存过期"""
        cache = FileCache(temp_cache_dir)
        
        # 设置立即过期的缓存
        await cache.set("key1", "value1", 0)
        
        # 获取过期缓存
        assert await cache.get("key1") is None
    
    @pytest.mark.asyncio
    async def test_file_cache_delete(self, temp_cache_dir):
        """测试文件缓存删除"""
        cache = FileCache(temp_cache_dir)
        
        await cache.set("key1", "value1", 300)
        assert await cache.get("key1") == "value1"
        
        # 删除缓存
        assert await cache.delete("key1") is True
        assert await cache.get("key1") is None
        assert await cache.delete("nonexistent") is False
    
    @pytest.mark.asyncio
    async def test_file_cache_clear(self, temp_cache_dir):
        """测试文件缓存清空"""
        cache = FileCache(temp_cache_dir)
        
        await cache.set("key1", "value1", 300)
        await cache.set("key2", "value2", 300)
        
        await cache.clear()
        
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
    
    @pytest.mark.asyncio
    async def test_file_cache_cleanup_expired(self, temp_cache_dir):
        """测试文件缓存清理过期条目"""
        cache = FileCache(temp_cache_dir)
        
        # 创建一些缓存条目
        await cache.set("key1", "value1", 300)  # 不过期
        await cache.set("key2", "value2", 0)    # 立即过期
        
        # 手动创建过期文件
        expired_file = cache._get_file_path("expired_key")
        expired_entry = CacheEntry(
            key="expired_key",
            value="expired_value",
            created_at=datetime.now() - timedelta(seconds=300),
            expires_at=datetime.now() - timedelta(seconds=100)
        )
        
        with open(expired_file, 'wb') as f:
            f.write(pickle.dumps(expired_entry))
        
        # 清理过期条目
        cleaned_count = await cache.cleanup_expired()
        
        assert cleaned_count >= 1
        assert await cache.get("key1") == "value1"  # 应该还在
        assert await cache.get("key2") is None      # 应该被清理


class TestRedisCache:
    """Redis缓存测试"""
    
    @pytest.mark.asyncio
    async def test_redis_cache_connection_failure(self):
        """测试Redis连接失败"""
        cache = RedisCache("redis://invalid:6379/0")
        
        # 尝试连接
        await cache.connect()
        
        # 连接应该失败
        assert cache.redis_client is None
    
    @pytest.mark.asyncio
    async def test_redis_cache_operations_without_connection(self):
        """测试无连接时的Redis缓存操作"""
        cache = RedisCache("redis://invalid:6379/0")
        
        # 所有操作都应该返回None或False
        assert await cache.get("key1") is None
        await cache.set("key1", "value1", 300)  # 应该不报错
        assert await cache.delete("key1") is False
        await cache.clear()  # 应该不报错


class TestCacheManager:
    """缓存管理器测试"""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """创建临时缓存目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """创建缓存管理器实例"""
        config = CacheConfig(
            cache_dir=temp_cache_dir,
            redis_url=None  # 不使用Redis
        )
        return CacheManager(config)
    
    @pytest.mark.asyncio
    async def test_cache_manager_initialization(self, cache_manager):
        """测试缓存管理器初始化"""
        await cache_manager.initialize()
        
        # 测试基本操作
        await cache_manager.set("key1", "value1", 300)
        assert await cache_manager.get("key1") == "value1"
    
    @pytest.mark.asyncio
    async def test_cache_manager_get_or_set(self, cache_manager):
        """测试缓存管理器的get_or_set功能"""
        await cache_manager.initialize()
        
        # 第一次调用，应该执行函数
        call_count = 0
        
        async def fetch_func():
            nonlocal call_count
            call_count += 1
            return f"value_{call_count}"
        
        result1 = await cache_manager.get_or_set("key1", fetch_func, 300)
        assert result1 == "value_1"
        assert call_count == 1
        
        # 第二次调用，应该从缓存获取
        result2 = await cache_manager.get_or_set("key1", fetch_func, 300)
        assert result2 == "value_1"
        assert call_count == 1  # 函数不应该被再次调用
    
    @pytest.mark.asyncio
    async def test_cache_manager_key_generation(self, cache_manager):
        """测试缓存键生成"""
        key1 = cache_manager._generate_key("test", "arg1", "arg2", param1="value1")
        key2 = cache_manager._generate_key("test", "arg1", "arg2", param1="value1")
        key3 = cache_manager._generate_key("test", "arg1", "arg2", param1="value2")
        
        # 相同参数应该生成相同键
        assert key1 == key2
        
        # 不同参数应该生成不同键
        assert key1 != key3
    
    @pytest.mark.asyncio
    async def test_cache_manager_delete(self, cache_manager):
        """测试缓存管理器删除"""
        await cache_manager.initialize()
        
        await cache_manager.set("key1", "value1", 300)
        assert await cache_manager.get("key1") == "value1"
        
        # 删除缓存
        assert await cache_manager.delete("key1") is True
        assert await cache_manager.get("key1") is None
    
    @pytest.mark.asyncio
    async def test_cache_manager_clear(self, cache_manager):
        """测试缓存管理器清空"""
        await cache_manager.initialize()
        
        await cache_manager.set("key1", "value1", 300)
        await cache_manager.set("key2", "value2", 300)
        
        await cache_manager.clear()
        
        assert await cache_manager.get("key1") is None
        assert await cache_manager.get("key2") is None
    
    @pytest.mark.asyncio
    async def test_cache_manager_stats(self, cache_manager):
        """测试缓存管理器统计"""
        await cache_manager.initialize()
        
        await cache_manager.set("key1", "value1", 300)
        
        stats = cache_manager.get_stats()
        
        assert "memory" in stats
        assert "file" in stats
        assert "redis" in stats
        assert stats["redis"]["available"] is False
    
    @pytest.mark.asyncio
    async def test_cache_manager_export_metrics(self, cache_manager, temp_cache_dir):
        """测试缓存管理器导出指标"""
        await cache_manager.initialize()
        
        await cache_manager.set("key1", "value1", 300)
        
        metrics_file = Path(temp_cache_dir) / "metrics.json"
        result_path = cache_manager.export_metrics(str(metrics_file))
        
        assert result_path == str(metrics_file)
        assert metrics_file.exists()
        
        # 验证导出的内容
        import json
        with open(metrics_file, 'r') as f:
            data = json.load(f)
        
        assert "export_time" in data
        assert "summary" in data
        assert "metrics_data" in data
