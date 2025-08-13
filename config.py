#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
包含GitHub相关配置和系统设置
支持多账号配置和自定义提交频率
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any

# 多账号配置
# 可以通过环境变量GITHUB_ACCOUNTS_CONFIG指定JSON配置文件路径
# 或者通过GITHUB_ACCOUNTS_JSON直接提供JSON字符串
GITHUB_ACCOUNTS_CONFIG = os.getenv('GITHUB_ACCOUNTS_CONFIG', os.path.join(os.path.dirname(__file__), 'data', 'accounts_config.json'))
GITHUB_ACCOUNTS_JSON = os.getenv('GITHUB_ACCOUNTS_JSON', '')

# 默认多账号配置示例
DEFAULT_ACCOUNTS_CONFIG = [
    {
        "name": "account1",
        "token": "",
        "username": "",
        "email": "",
        "repo": "auto-commit-repo-1",
        "enabled": True,
        "commit_times": ["09:00", "18:00"],
        "commit_frequency": "daily",  # daily, hourly, custom
        "custom_schedule": [],  # 自定义时间表，格式: ["HH:MM", ...]
        "auto_merge": True,  # 是否自动合并PR
        "delete_branch_after_merge": True  # 合并后是否删除分支
    }
]

# 提交频率配置
COMMIT_FREQUENCY_OPTIONS = {
    "hourly": [f"{h:02d}:00" for h in range(9, 18)],  # 每小时9-17点
    "daily": ["09:00", "18:00"],  # 每天两次
    "frequent": ["09:00", "12:00", "15:00", "18:00"],  # 每天四次
    "minimal": ["12:00"],  # 每天一次
    "custom": []  # 自定义，需要在配置中指定
}

# 并发控制配置
CONCURRENCY_CONFIG = {
    "max_workers": 3,  # 最大并发数，建议不超过3以减少GitHub API冲突
    "base_delay_range": (1.5, 3.0),  # 基础延迟范围（秒）
    "retry_delay_range": (3.0, 8.0),  # 重试延迟范围（秒）
    "max_retries_per_account": 3,  # 每个账号的最大重试次数
    "merge_retry_count": 8,  # PR合并的最大重试次数
    "merge_retry_backoff": 1.5,  # PR合并重试的退避系数
    "enable_smart_retry": True,  # 启用智能重试（检测冲突类型）
    "conflict_detection_keywords": [  # 冲突检测关键词
        "合并失败", "conflict", "not mergeable", "Base branch was modified",
        "merge conflict", "Pull Request is not mergeable"
    ]
}

# 提交配置
COMMIT_MESSAGE_TEMPLATE = "Auto commit on {date} - Keep the streak alive! 🔥"
PR_TITLE_TEMPLATE = "Auto PR on {date} - Daily contribution"
PR_BODY_TEMPLATE = """🤖 自动生成的PR

📅 日期: {date}
⏰ 时间: {time}
🎯 目的: 保持GitHub贡献图活跃

---
*此PR由自动化脚本生成*
"""

# 文件配置
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'auto_commit.log')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 时间配置
TIMEZONE = 'Asia/Shanghai'

# 提交配置（已移至多账号配置中）

# 分支配置
MAIN_BRANCH = 'main'
PR_BRANCH_PREFIX = 'auto-commit-'

# API配置
GITHUB_API_BASE = 'https://api.github.com'
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3


# 多账号管理函数
def load_accounts_config() -> List[Dict[str, Any]]:
    """加载多账号配置"""
    accounts = []
    
    # 优先从JSON字符串加载
    if GITHUB_ACCOUNTS_JSON:
        try:
            accounts = json.loads(GITHUB_ACCOUNTS_JSON)
        except json.JSONDecodeError as e:
            raise ValueError(f"GITHUB_ACCOUNTS_JSON格式错误: {e}")
    
    # 从配置文件加载
    elif GITHUB_ACCOUNTS_CONFIG and os.path.exists(GITHUB_ACCOUNTS_CONFIG):
        try:
            with open(GITHUB_ACCOUNTS_CONFIG, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"读取账号配置文件失败: {e}")
    
    # 如果没有找到配置，提示用户创建
    else:
        raise ValueError(f"未找到账号配置文件: {GITHUB_ACCOUNTS_CONFIG}\n请运行 './run.sh --create-config' 创建配置文件")
    
    # 验证和补充账号配置
    validated_accounts = []
    for i, account in enumerate(accounts):
        if not account.get('enabled', True):
            continue
            
        # 验证必需字段
        required_fields = ['token', 'username', 'email']
        missing_fields = [field for field in required_fields if not account.get(field)]
        if missing_fields:
            raise ValueError(f"账号 {account.get('name', f'#{i+1}')} 缺少必需字段: {', '.join(missing_fields)}")
        
        # 设置默认值
        account.setdefault('name', f'account_{i+1}')
        account.setdefault('repo', f'auto-commit-repo-{i+1}')
        account.setdefault('commit_frequency', 'daily')
        account.setdefault('custom_schedule', [])
        account.setdefault('auto_merge', True)
        account.setdefault('delete_branch_after_merge', True)
        
        # 根据频率设置提交时间
        frequency = account['commit_frequency']
        if frequency in COMMIT_FREQUENCY_OPTIONS:
            if frequency == 'custom':
                account['commit_times'] = account.get('custom_schedule', [])
            else:
                account['commit_times'] = COMMIT_FREQUENCY_OPTIONS[frequency]
        else:
            account['commit_times'] = account.get('commit_times', COMMIT_FREQUENCY_OPTIONS['daily'])
        
        validated_accounts.append(account)
    
    if not validated_accounts:
        raise ValueError("没有有效的账号配置")
    
    return validated_accounts

def get_account_by_name(name: str) -> Dict[str, Any]:
    """根据名称获取账号配置"""
    accounts = load_accounts_config()
    for account in accounts:
        if account['name'] == name:
            return account
    raise ValueError(f"未找到名为 '{name}' 的账号配置")

def list_enabled_accounts() -> List[str]:
    """列出所有启用的账号名称"""
    accounts = load_accounts_config()
    return [account['name'] for account in accounts if account.get('enabled', True)]

def validate_account_config(account: Dict[str, Any]) -> bool:
    """验证单个账号配置"""
    required_fields = ['token', 'username', 'email']
    for field in required_fields:
        if not account.get(field):
            raise ValueError(f"账号 {account.get('name', 'Unknown')} 缺少必需字段: {field}")
    
    # 验证提交时间格式
    commit_times = account.get('commit_times', [])
    for time_str in commit_times:
        try:
            datetime.strptime(time_str, '%H:%M')
        except ValueError:
            raise ValueError(f"账号 {account['name']} 的提交时间格式错误: {time_str}，应为 HH:MM 格式")
    
    return True

# 验证必要的环境变量
def validate_config():
    """验证配置是否完整"""
    try:
        accounts = load_accounts_config()
        for account in accounts:
            validate_account_config(account)
        return True
    except Exception as e:
        raise ValueError(f"配置验证失败: {e}")

def create_accounts_config_template(file_path: str = None) -> str:
    """创建账号配置模板文件"""
    if not file_path:
        file_path = os.path.join(DATA_DIR, 'accounts_config.json')
    
    template = [
        {
            "name": "account1",
            "token": "ghp_your_token_here",
            "username": "your_username1",
            "email": "your_email1@example.com",
            "repo": "auto-commit-repo-1",
            "enabled": True,
            "commit_frequency": "daily",
            "custom_schedule": [],
            "auto_merge": True,
            "delete_branch_after_merge": True
        },
        {
            "name": "account2",
            "token": "ghp_your_token_here",
            "username": "your_username2",
            "email": "your_email2@example.com",
            "repo": "auto-commit-repo-2",
            "enabled": True,
            "commit_frequency": "frequent",
            "custom_schedule": [],
            "auto_merge": True,
            "delete_branch_after_merge": True
        },
        {
            "name": "account3",
            "token": "ghp_your_token_here",
            "username": "your_username3",
            "email": "your_email3@example.com",
            "repo": "auto-commit-repo-3",
            "enabled": False,
            "commit_frequency": "custom",
            "custom_schedule": ["10:30", "14:15", "20:00"],
            "auto_merge": False,
            "delete_branch_after_merge": False
        }
    ]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    return file_path

# 初始化ACCOUNTS变量（向后兼容）
try:
    ACCOUNTS = load_accounts_config()
except Exception:
    # 如果加载失败，使用空列表，避免导入错误
    ACCOUNTS = []

if __name__ == '__main__':
    try:
        validate_config()
        print("✅ 配置验证通过")
        accounts = load_accounts_config()
        print(f"📋 已加载 {len(accounts)} 个账号配置")
        for account in accounts:
            print(f"  - {account['name']}: {account['username']} ({account['commit_frequency']})")
    except ValueError as e:
        print(f"❌ 配置验证失败: {e}")
        print("\n请运行以下命令创建配置文件:")
        print("./run.sh --create-config")
        print("\n或者手动创建 data/accounts_config.json 文件")