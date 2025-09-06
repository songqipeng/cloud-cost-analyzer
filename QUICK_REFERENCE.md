# 🚀 Cloud Cost Analyzer - 快速参考

## 🎯 核心能力
- **🌍 多云支持**: AWS、阿里云、腾讯云、火山云
- **🔍 深度分析**: 服务→区域→资源级别下钻
- **🎨 可视化**: 交互式图表和现代化报告
- **💡 智能优化**: AI驱动的成本优化建议
- **🔔 自动化**: 定时分析和通知推送

## ⚡ 快速开始

### 1. 安装配置
```bash
# 克隆项目
git clone https://github.com/songqipeng/cloud-cost-analyzer.git
cd cloud-cost-analyzer

# 配置AWS凭证
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# 安装依赖 (如果需要)
pip3 install pandas plotly rich boto3
```

### 2. 基本使用
```bash
# 查看帮助
./cloud_cost_analyzer.py help

# 检查配置
./cloud_cost_analyzer.py config

# 快速分析AWS (推荐新手)
./cloud_cost_analyzer.py quick

# 多云分析
./cloud_cost_analyzer.py multi-cloud

# 自定义时间范围
./cloud_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31
```

### 3. 演示完整功能
```bash
# 运行增强版演示 (展示所有新功能)
python3 demo_enhanced_analyzer.py
```

## 📊 输出格式

### 命令行输出
- ✅ Rich库美化的表格和面板
- ✅ 彩色进度条和状态显示
- ✅ 费用摘要和异常提醒

### HTML报告
- ✅ 交互式Plotly图表
- ✅ 现代化响应式设计
- ✅ 多维度数据可视化
- ✅ 智能优化建议面板

### 文本报告
- ✅ 结构化费用数据
- ✅ 服务和区域统计
- ✅ 便于自动化处理

## 🎯 典型场景

| 场景 | 命令 | 用途 |
|------|------|------|
| **日常监控** | `./cloud_cost_analyzer.py quick --format html` | 每日费用检查，查看HTML报告 |
| **月度分析** | `./cloud_cost_analyzer.py custom --start 2024-11-01 --end 2024-11-30` | 详细月度费用分析 |
| **多云对比** | `./cloud_cost_analyzer.py multi-cloud` | 跨平台费用效率对比 |
| **成本优化** | `python3 demo_enhanced_analyzer.py` | 获取AI优化建议 |
| **自动化运维** | 设置crontab定时任务 | 定期生成报告 |

## 🔧 高级功能

### 资源级分析
```bash
# 运行演示查看资源级下钻功能
python3 demo_enhanced_analyzer.py
# 会显示具体的EC2实例、RDS实例等资源费用
```

### 异常检测
- 📊 自动识别费用异常波动
- 📈 基于统计学的异常检测算法
- ⚠️ 高亮显示异常日期和金额

### 智能优化建议
- 💰 预留实例购买建议
- ⚡ Spot实例使用建议
- 📏 实例规格优化建议
- 💾 存储类别优化建议
- 🎯 按优先级排序的行动计划

### 可视化图表
- 📈 费用趋势折线图 (带移动平均线)
- 🥧 服务费用分布饼图
- 📊 区域费用柱状图
- 🔥 资源费用热力图
- ⚡ 多指标综合仪表板

## 🔔 通知配置

编辑 `config.json` 文件：
```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "sender_email": "your-email@gmail.com"
    },
    "feishu": {
      "enabled": true,
      "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
    }
  }
}
```

## 🚨 故障排除

### 常见问题
1. **权限错误**: 确保AWS用户有Cost Explorer权限
2. **无数据**: 检查时间范围和区域设置
3. **图表不显示**: 确保网络能访问Plotly CDN

### 调试命令
```bash
# 检查连接状态
./cloud_cost_analyzer.py config

# 查看详细日志
./cloud_cost_analyzer.py quick 2>&1 | tee debug.log
```

## 📞 获取帮助
- 运行 `./cloud_cost_analyzer.py help` 查看完整帮助
- 查看 `API_KEYS_GUIDE.md` 了解密钥配置
- 运行 `python3 demo_enhanced_analyzer.py` 体验完整功能