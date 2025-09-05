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
    
    # 图表配置
    CHART_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    CHART_STYLE = 'seaborn-v0_8'
    
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
        if os.path.exists(Config.CONFIG_FILE):
            try:
                with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}")
                return {}
        return {}
    
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
