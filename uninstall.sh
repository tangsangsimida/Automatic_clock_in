#!/bin/bash

# GitHub自动打卡系统 - 卸载脚本
# 用于完全删除项目并清理所有相关文件

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
PROJECT_NAME="$(basename "$SCRIPT_DIR")"
VENV_DIR="$SCRIPT_DIR/venv"
DATA_DIR="$SCRIPT_DIR/data"
LOGS_DIR="$SCRIPT_DIR/logs"

# 显示帮助信息
show_help() {
    cat << EOF
GitHub自动打卡系统 - 卸载脚本

用法: $0 [选项]

选项:
  -h, --help              显示此帮助信息
  -f, --force             强制卸载，不询问确认
  --keep-config           保留配置文件
  --keep-logs             保留日志文件
  --dry-run               仅显示将要删除的内容，不实际删除

示例:
  $0                      交互式卸载
  $0 --force              强制卸载所有内容
  $0 --keep-config        卸载但保留配置文件
  $0 --dry-run            预览将要删除的内容

EOF
}

# 检查systemd服务
check_systemd_service() {
    local service_name="github-auto-commit"
    if systemctl is-active --quiet "$service_name" 2>/dev/null; then
        log_warning "检测到systemd服务正在运行: $service_name"
        return 0
    elif systemctl list-unit-files | grep -q "$service_name"; then
        log_warning "检测到systemd服务已安装: $service_name"
        return 0
    fi
    return 1
}

# 停止并删除systemd服务
remove_systemd_service() {
    local service_name="github-auto-commit"
    local service_file="/etc/systemd/system/${service_name}.service"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] 将停止并删除systemd服务: $service_name"
        return
    fi
    
    log_info "停止systemd服务..."
    if systemctl is-active --quiet "$service_name" 2>/dev/null; then
        sudo systemctl stop "$service_name" || log_warning "无法停止服务"
    fi
    
    log_info "禁用systemd服务..."
    if systemctl is-enabled --quiet "$service_name" 2>/dev/null; then
        sudo systemctl disable "$service_name" || log_warning "无法禁用服务"
    fi
    
    log_info "删除systemd服务文件..."
    if [[ -f "$service_file" ]]; then
        sudo rm -f "$service_file" || log_warning "无法删除服务文件"
    fi
    
    log_info "重新加载systemd配置..."
    sudo systemctl daemon-reload || log_warning "无法重新加载systemd配置"
    
    log_success "systemd服务已删除"
}

# 检查crontab任务
check_crontab() {
    if crontab -l 2>/dev/null | grep -q "$SCRIPT_DIR"; then
        log_warning "检测到crontab任务包含此项目路径"
        return 0
    fi
    return 1
}

# 删除crontab任务
remove_crontab() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] 将删除相关的crontab任务"
        return
    fi
    
    log_info "删除crontab任务..."
    local temp_cron=$(mktemp)
    crontab -l 2>/dev/null | grep -v "$SCRIPT_DIR" > "$temp_cron" || true
    crontab "$temp_cron" || log_warning "无法更新crontab"
    rm -f "$temp_cron"
    log_success "crontab任务已删除"
}

# 停止运行中的进程
stop_processes() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] 将停止相关的运行进程"
        return
    fi
    
    log_info "停止运行中的进程..."
    
    # 查找并停止相关进程
    local pids=$(pgrep -f "$SCRIPT_DIR" 2>/dev/null || true)
    if [[ -n "$pids" ]]; then
        log_info "发现运行中的进程: $pids"
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        
        # 强制杀死仍在运行的进程
        local remaining_pids=$(pgrep -f "$SCRIPT_DIR" 2>/dev/null || true)
        if [[ -n "$remaining_pids" ]]; then
            log_warning "强制停止进程: $remaining_pids"
            echo "$remaining_pids" | xargs kill -KILL 2>/dev/null || true
        fi
        
        log_success "进程已停止"
    else
        log_info "未发现运行中的进程"
    fi
}

# 删除虚拟环境
remove_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY RUN] 将删除虚拟环境: $VENV_DIR"
        else
            log_info "删除虚拟环境..."
            rm -rf "$VENV_DIR"
            log_success "虚拟环境已删除"
        fi
    fi
}

# 删除数据文件
remove_data() {
    if [[ -d "$DATA_DIR" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY RUN] 将删除数据目录: $DATA_DIR"
        else
            log_info "删除数据文件..."
            rm -rf "$DATA_DIR"
            log_success "数据文件已删除"
        fi
    fi
}

# 删除日志文件
remove_logs() {
    if [[ "$KEEP_LOGS" == "true" ]]; then
        log_info "保留日志文件"
        return
    fi
    
    if [[ -d "$LOGS_DIR" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY RUN] 将删除日志目录: $LOGS_DIR"
        else
            log_info "删除日志文件..."
            rm -rf "$LOGS_DIR"
            log_success "日志文件已删除"
        fi
    fi
}

# 删除配置文件
remove_config() {
    if [[ "$KEEP_CONFIG" == "true" ]]; then
        log_info "保留配置文件"
        return
    fi
    
    local config_files=("data/accounts_config.json" "config.local.py")
    
    for config_file in "${config_files[@]}"; do
        local file_path="$SCRIPT_DIR/$config_file"
        if [[ -f "$file_path" ]]; then
            if [[ "$DRY_RUN" == "true" ]]; then
                log_info "[DRY RUN] 将删除配置文件: $file_path"
            else
                log_info "删除配置文件: $config_file"
                rm -f "$file_path"
                log_success "配置文件 $config_file 已删除"
            fi
        fi
    done
}

# 删除临时文件
remove_temp_files() {
    local temp_patterns=("*.pyc" "__pycache__" "*.log" "*.pid" "*.lock")
    
    for pattern in "${temp_patterns[@]}"; do
        if [[ "$DRY_RUN" == "true" ]]; then
            local files=$(find "$SCRIPT_DIR" -name "$pattern" 2>/dev/null || true)
            if [[ -n "$files" ]]; then
                log_info "[DRY RUN] 将删除临时文件: $pattern"
            fi
        else
            find "$SCRIPT_DIR" -name "$pattern" -delete 2>/dev/null || true
        fi
    done
    
    if [[ "$DRY_RUN" != "true" ]]; then
        log_success "临时文件已清理"
    fi
}

# 显示将要删除的内容
show_removal_summary() {
    log_info "将要删除的内容:"
    echo
    
    # 检查systemd服务
    if check_systemd_service; then
        echo "  ✓ systemd服务 (github-auto-commit)"
    fi
    
    # 检查crontab
    if check_crontab; then
        echo "  ✓ crontab任务"
    fi
    
    # 检查文件和目录
    [[ -d "$VENV_DIR" ]] && echo "  ✓ 虚拟环境 ($VENV_DIR)"
    [[ -d "$DATA_DIR" ]] && echo "  ✓ 数据文件 ($DATA_DIR)"
    
    if [[ "$KEEP_LOGS" != "true" ]] && [[ -d "$LOGS_DIR" ]]; then
        echo "  ✓ 日志文件 ($LOGS_DIR)"
    fi
    
    if [[ "$KEEP_CONFIG" != "true" ]]; then
        [[ -f "$SCRIPT_DIR/.env" ]] && echo "  ✓ 配置文件 (.env)"
        [[ -f "$SCRIPT_DIR/config.local.py" ]] && echo "  ✓ 配置文件 (config.local.py)"
    fi
    
    echo "  ✓ 临时文件 (*.pyc, __pycache__, *.log, *.pid, *.lock)"
    
    if [[ "$KEEP_CONFIG" != "true" ]] && [[ "$KEEP_LOGS" != "true" ]]; then
        echo
        log_warning "项目目录本身不会被删除，但所有相关文件将被清理"
    fi
    
    echo
}

# 确认卸载
confirm_uninstall() {
    if [[ "$FORCE" == "true" ]]; then
        return 0
    fi
    
    echo
    read -p "确定要卸载GitHub自动打卡系统吗？[y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "卸载已取消"
        exit 0
    fi
}

# 主卸载函数
main_uninstall() {
    log_info "开始卸载GitHub自动打卡系统..."
    echo
    
    # 停止进程
    stop_processes
    
    # 删除systemd服务
    if check_systemd_service; then
        remove_systemd_service
    fi
    
    # 删除crontab任务
    if check_crontab; then
        remove_crontab
    fi
    
    # 删除文件和目录
    remove_venv
    remove_data
    remove_logs
    remove_config
    remove_temp_files
    
    if [[ "$DRY_RUN" != "true" ]]; then
        echo
        log_success "GitHub自动打卡系统已完全卸载！"
        log_info "项目目录: $SCRIPT_DIR"
        log_info "您可以手动删除整个项目目录"
    else
        echo
        log_info "[DRY RUN] 预览完成，使用 --force 参数执行实际卸载"
    fi
}

# 解析命令行参数
FORCE="false"
KEEP_CONFIG="false"
KEEP_LOGS="false"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE="true"
            shift
            ;;
        --keep-config)
            KEEP_CONFIG="true"
            shift
            ;;
        --keep-logs)
            KEEP_LOGS="true"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 主程序
echo "GitHub自动打卡系统 - 卸载脚本"
echo "=============================="
echo

# 显示当前配置
log_info "当前配置:"
echo "  项目目录: $SCRIPT_DIR"
echo "  强制模式: $FORCE"
echo "  保留配置: $KEEP_CONFIG"
echo "  保留日志: $KEEP_LOGS"
echo "  预览模式: $DRY_RUN"
echo

# 显示删除摘要
show_removal_summary

# 确认卸载
if [[ "$DRY_RUN" != "true" ]]; then
    confirm_uninstall
fi

# 执行卸载
main_uninstall

exit 0