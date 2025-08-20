# GitHub自动打卡系统 🚀

一个用于Ubuntu系统的自动GitHub提交工具，通过定时创建PR来保持GitHub贡献图全绿。

## ✨ 功能特性

- 🕒 **定时提交**: 每天自动在指定时间提交代码
- 👥 **多账号支持**: 同时管理多个GitHub账号的自动提交
- 🔄 **自动PR**: 自动创建Pull Request保持活跃
- 🤖 **自动合并**: 创建PR后自动合并到主分支，无需手动操作
- 🗑️ **智能清理**: 合并后自动删除临时分支，保持仓库整洁

[查看完整功能特性](docs/features.md)

## 📋 系统要求

- Ubuntu 18.04+ (其他Linux发行版可能需要调整)
- Python 3.6+
- Git
- 网络连接

[查看详细系统要求](docs/system-requirements.md)

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

[查看详细配置说明](docs/configuration.md)

### 4. 测试配置

```bash
# 测试配置是否正确
./run.sh --test-config

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
  -r, --run-once [账号]   立即执行一次提交
  -s, --status            显示服务状态
  -t, --test-config       测试配置
```

[查看完整使用说明](docs/usage.md)

## 📚 文档

- [功能特性](docs/features.md)
- [系统要求](docs/system-requirements.md)
- [配置说明](docs/configuration.md)
- [使用说明](docs/usage.md)
- [项目结构](docs/project-structure.md)
- [故障排除](docs/troubleshooting.md)
- [安全注意事项](docs/security.md)
- [多用户协作指南](docs/multi-user-guide.md)
- [自动合并功能指南](docs/auto-merge-guide.md)
- [串行执行模式指南](docs/serial-execution-guide.md)

## 🙏 致谢

- [GitHub API](https://docs.github.com/en/rest) - 提供强大的API支持
- [Python Schedule](https://github.com/dbader/schedule) - 简单易用的任务调度库
- [Requests](https://github.com/psf/requests) - 优雅的HTTP库

## 📄 许可证

本项目采用 GPL-3.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如果您遇到问题或有建议，请：

1. 查看 [Issues](https://github.com/your-username/Automatic_clock_in/issues)
2. 创建新的 Issue
3. 发送邮件至：dennisreyoonjiho@gmail.com

---

⭐ 如果这个项目对您有帮助，请给它一个星标！