# 📁 项目结构

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
│   ├── features.md         # 功能特性文档
│   ├── system-requirements.md # 系统要求文档
│   ├── configuration.md    # 配置说明文档
│   ├── project-structure.md # 项目结构文档
│   ├── troubleshooting.md  # 故障排除文档
│   ├── security.md         # 安全注意事项文档
│   ├── auto-merge-guide.md # 自动合并功能指南
│   ├── multi-user-guide.md # 多用户协作指南
│   └── serial-execution-guide.md # 串行执行模式指南
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