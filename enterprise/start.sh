#!/bin/bash
# Enterprise Cloud Cost Analyzer - 启动脚本

set -e

echo "🚀 Enterprise Cloud Cost Analyzer 启动中..."
echo "================================================"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装Docker Desktop"
    echo "   下载地址: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未找到，请安装Docker Compose"
    echo "   或使用: docker compose (新版本)"
    exit 1
fi

# 检查环境文件
if [ ! -f .env ]; then
    echo "📋 创建环境配置文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，您可以根据需要修改配置"
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p storage
mkdir -p logs
mkdir -p .cache

# 启动服务
echo "🐳 启动Docker服务..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    docker compose ps
fi

echo ""
echo "✅ 服务启动完成!"
echo "================================================"
echo "🌐 Web Dashboard:    http://localhost:3000"
echo "📚 API Documentation: http://localhost:8000/api/docs"  
echo "📊 Grafana监控:      http://localhost:3001 (admin/admin123)"
echo "🔍 Prometheus:       http://localhost:9090"
echo "📈 Health Check:     http://localhost:8000/health"
echo "================================================"
echo ""
echo "💡 提示:"
echo "   • 首次启动可能需要几分钟来初始化数据库"
echo "   • 查看日志: docker-compose logs -f"
echo "   • 停止服务: docker-compose down"
echo ""
echo "🎉 享受您的企业级云成本分析平台！"