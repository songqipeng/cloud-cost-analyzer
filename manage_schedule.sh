#!/bin/bash
# AWS Cost Analyzer 定时任务管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="/opt/homebrew/bin/python3"
CRON_FILE="$SCRIPT_DIR/aws_analyzer_cron.txt"
LOG_FILE="$SCRIPT_DIR/cron.log"

case "$1" in
    "install")
        echo "安装每天早上8点的定时任务..."
        echo "# AWS Cost Analyzer - Daily Analysis at 8:00 AM" > "$CRON_FILE"
        echo "0 8 * * * cd $SCRIPT_DIR && $PYTHON_PATH aws_cost_analyzer.py quick >> $LOG_FILE 2>&1" >> "$CRON_FILE"
        crontab "$CRON_FILE"
        echo "✅ 定时任务已安装"
        ;;
    "uninstall")
        echo "卸载定时任务..."
        crontab -r 2>/dev/null || echo "没有找到现有的定时任务"
        echo "✅ 定时任务已卸载"
        ;;
    "status")
        echo "当前定时任务状态:"
        echo "===================="
        crontab -l 2>/dev/null || echo "没有安装定时任务"
        echo ""
        echo "日志文件位置: $LOG_FILE"
        if [ -f "$LOG_FILE" ]; then
            echo "最近的日志 (最后10行):"
            tail -10 "$LOG_FILE"
        else
            echo "还没有日志文件"
        fi
        ;;
    "test")
        echo "测试运行AWS费用分析器..."
        cd "$SCRIPT_DIR"
        $PYTHON_PATH aws_cost_analyzer.py quick
        echo "✅ 测试完成"
        ;;
    "logs")
        if [ -f "$LOG_FILE" ]; then
            echo "显示完整日志:"
            cat "$LOG_FILE"
        else
            echo "日志文件不存在: $LOG_FILE"
        fi
        ;;
    *)
        echo "AWS Cost Analyzer 定时任务管理"
        echo "用法: $0 {install|uninstall|status|test|logs}"
        echo ""
        echo "命令说明:"
        echo "  install   - 安装每天早上8点的定时任务"
        echo "  uninstall - 卸载定时任务"
        echo "  status    - 查看定时任务状态和最近日志"
        echo "  test      - 手动测试运行一次"
        echo "  logs      - 查看完整日志"
        ;;
esac
