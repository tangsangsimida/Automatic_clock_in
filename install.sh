#!/bin/bash
# -*- coding: utf-8 -*-

# GitHub自动提交系统安装脚本
# 适用于Ubuntu系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "检测到您正在使用root用户运行此脚本"
        log_warning "使用root用户可能会导致以下问题:"
        log_warning "1. 虚拟环境和配置文件的权限问题"
        log_warning "2. 普通用户无法正常使用和修改配置"
        log_warning "3. 安全风险增加"
        echo
        read -p "是否仍要继续安装? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "安装已取消。建议使用普通用户重新运行安装脚本。"
            exit 1
        fi
        log_warning "继续使用root用户安装..."
    fi
}

# 检查系统
check_system() {
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法检测操作系统"
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        log_warning "此脚本专为Ubuntu设计，但可能在其他发行版上运行。当前系统: $PRETTY_NAME"
        read -p "是否继续安装? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 安装依赖
install_dependencies() {
    log_info "正在安装系统依赖..."
    
    # 更新包列表
    sudo apt update
    
    # 安装Python3和pip
    sudo apt install -y python3 python3-pip python3-venv git
    
    log_success "系统依赖安装完成"
}

# 创建Python虚拟环境
setup_venv() {
    log_info "正在创建Python虚拟环境..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    VENV_DIR="$SCRIPT_DIR/venv"
    
    # 创建虚拟环境
    python3 -m venv "$VENV_DIR"
    
    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装Python依赖
    pip install requests schedule
    
    log_success "Python虚拟环境创建完成"
}

# 创建配置文件
setup_config() {
    log_info "正在设置配置..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 创建data目录
    mkdir -p "$SCRIPT_DIR/data"
    
    CONFIG_FILE="$SCRIPT_DIR/data/accounts_config.json"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        cat > "$CONFIG_FILE" << 'EOF'
[
  {
    "name": "account1",
    "username": "your_username_here",
    "email": "your_email@example.com",
    "token": "your_github_token_here",
    "repo": "auto-commit-repo",
    "commit_frequency": "daily",
    "enabled": true
  }
]
EOF
        
        log_warning "请编辑 $CONFIG_FILE 文件，填写您的GitHub信息"
        log_info "GitHub Token获取方法:"
        log_info "1. 访问 https://github.com/settings/tokens"
        log_info "2. 点击 'Generate new token (classic)'"
        log_info "3. 选择权限: repo, workflow"
        log_info "4. 复制生成的token到配置文件"
        
        read -p "按回车键继续..."
    else
        log_info "配置文件已存在: $CONFIG_FILE"
    fi
}

# 创建systemd服务
setup_systemd_service() {
    log_info "正在创建systemd服务..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SERVICE_NAME="github-auto-commit"
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    
    # 创建服务文件
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=GitHub Auto Commit Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/scheduler.py --daemon
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    sudo systemctl daemon-reload
    
    # 启用服务
    sudo systemctl enable "$SERVICE_NAME"
    
    log_success "systemd服务创建完成: $SERVICE_NAME"
}

# 创建crontab任务（备选方案）
setup_crontab() {
    log_info "正在设置crontab任务..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    CRON_SCRIPT="$SCRIPT_DIR/run_auto_commit.sh"
    
    # 创建运行脚本
    cat > "$CRON_SCRIPT" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
source venv/bin/activate
python scheduler.py --run-once
EOF
    
    chmod +x "$CRON_SCRIPT"
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "0 9,18 * * * $CRON_SCRIPT") | crontab -
    
    log_success "crontab任务设置完成"
}

# 创建管理脚本
create_management_scripts() {
    log_info "正在创建管理脚本..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # 创建启动脚本
    cat > "$SCRIPT_DIR/start.sh" << 'EOF'
#!/bin/bash

# GitHub自动提交系统启动脚本

SERVICE_NAME="github-auto-commit"

echo "🚀 GitHub自动提交系统启动脚本"
echo "===================================="

# 检查服务是否已经在运行
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ 服务已经在运行中"
    echo "📊 服务状态:"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    exit 0
fi

# 启动systemd服务
echo "🔄 正在启动systemd服务..."
sudo systemctl start $SERVICE_NAME

# 检查启动结果
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ 服务启动成功！"
    echo "📊 服务状态:"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    echo ""
    echo "💡 管理命令:"
    echo "  查看状态: ./status.sh"
    echo "  停止服务: ./stop.sh"
    echo "  重载配置: ./reload_config.sh"
    echo "  查看日志: sudo journalctl -u $SERVICE_NAME -f"
else
    echo "❌ 服务启动失败"
    echo "📋 错误信息:"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    exit 1
fi
EOF
    
    # 创建停止脚本
    cat > "$SCRIPT_DIR/stop.sh" << 'EOF'
#!/bin/bash

# GitHub自动提交系统停止脚本

SERVICE_NAME="github-auto-commit"
PID_FILE="/tmp/github-auto-commit.pid"

echo "🛑 GitHub自动提交系统停止脚本"
echo "===================================="

# 检查systemd服务是否在运行
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "🔄 正在停止systemd服务..."
    sudo systemctl stop $SERVICE_NAME
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "❌ systemd服务停止失败"
        exit 1
    else
        echo "✅ systemd服务已停止"
    fi
else
    echo "ℹ️  systemd服务未运行"
fi

# 检查是否有直接运行的进程
if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if kill -0 $PID 2>/dev/null; then
        echo "🔄 正在停止直接运行的进程 (PID: $PID)..."
        kill $PID
        sleep 2
        
        if kill -0 $PID 2>/dev/null; then
            echo "⚠️  进程未响应，强制终止..."
            kill -9 $PID
        fi
        
        rm -f $PID_FILE
        echo "✅ 直接运行的进程已停止"
    else
        echo "🧹 清理无效的PID文件"
        rm -f $PID_FILE
    fi
fi

echo "✅ 所有相关进程已停止"
EOF
    
    # 创建状态检查脚本
    cat > "$SCRIPT_DIR/status.sh" << 'EOF'
#!/bin/bash
echo "=== systemd服务状态 ==="
sudo systemctl status github-auto-commit
echo
echo "=== 最近日志 ==="
sudo journalctl -u github-auto-commit -n 20 --no-pager
EOF
    
    # 创建手动执行脚本
    cat > "$SCRIPT_DIR/run_once.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source venv/bin/activate
python scheduler.py --run-once
EOF

    # 创建直接启动脚本（备用方案）
    cat > "$SCRIPT_DIR/start_direct.sh" << 'EOF'
#!/bin/bash

# GitHub自动提交系统直接启动脚本（备用方案）
# 当systemd服务有问题时使用

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="/tmp/github-auto-commit.pid"
LOG_FILE="$SCRIPT_DIR/data/direct_run.log"

echo "🚀 GitHub自动提交系统直接启动脚本"
echo "======================================"
echo "⚠️  这是备用启动方案，建议优先使用 ./start.sh"
echo ""

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if kill -0 $PID 2>/dev/null; then
        echo "❌ 进程已在运行 (PID: $PID)"
        echo "💡 如需重启，请先运行: ./stop.sh"
        exit 1
    else
        echo "🧹 清理无效的PID文件"
        rm -f $PID_FILE
    fi
fi

# 检查systemd服务是否在运行
if systemctl is-active --quiet github-auto-commit; then
    echo "❌ systemd服务正在运行，请使用 ./stop.sh 停止后再使用直接启动"
    exit 1
fi

cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请重新运行安装脚本"
    exit 1
fi

echo "🔄 正在启动服务..."

# 启动服务并记录PID
source venv/bin/activate
nohup python scheduler.py --daemon > "$LOG_FILE" 2>&1 &
PID=$!

# 保存PID
echo $PID > "$PID_FILE"

# 等待一下检查是否启动成功
sleep 3

if kill -0 $PID 2>/dev/null; then
    echo "✅ 服务启动成功！(PID: $PID)"
    echo "📋 日志文件: $LOG_FILE"
    echo "📋 PID文件: $PID_FILE"
    echo ""
    echo "💡 管理命令:"
    echo "  停止服务: ./stop.sh"
    echo "  查看日志: tail -f $LOG_FILE"
    echo "  重载配置: ./reload_config.sh"
else
    echo "❌ 服务启动失败"
    rm -f "$PID_FILE"
    echo "📋 请检查日志: $LOG_FILE"
    exit 1
fi
EOF

    # 创建配置重载脚本
    cat > "$SCRIPT_DIR/reload_config.sh" << 'EOF'
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
EOF
    
    # 设置执行权限
    chmod +x "$SCRIPT_DIR"/*.sh
    
    log_success "管理脚本创建完成"
}

# 测试配置
test_configuration() {
    log_info "正在测试配置..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    cd "$SCRIPT_DIR"
    source venv/bin/activate
    
    # 测试配置
    if python -c "from config import validate_config; validate_config()"; then
        log_success "配置验证通过"
    else
        log_error "配置验证失败，请检查data/accounts_config.json文件"
        return 1
    fi
}

# 主安装流程
main() {
    echo "======================================"
    echo "    GitHub自动提交系统安装程序"
    echo "======================================"
    echo
    
    check_root
    check_system
    
    log_info "开始安装..."
    
    install_dependencies
    setup_venv
    setup_config
    
    # 询问用户选择服务类型
    echo
    log_info "请选择服务类型:"
    echo "1) systemd服务 (推荐)"
    echo "2) crontab任务"
    echo "3) 两者都安装"
    read -p "请选择 (1-3): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            setup_systemd_service
            ;;
        2)
            setup_crontab
            ;;
        3)
            setup_systemd_service
            setup_crontab
            ;;
        *)
            log_warning "无效选择，默认安装systemd服务"
            setup_systemd_service
            ;;
    esac
    
    create_management_scripts
    
    # 自动启动服务
    echo
    log_info "正在启动服务..."
    
    if sudo systemctl start github-auto-commit; then
        log_success "服务启动成功！"
        
        # 等待一下让服务完全启动
        sleep 2
        
        # 检查服务状态
        if systemctl is-active --quiet github-auto-commit; then
            log_success "服务运行正常"
        else
            log_warning "服务可能启动异常，请检查日志"
        fi
    else
        log_error "服务启动失败，请手动启动: sudo systemctl start github-auto-commit"
    fi
    
    echo
    log_success "安装完成！"
    echo
    log_info "下一步操作:"
    log_info "1. 编辑 data/accounts_config.json 文件，填写您的GitHub信息"
    log_info "2. 运行测试: ./run_once.sh"
    log_info "3. 重载配置: ./reload_config.sh (修改配置后)"
    log_info "4. 查看状态: ./status.sh"
    echo
    log_info "管理命令:"
    log_info "  启动服务: ./start.sh (推荐) 或 sudo systemctl start github-auto-commit"
    log_info "  停止服务: ./stop.sh 或 sudo systemctl stop github-auto-commit"
    log_info "  直接启动: ./start_direct.sh (备用方案，当systemd有问题时使用)"
    log_info "  重载配置: ./reload_config.sh (无需重启服务)"
    log_info "  查看状态: ./status.sh 或 sudo systemctl status github-auto-commit"
    log_info "  查看日志: sudo journalctl -u github-auto-commit -f"
    echo
    log_info "💡 配置热重载功能:"
    log_info "  • 修改配置文件后，系统会在30秒内自动检测并重载"
    log_info "  • 也可以手动执行 ./reload_config.sh 立即重载配置"
    log_info "  • 重载过程中服务不会中断，新配置立即生效"
    echo
}

# 运行主函数
main "$@"