#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建美观的AWS费用分析仪表板
生成轻量级但美观的HTML文件
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json

def create_beautiful_dashboard(df, save_path='aws_cost_dashboard_beautiful.html'):
    """创建美观的HTML仪表板"""
    
    if df is None or df.empty:
        print("没有数据可创建仪表板")
        return
    
    # 准备数据
    service_costs = df.groupby('Service')['Cost'].sum().sort_values(ascending=False)
    region_costs = df.groupby('Region')['Cost'].sum().sort_values(ascending=False)
    time_costs = df.groupby('Date')['Cost'].sum().reset_index()
    
    # 计算统计信息
    total_cost = df['Cost'].sum()
    avg_daily_cost = df.groupby('Date')['Cost'].sum().mean()
    max_daily_cost = df.groupby('Date')['Cost'].sum().max()
    min_daily_cost = df.groupby('Date')['Cost'].sum().min()
    
    # 创建图表
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('📈 费用趋势', '💰 服务费用分布', '🌍 区域费用分布', '📊 费用统计'),
        specs=[[{"type": "scatter"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "indicator"}]],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    # 1. 费用趋势图
    fig.add_trace(
        go.Scatter(
            x=time_costs['Date'], 
            y=time_costs['Cost'], 
            mode='lines+markers', 
            name='费用趋势',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8, color='#3498db', symbol='circle'),
            fill='tonexty',
            fillcolor='rgba(52, 152, 219, 0.1)'
        ),
        row=1, col=1
    )
    
    # 2. 服务费用分布 (前6名)
    top_services = service_costs.head(6)
    colors = ['#e74c3c', '#f39c12', '#27ae60', '#9b59b6', '#34495e', '#1abc9c']
    fig.add_trace(
        go.Bar(
            x=top_services.index, 
            y=top_services.values, 
            name='服务费用', 
            marker_color=colors[:len(top_services)],
            marker_line_color='rgba(0,0,0,0.3)',
            marker_line_width=1
        ),
        row=1, col=2
    )
    
    # 3. 区域费用分布
    region_colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6']
    fig.add_trace(
        go.Bar(
            x=region_costs.index, 
            y=region_costs.values, 
            name='区域费用', 
            marker_color=region_colors[:len(region_costs)],
            marker_line_color='rgba(0,0,0,0.3)',
            marker_line_width=1
        ),
        row=2, col=1
    )
    
    # 4. 费用统计指标
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=total_cost,
            title={'text': "总费用 ($)", 'font': {'size': 16}},
            delta={'reference': avg_daily_cost * 30, 'font': {'size': 12}},
            gauge={
                'axis': {'range': [None, total_cost * 1.2], 'tickwidth': 1, 'tickcolor': "#2c3e50"},
                'bar': {'color': "#3498db"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#34495e",
                'steps': [
                    {'range': [0, total_cost * 0.5], 'color': "#2ecc71"},
                    {'range': [total_cost * 0.5, total_cost * 0.8], 'color': "#f1c40f"},
                    {'range': [total_cost * 0.8, total_cost], 'color': "#e74c3c"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 3},
                    'thickness': 0.75,
                    'value': total_cost
                }
            }
        ),
        row=2, col=2
    )
    
    # 更新布局
    fig.update_layout(
        title={
            'text': "🚀 AWS费用分析仪表板",
            'font': {'size': 24, 'color': '#2c3e50'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=False,
        height=800,
        width=1000,
        paper_bgcolor='#ecf0f1',
        plot_bgcolor='white',
        font=dict(family="'Segoe UI', Arial, sans-serif", size=11, color='#2c3e50'),
        margin=dict(t=80, b=50, l=50, r=50)
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
    
    # 生成HTML内容
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS费用分析仪表板</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .chart-container {{
            padding: 30px;
        }}
        
        .chart-section {{
            margin-bottom: 40px;
        }}
        
        .chart-title {{
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 15px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
                padding: 20px;
            }}
            
            .chart-container {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AWS费用分析仪表板</h1>
            <p>实时监控和分析AWS云服务费用</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${total_cost:.2f}</div>
                <div class="stat-label">总费用</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${avg_daily_cost:.2f}</div>
                <div class="stat-label">平均每日费用</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${max_daily_cost:.2f}</div>
                <div class="stat-label">最高单日费用</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${min_daily_cost:.2f}</div>
                <div class="stat-label">最低单日费用</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-section">
                <div class="chart-title">📊 费用分析图表</div>
                <div id="chart"></div>
            </div>
        </div>
        
        <div class="footer">
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | AWS费用分析器</p>
        </div>
    </div>
    
    <script>
        {fig.to_json()}
        
        Plotly.newPlot('chart', fig.data, fig.layout, {{
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
        }});
        
        // 响应式调整
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('chart');
        }});
    </script>
</body>
</html>
"""
    
    # 保存HTML文件
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 美观的HTML仪表板已保存: {save_path}")

if __name__ == "__main__":
    print("创建美观的AWS费用分析仪表板...")
    
    # 这里需要先运行主程序获取数据
    # 或者直接调用这个函数
    print("请先运行 aws_cost_analyzer.py 获取数据，然后调用此函数")
