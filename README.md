# 🌐 Cloud Cost Analyzer - 多云费用分析器

一个功能强大的多云费用分析工具，支持**AWS、阿里云、腾讯云、火山云**四大主流云平台的费用分析和对比。

## 🚀 功能特性

### 🌟 多云平台支持
- **AWS** - Amazon Web Services 费用分析
- **阿里云** - Alibaba Cloud 费用分析  
- **腾讯云** - Tencent Cloud 费用分析
- **火山云** - Volcengine (ByteDance) 费用分析

### 📊 强大的分析功能
- **快速分析** - 一键分析过去1年的费用
- **自定义时间范围** - 支持指定任意时间范围
- **多维度分析** - 按服务、区域、时间等维度分析费用
- **对比分析** - 直观对比不同云平台的费用分布
- **趋势分析** - 费用变化趋势和异常检测

### 🎨 丰富的输出格式
- **美观图表** - 生成专业的PNG图表和HTML仪表板
- **多格式报告** - 支持TXT、HTML等多种输出格式
- **命令行界面** - 支持参数化执行，无需交互
- **实时显示** - 使用Rich库创建专业的表格输出

### 🔔 智能通知系统
- **邮件通知** - 支持SMTP邮件发送分析报告
- **飞书通知** - 支持飞书机器人消息推送
- **定时任务** - 支持每日定时运行分析并发送通知

### 🛡️ 安全可靠
- **自动凭证检测** - 智能检测各云平台凭证配置
- **环境变量支持** - 优先使用环境变量存储敏感信息
- **权限最小化** - 只需要费用查询相关权限
- **错误处理** - 完善的错误处理和重试机制

---

## 📦 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/songqipeng/cloud-cost-analyzer.git
cd cloud-cost-analyzer

# 安装依赖
pip3 install -r requirements.txt
```

### 2. 配置API密钥

详细的API密钥获取指南请参考：[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)

#### 环境变量配置（推荐）

```bash
# AWS
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."

# 阿里云
export ALIBABA_CLOUD_ACCESS_KEY_ID="LTAI..."
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."

# 腾讯云
export TENCENTCLOUD_SECRET_ID="AKIDxxx..."
export TENCENTCLOUD_SECRET_KEY="..."

# 火山云
export VOLCENGINE_ACCESS_KEY_ID="AKLT..."
export VOLCENGINE_SECRET_ACCESS_KEY="..."
```

### 3. 运行分析

```bash
# 给程序添加执行权限
chmod +x cloud_cost_analyzer.py

# 查看帮助信息
./cloud_cost_analyzer.py help

# 多云费用分析
./cloud_cost_analyzer.py multi-cloud

# 检查连接状态
./cloud_cost_analyzer.py config
```

---

## 🔧 使用方法

### 基本命令

```bash
./cloud_cost_analyzer.py [命令] [选项]
```

### 可用命令

| 命令 | 描述 | 示例 |
|------|------|------|
| `quick` | 快速分析过去1年的AWS费用 | `./cloud_cost_analyzer.py quick` |
| `custom` | 自定义时间范围AWS分析 | `./cloud_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31` |
| `multi-cloud` | 多云费用分析 | `./cloud_cost_analyzer.py multi-cloud` |
| `config` | 配置检查 | `./cloud_cost_analyzer.py config` |
| `help` | 显示帮助信息 | `./cloud_cost_analyzer.py help` |

### 选项说明

#### 时间范围选项（用于 custom 命令）
- `--start DATE` - 开始日期 (YYYY-MM-DD)
- `--end DATE` - 结束日期 (YYYY-MM-DD)

#### 输出选项
- `--output DIR` - 指定输出目录 (默认: 当前目录)
- `--format FMT` - 输出格式: txt, html, all (默认: all)

### 使用示例

```bash
# 查看使用指南
./cloud_cost_analyzer.py

# AWS快速分析
./cloud_cost_analyzer.py quick

# AWS自定义时间范围分析
./cloud_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31

# 多云费用分析（所有平台）
./cloud_cost_analyzer.py multi-cloud

# 生成详细报告到指定目录
./cloud_cost_analyzer.py multi-cloud --output ./reports --format all

# 只生成文本报告
./cloud_cost_analyzer.py multi-cloud --format txt

# 检查所有云平台连接状态
./cloud_cost_analyzer.py config
```

---

## 🔑 API密钥配置

### 支持的云平台和权限要求

| 云平台 | 所需权限 | 配置方式 |
|--------|----------|----------|
| **AWS** | `ce:GetCostAndUsage`<br>`ce:GetDimensionValues`<br>`sts:GetCallerIdentity` | IAM用户 + Access Key |
| **阿里云** | `AliyunBSSReadOnlyAccess` | RAM用户 + AccessKey |
| **腾讯云** | `QcloudBillingReadOnlyAccess` | CAM子用户 + SecretId/Key |
| **火山云** | `BillingReadOnlyAccess` | 子用户 + AccessKey |

### 详细配置指南

每个云平台的详细API密钥获取步骤请参考：**[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)**

该指南包含：
- 🔧 详细的控制台操作步骤
- 🔐 权限配置说明
- 💡 安全最佳实践
- 🚨 常见问题排查
- 📊 使用场景说明

---

## ⚙️ 配置文件

### 配置文件位置
- 主配置文件：`config.json`
- 示例配置：`config.example.json`

### 完整配置示例

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
    "analysis_type": "multi-cloud",
    "auto_install": true,
    "cron_comment": "Cloud Cost Analyzer - Daily Analysis"
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
  "tencent": {
    "enabled": true,
    "default_region": "ap-beijing",
    "secret_id": "",
    "secret_key": "",
    "cost_threshold": 0.01
  },
  "volcengine": {
    "enabled": true,
    "default_region": "cn-beijing",
    "access_key_id": "",
    "secret_access_key": "",
    "cost_threshold": 0.01
  },
  "multi_cloud": {
    "enabled": true,
    "providers": ["aws", "aliyun", "tencent", "volcengine"],
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

---

## 📊 输出格式

### 多云分析报告包含

#### 1. 费用摘要表格
```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ 云平台       ┃       总费用 ┃  货币   ┃ 平均每日费用 ┃ 记录数 ┃     时间跨度 ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━┩
│ AWS          │        34.07 │   USD   │        17.03 │     18 │        32 天 │
│ 阿里云       │       125.50 │   CNY   │        62.75 │     24 │        30 天 │
│ 腾讯云       │        89.20 │   CNY   │        44.60 │     15 │        28 天 │
│ 火山云       │        67.80 │   CNY   │        33.90 │     12 │        25 天 │
└──────────────┴──────────────┴─────────┴──────────────┴────────┴──────────────┘
```

#### 2. 按服务分析
- 各云平台的服务费用排行
- 总费用、平均费用、记录数统计
- 支持服务名称本地化显示

#### 3. 按区域分析
- 各云平台的区域费用分布
- 支持AWS区域和中国云厂商区域

### 生成的文件

- **文本报告**: `multi_cloud_cost_analysis_YYYYMMDD_HHMMSS.txt`
- **HTML报告**: `multi_cloud_cost_analysis_YYYYMMDD_HHMMSS.html`
- **执行日志**: `cron.log` (定时任务)

---

## ⏰ 定时任务

### 设置每日自动多云分析

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天早上8点执行多云分析）
0 8 * * * cd /path/to/cloud-cost-analyzer && python3 cloud_cost_analyzer.py multi-cloud >> cron.log 2>&1
```

### 使用管理脚本

```bash
# 查看定时任务状态
./manage_schedule.sh status

# 手动测试运行
./manage_schedule.sh test

# 查看执行日志
./manage_schedule.sh logs
```

---

## 🎯 使用场景

### 1. 单云平台分析
```bash
# 只分析AWS
./cloud_cost_analyzer.py quick

# 自定义时间范围分析AWS
./cloud_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31
```

### 2. 多云对比分析
```bash
# 全平台费用对比
./cloud_cost_analyzer.py multi-cloud

# 生成详细报告
./cloud_cost_analyzer.py multi-cloud --format all --output ./reports
```

### 3. 连接状态检查
```bash
# 检查所有云平台连接状态
./cloud_cost_analyzer.py config

# 输出示例：
# ✅ AWS连接: 成功 - 账户ID: 123456789012
# ✅ 阿里云连接: 成功 - 账户余额: 1000.00 元
# ✅ 腾讯云连接: 成功 - 账户余额: 500.00 元
# ✅ 火山云连接: 成功 - 可用余额: 200.00 元
```

### 4. 混合云成本优化
- 对比不同云平台的服务价格
- 分析资源使用效率
- 识别费用异常和优化机会
- 制定多云成本管理策略

---

## 🛡️ 安全注意事项

### 🔒 密钥安全

1. **使用最小权限原则**
   - 只授予必要的费用查询权限
   - 避免授予写入或管理权限

2. **环境变量优先**
   ```bash
   # 推荐：使用环境变量
   export AWS_ACCESS_KEY_ID="..."
   
   # 避免：在配置文件中硬编码
   ```

3. **定期轮换密钥**
   - 建议每3-6个月更换一次API密钥
   - 及时删除不用的密钥

4. **配置文件保护**
   ```bash
   # 设置配置文件权限
   chmod 600 config.json
   
   # 添加到.gitignore
   echo "config.json" >> .gitignore
   ```

### 🌐 网络安全

1. **API调用频率限制**
   - 各云平台都有API调用频率限制
   - 程序已内置重试机制和频率控制

2. **区域选择**
   - 选择距离最近的区域以提高访问速度
   - 确保选择的区域支持计费API

---

## 🚨 故障排除

### 常见错误及解决方案

#### AWS相关
```
❌ 错误：AccessDenied
✅ 解决：检查IAM用户是否有ce:GetCostAndUsage权限

❌ 错误：InvalidUserID.NotFound  
✅ 解决：检查Access Key是否正确，是否已激活
```

#### 阿里云相关
```
❌ 错误：SignatureDoesNotMatch
✅ 解决：检查AccessKey Secret是否正确

❌ 错误：Forbidden.RAM
✅ 解决：检查RAM用户是否有BSS权限
```

#### 腾讯云相关
```
❌ 错误：AuthFailure.SignatureFailure
✅ 解决：检查SecretId和SecretKey是否正确

❌ 错误：UnauthorizedOperation
✅ 解决：检查用户是否有计费查询权限
```

#### 火山云相关
```
❌ 错误：InvalidAccessKeyId
✅ 解决：检查Access Key ID是否正确

❌ 错误：SignatureDoesNotMatch
✅ 解决：检查Secret Access Key是否正确
```

### 调试命令

```bash
# 详细日志输出
./cloud_cost_analyzer.py config 2>&1 | tee debug.log

# 测试单个平台连接
python3 -c "
from src.aws_cost_analyzer.core.aliyun_client import AliyunClient
client = AliyunClient()
print(client.test_connection())
"
```

---

## 🛠️ 技术栈

- **Python 3.8+**
- **AWS SDK (boto3)** - AWS费用分析
- **阿里云SDK** - 阿里云费用分析
- **腾讯云SDK** - 腾讯云费用分析
- **火山云SDK** - 火山云费用分析
- **pandas** - 数据处理和分析
- **matplotlib/seaborn** - 图表生成
- **rich** - 美观的终端输出
- **requests** - HTTP请求处理

---

## 📁 项目结构

```
cloud-cost-analyzer/
├── cloud_cost_analyzer.py          # 主程序入口
├── requirements.txt                 # Python依赖包
├── config.json                      # 配置文件（自动生成）
├── config.example.json              # 配置示例文件
├── API_KEYS_GUIDE.md               # API密钥获取指南
├── README.md                        # 项目说明文档
├── manage_schedule.sh               # 定时任务管理脚本
├── src/                            # 源代码目录
│   └── aws_cost_analyzer/          # 主包目录
│       ├── core/                   # 核心模块
│       │   ├── client.py           # AWS客户端
│       │   ├── aliyun_client.py    # 阿里云客户端
│       │   ├── tencent_client.py   # 腾讯云客户端
│       │   ├── volcengine_client.py # 火山云客户端
│       │   ├── multi_cloud_analyzer.py # 多云分析器
│       │   └── *_data_processor.py # 各平台数据处理器
│       ├── notifications/          # 通知模块
│       ├── reports/                # 报告生成模块
│       └── utils/                  # 工具模块
└── tests/                          # 测试文件
```

---

## 🎉 开始使用

1. **克隆项目**
   ```bash
   git clone https://github.com/songqipeng/cloud-cost-analyzer.git
   cd cloud-cost-analyzer
   ```

2. **安装依赖**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **配置API密钥**
   - 参考 [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) 获取各云平台API密钥
   - 使用环境变量或配置文件进行配置

4. **运行分析**
   ```bash
   # 检查连接
   ./cloud_cost_analyzer.py config
   
   # 开始多云分析
   ./cloud_cost_analyzer.py multi-cloud
   ```

5. **设置定时任务**（可选）
   ```bash
   # 每天早上8点自动运行
   crontab -e
   # 添加：0 8 * * * cd /path/to/cloud-cost-analyzer && python3 cloud_cost_analyzer.py multi-cloud >> cron.log 2>&1
   ```

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请：
1. 查看 [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) 获取详细配置指南
2. 检查日志文件获取错误详情
3. 提交Issue或联系开发者

---

## 🎯 下一步计划

- [ ] 汇率自动转换功能
- [ ] 更丰富的HTML报告和图表
- [ ] 费用预测和智能告警
- [ ] 更多云平台支持（华为云、百度云等）
- [ ] Web界面和API接口
- [ ] 容器化部署支持

---

**🌟 开始您的多云费用分析之旅！**

```bash
./cloud_cost_analyzer.py multi-cloud
```