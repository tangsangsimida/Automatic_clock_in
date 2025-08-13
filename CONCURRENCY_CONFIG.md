# 并发控制配置说明

本文档说明了GitHub自动打卡系统中的并发控制配置参数，这些参数可以帮助您优化多账户并发提交时的性能和稳定性。

## 配置位置

并发控制配置位于 `config.py` 文件中的 `CONCURRENCY_CONFIG` 字典。

## 配置参数详解

### 基础并发设置

- **`max_workers`** (默认: 3)
  - 最大并发线程数
  - 建议值: 2-5
  - 说明: 过高的并发数可能导致GitHub API限制和更多冲突

- **`base_delay_range`** (默认: (1.5, 3.0))
  - 基础延迟范围（秒）
  - 说明: 每个账户启动前的随机延迟时间范围
  - 用途: 避免多个账户同时开始操作

### 重试机制设置

- **`max_retries_per_account`** (默认: 3)
  - 每个账户的最大重试次数
  - 建议值: 2-5
  - 说明: 当检测到冲突时，每个账户最多重试的次数

- **`retry_delay_range`** (默认: (3.0, 8.0))
  - 重试延迟范围（秒）
  - 说明: 重试前的随机等待时间范围
  - 用途: 给其他账户更多时间完成操作

### PR合并设置

- **`merge_retry_count`** (默认: 8)
  - PR合并的最大重试次数
  - 建议值: 5-10
  - 说明: PR合并失败时的重试次数

- **`merge_retry_backoff`** (默认: 1.5)
  - PR合并重试的退避系数
  - 说明: 每次重试的等待时间会按此系数递增
  - 计算公式: `wait_time = base_time * (backoff_factor ^ attempt)`

### 智能重试设置

- **`enable_smart_retry`** (默认: True)
  - 启用智能重试机制
  - 说明: 只对检测到的冲突进行重试，其他错误直接失败

- **`conflict_detection_keywords`** (默认: 见配置文件)
  - 冲突检测关键词列表
  - 说明: 用于识别是否为合并冲突的关键词
  - 可根据实际遇到的错误信息进行调整

## 调优建议

### 高并发场景（5+账户）
```python
CONCURRENCY_CONFIG = {
    "max_workers": 2,  # 降低并发数
    "base_delay_range": (2.0, 5.0),  # 增加基础延迟
    "retry_delay_range": (5.0, 12.0),  # 增加重试延迟
    "max_retries_per_account": 5,  # 增加重试次数
    # ... 其他配置保持默认
}
```

### 低延迟场景（2-3账户）
```python
CONCURRENCY_CONFIG = {
    "max_workers": 3,
    "base_delay_range": (0.5, 1.5),  # 减少基础延迟
    "retry_delay_range": (2.0, 5.0),  # 减少重试延迟
    "max_retries_per_account": 2,  # 减少重试次数
    # ... 其他配置保持默认
}
```

### 网络不稳定场景
```python
CONCURRENCY_CONFIG = {
    "max_workers": 2,  # 降低并发数
    "merge_retry_count": 12,  # 增加PR合并重试次数
    "merge_retry_backoff": 2.0,  # 增加退避系数
    # ... 其他配置保持默认
}
```

## 监控和调试

1. **查看日志**: 系统会记录详细的重试和冲突信息
2. **成功率统计**: 关注最终的成功/失败统计
3. **调整策略**: 根据实际运行情况调整参数

## 常见问题

**Q: 为什么还会出现PR合并冲突？**
A: 即使文件路径不同，GitHub的合并机制仍可能检测到冲突。通过增加延迟和重试可以缓解此问题。

**Q: 如何减少API调用次数？**
A: 降低 `max_workers` 和增加 `base_delay_range`，减少并发请求。

**Q: 重试次数设置多少合适？**
A: 建议根据账户数量调整：2-3个账户设置2-3次，5+账户设置3-5次。