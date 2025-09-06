"""
交互式图表生成模块
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, Optional, List
import json
from datetime import datetime


class InteractiveChartGenerator:
    """交互式图表生成器"""
    
    def __init__(self):
        """初始化图表生成器"""
        self.color_palette = [
            '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
            '#34495e', '#1abc9c', '#e67e22', '#95a5a6', '#f1c40f'
        ]
    
    def generate_cost_trend_chart(self, df: pd.DataFrame) -> str:
        """
        生成费用趋势图表
        
        Args:
            df: 费用数据
            
        Returns:
            图表的HTML字符串
        """
        if df.empty:
            return self._get_empty_chart_html("无费用数据")
        
        # 按日期聚合费用
        daily_costs = df.groupby('Date')['Cost'].sum().reset_index()
        daily_costs['Date'] = pd.to_datetime(daily_costs['Date'])
        daily_costs = daily_costs.sort_values('Date')
        
        # 创建趋势图
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_costs['Date'],
            y=daily_costs['Cost'],
            mode='lines+markers',
            name='日费用',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8, color='#3498db', symbol='circle'),
            hovertemplate='<b>日期:</b> %{x}<br><b>费用:</b> $%{y:.2f}<extra></extra>'
        ))
        
        # 添加移动平均线
        if len(daily_costs) > 7:
            daily_costs['MA7'] = daily_costs['Cost'].rolling(window=7).mean()
            fig.add_trace(go.Scatter(
                x=daily_costs['Date'],
                y=daily_costs['MA7'],
                mode='lines',
                name='7日均线',
                line=dict(color='#e74c3c', width=2, dash='dash'),
                hovertemplate='<b>日期:</b> %{x}<br><b>7日均线:</b> $%{y:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title={
                'text': '📈 费用趋势分析',
                'x': 0.5,
                'font': {'size': 24, 'color': '#2c3e50'}
            },
            xaxis_title='日期',
            yaxis_title='费用 (USD)',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            font=dict(size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='cost_trend_chart')
    
    def generate_service_cost_pie_chart(self, service_costs: pd.DataFrame) -> str:
        """
        生成服务费用饼图
        
        Args:
            service_costs: 服务费用数据
            
        Returns:
            图表的HTML字符串
        """
        if service_costs.empty:
            return self._get_empty_chart_html("无服务费用数据")
        
        # 只显示前10个服务，其余归为"其他"
        top_services = service_costs.head(10).copy()
        if len(service_costs) > 10:
            others_cost = service_costs.iloc[10:]['总费用'].sum()
            other_row = pd.DataFrame({
                'Service': ['其他服务'],
                '总费用': [others_cost],
                '平均费用': [others_cost / (len(service_costs) - 10)],
                '记录数': [service_costs.iloc[10:]['记录数'].sum()]
            })
            top_services = pd.concat([top_services, other_row], ignore_index=True)
        
        fig = go.Figure(data=[go.Pie(
            labels=top_services.index if hasattr(top_services, 'index') else top_services['Service'],
            values=top_services['总费用'],
            hole=0.3,
            hovertemplate='<b>%{label}</b><br>费用: $%{value:.2f}<br>占比: %{percent}<extra></extra>',
            textinfo='label+percent',
            textposition='auto',
            marker=dict(colors=self.color_palette)
        )])
        
        fig.update_layout(
            title={
                'text': '🥧 各服务费用分布',
                'x': 0.5,
                'font': {'size': 24, 'color': '#2c3e50'}
            },
            height=500,
            font=dict(size=12),
            template='plotly_white'
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='service_pie_chart')
    
    def generate_region_cost_bar_chart(self, region_costs: pd.DataFrame) -> str:
        """
        生成区域费用柱状图
        
        Args:
            region_costs: 区域费用数据
            
        Returns:
            图表的HTML字符串
        """
        if region_costs.empty:
            return self._get_empty_chart_html("无区域费用数据")
        
        # 只显示前15个区域
        top_regions = region_costs.head(15)
        
        fig = go.Figure(data=[
            go.Bar(
                x=top_regions['总费用'],
                y=top_regions.index,
                orientation='h',
                marker=dict(
                    color=top_regions['总费用'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="费用 (USD)")
                ),
                hovertemplate='<b>区域:</b> %{y}<br><b>总费用:</b> $%{x:.2f}<br><b>记录数:</b> %{customdata}<extra></extra>',
                customdata=top_regions['记录数']
            )
        ])
        
        fig.update_layout(
            title={
                'text': '🌍 各区域费用分布',
                'x': 0.5,
                'font': {'size': 24, 'color': '#2c3e50'}
            },
            xaxis_title='费用 (USD)',
            yaxis_title='区域',
            height=max(400, len(top_regions) * 25 + 100),
            template='plotly_white',
            font=dict(size=12)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='region_bar_chart')
    
    def generate_resource_cost_heatmap(self, resource_costs: pd.DataFrame) -> str:
        """
        生成资源费用热力图
        
        Args:
            resource_costs: 资源费用数据
            
        Returns:
            图表的HTML字符串
        """
        if resource_costs.empty or 'ResourceId' not in resource_costs.columns:
            return self._get_empty_chart_html("无资源费用数据")
        
        # 准备热力图数据：按服务和资源ID
        heatmap_data = resource_costs.pivot_table(
            index='Service', 
            columns='ResourceId', 
            values='总费用', 
            fill_value=0
        )
        
        # 限制显示的资源数量
        if heatmap_data.shape[1] > 20:
            # 选择费用最高的20个资源
            top_resources = resource_costs.nlargest(20, '总费用')['ResourceId']
            heatmap_data = heatmap_data[heatmap_data.columns.intersection(top_resources)]
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlBu_r',
            hovertemplate='<b>服务:</b> %{y}<br><b>资源:</b> %{x}<br><b>费用:</b> $%{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '🔥 资源费用热力图',
                'x': 0.5,
                'font': {'size': 24, 'color': '#2c3e50'}
            },
            xaxis_title='资源ID',
            yaxis_title='服务',
            height=max(400, len(heatmap_data) * 30 + 100),
            template='plotly_white',
            font=dict(size=12)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='resource_heatmap')
    
    def generate_cost_anomaly_chart(self, df: pd.DataFrame, anomalies: List[Dict]) -> str:
        """
        生成费用异常检测图表
        
        Args:
            df: 费用数据
            anomalies: 异常数据列表
            
        Returns:
            图表的HTML字符串
        """
        if df.empty:
            return self._get_empty_chart_html("无费用数据")
        
        # 按日期聚合费用
        daily_costs = df.groupby('Date')['Cost'].sum().reset_index()
        daily_costs['Date'] = pd.to_datetime(daily_costs['Date'])
        daily_costs = daily_costs.sort_values('Date')
        
        fig = go.Figure()
        
        # 正常费用线
        fig.add_trace(go.Scatter(
            x=daily_costs['Date'],
            y=daily_costs['Cost'],
            mode='lines+markers',
            name='日费用',
            line=dict(color='#3498db', width=2),
            marker=dict(size=6, color='#3498db')
        ))
        
        # 异常点
        if anomalies:
            anomaly_dates = [pd.to_datetime(a['date']) for a in anomalies]
            anomaly_costs = [a['cost'] for a in anomalies]
            
            fig.add_trace(go.Scatter(
                x=anomaly_dates,
                y=anomaly_costs,
                mode='markers',
                name='异常点',
                marker=dict(size=12, color='#e74c3c', symbol='diamond'),
                hovertemplate='<b>异常日期:</b> %{x}<br><b>费用:</b> $%{y:.2f}<br><b>类型:</b> %{customdata}<extra></extra>',
                customdata=[a['type'] for a in anomalies]
            ))
        
        # 添加平均线
        avg_cost = daily_costs['Cost'].mean()
        fig.add_hline(y=avg_cost, line_dash="dash", line_color="#95a5a6", 
                     annotation_text=f"平均费用: ${avg_cost:.2f}")
        
        fig.update_layout(
            title={
                'text': '⚠️ 费用异常检测',
                'x': 0.5,
                'font': {'size': 24, 'color': '#2c3e50'}
            },
            xaxis_title='日期',
            yaxis_title='费用 (USD)',
            template='plotly_white',
            height=500,
            font=dict(size=12)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='anomaly_chart')
    
    def generate_multi_metric_dashboard(
        self, 
        df: pd.DataFrame, 
        service_costs: pd.DataFrame,
        region_costs: pd.DataFrame,
        resource_costs: Optional[pd.DataFrame] = None
    ) -> str:
        """
        生成多指标仪表板
        
        Args:
            df: 费用数据
            service_costs: 服务费用数据
            region_costs: 区域费用数据
            resource_costs: 资源费用数据
            
        Returns:
            仪表板的HTML字符串
        """
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('费用趋势', '服务分布', '区域分布', '费用统计'),
            specs=[[{"type": "scatter"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )
        
        # 1. 费用趋势
        if not df.empty:
            daily_costs = df.groupby('Date')['Cost'].sum().reset_index()
            daily_costs['Date'] = pd.to_datetime(daily_costs['Date'])
            daily_costs = daily_costs.sort_values('Date')
            
            fig.add_trace(
                go.Scatter(x=daily_costs['Date'], y=daily_costs['Cost'],
                          mode='lines+markers', name='日费用'),
                row=1, col=1
            )
        
        # 2. 服务饼图
        if not service_costs.empty:
            top_services = service_costs.head(8)
            fig.add_trace(
                go.Pie(labels=top_services.index, values=top_services['总费用'],
                       name="服务费用"),
                row=1, col=2
            )
        
        # 3. 区域柱状图
        if not region_costs.empty:
            top_regions = region_costs.head(10)
            fig.add_trace(
                go.Bar(x=top_regions.index, y=top_regions['总费用'],
                       name="区域费用"),
                row=2, col=1
            )
        
        # 4. 总费用指示器
        total_cost = df['Cost'].sum() if not df.empty else 0
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=total_cost,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "总费用 (USD)"},
                gauge={'axis': {'range': [None, total_cost * 1.5]},
                       'bar': {'color': "#3498db"},
                       'steps': [
                           {'range': [0, total_cost * 0.5], 'color': "#ecf0f1"},
                           {'range': [total_cost * 0.5, total_cost * 1.2], 'color': "#bdc3c7"}],
                       'threshold': {'line': {'color': "#e74c3c", 'width': 4},
                                   'thickness': 0.75, 'value': total_cost * 1.1}}),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="💼 AWS费用分析仪表板",
            height=800,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='dashboard')
    
    def _get_empty_chart_html(self, message: str) -> str:
        """
        生成空图表HTML
        
        Args:
            message: 显示消息
            
        Returns:
            空图表HTML
        """
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16, color="#7f8c8d")
        )
        fig.update_layout(
            height=400,
            template='plotly_white',
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        return fig.to_html(include_plotlyjs='cdn')
    
    def get_chart_scripts(self) -> str:
        """
        获取图表相关的JavaScript脚本
        
        Returns:
            JavaScript代码字符串
        """
        return """
        <script>
            // 图表交互功能
            document.addEventListener('DOMContentLoaded', function() {
                // 添加图表容器样式
                const chartContainers = document.querySelectorAll('[id$="_chart"]');
                chartContainers.forEach(container => {
                    container.style.marginBottom = '2rem';
                    container.style.border = '1px solid #e1e8ed';
                    container.style.borderRadius = '10px';
                    container.style.padding = '1rem';
                    container.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
                });
                
                // 添加图表响应式处理
                window.addEventListener('resize', function() {
                    setTimeout(function() {
                        Plotly.Plots.resize();
                    }, 100);
                });
            });
        </script>
        """