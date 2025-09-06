"""
数据验证器测试
"""
import pytest
from datetime import datetime
from src.cloud_cost_analyzer.utils.validators import DataValidator


class TestDataValidator:
    """数据验证器测试类"""
    
    def test_validate_date_format_valid(self):
        """测试有效日期格式"""
        assert DataValidator.validate_date_format("2024-01-01") == True
        assert DataValidator.validate_date_format("2024-12-31") == True
    
    def test_validate_date_format_invalid(self):
        """测试无效日期格式"""
        assert DataValidator.validate_date_format("2024/01/01") == False
        assert DataValidator.validate_date_format("01-01-2024") == False
        assert DataValidator.validate_date_format("invalid") == False
    
    def test_validate_date_range_valid(self):
        """测试有效日期范围"""
        is_valid, error = DataValidator.validate_date_range("2024-01-01", "2024-12-31")
        assert is_valid == True
        assert error is None
    
    def test_validate_date_range_invalid(self):
        """测试无效日期范围"""
        # 开始日期晚于结束日期
        is_valid, error = DataValidator.validate_date_range("2024-12-31", "2024-01-01")
        assert is_valid == False
        assert "开始日期不能晚于结束日期" in error
        
        # 日期范围超过2年
        is_valid, error = DataValidator.validate_date_range("2020-01-01", "2024-12-31")
        assert is_valid == False
        assert "日期范围不能超过2年" in error
    
    def test_validate_email_valid(self):
        """测试有效邮箱格式"""
        assert DataValidator.validate_email("test@example.com") == True
        assert DataValidator.validate_email("user.name+tag@domain.co.uk") == True
    
    def test_validate_email_invalid(self):
        """测试无效邮箱格式"""
        assert DataValidator.validate_email("invalid-email") == False
        assert DataValidator.validate_email("@domain.com") == False
        assert DataValidator.validate_email("user@") == False
    
    def test_validate_webhook_url_valid(self):
        """测试有效webhook URL"""
        valid_url = "https://open.feishu.cn/open-apis/bot/v2/hook/12345678-1234-1234-1234-123456789abc"
        assert DataValidator.validate_webhook_url(valid_url) == True
    
    def test_validate_webhook_url_invalid(self):
        """测试无效webhook URL"""
        assert DataValidator.validate_webhook_url("https://example.com/webhook") == False
        assert DataValidator.validate_webhook_url("invalid-url") == False
    
    def test_validate_time_format_valid(self):
        """测试有效时间格式"""
        assert DataValidator.validate_time_format("09:00") == True
        assert DataValidator.validate_time_format("23:59") == True
    
    def test_validate_time_format_invalid(self):
        """测试无效时间格式"""
        assert DataValidator.validate_time_format("25:00") == False
        assert DataValidator.validate_time_format("invalid") == False
        assert DataValidator.validate_time_format("9:60") == False
