# 并行处理功能说明

## 概述

数据合成系统现在支持并行处理多个seeds，可以显著提升处理速度。通过配置文件中的 `max_workers` 参数来控制并行度。

## 配置参数

在配置文件（如 `configs/web_config.json`）中添加 `max_workers` 参数：

```json
{
  "environment_mode": "web",
  "max_depth": 10,
  "branching_factor": 2,
  ...
  "max_workers": 4
}
```

### max_workers 参数说明

- **值为 1**: 串行处理模式（默认），按顺序处理每个seed
- **值 > 1**: 并行处理模式，同时处理多个seeds
  - 建议值: 2-8，取决于你的CPU核心数和API限制
  - 过高的值可能导致API限流或内存占用过大

## 使用方法

### 方法 1: 使用并行启动脚本

```bash
# 使用web配置（并行度在配置文件中设置）
./run_parallel_synthesis.sh web example_seed_entities.json synthesis_results

# 使用自定义配置
./run_parallel_synthesis.sh custom configs/web_config_parallel.json example_seed_entities.json
```

### 方法 2: 直接运行Python脚本

```bash
python synthesis_pipeline_multi.py \
    --config configs/web_config_parallel.json \
    --seeds example_seed_entities.json \
    --output-dir synthesis_results
```

## 并行处理特性

### 自动处理

1. **进程池管理**: 使用 `ProcessPoolExecutor` 实现真正的并行处理
2. **线程安全写入**: QA结果实时保存，使用文件锁确保数据完整性
3. **错误隔离**: 单个seed失败不影响其他seeds的处理
4. **进度追踪**: 实时显示已完成的seeds数量

### 性能提升

假设处理单个seed需要60秒：

| Seeds数量 | 串行模式 (workers=1) | 并行模式 (workers=4) | 加速比 |
|----------|---------------------|---------------------|--------|
| 10       | 600秒 (~10分钟)      | 180秒 (~3分钟)       | 3.3x   |
| 20       | 1200秒 (~20分钟)     | 360秒 (~6分钟)       | 3.3x   |
| 100      | 6000秒 (~100分钟)    | 1800秒 (~30分钟)     | 3.3x   |

注意：实际加速比取决于I/O等待时间、API响应速度和系统资源。

## 配置示例

### 示例1: Web环境 - 并行4个workers

```json
{
  "environment_mode": "web",
  "environment_kwargs": {
    "web_search_top_k": 3
  },
  "available_tools": ["web_search", "web_visit"],
  "max_depth": 10,
  "branching_factor": 2,
  "max_workers": 4
}
```

### 示例2: Math环境 - 串行处理

```json
{
  "environment_mode": "math",
  "environment_kwargs": {},
  "available_tools": ["calculator"],
  "max_depth": 4,
  "branching_factor": 2,
  "max_workers": 1
}
```

### 示例3: Python环境 - 并行2个workers

```json
{
  "environment_mode": "python",
  "environment_kwargs": {},
  "available_tools": ["python_interpreter"],
  "max_depth": 4,
  "branching_factor": 2,
  "max_workers": 2
}
```

## 输出文件

无论使用串行还是并行模式，输出文件格式保持一致：

```
synthesis_results/
├── synthesized_qa_web_20251031_123456.jsonl    # QA对（实时追加）
├── trajectories_web_20251031_123456.json       # 所有轨迹
└── statistics_web_20251031_123456.json         # 统计信息
```

## 注意事项

### API限流

如果你的API提供商有请求速率限制，请注意：

- **并行度过高**可能触发限流，导致请求失败
- 建议从 `max_workers=2` 开始，逐步增加
- 监控API响应，如果频繁出现429错误，降低并行度

### 内存使用

- 每个worker会创建独立的环境和组件
- 并行度越高，内存占用越大
- 建议监控系统内存使用情况

### 结果顺序

- 并行处理时，结果按**完成顺序**写入，不保证与seeds输入顺序一致
- 每个QA对都有 `source_id` 标识其来源seed

## 故障排查

### 问题1: 并行处理比串行还慢

可能原因：
- API响应速度慢，I/O等待占主要时间
- 并行度设置过高，导致频繁上下文切换
- 系统CPU/内存资源不足

解决方案：
- 降低 `max_workers` 值
- 检查网络连接和API响应时间
- 监控系统资源使用

### 问题2: 频繁出现API错误

可能原因：
- 触发了API限流
- 并发请求过多

解决方案：
- 降低 `max_workers` 值
- 联系API提供商了解限流政策
- 考虑添加请求间隔

### 问题3: 某些seeds失败

- 并行处理会隔离错误，失败的seeds不影响其他seeds
- 查看控制台输出，找到失败的seed和错误信息
- 可以单独重新处理失败的seeds

## 最佳实践

1. **首次使用**: 从 `max_workers=1` 开始，验证配置正确
2. **小规模测试**: 用少量seeds测试并行性能，找到最佳 `max_workers` 值
3. **生产环境**: 根据API限制和系统资源，设置合适的并行度（通常2-8）
4. **监控日志**: 关注控制台输出，及时发现问题
5. **增量处理**: 对于大量seeds，可以分批处理，降低风险

## 与原版本的兼容性

- 原始的 `synthesis_pipeline.py` 保持不变，仍然可用
- `synthesis_pipeline_multi.py` 是并行增强版本
- 两个版本的配置文件格式兼容
- 如果配置文件中没有 `max_workers` 参数，默认为1（串行模式）

## 技术实现

- **并行框架**: `concurrent.futures.ProcessPoolExecutor`
- **进程隔离**: 每个seed在独立进程中处理
- **线程安全**: 使用 `threading.Lock` 保护文件写入
- **错误处理**: 进程级异常捕获，不影响其他进程

## 更新日志

- **2025-10-31**: 添加并行处理支持
  - 新增 `max_workers` 配置参数
  - 创建 `run_parallel_synthesis.sh` 启动脚本
  - 更新所有配置文件模板
  - 添加进度追踪和线程安全文件写入

