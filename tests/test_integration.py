"""
集成测试模块
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from src.cloud_cost_analyzer.core.multi_cloud_analyzer import MultiCloudAnalyzer


class TestIntegration:
    """集成测试类"""
    
    @pytest.mark.integration
    def test_multi_cloud_analyzer_initialization(self):
        """测试多云分析器初始化"""
        analyzer = MultiCloudAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'aws_client')
        assert hasattr(analyzer, 'aliyun_client')
        assert hasattr(analyzer, 'tencent_client')
        assert hasattr(analyzer, 'volcengine_client')
    
    @pytest.mark.integration
    @patch('src.cloud_cost_analyzer.core.client.AWSClient.test_connection')
    @patch('src.cloud_cost_analyzer.core.aliyun_client.AliyunClient.test_connection')
    def test_connection_testing(self, mock_aliyun, mock_aws):
        """测试连接测试功能"""
        mock_aws.return_value = (True, "AWS连接成功")
        mock_aliyun.return_value = (True, "阿里云连接成功")
        
        analyzer = MultiCloudAnalyzer()
        connections = analyzer.test_connections()
        
        assert 'aws' in connections
        assert 'aliyun' in connections
        assert connections['aws'][0] is True
        assert connections['aliyun'][0] is True
    
    @pytest.mark.slow
    def test_config_loading(self):
        """测试配置加载"""
        from src.cloud_cost_analyzer.utils.config import Config
        
        # 测试默认配置
        default_config = Config.get_default_config()
        assert 'aws' in default_config
        assert 'notifications' in default_config
        assert 'schedule' in default_config
        
        # 测试邮件提供商配置
        gmail_config = Config.get_email_provider_config('gmail')
        assert gmail_config.smtp_server == 'smtp.gmail.com'
        assert gmail_config.smtp_port == 587
