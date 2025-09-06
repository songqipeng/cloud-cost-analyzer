"""
HTML报告生成模块
"""
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from ..utils.config import Config
from .chart_generator import InteractiveChartGenerator


class HTMLReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self):
        """初始化HTML报告生成器"""
        self.chart_generator = InteractiveChartGenerator()
    
    def generate_cost_report(
        self,
        df: pd.DataFrame,
        output_file: str,
        service_costs: Optional[pd.DataFrame] = None,
        region_costs: Optional[pd.DataFrame] = None,
        resource_costs: Optional[pd.DataFrame] = None,
        anomalies: Optional[list] = None
    ) -> bool:
        """
        生成HTML费用报告
        
        Args:
            df: 费用数据
            output_file: 输出文件路径
            service_costs: 服务费用统计
            region_costs: 区域费用统计
            resource_costs: 资源费用统计
            anomalies: 异常数据列表
            
        Returns:
            生成是否成功
        """
        try:
            html_content = self._generate_html_content(df, service_costs, region_costs, resource_costs, anomalies)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            print(f"❌ HTML报告生成失败: {e}")
            return False
    
    def _generate_html_content(
        self,
        df: pd.DataFrame,
        service_costs: Optional[pd.DataFrame] = None,
        region_costs: Optional[pd.DataFrame] = None,
        resource_costs: Optional[pd.DataFrame] = None,
        anomalies: Optional[list] = None
    ) -> str:
        """生成HTML内容"""
        
        # 计算费用摘要
        cost_summary = self._calculate_cost_summary(df)
        
        # 生成图表
        trend_chart = self.chart_generator.generate_cost_trend_chart(df)
        service_pie_chart = self.chart_generator.generate_service_cost_pie_chart(service_costs) if service_costs is not None else ""
        region_bar_chart = self.chart_generator.generate_region_cost_bar_chart(region_costs) if region_costs is not None else ""
        resource_heatmap = self.chart_generator.generate_resource_cost_heatmap(resource_costs) if resource_costs is not None else ""
        anomaly_chart = self.chart_generator.generate_cost_anomaly_chart(df, anomalies) if anomalies else ""
        dashboard = self.chart_generator.generate_multi_metric_dashboard(df, service_costs, region_costs, resource_costs)
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 AWS费用分析报告 - 交互式仪表板</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        {self._get_modern_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-content">
                <h1>📊 AWS费用分析报告</h1>
                <div class="header-subtitle">智能费用分析 · 交互式可视化</div>
            </div>
            <div class="meta-info">
                <div class="meta-card">
                    <div class="meta-label">生成时间</div>
                    <div class="meta-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                <div class="meta-card">
                    <div class="meta-label">数据时间范围</div>
                    <div class="meta-value">{df['Date'].min().strftime('%Y-%m-%d')} 到 {df['Date'].max().strftime('%Y-%m-%d')}</div>
                </div>
                <div class="meta-card">
                    <div class="meta-label">数据记录数</div>
                    <div class="meta-value">{len(df):,} 条</div>
                </div>
                <div class="meta-card">
                    <div class="meta-label">总费用</div>
                    <div class="meta-value">${df['Cost'].sum():.2f}</div>
                </div>
            </div>
        </header>
        
        <main class="main-content">
            <!-- 仪表板总览 -->
            <section class="dashboard-section">
                <div class="section-header">
                    <h2>💼 费用仪表板</h2>
                    <p>多维度费用分析总览</p>
                </div>
                <div class="chart-container">
                    {dashboard}
                </div>
            </section>
            
            <!-- 费用趋势分析 -->
            <section class="chart-section">
                <div class="section-header">
                    <h2>📈 费用趋势分析</h2>
                    <p>时间序列费用变化趋势</p>
                </div>
                <div class="chart-container">
                    {trend_chart}
                </div>
            </section>
            
            <!-- 服务分析 -->
            {f'''
            <section class="chart-section">
                <div class="section-header">
                    <h2>🔧 服务费用分析</h2>
                    <p>各AWS服务的费用分布情况</p>
                </div>
                <div class="chart-container">
                    {service_pie_chart}
                </div>
                {self._generate_service_analysis_section(service_costs)}
            </section>
            ''' if service_costs is not None and not service_costs.empty else ''}
            
            <!-- 区域分析 -->
            {f'''
            <section class="chart-section">
                <div class="section-header">
                    <h2>🌍 区域费用分析</h2>
                    <p>各AWS区域的费用分布情况</p>
                </div>
                <div class="chart-container">
                    {region_bar_chart}
                </div>
                {self._generate_region_analysis_section(region_costs)}
            </section>
            ''' if region_costs is not None and not region_costs.empty else ''}
            
            <!-- 资源分析 -->
            {f'''
            <section class="chart-section">
                <div class="section-header">
                    <h2>🔥 资源费用热力图</h2>
                    <p>各资源的费用分布热力图</p>
                </div>
                <div class="chart-container">
                    {resource_heatmap}
                </div>
                {self._generate_resource_analysis_section(resource_costs)}
            </section>
            ''' if resource_costs is not None and not resource_costs.empty else ''}
            
            <!-- 异常检测 -->
            {f'''
            <section class="chart-section">
                <div class="section-header">
                    <h2>⚠️ 费用异常检测</h2>
                    <p>识别费用异常波动和潜在问题</p>
                </div>
                <div class="chart-container">
                    {anomaly_chart}
                </div>
                {self._generate_anomaly_analysis_section(anomalies)}
            </section>
            ''' if anomalies else ''}
            
            <!-- 费用摘要 -->
            <section class="summary-section">
                <div class="section-header">
                    <h2>📋 费用摘要</h2>
                    <p>关键费用指标总结</p>
                </div>
                {self._generate_cost_summary_section(cost_summary)}
            </section>
            
            <!-- 详细数据 -->
            <section class="data-section">
                <div class="section-header">
                    <h2>📄 详细数据</h2>
                    <p>完整的费用明细数据</p>
                </div>
                {self._generate_detailed_data_section(df)}
            </section>
        </main>
        
        <footer class="footer">
            <div class="footer-content">
                <p>🚀 此报告由AWS费用分析器自动生成</p>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据来源: AWS Cost Explorer API</p>
            </div>
        </footer>
    </div>
    
    {self.chart_generator.get_chart_scripts()}
    <script>
        {self._get_modern_javascript()}
    </script>
</body>
</html>
        """
        
        return html
    
    def _generate_resource_analysis_section(self, resource_costs: Optional[pd.DataFrame]) -> str:
        """生成资源分析部分"""
        if resource_costs is None or resource_costs.empty:
            return '<div class="no-data">暂无资源费用数据</div>'
        
        html = '<div class="analysis-section">'
        html += '<h3>💎 Top资源费用排行</h3>'
        html += '<div class="table-container">'
        html += '<table class="data-table">'
        html += '<thead><tr><th>服务</th><th>资源ID</th><th>区域</th><th>总费用</th><th>平均费用</th><th>记录数</th></tr></thead>'
        html += '<tbody>'
        
        for _, row in resource_costs.head(15).iterrows():
            html += f'''
            <tr>
                <td>{row['Service']}</td>
                <td><code>{row['ResourceId']}</code></td>
                <td>{row['区域']}</td>
                <td class="cost-value">${row['总费用']:.2f}</td>
                <td>${row['平均费用']:.2f}</td>
                <td>{row['记录数']}</td>
            </tr>
            '''
        
        html += '</tbody></table></div></div>'
        return html
    
    def _generate_anomaly_analysis_section(self, anomalies: Optional[list]) -> str:
        """生成异常分析部分"""
        if not anomalies:
            return '<div class="no-data">✅ 未检测到费用异常</div>'
        
        html = '<div class="analysis-section">'
        html += '<h3>🚨 检测到的费用异常</h3>'
        html += '<div class="table-container">'
        html += '<table class="data-table">'
        html += '<thead><tr><th>异常日期</th><th>费用金额</th><th>异常类型</th><th>偏差程度</th></tr></thead>'
        html += '<tbody>'
        
        for anomaly in anomalies[:10]:  # 只显示前10个异常
            anomaly_type_icon = '⬆️' if anomaly['type'] == 'high' else '⬇️'
            html += f'''
            <tr>
                <td>{anomaly['date'].strftime('%Y-%m-%d')}</td>
                <td class="cost-value">${anomaly['cost']:.2f}</td>
                <td>{anomaly_type_icon} {anomaly['type']}</td>
                <td>{anomaly['deviation']:.2f}σ</td>
            </tr>
            '''
        
        html += '</tbody></table></div></div>'
        return html
    
    def _get_modern_css_styles(self) -> str:
        """获取现代化CSS样式"""
        return """
        :root {
            --primary-color: #3498db;
            --secondary-color: #2c3e50;
            --accent-color: #e74c3c;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --background-color: #f8fafc;
            --card-background: #ffffff;
            --text-primary: #2c3e50;
            --text-secondary: #7f8c8d;
            --border-color: #e1e8ed;
            --shadow-light: 0 2px 10px rgba(0,0,0,0.1);
            --shadow-medium: 0 4px 20px rgba(0,0,0,0.15);
            --border-radius: 12px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: var(--background-color);
            min-height: 100vh;
            box-shadow: var(--shadow-medium);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
        }
        
        .header-content {
            position: relative;
            z-index: 2;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }
        
        .meta-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
            position: relative;
            z-index: 2;
        }
        
        .meta-card {
            background: rgba(255,255,255,0.2);
            border-radius: var(--border-radius);
            padding: 1rem;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.3);
        }
        
        .meta-label {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 0.5rem;
        }
        
        .meta-value {
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .main-content {
            padding: 2rem;
        }
        
        .chart-section, .dashboard-section, .summary-section, .data-section {
            background: var(--card-background);
            border-radius: var(--border-radius);
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-light);
            border: 1px solid var(--border-color);
        }
        
        .section-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .section-header h2 {
            font-size: 2rem;
            color: var(--secondary-color);
            margin-bottom: 0.5rem;
        }
        
        .section-header p {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }
        
        .chart-container {
            margin: 1rem 0;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--shadow-light);
        }
        
        .analysis-section {
            margin-top: 2rem;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: var(--border-radius);
            border-left: 4px solid var(--primary-color);
        }
        
        .analysis-section h3 {
            color: var(--secondary-color);
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }
        
        .table-container {
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--shadow-light);
        }
        
        .data-table th {
            background: linear-gradient(135deg, var(--primary-color) 0%, #2980b9 100%);
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .data-table td {
            padding: 0.8rem 1rem;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.9rem;
        }
        
        .data-table tr:hover {
            background-color: #f1f3f4;
        }
        
        .data-table tr:last-child td {
            border-bottom: none;
        }
        
        .cost-value {
            font-weight: 600;
            color: var(--accent-color);
        }
        
        .no-data {
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
            font-size: 1.1rem;
            background: #f8f9fa;
            border-radius: var(--border-radius);
            border: 2px dashed var(--border-color);
        }
        
        code {
            background: #f1f3f4;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.85rem;
            color: #e91e63;
        }
        
        .footer {
            background: var(--secondary-color);
            color: white;
            text-align: center;
            padding: 2rem;
        }
        
        .footer-content p {
            margin-bottom: 0.5rem;
        }
        
        .footer-content p:first-child {
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .footer-content p:last-child {
            opacity: 0.8;
            font-size: 0.9rem;
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .meta-info {
                grid-template-columns: 1fr;
            }
            
            .main-content {
                padding: 1rem;
            }
            
            .chart-section, .dashboard-section, .summary-section, .data-section {
                padding: 1rem;
            }
            
            .section-header h2 {
                font-size: 1.5rem;
            }
        }
        
        /* 打印样式 */
        @media print {
            body {
                background: white;
            }
            
            .container {
                box-shadow: none;
            }
            
            .header {
                background: var(--secondary-color) !important;
            }
            
            .chart-container {
                break-inside: avoid;
            }
        }
        """
    
    def _get_modern_javascript(self) -> str:
        """获取现代化JavaScript功能"""
        return """
        // 页面加载完成后执行
        document.addEventListener('DOMContentLoaded', function() {
            // 添加页面加载动画
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.5s ease-in-out';
            
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 100);
            
            // 添加平滑滚动
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
            
            // 添加表格排序功能
            const tables = document.querySelectorAll('.data-table');
            tables.forEach(addTableSorting);
            
            // 添加工具提示
            addTooltips();
            
            // 性能优化：图表懒加载
            observeChartContainers();
        });
        
        function addTableSorting(table) {
            const headers = table.querySelectorAll('th');
            headers.forEach((header, index) => {
                header.style.cursor = 'pointer';
                header.style.userSelect = 'none';
                header.title = '点击排序';
                
                header.addEventListener('click', () => {
                    sortTable(table, index);
                });
            });
        }
        
        function sortTable(table, columnIndex) {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const isNumeric = rows.length > 0 && 
                             !isNaN(parseFloat(rows[0].cells[columnIndex].textContent.replace(/[$,]/g, '')));
            
            rows.sort((a, b) => {
                let aVal = a.cells[columnIndex].textContent.trim();
                let bVal = b.cells[columnIndex].textContent.trim();
                
                if (isNumeric) {
                    aVal = parseFloat(aVal.replace(/[$,]/g, '')) || 0;
                    bVal = parseFloat(bVal.replace(/[$,]/g, '')) || 0;
                    return bVal - aVal; // 降序
                } else {
                    return aVal.localeCompare(bVal);
                }
            });
            
            // 重新添加排序后的行
            rows.forEach(row => tbody.appendChild(row));
            
            // 添加排序视觉反馈
            table.querySelectorAll('th').forEach(th => th.classList.remove('sorted'));
            table.querySelectorAll('th')[columnIndex].classList.add('sorted');
        }
        
        function addTooltips() {
            // 为费用值添加工具提示
            document.querySelectorAll('.cost-value').forEach(element => {
                const value = parseFloat(element.textContent.replace(/[$,]/g, ''));
                if (value > 1000) {
                    element.title = `${(value/1000).toFixed(2)}K`;
                }
            });
        }
        
        function observeChartContainers() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                    }
                });
            }, {
                threshold: 0.1
            });
            
            document.querySelectorAll('.chart-container').forEach(container => {
                observer.observe(container);
            });
        }
        
        // 添加CSS动画类
        const style = document.createElement('style');
        style.textContent = `
            .sorted::after {
                content: ' ↓';
                color: var(--primary-color);
            }
            
            .animate-in {
                animation: slideInUp 0.6s ease-out;
            }
            
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
        """
    
    def _get_css_styles(self) -> str:
        """获取CSS样式"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .meta-info {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }
        
        .meta-info p {
            background-color: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .main-content {
            padding: 2rem;
        }
        
        .section {
            margin-bottom: 3rem;
            background-color: #fafafa;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .section h2 {
            color: #2c3e50;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.5rem;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .summary-card {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(116, 185, 255, 0.3);
        }
        
        .summary-card h3 {
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            opacity: 0.9;
        }
        
        .summary-card .value {
            font-size: 2rem;
            font-weight: bold;
        }
        
        .table-container {
            overflow-x: auto;
            margin-top: 1rem;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        th {
            background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 1rem;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        .cost-value {
            font-weight: bold;
            color: #e74c3c;
        }
        
        .footer {
            background-color: #2c3e50;
            color: white;
            text-align: center;
            padding: 1rem;
        }
        
        .chart-placeholder {
            background-color: #ecf0f1;
            border: 2px dashed #bdc3c7;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            color: #7f8c8d;
            margin: 1rem 0;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .meta-info {
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .summary-grid {
                grid-template-columns: 1fr;
            }
            
            .main-content {
                padding: 1rem;
            }
        }
        """
    
    def _get_javascript(self) -> str:
        """获取JavaScript代码"""
        return """
        // 添加表格排序功能
        document.addEventListener('DOMContentLoaded', function() {
            const tables = document.querySelectorAll('table');
            tables.forEach(table => {
                const headers = table.querySelectorAll('th');
                headers.forEach((header, index) => {
                    header.style.cursor = 'pointer';
                    header.addEventListener('click', () => {
                        sortTable(table, index);
                    });
                });
            });
        });
        
        function sortTable(table, columnIndex) {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const isNumeric = columnIndex > 0; // 假设第一列是文本，其他列是数字
            
            rows.sort((a, b) => {
                const aVal = a.cells[columnIndex].textContent.trim();
                const bVal = b.cells[columnIndex].textContent.trim();
                
                if (isNumeric) {
                    const aNum = parseFloat(aVal.replace(/[$,]/g, ''));
                    const bNum = parseFloat(bVal.replace(/[$,]/g, ''));
                    return bNum - aNum; // 降序排列
                } else {
                    return aVal.localeCompare(bVal);
                }
            });
            
            rows.forEach(row => tbody.appendChild(row));
        }
        """
    
    def _calculate_cost_summary(self, df: pd.DataFrame) -> Dict[str, float]:
        """计算费用摘要"""
        if df.empty:
            return {
                'total_cost': 0.0,
                'avg_daily_cost': 0.0,
                'max_daily_cost': 0.0,
                'min_daily_cost': 0.0
            }
        
        total_cost = df['Cost'].sum()
        daily_costs = df.groupby('Date')['Cost'].sum()
        
        return {
            'total_cost': total_cost,
            'avg_daily_cost': daily_costs.mean(),
            'max_daily_cost': daily_costs.max(),
            'min_daily_cost': daily_costs.min()
        }
    
    def _generate_cost_summary_section(self, cost_summary: Dict[str, float]) -> str:
        """生成费用摘要部分"""
        return f"""
        <section class="section">
            <h2>💰 费用摘要</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>总费用</h3>
                    <div class="value">${cost_summary['total_cost']:.2f}</div>
                </div>
                <div class="summary-card">
                    <h3>平均每日费用</h3>
                    <div class="value">${cost_summary['avg_daily_cost']:.2f}</div>
                </div>
                <div class="summary-card">
                    <h3>最高单日费用</h3>
                    <div class="value">${cost_summary['max_daily_cost']:.2f}</div>
                </div>
                <div class="summary-card">
                    <h3>最低单日费用</h3>
                    <div class="value">${cost_summary['min_daily_cost']:.2f}</div>
                </div>
            </div>
        </section>
        """
    
    def _generate_service_analysis_section(self, service_costs: Optional[pd.DataFrame]) -> str:
        """生成服务分析部分"""
        if service_costs is None or service_costs.empty:
            return """
            <section class="section">
                <h2>🔧 按服务分析</h2>
                <p>暂无服务费用数据</p>
            </section>
            """
        
        table_rows = ""
        for service, row in service_costs.head(10).iterrows():
            table_rows += f"""
                <tr>
                    <td>{service}</td>
                    <td class="cost-value">${row['总费用']:.2f}</td>
                    <td class="cost-value">${row['平均费用']:.2f}</td>
                    <td>{row['记录数']}</td>
                </tr>
            """
        
        return f"""
        <section class="section">
            <h2>🔧 按服务分析</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>服务名称</th>
                            <th>总费用</th>
                            <th>平均费用</th>
                            <th>记录数</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </section>
        """
    
    def _generate_region_analysis_section(self, region_costs: Optional[pd.DataFrame]) -> str:
        """生成区域分析部分"""
        if region_costs is None or region_costs.empty:
            return """
            <section class="section">
                <h2>🌍 按区域分析</h2>
                <p>暂无区域费用数据</p>
            </section>
            """
        
        table_rows = ""
        for region, row in region_costs.head(10).iterrows():
            table_rows += f"""
                <tr>
                    <td>{region}</td>
                    <td class="cost-value">${row['总费用']:.2f}</td>
                    <td class="cost-value">${row['平均费用']:.2f}</td>
                    <td>{row['记录数']}</td>
                </tr>
            """
        
        return f"""
        <section class="section">
            <h2>🌍 按区域分析</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>区域名称</th>
                            <th>总费用</th>
                            <th>平均费用</th>
                            <th>记录数</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </section>
        """
    
    def _generate_detailed_data_section(self, df: pd.DataFrame) -> str:
        """生成详细数据部分"""
        if df.empty:
            return """
            <section class="section">
                <h2>📋 详细费用数据</h2>
                <p>暂无详细费用数据</p>
            </section>
            """
        
        # 按日期排序，只显示前50条记录
        df_sorted = df.sort_values(['Date', 'Cost'], ascending=[True, False]).head(50)
        
        table_rows = ""
        for _, row in df_sorted.iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d')
            service = row['Service'][:30] + "..." if len(row['Service']) > 30 else row['Service']
            region = row['Region'][:15] + "..." if len(row['Region']) > 15 else row['Region']
            
            table_rows += f"""
                <tr>
                    <td>{date_str}</td>
                    <td>{service}</td>
                    <td>{region}</td>
                    <td class="cost-value">${row['Cost']:.2f}</td>
                </tr>
            """
        
        return f"""
        <section class="section">
            <h2>📋 详细费用数据 (前50条)</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>服务</th>
                            <th>区域</th>
                            <th>费用</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </section>
        """
