"""
Async analyzer module
"""
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from .multi_cloud_analyzer import MultiCloudAnalyzer
from .async_clients import (
    AsyncAWSClient,
    AsyncAliyunClient,
    AsyncTencentClient,
    AsyncVolcengineClient,
)
from ..utils.logger import get_logger

logger = get_logger()


class AsyncMultiCloudAnalyzer(MultiCloudAnalyzer):
    """Asynchronous multi-cloud analyzer"""

    def __init__(self, max_concurrent: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)

        # Initialize async client wrappers
        self.async_aws_client = AsyncAWSClient(self.aws_client, self.executor)
        self.async_aliyun_client = AsyncAliyunClient(self.aliyun_client, self.executor)
        self.async_tencent_client = AsyncTencentClient(self.tencent_client, self.executor)
        self.async_volcengine_client = AsyncVolcengineClient(self.volcengine_client, self.executor)

        self.provider_map = {
            "aws": {
                "client": self.async_aws_client,
                "processor": self.aws_data_processor,
            },
            "aliyun": {
                "client": self.async_aliyun_client,
                "processor": self.aliyun_data_processor,
            },
            "tencent": {
                "client": self.async_tencent_client,
                "processor": self.tencent_data_processor,
            },
            "volcengine": {
                "client": self.async_volcengine_client,
                "processor": self.volcengine_data_processor,
            },
        }

    async def analyze_multi_cloud_costs_async(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        granularity: str = "MONTHLY",
    ) -> Dict[str, Any]:
        """Asynchronously analyze multi-cloud costs"""
        if not start_date or not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        enabled_providers = await self._get_enabled_providers_async()
        if not enabled_providers:
            logger.warning("No cloud providers are enabled or connected.")
            return self._prepare_empty_results()

        tasks = [
            self._analyze_provider_async(provider, start_date, end_date, granularity)
            for provider in enabled_providers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._process_async_results(results, enabled_providers)

    async def _analyze_provider_async(
        self, provider: str, start_date: str, end_date: str, granularity: str
    ) -> Dict[str, Any]:
        """Asynchronously analyze a single cloud provider."""
        logger.info(f"Starting async analysis for {provider}...")
        try:
            provider_info = self.provider_map[provider]
            client = provider_info["client"]
            processor = provider_info["processor"]

            # 1. Asynchronously fetch data
            cost_data = await client.get_cost_and_usage_with_retry(
                start_date, end_date, granularity
            )
            if not cost_data:
                logger.warning(f"No cost data returned for {provider}.")
                return {"provider": provider, "data": pd.DataFrame()}

            # 2. Process data (can be CPU bound, so run in executor)
            loop = asyncio.get_running_loop()
            processed_df = await loop.run_in_executor(
                self.executor, processor.process, cost_data
            )

            logger.info(f"Successfully completed async analysis for {provider}.")
            return {"provider": provider, "data": processed_df}

        except Exception as e:
            logger.error(f"Async analysis for {provider} failed: {e}", exc_info=True)
            return {"provider": provider, "error": str(e)}

    async def _get_enabled_providers_async(self) -> List[str]:
        """Asynchronously get the list of enabled cloud providers."""
        provider_checks = {
            "aws": self.async_aws_client.test_connection(),
            "aliyun": self.async_aliyun_client.test_connection(),
            "tencent": self.async_tencent_client.test_connection(),
            "volcengine": self.async_volcengine_client.test_connection(),
        }
        
        results = await asyncio.gather(*provider_checks.values(), return_exceptions=True)
        
        enabled_providers = []
        for provider, result in zip(provider_checks.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Connection test for {provider} failed with exception: {result}")
                continue

            is_connected, message = result
            if is_connected:
                logger.info(f"Connection successful for {provider}: {message}")
                enabled_providers.append(provider)
            else:
                logger.warning(f"Connection failed for {provider}: {message}")
        
        return enabled_providers

    def _process_async_results(
        self, results: List[Any], providers: List[str]
    ) -> Dict[str, Any]:
        """Process the results from the async analysis."""
        all_data = []
        errors = []

        for i, result in enumerate(results):
            provider = providers[i]
            if isinstance(result, Exception):
                errors.append({"provider": provider, "error": str(result)})
            elif "error" in result:
                errors.append(result)
            elif "data" in result and not result["data"].empty:
                all_data.append(result["data"])

        if not all_data:
            return self._prepare_empty_results(errors)

        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Perform final analysis on combined data
        # This part is CPU-bound and done synchronously after all data is fetched.
        service_costs = self.data_processor.analyze_costs_by_service(combined_df)
        region_costs = self.data_processor.analyze_costs_by_region(combined_df)
        summary = self.data_processor.get_cost_summary(combined_df)

        return {
            "summary": summary,
            "service_costs": service_costs,
            "region_costs": region_costs,
            "raw_data": combined_df,
            "errors": errors,
        }

    def _prepare_empty_results(self, errors: List = []) -> Dict[str, Any]:
        """Return a structured empty result."""
        return {
            "summary": {},
            "service_costs": pd.DataFrame(),
            "region_costs": pd.DataFrame(),
            "raw_data": pd.DataFrame(),
            "errors": errors,
        }

    async def test_connections_async(self) -> Dict[str, Tuple[bool, str]]:
        """Asynchronously test connections to all configured cloud providers."""
        provider_names = list(self.provider_map.keys())
        tasks = [self.provider_map[p]["client"].test_connection() for p in provider_names]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        connections = {}
        for i, result in enumerate(results):
            provider = provider_names[i]
            if isinstance(result, Exception):
                connections[provider] = (False, str(result))
            else:
                connections[provider] = result
        
        return connections

    def __del__(self):
        """Clean up resources."""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)
