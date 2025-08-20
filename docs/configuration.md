# ⚙️ 配置说明

## 账号配置 (data/accounts_config.json)

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
    "custom_schedule": [],
    "auto_merge": true,
    "delete_branch_after_merge": true
  },
  {
    "name": "account2",
    "token": "ghp_token2",
    "username": "user2",
    "email": "user2@example.com",
    "repo": "auto-commit-repo-2",
    "enabled": true,
    "commit_frequency": "frequent",
    "custom_schedule": [],
    "auto_merge": true,
    "delete_branch_after_merge": true
  },
  {
    "name": "account3",
    "token": "ghp_token3",
    "username": "user3",
    "email": "user3@example.com",
    "repo": "auto-commit-repo-3",
    "enabled": false,
    "commit_frequency": "custom",
    "custom_schedule": ["10:30", "14:15", "20:00"],
    "auto_merge": false,
    "delete_branch_after_merge": false
  }
]
```

## 配置字段详细说明

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
| `auto_merge` | boolean | ❌ | 是否自动合并PR（默认：true） | `true` / `false` |
| `delete_branch_after_merge` | boolean | ❌ | 合并后是否删除分支（默认：true） | `true` / `false` |

> 💡 **多用户协作提示**：如果需要多个用户同时提交到同一个仓库，请参考 [多用户协作指南](multi-user-guide.md) 了解详细配置方法和最佳实践。

### ⚠️ 重要提醒：username字段说明

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

## 提交频率选项

| 频率类型 | 说明 | 提交时间 |
|---------|------|----------|
| `daily` | 每天一次 | 09:00 |
| `frequent` | 频繁提交 | 09:00, 14:00, 20:00 |
| `hourly` | 每小时 | 09:00-18:00 (工作时间) |
| `minimal` | 最少提交 | 12:00 |
| `custom` | 自定义时间 | 根据 `custom_schedule` 设置 |

## 时间配置 (config.py)

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

## 提交内容配置

系统会自动生成包含以下内容的提交：

- 📅 当前日期和时间
- 🎯 随机的开发活动
- 💻 随机的技术栈
- 📊 模拟的统计信息
- 💭 随机的技术感悟