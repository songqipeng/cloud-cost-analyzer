"""
云服务客户端测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cloud_cost_analyzer.core.aliyun_client import AliyunClient
from cloud_cost_analyzer.core.tencent_client import TencentClient
from cloud_cost_analyzer.core.volcengine_client import VolcengineClient
from cloud_cost_analyzer.utils.exceptions import AWSConnectionError


class TestAliyunClient:
    """阿里云客户端测试"""
    
    def test_init_with_config(self, mock_config):
        """测试初始化配置"""
        client = AliyunClient(config=mock_config)
        assert client.config == mock_config
        assert client.region == "cn-hangzhou"
        
    def test_init_with_environment_variables(self, mock_environment_variables):
        """测试从环境变量初始化"""
        client = AliyunClient()
        # 环境变量应该被正确读取
        assert hasattr(client, 'access_key_id')
        assert hasattr(client, 'access_key_secret')
        
    @patch('alibabacloud_bssopenapi20171214.client.Client')
    def test_test_connection_success(self, mock_client, mock_config):
        """测试连接成功"""
        mock_instance = Mock()
        mock_instance.get_account_balance.return_value = Mock(
            body=Mock(data=Mock(available_amount="1000.00"))
        )
        mock_client.return_value = mock_instance
        
        client = AliyunClient(config=mock_config)
        result = client.test_connection()
        
        assert result is True
        
    @patch('alibabacloud_bssopenapi20171214.client.Client')
    def test_test_connection_failure(self, mock_client, mock_config):
        """测试连接失败"""
        mock_instance = Mock()
        mock_instance.get_account_balance.side_effect = Exception("Connection failed")
        mock_client.return_value = mock_instance
        
        client = AliyunClient(config=mock_config)
        
        with pytest.raises(AWSConnectionError):
            client.test_connection()
            
    @patch('alibabacloud_bssopenapi20171214.client.Client')
    def test_get_cost_data_success(self, mock_client, mock_config, mock_aliyun_cost_data):
        """测试获取费用数据成功"""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.body = type('obj', (object,), {'to_map': lambda: mock_aliyun_cost_data})()
        mock_instance.describe_instance_bills.return_value = mock_response
        mock_client.return_value = mock_instance
        
        client = AliyunClient(config=mock_config)
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = client.get_cost_data(start_date, end_date)
        
        assert result == mock_aliyun_cost_data
        
    def test_format_service_name(self, mock_config):
        """测试服务名称本地化"""
        client = AliyunClient(config=mock_config)
        
        assert client._format_service_name('ecs') == '云服务器ECS'
        assert client._format_service_name('oss') == '对象存储OSS'
        assert client._format_service_name('rds') == '云数据库RDS'
        assert client._format_service_name('unknown') == 'unknown'


class TestTencentClient:
    """腾讯云客户端测试"""
    
    def test_init_with_config(self, mock_config):
        """测试初始化配置"""
        client = TencentClient(config=mock_config)
        assert client.config == mock_config
        assert client.region == "ap-beijing"
        
    @patch('tencentcloud.billing.v20180709.billing_client.BillingClient')
    def test_test_connection_success(self, mock_client, mock_config):
        """测试连接成功"""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.Balance = "500.00"
        mock_instance.DescribeAccountBalance.return_value = mock_response
        mock_client.return_value = mock_instance
        
        client = TencentClient(config=mock_config)
        result = client.test_connection()
        
        assert result is True
        
    @patch('tencentcloud.billing.v20180709.billing_client.BillingClient')
    def test_get_cost_data_success(self, mock_client, mock_config, mock_tencent_cost_data):
        """测试获取费用数据成功"""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response._serialize = lambda: json.dumps(mock_tencent_cost_data)
        mock_instance.DescribeBillDetail.return_value = mock_response
        mock_client.return_value = mock_instance
        
        client = TencentClient(config=mock_config)
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = client.get_cost_data(start_date, end_date)
        
        assert 'Response' in result
        
    def test_format_service_name(self, mock_config):
        """测试服务名称本地化"""
        client = TencentClient(config=mock_config)
        
        assert client._format_service_name('cvm') == '云服务器CVM'
        assert client._format_service_name('cos') == '对象存储COS'
        assert client._format_service_name('cdb') == '云数据库MySQL'
        assert client._format_service_name('unknown') == 'unknown'


class TestVolcengineClient:
    """火山云客户端测试"""
    
    def test_init_with_config(self, mock_config):
        """测试初始化配置"""
        client = VolcengineClient(config=mock_config)
        assert client.config == mock_config
        assert client.region == "cn-beijing"
        
    @patch('volcengine.billing.BillingService')
    def test_test_connection_success(self, mock_service, mock_config):
        """测试连接成功"""
        mock_instance = Mock()
        mock_response = {
            'Result': {
                'AvailableBalance': 200.00
            }
        }
        mock_instance.get_balance.return_value = mock_response
        mock_service.return_value = mock_instance
        
        client = VolcengineClient(config=mock_config)
        result = client.test_connection()
        
        assert result is True
        
    @patch('volcengine.billing.BillingService')
    def test_get_cost_data_success(self, mock_service, mock_config, mock_volcengine_cost_data):
        """测试获取费用数据成功"""
        mock_instance = Mock()
        mock_instance.list_bill_detail.return_value = mock_volcengine_cost_data
        mock_service.return_value = mock_instance
        
        client = VolcengineClient(config=mock_config)
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = client.get_cost_data(start_date, end_date)
        
        assert result == mock_volcengine_cost_data
        
    def test_format_service_name(self, mock_config):
        """测试服务名称本地化"""
        client = VolcengineClient(config=mock_config)
        
        assert client._format_service_name('ECS') == '云服务器'
        assert client._format_service_name('TOS') == '对象存储'
        assert client._format_service_name('RDS') == '云数据库'
        assert client._format_service_name('Unknown') == 'Unknown'