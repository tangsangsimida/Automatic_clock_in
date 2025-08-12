# 自动合并功能指南

## 🚀 功能概述

本项目新增了自动合并PR和分支管理功能，解决了多用户提交时的冲突问题，并实现了完全自动化的工作流程。

## ✨ 新增功能

### 1. 📁 用户文件夹隔离

**问题**: 之前多个用户提交到同一路径会产生冲突

**解决方案**: 每个用户的文件放在独立的文件夹中

```
# 旧的文件路径
daily_commits/2024/01/2024-01-15.md

# 新的文件路径
users/account1/daily_commits/2024/01/2024-01-15.md
users/account2/daily_commits/2024/01/2024-01-15.md
users/account3/daily_commits/2024/01/2024-01-15.md
```

**优势**:
- ✅ 完全避免文件冲突
- ✅ 每个用户有独立的提交历史
- ✅ 便于管理和追踪

### 2. 🔄 自动合并PR

**功能**: 创建PR后自动合并到主分支

**流程**:
1. 创建分支和提交
2. 创建Pull Request
3. 等待2秒确保PR创建完成
4. 自动合并PR到主分支
5. 记录合并结果

**配置选项**:
```json
{
  "auto_merge": true  // 是否启用自动合并
}
```

### 3. 🗑️ 自动删除分支

**功能**: 合并成功后自动删除临时分支

**流程**:
1. PR合并成功后等待2秒
2. 删除对应的临时分支
3. 记录删除结果

**配置选项**:
```json
{
  "delete_branch_after_merge": true  // 是否删除分支
}
```

## ⚙️ 配置说明

### 完整配置示例

```json
[
  {
    "name": "account1",
    "token": "ghp_your_token_here",
    "username": "your_username1",
    "email": "your_email1@example.com",
    "repo": "auto-commit-repo-1",
    "enabled": true,
    "commit_frequency": "daily",
    "custom_schedule": [],
    "auto_merge": true,
    "delete_branch_after_merge": true
  },
  {
    "name": "account2",
    "token": "ghp_your_token_here",
    "username": "your_username2",
    "email": "your_email2@example.com",
    "repo": "auto-commit-repo-2",
    "enabled": true,
    "commit_frequency": "frequent",
    "custom_schedule": [],
    "auto_merge": false,
    "delete_branch_after_merge": false
  }
]
```

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `auto_merge` | boolean | `true` | 是否自动合并PR |
| `delete_branch_after_merge` | boolean | `true` | 合并后是否删除分支 |

## 🔧 使用方法

### 1. 更新配置文件

```bash
# 创建新的配置模板
python test_auto_merge.py --create-config

# 或手动编辑现有配置文件
vim data/accounts_config.json
```

### 2. 测试功能

```bash
# 查看功能说明
python test_auto_merge.py --info

# 测试自动合并功能
python test_auto_merge.py --test
```

### 3. 正常运行

```bash
# 运行自动提交（现在包含自动合并）
python auto_commit.py

# 或使用调度器
python scheduler.py
```

## 📊 工作流程对比

### 旧流程
```
1. 创建分支
2. 提交代码
3. 创建PR
4. ❌ 手动合并PR
5. ❌ 手动删除分支
6. ❌ 可能存在文件冲突
```

### 新流程
```
1. 创建分支
2. 提交代码到用户专属文件夹
3. 创建PR
4. ✅ 自动合并PR
5. ✅ 自动删除分支
6. ✅ 无文件冲突
```

## 🛡️ 安全性和可靠性

### 错误处理
- 每个步骤都有完整的错误处理
- 失败时会记录详细的错误信息
- 部分失败不会影响整个流程

### 日志记录
```
[account1] ✅ PR创建成功！
[account1] 📁 文件: users/account1/daily_commits/2024/01/2024-01-15.md
[account1] 🔗 PR链接: https://github.com/user/repo/pull/123
[account1] ✅ PR自动合并成功！
[account1] ✅ 分支 auto-commit-account1-20240115-143022 已删除
```

### 配置灵活性
- 可以为每个账号单独配置
- 支持禁用自动合并（仅创建PR）
- 支持禁用分支删除（保留分支）

## 🔍 故障排除

### 常见问题

**Q: 自动合并失败怎么办？**
A: 检查以下几点：
- GitHub Token 权限是否足够
- 仓库是否允许自动合并
- 网络连接是否正常
- 查看详细的错误日志

**Q: 分支删除失败怎么办？**
A: 这通常不影响主要功能，可能原因：
- 分支已被手动删除
- 权限不足
- 网络问题

**Q: 如何禁用自动合并？**
A: 在配置文件中设置：
```json
{
  "auto_merge": false,
  "delete_branch_after_merge": false
}
```

### 调试模式

```bash
# 查看详细日志
tail -f logs/auto_commit_account1.log

# 测试单个账号
python test_auto_merge.py --test
```

## 🎯 最佳实践

1. **测试环境**: 先在测试仓库中验证功能
2. **权限管理**: 确保Token有足够权限但不过度授权
3. **监控日志**: 定期检查日志文件
4. **备份配置**: 保存配置文件的备份
5. **渐进部署**: 先为部分账号启用，确认无误后全面启用

## 📈 性能优化

- 合并和删除操作之间有适当的延迟
- 错误重试机制
- 并发处理多个账号
- 最小化API调用次数

---

*更新时间: 2024-01-15*
*版本: v2.0 - 自动合并功能*