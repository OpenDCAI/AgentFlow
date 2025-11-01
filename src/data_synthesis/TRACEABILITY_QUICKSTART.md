# 追溯系统快速上手

## 快速开始

### 1. 运行数据合成（已自动包含追溯标识）

```bash
python synthesis_pipeline.py \
    --config configs/web_config.json \
    --seeds example_seed_entities.json \
    --output-dir synthesis_results
```

生成的文件会自动包含所有追溯标识。

### 2. 查看生成的数据

```bash
# 查看QA数据（每行一个JSON对象）
cat synthesis_results/synthesized_qa_web_20251030.jsonl | head -1 | jq .

# 查看Trajectory数据
cat synthesis_results/trajectories_web_20251030.json | jq '.[0]'
```

### 3. 使用追溯工具

#### 查看统计信息

```bash
python trace_utils.py \
    synthesis_results/synthesized_qa_web_20251030.jsonl \
    synthesis_results/trajectories_web_20251030.json
```

输出示例：
```
================================================================================
数据统计
================================================================================

总QA数: 15
总Trajectory数: 15
总Source数: 5

每个Source的数据量:
  src_20251030123456_0001_a3f2e8d1: 3 trajectories → 3 QAs
  src_20251030123456_0002_b4e3f9c2: 3 trajectories → 3 QAs
  src_20251030123456_0003_c5f4a0d3: 3 trajectories → 3 QAs
  ...
================================================================================
```

#### 追溯特定QA

```bash
python trace_utils.py \
    synthesis_results/synthesized_qa_web_20251030.jsonl \
    synthesis_results/trajectories_web_20251030.json \
    src_20251030123456_0001_a3f2e8d1_traj_0_qa_0
```

输出示例：
```
================================================================================
完整追溯链条: src_20251030123456_0001_a3f2e8d1_traj_0_qa_0
================================================================================

✓ 找到QA: What is the capital of France?
✓ 找到Trajectory: src_20251030123456_0001_a3f2e8d1_traj_0
  - 深度: 5 步
  - 节点数: 5
✓ 追溯到Source: src_20251030123456_0001_a3f2e8d1
  - 原始内容: Paris

📝 QA层:
  ID: src_20251030123456_0001_a3f2e8d1_traj_0_qa_0
  问题: What is the capital of France?
  答案: The capital of France is Paris...
  推理步骤: 3 步

🛤️  Trajectory层:
  ID: src_20251030123456_0001_a3f2e8d1_traj_0
  深度: 5
  节点详情:
    步骤 1:
      意图: Search for information about Paris
      工具: search
      观察: Paris is the capital and most populous city of France...
    ...

🌱 Source层:
  ID: src_20251030123456_0001_a3f2e8d1
  原始Seed: Paris
  元信息: {...}
================================================================================
```

### 4. 在Python中使用追溯API

```python
from trace_utils import DataTracer

# 初始化追溯器
tracer = DataTracer(
    qa_file="synthesis_results/synthesized_qa_web_20251030.jsonl",
    trajectory_file="synthesis_results/trajectories_web_20251030.json"
)

# 方法1: 完整追溯
result = tracer.trace_qa_to_source("src_20251030123456_0001_a3f2e8d1_traj_0_qa_0")
print(f"原始Seed: {result['seed_data']}")
print(f"QA问题: {result['qa']['question']}")

# 方法2: 查找某个source的所有QA
source_id = "src_20251030123456_0001_a3f2e8d1"
qas = tracer.get_qas_by_source(source_id)
print(f"Source {source_id} 生成了 {len(qas)} 个QA")

# 方法3: 获取统计信息
stats = tracer.get_statistics()
print(f"总共有 {stats['total_sources']} 个sources")
```

## 追溯标识格式说明

### Source ID
```
src_20251030123456_0001_a3f2e8d1
│   │              │    │
│   │              │    └─ 内容hash（8位）
│   │              └────── 序号（4位）
│   └───────────────────── 时间戳（YYYYMMDDHHmmss）
└───────────────────────── 前缀
```

### Trajectory ID
```
src_20251030123456_0001_a3f2e8d1_traj_0
│                                │    │
└─ Source ID                     │    └─ trajectory序号
                                 └────── 分隔符
```

### QA ID
```
src_20251030123456_0001_a3f2e8d1_traj_0_qa_0
│                                       │  │
└─ Trajectory ID                        │  └─ QA序号
                                        └──── 分隔符
```

## 常见使用场景

### 场景1: 分析某个seed的效果

```python
tracer = DataTracer(qa_file, traj_file)

# 获取该source的所有trajectories和QAs
source_id = "src_20251030123456_0001_a3f2e8d1"
trajs = tracer.get_trajectories_by_source(source_id)
qas = tracer.get_qas_by_source(source_id)

print(f"Seed生成了 {len(trajs)} 条trajectories")
print(f"总共产出 {len(qas)} 个QA对")

# 分析trajectory质量
avg_depth = sum(t['total_depth'] for t in trajs) / len(trajs)
print(f"平均深度: {avg_depth}")
```

### 场景2: QA质量检查

```python
# 当发现某个QA质量有问题时，快速定位到源数据
qa_id = "problematic_qa_id"
result = tracer.trace_qa_to_source(qa_id)

if result:
    print(f"问题QA来自seed: {result['seed_data']}")
    print(f"Trajectory有 {result['trajectory']['total_depth']} 步")
    
    # 检查trajectory的节点
    for node in result['trajectory']['nodes']:
        print(f"  {node['intent']}")
```

### 场景3: 批量统计分析

```python
tracer = DataTracer(qa_file, traj_file)
stats = tracer.get_statistics()

# 找出产出最多的source
source_qa_counts = stats['qas_per_source']
top_source = max(source_qa_counts.items(), key=lambda x: x[1])
print(f"产出最多的source: {top_source[0]} ({top_source[1]} QAs)")

# 找出产出最少的source
bottom_source = min(source_qa_counts.items(), key=lambda x: x[1])
print(f"产出最少的source: {bottom_source[0]} ({bottom_source[1]} QAs)")
```

### 场景4: 数据去重检查

```python
# 通过source_id检查是否有重复处理的seed
from collections import Counter

tracer = DataTracer(qa_file, traj_file)
qas = tracer._load_qas()

# 统计每个source出现的次数
source_counts = Counter(qa['source_id'] for qa in qas)

# 找出可能的重复
duplicates = {k: v for k, v in source_counts.items() if v > 10}
if duplicates:
    print(f"发现可能重复的sources: {duplicates}")
```

## 文件位置

- **追溯系统说明**: `TRACEABILITY.md` - 完整的技术文档
- **追溯工具**: `trace_utils.py` - Python工具库
- **本指南**: `TRACEABILITY_QUICKSTART.md` - 快速上手指南

## 注意事项

1. 所有ID都是自动生成的，无需手动管理
2. ID中的时间戳精确到秒，可用于时间排序
3. 内容hash保证了即使时间戳相同也不会冲突
4. 所有生成的数据文件都包含完整的追溯信息

