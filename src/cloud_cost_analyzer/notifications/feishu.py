"""
飞书通知模块
"""
import requests
from typing import Dict, Any, Optional
from ..utils.config import Config


class FeishuNotifier:
    """飞书通知类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化飞书通知器
        
        Args:
            config: 飞书配置
        """
        self.config = config
        self.feishu_config = config.get("notifications", {}).get("feishu", {})
    
    def is_enabled(self) -> bool:
        """检查飞书通知是否启用"""
        return self.feishu_config.get("enabled", False)
    
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """验证飞书配置"""
        if not self.is_enabled():
            return True, None
        
        if not self.feishu_config.get("webhook_url"):
            return False, "飞书配置不完整，缺少 webhook_url"
        
        return True, None
    
    def send_notification(self, title: str, content: str) -> bool:
        """
        发送飞书通知
        
        Args:
            title: 消息标题
            content: 消息内容
            
        Returns:
            发送是否成功
        """
        if not self.is_enabled():
            return False
        
        # 验证配置
        is_valid, error_msg = self.validate_config()
        if not is_valid:
            print(f"⚠️  {error_msg}，跳过飞书通知")
            return False
        
        try:
            # 构建飞书消息
            message = {
                "msg_type": "interactive",
                "card": {
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "content": content,
                                "tag": "lark_md"
                            }
                        }
                    ],
                    "header": {
                        "title": {
                            "content": title,
                            "tag": "plain_text"
                        }
                    }
                }
            }
            
            # 发送请求
            response = requests.post(
                self.feishu_config["webhook_url"],
                json=message,
                timeout=Config.FEISHU_TIMEOUT
            )
            
            if response.status_code == 200:
                print(f"✅ 飞书消息发送成功")
                return True
            else:
                print(f"⚠️  飞书消息发送失败: {response.status_code} - {response.text}，跳过飞书通知")
                return False
                
        except requests.exceptions.Timeout:
            print(f"⚠️  飞书请求超时，跳过飞书通知")
            return False
        except requests.exceptions.ConnectionError:
            print(f"⚠️  飞书连接错误，跳过飞书通知")
            return False
        except requests.exceptions.RequestException as e:
            print(f"⚠️  飞书请求异常: {e}，跳过飞书通知")
            return False
        except Exception as e:
            print(f"⚠️  飞书消息发送失败: {e}，跳过飞书通知")
            return False
    
    def format_cost_report_feishu(
        self,
        cost_summary: Dict[str, float],
        service_costs: Any,
        region_costs: Any,
        time_range: str = ""
    ) -> str:
        """
        格式化费用报告飞书消息内容
        
        Args:
            cost_summary: 费用摘要
            service_costs: 服务费用统计
            region_costs: 区域费用统计
            time_range: 时间范围
            
        Returns:
            格式化的飞书消息内容
        """
        content = f"**📊 AWS费用分析报告**\n\n"
        content += f"**时间范围:** {time_range}\n\n"
        
        # 费用摘要
        content += "**💰 费用摘要:**\n"
        content += f"• 总费用: **${cost_summary['total_cost']:.2f}**\n"
        content += f"• 平均每日费用: **${cost_summary['avg_daily_cost']:.2f}**\n"
        content += f"• 最高单日费用: **${cost_summary['max_daily_cost']:.2f}**\n"
        content += f"• 最低单日费用: **${cost_summary['min_daily_cost']:.2f}**\n\n"
        
        # 服务费用统计
        if service_costs is not None and not service_costs.empty:
            content += "**🔧 按服务分析 (前5名):**\n"
            for service, row in service_costs.head(5).iterrows():
                content += f"• {service}: **${row['总费用']:.2f}**\n"
            content += "\n"
        
        # 区域费用统计
        if region_costs is not None and not region_costs.empty:
            content += "**🌍 按区域分析 (前5名):**\n"
            for region, row in region_costs.head(5).iterrows():
                content += f"• {region}: **${row['总费用']:.2f}**\n"
            content += "\n"
        
        content += "---\n"
        content += "*此报告由AWS费用分析器自动生成*"
        
        return content
    
    def send_simple_message(self, message: str) -> bool:
        """
        发送简单文本消息
        
        Args:
            message: 消息内容
            
        Returns:
            发送是否成功
        """
        return self.send_notification("AWS费用分析器", message)
    
    def send_error_notification(self, error_message: str) -> bool:
        """
        发送错误通知
        
        Args:
            error_message: 错误消息
            
        Returns:
            发送是否成功
        """
        content = f"**❌ AWS费用分析器错误**\n\n{error_message}"
        return self.send_notification("AWS费用分析器 - 错误", content)
    
    def send_success_notification(self, success_message: str) -> bool:
        """
        发送成功通知
        
        Args:
            success_message: 成功消息
            
        Returns:
            发送是否成功
        """
        content = f"**✅ AWS费用分析器成功**\n\n{success_message}"
        return self.send_notification("AWS费用分析器 - 成功", content)
