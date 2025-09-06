"""
多云费用分析器模块
"""
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .client import AWSClient
from .aliyun_client import AliyunClient
from .tencent_client import TencentClient
from .volcengine_client import VolcengineClient
from .data_processor import DataProcessor
from .aliyun_data_processor import AliyunDataProcessor
from .tencent_data_processor import TencentDataProcessor
from .volcengine_data_processor import VolcengineDataProcessor
from ..notifications.manager import NotificationManager
from ..reports.text_report import TextReportGenerator
from ..reports.html_report import HTMLReportGenerator
from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger()


class MultiCloudAnalyzer:
    """多云费用分析器核心类 - 支持AWS、阿里云、腾讯云、火山云"""
    
    def __init__(self, aws_profile: Optional[str] = None, aws_region: str = 'us-east-1',
                 aliyun_access_key_id: Optional[str] = None, aliyun_access_key_secret: Optional[str] = None,
                 aliyun_region: str = 'cn-hangzhou',
                 tencent_secret_id: Optional[str] = None, tencent_secret_key: Optional[str] = None,
                 tencent_region: str = 'ap-beijing',
                 volcengine_access_key_id: Optional[str] = None, volcengine_secret_access_key: Optional[str] = None,
                 volcengine_region: str = 'cn-beijing'):
        """
        初始化多云费用分析器
        
        Args:
            aws_profile: AWS配置文件名称
            aws_region: AWS区域
            aliyun_access_key_id: 阿里云AccessKey ID
            aliyun_access_key_secret: 阿里云AccessKey Secret
            aliyun_region: 阿里云区域
            tencent_secret_id: 腾讯云SecretId
            tencent_secret_key: 腾讯云SecretKey
            tencent_region: 腾讯云区域
            volcengine_access_key_id: 火山云AccessKey ID
            volcengine_secret_access_key: 火山云SecretAccessKey
            volcengine_region: 火山云区域
        """
        self.console = Console()
        
        # 初始化AWS客户端和数据处理器
        self.aws_client = AWSClient(aws_profile, aws_region)
        self.aws_data_processor = DataProcessor(Config.COST_THRESHOLD)
        
        # 初始化阿里云客户端和数据处理器
        self.aliyun_client = AliyunClient(aliyun_access_key_id, aliyun_access_key_secret, aliyun_region)
        self.aliyun_data_processor = AliyunDataProcessor(Config.COST_THRESHOLD)
        
        # 初始化腾讯云客户端和数据处理器
        self.tencent_client = TencentClient(tencent_secret_id, tencent_secret_key, tencent_region)
        self.tencent_data_processor = TencentDataProcessor(Config.COST_THRESHOLD)
        
        # 初始化火山云客户端和数据处理器
        self.volcengine_client = VolcengineClient(volcengine_access_key_id, volcengine_secret_access_key, volcengine_region)
        self.volcengine_data_processor = VolcengineDataProcessor(Config.COST_THRESHOLD)
        
        # 报告生成器
        self.text_report_generator = TextReportGenerator()
        self.html_report_generator = HTMLReportGenerator()
        
        # 通知管理器
        self.notification_manager = None
    
    def initialize_notifications(self, config: Dict[str, Any]) -> None:
        """初始化通知管理器"""
        self.notification_manager = NotificationManager(config)
    
    def test_connections(self) -> Dict[str, tuple[bool, str]]:
        """测试所有云平台连接"""
        results = {}
        
        # 测试AWS连接
        aws_connected, aws_message = self.aws_client.test_connection()
        results['aws'] = (aws_connected, aws_message)
        
        # 测试阿里云连接
        aliyun_connected, aliyun_message = self.aliyun_client.test_connection()
        results['aliyun'] = (aliyun_connected, aliyun_message)
        
        # 测试腾讯云连接
        tencent_connected, tencent_message = self.tencent_client.test_connection()
        results['tencent'] = (tencent_connected, tencent_message)
        
        # 测试火山云连接
        volcengine_connected, volcengine_message = self.volcengine_client.test_connection()
        results['volcengine'] = (volcengine_connected, volcengine_message)
        
        return results
    
    def get_multi_cloud_cost_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                                  granularity: str = 'MONTHLY') -> Dict[str, Any]:
        """
        获取多云费用数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            granularity: 数据粒度
            
        Returns:
            多云费用数据字典
        """
        if not start_date or not end_date:
            # 默认获取过去1年的数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - relativedelta(years=1)).strftime('%Y-%m-%d')
        
        results = {}
        
        # 获取AWS费用数据
        try:
            aws_data = self.aws_client.get_cost_and_usage_with_retry(start_date, end_date, granularity)
            results['aws'] = aws_data
            logger.info("AWS费用数据获取成功" if aws_data else "AWS费用数据获取失败")
        except Exception as e:
            logger.error(f"AWS费用数据获取异常: {e}")
            results['aws'] = None
        
        # 获取阿里云费用数据
        try:
            aliyun_data = self.aliyun_client.get_cost_and_usage_with_retry(start_date, end_date, granularity)
            results['aliyun'] = aliyun_data
            logger.info("阿里云费用数据获取成功" if aliyun_data else "阿里云费用数据获取失败")
        except Exception as e:
            logger.error(f"阿里云费用数据获取异常: {e}")
            results['aliyun'] = None
        
        # 获取腾讯云费用数据
        try:
            tencent_data = self.tencent_client.get_cost_and_usage_with_retry(start_date, end_date, granularity)
            results['tencent'] = tencent_data
            logger.info("腾讯云费用数据获取成功" if tencent_data else "腾讯云费用数据获取失败")
        except Exception as e:
            logger.error(f"腾讯云费用数据获取异常: {e}")
            results['tencent'] = None
        
        # 获取火山云费用数据
        try:
            volcengine_data = self.volcengine_client.get_cost_and_usage_with_retry(start_date, end_date, granularity)
            results['volcengine'] = volcengine_data
            logger.info("火山云费用数据获取成功" if volcengine_data else "火山云费用数据获取失败")
        except Exception as e:
            logger.error(f"火山云费用数据获取异常: {e}")
            results['volcengine'] = None
        
        return results
    
    def analyze_multi_cloud_costs(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                                  granularity: str = 'MONTHLY') -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
        """
        分析多云费用数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            granularity: 数据粒度
            
        Returns:
            (原始数据字典, 服务统计字典, 区域统计字典)
        """
        # 获取多云费用数据
        multi_cloud_data = self.get_multi_cloud_cost_data(start_date, end_date, granularity)
        
        raw_data = {}
        service_costs = {}
        region_costs = {}
        
        # 处理AWS数据
        if multi_cloud_data.get('aws'):
            aws_df = self.aws_data_processor.parse_cost_data(multi_cloud_data['aws'])
            if not aws_df.empty:
                raw_data['aws'] = aws_df
                service_costs['aws'] = self.aws_data_processor.analyze_costs_by_service(aws_df)
                region_costs['aws'] = self.aws_data_processor.analyze_costs_by_region(aws_df)
        
        # 处理阿里云数据
        if multi_cloud_data.get('aliyun'):
            aliyun_df = self.aliyun_data_processor.parse_cost_data(multi_cloud_data['aliyun'])
            if not aliyun_df.empty:
                raw_data['aliyun'] = aliyun_df
                service_costs['aliyun'] = self.aliyun_data_processor.analyze_costs_by_service(aliyun_df)
                region_costs['aliyun'] = self.aliyun_data_processor.analyze_costs_by_region(aliyun_df)
        
        # 处理腾讯云数据
        if multi_cloud_data.get('tencent'):
            tencent_df = self.tencent_data_processor.parse_cost_data(multi_cloud_data['tencent'])
            if not tencent_df.empty:
                raw_data['tencent'] = tencent_df
                service_costs['tencent'] = self.tencent_data_processor.analyze_costs_by_service(tencent_df)
                region_costs['tencent'] = self.tencent_data_processor.analyze_costs_by_region(tencent_df)
        
        # 处理火山云数据
        if multi_cloud_data.get('volcengine'):
            volcengine_df = self.volcengine_data_processor.parse_cost_data(multi_cloud_data['volcengine'])
            if not volcengine_df.empty:
                raw_data['volcengine'] = volcengine_df
                service_costs['volcengine'] = self.volcengine_data_processor.analyze_costs_by_service(volcengine_df)
                region_costs['volcengine'] = self.volcengine_data_processor.analyze_costs_by_region(volcengine_df)
        
        return raw_data, service_costs, region_costs
    
    def print_multi_cloud_summary(self, raw_data: Dict[str, pd.DataFrame]) -> None:
        """打印多云费用摘要"""
        if not raw_data:
            self.console.print("[red]没有费用数据可分析[/red]")
            return
        
        # 创建多云费用摘要表格
        table = Table(
            show_header=True,
            header_style="bold magenta",
            width=80,
            show_lines=True
        )
        table.add_column("云平台", justify="left", style="white", width=15)
        table.add_column("总费用", justify="right", style="cyan", width=15)
        table.add_column("货币", justify="center", style="yellow", width=10)
        table.add_column("平均每日费用", justify="right", style="cyan", width=15)
        table.add_column("记录数", justify="right", style="cyan", width=10)
        table.add_column("时间跨度", justify="right", style="cyan", width=15)
        
        total_cost_usd = 0
        total_cost_cny = 0
        
        for provider, df in raw_data.items():
            if provider == 'aws':
                summary = self.aws_data_processor.get_cost_summary(df)
                currency = 'USD'
                total_cost_usd += summary.get('total_cost', 0)
                provider_name = 'AWS'
            elif provider == 'aliyun':
                summary = self.aliyun_data_processor.get_cost_summary(df)
                currency = summary.get('currency', 'CNY')
                total_cost_cny += summary.get('total_cost', 0)
                provider_name = '阿里云'
            elif provider == 'tencent':
                summary = self.tencent_data_processor.get_cost_summary(df)
                currency = summary.get('currency', 'CNY')
                total_cost_cny += summary.get('total_cost', 0)
                provider_name = '腾讯云'
            elif provider == 'volcengine':
                summary = self.volcengine_data_processor.get_cost_summary(df)
                currency = summary.get('currency', 'CNY')
                total_cost_cny += summary.get('total_cost', 0)
                provider_name = '火山云'
            else:
                continue
            
            table.add_row(
                provider_name,
                f"{summary.get('total_cost', 0):.2f}",
                currency,
                f"{summary.get('avg_daily_cost', 0):.2f}",
                str(summary.get('record_count', 0)),
                f"{summary.get('date_range', 0)} 天"
            )
        
        # 添加总计行（简化处理，不做汇率转换）
        if len(raw_data) > 1:
            table.add_row(
                "[bold]总计[/bold]",
                f"USD: {total_cost_usd:.2f}\nCNY: {total_cost_cny:.2f}",
                "混合",
                "-",
                "-",
                "-"
            )
        
        self.console.print(table)
    
    def print_multi_cloud_service_analysis(self, service_costs: Dict[str, pd.DataFrame]) -> None:
        """打印多云服务分析"""
        if not service_costs:
            self.console.print("[yellow]按服务分析: 无数据[/yellow]")
            return
        
        for provider, df in service_costs.items():
            if df.empty:
                continue
            
            provider_name = 'AWS' if provider == 'aws' else '阿里云'
            self.console.print(f"\n[bold blue]{provider_name} - 按服务分析:[/bold blue]")
            
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
            
            # 只显示前10个服务
            top_services = df.head(10)
            for service, row in top_services.iterrows():
                table.add_row(
                    service,
                    f"{row['总费用']:.4f}",
                    f"{row['平均费用']:.4f}",
                    str(row['记录数'])
                )
            
            self.console.print(table)
    
    def print_multi_cloud_region_analysis(self, region_costs: Dict[str, pd.DataFrame]) -> None:
        """打印多云区域分析"""
        if not region_costs:
            self.console.print("[yellow]按区域分析: 无数据[/yellow]")
            return
        
        for provider, df in region_costs.items():
            if df.empty:
                continue
            
            provider_name = 'AWS' if provider == 'aws' else '阿里云'
            self.console.print(f"\n[bold blue]{provider_name} - 按区域分析:[/bold blue]")
            
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
            
            for region, row in df.iterrows():
                table.add_row(
                    region,
                    f"{row['总费用']:.4f}",
                    f"{row['平均费用']:.4f}",
                    str(row['记录数'])
                )
            
            self.console.print(table)
    
    def generate_multi_cloud_reports(self, raw_data: Dict[str, pd.DataFrame], 
                                     service_costs: Dict[str, pd.DataFrame],
                                     region_costs: Dict[str, pd.DataFrame],
                                     output_dir: str = ".", 
                                     formats: List[str] = ["txt", "html"]) -> Dict[str, str]:
        """
        生成多云报告
        
        Args:
            raw_data: 原始费用数据
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
            txt_file = f"{output_dir}/multi_cloud_cost_analysis_{timestamp}.txt"
            if self._generate_multi_cloud_text_report(raw_data, service_costs, region_costs, txt_file):
                generated_files["txt"] = txt_file
        
        if "html" in formats:
            html_file = f"{output_dir}/multi_cloud_cost_analysis_{timestamp}.html"
            if self._generate_multi_cloud_html_report(raw_data, service_costs, region_costs, html_file):
                generated_files["html"] = html_file
        
        return generated_files
    
    def _generate_multi_cloud_text_report(self, raw_data: Dict[str, pd.DataFrame], 
                                          service_costs: Dict[str, pd.DataFrame],
                                          region_costs: Dict[str, pd.DataFrame], 
                                          output_file: str) -> bool:
        """生成多云文本报告"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("多云费用分析报告\n")
                f.write("=" * 80 + "\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                # 费用摘要
                f.write("费用摘要:\n")
                f.write("-" * 40 + "\n")
                
                total_usd = 0
                total_cny = 0
                
                for provider, df in raw_data.items():
                    if provider == 'aws':
                        summary = self.aws_data_processor.get_cost_summary(df)
                        currency = 'USD'
                        total_usd += summary['total_cost']
                    else:
                        summary = self.aliyun_data_processor.get_cost_summary(df)
                        currency = summary['currency']
                        total_cny += summary['total_cost']
                    
                    provider_name = 'AWS' if provider == 'aws' else '阿里云'
                    f.write(f"{provider_name}:\n")
                    f.write(f"  总费用: {summary.get('total_cost', 0):.2f} {currency}\n")
                    f.write(f"  平均每日费用: {summary.get('avg_daily_cost', 0):.2f} {currency}\n")
                    f.write(f"  记录数: {summary.get('record_count', 0)}\n")
                    f.write(f"  时间跨度: {summary.get('date_range', 0)} 天\n\n")
                
                if len(raw_data) > 1:
                    f.write(f"总计: {total_usd:.2f} USD + {total_cny:.2f} CNY\n\n")
                
                # 服务分析
                for provider, df in service_costs.items():
                    if df.empty:
                        continue
                    
                    provider_name = 'AWS' if provider == 'aws' else '阿里云'
                    f.write(f"{provider_name} - 按服务分析:\n")
                    f.write("-" * 40 + "\n")
                    
                    for service, row in df.head(10).iterrows():
                        f.write(f"{service:<40} {row['总费用']:>10.4f} {row['平均费用']:>10.4f} {row['记录数']:>8.0f}\n")
                    f.write("\n")
                
                # 区域分析
                for provider, df in region_costs.items():
                    if df.empty:
                        continue
                    
                    provider_name = 'AWS' if provider == 'aws' else '阿里云'
                    f.write(f"{provider_name} - 按区域分析:\n")
                    f.write("-" * 40 + "\n")
                    
                    for region, row in df.iterrows():
                        f.write(f"{region:<25} {row['总费用']:>15.4f} {row['平均费用']:>15.4f} {row['记录数']:>10.0f}\n")
                    f.write("\n")
            
            return True
            
        except Exception as e:
            logger.error(f"生成多云文本报告失败: {e}")
            return False
    
    def _generate_multi_cloud_html_report(self, raw_data: Dict[str, pd.DataFrame], 
                                          service_costs: Dict[str, pd.DataFrame],
                                          region_costs: Dict[str, pd.DataFrame], 
                                          output_file: str) -> bool:
        """生成多云HTML报告"""
        try:
            # 这里可以扩展HTML报告生成逻辑
            # 暂时使用简化版本
            return self._generate_multi_cloud_text_report(raw_data, service_costs, region_costs, 
                                                          output_file.replace('.html', '.txt'))
        except Exception as e:
            logger.error(f"生成多云HTML报告失败: {e}")
            return False
    
    def quick_multi_cloud_analysis(self) -> bool:
        """快速多云分析"""
        try:
            self.console.print("[cyan]🌐 多云费用分析 - 快速分析过去1年的费用...[/cyan]")
            
            # 分析多云费用数据
            raw_data, service_costs, region_costs = self.analyze_multi_cloud_costs()
            
            if not raw_data:
                self.console.print("[red]没有费用数据可分析[/red]")
                return False
            
            # 打印分析结果
            self.print_multi_cloud_summary(raw_data)
            self.print_multi_cloud_service_analysis(service_costs)
            self.print_multi_cloud_region_analysis(region_costs)
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ 多云分析失败: {e}[/red]")
            return False
