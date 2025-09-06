"""
多云分析器测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cloud_cost_analyzer.core.multi_cloud_analyzer import MultiCloudAnalyzer
from cloud_cost_analyzer.utils.exceptions import AWSAnalyzerError


class TestMultiCloudAnalyzer:
    """多云分析器测试类"""
    
    def test_init_with_config(self, mock_config):
        """测试初始化配置"""
        analyzer = MultiCloudAnalyzer(config=mock_config)
        assert analyzer.config == mock_config
        
    def test_get_enabled_providers(self, mock_config):
        """测试获取启用的云服务提供商"""
        analyzer = MultiCloudAnalyzer(config=mock_config)
        providers = analyzer._get_enabled_providers()
        
        expected_providers = ['aws', 'aliyun', 'tencent', 'volcengine']
        assert all(provider in providers for provider in expected_providers)
        
    def test_get_enabled_providers_with_disabled(self):
        """测试部分云服务提供商被禁用"""
        config = {
            "aws": {"enabled": True},
            "aliyun": {"enabled": False},  # 禁用阿里云
            "tencent": {"enabled": True},
            "volcengine": {"enabled": True}
        }
        
        analyzer = MultiCloudAnalyzer(config=config)
        providers = analyzer._get_enabled_providers()
        
        assert 'aws' in providers
        assert 'aliyun' not in providers  # 应该被排除
        assert 'tencent' in providers
        assert 'volcengine' in providers
        
    @patch('cloud_cost_analyzer.core.analyzer.AWSCostAnalyzer')
    @patch('cloud_cost_analyzer.core.aliyun_client.AliyunClient')
    def test_test_all_connections_success(self, mock_aliyun, mock_aws, mock_config):
        """测试所有连接成功"""
        # Mock各个客户端的测试连接方法
        mock_aws_instance = Mock()
        mock_aws_instance.test_connection.return_value = True
        mock_aws.return_value = mock_aws_instance
        
        mock_aliyun_instance = Mock()
        mock_aliyun_instance.test_connection.return_value = True
        mock_aliyun.return_value = mock_aliyun_instance
        
        analyzer = MultiCloudAnalyzer(config=mock_config)
        results = analyzer.test_all_connections()
        
        assert 'aws' in results
        assert results['aws']['success'] is True
        assert 'aliyun' in results
        assert results['aliyun']['success'] is True
        
    @patch('cloud_cost_analyzer.core.analyzer.AWSCostAnalyzer')
    def test_test_connection_failure(self, mock_aws, mock_config):
        """测试连接失败"""
        mock_aws_instance = Mock()
        mock_aws_instance.test_connection.side_effect = Exception("Connection failed")
        mock_aws.return_value = mock_aws_instance
        
        analyzer = MultiCloudAnalyzer(config=mock_config)
        results = analyzer.test_all_connections()
        
        assert 'aws' in results
        assert results['aws']['success'] is False
        assert 'Connection failed' in results['aws']['error']
        
    @patch('cloud_cost_analyzer.core.analyzer.AWSCostAnalyzer')
    @patch('cloud_cost_analyzer.core.aliyun_client.AliyunClient')
    def test_analyze_all_providers(self, mock_aliyun, mock_aws, mock_config):
        """测试分析所有云服务提供商"""
        # Mock AWS分析结果
        mock_aws_instance = Mock()
        mock_aws_instance.analyze.return_value = {
            'summary': {'total_cost': 100.0, 'currency': 'USD'},
            'by_service': pd.DataFrame({'Service': ['EC2'], 'Cost': [100.0]}),
            'by_region': pd.DataFrame({'Region': ['us-east-1'], 'Cost': [100.0]})
        }
        mock_aws.return_value = mock_aws_instance
        
        # Mock阿里云分析结果
        mock_aliyun_instance = Mock()
        mock_aliyun_instance.analyze.return_value = {
            'summary': {'total_cost': 200.0, 'currency': 'CNY'},
            'by_service': pd.DataFrame({'Service': ['ECS'], 'Cost': [200.0]}),
            'by_region': pd.DataFrame({'Region': ['cn-hangzhou'], 'Cost': [200.0]})
        }
        mock_aliyun.return_value = mock_aliyun_instance
        
        analyzer = MultiCloudAnalyzer(config=mock_config)
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        results = analyzer.analyze_all(start_date=start_date, end_date=end_date)
        
        assert 'aws' in results
        assert 'aliyun' in results
        assert results['aws']['success'] is True
        assert results['aliyun']['success'] is True
        assert results['aws']['data']['summary']['total_cost'] == 100.0
        assert results['aliyun']['data']['summary']['total_cost'] == 200.0
        
    def test_generate_comparison_report(self, mock_config):
        """测试生成对比报告"""
        # 准备测试数据
        results = {
            'aws': {
                'success': True,
                'data': {
                    'summary': {'total_cost': 100.0, 'currency': 'USD', 'days': 30},
                    'by_service': pd.DataFrame({
                        'Service': ['EC2', 'S3'],
                        'Cost': [80.0, 20.0]
                    })
                }
            },
            'aliyun': {
                'success': True,
                'data': {
                    'summary': {'total_cost': 500.0, 'currency': 'CNY', 'days': 30},
                    'by_service': pd.DataFrame({
                        'Service': ['ECS', 'OSS'],
                        'Cost': [400.0, 100.0]
                    })
                }
            }
        }
        
        analyzer = MultiCloudAnalyzer(config=mock_config)
        report = analyzer.generate_comparison_report(results)
        
        assert 'summary' in report
        assert 'by_provider' in report
        assert len(report['by_provider']) == 2
        
        # 检查摘要信息
        summary = report['summary']
        assert summary['total_providers'] == 2
        assert summary['successful_providers'] == 2
        
        # 检查各提供商信息
        aws_info = next(p for p in report['by_provider'] if p['provider'] == 'aws')
        assert aws_info['total_cost'] == 100.0
        assert aws_info['currency'] == 'USD'
        
    def test_generate_comparison_report_with_failures(self, mock_config):
        """测试包含失败情况的对比报告"""
        results = {
            'aws': {
                'success': True,
                'data': {
                    'summary': {'total_cost': 100.0, 'currency': 'USD', 'days': 30}
                }
            },
            'aliyun': {
                'success': False,
                'error': 'Connection failed'
            }
        }
        
        analyzer = MultiCloudAnalyzer(config=mock_config)
        report = analyzer.generate_comparison_report(results)
        
        assert report['summary']['total_providers'] == 2
        assert report['summary']['successful_providers'] == 1
        assert report['summary']['failed_providers'] == 1
        
    def test_currency_conversion(self, mock_config):
        """测试货币转换功能"""
        analyzer = MultiCloudAnalyzer(config=mock_config)
        
        # 测试CNY到USD转换（假设汇率为0.14）
        usd_amount = analyzer._convert_currency(100.0, 'CNY', 'USD', 0.14)
        assert abs(usd_amount - 14.0) < 0.01
        
        # 测试相同货币
        same_amount = analyzer._convert_currency(100.0, 'USD', 'USD', 1.0)
        assert same_amount == 100.0
        
    def test_format_provider_name(self, mock_config):
        """测试格式化云服务提供商名称"""
        analyzer = MultiCloudAnalyzer(config=mock_config)
        
        assert analyzer._format_provider_name('aws') == 'AWS'
        assert analyzer._format_provider_name('aliyun') == '阿里云'
        assert analyzer._format_provider_name('tencent') == '腾讯云'
        assert analyzer._format_provider_name('volcengine') == '火山云'
        assert analyzer._format_provider_name('unknown') == 'unknown'  # 未知提供商