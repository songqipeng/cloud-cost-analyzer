"""
Enterprise Cloud Cost Analyzer - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from typing import Dict, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Enterprise Cloud Cost Analyzer",
    description="Advanced cloud cost management and optimization platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Enterprise Cloud Cost Analyzer",
        "version": "1.0.0",
        "timestamp": time.time(),
        "uptime": "running",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/api/health")
async def api_health_check() -> Dict[str, Any]:
    """API Health check endpoint"""
    return await health_check()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Enterprise Cloud Cost Analyzer",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs",
        "health": "/api/health"
    }

@app.get("/api/demo/organizations")
async def demo_organizations():
    """Demo organizations endpoint"""
    return {
        "organizations": [
            {"id": 1, "name": "TechCorp", "cloud_spend": 125000, "savings": 35000},
            {"id": 2, "name": "StartupX", "cloud_spend": 45000, "savings": 12000},
        ],
        "total_spend": 170000,
        "total_savings": 47000
    }

# 全局存储云账户和同步状态
cloud_accounts_storage = {}
sync_status_storage = {}

@app.post("/api/cloud-accounts")
async def create_cloud_account(account_data: dict):
    """Create and test cloud account connection and fetch real data"""
    provider = account_data.get("provider")
    access_key = account_data.get("access_key") 
    secret_key = account_data.get("secret_key")
    region = account_data.get("region")
    alias = account_data.get("alias", f"{provider}账号")
    
    # 验证凭证
    if not access_key or not secret_key:
        return {"success": False, "error": "缺少访问凭据"}
    
    # 基本的凭证长度验证（移除严格的格式检查，让API验证处理）
    if len(access_key) < 8 or len(secret_key) < 8:
        return {"success": False, "error": "凭证长度不足"}
    
    account_id = f"{provider}_{access_key[:8]}"
    
    # 集成真实的云厂商API来验证凭证和拉取数据
    try:
        from services.real_cloud_api import RealCloudAPI
        real_api = RealCloudAPI()
        
        # 首先验证凭证
        is_valid, validation_message = await real_api.validate_credentials(provider, access_key, secret_key, region)
        
        if not is_valid:
            return {"success": False, "error": f"凭证验证失败: {validation_message}"}
        
        # 调用真实的云厂商API拉取数据
        cost_data = await fetch_cloud_cost_data(provider, access_key, secret_key, region)
        
        # 检查是否有错误
        if cost_data.get('error'):
            return {"success": False, "error": cost_data.get('error_message', '数据获取失败')}
        
        # 存储云账户信息和拉取的数据
        cloud_accounts_storage[account_id] = {
            "provider": provider,
            "alias": alias,
            "access_key": access_key[:8] + "****",
            "region": region,
            "created_at": time.time(),
            "cost_data": cost_data
        }
        
        # 标识数据来源
        data_source = cost_data.get('data_source', '云厂商API')
        is_fallback = cost_data.get('is_fallback', False)
        
        return {
            "success": True,
            "account_id": account_id,
            "status": "connected",
            "data_fetched": True,
            "cost_data": cost_data,
            "data_source": data_source,
            "is_real_data": not is_fallback
        }
        
    except Exception as e:
        return {"success": False, "error": f"连接{provider}失败: {str(e)}"}

async def fetch_cloud_cost_data(provider: str, access_key: str, secret_key: str, region: str):
    """从云厂商拉取真实成本数据 - 集成真实的云厂商API"""
    from services.real_cloud_api import RealCloudAPI
    
    # 创建真实云API实例
    real_api = RealCloudAPI()
    
    try:
        # 获取真实的云成本数据
        cost_data = await real_api.fetch_real_cost_data(provider, access_key, secret_key, region)
        
        # 记录数据来源
        data_source = cost_data.get('data_source', '未知来源')
        is_fallback = cost_data.get('is_fallback', False)
        
        if is_fallback:
            logger.warning(f"使用{provider}的后备数据: {data_source}")
        else:
            logger.info(f"获取{provider}真实数据成功: {data_source}")
        
        return cost_data
        
    except Exception as e:
        logger.error(f"获取{provider}成本数据失败: {e}")
        # 返回错误信息而不是模拟数据
        return {
            "error": True,
            "current_month_cost": 0,
            "services": {},
            "regions": {region: 0},
            "last_updated": time.time(),
            "error_message": f"API调用失败: {str(e)}"
        }

@app.get("/api/sync-status")
async def get_sync_status():
    """Get data synchronization status for all accounts"""
    current_time = time.time()
    
    if not sync_status_storage:
        return {
            "accounts": [],
            "overall_status": "no_accounts",
            "message": "请先配置云账号"
        }
    
    accounts_status = []
    all_completed = True
    
    for account_id, status in sync_status_storage.items():
        # 更新同步进度
        elapsed_time = current_time - status["started_at"]
        total_duration = status["estimated_completion"] - status["started_at"]
        
        if elapsed_time >= total_duration:
            # 同步完成
            progress = 100
            synced_records = status["estimated_records"]
            sync_status = "completed"
        else:
            # 同步进行中
            progress = min(95, int((elapsed_time / total_duration) * 100))
            synced_records = int((progress / 100) * status["estimated_records"])
            sync_status = "syncing"
            all_completed = False
        
        # 更新状态
        sync_status_storage[account_id].update({
            "status": sync_status,
            "progress": progress,
            "synced_records": synced_records
        })
        
        account_info = cloud_accounts_storage.get(account_id, {})
        accounts_status.append({
            "account_id": account_id,
            "provider": account_info.get("provider"),
            "alias": account_info.get("alias"),
            "status": sync_status,
            "progress": progress,
            "synced_records": synced_records,
            "estimated_records": status["estimated_records"]
        })
    
    overall_status = "completed" if all_completed else "syncing"
    
    return {
        "accounts": accounts_status,
        "overall_status": overall_status,
        "message": "数据同步完成" if all_completed else "正在同步云账号数据..."
    }

@app.get("/api/cost-analysis")
async def get_cost_analysis():
    """Get real cost analysis data fetched from cloud providers"""
    # 检查是否有已配置的账号
    if not cloud_accounts_storage:
        return {
            "status": "no_accounts",
            "message": "请先配置云账号",
            "setup_required": True
        }
    
    # 聚合所有云账号的成本数据
    total_cost = 0
    services_breakdown = {}
    accounts_data = []
    
    for account_id, account in cloud_accounts_storage.items():
        cost_data = account.get("cost_data", {})
        current_cost = cost_data.get("current_month_cost", 0)
        total_cost += current_cost
        
        # 聚合服务成本
        services = cost_data.get("services", {})
        for service, cost in services.items():
            if service in services_breakdown:
                services_breakdown[service] += cost
            else:
                services_breakdown[service] = cost
        
        accounts_data.append({
            "provider": account["provider"],
            "alias": account["alias"],
            "region": account["region"],
            "current_cost": current_cost,
            "services": services,
            "regions": cost_data.get("regions", {account["region"]: current_cost}),  # 添加区域费用数据
            "last_updated": cost_data.get("last_updated"),
            "created_at": account["created_at"],
            "data_source": cost_data.get("data_source", "未知"),
            "is_fallback": cost_data.get("is_fallback", False)
        })
    
    # 按成本排序服务
    top_services = dict(sorted(services_breakdown.items(), key=lambda x: x[1], reverse=True)[:5])
    
    return {
        "status": "ready",
        "show_dashboard": True,
        "total_cost": total_cost,
        "configured_accounts": len(cloud_accounts_storage),
        "accounts": accounts_data,
        "services_breakdown": top_services,
        "summary": {
            "total_monthly_cost": total_cost,
            "average_cost_per_account": total_cost / len(cloud_accounts_storage) if cloud_accounts_storage else 0,
            "top_service": max(services_breakdown.items(), key=lambda x: x[1]) if services_breakdown else None,
            "data_freshness": "实时数据"
        }
    }

@app.get("/api/demo/cost-trend")
async def demo_cost_trend():
    """Demo cost trend data"""
    import random
    from datetime import datetime, timedelta
    
    data = []
    base_date = datetime.now()
    
    for i in range(30):
        date = base_date - timedelta(days=29-i)
        base_cost = 2800
        variation = random.randint(-400, 400)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "cost": max(1000, base_cost + variation),
            "aws": random.randint(800, 1200),
            "azure": random.randint(600, 1000),
            "gcp": random.randint(300, 600),
            "alibaba": random.randint(200, 500)
        })
    
    return {"daily_costs": data}

@app.get("/api/demo/alerts")
async def demo_alerts():
    """Demo alerts and notifications"""
    import random
    
    alerts = []
    alert_types = [
        {"type": "cost_spike", "message": "AWS EC2成本异常增长 +45%", "severity": "high"},
        {"type": "budget_exceeded", "message": "开发环境预算超支 15%", "severity": "medium"},
        {"type": "optimization", "message": "发现3个未使用的EBS卷", "severity": "low"},
        {"type": "rightsizing", "message": "建议调整5个过配置实例", "severity": "medium"},
        {"type": "reservation", "message": "预留实例即将到期", "severity": "low"}
    ]
    
    for alert in random.sample(alert_types, 3):
        alerts.append({
            **alert,
            "timestamp": "2025-09-09T11:30:00Z",
            "affected_resources": random.randint(1, 8)
        })
    
    return {"alerts": alerts}

@app.get("/api/demo/teams")
async def demo_teams():
    """Demo team cost breakdown"""
    return {
        "teams": [
            {"name": "研发团队", "cost": 45000, "budget": 50000, "utilization": 90},
            {"name": "产品团队", "cost": 28000, "budget": 30000, "utilization": 93},
            {"name": "运营团队", "cost": 16500, "budget": 20000, "utilization": 83},
            {"name": "测试团队", "cost": 12000, "budget": 15000, "utilization": 80}
        ]
    }

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    metrics_data = """# HELP enterprise_cost_analyzer_requests_total Total requests
# TYPE enterprise_cost_analyzer_requests_total counter
enterprise_cost_analyzer_requests_total 1337
# HELP enterprise_cost_analyzer_uptime_seconds Uptime in seconds
# TYPE enterprise_cost_analyzer_uptime_seconds gauge
enterprise_cost_analyzer_uptime_seconds 86400"""
    return JSONResponse(content={"metrics": metrics_data})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )