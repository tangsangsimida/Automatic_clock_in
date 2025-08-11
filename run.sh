#!/bin/bash
# -*- coding: utf-8 -*-

# GitHub自动提交系统启动脚本

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

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查虚拟环境
check_venv() {
    if [[ ! -d "venv" ]]; then
        log_warning "虚拟环境不存在，正在创建..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        log_success "虚拟环境创建完成"
    fi
}

# 检查配置文件
check_config() {
    if [[ ! -f ".env" ]]; then
        log_warning "配置文件不存在，正在创建模板..."
        cat > ".env" << 'EOF'
# GitHub配置
# 请填写您的GitHub信息
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_username_here
GITHUB_EMAIL=your_email@example.com
GITHUB_REPO=auto-commit-repo
EOF
        log_error "请编辑 .env 文件，填写您的GitHub信息后重新运行"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "GitHub自动打卡系统 - 使用说明"
    echo ""
    echo "用法: $0 [选项] [参数]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -i, --install           安装系统依赖和设置环境"
    echo "  -r, --run-once [账号]   立即执行一次提交任务"
    echo "  -d, --daemon            以守护进程模式运行"
    echo "  -s, --status            显示服务状态"
    echo "  -t, --test              测试配置和连接"
    echo "  --interactive           交互式配置模式"
    echo "  --list-accounts         列出所有账号配置"
    echo "  --create-config         创建多账号配置模板"
    echo "  --validate-config       验证配置文件"
    echo ""
    echo "多账号管理:"
    echo "  --add-account           添加新账号配置"
    echo "  --edit-account [名称]   编辑指定账号配置"
    echo "  --disable-account [名称] 禁用指定账号"
    echo "  --enable-account [名称]  启用指定账号"
    echo ""
    echo "示例:"
    echo "  $0 --install            # 安装并配置系统"
    echo "  $0 --run-once           # 立即执行所有账号"
    echo "  $0 --run-once account1  # 立即执行指定账号"
    echo "  $0 --daemon             # 启动守护进程"
    echo "  $0 --test               # 测试配置"
    echo "  $0 --create-config      # 创建多账号配置模板"
    echo ""
}

# 安装依赖
install_deps() {
    log_info "正在安装依赖..."
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
    
    # 创建虚拟环境
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "依赖安装完成"
}

# 测试配置
test_config() {
    log_info "开始测试配置..."
    
    if [[ ! -f ".env" ]]; then
        log_error "配置文件不存在: .env"
        return 1
    fi
    
    source .env
    source venv/bin/activate
    
    # 运行测试脚本
    if [[ -f "test.py" ]]; then
        log_info "运行配置测试..."
        python3 test.py
    else
        log_info "运行基本配置验证..."
        python3 -c "from config import validate_config; validate_config(); print('✅ 配置验证通过')"
    fi
}

# 列出所有账号
list_accounts() {
    log_info "账号配置列表:"
    source venv/bin/activate
    python3 -c "
from config import load_accounts_config
try:
    accounts = load_accounts_config()
    for i, account in enumerate(accounts, 1):
        status = '✅ 启用' if account.get('enabled', True) else '❌ 禁用'
        frequency = account.get('commit_frequency', 'daily')
        times = ', '.join(account.get('commit_times', []))
        print(f'{i}. {account["name"]} ({status})')
        print(f'   用户: {account["username"]}')
        print(f'   仓库: {account["repo"]}')
        print(f'   频率: {frequency}')
        print(f'   时间: {times}')
        print()
except Exception as e:
    print(f'❌ 加载账号配置失败: {e}')
"
}

# 创建配置模板
create_config_template() {
    log_info "创建多账号配置模板..."
    source venv/bin/activate
    python3 -c "
from config import create_accounts_config_template
import os
try:
    template_file = create_accounts_config_template()
    print(f'✅ 配置模板已创建: {template_file}')
    print('请编辑此文件，填入您的GitHub账号信息')
except Exception as e:
    print(f'❌ 创建模板失败: {e}')
"
}

# 验证配置
validate_config_file() {
    log_info "验证配置文件..."
    source venv/bin/activate
    python3 -c "
from config import validate_config
try:
    validate_config()
    print('✅ 配置验证通过')
except Exception as e:
    print(f'❌ 配置验证失败: {e}')
"
}

# 添加账号配置
add_account() {
    log_info "添加新账号配置..."
    
    echo "请输入账号信息:"
    read -p "账号名称: " account_name
    read -p "GitHub用户名: " github_username
    read -p "GitHub邮箱: " github_email
    read -s -p "GitHub Token: " github_token
    echo
    read -p "仓库名称 (默认: auto-commit-repo): " repo_name
    repo_name=${repo_name:-"auto-commit-repo"}
    
    echo "提交频率选项:"
    echo "1. daily - 每天一次 (09:00)"
    echo "2. frequent - 频繁提交 (09:00, 14:00, 20:00)"
    echo "3. hourly - 每小时 (工作时间)"
    echo "4. minimal - 最少提交 (12:00)"
    echo "5. custom - 自定义时间"
    read -p "选择频率 (1-5): " freq_choice
    
    case $freq_choice in
        1) frequency="daily" ;;
        2) frequency="frequent" ;;
        3) frequency="hourly" ;;
        4) frequency="minimal" ;;
        5) frequency="custom" ;;
        *) frequency="daily" ;;
    esac
    
    custom_times="[]"
    if [[ "$frequency" == "custom" ]]; then
        echo "请输入自定义提交时间 (格式: HH:MM，多个时间用逗号分隔):"
        read -p "提交时间: " custom_input
        if [[ -n "$custom_input" ]]; then
            # 转换为JSON数组格式
            IFS=',' read -ra TIMES <<< "$custom_input"
            custom_times="["
            for i in "${!TIMES[@]}"; do
                time=$(echo "${TIMES[i]}" | xargs)  # 去除空格
                if [[ $i -gt 0 ]]; then
                    custom_times="$custom_times, "
                fi
                custom_times="$custom_times\"$time\""
            done
            custom_times="$custom_times]"
        fi
    fi
    
    # 添加到配置文件
    source venv/bin/activate
    python3 -c "
import json
import os
from config import DATA_DIR

config_file = os.path.join(DATA_DIR, 'accounts_config.json')
accounts = []

# 读取现有配置
if os.path.exists(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
    except:
        accounts = []

# 添加新账号
new_account = {
    'name': '$account_name',
    'token': '$github_token',
    'username': '$github_username',
    'email': '$github_email',
    'repo': '$repo_name',
    'enabled': True,
    'commit_frequency': '$frequency',
    'custom_schedule': $custom_times
}

accounts.append(new_account)

# 保存配置
os.makedirs(DATA_DIR, exist_ok=True)
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(accounts, f, indent=2, ensure_ascii=False)

print(f'✅ 账号 {new_account[\"name\"]} 已添加到配置文件')
"
}

# 主函数
main() {
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -i|--install)
            install_deps
            check_config
            log_info "安装完成，请编辑 .env 文件后运行 --test-config 测试配置"
            exit 0
            ;;
        -t|--test|--test-config)
            check_venv
            check_config
            test_config
            exit $?
            ;;
        -r|--run-once)
            check_venv
            check_config
            source .env
            source venv/bin/activate
            if [[ -n "$2" ]]; then
                # 执行指定账号
                python -c "from scheduler import AutoCommitScheduler; scheduler = AutoCommitScheduler(); scheduler.run_once('$2')"
            else
                # 执行所有账号
                python scheduler.py --run-once
            fi
            exit $?
            ;;
        -d|--daemon)
            check_venv
            check_config
            source .env
            source venv/bin/activate
            python scheduler.py --daemon
            exit $?
            ;;
        -s|--status)
            check_venv
            check_config
            source .env
            source venv/bin/activate
            python scheduler.py --status
            exit $?
            ;;
        --list-accounts)
            check_venv
            list_accounts
            exit $?
            ;;
        --create-config)
            check_venv
            create_config_template
            exit $?
            ;;
        --validate-config)
            check_venv
            validate_config_file
            exit $?
            ;;
        --add-account)
            check_venv
            add_account
            exit $?
            ;;
        --edit-account)
            if [[ -n "$2" ]]; then
                log_info "编辑账号: $2"
                log_info "请手动编辑配置文件: data/accounts_config.json"
            else
                log_error "请指定要编辑的账号名称"
            fi
            exit 0
            ;;
        --disable-account)
            if [[ -n "$2" ]]; then
                check_venv
                source venv/bin/activate
                python3 -c "
import json
import os
from config import DATA_DIR
config_file = os.path.join(DATA_DIR, 'accounts_config.json')
if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        accounts = json.load(f)
    for account in accounts:
        if account['name'] == '$2':
            account['enabled'] = False
            break
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)
    print(f'✅ 账号 $2 已禁用')
else:
    print('❌ 配置文件不存在')
"
            else
                log_error "请指定要禁用的账号名称"
            fi
            exit 0
            ;;
        --enable-account)
            if [[ -n "$2" ]]; then
                check_venv
                source venv/bin/activate
                python3 -c "
import json
import os
from config import DATA_DIR
config_file = os.path.join(DATA_DIR, 'accounts_config.json')
if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        accounts = json.load(f)
    for account in accounts:
        if account['name'] == '$2':
            account['enabled'] = True
            break
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)
    print(f'✅ 账号 $2 已启用')
else:
    print('❌ 配置文件不存在')
"
            else
                log_error "请指定要启用的账号名称"
            fi
            exit 0
            ;;
        --interactive|"")
            check_venv
            check_config
            source .env
            source venv/bin/activate
            python scheduler.py
            exit $?
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"