"""
CLI命令模块
"""
import click
import sys
import os
from datetime import datetime, date, timedelta
from typing import Optional

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from cloud_cost_analyzer.core.analyzer import AWSCostAnalyzer
from cloud_cost_analyzer.core.multi_cloud_analyzer import MultiCloudAnalyzer
from cloud_cost_analyzer.utils.config import Config
from cloud_cost_analyzer.utils.logger import get_logger
from cloud_cost_analyzer.utils.exceptions import AWSAnalyzerError, AWSConnectionError
from cloud_cost_analyzer.reports.generator import ReportGenerator

logger = get_logger()


@click.group()
@click.option('--config', '-c', default='config.json', help='配置文件路径')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.pass_context
def cli(ctx: click.Context, config: str, verbose: bool) -> None:
    """Cloud Cost Analyzer - 多云费用分析工具"""
    ctx.ensure_object(dict)
    
    try:
        if os.path.exists(config):
            ctx.obj['config'] = Config(config_file=config)
        else:
            # 使用默认配置
            ctx.obj['config'] = Config(config_dict={})
            
        ctx.obj['verbose'] = verbose
        
    except Exception as e:
        click.echo(f"❌ 配置加载失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def quick(ctx: click.Context) -> None:
    """快速AWS费用分析（过去1年）"""
    config = ctx.obj['config']
    
    try:
        analyzer = AWSCostAnalyzer(config=config)
        
        # 计算过去一年的日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        click.echo("🔍 开始AWS快速费用分析...")
        result = analyzer.analyze(start_date=start_date, end_date=end_date)
        
        # 生成报告
        generator = ReportGenerator(config)
        generator.generate_console_report(result, 'AWS')
        
        click.echo("✅ 分析完成!")
        
    except AWSConnectionError as e:
        click.echo(f"❌ AWS连接失败: {e}", err=True)
        sys.exit(1)
    except AWSAnalyzerError as e:
        click.echo(f"❌ 分析失败: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ 未知错误: {e}", err=True)
        if ctx.obj['verbose']:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--start', required=True, help='开始日期 (YYYY-MM-DD)')
@click.option('--end', required=True, help='结束日期 (YYYY-MM-DD)')
@click.option('--output', '-o', default='.', help='输出目录')
@click.option('--format', 'output_format', 
              type=click.Choice(['txt', 'html', 'all']), 
              default='all', help='输出格式')
@click.pass_context
def custom(ctx: click.Context, start: str, end: str, output: str, output_format: str) -> None:
    """自定义时间范围AWS分析"""
    config = ctx.obj['config']
    
    try:
        # 解析日期
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        
        analyzer = AWSCostAnalyzer(config=config)
        
        click.echo(f"🔍 分析AWS费用: {start} 到 {end}")
        result = analyzer.analyze(start_date=start_date, end_date=end_date)
        
        # 生成报告
        generator = ReportGenerator(config)
        generator.generate_console_report(result, 'AWS')
        
        if output_format in ['txt', 'all']:
            txt_file = generator.generate_text_report(result, 'AWS', output)
            click.echo(f"📄 文本报告已保存: {txt_file}")
            
        if output_format in ['html', 'all']:
            html_file = generator.generate_html_report(result, 'AWS', output)
            click.echo(f"🌐 HTML报告已保存: {html_file}")
        
        click.echo("✅ 分析完成!")
        
    except ValueError as e:
        click.echo(f"❌ 日期格式错误: {e}", err=True)
        sys.exit(1)
    except AWSAnalyzerError as e:
        click.echo(f"❌ 分析失败: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ 未知错误: {e}", err=True)
        if ctx.obj['verbose']:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command('multi-cloud')
@click.option('--start', help='开始日期 (YYYY-MM-DD)')
@click.option('--end', help='结束日期 (YYYY-MM-DD)')
@click.option('--output', '-o', default='.', help='输出目录')
@click.option('--format', 'output_format', 
              type=click.Choice(['txt', 'html', 'all']), 
              default='all', help='输出格式')
@click.pass_context
def multi_cloud(ctx: click.Context, start: Optional[str], end: Optional[str], 
                output: str, output_format: str) -> None:
    """多云费用分析"""
    config = ctx.obj['config']
    
    try:
        # 解析日期（如果提供）
        start_date = None
        end_date = None
        
        if start:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
        if end:
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
        
        analyzer = MultiCloudAnalyzer(config=config)
        
        click.echo("🌐 开始多云费用分析...")
        results = analyzer.analyze_all(start_date=start_date, end_date=end_date)
        
        # 生成对比报告
        comparison_report = analyzer.generate_comparison_report(results)
        
        # 生成报告
        generator = ReportGenerator(config)
        generator.generate_multi_cloud_console_report(comparison_report)
        
        if output_format in ['txt', 'all']:
            txt_file = generator.generate_multi_cloud_text_report(comparison_report, output)
            click.echo(f"📄 多云文本报告已保存: {txt_file}")
            
        if output_format in ['html', 'all']:
            html_file = generator.generate_multi_cloud_html_report(comparison_report, output)
            click.echo(f"🌐 多云HTML报告已保存: {html_file}")
        
        click.echo("✅ 多云分析完成!")
        
    except ValueError as e:
        click.echo(f"❌ 日期格式错误: {e}", err=True)
        sys.exit(1)
    except AWSAnalyzerError as e:
        click.echo(f"❌ 分析失败: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ 未知错误: {e}", err=True)
        if ctx.obj['verbose']:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.pass_context
def config_check(ctx: click.Context) -> None:
    """检查所有云平台连接配置"""
    config = ctx.obj['config']
    
    try:
        analyzer = MultiCloudAnalyzer(config=config)
        
        click.echo("🔍 检查云平台连接状态...")
        results = analyzer.test_all_connections()
        
        for provider, result in results.items():
            provider_name = analyzer._format_provider_name(provider)
            if result['success']:
                click.echo(f"✅ {provider_name}连接: 成功", color='green')
                if 'info' in result:
                    click.echo(f"   {result['info']}", color='green')
            else:
                click.echo(f"❌ {provider_name}连接: 失败", color='red')
                click.echo(f"   错误: {result['error']}", color='red')
        
        successful = sum(1 for r in results.values() if r['success'])
        total = len(results)
        
        click.echo(f"\n📊 连接状态: {successful}/{total} 成功")
        
    except Exception as e:
        click.echo(f"❌ 配置检查失败: {e}", err=True)
        if ctx.obj['verbose']:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
def version() -> None:
    """显示版本信息"""
    click.echo("Cloud Cost Analyzer v2.0.0")
    click.echo("多云费用分析工具")
    click.echo("支持: AWS、阿里云、腾讯云、火山云")


if __name__ == '__main__':
    cli()