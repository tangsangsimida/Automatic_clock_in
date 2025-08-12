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
- 🔥 **配置热重载**: 修改配置后无需重启服务，自动检测并应用新配置

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

### 3. 配置GitHub账号信息

创建账号配置：
```bash
# 创建配置模板
./run.sh --create-config

# 编辑配置文件
nano accounts_config.json
```

#### 获取GitHub Token

1. 访问 [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 设置Token名称和过期时间
4. **⚠️ 重要：选择正确的权限范围**
   - ✅ `repo` (完整仓库权限) - **必需**
   - ✅ `user:email` (读取邮箱) - **必需**
   - ✅ `user` (读取用户信息) - **推荐**
5. 生成并复制Token（⚠️ 只显示一次，请妥善保存）

#### Token权限说明

| 权限 | 必需性 | 说明 |
|------|--------|------|
| `repo` | ✅ 必需 | 创建、读取、写入仓库的完整权限 |
| `user:email` | ✅ 必需 | 读取用户邮箱地址，用于Git提交 |
| `user` | 🔶 推荐 | 读取用户基本信息，用于验证用户名 |

#### ⚠️ 常见Token问题

- **权限不足**：如果Token权限不够，会导致API调用失败
- **Token过期**：定期检查Token是否过期，及时更新
- **Token泄露**：不要将Token提交到公共仓库，使用`data/accounts_config.json`文件存储

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

### 🔗 专题指南
- [多Token同时提交到一个仓库指南](docs/multi-user-guide.md) - 详细说明如何使用多个Token以同一身份提交

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

### 🔥 配置热重载功能

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

## ⚙️ 配置说明

### 账号配置 (data/accounts_config.json)

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

### 配置字段详细说明

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `name` | string | ✅ | 账号标识名称，用于区分不同账号 | `"my_account"` |
| `token` | string | ✅ | GitHub Personal Access Token | `"ghp_xxxxxxxxxxxx"` |
| `username` | string | ✅ | **GitHub用户名**（⚠️ 重要：必须是您的真实GitHub用户名） | `"your_github_username"` |
| `email` | string | ✅ | GitHub账号关联的邮箱地址 | `"your@email.com"` |
| `repo` | string | ✅ | 要创建的仓库名称 | `"auto-commit-repo-1"` |
| `enabled` | boolean | ✅ | 是否启用此账号 | `true` / `false` |
| `commit_frequency` | string | ✅ | 提交频率类型 | `"daily"` / `"frequent"` / `"custom"` |
| `custom_schedule` | array | ❌ | 自定义提交时间（仅当频率为custom时使用） | `["09:00", "18:00"]` |

> 💡 **多Token提示**：如果需要使用多个Token同时提交到同一个仓库，请参考 [多Token提交指南](docs/multi-user-guide.md) 了解详细配置方法和最佳实践。

#### ⚠️ 重要提醒：username字段说明

**`username` 字段必须填写您的真实GitHub用户名，而不是显示名称或其他标识！**

- ✅ **正确示例**：如果您的GitHub个人主页是 `https://github.com/john_doe`，那么username应该填写 `"john_doe"`
- ❌ **错误示例**：填写显示名称如 `"John Doe"` 或其他非用户名的标识

**如何查找您的GitHub用户名：**
1. 登录GitHub后，点击右上角头像
2. 查看个人主页URL：`https://github.com/YOUR_USERNAME`
3. 或者在设置页面查看：Settings → Account → Username

**为什么这很重要：**
- 系统会根据username构建仓库API地址：`https://api.github.com/repos/{username}/{repo}`
- 如果username错误，会导致404错误，无法创建或访问仓库
- 这是导致"创建blob失败: 404"错误的常见原因

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
# 提交频率选项
COMMIT_FREQUENCY_OPTIONS = {
    "daily': ["09:00"],
	# 时间格式必须为两位数，不足补零
    'frequent': ["09:00", "14:00", "20:00"],
    'hourly': ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"],
    'minimal': ["12:00"],
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
├── data/
│   └── accounts_config.json # 多账号配置文件
├── accounts_config.example.json  # 多账号配置模板
├── docs/
│   └── multi-user-guide.md # 多Token提交指南
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

1. **❌ 创建blob失败: 404 - Not Found**
   
   **原因分析：**
   - 最常见原因：配置文件中的`username`字段填写错误
   - Token权限不足或已过期
   - 仓库不存在且创建失败
   
   **解决步骤：**
   ```bash
   # 1. 检查username配置是否正确
   # 确认username是您的真实GitHub用户名，不是显示名称
   
   # 2. 验证GitHub用户名
   curl https://api.github.com/users/YOUR_USERNAME
   
   # 3. 测试Token权限
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   
   # 4. 检查仓库是否存在
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO
   ```

2. **配置验证失败**
   ```bash
   # 检查环境变量是否正确设置
   cat data/accounts_config.json
   
   # 测试GitHub Token是否有效
   curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
   ```

3. **服务启动失败**
   ```bash
   # 查看详细错误信息
   sudo journalctl -u github-auto-commit -n 50
   
   # 检查服务配置
   sudo systemctl cat github-auto-commit
   ```

4. **权限问题**
   ```bash
   # 确保脚本有执行权限
   chmod +x *.sh
   
   # 检查文件所有者
   ls -la
   ```

5. **网络连接问题**
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
   chmod 600 data/accounts_config.json
   
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
