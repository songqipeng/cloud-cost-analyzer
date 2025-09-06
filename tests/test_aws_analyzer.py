"""
AWS费用分析器测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cloud_cost_analyzer.core.analyzer import AWSCostAnalyzer
from cloud_cost_analyzer.utils.exceptions import AWSConnectionError, AWSAnalyzerError


class TestAWSCostAnalyzer:
    """AWS费用分析器测试类"""
    
    def test_init_with_config(self, mock_config):
        """测试初始化配置"""
        analyzer = AWSCostAnalyzer(config=mock_config)
        assert analyzer.config == mock_config
        assert analyzer.region == "us-east-1"
        
    @patch('boto3.client')
    def test_init_boto3_client(self, mock_boto3, mock_config):
        """测试boto3客户端初始化"""
        analyzer = AWSCostAnalyzer(config=mock_config)
        analyzer._init_client()
        mock_boto3.assert_called_with('ce', region_name='us-east-1')
        
    @patch('boto3.client')
    def test_test_connection_success(self, mock_boto3, mock_config, mock_boto3_client):
        """测试连接成功"""
        mock_boto3.return_value = mock_boto3_client
        analyzer = AWSCostAnalyzer(config=mock_config)
        
        result = analyzer.test_connection()
        assert result is True
        mock_boto3_client.get_caller_identity.assert_called_once()
        
    @patch('boto3.client')
    def test_test_connection_failure(self, mock_boto3, mock_config):
        """测试连接失败"""
        mock_client = Mock()
        mock_client.get_caller_identity.side_effect = Exception("Connection failed")
        mock_boto3.return_value = mock_client
        
        analyzer = AWSCostAnalyzer(config=mock_config)
        
        with pytest.raises(AWSConnectionError):
            analyzer.test_connection()
            
    @patch('boto3.client')
    def test_get_cost_and_usage_success(self, mock_boto3, mock_config, mock_aws_cost_data):
        """测试获取费用数据成功"""
        mock_client = Mock()
        mock_client.get_cost_and_usage.return_value = mock_aws_cost_data
        mock_boto3.return_value = mock_client
        
        analyzer = AWSCostAnalyzer(config=mock_config)
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 2)
        
        result = analyzer.get_cost_and_usage(start_date, end_date)
        
        assert result == mock_aws_cost_data
        mock_client.get_cost_and_usage.assert_called_once()
        
    @patch('boto3.client')
    def test_get_cost_and_usage_api_error(self, mock_boto3, mock_config):
        """测试API调用错误"""
        mock_client = Mock()
        mock_client.get_cost_and_usage.side_effect = Exception("API Error")
        mock_boto3.return_value = mock_client
        
        analyzer = AWSCostAnalyzer(config=mock_config)
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 2)
        
        with pytest.raises(AWSAnalyzerError):
            analyzer.get_cost_and_usage(start_date, end_date)
            
    def test_process_cost_data(self, mock_config, mock_aws_cost_data):
        """测试费用数据处理"""
        analyzer = AWSCostAnalyzer(config=mock_config)
        
        df = analyzer.process_cost_data(mock_aws_cost_data)
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'Date' in df.columns
        assert 'Service' in df.columns
        assert 'Cost' in df.columns
        assert len(df) > 0
        
    def test_process_empty_cost_data(self, mock_config):
        """测试处理空费用数据"""
        analyzer = AWSCostAnalyzer(config=mock_config)
        empty_data = {'ResultsByTime': []}
        
        df = analyzer.process_cost_data(empty_data)
        
        assert isinstance(df, pd.DataFrame)
        assert df.empty
        
    @patch('boto3.client')
    def test_analyze_with_date_range(self, mock_boto3, mock_config, mock_aws_cost_data):
        """测试按日期范围分析"""
        mock_client = Mock()
        mock_client.get_cost_and_usage.return_value = mock_aws_cost_data
        mock_boto3.return_value = mock_client
        
        analyzer = AWSCostAnalyzer(config=mock_config)
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = analyzer.analyze(start_date=start_date, end_date=end_date)
        
        assert 'summary' in result
        assert 'by_service' in result
        assert 'by_region' in result
        assert isinstance(result['summary']['total_cost'], float)
        
    def test_validate_date_range(self, mock_config):
        """测试日期范围验证"""
        analyzer = AWSCostAnalyzer(config=mock_config)
        
        # 测试开始日期晚于结束日期
        start_date = date(2024, 1, 31)
        end_date = date(2024, 1, 1)
        
        with pytest.raises(ValueError, match="开始日期不能晚于结束日期"):
            analyzer._validate_date_range(start_date, end_date)
            
        # 测试未来日期
        future_date = date(2025, 12, 31)
        
        with pytest.raises(ValueError, match="日期不能是未来时间"):
            analyzer._validate_date_range(future_date, future_date)
            
    def test_filter_by_threshold(self, mock_config):
        """测试按阈值过滤"""
        analyzer = AWSCostAnalyzer(config=mock_config)
        
        # 创建测试DataFrame
        test_data = {
            'Service': ['EC2', 'S3', 'Lambda'],
            'Cost': [10.50, 0.005, 2.30]  # S3费用低于阈值0.01
        }
        df = pd.DataFrame(test_data)
        
        filtered_df = analyzer._filter_by_threshold(df, 'Cost')
        
        # 应该过滤掉S3（费用0.005 < 0.01）
        assert len(filtered_df) == 2
        assert 'S3' not in filtered_df['Service'].values
        assert 'EC2' in filtered_df['Service'].values
        assert 'Lambda' in filtered_df['Service'].values