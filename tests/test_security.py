"""
安全模块测试
"""
import pytest
import json
import tempfile
from datetime import datetime, date
from pathlib import Path

from cloud_cost_analyzer.utils.security import (
    SecureLogger, InputValidator, ConfigEncryption, SecurityManager
)
from cloud_cost_analyzer.models.cost_models import (
    CostAnalysisRequest, CloudProvider, Granularity
)


class TestSecureLogger:
    """安全日志记录器测试"""
    
    def test_mask_sensitive_data_string(self):
        """测试字符串敏感信息脱敏"""
        logger = SecureLogger()
        
        # 测试包含敏感键的字符串
        sensitive_text = "password=secret123"
        masked = logger._mask_string(sensitive_text)
        assert masked == "***MASKED***"
        
        # 测试包含API密钥的字符串
        api_key_text = "AKIAIOSFODNN7EXAMPLE"
        masked = logger._mask_string(api_key_text)
        assert masked == "***MASKED***"
        
        # 测试普通字符串
        normal_text = "This is a normal message"
        masked = logger._mask_string(normal_text)
        assert masked == normal_text
    
    def test_mask_sensitive_data_dict(self):
        """测试字典敏感信息脱敏"""
        logger = SecureLogger()
        
        data = {
            "username": "testuser",
            "password": "secret123",
            "api_key": "AKIAIOSFODNN7EXAMPLE",
            "normal_field": "normal_value"
        }
        
        masked_data = logger._mask_sensitive_data(data)
        
        assert masked_data["username"] == "testuser"
        assert masked_data["password"] == "***MASKED***"
        assert masked_data["api_key"] == "***MASKED***"
        assert masked_data["normal_field"] == "normal_value"
    
    def test_mask_sensitive_data_nested(self):
        """测试嵌套数据结构脱敏"""
        logger = SecureLogger()
        
        data = {
            "user": {
                "name": "testuser",
                "credentials": {
                    "password": "secret123",
                    "token": "abc123"
                }
            },
            "config": {
                "secret_key": "xyz789"
            }
        }
        
        masked_data = logger._mask_sensitive_data(data)
        
        assert masked_data["user"]["name"] == "testuser"
        assert masked_data["user"]["credentials"]["password"] == "***MASKED***"
        assert masked_data["user"]["credentials"]["token"] == "***MASKED***"
        assert masked_data["config"]["secret_key"] == "***MASKED***"


class TestInputValidator:
    """输入验证器测试"""
    
    def test_validate_date_format(self):
        """测试日期格式验证"""
        validator = InputValidator()
        
        # 有效日期格式
        assert validator.validate_date_format("2024-01-01") is True
        assert validator.validate_date_format("2023-12-31") is True
        
        # 无效日期格式
        assert validator.validate_date_format("2024/01/01") is False
        assert validator.validate_date_format("01-01-2024") is False
        assert validator.validate_date_format("invalid") is False
    
    def test_validate_date_range(self):
        """测试日期范围验证"""
        validator = InputValidator()
        
        # 有效日期范围
        assert validator.validate_date_range("2024-01-01", "2024-01-31") is True
        assert validator.validate_date_range("2024-01-01", "2024-01-01") is True
        
        # 开始日期晚于结束日期
        assert validator.validate_date_range("2024-01-31", "2024-01-01") is False
        
        # 未来日期
        future_date = "2025-12-31"
        assert validator.validate_date_range("2024-01-01", future_date) is False
    
    def test_validate_provider(self):
        """测试云服务提供商验证"""
        validator = InputValidator()
        
        # 有效的提供商
        assert validator.validate_provider("aws") is True
        assert validator.validate_provider("aliyun") is True
        assert validator.validate_provider("tencent") is True
        assert validator.validate_provider("volcengine") is True
        
        # 无效的提供商
        assert validator.validate_provider("invalid") is False
        assert validator.validate_provider("") is False
    
    def test_validate_region(self):
        """测试区域验证"""
        validator = InputValidator()
        
        # AWS区域
        assert validator.validate_region("us-east-1", "aws") is True
        assert validator.validate_region("eu-west-1", "aws") is True
        
        # 阿里云区域
        assert validator.validate_region("cn-hangzhou", "aliyun") is True
        assert validator.validate_region("cn-beijing", "aliyun") is True
        
        # 无效区域
        assert validator.validate_region("", "aws") is False
        assert validator.validate_region("invalid", "aws") is False
    
    def test_validate_granularity(self):
        """测试数据粒度验证"""
        validator = InputValidator()
        
        # 有效的粒度
        assert validator.validate_granularity("DAILY") is True
        assert validator.validate_granularity("MONTHLY") is True
        assert validator.validate_granularity("HOURLY") is True
        
        # 无效的粒度
        assert validator.validate_granularity("invalid") is False
        assert validator.validate_granularity("") is False


class TestConfigEncryption:
    """配置加密测试"""
    
    def test_encrypt_decrypt_config(self):
        """测试配置加密和解密"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            config_file = Path(temp_dir) / "test_config.enc"
            
            # 创建加密器
            encryption = ConfigEncryption(str(key_file))
            
            # 测试配置
            test_config = {
                "aws": {
                    "access_key": "test_key",
                    "secret_key": "test_secret"
                },
                "database": {
                    "host": "localhost",
                    "port": 5432
                }
            }
            
            # 加密配置
            success = encryption.encrypt_config(test_config, str(config_file))
            assert success is True
            assert config_file.exists()
            
            # 解密配置
            decrypted_config = encryption.decrypt_config(str(config_file))
            assert decrypted_config == test_config
    
    def test_encrypt_invalid_config(self):
        """测试无效配置加密"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            config_file = Path(temp_dir) / "test_config.enc"
            
            encryption = ConfigEncryption(str(key_file))
            
            # 测试无法序列化的配置
            invalid_config = {
                "function": lambda x: x  # 无法序列化
            }
            
            success = encryption.encrypt_config(invalid_config, str(config_file))
            assert success is False
    
    def test_decrypt_nonexistent_file(self):
        """测试解密不存在的文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_file = Path(temp_dir) / "test_key"
            nonexistent_file = Path(temp_dir) / "nonexistent.enc"
            
            encryption = ConfigEncryption(str(key_file))
            
            result = encryption.decrypt_config(str(nonexistent_file))
            assert result is None


class TestSecurityManager:
    """安全管理器测试"""
    
    def test_validate_analysis_request_valid(self):
        """测试有效分析请求验证"""
        manager = SecurityManager()
        
        request_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "providers": ["aws", "aliyun"],
            "granularity": "MONTHLY"
        }
        
        result = manager.validate_analysis_request(request_data)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_analysis_request_invalid_dates(self):
        """测试无效日期分析请求验证"""
        manager = SecurityManager()
        
        request_data = {
            "start_date": "2024-01-31",  # 开始日期晚于结束日期
            "end_date": "2024-01-01",
            "providers": ["aws"],
            "granularity": "MONTHLY"
        }
        
        result = manager.validate_analysis_request(request_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("日期范围无效" in error for error in result["errors"])
    
    def test_validate_analysis_request_invalid_provider(self):
        """测试无效提供商分析请求验证"""
        manager = SecurityManager()
        
        request_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "providers": ["invalid_provider"],
            "granularity": "MONTHLY"
        }
        
        result = manager.validate_analysis_request(request_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("不支持的云服务提供商" in error for error in result["errors"])
    
    def test_sanitize_output(self):
        """测试输出数据清理"""
        manager = SecurityManager()
        
        data = {
            "username": "testuser",
            "password": "secret123",
            "api_key": "AKIAIOSFODNN7EXAMPLE",
            "normal_field": "normal_value"
        }
        
        sanitized = manager.sanitize_output(data)
        
        assert sanitized["username"] == "testuser"
        assert sanitized["password"] == "***MASKED***"
        assert sanitized["api_key"] == "***MASKED***"
        assert sanitized["normal_field"] == "normal_value"


class TestCostAnalysisRequest:
    """成本分析请求模型测试"""
    
    def test_valid_request(self):
        """测试有效请求"""
        request = CostAnalysisRequest(
            providers=[CloudProvider.AWS, CloudProvider.ALIYUN],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            granularity=Granularity.MONTHLY
        )
        
        assert request.providers == [CloudProvider.AWS, CloudProvider.ALIYUN]
        assert request.start_date == date(2024, 1, 1)
        assert request.end_date == date(2024, 1, 31)
        assert request.granularity == Granularity.MONTHLY
    
    def test_invalid_date_range(self):
        """测试无效日期范围"""
        with pytest.raises(ValueError, match="结束日期不能早于开始日期"):
            CostAnalysisRequest(
                providers=[CloudProvider.AWS],
                start_date=date(2024, 1, 31),
                end_date=date(2024, 1, 1),
                granularity=Granularity.MONTHLY
            )
    
    def test_future_date(self):
        """测试未来日期"""
        future_date = date(2025, 12, 31)
        
        with pytest.raises(ValueError, match="日期不能是未来时间"):
            CostAnalysisRequest(
                providers=[CloudProvider.AWS],
                start_date=future_date,
                end_date=future_date,
                granularity=Granularity.MONTHLY
            )
    
    def test_date_range_limit(self):
        """测试日期范围限制"""
        with pytest.raises(ValueError, match="日期范围不能超过2年"):
            CostAnalysisRequest(
                providers=[CloudProvider.AWS],
                start_date=date(2022, 1, 1),
                end_date=date(2024, 1, 1),  # 超过2年
                granularity=Granularity.MONTHLY
            )
