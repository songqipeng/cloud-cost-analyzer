# AWS费用分析器 - 配置说明

## 📋 配置方式

### 1. 交互式配置向导（推荐）
```bash
./aws_cost_analyzer.py setup
```
- 引导式配置，用户友好
- 支持多种邮件服务商选择
- 自动生成配置文件

### 2. 命令行配置
```bash
# 配置邮件通知
./aws_cost_analyzer.py setup --enable-email --email-provider gmail --sender-email your@gmail.com --recipient-email admin@company.com

# 配置飞书通知
./aws_cost_analyzer.py setup --enable-feishu --feishu-webhook https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# 配置定时任务
./aws_cost_analyzer.py setup --enable-schedule --schedule-time 09:00 --schedule-type quick
```

### 3. 手动编辑配置文件
程序使用 `config.json` 文件进行配置。首次使用时，请复制 `config.example.json` 为 `config.json` 并根据需要修改配置。

```bash
cp config.example.json config.json
```

## 🔧 配置项详解

### 1. 通知配置 (notifications)

#### 邮件通知 (email)
```json
{
  "notifications": {
    "email": {
      "enabled": true,                    // 是否启用邮件通知
      "smtp_server": "smtp.gmail.com",    // SMTP服务器地址
      "smtp_port": 587,                   // SMTP端口
      "sender_email": "your-email@gmail.com",  // 发送者邮箱
      "sender_password": "your-app-password",  // 邮箱密码或应用密码
      "recipient_email": "recipient@example.com", // 接收者邮箱
      "use_tls": true                     // 是否使用TLS加密
    }
  }
}
```

**支持的邮件服务商：**

#### Gmail
- **SMTP服务器**: smtp.gmail.com:587 (TLS)
- **配置步骤**:
  1. 启用两步验证
  2. 生成应用专用密码
  3. 使用应用密码作为 `sender_password`

#### QQ邮箱
- **SMTP服务器**: smtp.qq.com:587 (TLS)
- **配置步骤**:
  1. 登录QQ邮箱
  2. 设置 → 账户 → 开启SMTP服务
  3. 获取授权码作为 `sender_password`

#### Outlook
- **SMTP服务器**: smtp-mail.outlook.com:587 (TLS)
- **配置步骤**:
  1. 使用Microsoft账户密码
  2. 确保账户支持SMTP访问

#### 163邮箱
- **SMTP服务器**: smtp.163.com:25 或 smtp.163.com:994 (SSL)
- **配置步骤**:
  1. 登录163邮箱
  2. 设置 → POP3/SMTP/IMAP → 开启SMTP服务
  3. 获取客户端授权密码

#### 飞书通知 (feishu)
```json
{
  "notifications": {
    "feishu": {
      "enabled": true,                    // 是否启用飞书通知
      "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-token", // 飞书机器人Webhook URL
      "secret": "your-secret-key"         // 飞书机器人签名密钥（可选）
    }
  }
}
```

**飞书机器人配置步骤：**
1. 在飞书群中添加自定义机器人
2. 获取Webhook URL
3. 设置签名密钥（可选，用于安全验证）
4. 将URL和密钥填入配置

### 2. 定时任务配置 (schedule)

```json
{
  "schedule": {
    "enabled": true,                      // 是否启用定时任务
    "time": "09:00",                      // 执行时间 (24小时制)
    "timezone": "Asia/Shanghai",          // 时区
    "analysis_type": "quick",             // 分析类型: quick, custom
    "auto_install": true,                 // 是否自动安装系统级定时任务
    "cron_comment": "AWS Cost Analyzer - Daily Analysis"  // cron任务注释
  }
}
```

**时间格式说明：**
- 使用24小时制，格式：HH:MM
- 例如：09:00 (上午9点), 18:30 (下午6点30分)

**定时任务类型：**
- **系统级cron任务** (推荐): 使用系统cron，无需保持程序运行
- **程序内定时任务**: 需要保持程序运行，适合测试和调试

### 3. AWS配置 (aws)

```json
{
  "aws": {
    "default_region": "us-east-1",        // 默认AWS区域
    "cost_threshold": 0.01                // 费用过滤阈值（美元）
  }
}
```

## 🚀 使用示例

### 1. 启用邮件通知
```json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "sender_email": "your-email@gmail.com",
      "sender_password": "your-app-password",
      "recipient_email": "admin@company.com",
      "use_tls": true
    }
  }
}
```

### 2. 启用飞书通知
```json
{
  "notifications": {
    "feishu": {
      "enabled": true,
      "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "secret": "your-secret-key"
    }
  }
}
```

### 3. 启用定时任务
```json
{
  "schedule": {
    "enabled": true,
    "time": "09:00",
    "timezone": "Asia/Shanghai",
    "analysis_type": "quick"
  }
}
```

**安装和管理定时任务：**
```bash
# 安装系统级定时任务
./aws_cost_analyzer.py cron-install

# 查看定时任务状态
./aws_cost_analyzer.py cron-status

# 卸载定时任务
./aws_cost_analyzer.py cron-uninstall

# 自动安装（推荐，第一次运行时）
./aws_cost_analyzer.py schedule
```

## 📧 通知内容格式

### 邮件通知
- 使用HTML格式
- 包含费用摘要、服务分析、区域分析
- 支持附件（报告文件）

### 飞书通知
- 使用Markdown格式
- 包含费用摘要、服务分析、区域分析
- 支持富文本卡片样式

## ⚠️ 安全注意事项

1. **密码安全**：
   - 使用应用专用密码，不要使用主密码
   - 定期更换密码
   - 不要在代码中硬编码密码

2. **配置文件安全**：
   - 不要将包含真实密码的 `config.json` 提交到版本控制
   - 使用 `config.example.json` 作为模板
   - 在生产环境中使用环境变量或密钥管理服务

3. **网络安全**：
   - 确保SMTP服务器使用TLS加密
   - 验证飞书Webhook URL的有效性

## 🔍 故障排除

### 邮件发送失败
1. 检查SMTP服务器地址和端口
2. 确认邮箱密码或应用密码正确
3. 检查网络连接和防火墙设置
4. 确认邮箱服务商允许SMTP访问

### 飞书消息发送失败
1. 检查Webhook URL是否正确
2. 确认机器人已添加到群组
3. 检查签名密钥配置
4. 验证网络连接

### 定时任务不执行
1. 确认 `schedule.enabled` 为 `true`
2. 检查时间格式是否正确
3. 确认程序持续运行
4. 检查系统时区设置

## 📞 技术支持

如遇到配置问题，请：
1. 检查配置文件格式是否正确
2. 查看程序输出的错误信息
3. 参考本文档的故障排除部分
4. 提交Issue获取帮助
