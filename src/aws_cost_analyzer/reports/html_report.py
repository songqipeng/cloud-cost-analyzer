"""
HTML报告生成模块
"""
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from ..utils.config import Config


class HTMLReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self):
        """初始化HTML报告生成器"""
        pass
    
    def generate_cost_report(
        self,
        df: pd.DataFrame,
        output_file: str,
        service_costs: Optional[pd.DataFrame] = None,
        region_costs: Optional[pd.DataFrame] = None
    ) -> bool:
        """
        生成HTML费用报告
        
        Args:
            df: 费用数据
            output_file: 输出文件路径
            service_costs: 服务费用统计
            region_costs: 区域费用统计
            
        Returns:
            生成是否成功
        """
        try:
            html_content = self._generate_html_content(df, service_costs, region_costs)
            
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
        region_costs: Optional[pd.DataFrame] = None
    ) -> str:
        """生成HTML内容"""
        
        # 计算费用摘要
        cost_summary = self._calculate_cost_summary(df)
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS费用分析报告</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📊 AWS费用分析报告</h1>
            <div class="meta-info">
                <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>数据时间范围:</strong> {df['Date'].min().strftime('%Y-%m-%d')} 到 {df['Date'].max().strftime('%Y-%m-%d')}</p>
                <p><strong>数据记录数:</strong> {len(df)} 条</p>
            </div>
        </header>
        
        <main class="main-content">
            {self._generate_cost_summary_section(cost_summary)}
            {self._generate_service_analysis_section(service_costs)}
            {self._generate_region_analysis_section(region_costs)}
            {self._generate_detailed_data_section(df)}
        </main>
        
        <footer class="footer">
            <p>此报告由AWS费用分析器自动生成</p>
        </footer>
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
        """
        
        return html
    
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
