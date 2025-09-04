#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建美观的AWS费用分析图表
生成专业、现代化的PNG图片
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from datetime import datetime
import warnings

# 忽略警告
warnings.filterwarnings('ignore')

# 设置现代化样式
plt.style.use('default')
sns.set_palette("husl")

def setup_modern_style():
    """设置现代化的图表样式"""
    # 设置字体 - 使用英文标签避免中文字体问题
    plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans', 'sans-serif']
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 16
    
    # 设置颜色
    plt.rcParams['axes.prop_cycle'] = plt.cycler('color', [
        '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#7209B7',
        '#3A86FF', '#06FFA5', '#FFBE0B', '#FB5607', '#8338EC'
    ])

def create_beautiful_service_chart(df, save_path='costs_by_service_beautiful.png'):
    """创建美观的服务费用分布图"""
    
    if df is None or df.empty:
        print("没有数据可绘制图表")
        return
    
    # 准备数据
    service_costs = df.groupby('Service')['Cost'].sum().sort_values(ascending=False)
    top_services = service_costs.head(8)
    
    # 设置样式
    setup_modern_style()
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # 设置背景
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('white')
    
    # 创建水平条形图
    y_pos = np.arange(len(top_services))
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#7209B7', '#3A86FF', '#06FFA5', '#FFBE0B']
    
    bars = ax.barh(y_pos, top_services.values, color=colors[:len(top_services)], 
                   height=0.7, edgecolor='white', linewidth=2)
    
    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, top_services.values)):
        ax.text(bar.get_width() + max(top_services.values) * 0.01, 
                bar.get_y() + bar.get_height()/2, 
                f'${value:.2f}', 
                ha='left', va='center', fontweight='bold', fontsize=11)
    
    # 设置标签
    ax.set_yticks(y_pos)
    ax.set_yticklabels([service.replace('Amazon ', '').replace('AWS ', '') for service in top_services.index], 
                       fontsize=11)
    ax.set_xlabel('Cost ($)', fontsize=12, fontweight='bold')
    
    # 设置标题
    ax.set_title('AWS Service Cost Distribution', fontsize=18, fontweight='bold', pad=20, color='#2c3e50')
    
    # 美化坐标轴
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#bdc3c7')
    ax.spines['bottom'].set_color('#bdc3c7')
    
    # 添加网格
    ax.grid(axis='x', alpha=0.3, linestyle='--', color='#bdc3c7')
    
    # 添加总费用信息
    total_cost = service_costs.sum()
    ax.text(0.02, 0.98, f'Total Cost: ${total_cost:.2f}', 
            transform=ax.transAxes, fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#ecf0f1', alpha=0.8))
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                facecolor='#f8f9fa', edgecolor='none')
    plt.close()
    
    print(f"✅ 美观的服务费用分布图已保存: {save_path}")

def create_beautiful_trend_chart(df, save_path='cost_trend_beautiful.png'):
    """创建美观的费用趋势图"""
    
    if df is None or df.empty:
        print("没有数据可绘制图表")
        return
    
    # 准备数据
    time_costs = df.groupby('Date')['Cost'].sum().reset_index()
    time_costs = time_costs.sort_values('Date')
    
    # 设置样式
    setup_modern_style()
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    fig.patch.set_facecolor('#f8f9fa')
    
    # 主图：费用趋势
    ax1.set_facecolor('white')
    
    # 绘制主趋势线
    line = ax1.plot(time_costs['Date'], time_costs['Cost'], 
                    color='#2E86AB', linewidth=3, marker='o', 
                    markersize=8, markerfacecolor='#2E86AB', 
                    markeredgecolor='white', markeredgewidth=2)
    
    # 添加填充区域
    ax1.fill_between(time_costs['Date'], time_costs['Cost'], 
                     alpha=0.3, color='#2E86AB')
    
    # 添加趋势线
    if len(time_costs) > 1:
        z = np.polyfit(range(len(time_costs)), time_costs['Cost'], 1)
        p = np.poly1d(z)
        ax1.plot(time_costs['Date'], p(range(len(time_costs))), 
                "r--", alpha=0.8, linewidth=2, label='趋势线')
        ax1.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # 设置标题和标签
    ax1.set_title('AWS Cost Trend Analysis', fontsize=18, fontweight='bold', 
                  pad=20, color='#2c3e50')
    ax1.set_ylabel('Cost ($)', fontsize=12, fontweight='bold')
    
    # 美化坐标轴
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#bdc3c7')
    ax1.spines['bottom'].set_color('#bdc3c7')
    
    # 添加网格
    ax1.grid(True, alpha=0.3, linestyle='--', color='#bdc3c7')
    
    # 添加统计信息
    max_cost = time_costs['Cost'].max()
    min_cost = time_costs['Cost'].min()
    avg_cost = time_costs['Cost'].mean()
    
    ax1.text(0.02, 0.98, f'Max: ${max_cost:.2f}\nMin: ${min_cost:.2f}\nAvg: ${avg_cost:.2f}', 
             transform=ax1.transAxes, fontsize=10, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='#ecf0f1', alpha=0.8),
             verticalalignment='top')
    
    # 子图：费用分布直方图
    ax2.set_facecolor('white')
    
    # 创建直方图
    n, bins, patches = ax2.hist(time_costs['Cost'], bins=15, alpha=0.7, 
                               color='#A23B72', edgecolor='white', linewidth=2)
    
    # 设置标题和标签
    ax2.set_title('Cost Distribution Histogram', fontsize=16, fontweight='bold', 
                  pad=15, color='#2c3e50')
    ax2.set_xlabel('Cost ($)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    
    # 美化坐标轴
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#bdc3c7')
    ax2.spines['bottom'].set_color('#bdc3c7')
    
    # 添加网格
    ax2.grid(True, alpha=0.3, linestyle='--', color='#bdc3c7')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                facecolor='#f8f9fa', edgecolor='none')
    plt.close()
    
    print(f"✅ 美观的费用趋势图已保存: {save_path}")

def create_beautiful_region_chart(df, save_path='costs_by_region_beautiful.png'):
    """创建美观的区域费用分布图"""
    
    if df is None or df.empty:
        print("没有数据可绘制图表")
        return
    
    # 准备数据
    region_costs = df.groupby('Region')['Cost'].sum().sort_values(ascending=False)
    
    # 设置样式
    setup_modern_style()
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('white')
    
    # 创建水平条形图替代饼图，避免标签重叠
    y_pos = np.arange(len(region_costs))
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#7209B7', '#3A86FF']
    
    bars = ax.barh(y_pos, region_costs.values, color=colors[:len(region_costs)], 
                   height=0.7, edgecolor='white', linewidth=2)
    
    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, region_costs.values)):
        ax.text(bar.get_width() + max(region_costs.values) * 0.01, 
                bar.get_y() + bar.get_height()/2, 
                f'${value:.2f}', 
                ha='left', va='center', fontweight='bold', fontsize=11)
    
    # 设置标签
    ax.set_yticks(y_pos)
    ax.set_yticklabels(region_costs.index, fontsize=11)
    ax.set_xlabel('Cost ($)', fontsize=12, fontweight='bold')
    
    # 设置标题
    ax.set_title('AWS Region Cost Distribution', fontsize=18, fontweight='bold', 
                 pad=20, color='#2c3e50')
    
    # 美化坐标轴
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#bdc3c7')
    ax.spines['bottom'].set_color('#bdc3c7')
    
    # 添加网格
    ax.grid(axis='x', alpha=0.3, linestyle='--', color='#bdc3c7')
    
    # 添加总费用信息
    total_cost = region_costs.sum()
    ax.text(0.02, 0.98, f'Total Cost: ${total_cost:.2f}', 
            transform=ax.transAxes, fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#ecf0f1', alpha=0.8))
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                facecolor='#f8f9fa', edgecolor='none')
    plt.close()
    
    print(f"✅ 美观的区域费用分布图已保存: {save_path}")

def create_comprehensive_dashboard(df, save_path='aws_cost_dashboard_beautiful.png'):
    """创建综合费用分析仪表板"""
    
    if df is None or df.empty:
        print("没有数据可绘制图表")
        return
    
    # 准备数据
    service_costs = df.groupby('Service')['Cost'].sum().sort_values(ascending=False)
    region_costs = df.groupby('Region')['Cost'].sum().sort_values(ascending=False)
    time_costs = df.groupby('Date')['Cost'].sum().reset_index()
    time_costs = time_costs.sort_values('Date')
    
    # 设置样式
    setup_modern_style()
    
    # 创建图形
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('#f8f9fa')
    
    # 创建网格布局
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. 费用趋势图 (左上，跨2列)
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.set_facecolor('white')
    ax1.plot(time_costs['Date'], time_costs['Cost'], 
             color='#2E86AB', linewidth=3, marker='o', markersize=6)
    ax1.fill_between(time_costs['Date'], time_costs['Cost'], alpha=0.3, color='#2E86AB')
    ax1.set_title('Cost Trend', fontsize=14, fontweight='bold', color='#2c3e50')
    ax1.set_ylabel('Cost ($)', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # 2. 总费用统计 (右上)
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_facecolor('white')
    total_cost = df['Cost'].sum()
    ax2.text(0.5, 0.5, f'${total_cost:.2f}', ha='center', va='center', 
             fontsize=24, fontweight='bold', color='#2E86AB')
    ax2.set_title('Total Cost', fontsize=14, fontweight='bold', color='#2c3e50')
    ax2.axis('off')
    
    # 3. 服务费用分布 (中左)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor('white')
    top_services = service_costs.head(5)
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#7209B7']
    ax3.bar(range(len(top_services)), top_services.values, color=colors)
    ax3.set_title('Service Cost', fontsize=14, fontweight='bold', color='#2c3e50')
    ax3.set_xticks(range(len(top_services)))
    ax3.set_xticklabels([s.replace('Amazon ', '').replace('AWS ', '')[:10] + '...' 
                         if len(s) > 10 else s.replace('Amazon ', '').replace('AWS ', '') 
                         for s in top_services.index], rotation=45, ha='right')
    ax3.grid(True, alpha=0.3)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    
    # 4. 区域费用分布 (中中) - 改为条形图
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor('white')
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    y_pos = np.arange(len(region_costs))
    ax4.barh(y_pos, region_costs.values, color=colors[:len(region_costs)])
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(region_costs.index, fontsize=9)
    ax4.set_title('Region Distribution', fontsize=14, fontweight='bold', color='#2c3e50')
    ax4.grid(True, alpha=0.3)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    
    # 5. 费用统计 (中右)
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.set_facecolor('white')
    avg_cost = time_costs['Cost'].mean()
    max_cost = time_costs['Cost'].max()
    min_cost = time_costs['Cost'].min()
    
    stats_text = f'Avg: ${avg_cost:.2f}\nMax: ${max_cost:.2f}\nMin: ${min_cost:.2f}'
    ax5.text(0.5, 0.5, stats_text, ha='center', va='center', 
             fontsize=12, fontweight='bold', color='#2c3e50')
    ax5.set_title('Cost Statistics', fontsize=14, fontweight='bold', color='#2c3e50')
    ax5.axis('off')
    
    # 6. 费用分布直方图 (底部，跨3列)
    ax6 = fig.add_subplot(gs[2, :])
    ax6.set_facecolor('white')
    ax6.hist(time_costs['Cost'], bins=15, alpha=0.7, color='#A23B72', 
             edgecolor='white', linewidth=2)
    ax6.set_title('Cost Distribution Histogram', fontsize=14, fontweight='bold', color='#2c3e50')
    ax6.set_xlabel('Cost ($)', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.spines['top'].set_visible(False)
    ax6.spines['right'].set_visible(False)
    
    # 添加总标题
    fig.suptitle('AWS Cost Analysis Dashboard', fontsize=20, fontweight='bold', 
                 color='#2c3e50', y=0.98)
    
    # 保存图片
    plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                facecolor='#f8f9fa', edgecolor='none')
    plt.close()
    
    print(f"✅ 美观的综合仪表板已保存: {save_path}")

def main():
    """主函数"""
    print("🎨 创建美观的AWS费用分析图表...")
    
    # 这里需要先运行主程序获取数据
    print("请先运行 aws_cost_analyzer.py 获取数据，然后调用此函数")

if __name__ == "__main__":
    main()
