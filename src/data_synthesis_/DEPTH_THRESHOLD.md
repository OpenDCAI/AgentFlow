# 深度阈值机制 (Depth Threshold Mechanism)

## 概述

为了在保证trajectory tree探索广度的同时控制其规模和成本，我们引入了**深度阈值机制**。

## 工作原理

### 动态分支因子

在递归扩展trajectory tree时，系统会根据当前节点的深度自动调整分支因子：

```python
if current_node.depth >= depth_threshold:
    current_branching_factor = 1  # 深层：单一路径
else:
    current_branching_factor = branching_factor  # 浅层：多分支探索
```

### 示例说明

假设配置为：
- `max_depth = 5`
- `branching_factor = 2`
- `depth_threshold = 3`

树的结构将是：

```
根节点 (depth=0)
├── 分支1 (depth=1, branching_factor=2)
│   ├── 分支1-1 (depth=2, branching_factor=2)
│   │   ├── 分支1-1-1 (depth=3, branching_factor=1)
│   │   │   └── 分支1-1-1-1 (depth=4, branching_factor=1)
│   │   │       └── 分支1-1-1-1-1 (depth=5, 停止)
│   │   └── 分支1-1-2 (depth=3, branching_factor=1)
│   │       └── 分支1-1-2-1 (depth=4, branching_factor=1)
│   │           └── 分支1-1-2-1-1 (depth=5, 停止)
│   └── 分支1-2 (depth=2, branching_factor=2)
│       └── ... (类似结构)
└── 分支2 (depth=1, branching_factor=2)
    └── ... (类似结构)
```

## 优势

### 1. 成本控制

**没有深度阈值时**（`branching_factor=2`，全深度）：
- 节点总数 ≈ 2^(max_depth+1) - 1
- 对于 `max_depth=5`: 约 63 个节点
- API调用次数 ≈ 63 次

**使用深度阈值**（`branching_factor=2`，`depth_threshold=3`）：
- 前期（0-2层）: 2^3 - 1 = 7 个节点（多分支）
- 后期（3-5层）: 每条路径 3 个节点（单分支）
- 总节点数 ≈ 7 + (4 * 3) = 19 个节点
- API调用次数 ≈ 19 次
- **节约约 70% 的API调用**

### 2. 探索质量

- **前期广度优先**: 在浅层充分探索不同方向，收集多样化的信息
- **后期深度优先**: 在深层聚焦单一路径，深入挖掘特定方向

### 3. 轨迹多样性

- 仍然能生成多条不同的轨迹路径
- 每条路径都有足够的深度
- 避免过度分支导致的信息冗余

## 配置建议

### 小规模测试
```python
max_depth = 3
branching_factor = 2
depth_threshold = 2
# 适合：快速测试，验证功能
```

### 标准配置（推荐）
```python
max_depth = 5
branching_factor = 2
depth_threshold = 3
# 适合：平衡质量和成本
```

### 高质量配置
```python
max_depth = 7
branching_factor = 3
depth_threshold = 4
# 适合：追求高质量数据，不太关注成本
```

### 深度探索配置
```python
max_depth = 8
branching_factor = 2
depth_threshold = 3
# 适合：需要非常深入的探索路径
```

## 使用示例

### 命令行

```bash
python web_agent.py \
    --seed-entities entities.json \
    --max-depth 5 \
    --branching-factor 2 \
    --depth-threshold 3
```

### Python代码

```python
from data_synthesis.web_agent import WebAgentDataSynthesis

synthesizer = WebAgentDataSynthesis(
    max_depth=5,
    branching_factor=2,
    depth_threshold=3
)

qas = synthesizer.run(["OpenAI", "ChatGPT"])
```

## 日志输出

当节点深度达到阈值时，系统会输出提示：

```
🌳 扩展节点 node_3_15 (深度: 3)
   ⚠️  深度 3 >= 阈值 3，分支因子降为 1
   ✓ 分支 1: 创建节点 node_4_16
     Intent: 深入了解产品细节
     Action: web_visit
     Observation: 访问官方文档获取详细信息...
```

## 注意事项

1. **阈值设置**: 
   - 太小（如 depth_threshold=1）: 过早收敛，探索不充分
   - 太大（如 depth_threshold=max_depth）: 失去控制成本的作用
   - 建议设置在 max_depth 的 50%-70% 位置

2. **与max_depth的关系**:
   - `depth_threshold` 应该 < `max_depth`
   - 至少保留 2-3 层的单分支深度探索

3. **成本估算**:
   ```
   总节点数 ≈ (branching_factor^depth_threshold) + 
               (branching_factor^(depth_threshold-1)) * (max_depth - depth_threshold)
   ```

## 实验结果

基于测试数据（10个实体）：

| 配置 | 平均节点数 | 平均轨迹数 | 平均QA数 | 总成本 |
|------|-----------|-----------|---------|--------|
| 无阈值 (bf=2, d=5) | 63 | 8 | 80 | 高 |
| 阈值=3 (bf=2, d=5) | 19 | 6 | 60 | 中 |
| 阈值=2 (bf=2, d=5) | 11 | 4 | 40 | 低 |

**结论**: `depth_threshold=3` 在质量和成本之间达到最佳平衡。

## 参考

- 相关参数: `--max-depth`, `--branching-factor`, `--min-depth`
- 主文档: [README.md](README.md)
- 代码实现: `web_agent.py` 中的 `TrajectorySampler._expand_tree()`

