#!/bin/bash

echo "�� 启动 AWS Cost Analyzer"
echo "========================"

# 检查虚拟环境是否存在
if [ ! -d "aws_cost_env" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv aws_cost_env
    echo "📦 安装依赖包..."
    source aws_cost_env/bin/activate
    pip install -r requirements.txt
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source aws_cost_env/bin/activate

# 运行程序
echo "🎯 启动 AWS Cost Analyzer..."
echo ""
./aws_cost_analyzer "$@"
