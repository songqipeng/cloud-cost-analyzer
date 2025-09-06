"""
通知管理器
"""
from typing import Dict, Any, Optional
from datetime import datetime
from .email import EmailNotifier
from .feishu import FeishuNotifier


class NotificationManager:
    """通知管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.email_notifier = EmailNotifier(config)
        self.feishu_notifier = FeishuNotifier(config)
    
    def send_cost_report(
        self,
        cost_summary: Dict[str, float],
        service_costs: Any,
        region_costs: Any,
        time_range: str = "",
        subject_suffix: str = ""
    ) -> Dict[str, bool]:
        """
        发送费用报告通知
        
        Args:
            cost_summary: 费用摘要
            service_costs: 服务费用统计
            region_costs: 区域费用统计
            time_range: 时间范围
            subject_suffix: 主题后缀
            
        Returns:
            发送结果字典
        """
        print(f"\n📤 发送通知...")
        
        results = {
            'email': False,
            'feishu': False
        }
        
        # 生成主题和时间范围
        current_date = datetime.now().strftime('%Y-%m-%d')
        full_time_range = f"{current_date}{subject_suffix}"
        
        # 发送邮件通知
        if self.email_notifier.is_enabled():
            subject = f"AWS费用分析报告 - {full_time_range}"
            email_content = self.email_notifier.format_cost_report_email(
                cost_summary, service_costs, region_costs, time_range
            )
            results['email'] = self.email_notifier.send_notification(subject, email_content)
        else:
            print(f"📧 邮件通知未启用")
        
        # 发送飞书通知
        if self.feishu_notifier.is_enabled():
            title = f"AWS费用分析报告 - {full_time_range}"
            feishu_content = self.feishu_notifier.format_cost_report_feishu(
                cost_summary, service_costs, region_costs, time_range
            )
            results['feishu'] = self.feishu_notifier.send_notification(title, feishu_content)
        else:
            print(f"📱 飞书通知未启用")
        
        # 显示通知结果摘要
        if results['email'] or results['feishu']:
            print(f"✅ 通知发送完成")
        else:
            print(f"⚠️  没有成功发送任何通知")
        
        return results
    
    def send_simple_notification(self, message: str, notification_type: str = "info") -> Dict[str, bool]:
        """
        发送简单通知
        
        Args:
            message: 消息内容
            notification_type: 通知类型 (info, success, error)
            
        Returns:
            发送结果字典
        """
        results = {
            'email': False,
            'feishu': False
        }
        
        # 根据类型设置标题和内容
        if notification_type == "error":
            title = "AWS费用分析器 - 错误"
            content = f"**❌ 错误**\n\n{message}"
        elif notification_type == "success":
            title = "AWS费用分析器 - 成功"
            content = f"**✅ 成功**\n\n{message}"
        else:
            title = "AWS费用分析器"
            content = f"**ℹ️ 信息**\n\n{message}"
        
        # 发送邮件通知
        if self.email_notifier.is_enabled():
            results['email'] = self.email_notifier.send_notification(title, content)
        
        # 发送飞书通知
        if self.feishu_notifier.is_enabled():
            results['feishu'] = self.feishu_notifier.send_notification(title, content)
        
        return results
    
    def send_error_notification(self, error_message: str) -> Dict[str, bool]:
        """
        发送错误通知
        
        Args:
            error_message: 错误消息
            
        Returns:
            发送结果字典
        """
        return self.send_simple_notification(error_message, "error")
    
    def send_success_notification(self, success_message: str) -> Dict[str, bool]:
        """
        发送成功通知
        
        Args:
            success_message: 成功消息
            
        Returns:
            发送结果字典
        """
        return self.send_simple_notification(success_message, "success")
    
    def get_notification_status(self) -> Dict[str, Dict[str, Any]]:
        """
        获取通知状态
        
        Returns:
            通知状态字典
        """
        return {
            'email': {
                'enabled': self.email_notifier.is_enabled(),
                'valid': self.email_notifier.validate_config()[0]
            },
            'feishu': {
                'enabled': self.feishu_notifier.is_enabled(),
                'valid': self.feishu_notifier.validate_config()[0]
            }
        }
    
    def test_notifications(self) -> Dict[str, bool]:
        """
        测试通知功能
        
        Returns:
            测试结果字典
        """
        test_message = f"这是一条测试消息，发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self.send_simple_notification(test_message, "info")
