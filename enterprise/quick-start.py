#!/usr/bin/env python3
"""
Enterprise Cloud Cost Analyzer - Quick Start Demo
无需Docker的快速体验版本
"""
import json
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading

class QuickStartDemo:
    """快速启动演示"""
    
    def __init__(self):
        self.port = 8080
        self.demo_data = self._generate_demo_data()
    
    def _generate_demo_data(self):
        """生成演示数据"""
        return {
            "dashboard": {
                "total_cost": 237710,
                "cost_trend": 17.6,
                "efficiency": 78.5,
                "active_alerts": 7,
                "cloud_accounts": 15,
                "cost_by_service": [
                    {"name": "Compute (EC2)", "cost": 85420, "percentage": 35.9},
                    {"name": "Storage (S3)", "cost": 62340, "percentage": 26.2},
                    {"name": "Database (RDS)", "cost": 41250, "percentage": 17.4},
                    {"name": "Network", "cost": 28900, "percentage": 12.2},
                    {"name": "AI/ML", "cost": 19800, "percentage": 8.3}
                ]
            },
            "optimization": {
                "total_savings": 50100,
                "opportunities": [
                    {"type": "rightsizing", "savings": 12450, "resources": 45, "confidence": 92},
                    {"type": "idle_resources", "savings": 8960, "resources": 23, "confidence": 95},
                    {"type": "reserved_instances", "savings": 15230, "resources": 67, "confidence": 88},
                    {"type": "spot_instances", "savings": 7820, "resources": 34, "confidence": 78},
                    {"type": "storage_optimization", "savings": 5640, "resources": 156, "confidence": 85}
                ]
            },
            "unit_economics": [
                {"metric": "Cost per Customer", "value": 45.67, "trend": "down", "change": -8.2},
                {"metric": "Cost per Feature", "value": 1250.34, "trend": "up", "change": 5.1},
                {"metric": "Revenue per Dollar", "value": 3.45, "trend": "up", "change": 15.2}
            ]
        }
    
    def create_demo_html(self):
        """创建演示HTML页面"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Cloud Cost Analyzer - Demo</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }}
        .header {{
            background: rgba(255,255,255,0.95);
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        .container {{
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 10px;
        }}
        .metric-label {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        .metric-change {{
            margin-top: 10px;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .positive {{ background: #d5f4e6; color: #27ae60; }}
        .negative {{ background: #fadbd8; color: #e74c3c; }}
        .chart-container {{
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }}
        .chart-title {{
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        .optimization-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .optimization-table th,
        .optimization-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .optimization-table th {{
            background: #f8f9fa;
            color: #2c3e50;
            font-weight: bold;
        }}
        .savings {{
            color: #27ae60;
            font-weight: bold;
        }}
        .confidence {{
            padding: 4px 8px;
            border-radius: 10px;
            color: white;
            font-size: 0.9em;
        }}
        .confidence-high {{ background: #27ae60; }}
        .confidence-medium {{ background: #f39c12; }}
        .confidence-low {{ background: #e74c3c; }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .feature-card {{
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        .feature-icon {{
            font-size: 2em;
            margin-bottom: 15px;
        }}
        .cta-section {{
            text-align: center;
            margin: 50px 0;
            padding: 40px;
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        .cta-button {{
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            margin: 10px;
            transition: transform 0.3s ease;
        }}
        .cta-button:hover {{
            transform: scale(1.05);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Enterprise Cloud Cost Analyzer</h1>
        <p>第三阶段企业级云成本管理平台 - 产品演示</p>
    </div>
    
    <div class="container">
        <!-- 核心指标 -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">${{self.demo_data["dashboard"]["total_cost"]:,.0f}}</div>
                <div class="metric-label">月度总成本</div>
                <div class="metric-change positive">+{self.demo_data["dashboard"]["cost_trend"]}% vs 上期</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${{self.demo_data["optimization"]["total_savings"]:,.0f}}</div>
                <div class="metric-label">优化节省潜力</div>
                <div class="metric-change positive">21.1% 成本节省</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.demo_data["dashboard"]["efficiency"]}%</div>
                <div class="metric-label">成本效率分数</div>
                <div class="metric-change positive">+2.3% 本月改善</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.demo_data["dashboard"]["cloud_accounts"]}</div>
                <div class="metric-label">云账户数量</div>
                <div class="metric-change">跨7个云厂商</div>
            </div>
        </div>
        
        <!-- 成本分布图表 -->
        <div class="chart-container">
            <div class="chart-title">☁️ 多云成本分布</div>
            <canvas id="costChart" width="400" height="200"></canvas>
        </div>
        
        <!-- 优化建议 -->
        <div class="chart-container">
            <div class="chart-title">🤖 智能优化建议</div>
            <table class="optimization-table">
                <thead>
                    <tr>
                        <th>优化类型</th>
                        <th>影响资源</th>
                        <th>预期节省</th>
                        <th>置信度</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # 添加优化建议表格
        type_map = {
            "rightsizing": "资源右侧化",
            "idle_resources": "闲置资源清理", 
            "reserved_instances": "预留实例优化",
            "spot_instances": "竞价实例推荐",
            "storage_optimization": "存储优化"
        }
        
        for opp in self.demo_data["optimization"]["opportunities"]:
            confidence_class = "confidence-high" if opp["confidence"] >= 90 else "confidence-medium" if opp["confidence"] >= 80 else "confidence-low"
            html_content += f"""
                    <tr>
                        <td>{type_map.get(opp["type"], opp["type"])}</td>
                        <td>{opp["resources"]} 个资源</td>
                        <td class="savings">${opp["savings"]:,.0f}/月</td>
                        <td><span class="confidence {confidence_class}">{opp["confidence"]}%</span></td>
                    </tr>
"""
        
        html_content += f"""
                </tbody>
            </table>
        </div>
        
        <!-- 单位经济学 -->
        <div class="chart-container">
            <div class="chart-title">📈 单位经济学分析</div>
            <canvas id="unitEconomicsChart" width="400" height="200"></canvas>
        </div>
        
        <!-- 产品特性 -->
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">☁️</div>
                <h3>多云支持</h3>
                <p>支持AWS、Azure、GCP、阿里云、腾讯云等7大云厂商，独家亚洲云优势</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3>智能优化</h3>
                <p>AI驱动的成本优化引擎，自动识别并执行优化建议，平均节省30-50%成本</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>单位经济学</h3>
                <p>深度业务分析，跟踪每客户、每功能、每交易的成本和收入指标</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3>实时监控</h3>
                <p>30秒内异常检测，99.5%准确率，实时告警和自动化响应</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🏢</div>
                <h3>成本分配</h3>
                <p>94.7%分配准确率，支持多维度Chargeback和Showback报告</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <h3>企业安全</h3>
                <p>SOC2合规、RBAC权限、PII脱敏，满足企业级安全要求</p>
            </div>
        </div>
        
        <!-- 行动号召 -->
        <div class="cta-section">
            <h2>🚀 立即体验完整功能</h2>
            <p>这只是产品能力的一个简化演示。完整的企业级平台包含更多强大功能。</p>
            <a href="#" class="cta-button" onclick="showInstallGuide()">🐳 安装完整版本</a>
            <a href="#" class="cta-button" onclick="showArchitecture()">🏗️ 查看架构设计</a>
            <a href="#" class="cta-button" onclick="showBusinessValue()">💰 商业价值分析</a>
        </div>
    </div>
    
    <script>
        // 成本分布图表
        const costCtx = document.getElementById('costChart').getContext('2d');
        const costChart = new Chart(costCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps([item["name"] for item in self.demo_data["dashboard"]["cost_by_service"]])},
                datasets: [{{
                    data: {json.dumps([item["cost"] for item in self.demo_data["dashboard"]["cost_by_service"]])},
                    backgroundColor: [
                        '#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6'
                    ]
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
        
        // 单位经济学图表
        const ueCtx = document.getElementById('unitEconomicsChart').getContext('2d');
        const ueChart = new Chart(ueCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([item["metric"] for item in self.demo_data["unit_economics"]])},
                datasets: [{{
                    label: '当前值',
                    data: {json.dumps([item["value"] for item in self.demo_data["unit_economics"]])},
                    backgroundColor: ['#3498db', '#e74c3c', '#27ae60']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        function showInstallGuide() {{
            alert('安装指南:\\n\\n1. 安装Docker Desktop\\n2. 运行: docker-compose up -d\\n3. 访问: http://localhost:3000\\n\\n详细说明请查看README.md文件');
        }}
        
        function showArchitecture() {{
            alert('企业级架构特性:\\n\\n• 微服务架构 + API Gateway\\n• PostgreSQL + ClickHouse + Redis\\n• React 18 + FastAPI\\n• 异步处理 + 分层缓存\\n• Kubernetes + Docker部署');
        }}
        
        function showBusinessValue() {{
            alert('商业价值评估:\\n\\n• 开发投资: $775K (7个月)\\n• 收入潜力: $5-10M ARR\\n• 目标市场: $500M\\n• 定价策略: 1.5-2% 云支出\\n• 平均ROI: 400%+');
        }}
    </script>
</body>
</html>
"""
        return html_content
    
    def start_demo_server(self):
        """启动演示服务器"""
        # 创建HTML文件
        html_content = self.create_demo_html()
        with open('demo.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🚀 启动企业级云成本分析平台演示...")
        print(f"📊 访问地址: http://localhost:{self.port}/demo.html")
        print(f"⏹️  按 Ctrl+C 停止服务")
        
        # 启动HTTP服务器
        class DemoHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # 禁用日志
        
        try:
            httpd = HTTPServer(('localhost', self.port), DemoHandler)
            
            # 自动打开浏览器
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{self.port}/demo.html')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            httpd.serve_forever()
            
        except KeyboardInterrupt:
            print("\\n✅ 演示服务已停止")
            httpd.shutdown()

if __name__ == "__main__":
    demo = QuickStartDemo()
    demo.start_demo_server()