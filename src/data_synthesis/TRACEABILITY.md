# 数据追溯系统说明

## 概述

数据合成系统现在包含完整的追溯标识系统，可以从QA对完全追溯回原始的seed数据。

## 追溯链条

```
Source (Seed) → Trajectory → QA
     ↓              ↓          ↓
  source_id ← source_id   qa_id
                    ↓          ↓
            trajectory_id ← trajectory_id
```

## 唯一标识符详解

### 1. Source ID (源标识)

**格式**: `src_{timestamp}_{index}_{hash}`

**示例**: `src_20251030123456_0001_a3f2e8d1`

**组成部分**:
- `timestamp`: 处理时间戳 (YYYYMMDDHHmmss)
- `index`: seed在批次中的序号 (4位数字，补零)
- `hash`: seed内容的MD5哈希前8位

**用途**: 唯一标识每个原始seed数据

### 2. Trajectory ID (轨迹标识)

**格式**: `{source_id}_traj_{index}`

**示例**: `src_20251030123456_0001_a3f2e8d1_traj_0`

**组成部分**:
- `source_id`: 所属的source ID
- `index`: trajectory在该source下的序号

**用途**: 唯一标识从seed生成的每条trajectory

### 3. QA ID (问答对标识)

**格式**: `{trajectory_id}_qa_{index}`

**示例**: `src_20251030123456_0001_a3f2e8d1_traj_0_qa_0`

**组成部分**:
- `trajectory_id`: 所属的trajectory ID
- `index`: QA在该trajectory下的序号

**用途**: 唯一标识生成的每个QA对

## 数据模型中的追溯字段

### TrajectoryNode
```python
node_id: str              # 节点ID (如 "d1_t0_b0")
parent_id: str            # 父节点ID
```

### Trajectory
```python
trajectory_id: str        # 轨迹ID (包含source_id)
source_id: str           # 源seed的ID
seed_data: str           # 原始seed内容
nodes: List[TrajectoryNode]  # 节点序列
```

### SynthesizedQA
```python
qa_id: str               # QA对的唯一ID
trajectory_id: str       # 来源trajectory的ID
source_id: str          # 源seed的ID
question: str           # 问题
answer: str            # 答案
metadata: dict         # 包含seed_data等元信息
```

## 追溯示例

### 1. 从QA追溯到Trajectory

```python
# 加载QA数据
with open("synthesized_qa_web_20251030.jsonl") as f:
    for line in f:
        qa = json.loads(line)
        trajectory_id = qa["trajectory_id"]
        print(f"QA {qa['qa_id']} 来自 Trajectory {trajectory_id}")
```

### 2. 从Trajectory追溯到Source

```python
# 加载trajectory数据
with open("trajectories_web_20251030.json") as f:
    trajectories = json.load(f)
    for traj in trajectories:
        source_id = traj["source_id"]
        seed_data = traj["seed_data"]
        print(f"Trajectory {traj['trajectory_id']} 来自 Source {source_id}: {seed_data}")
```

### 3. 完整追溯链

```python
# 给定一个QA ID，完整追溯
qa_id = "src_20251030123456_0001_a3f2e8d1_traj_0_qa_0"

# 从QA文件中找到QA
qa = find_qa_by_id(qa_id)  
print(f"QA: {qa['question']}")

# 使用trajectory_id找到trajectory
trajectory = find_trajectory_by_id(qa["trajectory_id"])
print(f"Trajectory: {len(trajectory['nodes'])} steps")

# 使用source_id找到原始seed
source_id = trajectory["source_id"]
seed_data = trajectory["seed_data"]
print(f"Source: {source_id} = {seed_data}")
```

## 文件结构

生成的文件包含完整的追溯信息：

### synthesized_qa_*.jsonl
```json
{
  "qa_id": "src_20251030123456_0001_a3f2e8d1_traj_0_qa_0",
  "trajectory_id": "src_20251030123456_0001_a3f2e8d1_traj_0",
  "source_id": "src_20251030123456_0001_a3f2e8d1",
  "question": "...",
  "answer": "...",
  "reasoning_steps": [...],
  "metadata": {
    "seed_data": "original seed content",
    "synthesis_date": "2025-10-30T12:34:56",
    ...
  }
}
```

### trajectories_*.json
```json
[
  {
    "trajectory_id": "src_20251030123456_0001_a3f2e8d1_traj_0",
    "source_id": "src_20251030123456_0001_a3f2e8d1",
    "seed_data": "original seed content",
    "total_depth": 5,
    "nodes": [
      {
        "node_id": "d1_t0_b0",
        "parent_id": "d0_t0_b0",
        "observation": "...",
        "action": {...}
      }
    ]
  }
]
```

## 追溯工具函数示例

```python
def trace_qa_to_source(qa_file: str, traj_file: str, qa_id: str):
    """从QA ID追溯到原始source"""
    # 加载QA
    with open(qa_file) as f:
        for line in f:
            qa = json.loads(line)
            if qa["qa_id"] == qa_id:
                print(f"✓ 找到QA: {qa['question'][:50]}...")
                
                # 加载trajectory
                with open(traj_file) as tf:
                    trajs = json.load(tf)
                    for traj in trajs:
                        if traj["trajectory_id"] == qa["trajectory_id"]:
                            print(f"✓ 找到Trajectory: {len(traj['nodes'])} steps")
                            print(f"✓ Source ID: {traj['source_id']}")
                            print(f"✓ Original Seed: {traj['seed_data']}")
                            return {
                                "qa": qa,
                                "trajectory": traj,
                                "source_id": traj["source_id"],
                                "seed_data": traj["seed_data"]
                            }
    return None
```

## 使用建议

1. **数据分析**: 使用source_id分组分析不同seed的生成效果
2. **质量检查**: 通过trajectory_id关联QA与其生成路径
3. **错误追踪**: 发现问题QA时可以快速定位到源数据
4. **数据去重**: 基于source_id识别重复处理的seed
5. **统计分析**: 计算每个source生成的trajectory和QA数量

## 时间戳说明

所有的source_id中包含处理时间戳，格式为YYYYMMDDHHmmss。这使得：
- 可以按时间排序和过滤数据
- 同一批次处理的数据有相近的时间戳
- 便于管理和归档不同批次的数据

## 注意事项

1. **唯一性保证**: source_id通过时间戳+索引+内容hash保证唯一
2. **层级关系**: ID命名体现了清晰的层级关系
3. **易读性**: ID格式便于人工阅读和理解
4. **可扩展性**: 如需添加新的追溯层级，可以继续扩展ID格式

