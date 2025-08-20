# 🔧 故障排除

## 常见问题

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

## 日志查看

```bash
# 查看应用日志
tail -f logs/auto_commit.log

# 查看systemd日志
sudo journalctl -u github-auto-commit -f

# 查看最近的错误
sudo journalctl -u github-auto-commit -p err
```