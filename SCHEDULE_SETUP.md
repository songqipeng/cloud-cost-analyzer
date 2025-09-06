# AWS费用分析器定时任务设置

## 🎯 定时任务配置

已成功配置每天早上8点自动运行AWS费用分析器！

### ⏰ 定时任务详情

- **执行时间**: 每天早上 8:00 AM
- **时区**: Asia/Shanghai (上海时间)
- **执行命令**: `python3 aws_cost_analyzer.py quick`
- **日志文件**: `/Users/songqipeng/learnpython/aws-cost-analyzer/cron.log`

### 📋 Cron任务配置

```bash
# AWS Cost Analyzer - Daily Analysis at 8:00 AM
0 8 * * * cd /Users/songqipeng/learnpython/aws-cost-analyzer && /opt/homebrew/bin/python3 aws_cost_analyzer.py quick >> /Users/songqipeng/learnpython/aws-cost-analyzer/cron.log 2>&1
```

### 🛠️ 管理命令

使用 `manage_schedule.sh` 脚本来管理定时任务：

```bash
# 查看定时任务状态
./manage_schedule.sh status

# 手动测试运行
./manage_schedule.sh test

# 查看日志
./manage_schedule.sh logs

# 重新安装定时任务
./manage_schedule.sh install

# 卸载定时任务
./manage_schedule.sh uninstall
```

### 📊 执行内容

每天早上8点，系统会自动：

1. **运行费用分析**: 分析过去1年的AWS费用数据
2. **生成报告**: 创建TXT和HTML格式的分析报告
3. **显示结果**: 在终端显示费用摘要、服务分析、区域分析
4. **记录日志**: 将所有输出保存到 `cron.log` 文件

### 📁 生成的文件

每次运行会在项目目录下生成：
- `cost_analysis_report_YYYYMMDD_HHMMSS.txt` - 文本格式报告
- `cost_analysis_report_YYYYMMDD_HHMMSS.html` - HTML格式报告
- `cron.log` - 定时任务执行日志

### 🔧 配置文件

定时任务配置存储在 `config.json` 中：

```json
{
  "schedule": {
    "enabled": true,
    "time": "08:00",
    "timezone": "Asia/Shanghai",
    "analysis_type": "quick",
    "auto_install": true,
    "cron_comment": "AWS Cost Analyzer - Daily Analysis"
  }
}
```

### 📧 通知功能

如果需要启用邮件或飞书通知，请编辑 `config.json` 文件中的通知配置：

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
    }
  }
}
```

### ⚠️ 注意事项

1. **系统权限**: 确保cron服务有权限访问项目目录
2. **Python路径**: 使用完整的Python路径 `/opt/homebrew/bin/python3`
3. **工作目录**: cron任务会切换到项目目录执行
4. **日志监控**: 定期查看 `cron.log` 确保任务正常执行
5. **AWS凭证**: 确保AWS凭证配置正确且有效

### 🔍 故障排除

如果定时任务没有执行：

1. 检查cron服务是否运行：`sudo launchctl list | grep cron`
2. 查看系统日志：`tail -f /var/log/system.log | grep cron`
3. 验证cron任务：`crontab -l`
4. 手动测试：`./manage_schedule.sh test`
5. 查看执行日志：`./manage_schedule.sh logs`

### 📅 下次执行时间

定时任务将在明天早上8:00首次自动执行。您可以通过以下命令手动测试：

```bash
./manage_schedule.sh test
```

## ✅ 设置完成

AWS费用分析器定时任务已成功配置！每天早上8点将自动运行并生成费用分析报告。
