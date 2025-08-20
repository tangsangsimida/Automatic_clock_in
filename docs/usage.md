# 📖 使用说明

## 命令行选项

```bash
./run.sh [选项] [参数]

基本选项:
  -h, --help              显示帮助信息
  -i, --install           安装系统依赖
  -r, --run-once [账号]   立即执行一次提交
  -d, --daemon            以守护进程模式运行
  -s, --status            显示服务状态
  -t, --test-config       测试配置
  --interactive           交互式配置

多账号管理:
  --list-accounts         列出所有账号配置
  --create-config         创建多账号配置模板
  --validate-config       验证配置文件
  --add-account           添加新账号配置
  --edit-account [名称]   编辑指定账号配置
  --disable-account [名称] 禁用指定账号
  --enable-account [名称]  启用指定账号

使用示例:
  ./run.sh --run-once           # 执行所有启用账号
  ./run.sh --run-once account1  # 执行指定账号
  ./run.sh --add-account        # 交互式添加账号
  ./run.sh --list-accounts      # 查看账号状态
```

## 管理脚本

```bash
# 查看服务状态
./status.sh

# 手动执行一次 (所有账号)
./run_once.sh

# 手动执行指定账号
./run_once.sh account1

# 启动服务
./start.sh

# 停止服务
./stop.sh
```

## systemd服务管理

```bash
# 启动服务
sudo systemctl start github-auto-commit

# 停止服务
sudo systemctl stop github-auto-commit

# 重启服务
sudo systemctl restart github-auto-commit

# 重载配置（无需重启服务）
./reload_config.sh

# 查看状态
sudo systemctl status github-auto-commit

# 查看日志
sudo journalctl -u github-auto-commit -f

# 开机自启
sudo systemctl enable github-auto-commit

# 禁用自启
sudo systemctl disable github-auto-commit
```

## 🔥 配置热重载功能

系统支持配置热重载，修改配置文件后无需重启服务：

```bash
# 方式1: 手动重载配置
./reload_config.sh

# 方式2: 自动检测（系统每30秒自动检查配置文件变化）
# 只需修改 data/accounts_config.json 文件，系统会自动重载
```

**配置重载特性：**
- ✅ 无需重启服务，配置立即生效
- ✅ 自动检测配置文件变化（30秒检查间隔）
- ✅ 支持手动触发重载
- ✅ 配置错误时自动回退到旧配置
- ✅ 重载过程完全透明，不影响正在运行的任务

## 🗑️ 卸载系统

如果您需要完全删除GitHub自动打卡系统，可以使用提供的卸载脚本：

### 基本卸载

```bash
# 交互式卸载（推荐）
./uninstall.sh

# 强制卸载（无需确认）
./uninstall.sh --force
```

### 卸载选项

```bash
./uninstall.sh [选项]

选项:
  -h, --help              显示帮助信息
  -f, --force             强制卸载，不询问确认
  --keep-config           保留配置文件
  --keep-logs             保留日志文件
  --dry-run               仅显示将要删除的内容，不实际删除

使用示例:
  ./uninstall.sh                    # 交互式卸载
  ./uninstall.sh --force            # 强制卸载所有内容
  ./uninstall.sh --keep-config      # 卸载但保留配置文件
  ./uninstall.sh --keep-logs        # 卸载但保留日志文件
  ./uninstall.sh --dry-run          # 预览将要删除的内容
```

### 卸载内容

卸载脚本将删除以下内容：

- ✅ **systemd服务**: 停止并删除 `github-auto-commit` 服务
- ✅ **crontab任务**: 删除相关的定时任务
- ✅ **运行进程**: 停止所有相关的运行进程
- ✅ **虚拟环境**: 删除 `venv/` 目录
- ✅ **数据文件**: 删除 `data/` 目录（包括账号配置）
- ✅ **日志文件**: 删除 `logs/` 目录（可选保留）
- ✅ **配置文件**: 删除 `data/accounts_config.json`（可选保留）
- ✅ **临时文件**: 清理 `*.pyc`、`__pycache__`、`*.pid` 等

### 注意事项

⚠️ **重要提醒**：
- 卸载操作不可逆，请确保已备份重要数据
- 项目目录本身不会被删除，需要手动删除
- 使用 `--dry-run` 选项可以预览将要删除的内容
- 如果保留了配置文件，重新安装时可以直接使用