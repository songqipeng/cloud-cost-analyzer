#!/usr/bin/env python3
"""
Cloud Cost Analyzer - 多云费用分析器
一个功能强大的多云服务费用分析工具，支持AWS、阿里云、腾讯云、火山云
"""
import sys
import os
import argparse
import subprocess
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aws_cost_analyzer.core.analyzer import AWSCostAnalyzer
from aws_cost_analyzer.core.multi_cloud_analyzer import MultiCloudAnalyzer
from aws_cost_analyzer.utils.config import Config
from aws_cost_analyzer.utils.validators import DataValidator
from aws_cost_analyzer.utils.logger import get_logger
from aws_cost_analyzer.utils.exceptions import AWSAnalyzerError, AWSConnectionError
from colorama import init, Fore, Style

logger = get_logger()

# 初始化colorama
init(autoreset=True)


def check_and_install_dependencies():
    """检查并自动安装所需的依赖包"""
    required_packages = {
        'boto3': 'boto3>=1.34.0',
        'pandas': 'pandas>=2.2.0',
        'matplotlib': 'matplotlib>=3.8.0',
        'seaborn': 'seaborn>=0.13.0',
        'plotly': 'plotly>=5.17.0',
        'dateutil': 'python-dateutil>=2.8.2',
        'rich': 'rich>=13.0.0',
        'colorama': 'colorama>=0.4.6',
        'requests': 'requests>=2.31.0',
        'schedule': 'schedule>=1.2.0'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        logger.info("检测到缺少依赖包，正在自动安装...")
        print(f"{Fore.YELLOW}📦 检测到缺少依赖包，正在自动安装...{Style.RESET_ALL}")
        for package in missing_packages:
            try:
                logger.info(f"正在安装 {package}...")
                print(f"正在安装 {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                logger.info(f"{package} 安装成功")
                print(f"{Fore.GREEN}✅ {package} 安装成功{Style.RESET_ALL}")
            except subprocess.CalledProcessError as e:
                logger.error(f"{package} 安装失败: {e}")
                print(f"{Fore.RED}❌ {package} 安装失败: {e}{Style.RESET_ALL}")
                return False
    
    return True


def setup_aws_credentials():
    """设置AWS凭证"""
    print(f"{Fore.CYAN}🔑 设置AWS凭证...{Style.RESET_ALL}")
    
    # 检查是否已有AWS凭证
    try:
        import boto3
        session = boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"{Fore.GREEN}✅ 检测到现有AWS凭证配置{Style.RESET_ALL}")
        print(f"账户ID: {identity.get('Account')}")
        return True
    except Exception:
        pass
    
    print(f"{Fore.YELLOW}未检测到AWS凭证，请配置AWS凭证{Style.RESET_ALL}")
    print("请使用以下方式之一配置AWS凭证:")
    print("1. AWS CLI: aws configure")
    print("2. 环境变量: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
    print("3. IAM角色 (推荐用于EC2)")
    print("4. AWS配置文件: ~/.aws/credentials")
    
    return False


def quick_analysis_cli(analyzer: AWSCostAnalyzer, args) -> None:
    """命令行快速分析"""
    try:
        # 分析费用数据
        df, service_costs, region_costs = analyzer.analyze_costs()
        
        if df is None or df.empty:
            print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
            return
        
        # 打印分析结果
        analyzer.print_summary(df)
        analyzer.print_service_analysis(service_costs)
        analyzer.print_region_analysis(region_costs)
        
        # 发送通知
        if analyzer.notification_manager:
            analyzer.send_notifications(df, service_costs, region_costs)
        
        # 生成报告
        if args.format in ['txt', 'all']:
            generated_files = analyzer.generate_reports(
                df, service_costs, region_costs, args.output, ['txt']
            )
            if 'txt' in generated_files:
                print(f"{Fore.GREEN}✅ 报告已保存: {generated_files['txt']}{Style.RESET_ALL}")
        
        if args.format in ['html', 'all']:
            generated_files = analyzer.generate_reports(
                df, service_costs, region_costs, args.output, ['html']
            )
            if 'html' in generated_files:
                print(f"{Fore.GREEN}✅ 报告已保存: {generated_files['html']}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ 快速分析失败: {e}{Style.RESET_ALL}")


def custom_analysis_cli(analyzer: AWSCostAnalyzer, args) -> None:
    """命令行自定义分析"""
    if not args.start or not args.end:
        print(f"{Fore.RED}❌ 自定义分析需要指定 --start 和 --end 参数{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}示例: python aws_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31{Style.RESET_ALL}")
        return
    
    # 验证日期格式
    is_valid, error_msg = DataValidator.validate_date_range(args.start, args.end)
    if not is_valid:
        print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
        return
    
    try:
        # 分析费用数据
        df, service_costs, region_costs = analyzer.analyze_costs(args.start, args.end)
        
        if df is None or df.empty:
            print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
            return
        
        # 打印分析结果
        analyzer.print_summary(df)
        analyzer.print_service_analysis(service_costs)
        analyzer.print_region_analysis(region_costs)
        
        # 发送通知
        if analyzer.notification_manager:
            time_range = f"{args.start} 到 {args.end}"
            analyzer.send_notifications(df, service_costs, region_costs, time_range)
        
        # 生成报告
        if args.format in ['txt', 'all']:
            generated_files = analyzer.generate_reports(
                df, service_costs, region_costs, args.output, ['txt']
            )
            if 'txt' in generated_files:
                print(f"{Fore.GREEN}✅ 报告已保存: {generated_files['txt']}{Style.RESET_ALL}")
        
        if args.format in ['html', 'all']:
            generated_files = analyzer.generate_reports(
                df, service_costs, region_costs, args.output, ['html']
            )
            if 'html' in generated_files:
                print(f"{Fore.GREEN}✅ 报告已保存: {generated_files['html']}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ 自定义分析失败: {e}{Style.RESET_ALL}")


def multi_cloud_analysis_cli(args) -> None:
    """多云分析"""
    try:
        # 创建多云分析器实例
        multi_analyzer = MultiCloudAnalyzer()
        
        # 加载配置并初始化通知管理器
        config = Config.load_config()
        if config:
            multi_analyzer.initialize_notifications(config)
        
        # 分析多云费用数据
        raw_data, service_costs, region_costs = multi_analyzer.analyze_multi_cloud_costs()
        
        if not raw_data:
            print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
            return
        
        # 打印分析结果
        multi_analyzer.print_multi_cloud_summary(raw_data)
        multi_analyzer.print_multi_cloud_service_analysis(service_costs)
        multi_analyzer.print_multi_cloud_region_analysis(region_costs)
        
        # 生成报告
        if args.format in ['txt', 'all']:
            generated_files = multi_analyzer.generate_multi_cloud_reports(
                raw_data, service_costs, region_costs, args.output, ['txt']
            )
            if 'txt' in generated_files:
                print(f"{Fore.GREEN}✅ 多云报告已保存: {generated_files['txt']}{Style.RESET_ALL}")
        
        if args.format in ['html', 'all']:
            generated_files = multi_analyzer.generate_multi_cloud_reports(
                raw_data, service_costs, region_costs, args.output, ['html']
            )
            if 'html' in generated_files:
                print(f"{Fore.GREEN}✅ 多云报告已保存: {generated_files['html']}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ 多云分析失败: {e}{Style.RESET_ALL}")


def config_check_cli(analyzer: AWSCostAnalyzer, args) -> None:
    """配置检查"""
    print(f"{Fore.CYAN}🔧 配置检查{Style.RESET_ALL}")
    print("=" * 50)
    
    # 检查多云连接
    multi_analyzer = MultiCloudAnalyzer()
    connections = multi_analyzer.test_connections()
    
    for provider, (is_connected, message) in connections.items():
        provider_names = {
            'aws': 'AWS',
            'aliyun': '阿里云', 
            'tencent': '腾讯云',
            'volcengine': '火山云'
        }
        provider_name = provider_names.get(provider, provider)
        
        if is_connected:
            print(f"{Fore.GREEN}✅ {provider_name}连接: {message}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ {provider_name}连接: {message}{Style.RESET_ALL}")
    
    # 检查配置文件
    config = Config.load_config()
    if config:
        print(f"{Fore.GREEN}✅ 配置文件: 已加载{Style.RESET_ALL}")
        
        # 验证配置
        is_valid, errors = DataValidator.validate_config(config)
        if is_valid:
            print(f"{Fore.GREEN}✅ 配置验证: 通过{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ 配置验证: 失败{Style.RESET_ALL}")
            for error in errors:
                print(f"  - {error}")
    else:
        print(f"{Fore.YELLOW}⚠️  配置文件: 未找到{Style.RESET_ALL}")


def print_usage_guide():
    """打印使用指南"""
    print("=" * 80)
    print(f"{Fore.CYAN}🚀 Cloud Cost Analyzer - 多云费用分析器{Style.RESET_ALL}")
    print("=" * 80)
    print("支持AWS、阿里云、腾讯云、火山云的多云费用分析工具")
    print("=" * 80)
    print()
    print(f"{Fore.YELLOW}📋 基本用法:{Style.RESET_ALL}")
    print("  aws_cost_analyzer [命令] [选项]")
    print()
    print(f"{Fore.YELLOW}🔧 可用命令:{Style.RESET_ALL}")
    print("  quick         快速分析过去1年的AWS费用")
    print("  custom        自定义时间范围AWS分析")
    print("  multi-cloud   多云费用分析 (AWS + 阿里云 + 腾讯云 + 火山云)")
    print("  config        配置检查")
    print("  help          显示此帮助信息")
    print()
    print(f"{Fore.YELLOW}📅 时间范围选项 (用于 custom 命令):{Style.RESET_ALL}")
    print("  --start DATE  开始日期 (YYYY-MM-DD)")
    print("  --end DATE    结束日期 (YYYY-MM-DD)")
    print()
    print(f"{Fore.YELLOW}📊 输出选项:{Style.RESET_ALL}")
    print("  --output DIR  指定输出目录 (默认: 当前目录)")
    print("  --format FMT  输出格式: txt, html, all (默认: all)")
    print()
    print(f"{Fore.YELLOW}💡 使用示例:{Style.RESET_ALL}")
    print("  # 快速分析AWS费用")
    print("  aws_cost_analyzer quick")
    print()
    print("  # 自定义时间范围AWS分析")
    print("  aws_cost_analyzer custom --start 2024-01-01 --end 2024-12-31")
    print()
    print("  # 多云费用分析 (AWS + 阿里云 + 腾讯云 + 火山云)")
    print("  cloud_cost_analyzer multi-cloud")
    print()
    print("  # 配置检查")
    print("  aws_cost_analyzer config")
    print()
    print(f"{Fore.YELLOW}⚠️  注意事项:{Style.RESET_ALL}")
    print("  - 首次使用需要配置AWS凭证")
    print("  - 需要Cost Explorer API访问权限")
    print("  - 费用数据可能有1-2天延迟")
    print()
    print(f"{Fore.YELLOW}📞 获取帮助:{Style.RESET_ALL}")
    print("  aws_cost_analyzer help")
    print("  aws_cost_analyzer [命令] --help")
    print("=" * 80)


def main():
    """主函数"""
    # 检查并安装依赖
    if not check_and_install_dependencies():
        print(f"{Fore.RED}❌ 依赖安装失败，请手动安装缺少的包{Style.RESET_ALL}")
        return 1
    
    # 设置AWS凭证
    if not setup_aws_credentials():
        print(f"{Fore.RED}❌ AWS凭证配置失败{Style.RESET_ALL}")
        return 1
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='AWS费用分析器',
        add_help=False
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 快速分析命令
    quick_parser = subparsers.add_parser('quick', help='快速分析过去1年的费用')
    quick_parser.add_argument('--output', default='.', help='输出目录')
    quick_parser.add_argument('--format', choices=['txt', 'html', 'all'], default='all', help='输出格式')
    
    # 自定义分析命令
    custom_parser = subparsers.add_parser('custom', help='自定义时间范围分析')
    custom_parser.add_argument('--start', required=True, help='开始日期 (YYYY-MM-DD)')
    custom_parser.add_argument('--end', required=True, help='结束日期 (YYYY-MM-DD)')
    custom_parser.add_argument('--output', default='.', help='输出目录')
    custom_parser.add_argument('--format', choices=['txt', 'html', 'all'], default='all', help='输出格式')
    
    # 多云分析命令
    multi_cloud_parser = subparsers.add_parser('multi-cloud', help='多云费用分析 (AWS + 阿里云)')
    multi_cloud_parser.add_argument('--output', default='.', help='输出目录')
    multi_cloud_parser.add_argument('--format', choices=['txt', 'html', 'all'], default='all', help='输出格式')
    
    # 配置检查命令
    config_parser = subparsers.add_parser('config', help='配置检查')
    
    # 帮助命令
    help_parser = subparsers.add_parser('help', help='显示帮助信息')
    
    args = parser.parse_args()
    
    # 如果没有指定命令或指定了help，显示使用指南
    if not args.command or args.command == 'help':
        print_usage_guide()
        return 0
    
    try:
        # 创建分析器实例
        analyzer = AWSCostAnalyzer()
        
        # 加载配置并初始化通知管理器
        config = Config.load_config()
        if config:
            analyzer.initialize_notifications(config)
        
        # 执行相应命令
        if args.command == 'quick':
            quick_analysis_cli(analyzer, args)
        elif args.command == 'custom':
            custom_analysis_cli(analyzer, args)
        elif args.command == 'multi-cloud':
            multi_cloud_analysis_cli(args)
        elif args.command == 'config':
            config_check_cli(analyzer, args)
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}用户中断操作{Style.RESET_ALL}")
        return 1
    except Exception as e:
        print(f"{Fore.RED}❌ 程序执行失败: {e}{Style.RESET_ALL}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
