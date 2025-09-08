"""
核心分析器模块
"""
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .client import AWSClient
from .data_processor import DataProcessor
from .cost_optimizer import CostOptimizationAnalyzer
from ..notifications.manager import NotificationManager
from ..reports.text_report import TextReportGenerator
from ..reports.html_report import HTMLReportGenerator
from ..utils.config import Config


class AWSCostAnalyzer:
    """AWS费用分析器核心类"""
    
    def __init__(self, profile: Optional[str] = None, region: str = 'us-east-1'):
        """
        初始化AWS费用分析器
        
        Args:
            profile: AWS配置文件名称
            region: AWS区域
        """
        self.profile = profile
        self.region = region
        self.client = AWSClient(profile, region)
        self.data_processor = DataProcessor(Config.COST_THRESHOLD)
        self.cost_optimizer = CostOptimizationAnalyzer()
        self.console = Console()
        
        # 报告生成器
        self.text_report_generator = TextReportGenerator()
        self.html_report_generator = HTMLReportGenerator()
        
        # 通知管理器
        self.notification_manager = None
    
    def initialize_notifications(self, config: Dict[str, Any]) -> None:
        """初始化通知管理器"""
        self.notification_manager = NotificationManager(config)
    
    def test_connection(self) -> tuple[bool, str]:
        """测试AWS连接"""
        return self.client.test_connection()
    
    def get_cost_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        granularity: str = 'MONTHLY'
    ) -> Optional[Dict[str, Any]]:
        """
        获取费用数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            granularity: 数据粒度
            
        Returns:
            费用数据字典
        """
        if not start_date or not end_date:
            # 默认获取过去1年的数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - relativedelta(years=1)).strftime('%Y-%m-%d')
        
        return self.client.get_cost_and_usage_with_retry(
            start_date, end_date, granularity
        )
    
    def analyze_costs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        granularity: str = 'MONTHLY',
        include_resource_details: bool = False,
        enable_optimization_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        分析费用数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            granularity: 数据粒度
            include_resource_details: 是否包含资源详细信息
            enable_optimization_analysis: 是否启用优化分析
            
        Returns:
            完整的分析结果字典
        """
        # 确保有默认日期
        if not start_date or not end_date:
            # 默认获取过去1年的数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - relativedelta(years=1)).strftime('%Y-%m-%d')
        
        # 获取基本费用数据
        cost_data = self.get_cost_data(start_date, end_date, granularity)
        if not cost_data:
            return {'error': 'Failed to retrieve cost data', 'data': None}
        
        # 解析费用数据
        df = self.data_processor.process(cost_data)
        if df.empty:
            return {'error': 'No cost data available', 'data': None}
        
        # 基础分析
        service_costs = self.data_processor.analyze_costs_by_service(df)
        region_costs = self.data_processor.analyze_costs_by_region(df)
        cost_summary = self.data_processor.get_cost_summary(df)
        
        # 构建结果字典
        analysis_result = {
            'data': df,
            'service_costs': service_costs,
            'region_costs': region_costs,
            'cost_summary': cost_summary,
            'top_services': self.data_processor.get_top_services(df),
            'top_regions': self.data_processor.get_top_regions(df)
        }
        
        # 资源级分析（如果启用）
        if include_resource_details:
            try:
                # 获取资源级费用数据
                resource_data = self.client.get_cost_by_resource(start_date, end_date, granularity='DAILY')
                if resource_data:
                    resource_df = self.data_processor.process(resource_data)
                    if not resource_df.empty:
                        # 使用基础分析方法
                        resource_service_costs = self.data_processor.analyze_costs_by_service(resource_df)
                        analysis_result['resource_costs'] = resource_service_costs
            except Exception as e:
                print(f"Warning: Could not retrieve resource details: {e}")
        
        # 异常检测
        try:
            anomalies = self.data_processor.detect_cost_anomalies(df)
            analysis_result['anomalies'] = anomalies
        except Exception as e:
            self.console.print(f"[yellow]Warning: Anomaly detection failed: {e}[/yellow]")
            analysis_result['anomalies'] = []
        
        # 成本优化分析（如果启用）
        if enable_optimization_analysis:
            try:
                # 使用资源费用数据，如果没有则为None
                resource_costs_data = analysis_result.get('resource_costs')
                optimization_report = self.cost_optimizer.analyze_cost_optimization_opportunities(
                    df, service_costs, resource_costs_data
                )
                analysis_result['optimization_report'] = optimization_report
            except Exception as e:
                print(f"Warning: Optimization analysis failed: {e}")
                analysis_result['optimization_report'] = {}
        
        return analysis_result
    
    def print_summary(self, df: pd.DataFrame) -> None:
        """打印费用摘要"""
        if df.empty:
            self.console.print("[red]没有费用数据可分析[/red]")
            return
        
        # 计算费用摘要
        cost_summary = self.data_processor.get_cost_summary(df)
        
        # 创建费用摘要表格
        table = Table(
            show_header=True,
            header_style="bold magenta",
            width=60,
            show_lines=True
        )
        table.add_column("费用类型", justify="left", style="white", width=20)
        table.add_column("金额", justify="right", style="cyan", width=15)
        
        table.add_row("总费用", f"${cost_summary['total_cost']:.2f}")
        table.add_row("平均每日费用", f"${cost_summary['avg_daily_cost']:.2f}")
        table.add_row("最高单日费用", f"${cost_summary['max_daily_cost']:.2f}")
        table.add_row("最低单日费用", f"${cost_summary['min_daily_cost']:.2f}")
        
        self.console.print(table)
    
    def print_service_analysis(self, service_costs: pd.DataFrame) -> None:
        """打印服务分析"""
        if service_costs.empty:
            self.console.print("[yellow]按服务分析: 无数据[/yellow]")
            return
        
        self.console.print("\n[bold blue]按服务分析:[/bold blue]")
        
        # 创建服务分析表格
        table = Table(
            show_header=True,
            header_style="bold magenta",
            width=80,
            show_lines=True
        )
        table.add_column("Service", justify="left", style="white", width=40)
        table.add_column("总费用", justify="right", style="cyan", width=15)
        table.add_column("平均费用", justify="right", style="cyan", width=15)
        table.add_column("记录数", justify="right", style="cyan", width=10)
        
        for service, row in service_costs.iterrows():
            table.add_row(
                service,
                f"${row['总费用']:.4f}",
                f"${row['平均费用']:.4f}",
                str(row['记录数'])
            )
        
        self.console.print(table)
    
    def print_region_analysis(self, region_costs: pd.DataFrame) -> None:
        """打印区域分析"""
        if region_costs.empty:
            self.console.print("[yellow]按区域分析: 无数据[/yellow]")
            return
        
        self.console.print("\n[bold blue]按区域分析:[/bold blue]")
        
        # 创建区域分析表格
        table = Table(
            show_header=True,
            header_style="bold magenta",
            width=80,
            show_lines=True
        )
        table.add_column("Region", justify="left", style="white", width=25)
        table.add_column("总费用", justify="right", style="cyan", width=15)
        table.add_column("平均费用", justify="right", style="cyan", width=15)
        table.add_column("记录数", justify="right", style="cyan", width=10)
        
        for region, row in region_costs.iterrows():
            table.add_row(
                region,
                f"${row['总费用']:.4f}",
                f"${row['平均费用']:.4f}",
                str(row['记录数'])
            )
        
        self.console.print(table)
    
    def print_enhanced_analysis_results(self, analysis_result: Dict[str, Any]) -> None:
        """打印增强的分析结果"""
        if 'error' in analysis_result:
            self.console.print(f"[red]Error: {analysis_result['error']}[/red]")
            return
        
        df = analysis_result.get('data')
        service_costs = analysis_result.get('service_costs')
        region_costs = analysis_result.get('region_costs')
        resource_costs = analysis_result.get('resource_costs')
        anomalies = analysis_result.get('anomalies', [])
        optimization_report = analysis_result.get('optimization_report', {})
        
        if df is None or df.empty:
            self.console.print("[red]没有数据可分析[/red]")
            return
        
        # 基础分析
        self.print_summary(df)
        if service_costs is not None and not service_costs.empty:
            self.print_service_analysis(service_costs)
        if region_costs is not None and not region_costs.empty:
            self.print_region_analysis(region_costs)
        
        # 资源分析
        if resource_costs is not None and not resource_costs.empty:
            self._print_resource_analysis(resource_costs)
        
        # 异常检测结果
        if anomalies:
            self._print_anomaly_analysis(anomalies)
        
        # 优化建议摘要
        if optimization_report:
            self._print_optimization_summary(optimization_report)
    
    def _print_resource_analysis(self, resource_costs: pd.DataFrame) -> None:
        """打印资源分析"""
        self.console.print("\n[bold blue]🔥 资源费用分析:[/bold blue]")
        
        table = Table(
            show_header=True,
            header_style="bold magenta", 
            width=100,
            show_lines=True
        )
        table.add_column("服务", justify="left", style="white", width=25)
        table.add_column("资源ID", justify="left", style="cyan", width=35)
        table.add_column("区域", justify="left", style="white", width=15)
        table.add_column("总费用", justify="right", style="green", width=12)
        table.add_column("记录数", justify="right", style="white", width=8)
        
        for _, row in resource_costs.head(10).iterrows():
            resource_id = str(row['ResourceId'])
            display_id = resource_id[:32] + "..." if len(resource_id) > 35 else resource_id
            
            table.add_row(
                row['Service'][:25],
                display_id,
                str(row['区域']),
                f"${row['总费用']:.2f}",
                str(row['记录数'])
            )
        
        self.console.print(table)
    
    def _print_anomaly_analysis(self, anomalies: List[Dict[str, Any]]) -> None:
        """打印异常分析"""
        self.console.print(f"\n[bold red]⚠️  检测到 {len(anomalies)} 个费用异常:[/bold red]")
        
        display_anomalies = anomalies[:5]  # 只显示前5个
        
        table = Table(
            show_header=True,
            header_style="bold magenta",
            width=80,
            show_lines=True
        )
        table.add_column("异常日期", justify="left", style="white", width=15)
        table.add_column("费用金额", justify="right", style="red", width=15)
        table.add_column("异常类型", justify="center", style="yellow", width=15)
        table.add_column("偏差程度", justify="right", style="cyan", width=15)
        
        for anomaly in display_anomalies:
            anomaly_type_display = "📈 高于正常" if anomaly['type'] == 'high' else "📉 低于正常"
            table.add_row(
                anomaly['date'].strftime('%Y-%m-%d'),
                f"${anomaly['cost']:.2f}",
                anomaly_type_display,
                f"{anomaly['deviation']:.1f}σ"
            )
        
        self.console.print(table)
    
    def _print_optimization_summary(self, optimization_report: Dict[str, Any]) -> None:
        """打印优化建议摘要"""
        total_savings = optimization_report.get('total_potential_savings', 0)
        priority_actions = optimization_report.get('priority_actions', [])
        
        # 潜在节省摘要
        panel_content = f"[bold green]💰 总潜在节省: ${total_savings:.2f}[/bold green]\n\n[bold cyan]🎯 优先行动计划:[/bold cyan]"
        
        for i, action in enumerate(priority_actions[:3], 1):
            priority_icon = "🔥" if action['priority'] == 0 else "⚡" if action['priority'] == 1 else "📋"
            savings = action.get('potential_savings', 0)
            description = action.get('description', '')[:55] + "..." if len(action.get('description', '')) > 55 else action.get('description', '')
            
            panel_content += f"\n{priority_icon} 行动 {i}: {description}"
            if savings > 0:
                panel_content += f" [green](${savings:.2f})[/green]"
        
        if len(priority_actions) > 3:
            panel_content += f"\n... 还有 {len(priority_actions) - 3} 个建议"
        
        panel = Panel(
            panel_content,
            title="🚀 成本优化建议",
            border_style="green",
            width=80
        )
        
        self.console.print(panel)
    
    def generate_reports(
        self,
        analysis_result: Dict[str, Any],
        output_dir: str = ".",
        formats: List[str] = ["txt", "html"]
    ) -> Dict[str, str]:
        """
        生成报告
        
        Args:
            analysis_result: 分析结果字典
            output_dir: 输出目录
            formats: 输出格式列表
            
        Returns:
            生成的文件路径字典
        """
        generated_files = {}
        
        if 'error' in analysis_result:
            self.console.print(f"[red]Error: {analysis_result['error']}[/red]")
            return generated_files
        
        # 提取数据
        df = analysis_result.get('data')
        service_costs = analysis_result.get('service_costs')
        region_costs = analysis_result.get('region_costs')
        resource_costs = analysis_result.get('resource_costs')
        anomalies = analysis_result.get('anomalies', [])
        optimization_report = analysis_result.get('optimization_report', {})
        
        if df is None or df.empty:
            self.console.print("[red]No data to generate reports[/red]")
            return generated_files
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if "txt" in formats:
            txt_file = f"{output_dir}/aws_cost_analysis_report_{timestamp}.txt"
            if self.text_report_generator.generate_cost_report(
                df, txt_file, service_costs, region_costs
            ):
                generated_files["txt"] = txt_file
        
        if "html" in formats:
            html_file = f"{output_dir}/aws_cost_analysis_report_{timestamp}.html"
            if self.html_report_generator.generate_cost_report(
                df, html_file, service_costs, region_costs, resource_costs, anomalies
            ):
                generated_files["html"] = html_file
                
                # 如果有优化报告，添加到HTML文件中
                if optimization_report:
                    try:
                        # 读取现有HTML内容
                        with open(html_file, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # 在报告末尾添加优化建议
                        optimization_html = self.cost_optimizer.generate_optimization_report_html(optimization_report)
                        insertion_point = html_content.find('<!-- 详细数据 -->')
                        if insertion_point != -1:
                            new_content = (
                                html_content[:insertion_point] + 
                                f'''
                                <!-- 优化建议 -->
                                <section class="optimization-section">
                                    <div class="section-header">
                                        <h2>💡 成本优化建议</h2>
                                        <p>基于AI分析的智能优化建议</p>
                                    </div>
                                    {optimization_html}
                                </section>
                                ''' + 
                                html_content[insertion_point:]
                            )
                            
                            # 写回文件
                            with open(html_file, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                                
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Could not add optimization report to HTML: {e}[/yellow]")
        
        return generated_files
    
    def send_notifications(
        self,
        df: pd.DataFrame,
        service_costs: pd.DataFrame,
        region_costs: pd.DataFrame,
        time_range: str = "",
        subject_suffix: str = ""
    ) -> Dict[str, bool]:
        """
        发送通知
        
        Args:
            df: 费用数据
            service_costs: 服务费用统计
            region_costs: 区域费用统计
            time_range: 时间范围
            subject_suffix: 主题后缀
            
        Returns:
            发送结果字典
        """
        if not self.notification_manager:
            return {"email": False, "feishu": False}
        
        # 计算费用摘要
        cost_summary = self.data_processor.get_cost_summary(df)
        
        return self.notification_manager.send_cost_report(
            cost_summary, service_costs, region_costs, time_range, subject_suffix
        )
    
    def quick_analysis(self) -> bool:
        """快速分析过去1年的费用"""
        try:
            self.console.print("[cyan]🕐 快速分析过去1年的费用...[/cyan]")
            
            # 分析费用数据
            df, service_costs, region_costs = self.analyze_costs()
            
            if df is None or df.empty:
                self.console.print("[red]没有费用数据可分析[/red]")
                return False
            
            # 打印分析结果
            self.print_summary(df)
            self.print_service_analysis(service_costs)
            self.print_region_analysis(region_costs)
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ 快速分析失败: {e}[/red]")
            return False
    
    def custom_analysis(self, start_date: str, end_date: str) -> bool:
        """自定义时间范围分析"""
        try:
            self.console.print(f"[cyan]📅 自定义时间范围分析: {start_date} 到 {end_date}[/cyan]")
            
            # 分析费用数据
            df, service_costs, region_costs = self.analyze_costs(start_date, end_date)
            
            if df is None or df.empty:
                self.console.print("[red]没有费用数据可分析[/red]")
                return False
            
            # 打印分析结果
            self.print_summary(df)
            self.print_service_analysis(service_costs)
            self.print_region_analysis(region_costs)
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ 自定义分析失败: {e}[/red]")
            return False
    
    def get_cost_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取费用趋势"""
        return self.data_processor.calculate_cost_trend(df)
    
    def detect_anomalies(self, df: pd.DataFrame, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """检测费用异常"""
        return self.data_processor.detect_cost_anomalies(df, threshold)
    
    def get_top_services(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """获取费用最高的服务"""
        return self.data_processor.get_top_services(df, top_n)
    
    def get_top_regions(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """获取费用最高的区域"""
        return self.data_processor.get_top_regions(df, top_n)
