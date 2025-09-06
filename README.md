# ☁️ Cloud Cost Analyzer 使用指南 🚀

一个功能强大的多云费用分析工具，支持 AWS、阿里云、腾讯云和火山引擎，帮助您轻松洞察和优化云成本。

## ✨ 主要特性

- **多云支持**: 一站式分析 AWS, 阿里云, 腾讯云, 火山引擎的费用数据。
- **多种报表**: 自动生成控制台摘要、TXT 和精美的 HTML 可视化报告。
- **异步执行**: 基于 `asyncio` 实现高性能的并发数据拉取。
- **配置灵活**: 通过 `config.json` 文件轻松配置通知、定时任务等高级功能。
- **定时任务**: 内置定时任务管理，可轻松实现每日自动分析。
- **易于扩展**: 代码结构清晰，方便添加新的云厂商支持。

## ⚙️ 安装与环境准备

### 1. 环境要求

- Python 3.8+

### 2. 克隆并安装

```bash
# 克隆项目
git clone https://github.com/songqipeng/cloud-cost-analyzer.git
cd cloud-cost-analyzer

# (推荐) 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# 安装依赖
pip install -e .[dev]
```

## 🔑 配置

### 1. 云平台凭证

推荐使用环境变量来配置云平台的访问凭证。这是最安全、最灵活的方式。

```bash
# --- AWS ---
export AWS_ACCESS_KEY_ID="Your_AWS_Access_Key_ID"
export AWS_SECRET_ACCESS_KEY="Your_AWS_Secret_Access_Key"
export AWS_DEFAULT_REGION="us-east-1"

# --- 阿里云 ---
export ALIBABA_CLOUD_ACCESS_KEY_ID="Your_Aliyun_Access_Key_ID"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="Your_Aliyun_Access_Key_Secret"

# --- 腾讯云 ---
export TENCENTCLOUD_SECRET_ID="Your_Tencent_Secret_Id"
export TENCENTCLOUD_SECRET_KEY="Your_Tencent_Secret_Key"

# --- 火山引擎 ---
export VOLCENGINE_ACCESS_KEY_ID="Your_Volcengine_Access_Key_ID"
export VOLCENGINE_SECRET_ACCESS_KEY="Your_Volcengine_Secret_Access_Key"
```

**所需API权限:**
- **AWS**: `ce:GetCostAndUsage`, `ce:GetDimensionValues`
- **阿里云**: `AliyunBSSReadOnlyAccess`
- **腾讯云**: `QcloudBillingReadOnlyAccess`
- **火山引擎**: `BillingReadOnlyAccess`

更多详情请参考 [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md)。

### 2. 高级配置文件 (可选)

要使用通知、定时任务等高级功能，您需要创建一个 `config.json` 文件。

1.  复制示例文件：
    ```bash
    cp config.example.json config.json
    ```
2.  根据需要编辑 `config.json` 文件：

    ```json
    {
      "notifications": {
        "email": {
          "enabled": true,
          "smtp_server": "smtp.example.com",
          "smtp_port": 587,
          "sender_email": "your-email@example.com",
          "sender_password": "your-app-password",
          "recipient_email": "recipient@example.com",
          "use_tls": true
        },
        "feishu": {
          "enabled": true,
          "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-token",
          "secret": "your-feishu-bot-secret"
        }
      },
      "schedule": {
        "enabled": true,
        "time": "09:00",
        "timezone": "Asia/Shanghai",
        "analysis_type": "quick",
        "auto_install": true,
        "cron_comment": "Cloud Cost Analyzer - Daily Analysis"
      },
      "aws": {
        "default_region": "us-east-1",
        "cost_threshold": 0.01
      }
    }
    ```

## 🚀 使用方法

工具通过 `cloud-cost-analyzer` 命令进行调用。

### 1. 检查配置与连接

在开始分析前，建议先检查所有云平台的连接状态。

```bash
cloud-cost-analyzer config-check
```

### 2. 快速分析 (AWS)

对AWS在过去一年的费用进行快速分析。

```bash
cloud-cost-analyzer quick
```

### 3. 自定义分析 (AWS)

对AWS在指定时间范围内的费用进行分析，并生成报告。

```bash
cloud-cost-analyzer custom --start 2024-01-01 --end 2024-01-31 --output ./reports --format all
```

- `--output`: 指定报告输出目录。
- `--format`: 指定报告格式 (`txt`, `html`, `all`)。

### 4. 多云分析

对所有已配置的云平台进行费用分析。

```bash
# 分析过去30天的费用
cloud-cost-analyzer multi-cloud

# 指定时间范围和输出
cloud-cost-analyzer multi-cloud --start 2024-01-01 --end 2024-01-31 --output ./reports
```

### 5. 查看版本

```bash
cloud-cost-analyzer version
```

## ⏰ 定时任务

您可以通过 `manage_schedule.sh` 脚本轻松管理定时分析任务（基于 `cron`）。

1.  **添加或更新定时任务**

    (请先确保 `config.json` 中的 `schedule` 部分已启用并配置正确)

    ```bash
    ./manage_schedule.sh install
    ```

2.  **查看当前任务**

    ```bash
    ./manage_schedule.sh view
    ```

3.  **移除定时任务**

    ```bash
    ./manage_schedule.sh uninstall
    ```

## 📄 输出示例

### 控制台输出

```
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┓
┃ 云平台 ┃ 总费用   ┃ 货币    ┃ 平均每日费用 ┃ 记录数  ┃ 时间跨度 ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│ AWS    │ 34.07    │ USD     │ 17.03        │ 150     │ 30 天    │
│ 阿里云 │ 125.50   │ CNY     │ 62.75        │ 200     │ 30 天    │
└────────┴──────────┴─────────┴──────────────┴─────────┴──────────┘
```

### HTML 报告

HTML 报告会生成在指定的 `--output` 目录下，包含交互式图表，非常直观。

![HTML Report Screenshot](https://raw.githubusercontent.com/songqipeng/cloud-cost-analyzer/main/assets/report_screenshot.png)  
*(请将此处的截图链接替换为您自己的项目截图)*
