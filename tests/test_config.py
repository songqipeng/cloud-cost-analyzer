"""
配置管理测试
"""
import pytest
import os
import tempfile
import json
from src.cloud_cost_analyzer.utils.config import Config


class TestConfig:
    """配置管理测试类"""
    
    def test_get_email_provider_config(self):
        """测试获取邮件服务商配置"""
        # 测试Gmail配置
        gmail_config = Config.get_email_provider_config('gmail')
        assert gmail_config.smtp_server == 'smtp.gmail.com'
        assert gmail_config.smtp_port == 587
        assert gmail_config.use_tls == True
        
        # 测试QQ配置
        qq_config = Config.get_email_provider_config('qq')
        assert qq_config.smtp_server == 'smtp.qq.com'
        assert qq_config.smtp_port == 587
        
        # 测试默认配置
        default_config = Config.get_email_provider_config('unknown')
        assert default_config.smtp_server == 'smtp.gmail.com'
    
    def test_get_default_config(self):
        """测试获取默认配置"""
        config = Config.get_default_config()
        
        # 检查基本结构
        assert 'aws' in config
        assert 'notifications' in config
        assert 'schedule' in config
        
        # 检查AWS配置
        assert config['aws']['region'] == 'us-east-1'
        
        # 检查通知配置
        assert config['notifications']['email']['enabled'] == False
        assert config['notifications']['feishu']['enabled'] == False
        
        # 检查定时任务配置
        assert config['schedule']['enabled'] == False
        assert config['schedule']['time'] == '09:00'
    
    def test_get_chart_config(self):
        """测试获取图表配置"""
        # 测试默认配置
        config = {}
        chart_config = Config.get_chart_config(config)
        assert chart_config['colors'] == Config.DEFAULT_CHART_COLORS
        assert chart_config['style'] == Config.DEFAULT_CHART_STYLE
        assert chart_config['max_services_display'] == Config.MAX_SERVICES_DISPLAY
        
        # 测试自定义配置
        custom_config = {
            'chart': {
                'colors': ['#FF0000', '#00FF00'],
                'style': 'custom-style',
                'max_services_display': 5
            }
        }
        chart_config = Config.get_chart_config(custom_config)
        assert chart_config['colors'] == ['#FF0000', '#00FF00']
        assert chart_config['style'] == 'custom-style'
        assert chart_config['max_services_display'] == 5
    
    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # 测试配置
            test_config = {
                'test': 'value',
                'nested': {
                    'key': 'value'
                }
            }
            
            # 临时修改配置文件路径
            original_config_file = Config.CONFIG_FILE
            Config.CONFIG_FILE = temp_file
            
            # 保存配置
            assert Config.save_config(test_config) == True
            
            # 加载配置
            loaded_config = Config.load_config()
            # 由于环境变量覆盖，配置可能包含额外的字段
            assert loaded_config['test'] == test_config['test']
            assert loaded_config['nested'] == test_config['nested']
            
        finally:
            # 恢复原始配置
            Config.CONFIG_FILE = original_config_file
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)
