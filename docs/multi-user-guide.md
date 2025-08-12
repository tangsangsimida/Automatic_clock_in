# 多用户同时提交到一个仓库使用指南

## 概述

本项目支持多个GitHub用户同时向同一个仓库提交代码，这在以下场景中非常有用：
- 团队协作开发
- 多人维护同一项目
- 开源项目贡献
- 提高仓库的活跃度和多样性
- 分布式团队开发

## 配置方法

### 1. 基本配置结构

在 `data/accounts_config.json` 中配置多个用户账号指向同一个仓库：

```json
{
  "accounts": [
    {
      "name": "主开发者",
      "token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "username": "developer1",
      "email": "dev1@example.com",
      "repo": "owner/shared-repo",
      "enabled": true,
      "commit_frequency": "high",
      "custom_schedule": "0 9,14,18 * * *",
      "description": "主要开发账号"
    },
    {
      "name": "协作开发者",
      "token": "ghp_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
      "username": "developer2",
      "email": "dev2@example.com",
      "repo": "owner/shared-repo",
      "enabled": true,
      "commit_frequency": "medium",
      "custom_schedule": "0 10,15,19 * * *",
      "description": "协作开发账号"
    },
    {
      "name": "测试工程师",
      "token": "ghp_zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz",
      "username": "tester1",
      "email": "test@example.com",
      "repo": "owner/shared-repo",
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
- **不同用户名**：每个账号使用不同的 `username`，对应不同的GitHub用户
- **协作者权限**：⚠️ **重要**：仓库所有者必须将所有协作用户添加为仓库的Collaborator

#### 时间调度
- **错开时间**：使用不同的 `custom_schedule` 避免同时提交(建议)
- **频率差异**：设置不同的 `commit_frequency` 模拟真实的协作模式(建议)

#### 身份区分
- **不同邮箱**：每个账号使用不同的 `email`
- **不同用户名**：每个账号使用不同的 `username`，对应真实的GitHub用户
- **不同名称**：通过 `name` 字段区分不同账号的用途
- **描述标识**：在 `description` 中标明账号用途和角色

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

**添加协作者步骤**：
1. 进入目标仓库页面
2. 点击 `Settings` 选项卡
3. 在左侧菜单中选择 `Collaborators and teams`
4. 点击 `Add people` 按钮
5. 输入协作者的GitHub用户名或邮箱
6. 选择权限级别：
   - **Write**：可以推送代码、创建分支、管理Issues和PR
   - **Maintain**：Write权限 + 管理仓库设置
   - **Admin**：完全控制权限
7. 发送邀请，协作者接受后即可获得权限

**权限级别建议**：
- **主开发者**：Admin 或 Maintain
- **协作开发者**：Write
- **测试人员**：Write

#### Token权限
每个账号的Token需要包含以下权限：
- `repo` - 完整的仓库访问权限
- `user:email` - 访问用户邮箱信息
- `read:user` - 读取用户基本信息

## ⚠️ 重要配置要求

### 协作者权限设置

**必要条件**：要实现多个用户提交到同一个仓库，必须满足以下条件：

1. **仓库权限**：所有协作用户必须被添加为仓库的Collaborator
2. **Token权限**：每个用户的Token必须有足够的权限访问目标仓库
3. **配置正确性**：确保每个账号的 `username` 对应真实的GitHub用户名

**配置验证**：
```json
// ✅ 正确配置示例
{
  "username": "developer1",        // 真实的GitHub用户名
  "repo": "owner/shared-repo",     // 目标仓库
  "token": "ghp_xxx..."            // 该用户的有效Token
}
```

**权限验证步骤**：
1. 确认用户已被添加为仓库协作者
2. 验证Token具有仓库访问权限
3. 测试提交权限是否正常

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

