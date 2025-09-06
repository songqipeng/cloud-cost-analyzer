"""
报告生成器
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化报告生成器"""
        self.config = config
        self.console = Console()
        
    def generate_console_report(self, data: Dict[str, Any], provider: str) -> None:
        """生成控制台报告"""
        self.console.print(f"\n[bold blue]📊 {provider} 费用分析报告[/bold blue]")
        
        # 摘要信息
        summary = data.get('summary', {})
        self._print_summary_panel(summary, provider)
        
        # 按服务分析
        if 'by_service' in data:
            self._print_service_table(data['by_service'], f"{provider} 按服务费用分析")
        
        # 按区域分析
        if 'by_region' in data:
            self._print_region_table(data['by_region'], f"{provider} 按区域费用分析")
    
    def generate_multi_cloud_console_report(self, data: Dict[str, Any]) -> None:
        """生成多云控制台报告"""
        self.console.print("\n[bold green]🌐 多云费用分析报告[/bold green]")
        
        # 摘要信息
        summary = data.get('summary', {})
        self._print_multi_cloud_summary(summary)
        
        # 各云平台对比
        if 'by_provider' in data:
            self._print_provider_comparison_table(data['by_provider'])
        
        # 详细分析
        for provider_data in data.get('by_provider', []):
            if provider_data.get('success') and 'details' in provider_data:
                self._print_provider_details(provider_data)
    
    def _print_summary_panel(self, summary: Dict[str, Any], provider: str) -> None:
        """打印摘要面板"""
        total_cost = summary.get('total_cost', 0.0)
        currency = summary.get('currency', 'USD')
        days = summary.get('days', 0)
        avg_daily = summary.get('average_daily_cost', 0.0)
        
        content = f"""
        总费用: {total_cost:.2f} {currency}
        分析天数: {days} 天
        平均每日: {avg_daily:.2f} {currency}
        """
        
        self.console.print(Panel(content.strip(), title=f"{provider} 费用摘要", border_style="blue"))
    
    def _print_multi_cloud_summary(self, summary: Dict[str, Any]) -> None:
        """打印多云摘要"""
        total_providers = summary.get('total_providers', 0)
        successful = summary.get('successful_providers', 0)
        failed = summary.get('failed_providers', 0)
        
        content = f"""
        总云平台数: {total_providers}
        成功连接: {successful}
        连接失败: {failed}
        """
        
        self.console.print(Panel(content.strip(), title="多云分析摘要", border_style="green"))
    
    def _print_service_table(self, df, title: str) -> None:
        """打印服务费用表格"""
        if df.empty:
            return
            
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("服务", style="cyan", no_wrap=True)
        table.add_column("总费用", justify="right", style="green")
        table.add_column("平均费用", justify="right", style="yellow")
        table.add_column("记录数", justify="right", style="blue")
        
        for _, row in df.head(10).iterrows():  # 只显示前10个
            table.add_row(
                str(row.get('Service', '')),
                f"{row.get('Cost', 0.0):.2f}",
                f"{row.get('AvgCost', 0.0):.2f}",
                str(int(row.get('Count', 0)))
            )
        
        self.console.print(table)
    
    def _print_region_table(self, df, title: str) -> None:
        """打印区域费用表格"""
        if df.empty:
            return
            
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("区域", style="cyan", no_wrap=True)
        table.add_column("总费用", justify="right", style="green")
        table.add_column("记录数", justify="right", style="blue")
        
        for _, row in df.iterrows():
            table.add_row(
                str(row.get('Region', '')),
                f"{row.get('Cost', 0.0):.2f}",
                str(int(row.get('Count', 0)))
            )
        
        self.console.print(table)
    
    def _print_provider_comparison_table(self, providers: List[Dict[str, Any]]) -> None:
        """打印云平台对比表格"""
        table = Table(title="多云平台费用对比", show_header=True, header_style="bold magenta")
        table.add_column("云平台", style="cyan", no_wrap=True)
        table.add_column("总费用", justify="right", style="green")
        table.add_column("货币", justify="center", style="yellow")
        table.add_column("平均每日费用", justify="right", style="blue")
        table.add_column("记录数", justify="right", style="white")
        table.add_column("时间跨度", justify="right", style="magenta")
        
        for provider_data in providers:
            if not provider_data.get('success'):
                continue
                
            provider = provider_data.get('provider_name', 'Unknown')
            total_cost = provider_data.get('total_cost', 0.0)
            currency = provider_data.get('currency', 'Unknown')
            avg_daily = provider_data.get('avg_daily_cost', 0.0)
            record_count = provider_data.get('record_count', 0)
            days = provider_data.get('days', 0)
            
            table.add_row(
                provider,
                f"{total_cost:.2f}",
                currency,
                f"{avg_daily:.2f}",
                str(record_count),
                f"{days} 天"
            )
        
        self.console.print(table)
    
    def _print_provider_details(self, provider_data: Dict[str, Any]) -> None:
        """打印云平台详细信息"""
        provider = provider_data.get('provider_name', 'Unknown')
        details = provider_data.get('details', {})
        
        self.console.print(f"\n[bold]{provider} 详细分析[/bold]")
        
        if 'by_service' in details:
            self._print_service_table(details['by_service'], f"{provider} 服务费用")
        
        if 'by_region' in details:
            self._print_region_table(details['by_region'], f"{provider} 区域费用")
    
    def generate_text_report(self, data: Dict[str, Any], provider: str, output_dir: str) -> str:
        """生成文本报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{provider.lower()}_cost_analysis_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{provider} 费用分析报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 摘要
            summary = data.get('summary', {})
            f.write("费用摘要:\n")
            f.write(f"  总费用: {summary.get('total_cost', 0.0):.2f} {summary.get('currency', 'USD')}\n")
            f.write(f"  分析天数: {summary.get('days', 0)} 天\n")
            f.write(f"  平均每日: {summary.get('average_daily_cost', 0.0):.2f} {summary.get('currency', 'USD')}\n\n")
            
            # 按服务分析
            if 'by_service' in data and not data['by_service'].empty:
                f.write("按服务费用分析:\n")
                for _, row in data['by_service'].head(20).iterrows():
                    f.write(f"  {row.get('Service', '')}: {row.get('Cost', 0.0):.2f}\n")
                f.write("\n")
            
            # 按区域分析
            if 'by_region' in data and not data['by_region'].empty:
                f.write("按区域费用分析:\n")
                for _, row in data['by_region'].iterrows():
                    f.write(f"  {row.get('Region', '')}: {row.get('Cost', 0.0):.2f}\n")
        
        return filepath
    
    def generate_html_report(self, data: Dict[str, Any], provider: str, output_dir: str) -> str:
        """生成HTML报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{provider.lower()}_cost_analysis_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        html_content = self._generate_html_content(data, provider)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_multi_cloud_text_report(self, data: Dict[str, Any], output_dir: str) -> str:
        """生成多云文本报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multi_cloud_cost_analysis_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("多云费用分析报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 摘要
            summary = data.get('summary', {})
            f.write("分析摘要:\n")
            f.write(f"  总云平台数: {summary.get('total_providers', 0)}\n")
            f.write(f"  成功连接: {summary.get('successful_providers', 0)}\n")
            f.write(f"  连接失败: {summary.get('failed_providers', 0)}\n\n")
            
            # 各云平台对比
            f.write("云平台费用对比:\n")
            for provider_data in data.get('by_provider', []):
                if provider_data.get('success'):
                    provider = provider_data.get('provider_name', 'Unknown')
                    total_cost = provider_data.get('total_cost', 0.0)
                    currency = provider_data.get('currency', 'Unknown')
                    f.write(f"  {provider}: {total_cost:.2f} {currency}\n")
        
        return filepath
    
    def generate_multi_cloud_html_report(self, data: Dict[str, Any], output_dir: str) -> str:
        """生成多云HTML报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multi_cloud_cost_analysis_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        html_content = self._generate_multi_cloud_html_content(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def _generate_html_content(self, data: Dict[str, Any], provider: str) -> str:
        """生成HTML内容"""
        # 这里应该实现完整的HTML生成逻辑
        # 为了简化，暂时返回基本HTML结构
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{provider} 费用分析报告</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 15px; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{provider} 费用分析报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <h2>费用摘要</h2>
                <p>总费用: {data.get('summary', {}).get('total_cost', 0.0):.2f} {data.get('summary', {}).get('currency', 'USD')}</p>
                <p>分析天数: {data.get('summary', {}).get('days', 0)} 天</p>
            </div>
            
            <!-- 这里可以添加更多详细内容 -->
        </body>
        </html>
        """
    
    def _generate_multi_cloud_html_content(self, data: Dict[str, Any]) -> str:
        """生成多云HTML内容"""
        # 简化的HTML生成逻辑
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>多云费用分析报告</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 15px; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>多云费用分析报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <h2>分析摘要</h2>
                <p>总云平台数: {data.get('summary', {}).get('total_providers', 0)}</p>
                <p>成功连接: {data.get('summary', {}).get('successful_providers', 0)}</p>
            </div>
            
            <!-- 这里可以添加云平台对比表格和图表 -->
        </body>
        </html>
        """