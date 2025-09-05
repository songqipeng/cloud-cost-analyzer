"""
文本报告生成模块
"""
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from ..utils.config import Config


class TextReportGenerator:
    """文本报告生成器"""
    
    def __init__(self):
        """初始化文本报告生成器"""
        pass
    
    def generate_cost_report(
        self,
        df: pd.DataFrame,
        output_file: str,
        service_costs: Optional[pd.DataFrame] = None,
        region_costs: Optional[pd.DataFrame] = None
    ) -> bool:
        """
        生成费用报告
        
        Args:
            df: 费用数据
            output_file: 输出文件路径
            service_costs: 服务费用统计
            region_costs: 区域费用统计
            
        Returns:
            生成是否成功
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入报告头部
                f.write("=" * 80 + "\n")
                f.write("AWS费用分析报告\n")
                f.write("=" * 80 + "\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"数据时间范围: {df['Date'].min().strftime('%Y-%m-%d')} 到 {df['Date'].max().strftime('%Y-%m-%d')}\n")
                f.write("=" * 80 + "\n\n")
                
                # 写入费用摘要
                self._write_cost_summary(f, df)
                
                # 写入服务分析
                if service_costs is not None and not service_costs.empty:
                    self._write_service_analysis(f, service_costs)
                
                # 写入区域分析
                if region_costs is not None and not region_costs.empty:
                    self._write_region_analysis(f, region_costs)
                
                # 写入详细数据
                self._write_detailed_data(f, df)
                
                # 写入报告尾部
                f.write("\n" + "=" * 80 + "\n")
                f.write("报告结束\n")
                f.write("=" * 80 + "\n")
            
            return True
            
        except Exception as e:
            print(f"❌ 文本报告生成失败: {e}")
            return False
    
    def _write_cost_summary(self, file, df: pd.DataFrame) -> None:
        """写入费用摘要"""
        if df.empty:
            file.write("费用摘要: 无数据\n\n")
            return
        
        # 计算费用摘要
        total_cost = df['Cost'].sum()
        daily_costs = df.groupby('Date')['Cost'].sum()
        avg_daily_cost = daily_costs.mean()
        max_daily_cost = daily_costs.max()
        min_daily_cost = daily_costs.min()
        
        file.write("费用摘要:\n")
        file.write("-" * 40 + "\n")
        file.write(f"总费用: ${total_cost:.2f}\n")
        file.write(f"平均每日费用: ${avg_daily_cost:.2f}\n")
        file.write(f"最高单日费用: ${max_daily_cost:.2f}\n")
        file.write(f"最低单日费用: ${min_daily_cost:.2f}\n")
        file.write(f"数据记录数: {len(df)}\n")
        file.write(f"时间跨度: {(df['Date'].max() - df['Date'].min()).days + 1} 天\n\n")
    
    def _write_service_analysis(self, file, service_costs: pd.DataFrame) -> None:
        """写入服务分析"""
        file.write("按服务分析:\n")
        file.write("-" * 40 + "\n")
        
        # 写入表头
        file.write(f"{'服务名称':<40} {'总费用':<12} {'平均费用':<12} {'记录数':<8}\n")
        file.write("-" * 80 + "\n")
        
        # 写入数据
        for service, row in service_costs.iterrows():
            service_name = service[:37] + "..." if len(service) > 40 else service
            file.write(f"{service_name:<40} ${row['总费用']:<11.2f} ${row['平均费用']:<11.2f} {row['记录数']:<8}\n")
        
        file.write("\n")
    
    def _write_region_analysis(self, file, region_costs: pd.DataFrame) -> None:
        """写入区域分析"""
        file.write("按区域分析:\n")
        file.write("-" * 40 + "\n")
        
        # 写入表头
        file.write(f"{'区域名称':<20} {'总费用':<12} {'平均费用':<12} {'记录数':<8}\n")
        file.write("-" * 60 + "\n")
        
        # 写入数据
        for region, row in region_costs.iterrows():
            file.write(f"{region:<20} ${row['总费用']:<11.2f} ${row['平均费用']:<11.2f} {row['记录数']:<8}\n")
        
        file.write("\n")
    
    def _write_detailed_data(self, file, df: pd.DataFrame) -> None:
        """写入详细数据"""
        file.write("详细费用数据:\n")
        file.write("-" * 40 + "\n")
        
        # 写入表头
        file.write(f"{'日期':<12} {'服务':<30} {'区域':<15} {'费用':<12}\n")
        file.write("-" * 80 + "\n")
        
        # 按日期排序
        df_sorted = df.sort_values(['Date', 'Cost'], ascending=[True, False])
        
        # 写入数据
        for _, row in df_sorted.iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d')
            service = row['Service'][:27] + "..." if len(row['Service']) > 30 else row['Service']
            region = row['Region'][:12] + "..." if len(row['Region']) > 15 else row['Region']
            cost = row['Cost']
            
            file.write(f"{date_str:<12} {service:<30} {region:<15} ${cost:<11.2f}\n")
        
        file.write("\n")
    
    def generate_summary_report(
        self,
        cost_summary: Dict[str, float],
        service_costs: Optional[pd.DataFrame] = None,
        region_costs: Optional[pd.DataFrame] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        生成摘要报告
        
        Args:
            cost_summary: 费用摘要
            service_costs: 服务费用统计
            region_costs: 区域费用统计
            output_file: 输出文件路径
            
        Returns:
            报告内容字符串
        """
        report_lines = []
        
        # 报告头部
        report_lines.append("=" * 60)
        report_lines.append("AWS费用分析摘要报告")
        report_lines.append("=" * 60)
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 费用摘要
        report_lines.append("💰 费用摘要:")
        report_lines.append("-" * 30)
        report_lines.append(f"总费用: ${cost_summary['total_cost']:.2f}")
        report_lines.append(f"平均每日费用: ${cost_summary['avg_daily_cost']:.2f}")
        report_lines.append(f"最高单日费用: ${cost_summary['max_daily_cost']:.2f}")
        report_lines.append(f"最低单日费用: ${cost_summary['min_daily_cost']:.2f}")
        report_lines.append("")
        
        # 服务分析
        if service_costs is not None and not service_costs.empty:
            report_lines.append("🔧 按服务分析 (前5名):")
            report_lines.append("-" * 30)
            for service, row in service_costs.head(5).iterrows():
                report_lines.append(f"• {service}: ${row['总费用']:.2f}")
            report_lines.append("")
        
        # 区域分析
        if region_costs is not None and not region_costs.empty:
            report_lines.append("🌍 按区域分析 (前5名):")
            report_lines.append("-" * 30)
            for region, row in region_costs.head(5).iterrows():
                report_lines.append(f"• {region}: ${row['总费用']:.2f}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        report_content = "\n".join(report_lines)
        
        # 如果指定了输出文件，则写入文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            except Exception as e:
                print(f"❌ 摘要报告保存失败: {e}")
        
        return report_content
