"""
Defines the Pydantic models for application configuration.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, SecretStr


class EmailSettings(BaseModel):
    enabled: bool = False
    smtp_server: str
    smtp_port: int = 587
    sender_email: str
    sender_password: SecretStr
    recipient_email: str
    use_tls: bool = True


class FeishuSettings(BaseModel):
    enabled: bool = False
    webhook_url: str
    secret: Optional[SecretStr] = None


class NotificationSettings(BaseModel):
    email: EmailSettings
    feishu: FeishuSettings


class ScheduleSettings(BaseModel):
    enabled: bool = False
    time: str = "09:00"
    timezone: str = "Asia/Shanghai"
    analysis_type: Literal["quick", "custom"] = "quick"
    auto_install: bool = True
    cron_comment: str = "Cloud Cost Analyzer - Daily Analysis"


class AWSSettings(BaseModel):
    default_region: str = "us-east-1"
    cost_threshold: float = Field(0.01, description="The minimum cost to be included in the analysis.")


class AppSettings(BaseModel):
    """Top-level application settings model."""
    notifications: NotificationSettings
    schedule: ScheduleSettings
    aws: AWSSettings
