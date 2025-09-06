"""
配置向导模块
"""
import os
import json
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

from .config import Config


class ConfigWizard:
    """配置向导类"""
    
    def __init__(self):
        self.console = Console()
    
    def run_wizard(self) -> Dict[str, Any]:
        """运行配置向导"""
        self.console.print(Panel.fit(
            "[bold blue]🔧 Cloud Cost Analyzer 配置向导[/bold blue]\n"
            "这个向导将帮助您配置Cloud Cost Analyzer",
            border_style="blue"
        ))
        
        config = {}
        
        # 云平台配置
        config.update(self._configure_cloud_platforms())
        
        # 通知配置
        config.update(self._configure_notifications())
        
        # 定时任务配置
        config.update(self._configure_schedule())
        
        # 保存配置
        if self._save_config(config):
            self.console.print("\n[green]✅ 配置已保存到 config.json[/green]")
        else:
            self.console.print("\n[red]❌ 配置保存失败[/red]")
        
        return config
    
    def _configure_cloud_platforms(self) -> Dict[str, Any]:
        """配置云平台"""
        self.console.print("\n[bold]🌐 云平台配置[/bold]")
        
        config = {}
        
        # AWS配置
        if Confirm.ask("是否配置AWS？"):
            config['aws'] = self._configure_aws()
        
        # 阿里云配置
        if Confirm.ask("是否配置阿里云？"):
            config['aliyun'] = self._configure_aliyun()
        
        # 腾讯云配置
        if Confirm.ask("是否配置腾讯云？"):
            config['tencent'] = self._configure_tencent()
        
        # 火山云配置
        if Confirm.ask("是否配置火山云？"):
            config['volcengine'] = self._configure_volcengine()
        
        return config
    
    def _configure_aws(self) -> Dict[str, Any]:
        """配置AWS"""
        self.console.print("\n[yellow]☁️ AWS配置[/yellow]")
        
        region = Prompt.ask(
            "AWS区域", 
            default="us-east-1",
            choices=["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        )
        
        self.console.print(
            "[dim]请确保已配置AWS凭证（环境变量或AWS CLI）[/dim]"
        )
        
        return {
            "default_region": region,
            "cost_threshold": 0.01
        }
    
    def _configure_aliyun(self) -> Dict[str, Any]:
        """配置阿里云"""
        self.console.print("\n[yellow]☁️ 阿里云配置[/yellow]")
        
        region = Prompt.ask(
            "阿里云区域",
            default="cn-hangzhou",
            choices=["cn-hangzhou", "cn-beijing", "cn-shanghai", "cn-shenzhen"]
        )
        
        access_key_id = Prompt.ask("AccessKey ID", password=True)
        access_key_secret = Prompt.ask("AccessKey Secret", password=True)
        
        return {
            "enabled": True,
            "default_region": region,
            "access_key_id": access_key_id,
            "access_key_secret": access_key_secret,
            "cost_threshold": 0.01
        }
    
    def _configure_tencent(self) -> Dict[str, Any]:
        """配置腾讯云"""
        self.console.print("\n[yellow]☁️ 腾讯云配置[/yellow]")
        
        region = Prompt.ask(
            "腾讯云区域",
            default="ap-beijing",
            choices=["ap-beijing", "ap-shanghai", "ap-guangzhou", "ap-chengdu"]
        )
        
        secret_id = Prompt.ask("SecretId", password=True)
        secret_key = Prompt.ask("SecretKey", password=True)
        
        return {
            "enabled": True,
            "default_region": region,
            "secret_id": secret_id,
            "secret_key": secret_key,
            "cost_threshold": 0.01
        }
    
    def _configure_volcengine(self) -> Dict[str, Any]:
        """配置火山云"""
        self.console.print("\n[yellow]☁️ 火山云配置[/yellow]")
        
        region = Prompt.ask(
            "火山云区域",
            default="cn-beijing",
            choices=["cn-beijing", "cn-shanghai", "cn-guangzhou"]
        )
        
        access_key_id = Prompt.ask("AccessKey ID", password=True)
        secret_access_key = Prompt.ask("Secret Access Key", password=True)
        
        return {
            "enabled": True,
            "default_region": region,
            "access_key_id": access_key_id,
            "secret_access_key": secret_access_key,
            "cost_threshold": 0.01
        }
    
    def _configure_notifications(self) -> Dict[str, Any]:
        """配置通知"""
        self.console.print("\n[bold]🔔 通知配置[/bold]")
        
        notifications = {}
        
        # 邮件通知
        if Confirm.ask("是否配置邮件通知？"):
            notifications['email'] = self._configure_email()
        
        # 飞书通知
        if Confirm.ask("是否配置飞书通知？"):
            notifications['feishu'] = self._configure_feishu()
        
        return {"notifications": notifications} if notifications else {}
    
    def _configure_email(self) -> Dict[str, Any]:
        """配置邮件"""
        self.console.print("\n[yellow]📧 邮件配置[/yellow]")
        
        provider = Prompt.ask(
            "邮件服务商",
            choices=["gmail", "qq", "outlook", "163"],
            default="gmail"
        )
        
        provider_config = Config.get_email_provider_config(provider)
        
        smtp_server = Prompt.ask("SMTP服务器", default=provider_config.smtp_server)
        smtp_port = int(Prompt.ask("SMTP端口", default=str(provider_config.smtp_port)))
        sender_email = Prompt.ask("发送邮箱")
        sender_password = Prompt.ask("邮箱密码/授权码", password=True)
        recipient_email = Prompt.ask("接收邮箱")
        
        return {
            "enabled": True,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "use_tls": provider_config.use_tls,
            "sender_email": sender_email,
            "sender_password": sender_password,
            "recipient_email": recipient_email
        }
    
    def _configure_feishu(self) -> Dict[str, Any]:
        """配置飞书"""
        self.console.print("\n[yellow]💬 飞书配置[/yellow]")
        
        webhook_url = Prompt.ask("飞书机器人Webhook URL")
        secret = Prompt.ask("飞书机器人密钥", password=True)
        
        return {
            "enabled": True,
            "webhook_url": webhook_url,
            "secret": secret
        }
    
    def _configure_schedule(self) -> Dict[str, Any]:
        """配置定时任务"""
        self.console.print("\n[bold]⏰ 定时任务配置[/bold]")
        
        if not Confirm.ask("是否配置定时任务？"):
            return {}
        
        time = Prompt.ask("执行时间 (HH:MM)", default="08:00")
        timezone = Prompt.ask("时区", default="Asia/Shanghai")
        analysis_type = Prompt.ask(
            "分析类型",
            choices=["quick", "custom", "multi-cloud"],
            default="multi-cloud"
        )
        
        return {
            "schedule": {
                "enabled": True,
                "time": time,
                "timezone": timezone,
                "analysis_type": analysis_type,
                "auto_install": True,
                "cron_comment": "Cloud Cost Analyzer - Daily Analysis"
            }
        }
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            with open(Config.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.console.print(f"[red]配置保存失败: {e}[/red]")
            return False
