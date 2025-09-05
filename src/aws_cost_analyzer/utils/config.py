"""
配置管理模块
"""
import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class EmailProviderConfig:
    """邮件服务提供商配置"""
    smtp_server: str
    smtp_port: int
    use_tls: bool
    description: str


class Config:
    """配置管理类"""
    
    # AWS配置
    DEFAULT_REGION = 'us-east-1'
    DEFAULT_GRANULARITY = 'MONTHLY'
    
    # 图表配置（可从配置文件覆盖）
    DEFAULT_CHART_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    DEFAULT_CHART_STYLE = 'seaborn-v0_8'
    
    # 显示配置
    MAX_SERVICES_DISPLAY = 10
    MAX_REGIONS_DISPLAY = 10
    COST_THRESHOLD = 0.01  # 最小显示费用阈值
    
    # 文件配置
    CONFIG_FILE = 'config.json'
    CONFIG_EXAMPLE_FILE = 'config.example.json'
    
    # 通知配置
    EMAIL_TIMEOUT = 30
    FEISHU_TIMEOUT = 10
    
    @staticmethod
    def get_email_provider_config(provider: str) -> EmailProviderConfig:
        """获取邮件服务提供商配置"""
        providers = {
            'gmail': EmailProviderConfig(
                smtp_server='smtp.gmail.com',
                smtp_port=587,
                use_tls=True,
                description='Gmail - 需要应用专用密码'
            ),
            'qq': EmailProviderConfig(
                smtp_server='smtp.qq.com',
                smtp_port=587,
                use_tls=True,
                description='QQ邮箱 - 需要开启SMTP服务并获取授权码'
            ),
            'outlook': EmailProviderConfig(
                smtp_server='smtp-mail.outlook.com',
                smtp_port=587,
                use_tls=True,
                description='Outlook - 使用账户密码'
            ),
            '163': EmailProviderConfig(
                smtp_server='smtp.163.com',
                smtp_port=25,
                use_tls=False,
                description='163邮箱 - 需要开启SMTP服务'
            )
        }
        return providers.get(provider, providers['gmail'])
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """加载配置文件"""
        config = {}
        
        # 从文件加载配置
        if os.path.exists(Config.CONFIG_FILE):
            try:
                with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}")
                config = {}
        
        # 从环境变量覆盖敏感配置
        config = Config._apply_env_overrides(config)
        
        return config
    
    @staticmethod
    def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        # 邮件配置环境变量覆盖
        if 'notifications' not in config:
            config['notifications'] = {}
        if 'email' not in config['notifications']:
            config['notifications']['email'] = {}
        
        email_config = config['notifications']['email']
        
        # 环境变量优先级更高
        if os.getenv('AWS_ANALYZER_EMAIL_PASSWORD'):
            email_config['sender_password'] = os.getenv('AWS_ANALYZER_EMAIL_PASSWORD')
        if os.getenv('AWS_ANALYZER_SENDER_EMAIL'):
            email_config['sender_email'] = os.getenv('AWS_ANALYZER_SENDER_EMAIL')
        if os.getenv('AWS_ANALYZER_RECIPIENT_EMAIL'):
            email_config['recipient_email'] = os.getenv('AWS_ANALYZER_RECIPIENT_EMAIL')
        if os.getenv('AWS_ANALYZER_SMTP_SERVER'):
            email_config['smtp_server'] = os.getenv('AWS_ANALYZER_SMTP_SERVER')
        if os.getenv('AWS_ANALYZER_SMTP_PORT'):
            email_config['smtp_port'] = int(os.getenv('AWS_ANALYZER_SMTP_PORT'))
        
        # 飞书配置环境变量覆盖
        if 'feishu' not in config['notifications']:
            config['notifications']['feishu'] = {}
        
        feishu_config = config['notifications']['feishu']
        if os.getenv('AWS_ANALYZER_FEISHU_WEBHOOK'):
            feishu_config['webhook_url'] = os.getenv('AWS_ANALYZER_FEISHU_WEBHOOK')
        if os.getenv('AWS_ANALYZER_FEISHU_SECRET'):
            feishu_config['secret'] = os.getenv('AWS_ANALYZER_FEISHU_SECRET')
        
        return config
    
    @staticmethod
    def get_chart_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """获取图表配置"""
        chart_config = config.get('chart', {})
        return {
            'colors': chart_config.get('colors', Config.DEFAULT_CHART_COLORS),
            'style': chart_config.get('style', Config.DEFAULT_CHART_STYLE),
            'max_services_display': chart_config.get('max_services_display', Config.MAX_SERVICES_DISPLAY),
            'max_regions_display': chart_config.get('max_regions_display', Config.MAX_REGIONS_DISPLAY),
            'cost_threshold': chart_config.get('cost_threshold', Config.COST_THRESHOLD)
        }
    
    @staticmethod
    def save_config(config: Dict[str, Any]) -> bool:
        """保存配置文件"""
        try:
            with open(Config.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")
            return False
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "aws": {
                "region": Config.DEFAULT_REGION,
                "profile": None
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "provider": "gmail",
                    "smtp_server": "",
                    "smtp_port": 587,
                    "use_tls": True,
                    "sender_email": "",
                    "sender_password": "",
                    "recipient_email": ""
                },
                "feishu": {
                    "enabled": False,
                    "webhook_url": "",
                    "secret": ""
                }
            },
            "schedule": {
                "enabled": False,
                "time": "09:00",
                "timezone": "Asia/Shanghai",
                "analysis_type": "quick",
                "auto_install": True,
                "cron_comment": "AWS Cost Analyzer"
            }
        }
