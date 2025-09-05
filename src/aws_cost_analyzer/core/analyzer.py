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
        granularity: str = 'MONTHLY'
    ) -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        分析费用数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            granularity: 数据粒度
            
        Returns:
            (原始数据, 服务统计, 区域统计)
        """
        # 获取费用数据
        cost_data = self.get_cost_data(start_date, end_date, granularity)
        if not cost_data:
            return None, None, None
        
        # 解析数据
        df = self.data_processor.parse_cost_data(cost_data)
        if df.empty:
            return df, None, None
        
        # 分析数据
        service_costs = self.data_processor.analyze_costs_by_service(df)
        region_costs = self.data_processor.analyze_costs_by_region(df)
        
        return df, service_costs, region_costs
    
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
    
    def generate_reports(
        self,
        df: pd.DataFrame,
        service_costs: pd.DataFrame,
        region_costs: pd.DataFrame,
        output_dir: str = ".",
        formats: List[str] = ["txt", "html"]
    ) -> Dict[str, str]:
        """
        生成报告
        
        Args:
            df: 费用数据
            service_costs: 服务费用统计
            region_costs: 区域费用统计
            output_dir: 输出目录
            formats: 输出格式列表
            
        Returns:
            生成的文件路径字典
        """
        generated_files = {}
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if "txt" in formats:
            txt_file = f"{output_dir}/cost_analysis_report_{timestamp}.txt"
            if self.text_report_generator.generate_cost_report(
                df, txt_file, service_costs, region_costs
            ):
                generated_files["txt"] = txt_file
        
        if "html" in formats:
            html_file = f"{output_dir}/cost_analysis_report_{timestamp}.html"
            if self.html_report_generator.generate_cost_report(
                df, html_file, service_costs, region_costs
            ):
                generated_files["html"] = html_file
        
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
