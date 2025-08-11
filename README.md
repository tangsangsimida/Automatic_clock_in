# GitHub自动打卡系统 🚀

一个用于Ubuntu系统的自动GitHub提交工具，通过定时创建PR来保持GitHub贡献图全绿。

## ✨ 功能特性

- 🕒 **定时提交**: 每天自动在指定时间提交代码
- 👥 **多账号支持**: 同时管理多个GitHub账号的自动提交
- 🔄 **自动PR**: 自动创建Pull Request保持活跃
- 📊 **智能内容**: 生成随机的提交内容和技术栈信息
- ⚙️ **灵活配置**: 支持自定义提交时间和频率
- 📅 **多种频率**: 支持每日、频繁、每小时、最少、自定义等提交模式
- 🛠️ **多种部署**: 支持systemd服务和crontab定时任务
- 📝 **详细日志**: 完整的操作日志记录，每个账号独立日志
- 🎮 **交互模式**: 支持命令行交互操作
- 🚀 **并发执行**: 多账号并发提交，提高效率

## 📋 系统要求

- Ubuntu 18.04+ (其他Linux发行版可能需要调整)
- Python 3.6+
- Git
- 网络连接

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/Automatic_clock_in.git
cd Automatic_clock_in
```

### 2. 运行安装脚本

```bash
# 给脚本执行权限
chmod +x install.sh run.sh

# 运行安装脚本
./install.sh
```

### 3. 配置GitHub信息

#### 单账号模式 (简单)
编辑 `.env` 文件，填写您的GitHub信息：

```bash
# GitHub配置
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_USERNAME=your_username
GITHUB_EMAIL=your_email@example.com
GITHUB_REPO=auto-commit-repo
```

#### 多账号模式 (推荐)
创建多账号配置：
```bash
# 创建配置模板
./run.sh --create-config

# 编辑配置文件
nano data/accounts_config.json
```

#### 获取GitHub Token

1. 访问 [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择权限：`repo`, `workflow`
4. 复制生成的token到配置文件

### 4. 测试配置

```bash
# 测试配置是否正确
./run.sh --test-config

# 验证多账号配置
./run.sh --validate-config

# 查看账号列表
./run.sh --list-accounts

# 立即执行一次任务
./run.sh --run-once
```

### 5. 启动服务

```bash
# 启动systemd服务
sudo systemctl start github-auto-commit

# 设置开机自启
sudo systemctl enable github-auto-commit
```

## 📖 使用说明

### 命令行选项

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

### 管理脚本

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

### systemd服务管理

```bash
# 启动服务
sudo systemctl start github-auto-commit

# 停止服务
sudo systemctl stop github-auto-commit

# 重启服务
sudo systemctl restart github-auto-commit

# 查看状态
sudo systemctl status github-auto-commit

# 查看日志
sudo journalctl -u github-auto-commit -f

# 开机自启
sudo systemctl enable github-auto-commit

# 禁用自启
sudo systemctl disable github-auto-commit
```

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
- ✅ **配置文件**: 删除 `.env` 和 `config.local.py`（可选保留）
- ✅ **临时文件**: 清理 `*.pyc`、`__pycache__`、`*.pid` 等

### 注意事项

⚠️ **重要提醒**：
- 卸载操作不可逆，请确保已备份重要数据
- 项目目录本身不会被删除，需要手动删除
- 使用 `--dry-run` 选项可以预览将要删除的内容
- 如果保留了配置文件，重新安装时可以直接使用

## ⚙️ 配置说明

### 单账号配置 (.env)

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | ✅ | - |
| `GITHUB_USERNAME` | GitHub用户名 | ✅ | - |
| `GITHUB_EMAIL` | GitHub邮箱 | ✅ | - |
| `GITHUB_REPO` | 仓库名称 | ❌ | auto-commit-repo |

### 多账号配置 (data/accounts_config.json)

```json
[
  {
    "name": "account1",
    "token": "ghp_token1",
    "username": "user1",
    "email": "user1@example.com",
    "repo": "auto-commit-repo-1",
    "enabled": true,
    "commit_frequency": "daily",
    "custom_schedule": []
  },
  {
    "name": "account2",
    "token": "ghp_token2",
    "username": "user2",
    "email": "user2@example.com",
    "repo": "auto-commit-repo-2",
    "enabled": true,
    "commit_frequency": "frequent",
    "custom_schedule": []
  },
  {
    "name": "account3",
    "token": "ghp_token3",
    "username": "user3",
    "email": "user3@example.com",
    "repo": "auto-commit-repo-3",
    "enabled": false,
    "commit_frequency": "custom",
    "custom_schedule": ["10:30", "14:15", "20:00"]
  }
]
```

### 提交频率选项

| 频率类型 | 说明 | 提交时间 |
|---------|------|----------|
| `daily` | 每天一次 | 09:00 |
| `frequent` | 频繁提交 | 09:00, 14:00, 20:00 |
| `hourly` | 每小时 | 09:00-18:00 (工作时间) |
| `minimal` | 最少提交 | 12:00 |
| `custom` | 自定义时间 | 根据 `custom_schedule` 设置 |

### 时间配置 (config.py)

```python
# 每天提交的时间点 (单账号模式)
COMMIT_TIMES = ['09:00', '18:00']

# 提交频率选项 (多账号模式)
COMMIT_FREQUENCY_OPTIONS = {
    'daily': ['09:00'],
    'frequent': ['09:00', '14:00', '20:00'],
    'hourly': ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'],
    'minimal': ['12:00'],
    'custom': []  # 由 custom_schedule 指定
}

# 时区设置
TIMEZONE = 'Asia/Shanghai'
```

### 提交内容配置

系统会自动生成包含以下内容的提交：

- 📅 当前日期和时间
- 🎯 随机的开发活动
- 💻 随机的技术栈
- 📊 模拟的统计信息
- 💭 随机的技术感悟

## 📁 项目结构

```
Automatic_clock_in/
├── config.py              # 配置文件
├── auto_commit.py          # 主要功能实现
├── scheduler.py            # 定时任务调度器
├── install.sh              # 安装脚本
├── run.sh                  # 启动脚本
├── uninstall.sh            # 卸载脚本
├── test.py                 # 系统测试脚本
├── requirements.txt        # Python依赖
├── .env                    # 环境变量配置
├── .env.example            # 环境变量模板
├── accounts_config.example.json  # 多账号配置模板
├── .gitignore              # Git忽略文件
├── data/                   # 数据目录
│   ├── accounts_config.json         # 多账号配置
│   ├── commit_data_default_*.json   # 单账号数据
│   ├── commit_data_account1_*.json  # 账号1数据
│   └── commit_data_account2_*.json  # 账号2数据
├── logs/                   # 日志目录
│   ├── auto_commit_default_*.log    # 单账号日志
│   ├── auto_commit_account1_*.log   # 账号1日志
│   ├── auto_commit_account2_*.log   # 账号2日志
│   └── scheduler.log                # 调度器日志
└── venv/                   # Python虚拟环境
```

## 🔧 故障排除

### 常见问题

1. **配置验证失败**
   ```bash
   # 检查环境变量是否正确设置
   cat .env
   
   # 测试GitHub Token是否有效
   curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
   ```

2. **服务启动失败**
   ```bash
   # 查看详细错误信息
   sudo journalctl -u github-auto-commit -n 50
   
   # 检查服务配置
   sudo systemctl cat github-auto-commit
   ```

3. **权限问题**
   ```bash
   # 确保脚本有执行权限
   chmod +x *.sh
   
   # 检查文件所有者
   ls -la
   ```

4. **网络连接问题**
   ```bash
   # 测试GitHub API连接
   curl -I https://api.github.com
   
   # 检查DNS解析
   nslookup github.com
   ```

### 日志查看

```bash
# 查看应用日志
tail -f logs/auto_commit.log

# 查看systemd日志
sudo journalctl -u github-auto-commit -f

# 查看最近的错误
sudo journalctl -u github-auto-commit -p err
```

## 🛡️ 安全注意事项

1. **Token安全**
   - 不要将GitHub Token提交到公共仓库
   - 定期轮换Token
   - 使用最小权限原则

2. **文件权限**
   ```bash
   # 设置配置文件权限
   chmod 600 .env
   
   # 确保日志目录权限
   chmod 755 logs/
   ```

3. **网络安全**
   - 确保系统防火墙配置正确
   - 定期更新系统和依赖包

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 GPL-3.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [GitHub API](https://docs.github.com/en/rest) - 提供强大的API支持
- [Python Schedule](https://github.com/dbader/schedule) - 简单易用的任务调度库
- [Requests](https://github.com/psf/requests) - 优雅的HTTP库

## 📞 支持

如果您遇到问题或有建议，请：

1. 查看 [Issues](https://github.com/your-username/Automatic_clock_in/issues)
2. 创建新的 Issue
3. 发送邮件至：dennisreyoonjiho@gmail.com

---

⭐ 如果这个项目对您有帮助，请给它一个星标！
