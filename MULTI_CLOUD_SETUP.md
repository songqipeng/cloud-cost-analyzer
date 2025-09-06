# 多云费用分析器设置指南

## 🌐 多云支持概述

AWS费用分析器现已支持多云平台费用分析，可以同时分析AWS和阿里云的费用数据！

### ✨ 新增功能

- **🔄 多云分析**: 同时分析AWS和阿里云费用
- **📊 统一报告**: 生成包含多个云平台的综合报告
- **🔍 对比分析**: 直观对比不同云平台的费用分布
- **⚙️ 灵活配置**: 支持单独或组合使用不同云平台

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装阿里云SDK（已包含在requirements.txt中）
pip3 install -r requirements.txt
```

### 2. 配置阿里云凭证

有两种方式配置阿里云凭证：

#### 方式一：环境变量（推荐）

```bash
# 设置阿里云凭证环境变量
export ALIBABA_CLOUD_ACCESS_KEY_ID="your_access_key_id"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your_access_key_secret"
```

#### 方式二：配置文件

编辑 `config.json` 文件：

```json
{
  "aliyun": {
    "enabled": true,
    "default_region": "cn-hangzhou",
    "access_key_id": "your_access_key_id",
    "access_key_secret": "your_access_key_secret",
    "cost_threshold": 0.01
  }
}
```

### 3. 运行多云分析

```bash
# 多云费用分析
python3 aws_cost_analyzer.py multi-cloud

# 只生成文本报告
python3 aws_cost_analyzer.py multi-cloud --format txt

# 指定输出目录
python3 aws_cost_analyzer.py multi-cloud --output ./reports
```

## 📋 可用命令

### 原有命令（AWS专用）

```bash
# AWS快速分析
python3 aws_cost_analyzer.py quick

# AWS自定义时间范围分析
python3 aws_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31
```

### 新增命令（多云）

```bash
# 多云费用分析
python3 aws_cost_analyzer.py multi-cloud

# 配置检查（包含AWS和阿里云连接测试）
python3 aws_cost_analyzer.py config
```

## ⚙️ 配置详解

### 完整配置文件示例

```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "sender_email": "your-email@gmail.com",
      "sender_password": "your-app-password",
      "recipient_email": "recipient@example.com",
      "use_tls": true
    },
    "feishu": {
      "enabled": true,
      "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
      "secret": "your-secret-key"
    }
  },
  "schedule": {
    "enabled": true,
    "time": "08:00",
    "timezone": "Asia/Shanghai",
    "analysis_type": "quick",
    "auto_install": true,
    "cron_comment": "AWS Cost Analyzer - Daily Analysis"
  },
  "aws": {
    "default_region": "us-east-1",
    "cost_threshold": 0.01
  },
  "aliyun": {
    "enabled": true,
    "default_region": "cn-hangzhou",
    "access_key_id": "",
    "access_key_secret": "",
    "cost_threshold": 0.01
  },
  "multi_cloud": {
    "enabled": true,
    "providers": ["aws", "aliyun"],
    "currency_conversion": {
      "enabled": false,
      "base_currency": "USD",
      "exchange_rates": {
        "CNY": 7.2
      }
    }
  }
}
```

### 配置项说明

#### AWS配置 (aws)
- `default_region`: 默认AWS区域
- `cost_threshold`: 费用过滤阈值（美元）

#### 阿里云配置 (aliyun)
- `enabled`: 是否启用阿里云分析
- `default_region`: 默认阿里云区域
- `access_key_id`: 阿里云AccessKey ID
- `access_key_secret`: 阿里云AccessKey Secret
- `cost_threshold`: 费用过滤阈值（人民币）

#### 多云配置 (multi_cloud)
- `enabled`: 是否启用多云分析
- `providers`: 启用的云平台列表
- `currency_conversion`: 汇率转换配置（暂未实现）

## 🔑 获取阿里云凭证

### 1. 登录阿里云控制台

访问 [阿里云控制台](https://ecs.console.aliyun.com/)

### 2. 创建AccessKey

1. 点击右上角头像 → 访问控制
2. 用户管理 → 创建用户
3. 为用户添加权限：
   - `AliyunBSSFullAccess` - 费用中心完全访问权限
   - `AliyunBSSReadOnlyAccess` - 费用中心只读权限（推荐）

### 3. 获取AccessKey

1. 在用户列表中找到创建的用户
2. 点击"创建AccessKey"
3. 保存AccessKey ID和AccessKey Secret

## 📊 输出格式

### 多云分析报告包含

1. **费用摘要表格**
   - 各云平台总费用对比
   - 货币单位显示（USD/CNY）
   - 平均每日费用
   - 记录数和时间跨度

2. **按服务分析**
   - 各云平台的服务费用排行
   - 总费用、平均费用、记录数

3. **按区域分析**
   - 各云平台的区域费用分布
   - 支持AWS区域和阿里云区域

### 生成的文件

- `multi_cloud_cost_analysis_YYYYMMDD_HHMMSS.txt` - 文本格式报告
- `multi_cloud_cost_analysis_YYYYMMDD_HHMMSS.html` - HTML格式报告（开发中）

## 🔧 故障排除

### 常见问题

#### 1. 阿里云连接失败

**问题**: `❌ 阿里云连接: 阿里云凭证未配置`

**解决方案**:
- 检查环境变量是否正确设置
- 确认config.json中的凭证配置
- 验证AccessKey是否有效

#### 2. 权限不足

**问题**: 阿里云API调用失败

**解决方案**:
- 确认用户有BSS（费用中心）访问权限
- 检查AccessKey是否激活
- 验证账户是否有费用数据

#### 3. 网络连接问题

**问题**: 连接阿里云API超时

**解决方案**:
- 检查网络连接
- 确认防火墙设置
- 尝试使用不同的阿里云区域

### 调试命令

```bash
# 检查连接状态
python3 aws_cost_analyzer.py config

# 查看详细日志
python3 aws_cost_analyzer.py multi-cloud --format txt 2>&1 | tee debug.log
```

## 🕐 定时任务

多云分析也支持定时任务！

### 更新定时任务为多云分析

```bash
# 编辑定时任务
crontab -e

# 将原来的命令改为多云分析
0 8 * * * cd /Users/songqipeng/learnpython/aws-cost-analyzer && /opt/homebrew/bin/python3 aws_cost_analyzer.py multi-cloud >> /Users/songqipeng/learnpython/aws-cost-analyzer/cron.log 2>&1
```

### 使用管理脚本

```bash
# 卸载现有任务
./manage_schedule.sh uninstall

# 手动编辑cron文件，将quick改为multi-cloud
vim aws_analyzer_cron.txt

# 重新安装
./manage_schedule.sh install
```

## 📈 使用建议

### 1. 渐进式部署

1. **第一步**: 先配置AWS，确保正常工作
2. **第二步**: 添加阿里云凭证，测试连接
3. **第三步**: 运行多云分析，验证结果
4. **第四步**: 更新定时任务为多云模式

### 2. 安全最佳实践

- 使用环境变量存储凭证
- 定期轮换AccessKey
- 使用最小权限原则
- 不要在代码中硬编码凭证

### 3. 成本优化

- 设置合理的费用阈值过滤小额费用
- 定期分析费用趋势
- 关注异常费用增长
- 对比不同云平台的成本效益

## 🎯 下一步计划

- [ ] 汇率自动转换功能
- [ ] 更丰富的HTML报告
- [ ] 费用预测和告警
- [ ] 更多云平台支持（腾讯云、华为云等）
- [ ] 图表可视化增强

## ✅ 设置完成

恭喜！您的AWS费用分析器现在已支持多云分析。可以同时监控AWS和阿里云的费用了！🎉

如有问题，请查看日志文件或提交Issue。
