#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWS费用分析器
用于分析AWS云服务的费用情况，包括费用趋势、服务分布、区域分析等
"""

# 自动依赖检查和安装
def check_and_install_dependencies():
    """检查并自动安装所需的依赖包"""
    required_packages = {
        'boto3': 'boto3>=1.34.0',
        'pandas': 'pandas>=2.2.0',
        'matplotlib': 'matplotlib>=3.8.0',
        'seaborn': 'seaborn>=0.13.0',
        'plotly': 'plotly>=5.17.0',
        'dateutil': 'python-dateutil>=2.8.2',  # 导入名是dateutil，包名是python-dateutil
        'tabulate': 'tabulate>=0.9.0',
        'colorama': 'colorama>=0.4.6'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("🔍 检测到缺少依赖包，正在自动安装...")
        import subprocess
        import sys
        
        for package in missing_packages:
            print(f"📦 安装 {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败: {e}")
                print("请手动运行: pip install -r requirements.txt")
                sys.exit(1)
        
        print("🎉 所有依赖包安装完成！")
        print("⚠️  注意: 建议使用虚拟环境来管理依赖包")
        print("   创建虚拟环境: python3 -m venv aws_cost_env")
        print("   激活虚拟环境: source aws_cost_env/bin/activate")
        print()

# 检查依赖
check_and_install_dependencies()

import boto3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import os
import sys
import getpass
import argparse
from tabulate import tabulate
from colorama import init, Fore, Style
import warnings

# 忽略matplotlib的警告
warnings.filterwarnings('ignore')

# 初始化colorama
init(autoreset=True)

class AWSCostAnalyzer:
    """AWS费用分析器主类"""
    
    def __init__(self, profile_name=None, auto_setup=True):
        """
        初始化AWS费用分析器
        
        Args:
            profile_name (str): AWS配置文件名称，如果为None则使用默认配置
            auto_setup (bool): 是否自动设置AWS凭证
        """
        self.profile_name = profile_name
        self.ce_client = None
        self.region = 'us-east-1'  # Cost Explorer API只在us-east-1可用
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        if auto_setup:
            self._setup_aws_credentials()
        
        self._init_aws_client()
    
    def _setup_aws_credentials(self):
        """自动设置AWS凭证"""
        print(f"{Fore.CYAN}🔍 检查AWS凭证配置...{Style.RESET_ALL}")
        
        # 检查是否已有AWS凭证
        if self._check_existing_credentials():
            print(f"{Fore.GREEN}✅ 检测到现有AWS凭证配置{Style.RESET_ALL}")
            return
        
        # 如果没有凭证，引导用户输入
        print(f"{Fore.YELLOW}⚠️  未检测到AWS凭证，需要配置{Style.RESET_ALL}")
        self._prompt_for_credentials()
    
    def _check_existing_credentials(self):
        """检查是否已有AWS凭证"""
        try:
            # 检查环境变量
            if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
                return True
            
            # 检查AWS配置文件
            aws_config_path = os.path.expanduser('~/.aws/credentials')
            if os.path.exists(aws_config_path):
                return True
            
            # 尝试创建临时客户端测试
            test_client = boto3.client('sts', region_name='us-east-1')
            test_client.get_caller_identity()
            return True
            
        except Exception:
            return False
    
    def _prompt_for_credentials(self):
        """提示用户输入AWS凭证"""
        print(f"\n{Fore.CYAN}请输入AWS凭证信息:{Style.RESET_ALL}")
        
        access_key = input("AWS Access Key ID: ").strip()
        if not access_key:
            print(f"{Fore.RED}❌ Access Key ID不能为空{Style.RESET_ALL}")
            return
        
        secret_key = getpass.getpass("AWS Secret Access Key: ").strip()
        if not secret_key:
            print(f"{Fore.RED}❌ Secret Access Key不能为空{Style.RESET_ALL}")
            return
        
        region = input("AWS Region (默认: us-east-1): ").strip() or 'us-east-1'
        
        # 设置环境变量
        os.environ['AWS_ACCESS_KEY_ID'] = access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
        os.environ['AWS_DEFAULT_REGION'] = region
        
        print(f"{Fore.GREEN}✅ AWS凭证已设置{Style.RESET_ALL}")
    
    def _init_aws_client(self):
        """初始化AWS客户端"""
        try:
            if self.profile_name:
                session = boto3.Session(profile_name=self.profile_name)
                self.ce_client = session.client('ce', region_name=self.region)
            else:
                self.ce_client = boto3.client('ce', region_name=self.region)
            
            print(f"{Fore.GREEN}✓ AWS客户端初始化成功{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ AWS客户端初始化失败: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}请确保已配置AWS凭证或IAM角色{Style.RESET_ALL}")
    
    def get_cost_data(self, start_date=None, end_date=None, granularity='MONTHLY'):
        """
        获取AWS费用数据
        
        Args:
            start_date (str): 开始日期，格式：YYYY-MM-DD
            end_date (str): 结束日期，格式：YYYY-MM-DD
            granularity (str): 数据粒度，DAILY, MONTHLY, HOURLY
            
        Returns:
            dict: AWS费用数据
        """
        if not self.ce_client:
            print(f"{Fore.RED}AWS客户端未初始化{Style.RESET_ALL}")
            return None
        
        # 如果没有指定日期，默认获取过去6个月的数据
        if not start_date:
            start_date = (datetime.now() - relativedelta(months=6)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity=granularity,
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'}
                ]
            )
            
            print(f"{Fore.GREEN}✓ 成功获取费用数据 ({start_date} 到 {end_date}){Style.RESET_ALL}")
            return response
            
        except Exception as e:
            print(f"{Fore.RED}✗ 获取费用数据失败: {e}{Style.RESET_ALL}")
            return None
    
    def parse_cost_data(self, cost_data):
        """
        解析AWS费用数据
        
        Args:
            cost_data (dict): AWS费用数据
            
        Returns:
            pd.DataFrame: 解析后的费用数据
        """
        if not cost_data:
            return None
        
        parsed_data = []
        
        for result in cost_data.get('ResultsByTime', []):
            time_period = result['TimePeriod']['Start']
            
            for group in result.get('Groups', []):
                keys = group['Keys']
                cost = group['Metrics']['UnblendedCost']['Amount']
                unit = group['Metrics']['UnblendedCost']['Unit']
                
                # 解析分组键
                service = keys[0] if len(keys) > 0 else 'Unknown'
                region = keys[1] if len(keys) > 1 else 'Unknown'
                
                parsed_data.append({
                    'Date': time_period,
                    'Service': service,
                    'Region': region,
                    'Cost': float(cost),
                    'Unit': unit
                })
        
        df = pd.DataFrame(parsed_data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        return df
    
    def analyze_costs_by_service(self, df):
        """
        按服务分析费用
        
        Args:
            df (pd.DataFrame): 费用数据
            
        Returns:
            pd.DataFrame: 按服务汇总的费用数据
        """
        if df is None or df.empty:
            return None
        
        service_costs = df.groupby('Service')['Cost'].agg(['sum', 'mean', 'count']).round(4)
        service_costs.columns = ['总费用', '平均费用', '记录数']
        service_costs = service_costs.sort_values('总费用', ascending=False)
        
        return service_costs
    
    def analyze_costs_by_region(self, df):
        """
        按区域分析费用
        
        Args:
            df (pd.DataFrame): 费用数据
            
        Returns:
            pd.DataFrame: 按区域汇总的费用数据
        """
        if df is None or df.empty:
            return None
        
        region_costs = df.groupby('Region')['Cost'].agg(['sum', 'mean', 'count']).round(4)
        region_costs.columns = ['总费用', '平均费用', '记录数']
        region_costs = region_costs.sort_values('总费用', ascending=False)
        
        return region_costs
    
    def analyze_costs_by_time(self, df):
        """
        按时间分析费用趋势
        
        Args:
            df (pd.DataFrame): 费用数据
            
        Returns:
            pd.DataFrame: 按时间汇总的费用数据
        """
        if df is None or df.empty:
            return None
        
        time_costs = df.groupby('Date')['Cost'].sum().reset_index()
        time_costs = time_costs.sort_values('Date')
        
        return time_costs
    
    def generate_cost_report(self, df, output_file='aws_cost_report.txt'):
        """
        生成费用报告
        
        Args:
            df (pd.DataFrame): 费用数据
            output_file (str): 输出文件名
        """
        if df is None or df.empty:
            print(f"{Fore.RED}没有数据可生成报告{Style.RESET_ALL}")
            return
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("AWS费用分析报告")
        report_lines.append("=" * 60)
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"数据时间范围: {df['Date'].min().strftime('%Y-%m-%d')} 到 {df['Date'].max().strftime('%Y-%m-%d')}")
        report_lines.append(f"总费用: ${df['Cost'].sum():.2f}")
        report_lines.append(f"平均每日费用: ${df.groupby('Date')['Cost'].sum().mean():.2f}")
        report_lines.append("")
        
        # 按服务分析
        service_costs = self.analyze_costs_by_service(df)
        if service_costs is not None:
            report_lines.append("按服务分析 (前10名):")
            report_lines.append("-" * 40)
            for service, row in service_costs.head(10).iterrows():
                report_lines.append(f"{service}: ${row['总费用']:.2f}")
            report_lines.append("")
        
        # 按区域分析
        region_costs = self.analyze_costs_by_region(df)
        if region_costs is not None:
            report_lines.append("按区域分析:")
            report_lines.append("-" * 40)
            for region, row in region_costs.iterrows():
                report_lines.append(f"{region}: ${row['总费用']:.2f}")
            report_lines.append("")
        
        # 时间趋势
        time_costs = self.analyze_costs_by_time(df)
        if time_costs is not None:
            report_lines.append("费用时间趋势:")
            report_lines.append("-" * 40)
            for _, row in time_costs.tail(10).iterrows():
                report_lines.append(f"{row['Date'].strftime('%Y-%m-%d')}: ${row['Cost']:.2f}")
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"{Fore.GREEN}✓ 费用报告已生成: {output_file}{Style.RESET_ALL}")
    
    def plot_costs_by_service(self, df, save_path='costs_by_service.png'):
        """
        绘制按服务分类的费用饼图
        
        Args:
            df (pd.DataFrame): 费用数据
            save_path (str): 保存路径
        """
        if df is None or df.empty:
            print(f"{Fore.RED}没有数据可绘制图表{Style.RESET_ALL}")
            return
        
        service_costs = self.analyze_costs_by_service(df)
        if service_costs is None:
            return
        
        # 只显示前10名服务，其他归为"其他"
        top_services = service_costs.head(10)
        other_cost = service_costs.iloc[10:]['总费用'].sum() if len(service_costs) > 10 else 0
        
        if other_cost > 0:
            top_services.loc['其他'] = [other_cost, 0, 0]
        
        plt.figure(figsize=(12, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(top_services)))
        
        wedges, texts, autotexts = plt.pie(
            top_services['总费用'], 
            labels=top_services.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        
        plt.title('AWS费用按服务分布', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        # 添加图例
        plt.legend(wedges, [f'{service}: ${cost:.2f}' for service, cost in zip(top_services.index, top_services['总费用'])],
                  title="服务费用", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Fore.GREEN}✓ 服务费用分布图已保存: {save_path}{Style.RESET_ALL}")
    
    def plot_cost_trend(self, df, save_path='cost_trend.png'):
        """
        绘制费用趋势图
        
        Args:
            df (pd.DataFrame): 费用数据
            save_path (str): 保存路径
        """
        if df is None or df.empty:
            print(f"{Fore.RED}没有数据可绘制图表{Style.RESET_ALL}")
            return
        
        time_costs = self.analyze_costs_by_time(df)
        if time_costs is None:
            return
        
        plt.figure(figsize=(14, 8))
        
        # 主图：费用趋势
        plt.subplot(2, 1, 1)
        plt.plot(time_costs['Date'], time_costs['Cost'], marker='o', linewidth=2, markersize=6)
        plt.title('AWS费用趋势', fontsize=16, fontweight='bold')
        plt.ylabel('费用 ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # 添加趋势线
        z = np.polyfit(range(len(time_costs)), time_costs['Cost'], 1)
        p = np.poly1d(z)
        plt.plot(time_costs['Date'], p(range(len(time_costs))), "r--", alpha=0.8, label='趋势线')
        plt.legend()
        
        # 子图：费用分布
        plt.subplot(2, 1, 2)
        plt.hist(time_costs['Cost'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('费用分布直方图', fontsize=14, fontweight='bold')
        plt.xlabel('费用 ($)', fontsize=12)
        plt.ylabel('频次', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Fore.GREEN}✓ 费用趋势图已保存: {save_path}{Style.RESET_ALL}")
    
    def create_interactive_dashboard(self, df, save_path='aws_cost_dashboard.html'):
        """
        创建交互式费用仪表板
        
        Args:
            df (pd.DataFrame): 费用数据
            save_path (str): 保存路径
        """
        if df is None or df.empty:
            print(f"{Fore.RED}没有数据可创建仪表板{Style.RESET_ALL}")
            return
        
        # 准备数据
        service_costs = self.analyze_costs_by_service(df)
        region_costs = self.analyze_costs_by_region(df)
        time_costs = self.analyze_costs_by_time(df)
        
        if service_costs is None or region_costs is None or time_costs is None:
            return
        
        # 计算统计信息
        total_cost = df['Cost'].sum()
        avg_daily_cost = df.groupby('Date')['Cost'].sum().mean()
        max_daily_cost = df.groupby('Date')['Cost'].sum().max()
        min_daily_cost = df.groupby('Date')['Cost'].sum().min()
        
        # 创建子图
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('📈 费用趋势', '💰 服务费用分布', '🌍 区域费用分布', 
                           '📊 费用统计', '📅 月度费用', '🎯 费用分析'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "indicator"}],
                   [{"type": "bar", "colspan": 2}, None]],
            vertical_spacing=0.08,
            horizontal_spacing=0.08
        )
        
        # 1. 费用趋势图
        fig.add_trace(
            go.Scatter(
                x=time_costs['Date'], 
                y=time_costs['Cost'], 
                mode='lines+markers', 
                name='费用趋势',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8, color='#1f77b4', symbol='circle'),
                fill='tonexty',
                fillcolor='rgba(31, 119, 180, 0.1)'
            ),
            row=1, col=1
        )
        
        # 2. 服务费用分布 (前8名)
        top_services = service_costs.head(8)
        colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
        fig.add_trace(
            go.Bar(
                x=top_services.index, 
                y=top_services['总费用'], 
                name='服务费用', 
                marker_color=colors[:len(top_services)],
                marker_line_color='rgba(0,0,0,0.5)',
                marker_line_width=1
            ),
            row=1, col=2
        )
        
        # 3. 区域费用分布
        region_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        fig.add_trace(
            go.Bar(
                x=region_costs.index, 
                y=region_costs['总费用'], 
                name='区域费用', 
                marker_color=region_colors[:len(region_costs)],
                marker_line_color='rgba(0,0,0,0.5)',
                marker_line_width=1
            ),
            row=2, col=1
        )
        
        # 4. 费用统计指标
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=total_cost,
                title={'text': "总费用 ($)", 'font': {'size': 18}},
                delta={'reference': avg_daily_cost * 30, 'font': {'size': 14}},
                gauge={
                    'axis': {'range': [None, total_cost * 1.2], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#1f77b4"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, total_cost * 0.5], 'color': "lightgreen"},
                        {'range': [total_cost * 0.5, total_cost * 0.8], 'color': "yellow"},
                        {'range': [total_cost * 0.8, total_cost], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': total_cost
                    }
                }
            ),
            row=2, col=2
        )
        
        # 5. 月度费用分析
        monthly_costs = df.groupby(df['Date'].dt.to_period('M'))['Cost'].sum().reset_index()
        monthly_costs['Date'] = monthly_costs['Date'].astype(str)
        
        fig.add_trace(
            go.Bar(
                x=monthly_costs['Date'], 
                y=monthly_costs['Cost'], 
                name='月度费用',
                marker_color='#17a2b8',
                marker_line_color='rgba(0,0,0,0.5)',
                marker_line_width=1
            ),
            row=3, col=1
        )
        
        # 更新布局
        fig.update_layout(
            title={
                'text': "🚀 AWS费用分析仪表板",
                'font': {'size': 28, 'color': '#2c3e50'},
                'x': 0.5,
                'xanchor': 'center'
            },
            showlegend=False,
            height=1000,
            width=1200,
            paper_bgcolor='#f8f9fa',
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12, color='#2c3e50'),
            margin=dict(t=100, b=50, l=50, r=50)
        )
        
        # 更新子图样式
        fig.update_xaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(0,0,0,0.1)',
            tickangle=45
        )
        fig.update_yaxes(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(0,0,0,0.1)'
        )
        
        # 保存为HTML文件
        fig.write_html(save_path)
        print(f"{Fore.GREEN}✓ 交互式仪表板已保存: {save_path}{Style.RESET_ALL}")
    
    def print_summary(self, df):
        """
        打印费用摘要
        
        Args:
            df (pd.DataFrame): 费用数据
        """
        if df is None or df.empty:
            print(f"{Fore.RED}没有数据可显示{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}AWS费用摘要{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        # 基本统计
        total_cost = df['Cost'].sum()
        avg_daily_cost = df.groupby('Date')['Cost'].sum().mean()
        max_daily_cost = df.groupby('Date')['Cost'].sum().max()
        min_daily_cost = df.groupby('Date')['Cost'].sum().min()
        
        print(f"总费用: {Fore.GREEN}${total_cost:.2f}{Style.RESET_ALL}")
        print(f"平均每日费用: {Fore.YELLOW}${avg_daily_cost:.2f}{Style.RESET_ALL}")
        print(f"最高单日费用: {Fore.RED}${max_daily_cost:.2f}{Style.RESET_ALL}")
        print(f"最低单日费用: {Fore.GREEN}${min_daily_cost:.2f}{Style.RESET_ALL}")
        
        # 按服务分析
        service_costs = self.analyze_costs_by_service(df)
        if service_costs is not None:
            print(f"\n{Fore.CYAN}按服务分析 (前5名):{Style.RESET_ALL}")
            print(tabulate(service_costs.head(), headers='keys', tablefmt='grid'))
        
        # 按区域分析
        region_costs = self.analyze_costs_by_region(df)
        if region_costs is not None:
            print(f"\n{Fore.CYAN}按区域分析:{Style.RESET_ALL}")
            print(tabulate(region_costs, headers='keys', tablefmt='grid'))


def print_banner():
    """打印程序横幅"""
    print("=" * 70)
    print("🚀 AWS费用分析器")
    print("=" * 70)
    print("快速分析AWS云服务费用，生成报告和可视化图表")
    print("=" * 70)

def print_menu():
    """打印主菜单"""
    print("\n📋 请选择分析选项:")
    print("1. 🕐 快速分析 (过去3个月)")
    print("2. 📅 自定义时间范围分析")
    print("3. 📊 生成详细报告和图表")
    print("4. 🔍 按服务分析费用")
    print("5. 🌍 按区域分析费用")
    print("6. 📈 费用趋势分析")
    print("7. 🎯 费用优化建议")
    print("8. ⚙️  配置检查")
    print("0. 🚪 退出")
    print("-" * 50)

def get_user_choice():
    """获取用户选择"""
    while True:
        try:
            choice = input("请输入选项编号 (0-8): ").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                return choice
            else:
                print("❌ 无效选项，请输入0-8之间的数字")
        except KeyboardInterrupt:
            print("\n👋 再见！")
            sys.exit(0)

def quick_analysis(analyzer):
    """快速分析过去3个月的费用"""
    print("\n🕐 正在执行快速分析...")
    
    # 获取过去3个月的数据
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    cost_data = analyzer.get_cost_data(start_date, end_date, 'DAILY')
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    analyzer.print_summary(df)
    analyzer.generate_cost_report(df, 'quick_analysis_report.txt')
    print(f"{Fore.GREEN}✅ 快速分析完成！报告已保存: quick_analysis_report.txt{Style.RESET_ALL}")

def custom_analysis(analyzer):
    """自定义时间范围分析"""
    print("\n📅 自定义时间范围分析")
    
    try:
        start_date = input("请输入开始日期 (YYYY-MM-DD): ").strip()
        end_date = input("请输入结束日期 (YYYY-MM-DD): ").strip()
        
        if not start_date or not end_date:
            print(f"{Fore.RED}❌ 日期不能为空{Style.RESET_ALL}")
            return
        
        # 验证日期格式
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        cost_data = analyzer.get_cost_data(start_date, end_date, 'DAILY')
        if not cost_data:
            print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
            return
        
        df = analyzer.parse_cost_data(cost_data)
        if df is None or df.empty:
            print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
            return
        
        analyzer.print_summary(df)
        analyzer.generate_cost_report(df, f'custom_analysis_{start_date}_to_{end_date}.txt')
        print(f"{Fore.GREEN}✅ 自定义分析完成！{Style.RESET_ALL}")
        
    except ValueError:
        print(f"{Fore.RED}❌ 日期格式错误，请使用 YYYY-MM-DD 格式{Style.RESET_ALL}")

def detailed_analysis(analyzer):
    """生成详细报告和图表"""
    print("\n📊 正在生成详细报告和图表...")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    # 生成所有报告和图表
    analyzer.print_summary(df)
    analyzer.generate_cost_report(df)
    
    try:
        analyzer.plot_costs_by_service(df)
        analyzer.plot_cost_trend(df)
        analyzer.create_interactive_dashboard(df)
        
        # 生成美观的HTML仪表板
        from create_beautiful_dashboard import create_beautiful_dashboard
        create_beautiful_dashboard(df, 'aws_cost_dashboard_beautiful.html')
        
        # 生成美观的PNG图表
        from create_beautiful_charts import (
            create_beautiful_service_chart,
            create_beautiful_trend_chart,
            create_beautiful_region_chart,
            create_comprehensive_dashboard
        )
        
        create_beautiful_service_chart(df, 'costs_by_service_beautiful.png')
        create_beautiful_trend_chart(df, 'cost_trend_beautiful.png')
        create_beautiful_region_chart(df, 'costs_by_region_beautiful.png')
        create_comprehensive_dashboard(df, 'aws_cost_dashboard_beautiful.png')
        
        print(f"\n{Fore.GREEN}✅ 详细分析完成！{Style.RESET_ALL}")
        print(f"{Fore.GREEN}生成的文件:{Style.RESET_ALL}")
        print(f"  - aws_cost_report.txt (费用报告)")
        print(f"  - costs_by_service.png (服务费用分布图)")
        print(f"  - cost_trend.png (费用趋势图)")
        print(f"  - aws_cost_dashboard.html (交互式仪表板)")
        print(f"  - aws_cost_dashboard_beautiful.html (美观仪表板)")
        print(f"  - costs_by_service_beautiful.png (美观服务费用图)")
        print(f"  - cost_trend_beautiful.png (美观费用趋势图)")
        print(f"  - costs_by_region_beautiful.png (美观区域费用图)")
        print(f"  - aws_cost_dashboard_beautiful.png (美观综合仪表板)")
        
    except ImportError as e:
        print(f"{Fore.YELLOW}警告: 某些图表功能需要额外的依赖: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.YELLOW}警告: 生成美观图表时出错: {e}{Style.RESET_ALL}")

def service_analysis(analyzer):
    """按服务分析费用"""
    print("\n🔍 按服务分析费用...")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    service_costs = analyzer.analyze_costs_by_service(df)
    if service_costs is not None:
        print(f"\n{Fore.CYAN}按服务分析 (前10名):{Style.RESET_ALL}")
        print(tabulate(service_costs.head(10), headers='keys', tablefmt='grid'))
        
        # 生成服务费用图表
        analyzer.plot_costs_by_service(df, 'service_analysis.png')
        print(f"{Fore.GREEN}✅ 服务分析完成！图表已保存: service_analysis.png{Style.RESET_ALL}")

def region_analysis(analyzer):
    """按区域分析费用"""
    print("\n🌍 按区域分析费用...")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    region_costs = analyzer.analyze_costs_by_region(df)
    if region_costs is not None:
        print(f"\n{Fore.CYAN}按区域分析:{Style.RESET_ALL}")
        print(tabulate(region_costs, headers='keys', tablefmt='grid'))
        
        # 生成区域费用图表
        from create_beautiful_charts import create_beautiful_region_chart
        create_beautiful_region_chart(df, 'region_analysis.png')
        print(f"{Fore.GREEN}✅ 区域分析完成！图表已保存: region_analysis.png{Style.RESET_ALL}")

def trend_analysis(analyzer):
    """费用趋势分析"""
    print("\n📈 费用趋势分析...")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    time_costs = analyzer.analyze_costs_by_time(df)
    if time_costs is not None:
        print(f"\n{Fore.CYAN}费用趋势分析:{Style.RESET_ALL}")
        print(tabulate(time_costs.tail(10), headers='keys', tablefmt='grid'))
        
        # 生成趋势图表
        analyzer.plot_cost_trend(df, 'trend_analysis.png')
        print(f"{Fore.GREEN}✅ 趋势分析完成！图表已保存: trend_analysis.png{Style.RESET_ALL}")

def optimization_suggestions(analyzer):
    """费用优化建议"""
    print("\n🎯 费用优化建议...")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    # 分析费用数据并提供建议
    total_cost = df['Cost'].sum()
    service_costs = analyzer.analyze_costs_by_service(df)
    
    print(f"\n{Fore.CYAN}费用优化建议:{Style.RESET_ALL}")
    print("-" * 50)
    
    if service_costs is not None and not service_costs.empty:
        top_service = service_costs.index[0]
        top_cost = service_costs.iloc[0]['总费用']
        percentage = (top_cost / total_cost) * 100
        
        print(f"1. 💰 最高费用服务: {top_service} (${top_cost:.2f}, {percentage:.1f}%)")
        print(f"   建议: 检查该服务的使用情况，考虑优化配置或使用更经济的替代方案")
        
        if len(service_costs) > 1:
            second_service = service_costs.index[1]
            second_cost = service_costs.iloc[1]['总费用']
            print(f"2. 📊 第二高费用服务: {second_service} (${second_cost:.2f})")
            print(f"   建议: 评估该服务的必要性，考虑按需使用")
    
    # 时间趋势分析
    time_costs = analyzer.analyze_costs_by_time(df)
    if time_costs is not None and len(time_costs) > 1:
        recent_cost = time_costs['Cost'].iloc[-1]
        avg_cost = time_costs['Cost'].mean()
        
        if recent_cost > avg_cost * 1.2:
            print(f"3. 📈 费用趋势: 最近费用 (${recent_cost:.2f}) 高于平均值 (${avg_cost:.2f})")
            print(f"   建议: 检查最近的服务使用情况，可能有异常费用")
        elif recent_cost < avg_cost * 0.8:
            print(f"4. 📉 费用趋势: 最近费用 (${recent_cost:.2f}) 低于平均值 (${avg_cost:.2f})")
            print(f"   建议: 继续保持当前的使用模式")
    
    print(f"\n{Fore.GREEN}✅ 优化建议生成完成！{Style.RESET_ALL}")

def config_check(analyzer):
    """配置检查"""
    print("\n⚙️  配置检查...")
    
    print(f"{Fore.CYAN}AWS配置状态:{Style.RESET_ALL}")
    print("-" * 30)
    
    # 检查AWS凭证
    if analyzer.ce_client:
        try:
            # 测试API调用
            response = analyzer.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'End': datetime.now().strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            print(f"✅ AWS凭证: 有效")
            print(f"✅ Cost Explorer API: 可访问")
            print(f"✅ 权限: 正常")
        except Exception as e:
            print(f"❌ AWS配置: 有问题 - {e}")
    else:
        print(f"❌ AWS客户端: 未初始化")
    
    # 检查依赖包
    print(f"\n{Fore.CYAN}依赖包检查:{Style.RESET_ALL}")
    print("-" * 30)
    
    required_packages = ['boto3', 'pandas', 'matplotlib', 'plotly', 'seaborn']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装")
        except ImportError:
            print(f"❌ {package}: 未安装")
    
    print(f"\n{Fore.GREEN}✅ 配置检查完成！{Style.RESET_ALL}")

def print_usage_guide():
    """打印使用指南"""
    print("=" * 80)
    print("🚀 AWS费用分析器 - 使用指南")
    print("=" * 80)
    print("一个功能强大的AWS云服务费用分析工具")
    print("=" * 80)
    print()
    print("📋 基本用法:")
    print("  aws_cost_analyzer [命令] [选项]")
    print()
    print("🔧 可用命令:")
    print("  quick         快速分析过去3个月的费用")
    print("  custom        自定义时间范围分析")
    print("  detailed      生成详细报告和图表")
    print("  service       按服务分析费用")
    print("  region        按区域分析费用")
    print("  trend         费用趋势分析")
    print("  optimize      费用优化建议")
    print("  config        配置检查")
    print("  help          显示此帮助信息")
    print()
    print("📅 时间范围选项 (用于 custom 命令):")
    print("  --start DATE  开始日期 (YYYY-MM-DD)")
    print("  --end DATE    结束日期 (YYYY-MM-DD)")
    print()
    print("📊 输出选项:")
    print("  --output DIR  指定输出目录 (默认: 当前目录)")
    print("  --format FMT  输出格式: txt, html, png, all (默认: all)")
    print()
    print("🔑 AWS配置选项:")
    print("  --profile NAME   使用指定的AWS配置文件")
    print("  --no-auto-setup  跳过自动AWS凭证设置")
    print()
    print("💡 使用示例:")
    print("  # 快速分析")
    print("  aws_cost_analyzer quick")
    print()
    print("  # 自定义时间范围分析")
    print("  aws_cost_analyzer custom --start 2024-01-01 --end 2024-12-31")
    print()
    print("  # 生成详细报告")
    print("  aws_cost_analyzer detailed --output ./reports")
    print()
    print("  # 按服务分析")
    print("  aws_cost_analyzer service --format png")
    print()
    print("  # 配置检查")
    print("  aws_cost_analyzer config")
    print()
    print("⚠️  注意事项:")
    print("  - 首次使用需要配置AWS凭证")
    print("  - 需要Cost Explorer API访问权限")
    print("  - 费用数据可能有1-2天延迟")
    print()
    print("📞 获取帮助:")
    print("  aws_cost_analyzer help")
    print("  aws_cost_analyzer [命令] --help")
    print("=" * 80)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='AWS费用分析器 - 分析AWS云服务费用',
        add_help=False
    )
    
    # 主命令
    parser.add_argument('command', nargs='?', default='help',
                       choices=['quick', 'custom', 'detailed', 'service', 'region', 
                               'trend', 'optimize', 'config', 'help'],
                       help='要执行的命令')
    
    # 时间范围选项
    parser.add_argument('--start', type=str, 
                       help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end', type=str,
                       help='结束日期 (YYYY-MM-DD)')
    
    # 输出选项
    parser.add_argument('--output', type=str, default='.',
                       help='输出目录 (默认: 当前目录)')
    parser.add_argument('--format', type=str, default='all',
                       choices=['txt', 'html', 'png', 'all'],
                       help='输出格式 (默认: all)')
    
    # AWS配置选项
    parser.add_argument('--profile', type=str,
                       help='AWS配置文件名称')
    parser.add_argument('--no-auto-setup', action='store_true',
                       help='跳过自动AWS凭证设置')
    
    # 帮助选项
    parser.add_argument('-h', '--help', action='store_true',
                       help='显示帮助信息')
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 显示帮助信息
    if args.command == 'help' or args.help:
        print_usage_guide()
        return
    
    # 创建分析器实例
    analyzer = AWSCostAnalyzer(
        profile_name=args.profile,
        auto_setup=not args.no_auto_setup
    )
    
    if not analyzer.ce_client:
        print(f"{Fore.RED}❌ AWS配置失败，无法继续{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}请检查AWS凭证配置或使用 --help 查看帮助{Style.RESET_ALL}")
        return
    
    # 根据命令执行相应功能
    if args.command == 'quick':
        quick_analysis_cli(analyzer, args)
    elif args.command == 'custom':
        custom_analysis_cli(analyzer, args)
    elif args.command == 'detailed':
        detailed_analysis_cli(analyzer, args)
    elif args.command == 'service':
        service_analysis_cli(analyzer, args)
    elif args.command == 'region':
        region_analysis_cli(analyzer, args)
    elif args.command == 'trend':
        trend_analysis_cli(analyzer, args)
    elif args.command == 'optimize':
        optimization_suggestions_cli(analyzer, args)
    elif args.command == 'config':
        config_check_cli(analyzer, args)

def quick_analysis_cli(analyzer, args):
    """命令行快速分析"""
    print(f"{Fore.CYAN}🕐 快速分析过去3个月的费用...{Style.RESET_ALL}")
    
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    cost_data = analyzer.get_cost_data(start_date, end_date, 'DAILY')
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    analyzer.print_summary(df)
    
    if args.format in ['txt', 'all']:
        output_file = os.path.join(args.output, 'quick_analysis_report.txt')
        analyzer.generate_cost_report(df, output_file)
        print(f"{Fore.GREEN}✅ 报告已保存: {output_file}{Style.RESET_ALL}")

def custom_analysis_cli(analyzer, args):
    """命令行自定义分析"""
    if not args.start or not args.end:
        print(f"{Fore.RED}❌ 自定义分析需要指定 --start 和 --end 参数{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}示例: python aws_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📅 自定义时间范围分析: {args.start} 到 {args.end}{Style.RESET_ALL}")
    
    try:
        # 验证日期格式
        datetime.strptime(args.start, '%Y-%m-%d')
        datetime.strptime(args.end, '%Y-%m-%d')
        
        cost_data = analyzer.get_cost_data(args.start, args.end, 'DAILY')
        if not cost_data:
            print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
            return
        
        df = analyzer.parse_cost_data(cost_data)
        if df is None or df.empty:
            print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
            return
        
        analyzer.print_summary(df)
        
        if args.format in ['txt', 'all']:
            output_file = os.path.join(args.output, f'custom_analysis_{args.start}_to_{args.end}.txt')
            analyzer.generate_cost_report(df, output_file)
            print(f"{Fore.GREEN}✅ 报告已保存: {output_file}{Style.RESET_ALL}")
            
    except ValueError:
        print(f"{Fore.RED}❌ 日期格式错误，请使用 YYYY-MM-DD 格式{Style.RESET_ALL}")

def detailed_analysis_cli(analyzer, args):
    """命令行详细分析"""
    print(f"{Fore.CYAN}📊 生成详细报告和图表...{Style.RESET_ALL}")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    analyzer.print_summary(df)
    
    # 生成报告和图表
    if args.format in ['txt', 'all']:
        output_file = os.path.join(args.output, 'aws_cost_report.txt')
        analyzer.generate_cost_report(df, output_file)
        print(f"{Fore.GREEN}✅ 报告已保存: {output_file}{Style.RESET_ALL}")
    
    if args.format in ['png', 'all']:
        try:
            service_file = os.path.join(args.output, 'costs_by_service.png')
            trend_file = os.path.join(args.output, 'cost_trend.png')
            analyzer.plot_costs_by_service(df, service_file)
            analyzer.plot_cost_trend(df, trend_file)
            print(f"{Fore.GREEN}✅ 图表已保存: {service_file}, {trend_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}警告: 生成图表时出错: {e}{Style.RESET_ALL}")
    
    if args.format in ['html', 'all']:
        try:
            dashboard_file = os.path.join(args.output, 'aws_cost_dashboard.html')
            analyzer.create_interactive_dashboard(df, dashboard_file)
            print(f"{Fore.GREEN}✅ 仪表板已保存: {dashboard_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}警告: 生成仪表板时出错: {e}{Style.RESET_ALL}")

def service_analysis_cli(analyzer, args):
    """命令行服务分析"""
    print(f"{Fore.CYAN}🔍 按服务分析费用...{Style.RESET_ALL}")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    service_costs = analyzer.analyze_costs_by_service(df)
    if service_costs is not None:
        print(f"\n{Fore.CYAN}按服务分析 (前10名):{Style.RESET_ALL}")
        print(tabulate(service_costs.head(10), headers='keys', tablefmt='grid'))
        
        if args.format in ['png', 'all']:
            output_file = os.path.join(args.output, 'service_analysis.png')
            analyzer.plot_costs_by_service(df, output_file)
            print(f"{Fore.GREEN}✅ 图表已保存: {output_file}{Style.RESET_ALL}")

def region_analysis_cli(analyzer, args):
    """命令行区域分析"""
    print(f"{Fore.CYAN}🌍 按区域分析费用...{Style.RESET_ALL}")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    region_costs = analyzer.analyze_costs_by_region(df)
    if region_costs is not None:
        print(f"\n{Fore.CYAN}按区域分析:{Style.RESET_ALL}")
        print(tabulate(region_costs, headers='keys', tablefmt='grid'))
        
        if args.format in ['png', 'all']:
            try:
                from create_beautiful_charts import create_beautiful_region_chart
                output_file = os.path.join(args.output, 'region_analysis.png')
                create_beautiful_region_chart(df, output_file)
                print(f"{Fore.GREEN}✅ 图表已保存: {output_file}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}警告: 生成图表时出错: {e}{Style.RESET_ALL}")

def trend_analysis_cli(analyzer, args):
    """命令行趋势分析"""
    print(f"{Fore.CYAN}📈 费用趋势分析...{Style.RESET_ALL}")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    time_costs = analyzer.analyze_costs_by_time(df)
    if time_costs is not None:
        print(f"\n{Fore.CYAN}费用趋势分析:{Style.RESET_ALL}")
        print(tabulate(time_costs.tail(10), headers='keys', tablefmt='grid'))
        
        if args.format in ['png', 'all']:
            output_file = os.path.join(args.output, 'trend_analysis.png')
            analyzer.plot_cost_trend(df, output_file)
            print(f"{Fore.GREEN}✅ 图表已保存: {output_file}{Style.RESET_ALL}")

def optimization_suggestions_cli(analyzer, args):
    """命令行优化建议"""
    print(f"{Fore.CYAN}🎯 费用优化建议...{Style.RESET_ALL}")
    
    cost_data = analyzer.get_cost_data()
    if not cost_data:
        print(f"{Fore.RED}无法获取费用数据{Style.RESET_ALL}")
        return
    
    df = analyzer.parse_cost_data(cost_data)
    if df is None or df.empty:
        print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
        return
    
    # 分析费用数据并提供建议
    total_cost = df['Cost'].sum()
    service_costs = analyzer.analyze_costs_by_service(df)
    
    print(f"\n{Fore.CYAN}费用优化建议:{Style.RESET_ALL}")
    print("-" * 50)
    
    if service_costs is not None and not service_costs.empty:
        top_service = service_costs.index[0]
        top_cost = service_costs.iloc[0]['总费用']
        percentage = (top_cost / total_cost) * 100
        
        print(f"1. 💰 最高费用服务: {top_service} (${top_cost:.2f}, {percentage:.1f}%)")
        print(f"   建议: 检查该服务的使用情况，考虑优化配置或使用更经济的替代方案")
        
        if len(service_costs) > 1:
            second_service = service_costs.index[1]
            second_cost = service_costs.iloc[1]['总费用']
            print(f"2. 📊 第二高费用服务: {second_service} (${second_cost:.2f})")
            print(f"   建议: 评估该服务的必要性，考虑按需使用")
    
    # 时间趋势分析
    time_costs = analyzer.analyze_costs_by_time(df)
    if time_costs is not None and len(time_costs) > 1:
        recent_cost = time_costs['Cost'].iloc[-1]
        avg_cost = time_costs['Cost'].mean()
        
        if recent_cost > avg_cost * 1.2:
            print(f"3. 📈 费用趋势: 最近费用 (${recent_cost:.2f}) 高于平均值 (${avg_cost:.2f})")
            print(f"   建议: 检查最近的服务使用情况，可能有异常费用")
        elif recent_cost < avg_cost * 0.8:
            print(f"4. 📉 费用趋势: 最近费用 (${recent_cost:.2f}) 低于平均值 (${avg_cost:.2f})")
            print(f"   建议: 继续保持当前的使用模式")

def config_check_cli(analyzer, args):
    """命令行配置检查"""
    print(f"{Fore.CYAN}⚙️  配置检查...{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}AWS配置状态:{Style.RESET_ALL}")
    print("-" * 30)
    
    # 检查AWS凭证
    if analyzer.ce_client:
        try:
            # 测试API调用
            response = analyzer.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'End': datetime.now().strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            print(f"✅ AWS凭证: 有效")
            print(f"✅ Cost Explorer API: 可访问")
            print(f"✅ 权限: 正常")
        except Exception as e:
            print(f"❌ AWS配置: 有问题 - {e}")
    else:
        print(f"❌ AWS客户端: 未初始化")
    
    # 检查依赖包
    print(f"\n{Fore.CYAN}依赖包检查:{Style.RESET_ALL}")
    print("-" * 30)
    
    required_packages = ['boto3', 'pandas', 'matplotlib', 'plotly', 'seaborn']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装")
        except ImportError:
            print(f"❌ {package}: 未安装")


if __name__ == "__main__":
    main()
