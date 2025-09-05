"""
数据验证模块
"""
import re
from datetime import datetime, date
from typing import Optional, Tuple, List
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class DataValidator:
    """数据验证类"""
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """验证日期格式"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
        """验证日期范围"""
        if not DataValidator.validate_date_format(start_date):
            return False, f"开始日期格式错误: {start_date}"
        
        if not DataValidator.validate_date_format(end_date):
            return False, f"结束日期格式错误: {end_date}"
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start > end:
                return False, "开始日期不能晚于结束日期"
            
            # 检查日期范围不能超过2年
            if (end - start).days > 730:
                return False, "日期范围不能超过2年"
            
            return True, None
        except Exception as e:
            return False, f"日期验证失败: {e}"
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_webhook_url(url: str) -> bool:
        """验证webhook URL格式"""
        pattern = r'^https://open\.feishu\.cn/open-apis/bot/v2/hook/[a-zA-Z0-9-]+$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """验证时间格式 (HH:MM)"""
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_aws_credentials(profile: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """验证AWS凭证"""
        try:
            session = boto3.Session(profile_name=profile)
            sts = session.client('sts')
            sts.get_caller_identity()
            return True, None
        except NoCredentialsError:
            return False, "未找到AWS凭证"
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidUserID.NotFound':
                return False, "AWS凭证无效"
            elif error_code == 'AccessDenied':
                return False, "AWS凭证权限不足"
            else:
                return False, f"AWS凭证验证失败: {error_code}"
        except Exception as e:
            return False, f"AWS凭证验证异常: {e}"
    
    @staticmethod
    def validate_cost_explorer_permissions(profile: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """验证Cost Explorer API权限"""
        try:
            session = boto3.Session(profile_name=profile)
            ce = session.client('ce')
            # 尝试获取费用数据来验证权限
            ce.get_cost_and_usage(
                TimePeriod={
                    'Start': '2024-01-01',
                    'End': '2024-01-02'
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            return True, None
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDenied':
                return False, "缺少Cost Explorer API访问权限"
            elif error_code == 'ThrottlingException':
                return False, "API调用频率过高，请稍后重试"
            else:
                return False, f"Cost Explorer权限验证失败: {error_code}"
        except Exception as e:
            return False, f"Cost Explorer权限验证异常: {e}"
    
    @staticmethod
    def validate_config(config: dict) -> Tuple[bool, List[str]]:
        """验证配置完整性"""
        errors = []
        
        # 验证邮件配置
        if config.get("notifications", {}).get("email", {}).get("enabled", False):
            email_config = config["notifications"]["email"]
            required_fields = ["smtp_server", "smtp_port", "sender_email", "sender_password", "recipient_email"]
            
            for field in required_fields:
                if not email_config.get(field):
                    errors.append(f"邮件配置缺少必要字段: {field}")
            
            # 验证邮箱格式
            if email_config.get("sender_email") and not DataValidator.validate_email(email_config["sender_email"]):
                errors.append("发送者邮箱格式错误")
            
            if email_config.get("recipient_email") and not DataValidator.validate_email(email_config["recipient_email"]):
                errors.append("接收者邮箱格式错误")
        
        # 验证飞书配置
        if config.get("notifications", {}).get("feishu", {}).get("enabled", False):
            feishu_config = config["notifications"]["feishu"]
            if not feishu_config.get("webhook_url"):
                errors.append("飞书配置缺少webhook_url")
            elif not DataValidator.validate_webhook_url(feishu_config["webhook_url"]):
                errors.append("飞书webhook URL格式错误")
        
        # 验证定时任务配置
        if config.get("schedule", {}).get("enabled", False):
            schedule_config = config["schedule"]
            if not DataValidator.validate_time_format(schedule_config.get("time", "")):
                errors.append("定时任务时间格式错误")
        
        return len(errors) == 0, errors
