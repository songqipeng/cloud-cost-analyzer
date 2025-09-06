#!/usr/bin/env python3
"""
演示增强版AWS费用分析器功能
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aws_cost_analyzer.core.analyzer import AWSCostAnalyzer
from aws_cost_analyzer.core.data_processor import DataProcessor
from aws_cost_analyzer.core.cost_optimizer import CostOptimizationAnalyzer
from aws_cost_analyzer.reports.html_report import HTMLReportGenerator
from rich.console import Console
from rich.panel import Panel


def generate_demo_data():
    """生成演示数据"""
    console = Console()
    console.print("[blue]🔬 生成演示数据...[/blue]")
    
    # 生成过去90天的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 模拟AWS服务
    services = [
        'Amazon Elastic Compute Cloud - Compute',
        'Amazon Relational Database Service',
        'Amazon Simple Storage Service',
        'Amazon Elastic Load Balancing',
        'Amazon CloudFront',
        'Amazon VPC',
        'Amazon Route 53',
        'AWS Lambda'
    ]
    
    regions = [
        'us-east-1', 'us-west-2', 'eu-west-1', 
        'ap-northeast-1', 'ap-southeast-1'
    ]
    
    # 生成资源ID
    resource_ids = [
        'i-0123456789abcdef0', 'i-0abcdef123456789',
        'db-instance-1', 'db-instance-2',
        'my-s3-bucket', 'backup-bucket',
        'my-load-balancer', 'api-load-balancer',
        'lambda-function-1', 'lambda-function-2'
    ]
    
    data = []
    
    for date in dates:
        # 基础费用趋势（有一些波动）
        base_multiplier = 1 + 0.1 * np.sin(2 * np.pi * (date - start_date).days / 30)  # 月度周期
        daily_noise = np.random.normal(1, 0.2)  # 日常波动
        
        for service in services:
            for region in regions[:3]:  # 只用前3个区域
                # 不是每个服务在每个区域都有费用
                if np.random.random() > 0.7:
                    continue
                
                # 基础费用（不同服务有不同的费用水平）
                if 'Compute' in service:
                    base_cost = np.random.uniform(20, 200)
                elif 'Database' in service:
                    base_cost = np.random.uniform(50, 300)
                elif 'Storage' in service:
                    base_cost = np.random.uniform(5, 50)
                else:
                    base_cost = np.random.uniform(10, 100)
                
                # 应用趋势和波动
                final_cost = base_cost * base_multiplier * daily_noise
                
                # 添加一些异常值
                if np.random.random() > 0.95:  # 5%概率出现异常
                    final_cost *= np.random.uniform(2, 5)  # 异常高费用
                
                # 随机选择资源ID
                if 'Compute' in service:
                    resource_id = np.random.choice(['i-0123456789abcdef0', 'i-0abcdef123456789'])
                elif 'Database' in service:
                    resource_id = np.random.choice(['db-instance-1', 'db-instance-2'])
                elif 'Storage' in service:
                    resource_id = np.random.choice(['my-s3-bucket', 'backup-bucket'])
                else:
                    resource_id = np.random.choice(resource_ids)
                
                data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Service': service,
                    'Region': region,
                    'ResourceId': resource_id,
                    'Cost': max(0.01, final_cost),  # 确保费用为正
                    'Unit': 'USD'
                })
    
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    
    console.print(f"[green]✅ 生成了 {len(df)} 条演示数据记录[/green]")
    
    return df


def demo_enhanced_analysis():
    """演示增强版分析功能"""
    console = Console()
    
    # 显示演示标题
    title_panel = Panel.fit(
        "[bold blue]🚀 AWS费用分析器 - 增强版演示[/bold blue]\n"
        "[cyan]展示深入分析、可视化图表和智能优化建议功能[/cyan]",
        border_style="blue"
    )
    console.print(title_panel)
    
    # 生成演示数据
    demo_df = generate_demo_data()
    
    # 初始化组件
    data_processor = DataProcessor(cost_threshold=0.01)
    cost_optimizer = CostOptimizationAnalyzer()
    html_generator = HTMLReportGenerator()
    
    console.print("\n[blue]📊 执行增强版费用分析...[/blue]")
    
    # 构建分析结果
    service_costs = data_processor.analyze_costs_by_service(demo_df)
    region_costs = data_processor.analyze_costs_by_region(demo_df)
    resource_costs = data_processor.analyze_costs_by_resource(demo_df)
    cost_summary = data_processor.get_cost_summary(demo_df)
    trend_analysis = data_processor.analyze_cost_trends(demo_df)
    anomalies = data_processor.detect_cost_anomalies(demo_df)
    
    # 生成优化建议
    console.print("[blue]🔍 分析优化机会...[/blue]")
    optimization_report = cost_optimizer.analyze_cost_optimization_opportunities(
        demo_df, service_costs, resource_costs
    )
    
    # 构建完整分析结果
    analysis_result = {
        'data': demo_df,
        'service_costs': service_costs,
        'region_costs': region_costs,
        'resource_costs': resource_costs,
        'cost_summary': cost_summary,
        'trend_analysis': trend_analysis,
        'anomalies': anomalies,
        'optimization_report': optimization_report
    }
    
    # 创建模拟的分析器来使用其打印方法
    class DemoAnalyzer:
        def __init__(self):
            self.console = Console()
            self.data_processor = data_processor
            self.cost_optimizer = cost_optimizer
        
        def _print_resource_analysis(self, resource_costs):
            self.console.print("\n[bold blue]🔥 资源费用分析:[/bold blue]")
            
            from rich.table import Table
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
        
        def _print_anomaly_analysis(self, anomalies):
            self.console.print(f"\n[bold red]⚠️  检测到 {len(anomalies)} 个费用异常:[/bold red]")
            
            from rich.table import Table
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
            
            for anomaly in anomalies[:5]:
                anomaly_type_display = "📈 高于正常" if anomaly['type'] == 'high' else "📉 低于正常"
                table.add_row(
                    anomaly['date'].strftime('%Y-%m-%d'),
                    f"${anomaly['cost']:.2f}",
                    anomaly_type_display,
                    f"{anomaly['deviation']:.1f}σ"
                )
            
            self.console.print(table)
        
        def _print_optimization_summary(self, optimization_report):
            total_savings = optimization_report.get('total_potential_savings', 0)
            priority_actions = optimization_report.get('priority_actions', [])
            
            from rich.panel import Panel
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
    
    demo_analyzer = DemoAnalyzer()
    
    # 显示分析结果
    console.print("\n[bold green]📈 费用分析结果:[/bold green]")
    
    # 基础摘要
    from rich.table import Table
    summary_table = Table(
        show_header=True,
        header_style="bold magenta",
        width=60,
        show_lines=True
    )
    summary_table.add_column("费用类型", justify="left", style="white", width=20)
    summary_table.add_column("金额", justify="right", style="cyan", width=15)
    
    summary_table.add_row("总费用", f"${cost_summary['total_cost']:.2f}")
    summary_table.add_row("平均每日费用", f"${cost_summary['avg_daily_cost']:.2f}")
    summary_table.add_row("最高单日费用", f"${cost_summary['max_daily_cost']:.2f}")
    summary_table.add_row("最低单日费用", f"${cost_summary['min_daily_cost']:.2f}")
    
    console.print(summary_table)
    
    # 服务分析
    console.print("\n[bold blue]按服务分析:[/bold blue]")
    service_table = Table(
        show_header=True,
        header_style="bold magenta",
        width=80,
        show_lines=True
    )
    service_table.add_column("Service", justify="left", style="white", width=40)
    service_table.add_column("总费用", justify="right", style="cyan", width=15)
    service_table.add_column("平均费用", justify="right", style="cyan", width=15)
    service_table.add_column("记录数", justify="right", style="cyan", width=10)
    
    for service, row in service_costs.head(5).iterrows():
        service_table.add_row(
            service[:40],
            f"${row['总费用']:.2f}",
            f"${row['平均费用']:.2f}",
            str(row['记录数'])
        )
    
    console.print(service_table)
    
    # 资源分析
    if not resource_costs.empty:
        demo_analyzer._print_resource_analysis(resource_costs)
    
    # 异常检测
    if anomalies:
        demo_analyzer._print_anomaly_analysis(anomalies)
    
    # 优化建议
    if optimization_report:
        demo_analyzer._print_optimization_summary(optimization_report)
    
    # 生成HTML报告
    console.print("\n[blue]📄 生成增强版HTML报告...[/blue]")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_file = f"demo_enhanced_aws_cost_analysis_{timestamp}.html"
    
    try:
        success = html_generator.generate_cost_report(
            demo_df, html_file, service_costs, region_costs, resource_costs, anomalies
        )
        
        if success:
            # 添加优化建议到HTML报告
            if optimization_report:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                optimization_html = cost_optimizer.generate_optimization_report_html(optimization_report)
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
                    
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
            
            console.print(f"[green]✅ HTML报告已生成: {html_file}[/green]")
            console.print(f"[cyan]📱 请在浏览器中打开查看交互式图表和现代化界面[/cyan]")
            
            # 显示报告路径
            import os
            full_path = os.path.abspath(html_file)
            console.print(f"[blue]🔗 完整路径: {full_path}[/blue]")
            
        else:
            console.print("[red]❌ HTML报告生成失败[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ 生成HTML报告时出错: {e}[/red]")
    
    # 显示总结
    total_savings = optimization_report.get('total_potential_savings', 0)
    summary_panel = Panel.fit(
        f"[bold green]🎉 演示完成！[/bold green]\n\n"
        f"[white]📊 分析了 [cyan]{len(demo_df)}[/cyan] 条费用记录[/white]\n"
        f"[white]💰 总费用: [green]${cost_summary['total_cost']:.2f}[/green][/white]\n"
        f"[white]⚠️  检测到 [red]{len(anomalies)}[/red] 个异常[/white]\n"
        f"[white]💡 潜在节省: [yellow]${total_savings:.2f}[/yellow][/white]\n\n"
        f"[cyan]🚀 增强功能包括：资源级分析、异常检测、交互式图表、智能优化建议[/cyan]",
        border_style="green"
    )
    console.print(summary_panel)


if __name__ == "__main__":
    demo_enhanced_analysis()