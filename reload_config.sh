#!/bin/bash

# GitHub自动提交系统 - 配置重载脚本
# 用于在不重启服务的情况下重新加载配置文件

SERVICE_NAME="github-auto-commit"
PID_FILE="/tmp/github-auto-commit.pid"

echo "🔄 GitHub自动提交系统 - 配置重载工具"
echo "========================================"

# 检查服务是否在运行
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "📡 检测到systemd服务正在运行，发送重载信号..."
    
    # 获取服务的主进程ID
    SERVICE_PID=$(systemctl show --property MainPID --value $SERVICE_NAME)
    
    if [ "$SERVICE_PID" != "0" ] && [ -n "$SERVICE_PID" ]; then
        echo "📋 向进程 $SERVICE_PID 发送SIGHUP信号..."
        kill -HUP $SERVICE_PID
        
        if [ $? -eq 0 ]; then
            echo "✅ 配置重载信号已发送成功"
            echo "📝 请查看服务日志确认配置是否重载成功:"
            echo "   sudo journalctl -u $SERVICE_NAME -f"
        else
            echo "❌ 发送重载信号失败"
            exit 1
        fi
    else
        echo "❌ 无法获取服务进程ID"
        exit 1
    fi
    
elif [ -f "$PID_FILE" ]; then
    echo "📡 检测到PID文件，发送重载信号..."
    
    PID=$(cat $PID_FILE)
    if kill -0 $PID 2>/dev/null; then
        echo "📋 向进程 $PID 发送SIGHUP信号..."
        kill -HUP $PID
        
        if [ $? -eq 0 ]; then
            echo "✅ 配置重载信号已发送成功"
        else
            echo "❌ 发送重载信号失败"
            exit 1
        fi
    else
        echo "❌ PID文件中的进程不存在，清理PID文件"
        rm -f $PID_FILE
        exit 1
    fi
    
else
    echo "❌ 服务未运行"
    echo "💡 请先启动服务:"
    echo "   sudo systemctl start $SERVICE_NAME"
    echo "   或者使用: ./start.sh"
    exit 1
fi

echo ""
echo "📖 使用说明:"
echo "• 配置重载后，新的定时任务将立即生效"
echo "• 如果配置有错误，系统会继续使用旧配置"
echo "• 建议修改配置前先备份原文件"
echo "• 可以通过以下命令查看当前配置状态:"
echo "   ./status.sh"