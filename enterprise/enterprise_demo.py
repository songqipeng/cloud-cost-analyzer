#!/usr/bin/env python3
"""
Enterprise Cloud Cost Analyzer - 完整企业级演示
包含所有第三阶段功能的完整演示版本
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import socket
from urllib.parse import parse_qs, urlparse
import random

class EnterpriseDemo:
    """完整的企业级演示服务器"""
    
    def __init__(self):
        self.port = 8888
        self.demo_data = self._generate_comprehensive_data()
        self.api_responses = self._setup_api_responses()
        
    def _generate_comprehensive_data(self):
        """生成完整的企业级演示数据"""
        return {
            "organizations": [
                {
                    "id": "org-001",
                    "name": "TechCorp Global",
                    "subscription": "enterprise",
                    "users": 150,
                    "teams": 8,
                    "monthly_spend": 237710,
                    "cost_efficiency": 78.5,
                    "last_optimization": "2024-01-08"
                }
            ],
            "cloud_accounts": [
                {"provider": "AWS", "account_id": "123456789012", "monthly_cost": 85420, "resources": 1247, "region": "us-east-1"},
                {"provider": "Azure", "account_id": "sub-456789", "monthly_cost": 62340, "resources": 892, "region": "East US"},
                {"provider": "GCP", "account_id": "project-789", "monthly_cost": 41250, "resources": 653, "region": "us-central1"},
                {"provider": "Alibaba Cloud", "account_id": "ali-123", "monthly_cost": 28900, "resources": 421, "region": "cn-hangzhou"},
                {"provider": "Tencent Cloud", "account_id": "ten-456", "monthly_cost": 19800, "resources": 287, "region": "ap-beijing"}
            ],
            "optimization_opportunities": [
                {
                    "id": "opt-001",
                    "type": "rightsizing",
                    "title": "EC2实例右侧化",
                    "description": "45个EC2实例利用率低于20%，建议调整实例类型",
                    "resources": 45,
                    "current_cost": 15200,
                    "potential_savings": 6840,
                    "savings_percentage": 45.0,
                    "confidence": 0.92,
                    "implementation_effort": "Low",
                    "risk_level": "Low",
                    "estimated_completion": "3-5 days"
                },
                {
                    "id": "opt-002", 
                    "type": "idle_resources",
                    "title": "闲置资源清理",
                    "description": "23个资源连续7天无活动，建议停止或删除",
                    "resources": 23,
                    "current_cost": 8960,
                    "potential_savings": 8512,
                    "savings_percentage": 95.0,
                    "confidence": 0.95,
                    "implementation_effort": "Low",
                    "risk_level": "Low",
                    "estimated_completion": "1-2 days"
                },
                {
                    "id": "opt-003",
                    "type": "reserved_instances", 
                    "title": "预留实例采购",
                    "description": "67个稳定运行实例适合购买RI，预计节省30-60%成本",
                    "resources": 67,
                    "current_cost": 24500,
                    "potential_savings": 11025,
                    "savings_percentage": 45.0,
                    "confidence": 0.88,
                    "implementation_effort": "Medium",
                    "risk_level": "Low", 
                    "estimated_completion": "1-2 weeks"
                }
            ],
            "unit_economics": [
                {
                    "metric": "Cost per Customer",
                    "current_value": 45.67,
                    "previous_value": 49.82,
                    "change_percentage": -8.3,
                    "trend": "improving",
                    "benchmark": 52.00,
                    "target": 42.00
                },
                {
                    "metric": "Cost per Feature",
                    "current_value": 1250.34,
                    "previous_value": 1189.12,
                    "change_percentage": 5.1,
                    "trend": "degrading",
                    "benchmark": 1100.00,
                    "target": 1000.00
                },
                {
                    "metric": "Revenue per Dollar Spent",
                    "current_value": 3.45,
                    "previous_value": 2.99,
                    "change_percentage": 15.4,
                    "trend": "improving",
                    "benchmark": 3.20,
                    "target": 4.00
                }
            ],
            "cost_allocation": {
                "total_allocated": 224567.50,
                "total_unallocated": 13142.50,
                "allocation_rate": 94.5,
                "methods_used": ["direct", "proportional", "weighted"],
                "team_allocations": [
                    {"team": "Engineering", "allocated": 78500, "budget": 85000, "utilization": 92.4},
                    {"team": "Data Science", "allocated": 45200, "budget": 50000, "utilization": 90.4},
                    {"team": "DevOps", "allocated": 32100, "budget": 35000, "utilization": 91.7},
                    {"team": "QA", "allocated": 18900, "budget": 25000, "utilization": 75.6},
                    {"team": "Infrastructure", "allocated": 49867.50, "budget": 55000, "utilization": 90.7}
                ]
            },
            "real_time_alerts": [
                {
                    "id": "alert-001",
                    "type": "cost_spike",
                    "severity": "high",
                    "title": "AWS EC2成本异常增长",
                    "description": "EC2实例成本在过去1小时内增长25.5%",
                    "affected_resource": "EC2 us-east-1",
                    "current_value": 847.50,
                    "baseline_value": 675.20,
                    "threshold": 742.72,
                    "detected_at": datetime.now(),
                    "is_resolved": False
                },
                {
                    "id": "alert-002", 
                    "type": "budget_breach",
                    "severity": "medium",
                    "title": "工程团队接近预算上限",
                    "description": "工程团队本月已使用92.4%预算",
                    "affected_resource": "Team: Engineering",
                    "current_value": 78500,
                    "threshold": 76500,
                    "detected_at": datetime.now() - timedelta(hours=2),
                    "is_resolved": False
                }
            ],
            "business_intelligence": {
                "monthly_summary": {
                    "total_revenue": 1250000,
                    "total_cost": 237710,
                    "gross_margin": 81.0,
                    "customer_count": 5200,
                    "active_features": 47,
                    "transaction_volume": 2340000
                },
                "forecasting": {
                    "next_month_cost": 267430,
                    "next_month_growth": 12.5,
                    "q1_projection": 825000,
                    "annual_projection": 3180000,
                    "confidence_interval": [2950000, 3410000]
                }
            }
        }
    
    def _setup_api_responses(self):
        """设置API响应"""
        return {
            "/api/health": {
                "status": "healthy",
                "timestamp": time.time(),
                "services": {
                    "database": "healthy",
                    "cache": "healthy", 
                    "monitoring": "healthy"
                },
                "version": "1.0.0"
            },
            "/api/v1/dashboard/summary": {
                "success": True,
                "data": {
                    "total_cost": sum([acc["monthly_cost"] for acc in self.demo_data["cloud_accounts"]]),
                    "cost_trend": 17.6,
                    "efficiency_score": 78.5,
                    "active_alerts": len(self.demo_data["real_time_alerts"]),
                    "cloud_accounts": len(self.demo_data["cloud_accounts"]),
                    "optimization_opportunities": len(self.demo_data["optimization_opportunities"]),
                    "potential_savings": sum([opp["potential_savings"] for opp in self.demo_data["optimization_opportunities"]])
                }
            },
            "/api/v1/optimization/opportunities": {
                "success": True,
                "data": self.demo_data["optimization_opportunities"]
            },
            "/api/v1/unit-economics/metrics": {
                "success": True,
                "data": self.demo_data["unit_economics"]
            },
            "/api/v1/cost-allocation/summary": {
                "success": True,
                "data": self.demo_data["cost_allocation"]
            }
        }
    
    def create_enterprise_html(self):
        """创建完整的企业级HTML页面"""
        total_cost = sum([acc["monthly_cost"] for acc in self.demo_data["cloud_accounts"]])
        total_savings = sum([opp["potential_savings"] for opp in self.demo_data["optimization_opportunities"]])
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Cloud Cost Analyzer - 完整版演示</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}
        .header {{
            background: rgba(255,255,255,0.98);
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            backdrop-filter: blur(15px);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        .header h1 {{
            color: #2c3e50;
            font-size: 2.8em;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #7f8c8d;
            font-size: 1.3em;
        }}
        .nav-tabs {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
            background: rgba(255,255,255,0.9);
            border-radius: 25px;
            padding: 5px;
            backdrop-filter: blur(10px);
            max-width: 800px;
            margin: 20px auto;
        }}
        .nav-tab {{
            padding: 12px 24px;
            margin: 0 5px;
            background: transparent;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 500;
            color: #7f8c8d;
            transition: all 0.3s ease;
        }}
        .nav-tab.active {{
            background: #3498db;
            color: white;
            box-shadow: 0 4px 15px rgba(52,152,219,0.3);
        }}
        .container {{
            max-width: 1400px;
            margin: 20px auto;
            padding: 0 20px;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
            animation: fadeIn 0.5s ease-in;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
            text-align: center;
            transition: all 0.3s ease;
            backdrop-filter: blur(15px);
            position: relative;
            overflow: hidden;
        }}
        .metric-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }}
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(45deg, #3498db, #2980b9);
        }}
        .metric-icon {{
            font-size: 3em;
            margin-bottom: 15px;
        }}
        .metric-value {{
            font-size: 2.8em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .metric-label {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        .metric-change {{
            margin-top: 15px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .positive {{ background: #d5f4e6; color: #27ae60; }}
        .negative {{ background: #fadbd8; color: #e74c3c; }}
        .chart-container {{
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
            margin-bottom: 25px;
            backdrop-filter: blur(15px);
        }}
        .chart-title {{
            font-size: 1.6em;
            color: #2c3e50;
            margin-bottom: 25px;
            text-align: center;
            font-weight: 600;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .data-table th,
        .data-table td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        .data-table th {{
            background: #f8f9fa;
            color: #2c3e50;
            font-weight: bold;
            font-size: 1.1em;
        }}
        .data-table tr:hover {{
            background: #f8f9fa;
        }}
        .savings {{ color: #27ae60; font-weight: bold; }}
        .cost {{ color: #e74c3c; font-weight: bold; }}
        .status {{
            padding: 6px 12px;
            border-radius: 15px;
            color: white;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status-high {{ background: #e74c3c; }}
        .status-medium {{ background: #f39c12; }}
        .status-low {{ background: #27ae60; }}
        .alert-card {{
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 5px solid #e74c3c;
            backdrop-filter: blur(10px);
        }}
        .alert-high {{ border-left-color: #e74c3c; }}
        .alert-medium {{ border-left-color: #f39c12; }}
        .alert-low {{ border-left-color: #3498db; }}
        .feature-showcase {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }}
        .feature-card {{
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }}
        .feature-card:hover {{
            transform: translateY(-5px);
        }}
        .feature-icon {{
            font-size: 2.5em;
            margin-bottom: 15px;
            color: #3498db;
        }}
        .feature-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .api-section {{
            background: rgba(255,255,255,0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            margin: 30px 0;
            backdrop-filter: blur(10px);
        }}
        .api-endpoint {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            border-left: 4px solid #3498db;
        }}
        .real-time-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #27ae60;
            border-radius: 50%;
            animation: pulse 2s infinite;
            margin-right: 10px;
        }}
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(39, 174, 96, 0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(39, 174, 96, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(39, 174, 96, 0); }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Enterprise Cloud Cost Analyzer</h1>
        <p>企业级云成本管理与优化平台 - 完整版演示</p>
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('dashboard')">📊 总览仪表板</button>
            <button class="nav-tab" onclick="showTab('optimization')">🤖 智能优化</button>
            <button class="nav-tab" onclick="showTab('unit-economics')">📈 单位经济学</button>
            <button class="nav-tab" onclick="showTab('allocation')">🏢 成本分配</button>
            <button class="nav-tab" onclick="showTab('monitoring')">⚡ 实时监控</button>
            <button class="nav-tab" onclick="showTab('api')">🔌 API接口</button>
        </div>
    </div>
    
    <div class="container">
        <!-- 总览仪表板 -->
        <div id="dashboard" class="tab-content active">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon">💰</div>
                    <div class="metric-value">${total_cost:,.0f}</div>
                    <div class="metric-label">月度总成本</div>
                    <div class="metric-change positive">节省潜力: ${total_savings:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">☁️</div>
                    <div class="metric-value">{len(self.demo_data["cloud_accounts"])}</div>
                    <div class="metric-label">云厂商接入</div>
                    <div class="metric-change">跨{len(self.demo_data["cloud_accounts"])}大云平台</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">🎯</div>
                    <div class="metric-value">94.5%</div>
                    <div class="metric-label">成本分配准确率</div>
                    <div class="metric-change positive">+2.1% vs 上月</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">⚡</div>
                    <div class="metric-value">{len(self.demo_data["real_time_alerts"])}</div>
                    <div class="metric-label">实时告警</div>
                    <div class="metric-change negative">需要处理</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">🌍 多云成本分布</div>
                <canvas id="multiCloudChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">📊 团队预算使用情况</div>
                <canvas id="teamBudgetChart" width="400" height="300"></canvas>
            </div>
        </div>
        
        <!-- 智能优化 -->
        <div id="optimization" class="tab-content">
            <div class="chart-container">
                <div class="chart-title">🤖 优化机会总览</div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>优化类型</th>
                            <th>影响资源</th>
                            <th>当前成本</th>
                            <th>预期节省</th>
                            <th>节省比例</th>
                            <th>置信度</th>
                            <th>实施难度</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # 添加优化机会数据
        for opp in self.demo_data["optimization_opportunities"]:
            type_map = {
                "rightsizing": "资源右侧化",
                "idle_resources": "闲置资源清理",
                "reserved_instances": "预留实例优化"
            }
            html_content += f"""
                        <tr>
                            <td>{type_map.get(opp["type"], opp["type"])}</td>
                            <td>{opp["resources"]} 个</td>
                            <td class="cost">${opp["current_cost"]:,.0f}</td>
                            <td class="savings">${opp["potential_savings"]:,.0f}</td>
                            <td>{opp["savings_percentage"]:.1f}%</td>
                            <td><span class="status status-{'high' if opp['confidence'] > 0.9 else 'medium'}">{opp['confidence']:.0%}</span></td>
                            <td>{opp["implementation_effort"]}</td>
                        </tr>
"""
        
        html_content += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">💡 优化建议详情</div>
                <div class="feature-showcase">
"""
        
        # 添加详细优化建议
        for opp in self.demo_data["optimization_opportunities"]:
            html_content += f"""
                    <div class="feature-card">
                        <div class="feature-icon">🔧</div>
                        <div class="feature-title">{opp["title"]}</div>
                        <p>{opp["description"]}</p>
                        <p><strong>预计完成时间:</strong> {opp["estimated_completion"]}</p>
                        <p><strong>风险等级:</strong> {opp["risk_level"]}</p>
                    </div>
"""
        
        html_content += f"""
                </div>
            </div>
        </div>
        
        <!-- 单位经济学 -->
        <div id="unit-economics" class="tab-content">
            <div class="metrics-grid">
"""
        
        # 添加单位经济学指标
        for metric in self.demo_data["unit_economics"]:
            trend_color = "positive" if metric["trend"] == "improving" else "negative"
            html_content += f"""
                <div class="metric-card">
                    <div class="metric-icon">📊</div>
                    <div class="metric-value">${metric["current_value"]:.2f}</div>
                    <div class="metric-label">{metric["metric"]}</div>
                    <div class="metric-change {trend_color}">{metric["change_percentage"]:+.1f}% vs 上期</div>
                </div>
"""
        
        html_content += f"""
            </div>
            
            <div class="chart-container">
                <div class="chart-title">📈 业务价值指标趋势</div>
                <canvas id="unitEconomicsChart" width="400" height="300"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">🎯 关键业务洞察</div>
                <div class="feature-showcase">
                    <div class="feature-card">
                        <div class="feature-icon">👥</div>
                        <div class="feature-title">客户成本效率</div>
                        <p>每客户成本下降8.3%，表明规模效应显现。建议继续优化客户获取成本，目标降至$42/客户。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⚙️</div>
                        <div class="feature-title">功能投入回报</div>
                        <p>功能开发成本略有上升，但每投入$1的云成本可带来$3.45收入，ROI表现优秀。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <div class="feature-title">收入增长驱动</div>
                        <p>单位云成本的收入产出提升15.4%，表明业务效率和产品价值在持续改善。</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 成本分配 -->
        <div id="allocation" class="tab-content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-icon">🎯</div>
                    <div class="metric-value">94.5%</div>
                    <div class="metric-label">成本分配率</div>
                    <div class="metric-change positive">业界领先水平</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">💸</div>
                    <div class="metric-value">${self.demo_data["cost_allocation"]["total_allocated"]:,.0f}</div>
                    <div class="metric-label">已分配成本</div>
                    <div class="metric-change">剩余${self.demo_data["cost_allocation"]["total_unallocated"]:,.0f}未分配</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">🏢</div>
                    <div class="metric-value">{len(self.demo_data["cost_allocation"]["team_allocations"])}</div>
                    <div class="metric-label">团队数量</div>
                    <div class="metric-change">覆盖全部业务团队</div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">📋</div>
                    <div class="metric-value">{len(self.demo_data["cost_allocation"]["methods_used"])}</div>
                    <div class="metric-label">分配方法</div>
                    <div class="metric-change">多维度精准分配</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">🏢 团队成本分配与预算对比</div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>团队</th>
                            <th>分配成本</th>
                            <th>预算</th>
                            <th>预算使用率</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # 添加团队分配数据
        for team in self.demo_data["cost_allocation"]["team_allocations"]:
            status = "正常" if team["utilization"] < 90 else "接近上限" if team["utilization"] < 95 else "需要关注"
            status_class = "status-low" if team["utilization"] < 90 else "status-medium" if team["utilization"] < 95 else "status-high"
            
            html_content += f"""
                        <tr>
                            <td>{team["team"]}</td>
                            <td class="cost">${team["allocated"]:,.0f}</td>
                            <td>${team["budget"]:,.0f}</td>
                            <td>{team["utilization"]:.1f}%</td>
                            <td><span class="status {status_class}">{status}</span></td>
                        </tr>
"""
        
        html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- 实时监控 -->
        <div id="monitoring" class="tab-content">
            <div class="chart-container">
                <div class="chart-title">
                    <span class="real-time-indicator"></span>实时告警监控
                </div>
"""
        
        # 添加实时告警
        for alert in self.demo_data["real_time_alerts"]:
            alert_class = f"alert-{alert['severity']}"
            html_content += f"""
                <div class="alert-card {alert_class}">
                    <h4>{alert["title"]} 
                        <span class="status status-{alert['severity']}">{alert['severity'].upper()}</span>
                    </h4>
                    <p>{alert["description"]}</p>
                    <p><strong>影响资源:</strong> {alert["affected_resource"]}</p>
                    <p><strong>检测时间:</strong> {alert["detected_at"].strftime('%Y-%m-%d %H:%M:%S')}</p>
                    {'<p><strong>当前值:</strong> $' + f"{alert['current_value']:.2f}" + '</p>' if "current_value" in alert else ''}
                </div>
"""
        
        html_content += f"""
            </div>
            
            <div class="feature-showcase">
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">实时处理能力</div>
                    <p><strong>数据延迟:</strong> &lt;30秒</p>
                    <p><strong>处理吞吐:</strong> 173,039 ops/sec</p>
                    <p><strong>异常检测准确率:</strong> 99.5%</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📡</div>
                    <div class="feature-title">多渠道告警</div>
                    <p><strong>WebSocket:</strong> 实时推送</p>
                    <p><strong>邮件通知:</strong> 关键告警</p>
                    <p><strong>Slack集成:</strong> 团队协作</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔄</div>
                    <div class="feature-title">自动化响应</div>
                    <p><strong>智能聚合:</strong> 减少告警噪音</p>
                    <p><strong>自动扩缩:</strong> 动态资源调整</p>
                    <p><strong>预算控制:</strong> 超支自动阻止</p>
                </div>
            </div>
        </div>
        
        <!-- API接口 -->
        <div id="api" class="tab-content">
            <div class="api-section">
                <div class="chart-title">🔌 Enterprise API 接口</div>
                
                <h3>核心API端点</h3>
                <div class="api-endpoint">
                    GET /api/health - 系统健康检查
                </div>
                <div class="api-endpoint">
                    GET /api/v1/dashboard/summary - 仪表板汇总数据
                </div>
                <div class="api-endpoint">
                    GET /api/v1/optimization/opportunities - 获取优化建议
                </div>
                <div class="api-endpoint">
                    GET /api/v1/unit-economics/metrics - 单位经济学指标
                </div>
                <div class="api-endpoint">
                    GET /api/v1/cost-allocation/summary - 成本分配汇总
                </div>
                
                <h3>实时API测试</h3>
                <div style="margin: 20px 0;">
                    <button onclick="testApi('/api/health')" style="background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">测试健康检查</button>
                    <button onclick="testApi('/api/v1/dashboard/summary')" style="background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">测试仪表板API</button>
                </div>
                
                <div id="apiResponse" style="background: #f8f9fa; padding: 20px; border-radius: 8px; font-family: monospace; white-space: pre-wrap; display: none;"></div>
            </div>
        </div>
    </div>
    
    <script>
        // 标签页切换
        function showTab(tabName) {{
            // 隐藏所有标签内容
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // 移除所有活跃标签
            const tabs = document.querySelectorAll('.nav-tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // 显示选中标签内容
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        // 多云成本分布图表
        const multiCloudCtx = document.getElementById('multiCloudChart').getContext('2d');
        const multiCloudChart = new Chart(multiCloudCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps([acc["provider"] for acc in self.demo_data["cloud_accounts"]])},
                datasets: [{{
                    data: {json.dumps([acc["monthly_cost"] for acc in self.demo_data["cloud_accounts"]])},
                    backgroundColor: ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // 团队预算图表
        const teamBudgetCtx = document.getElementById('teamBudgetChart').getContext('2d');
        const teamBudgetChart = new Chart(teamBudgetCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([team["team"] for team in self.demo_data["cost_allocation"]["team_allocations"]])},
                datasets: [{{
                    label: '预算',
                    data: {json.dumps([team["budget"] for team in self.demo_data["cost_allocation"]["team_allocations"]])},
                    backgroundColor: '#ecf0f1'
                }}, {{
                    label: '实际使用',
                    data: {json.dumps([team["allocated"] for team in self.demo_data["cost_allocation"]["team_allocations"]])},
                    backgroundColor: '#3498db'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return '$' + (value/1000).toFixed(0) + 'K';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // 单位经济学趋势图表
        const unitEconomicsCtx = document.getElementById('unitEconomicsChart').getContext('2d');
        const unitEconomicsChart = new Chart(unitEconomicsCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps([metric["metric"] for metric in self.demo_data["unit_economics"]])},
                datasets: [{{
                    label: '当前值',
                    data: {json.dumps([metric["current_value"] for metric in self.demo_data["unit_economics"]])},
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true
                }}, {{
                    label: '目标值',
                    data: {json.dumps([metric["target"] for metric in self.demo_data["unit_economics"]])},
                    borderColor: '#27ae60',
                    borderDash: [5, 5]
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // API测试功能
        function testApi(endpoint) {{
            const responseDiv = document.getElementById('apiResponse');
            responseDiv.style.display = 'block';
            responseDiv.textContent = '正在请求 ' + endpoint + '...';
            
            fetch(endpoint)
                .then(response => response.json())
                .then(data => {{
                    responseDiv.textContent = JSON.stringify(data, null, 2);
                }})
                .catch(error => {{
                    responseDiv.textContent = '错误: ' + error.message;
                }});
        }}
        
        // 实时数据更新
        function updateRealTimeData() {{
            // 模拟实时数据更新
            const indicators = document.querySelectorAll('.real-time-indicator');
            indicators.forEach(indicator => {{
                indicator.style.background = '#27ae60';
                setTimeout(() => {{
                    indicator.style.background = '#3498db';
                }}, 100);
            }});
        }}
        
        // 每30秒更新一次实时数据
        setInterval(updateRealTimeData, 30000);
        
        console.log('🚀 Enterprise Cloud Cost Analyzer - 完整版演示已加载');
        console.log('📊 包含功能: 多云管理、智能优化、单位经济学、成本分配、实时监控');
        console.log('🔌 API端点已就绪，可进行功能测试');
    </script>
</body>
</html>
"""
        return html_content
    
    def start_enterprise_server(self):
        """启动企业级演示服务器"""
        class EnterpriseHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.demo = kwargs.pop('demo')
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                if self.path == '/':
                    self.path = '/enterprise.html'
                
                # API 端点处理
                if self.path.startswith('/api/'):
                    self.handle_api_request()
                    return
                
                # 静态文件处理
                if self.path == '/enterprise.html':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    html_content = self.demo.create_enterprise_html()
                    self.wfile.write(html_content.encode('utf-8'))
                else:
                    super().do_GET()
            
            def handle_api_request(self):
                """处理API请求"""
                endpoint = self.path
                
                if endpoint in self.demo.api_responses:
                    response_data = self.demo.api_responses[endpoint].copy()
                    
                    # 添加实时时间戳
                    if 'timestamp' in response_data:
                        response_data['timestamp'] = time.time()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    json_response = json.dumps(response_data, default=str, ensure_ascii=False, indent=2)
                    self.wfile.write(json_response.encode('utf-8'))
                else:
                    # 404 响应
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_response = {{"error": "API endpoint not found", "path": endpoint}}
                    self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
            def log_message(self, format, *args):
                pass  # 禁用访问日志
        
        # 创建HTML文件
        html_content = self.create_enterprise_html()
        with open('enterprise.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🚀 启动企业级云成本分析平台完整演示...")
        print(f"📊 访问地址: http://localhost:{self.port}")
        print(f"🔌 API端点: http://localhost:{self.port}/api/health")
        print(f"⏹️  按 Ctrl+C 停止服务")
        
        # 启动HTTP服务器
        def handler_factory(*args, **kwargs):
            return EnterpriseHandler(*args, demo=self, **kwargs)
        
        try:
            httpd = HTTPServer(('localhost', self.port), handler_factory)
            
            # 自动打开浏览器
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{self.port}')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            httpd.serve_forever()
            
        except KeyboardInterrupt:
            print("\\n✅ 企业级演示服务已停止")
            httpd.shutdown()
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"❌ 端口 {self.port} 被占用，尝试使用端口 {self.port + 1}")
                self.port += 1
                self.start_enterprise_server()
            else:
                raise

if __name__ == "__main__":
    demo = EnterpriseDemo()
    demo.start_enterprise_server()