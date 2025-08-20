# 📋 系统要求

- Ubuntu 18.04+ (其他Linux发行版可能需要调整)
- Python 3.6+
- Git
- 网络连接

# 🚀 快速开始

## 1. 克隆项目

```bash
git clone https://github.com/your-username/Automatic_clock_in.git
cd Automatic_clock_in
```

## 2. 运行安装脚本

```bash
# 给脚本执行权限
chmod +x install.sh run.sh

# 运行安装脚本
./install.sh
```

## 3. 配置GitHub账号信息

创建账号配置：
```bash
# 创建配置模板
./run.sh --create-config

# 编辑配置文件
nano accounts_config.json
```

### 获取GitHub Token

1. 访问 [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 设置Token名称和过期时间
4. **⚠️ 重要：选择正确的权限范围**
   - ✅ `repo` (完整仓库权限) - **必需**
   - ✅ `user:email` (读取邮箱) - **必需**
   - ✅ `user` (读取用户信息) - **推荐**
5. 生成并复制Token（⚠️ 只显示一次，请妥善保存）

### Token权限说明

| 权限 | 必需性 | 说明 |
|------|--------|------|
| `repo` | ✅ 必需 | 创建、读取、写入仓库的完整权限 |
| `user:email` | ✅ 必需 | 读取用户邮箱地址，用于Git提交 |
| `user` | 🔶 推荐 | 读取用户基本信息，用于验证用户名 |

### ⚠️ 常见Token问题

- **权限不足**：如果Token权限不够，会导致API调用失败
- **Token过期**：定期检查Token是否过期，及时更新
- **Token泄露**：不要将Token提交到公共仓库，使用`data/accounts_config.json`文件存储

## 4. 测试配置

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

## 5. 启动服务

```bash
# 启动systemd服务
sudo systemctl start github-auto-commit

# 设置开机自启
sudo systemctl enable github-auto-commit
```