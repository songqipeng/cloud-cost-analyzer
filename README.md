```

   ____ _                 _ _     _   _             
  / ___| | ___  _   _  __| | |__ | |_| |__   ___ _ __
 | |   | |/ _ \| | | |/ _` | '_ \| __| '_ \ / _ \ '__|
 | |___| | (_) | |_| | (_| | | | | |_| | | |  __/ |
  \____|_|\___/ \__,_|\__,_|_| |_|\__|_| |_|\___|_|

   ____           _        _   _                
  / ___|__ _  ___| | _____| |_| |__   ___ _ __
 | |   / _` |/ __| |/ / _ \ __| '_ \ / _ \ '__|
 | |__| (_| | (__|   <  __/ |_| | | |  __/ |
  \____\__,_|\___|_|\_\___|\__|_| |_|\___|_|

```

# ☁️ Cloud Cost Analyzer 🚀

[![Build Status](https://img.shields.io/github/actions/workflow/status/songqipeng/cloud-cost-analyzer/ci.yml?branch=main)](https://github.com/songqipeng/cloud-cost-analyzer/actions) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/cloud-cost-analyzer.svg)](https://pypi.org/project/cloud-cost-analyzer/)

一个功能强大的多云费用分析工具，支持 AWS、阿里云、腾讯云和火山引擎，帮助您轻松洞察和优化云成本。

---

## ✨ 主要特性

- **多云支持**: 一站式分析 AWS, 阿里云, 腾讯云, 火山引擎的费用数据。
- **多种报表**: 自动生成控制台摘要、TXT 和精美的 HTML 可视化报告。
- **异步执行**: 基于 `asyncio` 实现高性能的并发数据拉取。
- **配置灵活**: 通过 `config.json` 文件轻松配置通知、定时任务等高级功能。
- **定时任务**: 内置定时任务管理，可轻松实现每日自动分析。
- **易于扩展**: 代码结构清晰，方便添加新的云厂商支持。

---

## ⚙️ 安装与配置

### 1. 安装

无需虚拟环境，四步即可完成安装。

```bash
# 1. 克隆项目
git clone https://github.com/songqipeng/cloud-cost-analyzer.git

# 2. 进入目录
cd cloud-cost-analyzer

# 3. (推荐) 升级pip
python -m pip install --upgrade pip

# 4. 安装依赖
pip install -e .[dev]
```

### 2. 配置云平台凭证

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

> **权限要求**: 各平台仅需**只读**的账单访问权限，如 AWS 的 `ce:GetCostAndUsage`、阿里云的 `AliyunBSSReadOnlyAccess` 等。详情请参考 `API_KEYS_GUIDE.md`。

### 3. 高级配置文件 (可选)

若要使用邮件/飞书通知、定时任务等高级功能，请从 `config.example.json` 复制创建 `config.json` 并修改。

```bash
cp config.example.json config.json
```

---

## 🚀 快速使用

工具通过 `cloud-cost-analyzer` 命令进行调用。

### 1. 检查连接

在分析前，先检查所有云平台的连接状态。

```bash
cloud-cost-analyzer config-check
```

### 2. 执行多云分析

一键分析所有已配置云平台在过去30天的费用，并生成报告。

```bash
cloud-cost-analyzer multi-cloud --output ./reports --format all
```

### 3. 查看版本

```bash
cloud-cost-analyzer version
```

---

## 📚 命令参考

| 命令 | 描述 | 示例 |
| :--- | :--- | :--- |
| `config-check` | 检查所有云平台连接配置 | `cloud-cost-analyzer config-check` |
| `quick` | 快速分析AWS过去一年的费用 | `cloud-cost-analyzer quick` |
| `custom` | 自定义时间范围分析AWS | `... custom --start YYYY-MM-DD --end YYYY-MM-DD` |
| `multi-cloud` | 分析所有已配置的云平台 | `... multi-cloud --start YYYY-MM-DD` |
| `version` | 显示版本信息 | `cloud-cost-analyzer version` |

---

## 🤝 贡献

欢迎通过提交 Issue 和 Pull Request 来为这个项目做出贡献！

## 📄 许可证

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 发布。