"""
进度显示模块
"""
from typing import Optional, Iterator, Any
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class ProgressManager:
    """进度管理器"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
    
    def __enter__(self):
        self.progress.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()
    
    def add_task(self, description: str, total: Optional[float] = None) -> TaskID:
        """添加任务"""
        return self.progress.add_task(description, total=total)
    
    def update(self, task_id: TaskID, advance: float = 1, description: Optional[str] = None):
        """更新任务进度"""
        self.progress.update(task_id, advance=advance, description=description)
    
    def set_description(self, task_id: TaskID, description: str):
        """设置任务描述"""
        self.progress.update(task_id, description=description)


class CloudAnalysisProgress:
    """云分析进度显示"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.progress_manager = ProgressManager(console)
    
    def show_analysis_progress(self, providers: list[str]) -> Iterator[dict]:
        """显示分析进度"""
        with self.progress_manager as progress:
            # 创建主任务
            main_task = progress.add_task("多云费用分析", total=len(providers) * 3)
            
            for i, provider in enumerate(providers):
                # 连接测试
                progress.update(
                    main_task, 
                    description=f"测试 {provider} 连接...",
                    advance=0
                )
                yield {"stage": "connection", "provider": provider}
                
                # 数据获取
                progress.update(
                    main_task,
                    description=f"获取 {provider} 费用数据...",
                    advance=1/3
                )
                yield {"stage": "data_fetch", "provider": provider}
                
                # 数据处理
                progress.update(
                    main_task,
                    description=f"处理 {provider} 数据...",
                    advance=1/3
                )
                yield {"stage": "data_process", "provider": provider}
                
                # 完成当前提供商
                progress.update(
                    main_task,
                    description=f"{provider} 分析完成",
                    advance=1/3
                )
            
            # 最终处理
            progress.update(
                main_task,
                description="生成分析报告...",
                advance=0
            )
            yield {"stage": "report_generation"}
            
            progress.update(
                main_task,
                description="分析完成！",
                advance=0
            )


def show_welcome_message(console: Console):
    """显示欢迎信息"""
    welcome_text = Text()
    welcome_text.append("🌐 Cloud Cost Analyzer", style="bold blue")
    welcome_text.append("\n多云费用分析工具", style="dim")
    welcome_text.append("\n\n支持平台: AWS, 阿里云, 腾讯云, 火山云", style="green")
    
    console.print(Panel.fit(welcome_text, border_style="blue"))


def show_analysis_summary(console: Console, results: dict):
    """显示分析摘要"""
    summary_text = Text()
    summary_text.append("📊 分析摘要", style="bold green")
    summary_text.append(f"\n\n总费用: {results.get('total_cost', 'N/A')}")
    summary_text.append(f"\n分析时间: {results.get('analysis_time', 'N/A')}")
    summary_text.append(f"\n数据点数: {results.get('data_points', 'N/A')}")
    
    console.print(Panel.fit(summary_text, border_style="green"))


def show_error_message(console: Console, error: Exception, context: str = ""):
    """显示错误信息"""
    error_text = Text()
    error_text.append("❌ 错误", style="bold red")
    if context:
        error_text.append(f"\n\n上下文: {context}", style="dim")
    error_text.append(f"\n\n错误信息: {str(error)}", style="red")
    
    console.print(Panel.fit(error_text, border_style="red"))
