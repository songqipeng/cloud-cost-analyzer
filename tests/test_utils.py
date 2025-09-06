"""
工具类测试
"""
import pytest
from unittest.mock import Mock, patch, mock_open
import json
import os
from datetime import datetime, date

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cloud_cost_analyzer.utils.config import Config
from cloud_cost_analyzer.utils.validators import DataValidator
from cloud_cost_analyzer.utils.exceptions import AWSAnalyzerError, AWSConnectionError


class TestConfig:
    """配置类测试"""
    
    def test_load_from_file(self, temp_config_file):
        """测试从文件加载配置"""
        config = Config(config_file=temp_config_file)
        
        assert config.get('aws.default_region') == 'us-east-1'
        assert config.get('aws.cost_threshold') == 0.01
        assert config.get('notifications.email.enabled') is False
        
    def test_load_from_dict(self, mock_config):
        """测试从字典加载配置"""
        config = Config(config_dict=mock_config)
        
        assert config.get('aws.default_region') == 'us-east-1'
        assert config.get('aliyun.enabled') is True
        
    def test_get_with_default(self, mock_config):
        """测试获取配置值（带默认值）"""
        config = Config(config_dict=mock_config)
        
        # 存在的配置
        assert config.get('aws.default_region') == 'us-east-1'
        
        # 不存在的配置，返回默认值
        assert config.get('non.existent.key', 'default') == 'default'
        
        # 不存在的配置，无默认值，返回None
        assert config.get('non.existent.key') is None
        
    def test_set_config(self, mock_config):
        """测试设置配置值"""
        config = Config(config_dict=mock_config)
        
        config.set('new.config.key', 'new_value')
        assert config.get('new.config.key') == 'new_value'
        
    def test_update_config(self, mock_config):
        """测试批量更新配置"""
        config = Config(config_dict=mock_config)
        
        updates = {
            'aws.cost_threshold': 0.05,
            'new.key': 'new_value'
        }
        config.update(updates)
        
        assert config.get('aws.cost_threshold') == 0.05
        assert config.get('new.key') == 'new_value'
        
    def test_has_config(self, mock_config):
        """测试检查配置是否存在"""
        config = Config(config_dict=mock_config)
        
        assert config.has('aws.default_region') is True
        assert config.has('non.existent.key') is False
        
    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_file(self, mock_file, mock_config, tmp_path):
        """测试保存配置到文件"""
        config = Config(config_dict=mock_config)
        save_path = tmp_path / "test_config.json"
        
        config.save(str(save_path))
        
        mock_file.assert_called_once_with(str(save_path), 'w', encoding='utf-8')
        
    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        with pytest.raises(FileNotFoundError):
            Config(config_file="nonexistent.json")
            
    def test_load_invalid_json(self, tmp_path):
        """测试加载无效JSON文件"""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("invalid json content")
        
        with pytest.raises(json.JSONDecodeError):
            Config(config_file=str(invalid_json))
            
    def test_environment_variable_override(self, mock_config, monkeypatch):
        """测试环境变量覆盖配置"""
        monkeypatch.setenv('AWS_DEFAULT_REGION', 'us-west-2')
        
        config = Config(config_dict=mock_config)
        
        # 环境变量应该覆盖配置文件中的值
        assert config.get_with_env('aws.default_region', 'AWS_DEFAULT_REGION') == 'us-west-2'
        
    def test_get_section(self, mock_config):
        """测试获取配置节"""
        config = Config(config_dict=mock_config)
        
        aws_section = config.get_section('aws')
        assert aws_section['default_region'] == 'us-east-1'
        assert aws_section['cost_threshold'] == 0.01


class TestDataValidator:
    """数据验证器测试"""
    
    def test_validate_date_range_valid(self):
        """测试有效的日期范围"""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        # 不应该抛出异常
        DataValidator.validate_date_range(start_date, end_date)
        
    def test_validate_date_range_invalid_order(self):
        """测试无效的日期顺序"""
        start_date = date(2024, 1, 31)
        end_date = date(2024, 1, 1)
        
        with pytest.raises(ValueError, match="开始日期不能晚于结束日期"):
            DataValidator.validate_date_range(start_date, end_date)
            
    def test_validate_date_range_future_date(self):
        """测试未来日期"""
        future_date = date(2025, 12, 31)
        
        with pytest.raises(ValueError, match="日期不能是未来时间"):
            DataValidator.validate_date_range(future_date, future_date)
            
    def test_validate_cost_threshold_valid(self):
        """测试有效的费用阈值"""
        # 不应该抛出异常
        DataValidator.validate_cost_threshold(0.01)
        DataValidator.validate_cost_threshold(10.5)
        
    def test_validate_cost_threshold_invalid(self):
        """测试无效的费用阈值"""
        with pytest.raises(ValueError, match="费用阈值必须大于0"):
            DataValidator.validate_cost_threshold(0)
            
        with pytest.raises(ValueError, match="费用阈值必须大于0"):
            DataValidator.validate_cost_threshold(-1)
            
    def test_validate_aws_credentials_valid(self):
        """测试有效的AWS凭证"""
        credentials = {
            'access_key_id': 'AKIATEST123456789',
            'secret_access_key': 'test-secret-key',
            'region': 'us-east-1'
        }
        
        # 不应该抛出异常
        DataValidator.validate_aws_credentials(credentials)
        
    def test_validate_aws_credentials_missing_key(self):
        """测试缺少必需的AWS凭证"""
        incomplete_credentials = {
            'access_key_id': 'AKIATEST123456789',
            'region': 'us-east-1'
            # 缺少 secret_access_key
        }
        
        with pytest.raises(ValueError, match="AWS凭证不完整"):
            DataValidator.validate_aws_credentials(incomplete_credentials)
            
    def test_validate_aws_credentials_invalid_format(self):
        """测试无效格式的AWS凭证"""
        invalid_credentials = {
            'access_key_id': 'invalid-key',  # 格式不正确
            'secret_access_key': 'test-secret-key',
            'region': 'us-east-1'
        }
        
        with pytest.raises(ValueError, match="AWS Access Key ID格式不正确"):
            DataValidator.validate_aws_credentials(invalid_credentials)
            
    def test_validate_email_valid(self):
        """测试有效的邮箱地址"""
        valid_emails = [
            'user@example.com',
            'test.user@domain.co.uk',
            'user+tag@example.org'
        ]
        
        for email in valid_emails:
            assert DataValidator.validate_email(email) is True
            
    def test_validate_email_invalid(self):
        """测试无效的邮箱地址"""
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user@@domain.com'
        ]
        
        for email in invalid_emails:
            assert DataValidator.validate_email(email) is False
            
    def test_validate_url_valid(self):
        """测试有效的URL"""
        valid_urls = [
            'https://example.com',
            'http://subdomain.example.org/path',
            'https://api.example.com/v1/webhook?param=value'
        ]
        
        for url in valid_urls:
            assert DataValidator.validate_url(url) is True
            
    def test_validate_url_invalid(self):
        """测试无效的URL"""
        invalid_urls = [
            'not-a-url',
            'ftp://example.com',  # 不支持的协议
            'http://',
            ''
        ]
        
        for url in invalid_urls:
            assert DataValidator.validate_url(url) is False
            
    def test_sanitize_service_name(self):
        """测试服务名称清理"""
        test_cases = [
            ('EC2-Instance', 'EC2-Instance'),
            ('Amazon Elastic Compute Cloud', 'EC2'),
            ('Simple Storage Service', 'S3'),
            ('Unknown Service', 'Unknown Service')
        ]
        
        for input_name, expected in test_cases:
            result = DataValidator.sanitize_service_name(input_name)
            assert result == expected