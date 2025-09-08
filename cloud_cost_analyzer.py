#!/usr/bin/env python3
"""
Cloud Cost Analyzer - 多云费用分析工具
用户友好的入口脚本，保持向后兼容性

支持的命令：
- python cloud_cost_analyzer.py quick                    # 快速分析
- python cloud_cost_analyzer.py multi-cloud             # 多云对比
- python cloud_cost_analyzer.py config                  # 配置检查  
- python cloud_cost_analyzer.py custom --start --end    # 自定义分析
"""
import sys
import os
from typing import Optional, List
import argparse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from cloud_cost_analyzer.core.multi_cloud_analyzer import MultiCloudAnalyzer
    from cloud_cost_analyzer.core.analyzer import AWSCostAnalyzer  
    from cloud_cost_analyzer.utils.config import Config
    from colorama import init, Fore, Style
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请先安装依赖: pip install -e .")
    sys.exit(1)

# 初始化colorama
init()


def setup_aws_credentials() -> bool:
    """设置AWS凭证"""
    import boto3
    from botocore.exceptions import NoCredentialsError, ClientError
    
    print(f"{Fore.CYAN}🔑 设置AWS凭证...{Style.RESET_ALL}")
    
    try:
        session = boto3.Session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        account_id = identity.get('Account')
        print(f"{Fore.GREEN}✅ 检测到现有AWS凭证配置{Style.RESET_ALL}")
        print(f"账户ID: {account_id}")
        return True
    except NoCredentialsError:
        print(f"{Fore.YELLOW}⚠️  未找到AWS凭证，请配置环境变量或AWS CLI{Style.RESET_ALL}")
        return False
    except ClientError as e:
        print(f"{Fore.RED}❌ AWS凭证验证失败: {e}{Style.RESET_ALL}")
        return False


def quick_analysis_cli(args) -> None:
    """快速分析 - 自动选择第一个可用的云平台"""
    try:
        # 创建多云分析器
        multi_analyzer = MultiCloudAnalyzer()
        
        # 检查所有云平台连接状态
        print(f"{Fore.CYAN}🔍 检查云平台连接状态...{Style.RESET_ALL}")
        connections = multi_analyzer.test_connections()
        
        # 显示连接状态
        for provider, (is_connected, message) in connections.items():
            provider_names = {
                'aws': 'AWS',
                'aliyun': '阿里云', 
                'tencent': '腾讯云',
                'volcengine': '火山云'
            }
            provider_name = provider_names.get(provider, provider)
            
            if is_connected:
                print(f"{Fore.GREEN}✅ {provider_name}: {message}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️  {provider_name}: {message}{Style.RESET_ALL}")
        
        # 找到第一个可用的云平台
        available_provider = None
        for provider, (is_connected, message) in connections.items():
            if is_connected:
                available_provider = provider
                break
        
        if not available_provider:
            print(f"\n{Fore.RED}❌ 没有可用的云平台连接{Style.RESET_ALL}")
            print("请配置至少一个云平台的凭证，参考：python cloud_cost_analyzer.py help")
            return
        
        provider_names = {
            'aws': 'AWS',
            'aliyun': '阿里云',
            'tencent': '腾讯云',
            'volcengine': '火山云'
        }
        provider_name = provider_names.get(available_provider, available_provider)
        
        print(f"\n{Fore.CYAN}🚀 使用 {provider_name} 进行快速分析（过去1年）{Style.RESET_ALL}")
        
        # 根据云平台类型创建对应的分析器
        if available_provider == 'aws':
            analyzer = AWSCostAnalyzer()
            analysis_result = analyzer.analyze_costs()
            
            if not analysis_result:
                print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
                return
            
            # 打印分析结果
            analyzer.print_enhanced_analysis_results(analysis_result)
            
            # 生成报告
            generated_files = analyzer.generate_reports(analysis_result, args.output, ['txt', 'html'])
            for format_type, file_path in generated_files.items():
                print(f"{Fore.GREEN}✅ 报告已保存: {file_path}{Style.RESET_ALL}")
                
        else:
            # 使用多云分析器分析单个平台
            raw_data, service_costs, region_costs = multi_analyzer.analyze_single_provider_costs(available_provider)
            if not raw_data:
                print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
                return
                
            # 打印分析结果
            multi_analyzer.print_provider_analysis(available_provider, raw_data, service_costs, region_costs)
            
            # 生成报告
            generated_files = multi_analyzer.generate_single_provider_reports(
                available_provider, raw_data, service_costs, region_costs, args.output, ['txt', 'html']
            )
            for format_type, file_path in generated_files.items():
                print(f"{Fore.GREEN}✅ 报告已保存: {file_path}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ 快速分析失败: {e}{Style.RESET_ALL}")


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
        print(f"{Fore.CYAN}🌐 开始多云费用分析...{Style.RESET_ALL}")
        raw_data, service_costs, region_costs = multi_analyzer.analyze_multi_cloud_costs()
        
        if not raw_data:
            print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
            return
        
        # 打印分析结果
        multi_analyzer.print_multi_cloud_summary(raw_data)
        multi_analyzer.print_multi_cloud_service_analysis(service_costs)
        multi_analyzer.print_multi_cloud_region_analysis(region_costs)
        
        # 生成报告
        generated_files = multi_analyzer.generate_multi_cloud_reports(
            raw_data, service_costs, region_costs, args.output, ['txt', 'html']
        )
        for format_type, file_path in generated_files.items():
            print(f"{Fore.GREEN}✅ 多云报告已保存: {file_path}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ 多云分析失败: {e}{Style.RESET_ALL}")


def config_check_cli(args) -> None:
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
    else:
        print(f"{Fore.YELLOW}⚠️  配置文件: 未找到或格式错误{Style.RESET_ALL}")


def custom_analysis_cli(args) -> None:
    """自定义时间范围分析"""
    try:
        if not args.start or not args.end:
            print(f"{Fore.RED}❌ 请指定开始和结束日期: --start YYYY-MM-DD --end YYYY-MM-DD{Style.RESET_ALL}")
            return
            
        print(f"{Fore.CYAN}📊 自定义分析 ({args.start} 至 {args.end}){Style.RESET_ALL}")
        
        # 使用AWS分析器进行自定义分析
        analyzer = AWSCostAnalyzer()
        analysis_result = analyzer.analyze_costs_custom(args.start, args.end)
        
        if not analysis_result:
            print(f"{Fore.RED}没有费用数据可分析{Style.RESET_ALL}")
            return
        
        # 打印分析结果
        analyzer.print_enhanced_analysis_results(analysis_result)
        
        # 生成报告
        generated_files = analyzer.generate_reports(analysis_result, args.output, ['txt', 'html'])
        for format_type, file_path in generated_files.items():
            print(f"{Fore.GREEN}✅ 报告已保存: {file_path}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ 自定义分析失败: {e}{Style.RESET_ALL}")


def print_help():
    """打印帮助信息"""
    help_text = f"""
{Fore.CYAN}Cloud Cost Analyzer - 多云费用分析工具{Style.RESET_ALL}

{Fore.YELLOW}基本用法:{Style.RESET_ALL}
  python cloud_cost_analyzer.py <命令> [选项]

{Fore.YELLOW}可用命令:{Style.RESET_ALL}
  {Fore.GREEN}quick{Style.RESET_ALL}         快速分析（自动选择第一个可用云平台）
  {Fore.GREEN}multi-cloud{Style.RESET_ALL}   多云对比分析
  {Fore.GREEN}config{Style.RESET_ALL}        检查配置和连接状态
  {Fore.GREEN}custom{Style.RESET_ALL}        自定义时间范围分析 (需要 --start --end)
  {Fore.GREEN}help{Style.RESET_ALL}          显示此帮助信息

{Fore.YELLOW}选项:{Style.RESET_ALL}
  --output DIR      指定输出目录 (默认: 当前目录)
  --format FORMAT   输出格式: txt, html, all (默认: all)
  --start DATE      开始日期 (YYYY-MM-DD, 用于custom命令)
  --end DATE        结束日期 (YYYY-MM-DD, 用于custom命令)

{Fore.YELLOW}示例:{Style.RESET_ALL}
  python cloud_cost_analyzer.py quick
  python cloud_cost_analyzer.py multi-cloud --output ./reports
  python cloud_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31
  python cloud_cost_analyzer.py config

{Fore.YELLOW}配置说明:{Style.RESET_ALL}
  请参考 API_KEYS_GUIDE.md 了解如何配置各云平台的API密钥
"""
    print(help_text)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Cloud Cost Analyzer - 多云费用分析工具',
        add_help=False
    )
    
    parser.add_argument('command', nargs='?', choices=['quick', 'multi-cloud', 'config', 'custom', 'help'], 
                       help='要执行的命令')
    parser.add_argument('--output', default='.', help='输出目录')
    parser.add_argument('--format', choices=['txt', 'html', 'all'], default='all', help='输出格式')
    parser.add_argument('--start', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end', help='结束日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if not args.command or args.command == 'help':
        print_help()
        return
    
    # 执行对应命令
    if args.command == 'quick':
        quick_analysis_cli(args)
    elif args.command == 'multi-cloud':
        multi_cloud_analysis_cli(args)
    elif args.command == 'config':
        config_check_cli(args)
    elif args.command == 'custom':
        custom_analysis_cli(args)


if __name__ == '__main__':
    main()