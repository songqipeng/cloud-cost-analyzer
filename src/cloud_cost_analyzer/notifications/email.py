"""
邮件通知模块
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional
from ..utils.config import Config


class EmailNotifier:
    """邮件通知类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化邮件通知器
        
        Args:
            config: 邮件配置
        """
        self.config = config
        self.email_config = config.get("notifications", {}).get("email", {})
    
    def is_enabled(self) -> bool:
        """检查邮件通知是否启用"""
        return self.email_config.get("enabled", False)
    
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """验证邮件配置"""
        if not self.is_enabled():
            return True, None
        
        required_fields = ["smtp_server", "smtp_port", "sender_email", "sender_password", "recipient_email"]
        for field in required_fields:
            if not self.email_config.get(field):
                return False, f"邮件配置不完整，缺少 {field}"
        
        return True, None
    
    def send_notification(
        self,
        subject: str,
        body: str,
        attachment_path: Optional[str] = None
    ) -> bool:
        """
        发送邮件通知
        
        Args:
            subject: 邮件主题
            body: 邮件正文
            attachment_path: 附件路径
            
        Returns:
            发送是否成功
        """
        if not self.is_enabled():
            return False
        
        # 验证配置
        is_valid, error_msg = self.validate_config()
        if not is_valid:
            print(f"⚠️  {error_msg}，跳过邮件通知")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.email_config["sender_email"]
            msg['To'] = self.email_config["recipient_email"]
            msg['Subject'] = subject
            
            # 添加邮件正文
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # 添加附件（如果有）
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
            
            # 连接SMTP服务器并发送邮件
            server = smtplib.SMTP(
                self.email_config["smtp_server"],
                self.email_config["smtp_port"],
                timeout=Config.EMAIL_TIMEOUT
            )
            
            if self.email_config.get("use_tls", True):
                server.starttls()
            
            server.login(
                self.email_config["sender_email"],
                self.email_config["sender_password"]
            )
            
            text = msg.as_string()
            server.sendmail(
                self.email_config["sender_email"],
                self.email_config["recipient_email"],
                text
            )
            server.quit()
            
            print(f"✅ 邮件发送成功")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"⚠️  邮件认证失败: {e}，跳过邮件通知")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            print(f"⚠️  邮件收件人拒绝: {e}，跳过邮件通知")
            return False
        except smtplib.SMTPServerDisconnected as e:
            print(f"⚠️  SMTP服务器连接断开: {e}，跳过邮件通知")
            return False
        except smtplib.SMTPException as e:
            print(f"⚠️  SMTP错误: {e}，跳过邮件通知")
            return False
        except Exception as e:
            print(f"⚠️  邮件发送失败: {e}，跳过邮件通知")
            return False
    
    def format_cost_report_email(
        self,
        cost_summary: Dict[str, float],
        service_costs: Any,
        region_costs: Any,
        time_range: str = ""
    ) -> str:
        """
        格式化费用报告邮件内容
        
        Args:
            cost_summary: 费用摘要
            service_costs: 服务费用统计
            region_costs: 区域费用统计
            time_range: 时间范围
            
        Returns:
            格式化的邮件内容
        """
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .summary {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .section {{ margin: 20px 0; }}
                .table {{ border-collapse: collapse; width: 100%; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .table th {{ background-color: #f2f2f2; }}
                .highlight {{ color: #d73502; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📊 AWS费用分析报告</h2>
                <p>时间范围: {time_range}</p>
            </div>
            
            <div class="summary">
                <h3>💰 费用摘要</h3>
                <ul>
                    <li>总费用: <span class="highlight">${cost_summary['total_cost']:.2f}</span></li>
                    <li>平均每日费用: <span class="highlight">${cost_summary['avg_daily_cost']:.2f}</span></li>
                    <li>最高单日费用: <span class="highlight">${cost_summary['max_daily_cost']:.2f}</span></li>
                    <li>最低单日费用: <span class="highlight">${cost_summary['min_daily_cost']:.2f}</span></li>
                </ul>
            </div>
        """
        
        # 添加服务费用统计
        if service_costs is not None and not service_costs.empty:
            html_content += """
            <div class="section">
                <h3>🔧 按服务分析</h3>
                <table class="table">
                    <tr>
                        <th>服务</th>
                        <th>总费用</th>
                        <th>平均费用</th>
                        <th>记录数</th>
                    </tr>
            """
            
            for service, row in service_costs.head(10).iterrows():
                html_content += f"""
                    <tr>
                        <td>{service}</td>
                        <td>${row['总费用']:.2f}</td>
                        <td>${row['平均费用']:.2f}</td>
                        <td>{row['记录数']}</td>
                    </tr>
                """
            
            html_content += "</table></div>"
        
        # 添加区域费用统计
        if region_costs is not None and not region_costs.empty:
            html_content += """
            <div class="section">
                <h3>🌍 按区域分析</h3>
                <table class="table">
                    <tr>
                        <th>区域</th>
                        <th>总费用</th>
                        <th>平均费用</th>
                        <th>记录数</th>
                    </tr>
            """
            
            for region, row in region_costs.head(10).iterrows():
                html_content += f"""
                    <tr>
                        <td>{region}</td>
                        <td>${row['总费用']:.2f}</td>
                        <td>${row['平均费用']:.2f}</td>
                        <td>{row['记录数']}</td>
                    </tr>
                """
            
            html_content += "</table></div>"
        
        html_content += """
            <div class="section">
                <p><em>此报告由AWS费用分析器自动生成</em></p>
            </div>
        </body>
        </html>
        """
        
        return html_content
