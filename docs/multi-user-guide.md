# 多Token同时提交到一个仓库使用指南

## 概述

本项目支持使用多个GitHub Token以同一用户身份向同一个仓库提交代码，这在以下场景中非常有用：
- 多设备开发环境
- Token备份和容错
- 时间分散的自动提交
- 提高仓库活跃度的真实性
- 多环境部署自动化

## 配置方法

### 1. 基本配置结构

在 `data/accounts_config.json` 中配置多个账号指向同一个仓库：

```json
{
  "accounts": [
    {
      "name": "主开发者",
      "token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "username": "shared-owner",
      "email": "dev1@example.com",
      "repo": "shared-owner/shared-repo",
      "enabled": true,
      "commit_frequency": "high",
      "custom_schedule": "0 9,14,18 * * *",
      "description": "主要开发账号"
    },
    {
      "name": "协作开发者",
      "token": "ghp_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
      "username": "shared-owner",
      "email": "dev2@example.com",
      "repo": "shared-owner/shared-repo",
      "enabled": true,
      "commit_frequency": "medium",
      "custom_schedule": "0 10,15,19 * * *",
      "description": "协作开发账号"
    },
    {
      "name": "测试账号",
      "token": "ghp_zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz",
      "username": "shared-owner",
      "email": "test@example.com",
      "repo": "shared-owner/shared-repo",
      "enabled": true,
      "commit_frequency": "low",
      "custom_schedule": "0 16 * * *",
      "description": "测试提交账号"
    }
  ]
}
```

### 2. 关键配置说明

#### 仓库配置
- **相同仓库**：所有账号的 `repo` 字段设置为同一个仓库
- **相同用户名**：⚠️ **重要**：所有账号的 `username` 字段必须相同，且与 `repo` 中的用户名一致
- **不同权限**：确保所有账号都有该仓库的写入权限

#### 时间调度
- **错开时间**：使用不同的 `custom_schedule` 避免同时提交(建议)
- **频率差异**：设置不同的 `commit_frequency` 模拟真实的协作模式(建议)

#### 身份区分
- **不同邮箱**：每个账号使用不同的 `email`
- **相同用户名**：⚠️ **注意**：所有账号必须使用相同的 `username`，这是技术限制
- **不同名称**：通过 `name` 字段区分不同账号的用途
- **描述标识**：在 `description` 中标明账号用途

## 最佳实践

### 1. 时间安排策略

```json
// 推荐的时间安排模式
{
  "主开发者": "0 9,14,18 * * *",    // 上午9点、下午2点、晚上6点
  "协作开发者": "0 10,15,19 * * *",  // 上午10点、下午3点、晚上7点
  "测试账号": "0 16 * * *"          // 下午4点
}
```

### 2. 提交频率建议

- **主开发者**：`high` - 每天多次提交
- **协作开发者**：`medium` - 每天1-2次提交
- **测试/维护账号**：`low` - 每天1次或更少

### 3. 权限管理

#### GitHub仓库设置
1. 将所有协作账号添加为仓库的 Collaborator
2. 设置适当的权限级别（Write 或 Admin）
3. 确保仓库允许多人推送

#### Token权限
每个账号的Token需要包含以下权限：
- `repo` - 完整的仓库访问权限
- `user:email` - 访问用户邮箱信息
- `read:user` - 读取用户基本信息

## ⚠️ 重要技术限制

### username 和 repo 字段的匹配要求

**关键限制**：要实现多个账号提交到同一个仓库，必须满足以下条件：

1. **username 字段必须相同**：所有账号的 `username` 字段必须设置为相同的值
2. **repo 字段匹配**：`repo` 字段中的用户名部分必须与 `username` 字段一致
3. **示例说明**：
   ```json
   // ✅ 正确配置
   {
     "username": "shared-owner",
     "repo": "shared-owner/my-repo"
   }
   
   // ❌ 错误配置
   {
     "username": "user1",
     "repo": "shared-owner/my-repo"  // username 与 repo 中的用户名不匹配
   }
   ```

**技术原因**：
- 系统使用 `username` 字段来确定提交者身份
- `repo` 字段用于确定目标仓库
- 两者必须匹配才能正确执行 Git 操作

**实际应用**：
- 这意味着多个账号实际上是使用不同的 Token 以同一个用户身份提交
- 通过不同的 `email` 和 `name` 字段来区分提交记录
- 适用于一个用户拥有多个 Token 或多个设备的场景

## 注意事项

### 1. 安全考虑

- **Token安全**：每个Token都要妥善保管，不要泄露
- **权限最小化**：只给予必要的仓库权限
- **定期轮换**：定期更新Token以提高安全性

### 2. 避免冲突

- **时间错开**：避免多个账号同时提交造成冲突
- **分支策略**：考虑使用不同分支进行开发
- **文件分离**：不同账号修改不同的文件区域

### 3. 合规性

- **遵守GitHub ToS**：确保使用方式符合GitHub服务条款
- **团队协议**：在团队内部明确多账号使用规则
- **透明度**：保持提交记录的真实性和可追溯性

## 监控和管理

### 1. 查看运行状态

```bash
# 查看所有账号状态
./run.sh --status

# 查看特定账号日志
./run.sh --logs account_name

# 测试所有账号配置
./run.sh --test-config
```

### 2. 动态管理

```bash
# 启用/禁用特定账号
./run.sh --enable account_name
./run.sh --disable account_name

# 重新加载配置
./run.sh --reload

# 立即执行一次提交
./run.sh --run-once account_name
```

### 3. 日志分析

系统会为每个账号生成独立的日志文件：
```
logs/
├── main_developer.log
├── collaborator.log
└── tester.log
```

## 故障排除

### 常见问题

1. **权限被拒绝**
   - 检查Token是否有效
   - 确认账号是否有仓库写入权限

2. **提交冲突**
   - 调整时间调度避免同时提交
   - 检查是否有网络延迟导致的时间偏差

3. **账号被限制**
   - 检查GitHub API限制
   - 适当降低提交频率

### 调试命令

```bash
# 测试单个账号
./run.sh --test-account account_name

# 查看详细错误信息
./run.sh --debug

# 验证仓库权限
./run.sh --check-permissions
```

