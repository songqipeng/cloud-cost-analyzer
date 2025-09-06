#!/usr/bin/env python3
"""
AWS费用分析器产品能力全览和使用指南
"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.tree import Tree
from rich.text import Text

console = Console()

def show_product_capabilities():
    """展示产品完整能力"""
    
    # 产品标题
    title = Panel.fit(
        "[bold blue]🌐 Cloud Cost Analyzer - 多云费用分析器[/bold blue]\n"
        "[cyan]专业的云服务费用分析、优化和管理平台[/cyan]",
        border_style="blue"
    )
    console.print(title)
    
    # 核心能力概览
    console.print("\n[bold green]🎯 核心能力概览[/bold green]")
    
    capabilities = [
        Panel(
            "[bold]🌍 多云平台支持[/bold]\n"
            "• AWS Amazon Web Services\n"
            "• 阿里云 Alibaba Cloud\n"
            "• 腾讯云 Tencent Cloud\n"
            "• 火山云 Volcengine\n"
            "• 统一分析和对比",
            title="多云覆盖",
            border_style="cyan",
            width=25
        ),
        Panel(
            "[bold]📊 深度分析能力[/bold]\n"
            "• 服务级费用分析\n"
            "• 区域级费用分布\n"
            "• 资源级费用下钻\n"
            "• 时间序列趋势\n"
            "• 异常检测监控",
            title="分析深度",
            border_style="green",
            width=25
        ),
        Panel(
            "[bold]🎨 可视化报告[/bold]\n"
            "• 交互式图表\n"
            "• 现代化仪表板\n"
            "• HTML/TXT报告\n"
            "• 移动端适配\n"
            "• 一键导出分享",
            title="可视化",
            border_style="magenta",
            width=25
        ),
        Panel(
            "[bold]💡 智能优化[/bold]\n"
            "• AI成本优化建议\n"
            "• 预留实例推荐\n"
            "• 资源规格优化\n"
            "• 存储类别建议\n"
            "• ROI计算分析",
            title="智能建议",
            border_style="yellow",
            width=25
        )
    ]
    
    console.print(Columns(capabilities, equal=True, expand=True))

def show_detailed_features():
    """展示详细功能特性"""
    
    console.print("\n[bold blue]📋 详细功能特性[/bold blue]")
    
    # 创建功能树
    feature_tree = Tree("[bold]🌟 功能模块", style="bold blue")
    
    # 多云分析
    multicloud = feature_tree.add("[bold cyan]🌍 多云费用分析")
    multicloud.add("✅ AWS费用获取和解析")
    multicloud.add("✅ 阿里云计费数据集成") 
    multicloud.add("✅ 腾讯云费用统计")
    multicloud.add("✅ 火山云成本分析")
    multicloud.add("✅ 跨平台费用对比")
    multicloud.add("✅ 汇率转换支持")
    
    # 深度分析
    analysis = feature_tree.add("[bold green]🔍 深度分析引擎")
    analysis.add("📊 按服务类型分析 (EC2/RDS/S3等)")
    analysis.add("🌏 按地理区域分析")
    analysis.add("🔧 按资源实例分析 (实例ID级别)")
    analysis.add("📅 按时间维度分析 (日/月/年)")
    analysis.add("🏷️ 按标签维度分析")
    analysis.add("⚠️ 费用异常自动检测")
    analysis.add("📈 费用趋势预测分析")
    
    # 可视化
    viz = feature_tree.add("[bold magenta]🎨 可视化展示")
    viz.add("📊 交互式Plotly图表")
    viz.add("📈 费用趋势动态折线图")
    viz.add("🥧 服务分布交互式饼图")
    viz.add("📊 区域费用彩色柱状图") 
    viz.add("🔥 资源费用热力图")
    viz.add("⚡ 多指标综合仪表板")
    viz.add("📱 响应式移动端适配")
    
    # 智能优化
    optimize = feature_tree.add("[bold yellow]💡 智能优化建议")
    optimize.add("🤖 AI驱动的成本优化算法")
    optimize.add("💰 预留实例购买建议")
    optimize.add("⚡ Spot实例使用建议")
    optimize.add("📏 实例规格右调建议")
    optimize.add("💾 存储类别优化建议")
    optimize.add("🔄 负载均衡器整合建议")
    optimize.add("🎯 优先级行动计划")
    
    # 通知和自动化
    notify = feature_tree.add("[bold red]🔔 通知和自动化")
    notify.add("📧 邮件报告自动发送")
    notify.add("📱 飞书机器人消息推送")
    notify.add("⏰ 定时分析任务")
    notify.add("🚨 费用告警通知")
    notify.add("📊 定期报告生成")
    
    console.print(feature_tree)

def show_usage_guide():
    """展示使用指南"""
    
    console.print("\n[bold green]🚀 使用指南[/bold green]")
    
    # 基本命令
    basic_table = Table(
        title="基本命令",
        show_header=True,
        header_style="bold magenta",
        width=120
    )
    basic_table.add_column("命令", justify="left", style="cyan", width=25)
    basic_table.add_column("功能描述", justify="left", style="white", width=45)
    basic_table.add_column("使用示例", justify="left", style="green", width=50)
    
    basic_table.add_row(
        "help",
        "显示帮助信息和使用说明",
        "./cloud_cost_analyzer.py help"
    )
    
    basic_table.add_row(
        "config", 
        "检查所有云平台的连接状态和配置",
        "./cloud_cost_analyzer.py config"
    )
    
    basic_table.add_row(
        "quick",
        "快速分析AWS过去1年的费用数据",
        "./cloud_cost_analyzer.py quick"
    )
    
    basic_table.add_row(
        "custom",
        "自定义时间范围的AWS费用分析",
        "./cloud_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31"
    )
    
    basic_table.add_row(
        "multi-cloud",
        "多云平台费用分析和对比",
        "./cloud_cost_analyzer.py multi-cloud"
    )
    
    console.print(basic_table)
    
    # 高级选项
    console.print("\n[bold blue]⚙️ 高级选项[/bold blue]")
    
    options_table = Table(
        show_header=True,
        header_style="bold blue",
        width=100
    )
    options_table.add_column("选项", justify="left", style="yellow", width=20)
    options_table.add_column("说明", justify="left", style="white", width=40)
    options_table.add_column("示例", justify="left", style="cyan", width=40)
    
    options_table.add_row(
        "--start DATE",
        "指定分析开始日期",
        "--start 2024-01-01"
    )
    
    options_table.add_row(
        "--end DATE",
        "指定分析结束日期",
        "--end 2024-12-31"
    )
    
    options_table.add_row(
        "--output DIR",
        "指定报告输出目录",
        "--output ./reports"
    )
    
    options_table.add_row(
        "--format FMT",
        "指定输出格式 (txt/html/all)",
        "--format html"
    )
    
    console.print(options_table)

def show_setup_guide():
    """展示配置指南"""
    
    console.print("\n[bold red]🔧 配置指南[/bold red]")
    
    setup_steps = Panel(
        """[bold cyan]1. 环境准备[/bold cyan]
```bash
# 克隆项目
git clone https://github.com/songqipeng/cloud-cost-analyzer.git
cd cloud-cost-analyzer

# 安装Python依赖
pip3 install -r requirements.txt
```

[bold cyan]2. AWS配置 (必需)[/bold cyan]
```bash
# 方式1: 环境变量 (推荐)
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."

# 方式2: AWS CLI配置
aws configure
```

[bold cyan]3. 多云配置 (可选)[/bold cyan]
```bash
# 阿里云
export ALIBABA_CLOUD_ACCESS_KEY_ID="LTAI..."
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."

# 腾讯云
export TENCENTCLOUD_SECRET_ID="AKIDxxx..."
export TENCENTCLOUD_SECRET_KEY="..."

# 火山云
export VOLCENGINE_ACCESS_KEY_ID="AKLT..."
export VOLCENGINE_SECRET_ACCESS_KEY="..."
```

[bold cyan]4. 通知配置 (可选)[/bold cyan]
编辑 config.json 文件配置邮件和飞书通知

[bold cyan]5. 测试运行[/bold cyan]
```bash
# 检查配置
./cloud_cost_analyzer.py config

# 运行分析
./cloud_cost_analyzer.py quick
```""",
        title="🛠️ 快速开始",
        border_style="green",
        width=80
    )
    
    console.print(setup_steps)

def show_use_cases():
    """展示使用场景"""
    
    console.print("\n[bold purple]🎯 典型使用场景[/bold purple]")
    
    scenarios = [
        Panel(
            "[bold]💼 企业成本管理[/bold]\n"
            "• 多云费用统一分析\n"
            "• 部门成本分摊\n"
            "• 预算控制监控\n"
            "• 成本趋势预测\n"
            "• 高管报告生成",
            title="企业级应用",
            border_style="blue",
            width=30
        ),
        Panel(
            "[bold]🔍 成本优化专家[/bold]\n"
            "• 资源使用率分析\n"
            "• 预留实例规划\n"
            "• 存储优化建议\n"
            "• 架构成本评估\n"
            "• ROI效果跟踪",
            title="专业优化",
            border_style="green", 
            width=30
        ),
        Panel(
            "[bold]🚨 监控告警[/bold]\n"
            "• 费用异常检测\n"
            "• 预算超支预警\n"
            "• 定时报告推送\n"
            "• 自动化运维\n"
            "• 团队协作通知",
            title="运维监控",
            border_style="red",
            width=30
        )
    ]
    
    console.print(Columns(scenarios, equal=True, expand=True))
    
    # 具体示例
    console.print("\n[bold yellow]💡 实际使用示例[/bold yellow]")
    
    examples = Panel(
        """[bold cyan]场景1: 日常成本监控[/bold cyan]
```bash
# 每日快速检查
./cloud_cost_analyzer.py quick --format html
# 查看生成的HTML报告，了解费用趋势和异常
```

[bold cyan]场景2: 月度成本分析[/bold cyan]
```bash
# 自定义月度分析
./cloud_cost_analyzer.py custom --start 2024-11-01 --end 2024-11-30 --output ./monthly
# 生成详细的月度报告，包含优化建议
```

[bold cyan]场景3: 多云对比分析[/bold cyan]
```bash
# 跨平台费用对比
./cloud_cost_analyzer.py multi-cloud --format all
# 对比不同云平台的费用效率
```

[bold cyan]场景4: 成本优化项目[/bold cyan]
```bash
# 运行演示版查看完整功能
python3 demo_enhanced_analyzer.py
# 获取AI优化建议和具体行动计划
```

[bold cyan]场景5: 自动化运维[/bold cyan]
```bash
# 设置定时任务
crontab -e
# 添加: 0 8 * * * cd /path/to/analyzer && python3 cloud_cost_analyzer.py multi-cloud
```""",
        title="🚀 实践示例",
        border_style="yellow"
    )
    
    console.print(examples)

def show_output_samples():
    """展示输出示例"""
    
    console.print("\n[bold green]📊 输出示例[/bold green]")
    
    # 终端输出示例
    terminal_sample = Panel(
        """[bold cyan]终端输出 (Rich美化)[/bold cyan]
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 费用类型                        ┃                   金额 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 总费用                          │             $122618.13 │
│ 平均每日费用                    │               $1347.45 │
│ 最高单日费用                    │               $3179.83 │
│ 最低单日费用                    │                $481.22 │
└─────────────────────────────────┴────────────────────────┘

🔥 资源费用分析:
📊 检测到 5 个费用异常
💰 总潜在节省: $46,289.60""",
        title="🖥️ 命令行界面",
        border_style="cyan"
    )
    
    # HTML报告示例
    html_sample = Panel(
        """[bold magenta]HTML报告特性[/bold magenta]
🎨 现代化设计界面
📊 交互式Plotly图表
📱 移动端响应式布局
🔍 数据筛选和排序
💡 智能优化建议面板
⚠️ 异常检测可视化
📈 费用趋势动态展示
🎯 一键分享和导出""",
        title="🌐 HTML报告",
        border_style="magenta"
    )
    
    console.print(Columns([terminal_sample, html_sample], equal=True))

def main():
    """主函数"""
    show_product_capabilities()
    show_detailed_features()
    show_usage_guide()
    show_setup_guide()
    show_use_cases()
    show_output_samples()
    
    # 总结
    summary = Panel.fit(
        "[bold blue]🎉 Cloud Cost Analyzer 让云成本管理变得简单高效！[/bold blue]\n\n"
        "[white]✅ 支持4大云平台统一分析[/white]\n"
        "[white]✅ 资源级深度费用下钻[/white]\n" 
        "[white]✅ AI驱动的智能优化建议[/white]\n"
        "[white]✅ 专业的可视化报告[/white]\n"
        "[white]✅ 自动化监控和通知[/white]\n\n"
        "[cyan]立即开始: python3 demo_enhanced_analyzer.py[/cyan]",
        border_style="green"
    )
    console.print(f"\n{summary}")

if __name__ == "__main__":
    main()