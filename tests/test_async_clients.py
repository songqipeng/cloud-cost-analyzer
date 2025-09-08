"""
异步客户端测试
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, date

from cloud_cost_analyzer.core.async_clients import (
    AsyncAWSClient, AsyncAliyunClient, AsyncTencentClient, 
    AsyncVolcengineClient, AsyncMultiCloudClient, AsyncClientConfig
)
from cloud_cost_analyzer.models.cost_models import CloudProvider


class TestAsyncClientConfig:
    """异步客户端配置测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = AsyncClientConfig()
        
        assert config.timeout == 30
        assert config.max_concurrent_requests == 5
        assert config.retry_attempts == 3
        assert config.retry_delay == 1.0
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = AsyncClientConfig(
            timeout=60,
            max_concurrent_requests=10,
            retry_attempts=5,
            retry_delay=2.0
        )
        
        assert config.timeout == 60
        assert config.max_concurrent_requests == 10
        assert config.retry_attempts == 5
        assert config.retry_delay == 2.0


class TestAsyncAWSClient:
    """异步AWS客户端测试"""
    
    @pytest.fixture
    def aws_client(self):
        """创建AWS客户端实例"""
        return AsyncAWSClient(
            access_key_id="test_key",
            secret_access_key="test_secret",
            region="us-east-1"
        )
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, aws_client):
        """测试连接成功"""
        with patch('aioboto3.Session') as mock_session:
            mock_sts = AsyncMock()
            mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
            
            mock_session.return_value.__aenter__.return_value.client.return_value.__aenter__.return_value = mock_sts
            
            success, message = await aws_client.test_connection()
            
            assert success is True
            assert "123456789012" in message
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, aws_client):
        """测试连接失败"""
        with patch('aioboto3.Session') as mock_session:
            mock_sts = AsyncMock()
            mock_sts.get_caller_identity.side_effect = Exception("Connection failed")
            
            mock_session.return_value.__aenter__.return_value.client.return_value.__aenter__.return_value = mock_sts
            
            success, message = await aws_client.test_connection()
            
            assert success is False
            assert "Connection failed" in message
    
    @pytest.mark.asyncio
    async def test_get_cost_and_usage_async_success(self, aws_client):
        """测试获取费用数据成功"""
        mock_response = {
            'ResultsByTime': [
                {
                    'TimePeriod': {'Start': '2024-01-01', 'End': '2024-01-02'},
                    'Groups': [
                        {
                            'Keys': ['EC2', 'us-east-1'],
                            'Metrics': {'BlendedCost': {'Amount': '100.50', 'Unit': 'USD'}}
                        }
                    ]
                }
            ],
            'GroupDefinitions': []
        }
        
        with patch('aioboto3.Session') as mock_session:
            mock_ce = AsyncMock()
            mock_ce.get_cost_and_usage.return_value = mock_response
            
            mock_session.return_value.__aenter__.return_value.client.return_value.__aenter__.return_value = mock_ce
            
            result = await aws_client.get_cost_and_usage_async("2024-01-01", "2024-01-02")
            
            assert result == mock_response
            mock_ce.get_cost_and_usage.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cost_and_usage_async_failure(self, aws_client):
        """测试获取费用数据失败"""
        with patch('aioboto3.Session') as mock_session:
            mock_ce = AsyncMock()
            mock_ce.get_cost_and_usage.side_effect = Exception("API Error")
            
            mock_session.return_value.__aenter__.return_value.client.return_value.__aenter__.return_value = mock_ce
            
            result = await aws_client.get_cost_and_usage_async("2024-01-01", "2024-01-02")
            
            assert result is None


class TestAsyncAliyunClient:
    """异步阿里云客户端测试"""
    
    @pytest.fixture
    def aliyun_client(self):
        """创建阿里云客户端实例"""
        return AsyncAliyunClient(
            access_key_id="test_key",
            access_key_secret="test_secret",
            region="cn-hangzhou"
        )
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, aliyun_client):
        """测试连接成功"""
        success, message = await aliyun_client.test_connection()
        
        assert success is True
        assert "阿里云连接测试成功" in message
    
    @pytest.mark.asyncio
    async def test_get_cost_and_usage_async_success(self, aliyun_client):
        """测试获取费用数据成功"""
        result = await aliyun_client.get_cost_and_usage_async("2024-01-01", "2024-01-02")
        
        assert result is not None
        assert 'ResultsByTime' in result
        assert len(result['ResultsByTime']) > 0


class TestAsyncTencentClient:
    """异步腾讯云客户端测试"""
    
    @pytest.fixture
    def tencent_client(self):
        """创建腾讯云客户端实例"""
        return AsyncTencentClient(
            secret_id="test_id",
            secret_key="test_key",
            region="ap-beijing"
        )
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, tencent_client):
        """测试连接成功"""
        success, message = await tencent_client.test_connection()
        
        assert success is True
        assert "腾讯云连接测试成功" in message
    
    @pytest.mark.asyncio
    async def test_get_cost_and_usage_async_success(self, tencent_client):
        """测试获取费用数据成功"""
        result = await tencent_client.get_cost_and_usage_async("2024-01-01", "2024-01-02")
        
        assert result is not None
        assert 'ResultsByTime' in result
        assert len(result['ResultsByTime']) > 0


class TestAsyncVolcengineClient:
    """异步火山引擎客户端测试"""
    
    @pytest.fixture
    def volcengine_client(self):
        """创建火山引擎客户端实例"""
        return AsyncVolcengineClient(
            access_key_id="test_key",
            secret_access_key="test_secret",
            region="cn-beijing"
        )
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, volcengine_client):
        """测试连接成功"""
        success, message = await volcengine_client.test_connection()
        
        assert success is True
        assert "火山引擎连接测试成功" in message
    
    @pytest.mark.asyncio
    async def test_get_cost_and_usage_async_success(self, volcengine_client):
        """测试获取费用数据成功"""
        result = await volcengine_client.get_cost_and_usage_async("2024-01-01", "2024-01-02")
        
        assert result is not None
        assert 'ResultsByTime' in result
        assert len(result['ResultsByTime']) > 0


class TestAsyncMultiCloudClient:
    """异步多云客户端测试"""
    
    @pytest.fixture
    def multi_cloud_client(self):
        """创建多云客户端实例"""
        client = AsyncMultiCloudClient()
        
        # 添加模拟客户端
        aws_client = AsyncMock()
        aws_client.test_connection.return_value = (True, "AWS连接成功")
        aws_client.get_cost_and_usage_async.return_value = {"ResultsByTime": []}
        
        aliyun_client = AsyncMock()
        aliyun_client.test_connection.return_value = (True, "阿里云连接成功")
        aliyun_client.get_cost_and_usage_async.return_value = {"ResultsByTime": []}
        
        client.add_client(CloudProvider.AWS, aws_client)
        client.add_client(CloudProvider.ALIYUN, aliyun_client)
        
        return client
    
    @pytest.mark.asyncio
    async def test_test_all_connections_success(self, multi_cloud_client):
        """测试所有连接成功"""
        results = await multi_cloud_client.test_all_connections()
        
        assert CloudProvider.AWS in results
        assert CloudProvider.ALIYUN in results
        assert results[CloudProvider.AWS][0] is True
        assert results[CloudProvider.ALIYUN][0] is True
    
    @pytest.mark.asyncio
    async def test_get_multi_cloud_cost_data_success(self, multi_cloud_client):
        """测试获取多云费用数据成功"""
        providers = [CloudProvider.AWS, CloudProvider.ALIYUN]
        
        results = await multi_cloud_client.get_multi_cloud_cost_data(
            providers, "2024-01-01", "2024-01-02"
        )
        
        assert CloudProvider.AWS in results
        assert CloudProvider.ALIYUN in results
        assert results[CloudProvider.AWS] is not None
        assert results[CloudProvider.ALIYUN] is not None
    
    @pytest.mark.asyncio
    async def test_get_cost_data_with_retry_success(self, multi_cloud_client):
        """测试带重试的费用数据获取成功"""
        result = await multi_cloud_client.get_cost_data_with_retry(
            CloudProvider.AWS, "2024-01-01", "2024-01-02"
        )
        
        assert result is not None
        assert 'ResultsByTime' in result
    
    @pytest.mark.asyncio
    async def test_get_cost_data_with_retry_failure(self, multi_cloud_client):
        """测试带重试的费用数据获取失败"""
        # 创建总是失败的客户端
        failing_client = AsyncMock()
        failing_client.get_cost_and_usage_async.side_effect = Exception("API Error")
        
        multi_cloud_client.add_client(CloudProvider.TENCENT, failing_client)
        
        result = await multi_cloud_client.get_cost_data_with_retry(
            CloudProvider.TENCENT, "2024-01-01", "2024-01-02"
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_limit(self):
        """测试并发请求限制"""
        config = AsyncClientConfig(max_concurrent_requests=2)
        client = AsyncMultiCloudClient(config)
        
        # 创建慢客户端
        slow_client = AsyncMock()
        slow_client.get_cost_and_usage_async.return_value = {"ResultsByTime": []}
        
        # 模拟慢请求
        async def slow_request(*args, **kwargs):
            await asyncio.sleep(0.1)
            return {"ResultsByTime": []}
        
        slow_client.get_cost_and_usage_async.side_effect = slow_request
        
        client.add_client(CloudProvider.AWS, slow_client)
        client.add_client(CloudProvider.ALIYUN, slow_client)
        client.add_client(CloudProvider.TENCENT, slow_client)
        
        start_time = asyncio.get_event_loop().time()
        
        results = await client.get_multi_cloud_cost_data(
            [CloudProvider.AWS, CloudProvider.ALIYUN, CloudProvider.TENCENT],
            "2024-01-01", "2024-01-02"
        )
        
        end_time = asyncio.get_event_loop().time()
        
        # 由于并发限制，总时间应该大于单个请求时间
        assert end_time - start_time >= 0.1
        assert len(results) == 3
