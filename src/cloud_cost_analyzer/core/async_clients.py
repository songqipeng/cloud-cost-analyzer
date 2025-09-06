"""
Asynchronous wrappers for cloud clients.
"""
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor

from .aliyun_client import AliyunClient
from .tencent_client import TencentClient
from .volcengine_client import VolcengineClient
from .client import AWSClient


class AsyncAWSClient:
    """Async wrapper for the AWSClient."""

    def __init__(self, sync_client: AWSClient, executor: ThreadPoolExecutor):
        self._sync_client = sync_client
        self._executor = executor
        self._loop = asyncio.get_running_loop()

    async def get_cost_and_usage_with_retry(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        return await self._loop.run_in_executor(
            self._executor, lambda: self._sync_client.get_cost_and_usage_with_retry(*args, **kwargs)
        )

    async def test_connection(self) -> Tuple[bool, str]:
        return await self._loop.run_in_executor(
            self._executor, self._sync_client.test_connection
        )


class AsyncAliyunClient:
    """Async wrapper for the AliyunClient."""

    def __init__(self, sync_client: AliyunClient, executor: ThreadPoolExecutor):
        self._sync_client = sync_client
        self._executor = executor
        self._loop = asyncio.get_running_loop()

    async def get_cost_and_usage_with_retry(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        return await self._loop.run_in_executor(
            self._executor, lambda: self._sync_client.get_cost_and_usage_with_retry(*args, **kwargs)
        )

    async def test_connection(self) -> Tuple[bool, str]:
        return await self._loop.run_in_executor(
            self._executor, self._sync_client.test_connection
        )


class AsyncTencentClient:
    """Async wrapper for the TencentClient."""

    def __init__(self, sync_client: TencentClient, executor: ThreadPoolExecutor):
        self._sync_client = sync_client
        self._executor = executor
        self._loop = asyncio.get_running_loop()

    async def get_cost_and_usage_with_retry(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        return await self._loop.run_in_executor(
            self._executor, lambda: self._sync_client.get_cost_and_usage_with_retry(*args, **kwargs)
        )

    async def test_connection(self) -> Tuple[bool, str]:
        return await self._loop.run_in_executor(
            self._executor, self._sync_client.test_connection
        )


class AsyncVolcengineClient:
    """Async wrapper for the VolcengineClient."""

    def __init__(self, sync_client: VolcengineClient, executor: ThreadPoolExecutor):
        self._sync_client = sync_client
        self._executor = executor
        self._loop = asyncio.get_running_loop()

    async def get_cost_and_usage_with_retry(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        return await self._loop.run_in_executor(
            self._executor, lambda: self._sync_client.get_cost_and_usage_with_retry(*args, **kwargs)
        )

    async def test_connection(self) -> Tuple[bool, str]:
        return await self._loop.run_in_executor(
            self._executor, self._sync_client.test_connection
        )
