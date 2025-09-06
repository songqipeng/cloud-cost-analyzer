"""
缓存管理模块
"""
import json
import hashlib
import os
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import pickle


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_hours = ttl_hours
    
    def _get_cache_key(self, key: str) -> str:
        """生成缓存键"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.cache"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """检查缓存是否有效"""
        if not cache_path.exists():
            return False
        
        # 检查文件修改时间
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - mtime < timedelta(hours=self.ttl_hours)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        cache_path = self._get_cache_path(key)
        
        if not self._is_cache_valid(cache_path):
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """设置缓存数据"""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存数据"""
        cache_path = self._get_cache_path(key)
        
        try:
            if cache_path.exists():
                cache_path.unlink()
            return True
        except Exception:
            return False
    
    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            return True
        except Exception:
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_dir": str(self.cache_dir),
            "file_count": len(cache_files),
            "total_size": total_size,
            "ttl_hours": self.ttl_hours
        }


class CostDataCache:
    """费用数据缓存"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    def get_cost_data(
        self, 
        provider: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[Dict[str, Any]]:
        """获取费用数据缓存"""
        key = f"cost_data_{provider}_{start_date}_{end_date}"
        return self.cache_manager.get(key)
    
    def set_cost_data(
        self, 
        provider: str, 
        start_date: str, 
        end_date: str, 
        data: Dict[str, Any]
    ) -> bool:
        """设置费用数据缓存"""
        key = f"cost_data_{provider}_{start_date}_{end_date}"
        return self.cache_manager.set(key, data)
    
    def get_connection_status(self, provider: str) -> Optional[Dict[str, Any]]:
        """获取连接状态缓存"""
        key = f"connection_status_{provider}"
        return self.cache_manager.get(key)
    
    def set_connection_status(
        self, 
        provider: str, 
        status: Dict[str, Any]
    ) -> bool:
        """设置连接状态缓存"""
        key = f"connection_status_{provider}"
        return self.cache_manager.set(key, status)
    
    def get_analysis_result(
        self, 
        analysis_type: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[Dict[str, Any]]:
        """获取分析结果缓存"""
        key = f"analysis_result_{analysis_type}_{start_date}_{end_date}"
        return self.cache_manager.get(key)
    
    def set_analysis_result(
        self, 
        analysis_type: str, 
        start_date: str, 
        end_date: str, 
        result: Dict[str, Any]
    ) -> bool:
        """设置分析结果缓存"""
        key = f"analysis_result_{analysis_type}_{start_date}_{end_date}"
        return self.cache_manager.set(key, result)


# 全局缓存实例
_cache_manager = CacheManager()
_cost_data_cache = CostDataCache(_cache_manager)


def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    return _cache_manager


def get_cost_data_cache() -> CostDataCache:
    """获取费用数据缓存实例"""
    return _cost_data_cache
