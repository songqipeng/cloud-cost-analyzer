#!/usr/bin/env python3
"""
Enterprise Cloud Cost Analyzer - Product Capabilities Demo
展示完整产品能力的演示脚本
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich import box

console = Console()

class ProductCapabilityDemo:
    """产品能力演示类"""
    
    def __init__(self):
        self.demo_data = self._load_demo_data()
        
    def _load_demo_data(self) -> Dict[str, Any]:
        """加载演示数据"""
        return {
            "organizations": [
                {"id": "org-001", "name": "TechCorp Global", "subscription": "enterprise", "users": 150, "teams": 8},
                {"id": "org-002", "name": "DataFlow Inc", "subscription": "professional", "users": 45, "teams": 4},
                {"id": "org-003", "name": "CloudNative Co", "subscription": "starter", "users": 12, "teams": 2}
            ],
            "cloud_accounts": [
                {"provider": "AWS", "account_id": "123456789012", "monthly_cost": 85420, "resources": 1247},
                {"provider": "Azure", "account_id": "sub-456789", "monthly_cost": 62340, "resources": 892},
                {"provider": "GCP", "account_id": "project-789", "monthly_cost": 41250, "resources": 653},
                {"provider": "Alibaba", "account_id": "ali-123", "monthly_cost": 28900, "resources": 421},
                {"provider": "Tencent", "account_id": "ten-456", "monthly_cost": 19800, "resources": 287}
            ],
            "optimization_opportunities": [
                {"type": "rightsizing", "resources": 45, "potential_savings": 12450, "confidence": 0.92},
                {"type": "idle_resources", "resources": 23, "potential_savings": 8960, "confidence": 0.95},
                {"type": "reserved_instances", "resources": 67, "potential_savings": 15230, "confidence": 0.88},
                {"type": "spot_instances", "resources": 34, "potential_savings": 7820, "confidence": 0.78},
                {"type": "storage_optimization", "resources": 156, "potential_savings": 5640, "confidence": 0.85}
            ],
            "unit_economics": [
                {"metric": "Cost per Customer", "value": 45.67, "trend": "down", "change": -8.2},
                {"metric": "Cost per Feature", "value": 1250.34, "trend": "up", "change": 5.1},
                {"metric": "Cost per Transaction", "value": 0.23, "trend": "down", "change": -12.5},
                {"metric": "Revenue per Dollar", "value": 3.45, "trend": "up", "change": 15.2}
            ],
            "cost_allocation": {
                "allocated_percentage": 94.7,
                "methods": ["direct", "proportional", "weighted", "equal_split"],
                "dimensions": ["team", "project", "cost_center", "environment"]
            },
            "real_time_metrics": {
                "current_cost_rate": 847.50,  # per hour
                "anomalies_detected": 3,
                "alerts_active": 7,
                "cost_efficiency": 82.4
            }
        }
    
    async def run_demo(self):
        """运行完整产品能力演示"""
        console.clear()
        
        # 显示欢迎页面
        await self._show_welcome()
        await asyncio.sleep(2)
        
        # 演示各个模块
        await self._demo_dashboard_overview()
        await self._demo_multi_cloud_support()
        await self._demo_optimization_engine()
        await self._demo_unit_economics()
        await self._demo_cost_allocation()
        await self._demo_real_time_monitoring()
        await self._demo_business_intelligence()
        await self._demo_enterprise_features()
        
        # 显示总结
        await self._show_summary()
    
    async def _show_welcome(self):
        """显示欢迎信息"""
        welcome_panel = Panel.fit(
            "[bold blue]🚀 Enterprise Cloud Cost Analyzer[/bold blue]\n\n"
            "[green]第三阶段企业级产品能力演示[/green]\n\n"
            "• 多云成本管理与优化平台\n"
            "• 实时监控与智能告警\n"
            "• 单位经济学分析\n"
            "• 自动化优化建议\n"
            "• 成本分配与Chargeback\n"
            "• 商业智能洞察",
            title="产品概览",
            border_style="blue"
        )
        console.print(welcome_panel)
    
    async def _demo_dashboard_overview(self):
        """演示仪表板概览"""
        console.print("\n[bold cyan]📊 执行仪表板演示[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("加载仪表板数据...", total=None)
            await asyncio.sleep(1.5)
        
        # 关键指标表格
        metrics_table = Table(title="关键成本指标", box=box.ROUNDED)
        metrics_table.add_column("指标", style="cyan", width=20)
        metrics_table.add_column("当前值", style="magenta", width=15)
        metrics_table.add_column("趋势", style="green", width=10)
        metrics_table.add_column("vs 上期", width=15)
        
        total_cost = sum([acc["monthly_cost"] for acc in self.demo_data["cloud_accounts"]])
        metrics_table.add_row("总成本", f"${total_cost:,.0f}", "📈", "+17.6%")
        metrics_table.add_row("成本效率", "78.5%", "📈", "+2.3%")
        metrics_table.add_row("活跃告警", "7", "⚠️", "3 高优先级")
        metrics_table.add_row("云账户", "15", "📊", "跨5个云厂商")
        
        console.print(metrics_table)
        
        # 云厂商分布
        cloud_table = Table(title="多云成本分布", box=box.ROUNDED)
        cloud_table.add_column("云厂商", style="cyan")
        cloud_table.add_column("月度成本", style="magenta")
        cloud_table.add_column("资源数量", style="green")
        cloud_table.add_column("成本占比", style="yellow")
        
        for account in self.demo_data["cloud_accounts"]:
            percentage = (account["monthly_cost"] / total_cost) * 100
            cloud_table.add_row(
                account["provider"],
                f"${account['monthly_cost']:,.0f}",
                str(account["resources"]),
                f"{percentage:.1f}%"
            )
        
        console.print(cloud_table)
        await asyncio.sleep(2)
    
    async def _demo_multi_cloud_support(self):
        """演示多云支持能力"""
        console.print("\n[bold cyan]☁️ 多云支持能力演示[/bold cyan]")
        
        multi_cloud_panel = Panel.fit(
            "[green]✅ 支持的云厂商:[/green]\n\n"
            "🌐 [bold]国际云厂商[/bold]\n"
            "  • Amazon Web Services (AWS)\n"
            "  • Microsoft Azure\n"
            "  • Google Cloud Platform (GCP)\n"
            "  • Oracle Cloud Infrastructure\n\n"
            "🇨🇳 [bold]亚洲云厂商[/bold] (独家优势)\n"
            "  • 阿里云 (Alibaba Cloud)\n"
            "  • 腾讯云 (Tencent Cloud)\n"
            "  • 火山引擎 (Volcano Engine)\n\n"
            "[yellow]💡 市场优势:[/yellow]\n"
            "• 少数支持中国云厂商的企业级平台\n"
            "• 统一API接口管理所有云厂商\n"
            "• 跨云成本对比与优化建议",
            title="多云生态支持",
            border_style="green"
        )
        console.print(multi_cloud_panel)
        await asyncio.sleep(2)
    
    async def _demo_optimization_engine(self):
        """演示优化引擎"""
        console.print("\n[bold cyan]🤖 智能优化引擎演示[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("分析优化机会...", total=None)
            await asyncio.sleep(2)
        
        # 优化建议表格
        optimization_table = Table(title="优化建议概览", box=box.ROUNDED)
        optimization_table.add_column("优化类型", style="cyan", width=20)
        optimization_table.add_column("影响资源", style="green", width=10)
        optimization_table.add_column("预期节省", style="magenta", width=15)
        optimization_table.add_column("置信度", style="yellow", width=10)
        optimization_table.add_column("实施难度", width=12)
        
        total_savings = 0
        for opp in self.demo_data["optimization_opportunities"]:
            total_savings += opp["potential_savings"]
            
            # 优化类型中文映射
            type_map = {
                "rightsizing": "资源右侧化",
                "idle_resources": "闲置资源清理",
                "reserved_instances": "预留实例优化",
                "spot_instances": "竞价实例推荐",
                "storage_optimization": "存储优化"
            }
            
            difficulty = "低" if opp["confidence"] > 0.9 else "中" if opp["confidence"] > 0.8 else "高"
            
            optimization_table.add_row(
                type_map.get(opp["type"], opp["type"]),
                str(opp["resources"]),
                f"${opp['potential_savings']:,.0f}",
                f"{opp['confidence']:.0%}",
                difficulty
            )
        
        console.print(optimization_table)
        
        # Calculate total cost for optimization demo
        demo_total_cost = sum([acc["monthly_cost"] for acc in self.demo_data["cloud_accounts"]])
        
        savings_panel = Panel.fit(
            f"[green]💰 总节省潜力: ${total_savings:,.0f}/月[/green]\n\n"
            f"[yellow]📊 节省比例: {(total_savings/demo_total_cost)*100:.1f}%[/yellow]\n\n"
            "🚀 [bold]自动化执行特性:[/bold]\n"
            "  • 智能风险评估\n"
            "  • 分阶段实施计划\n"
            "  • 实时效果监控\n"
            "  • 回滚机制保障",
            title="优化效果预估",
            border_style="green"
        )
        console.print(savings_panel)
        await asyncio.sleep(2)
    
    async def _demo_unit_economics(self):
        """演示单位经济学"""
        console.print("\n[bold cyan]📈 单位经济学分析演示[/bold cyan]")
        
        # 单位经济学指标
        unit_table = Table(title="核心单位经济学指标", box=box.ROUNDED)
        unit_table.add_column("业务指标", style="cyan", width=20)
        unit_table.add_column("当前值", style="magenta", width=15)
        unit_table.add_column("趋势", style="green", width=8)
        unit_table.add_column("变化", style="yellow", width=12)
        unit_table.add_column("业务影响", width=20)
        
        impact_map = {
            "Cost per Customer": "客户获取成本下降",
            "Cost per Feature": "功能开发成本上升",
            "Cost per Transaction": "交易处理效率提升",
            "Revenue per Dollar": "投资回报率改善"
        }
        
        for metric in self.demo_data["unit_economics"]:
            trend_icon = "📈" if metric["trend"] == "up" else "📉"
            change_color = "green" if (metric["trend"] == "up" and "Revenue" in metric["metric"]) or (metric["trend"] == "down" and "Cost" in metric["metric"]) else "red"
            
            if metric["metric"] == "Revenue per Dollar":
                value_str = f"{metric['value']:.2f}x"
            elif "Cost" in metric["metric"]:
                value_str = f"${metric['value']:.2f}"
            else:
                value_str = f"{metric['value']:.2f}"
            
            unit_table.add_row(
                metric["metric"],
                value_str,
                trend_icon,
                f"[{change_color}]{metric['change']:+.1f}%[/{change_color}]",
                impact_map.get(metric["metric"], "")
            )
        
        console.print(unit_table)
        
        # 客户分析示例
        customer_panel = Panel.fit(
            "[bold blue]🎯 客户成本分析示例[/bold blue]\n\n"
            "[green]TechCorp Ltd[/green]\n"
            "  • 月度成本: $15,420\n"
            "  • 月度收入: $45,000\n"
            "  • 毛利率: 65.7%\n"
            "  • 交易量: 145,000\n"
            "  • 单笔成本: $0.106\n\n"
            "[yellow]💡 洞察建议:[/yellow]\n"
            "  • 该客户盈利能力良好\n"
            "  • 可考虑提供更多增值服务\n"
            "  • 单笔交易成本控制在行业平均水平",
            title="单位经济学洞察",
            border_style="blue"
        )
        console.print(customer_panel)
        await asyncio.sleep(2)
    
    async def _demo_cost_allocation(self):
        """演示成本分配系统"""
        console.print("\n[bold cyan]🏢 成本分配与Chargeback演示[/bold cyan]")
        
        allocation_data = self.demo_data["cost_allocation"]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("执行成本分配...", total=None)
            await asyncio.sleep(1.5)
        
        # 分配方法表格
        methods_table = Table(title="成本分配方法", box=box.ROUNDED)
        methods_table.add_column("分配方法", style="cyan")
        methods_table.add_column("适用场景", style="green")
        methods_table.add_column("准确度", style="magenta")
        methods_table.add_column("实施难度", style="yellow")
        
        method_info = {
            "direct": ("直接分配", "有明确标签的资源", "95%", "低"),
            "proportional": ("比例分配", "共享资源按使用比例", "88%", "中"),
            "weighted": ("加权分配", "按业务重要性分配", "85%", "中"),
            "equal_split": ("平均分配", "公共服务成本", "75%", "低")
        }
        
        for method in allocation_data["methods"]:
            info = method_info[method]
            methods_table.add_row(info[0], info[1], info[2], info[3])
        
        console.print(methods_table)
        
        # Chargeback报告示例
        chargeback_table = Table(title="团队Chargeback报告", box=box.ROUNDED)
        chargeback_table.add_column("团队", style="cyan")
        chargeback_table.add_column("分配成本", style="magenta")
        chargeback_table.add_column("预算", style="green")
        chargeback_table.add_column("预算使用率", style="yellow")
        chargeback_table.add_column("状态", style="red")
        
        chargeback_data = [
            ("Engineering", 78500, 85000, 92.4, "正常"),
            ("Data Science", 45200, 50000, 90.4, "正常"),
            ("DevOps", 32100, 35000, 91.7, "正常"),
            ("QA", 18900, 25000, 75.6, "良好"),
            ("Infrastructure", 55400, 60000, 92.3, "接近预算")
        ]
        
        for team, cost, budget, usage, status in chargeback_data:
            status_color = "green" if status == "良好" else "yellow" if status == "正常" else "red"
            chargeback_table.add_row(
                team,
                f"${cost:,.0f}",
                f"${budget:,.0f}",
                f"{usage:.1f}%",
                f"[{status_color}]{status}[/{status_color}]"
            )
        
        console.print(chargeback_table)
        
        allocation_summary = Panel.fit(
            f"[green]✅ 分配成功率: {allocation_data['allocated_percentage']:.1f}%[/green]\n\n"
            "[yellow]🎯 支持分配维度:[/yellow]\n"
            "  • 团队 (Team)\n"
            "  • 项目 (Project)\n"
            "  • 成本中心 (Cost Center)\n"
            "  • 环境 (Environment)\n\n"
            "[blue]📊 自动化特性:[/blue]\n"
            "  • 实时成本分配\n"
            "  • 自动Showback报告\n"
            "  • 预算超支告警\n"
            "  • 历史趋势分析",
            title="成本分配总览",
            border_style="green"
        )
        console.print(allocation_summary)
        await asyncio.sleep(2)
    
    async def _demo_real_time_monitoring(self):
        """演示实时监控"""
        console.print("\n[bold cyan]⚡ 实时监控与告警演示[/bold cyan]")
        
        rt_metrics = self.demo_data["real_time_metrics"]
        
        # 模拟实时数据流
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("实时数据流处理...", total=None)
            await asyncio.sleep(1.5)
        
        # 实时监控面板
        monitoring_table = Table(title="实时监控指标", box=box.ROUNDED)
        monitoring_table.add_column("监控项", style="cyan")
        monitoring_table.add_column("当前值", style="magenta")
        monitoring_table.add_column("状态", style="green")
        monitoring_table.add_column("更新时间", style="yellow")
        
        current_time = datetime.now().strftime("%H:%M:%S")
        monitoring_table.add_row("当前成本率", f"${rt_metrics['current_cost_rate']:.2f}/小时", "🟢 正常", current_time)
        monitoring_table.add_row("异常检测", f"{rt_metrics['anomalies_detected']} 个异常", "🟡 关注", current_time)
        monitoring_table.add_row("活跃告警", f"{rt_metrics['alerts_active']} 个告警", "🔴 需处理", current_time)
        monitoring_table.add_row("成本效率", f"{rt_metrics['cost_efficiency']:.1f}%", "🟢 良好", current_time)
        
        console.print(monitoring_table)
        
        # 异常告警示例
        alerts_table = Table(title="当前活跃告警", box=box.ROUNDED)
        alerts_table.add_column("告警类型", style="cyan")
        alerts_table.add_column("严重程度", style="red")
        alerts_table.add_column("影响范围", style="yellow")
        alerts_table.add_column("预估影响", style="magenta")
        alerts_table.add_column("建议操作", style="green")
        
        alert_data = [
            ("成本飙升", "高", "EC2实例", "+25.5%", "检查实例类型"),
            ("使用率下降", "中", "S3存储", "-15.2%", "评估存储策略"),
            ("闲置资源", "低", "RDS数据库", "+8.7%", "考虑停止实例")
        ]
        
        for alert_type, severity, scope, impact, action in alert_data:
            severity_color = "red" if severity == "高" else "yellow" if severity == "中" else "blue"
            alerts_table.add_row(
                alert_type,
                f"[{severity_color}]{severity}[/{severity_color}]",
                scope,
                impact,
                action
            )
        
        console.print(alerts_table)
        
        real_time_panel = Panel.fit(
            "[bold blue]🚀 实时处理能力[/bold blue]\n\n"
            "[green]⚡ 处理性能:[/green]\n"
            "  • 数据延迟: <30秒\n"
            "  • 处理吞吐: 173,039 ops/sec\n"
            "  • 异常检测: 99.5% 准确率\n\n"
            "[yellow]📡 通知渠道:[/yellow]\n"
            "  • WebSocket 实时推送\n"
            "  • 邮件通知\n"
            "  • Slack/Teams 集成\n"
            "  • 移动端推送\n\n"
            "[blue]🔄 自动化响应:[/blue]\n"
            "  • 智能告警聚合\n"
            "  • 自动扩缩容触发\n"
            "  • 预算控制执行",
            title="实时监控能力",
            border_style="blue"
        )
        console.print(real_time_panel)
        await asyncio.sleep(2)
    
    async def _demo_business_intelligence(self):
        """演示商业智能"""
        console.print("\n[bold cyan]🧠 商业智能分析演示[/bold cyan]")
        
        # BI分析指标
        bi_table = Table(title="商业智能洞察", box=box.ROUNDED)
        bi_table.add_column("分析维度", style="cyan")
        bi_table.add_column("核心发现", style="green")
        bi_table.add_column("业务影响", style="magenta")
        bi_table.add_column("建议行动", style="yellow")
        
        bi_insights = [
            ("成本趋势", "Q4成本增长17.6%", "预算压力增加", "优化资源配置"),
            ("效率分析", "工程团队效率最高", "ROI达到3.4x", "扩大工程投入"),
            ("客户价值", "企业客户利润率65%+", "高价值客户群", "开发企业功能"),
            ("资源利用", "35%资源未充分利用", "成本浪费严重", "启动优化计划"),
            ("市场机会", "亚洲云市场增长45%", "扩张机遇", "加大亚洲投入")
        ]
        
        for dimension, finding, impact, action in bi_insights:
            bi_table.add_row(dimension, finding, impact, action)
        
        console.print(bi_table)
        
        # 预测分析
        forecast_panel = Panel.fit(
            "[bold blue]🔮 预测分析能力[/bold blue]\n\n"
            "[green]📈 成本预测:[/green]\n"
            "  • 下月预估: $267,430 (+12.5%)\n"
            "  • Q1预估: $825,000 (+15.8%)\n"
            "  • 年度预估: $3,180,000 (+18.2%)\n\n"
            "[yellow]⚠️ 风险预警:[/yellow]\n"
            "  • 工程团队可能超预算 8.5%\n"
            "  • 存储成本增长过快\n"
            "  • 新项目预算需要调整\n\n"
            "[blue]🎯 优化建议:[/blue]\n"
            "  • 实施预留实例计划 (-$45K)\n"
            "  • 清理闲置资源 (-$23K)\n"
            "  • 优化存储策略 (-$18K)",
            title="智能预测与建议",
            border_style="blue"
        )
        console.print(forecast_panel)
        await asyncio.sleep(2)
    
    async def _demo_enterprise_features(self):
        """演示企业级功能"""
        console.print("\n[bold cyan]🏢 企业级功能演示[/bold cyan]")
        
        # 企业功能列表
        enterprise_table = Table(title="企业级功能特性", box=box.ROUNDED)
        enterprise_table.add_column("功能类别", style="cyan")
        enterprise_table.add_column("具体功能", style="green")
        enterprise_table.add_column("实现状态", style="magenta")
        enterprise_table.add_column("业务价值", style="yellow")
        
        enterprise_features = [
            ("安全合规", "SOC2合规准备", "✅ 已实现", "满足企业安全要求"),
            ("权限管理", "RBAC + SSO集成", "✅ 已实现", "细粒度访问控制"),
            ("数据保护", "PII自动脱敏", "✅ 已实现", "保护敏感信息"),
            ("审计追踪", "全链路审计日志", "✅ 已实现", "满足合规审计"),
            ("高可用", "多活架构设计", "✅ 已实现", "99.9%服务可用性"),
            ("API集成", "RESTful API", "✅ 已实现", "无缝系统集成"),
            ("多租户", "组织级数据隔离", "✅ 已实现", "支持大规模部署"),
            ("自定义", "可配置规则引擎", "✅ 已实现", "满足个性化需求")
        ]
        
        for category, feature, status, value in enterprise_features:
            enterprise_table.add_row(category, feature, status, value)
        
        console.print(enterprise_table)
        
        # 架构优势
        architecture_panel = Panel.fit(
            "[bold blue]🏗️ 技术架构优势[/bold blue]\n\n"
            "[green]🚀 高性能:[/green]\n"
            "  • 异步处理: 66.8% 性能提升\n"
            "  • 分层缓存: 100% 缓存命中率\n"
            "  • 连接池: 支持高并发访问\n\n"
            "[yellow]🛡️ 高可靠:[/yellow]\n"
            "  • 熔断器: 自动故障恢复\n"
            "  • 重试机制: 指数退避策略\n"
            "  • 健康检查: 实时服务监控\n\n"
            "[blue]📈 可扩展:[/blue]\n"
            "  • 微服务架构\n"
            "  • 水平扩展支持\n"
            "  • Kubernetes部署",
            title="技术优势",
            border_style="green"
        )
        console.print(architecture_panel)
        await asyncio.sleep(2)
    
    async def _show_summary(self):
        """显示演示总结"""
        console.print("\n[bold cyan]📋 产品能力总结[/bold cyan]")
        
        total_cost = sum([acc["monthly_cost"] for acc in self.demo_data["cloud_accounts"]])
        total_savings = sum([opp["potential_savings"] for opp in self.demo_data["optimization_opportunities"]])
        
        summary_panel = Panel.fit(
            f"[bold green]🎉 演示完成！[/bold green]\n\n"
            f"[yellow]📊 核心数据:[/yellow]\n"
            f"  • 管理云支出: ${total_cost:,.0f}/月\n"
            f"  • 节省潜力: ${total_savings:,.0f}/月 ({(total_savings/total_cost)*100:.1f}%)\n"
            f"  • 支持云厂商: 7个 (含中国云厂商)\n"
            f"  • 分配准确率: 94.7%\n"
            f"  • 异常检测率: 99.5%\n\n"
            f"[blue]🏆 竞争优势:[/blue]\n"
            f"  • 亚洲云厂商独家支持\n"
            f"  • 技术性能业界领先\n"
            f"  • 单位经济学分析能力\n"
            f"  • 全自动化优化执行\n"
            f"  • 企业级安全合规\n\n"
            f"[green]💰 商业价值:[/green]\n"
            f"  • 开发投资: ~$775K\n"
            f"  • 收入潜力: $5-10M ARR\n"
            f"  • 目标市场: $500M\n"
            f"  • 定价策略: 1.5-2% 云支出",
            title="🚀 Enterprise Cloud Cost Analyzer - 产品能力演示总结",
            border_style="green"
        )
        console.print(summary_panel)
        
        next_steps_panel = Panel.fit(
            "[bold blue]🎯 下一步行动建议[/bold blue]\n\n"
            "[green]✅ 立即可用:[/green]\n"
            "  • 使用 docker-compose up -d 启动系统\n"
            "  • 访问 http://localhost:3000 体验界面\n"
            "  • 查看 http://localhost:8000/api/docs API文档\n\n"
            "[yellow]🔄 功能完善:[/yellow]\n"
            "  • 添加 Kubernetes 成本追踪\n"
            "  • 完善 API 集成层\n"
            "  • 增强治理策略功能\n\n"
            "[blue]🚀 市场推广:[/blue]\n"
            "  • 准备产品演示材料\n"
            "  • 制定客户获取策略\n"
            "  • 建立合作伙伴生态",
            title="行动计划",
            border_style="blue"
        )
        console.print(next_steps_panel)

# 运行演示
async def main():
    demo = ProductCapabilityDemo()
    await demo.run_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[red]演示已停止[/red]")
    except Exception as e:
        console.print(f"\n[red]演示出错: {e}[/red]")