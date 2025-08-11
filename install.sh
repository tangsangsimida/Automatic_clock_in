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
    ENV_FILE="$SCRIPT_DIR/.env"
    
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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source venv/bin/activate
python scheduler.py --daemon
EOF
    
    # 创建停止脚本
    cat > "$SCRIPT_DIR/stop.sh" << 'EOF'
#!/bin/bash
sudo systemctl stop github-auto-commit
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
    
    echo
    log_success "安装完成！"
    echo
    log_info "下一步操作:"
    log_info "1. 编辑 data/accounts_config.json 文件，填写您的GitHub信息"
    log_info "2. 运行测试: ./run_once.sh"
    log_info "3. 启动服务: sudo systemctl start github-auto-commit"
    log_info "4. 查看状态: ./status.sh"
    echo
    log_info "管理命令:"
    log_info "  启动服务: sudo systemctl start github-auto-commit"
    log_info "  停止服务: sudo systemctl stop github-auto-commit"
    log_info "  查看状态: sudo systemctl status github-auto-commit"
    log_info "  查看日志: sudo journalctl -u github-auto-commit -f"
    echo
}

# 运行主函数
main "$@"