# 追溯系统实例演示

## 完整的数据流示例

### 输入: 3个Seed实体

```json
["Paris", "Albert Einstein", "Python programming"]
```

---

## 数据生成过程

### Seed 1: "Paris"

#### Source ID生成
```
输入: "Paris"
时间: 2025-10-30 12:34:56
序号: 1
Hash: md5("Paris")[:8] = "a3f2e8d1"

生成的Source ID:
src_20251030123456_0001_a3f2e8d1
```

#### 生成的Trajectories

**Trajectory 1**:
```json
{
  "trajectory_id": "src_20251030123456_0001_a3f2e8d1_traj_0",
  "source_id": "src_20251030123456_0001_a3f2e8d1",
  "seed_data": "Paris",
  "total_depth": 5,
  "nodes": [
    {
      "node_id": "d1_t0_b0",
      "intent": "Search for basic information about Paris",
      "action": {"tool_name": "search", "parameters": {"query": "Paris"}},
      "observation": "Paris is the capital and most populous city of France..."
    },
    {
      "node_id": "d2_t1_b0",
      "intent": "Get more details about Paris population",
      "action": {"tool_name": "search", "parameters": {"query": "Paris population"}},
      "observation": "The population of Paris is approximately 2.2 million..."
    },
    ...
  ]
}
```

**Trajectory 2**:
```json
{
  "trajectory_id": "src_20251030123456_0001_a3f2e8d1_traj_1",
  "source_id": "src_20251030123456_0001_a3f2e8d1",
  "seed_data": "Paris",
  "total_depth": 4,
  "nodes": [...]
}
```

**Trajectory 3**:
```json
{
  "trajectory_id": "src_20251030123456_0001_a3f2e8d1_traj_2",
  "source_id": "src_20251030123456_0001_a3f2e8d1",
  "seed_data": "Paris",
  "total_depth": 6,
  "nodes": [...]
}
```

#### 生成的QA对

**QA 1** (from Trajectory 0):
```json
{
  "qa_id": "src_20251030123456_0001_a3f2e8d1_traj_0_qa_0",
  "trajectory_id": "src_20251030123456_0001_a3f2e8d1_traj_0",
  "source_id": "src_20251030123456_0001_a3f2e8d1",
  "question": "What is the population of Paris and what is it known for?",
  "answer": "Paris has a population of approximately 2.2 million people. It is known as the capital of France and is famous for landmarks like the Eiffel Tower.",
  "reasoning_steps": [
    {
      "step": 1,
      "description": "Search for basic information about Paris",
      "action": "search",
      "observation": "Found that Paris is the capital of France"
    },
    {
      "step": 2,
      "description": "Get population data",
      "action": "search",
      "observation": "Population is approximately 2.2 million"
    }
  ],
  "metadata": {
    "seed_data": "Paris",
    "trajectory_depth": 5,
    "synthesis_date": "2025-10-30T12:35:10"
  }
}
```

**QA 2** (from Trajectory 1):
```json
{
  "qa_id": "src_20251030123456_0001_a3f2e8d1_traj_1_qa_0",
  "trajectory_id": "src_20251030123456_0001_a3f2e8d1_traj_1",
  "source_id": "src_20251030123456_0001_a3f2e8d1",
  "question": "Which famous monuments are located in Paris?",
  "answer": "Paris is home to famous monuments including the Eiffel Tower, Notre-Dame Cathedral, and the Louvre Museum.",
  "reasoning_steps": [...],
  "metadata": {
    "seed_data": "Paris",
    "trajectory_depth": 4,
    "synthesis_date": "2025-10-30T12:35:20"
  }
}
```

**QA 3** (from Trajectory 2):
```json
{
  "qa_id": "src_20251030123456_0001_a3f2e8d1_traj_2_qa_0",
  "trajectory_id": "src_20251030123456_0001_a3f2e8d1_traj_2",
  "source_id": "src_20251030123456_0001_a3f2e8d1",
  "question": "What is the climate like in Paris?",
  "answer": "Paris has an oceanic climate with mild temperatures year-round...",
  "reasoning_steps": [...],
  "metadata": {
    "seed_data": "Paris",
    "trajectory_depth": 6,
    "synthesis_date": "2025-10-30T12:35:30"
  }
}
```

---

### Seed 2: "Albert Einstein"

#### Source ID生成
```
输入: "Albert Einstein"
时间: 2025-10-30 12:35:45
序号: 2
Hash: md5("Albert Einstein")[:8] = "b4e3f9c2"

生成的Source ID:
src_20251030123545_0002_b4e3f9c2
```

#### 生成的Trajectories和QAs
```
Trajectory IDs:
- src_20251030123545_0002_b4e3f9c2_traj_0
- src_20251030123545_0002_b4e3f9c2_traj_1
- src_20251030123545_0002_b4e3f9c2_traj_2

QA IDs:
- src_20251030123545_0002_b4e3f9c2_traj_0_qa_0
- src_20251030123545_0002_b4e3f9c2_traj_1_qa_0
- src_20251030123545_0002_b4e3f9c2_traj_2_qa_0
```

---

### Seed 3: "Python programming"

#### Source ID生成
```
输入: "Python programming"
时间: 2025-10-30 12:36:30
序号: 3
Hash: md5("Python programming")[:8] = "c5f4a0d3"

生成的Source ID:
src_20251030123630_0003_c5f4a0d3
```

---

## 追溯示例

### 示例1: 从QA ID追溯到Source

给定QA ID: `src_20251030123456_0001_a3f2e8d1_traj_0_qa_0`

#### 步骤1: 从QA ID提取Trajectory ID
```
QA ID:         src_20251030123456_0001_a3f2e8d1_traj_0_qa_0
                                                          └─ 去掉 "_qa_0"
Trajectory ID: src_20251030123456_0001_a3f2e8d1_traj_0
```

#### 步骤2: 从Trajectory ID提取Source ID
```
Trajectory ID: src_20251030123456_0001_a3f2e8d1_traj_0
                                                 └─ 去掉 "_traj_0"
Source ID:     src_20251030123456_0001_a3f2e8d1
```

#### 步骤3: 从Source ID解析信息
```
Source ID: src_20251030123456_0001_a3f2e8d1
           │   │              │    │
           │   │              │    └─ 内容hash
           │   │              └────── 第1个seed
           │   └───────────────────── 2025-10-30 12:34:56
           └───────────────────────── Source前缀

最终追溯到:
- 时间: 2025-10-30 12:34:56
- 批次序号: 1
- 原始内容: "Paris" (通过查找seed_data字段)
```

---

## 完整追溯树状图

```
Seed Batch (3 seeds)
│
├─ Seed 1: "Paris"
│  │
│  ├─ source_id: src_20251030123456_0001_a3f2e8d1
│  │
│  ├─ Trajectory 0: src_20251030123456_0001_a3f2e8d1_traj_0
│  │  └─ QA 0: src_20251030123456_0001_a3f2e8d1_traj_0_qa_0
│  │     Question: "What is the population of Paris..."
│  │
│  ├─ Trajectory 1: src_20251030123456_0001_a3f2e8d1_traj_1
│  │  └─ QA 0: src_20251030123456_0001_a3f2e8d1_traj_1_qa_0
│  │     Question: "Which famous monuments are located..."
│  │
│  └─ Trajectory 2: src_20251030123456_0001_a3f2e8d1_traj_2
│     └─ QA 0: src_20251030123456_0001_a3f2e8d1_traj_2_qa_0
│        Question: "What is the climate like in Paris..."
│
├─ Seed 2: "Albert Einstein"
│  │
│  ├─ source_id: src_20251030123545_0002_b4e3f9c2
│  │
│  ├─ Trajectory 0: src_20251030123545_0002_b4e3f9c2_traj_0
│  │  └─ QA 0: src_20251030123545_0002_b4e3f9c2_traj_0_qa_0
│  │
│  ├─ Trajectory 1: src_20251030123545_0002_b4e3f9c2_traj_1
│  │  └─ QA 0: src_20251030123545_0002_b4e3f9c2_traj_1_qa_0
│  │
│  └─ Trajectory 2: src_20251030123545_0002_b4e3f9c2_traj_2
│     └─ QA 0: src_20251030123545_0002_b4e3f9c2_traj_2_qa_0
│
└─ Seed 3: "Python programming"
   │
   ├─ source_id: src_20251030123630_0003_c5f4a0d3
   │
   ├─ Trajectory 0: src_20251030123630_0003_c5f4a0d3_traj_0
   │  └─ QA 0: src_20251030123630_0003_c5f4a0d3_traj_0_qa_0
   │
   ├─ Trajectory 1: src_20251030123630_0003_c5f4a0d3_traj_1
   │  └─ QA 0: src_20251030123630_0003_c5f4a0d3_traj_1_qa_0
   │
   └─ Trajectory 2: src_20251030123630_0003_c5f4a0d3_traj_2
      └─ QA 0: src_20251030123630_0003_c5f4a0d3_traj_2_qa_0
```

---

## 实际使用命令

### 1. 查看统计信息

```bash
$ python trace_utils.py \
    synthesis_results/synthesized_qa_web_20251030.jsonl \
    synthesis_results/trajectories_web_20251030.json

================================================================================
数据统计
================================================================================

总QA数: 9
总Trajectory数: 9
总Source数: 3

每个Source的数据量:
  src_20251030123456_0001_a3f2e8d1: 3 trajectories → 3 QAs
  src_20251030123545_0002_b4e3f9c2: 3 trajectories → 3 QAs
  src_20251030123630_0003_c5f4a0d3: 3 trajectories → 3 QAs
================================================================================
```

### 2. 追溯特定QA

```bash
$ python trace_utils.py \
    synthesis_results/synthesized_qa_web_20251030.jsonl \
    synthesis_results/trajectories_web_20251030.json \
    src_20251030123456_0001_a3f2e8d1_traj_0_qa_0

================================================================================
完整追溯链条: src_20251030123456_0001_a3f2e8d1_traj_0_qa_0
================================================================================

✓ 找到QA: What is the population of Paris and what is it known for?
✓ 找到Trajectory: src_20251030123456_0001_a3f2e8d1_traj_0
  - 深度: 5 步
  - 节点数: 5
✓ 追溯到Source: src_20251030123456_0001_a3f2e8d1
  - 原始内容: Paris

📝 QA层:
  ID: src_20251030123456_0001_a3f2e8d1_traj_0_qa_0
  问题: What is the population of Paris and what is it known for?
  答案: Paris has a population of approximately 2.2 million people...
  推理步骤: 2 步

🛤️  Trajectory层:
  ID: src_20251030123456_0001_a3f2e8d1_traj_0
  深度: 5
  节点详情:
    步骤 1:
      意图: Search for basic information about Paris
      工具: search
      观察: Paris is the capital and most populous city of France...
    步骤 2:
      意图: Get population data
      工具: search
      观察: Population is approximately 2.2 million...
    ...

🌱 Source层:
  ID: src_20251030123456_0001_a3f2e8d1
  原始Seed: Paris
  元信息: {'seed_data': 'Paris', 'synthesis_date': '2025-10-30T12:35:10', ...}

================================================================================
```

### 3. Python API使用

```python
from trace_utils import DataTracer

# 初始化
tracer = DataTracer(
    "synthesis_results/synthesized_qa_web_20251030.jsonl",
    "synthesis_results/trajectories_web_20251030.json"
)

# 追溯QA
result = tracer.trace_qa_to_source("src_20251030123456_0001_a3f2e8d1_traj_0_qa_0")
print(f"原始Seed: {result['seed_data']}")  # 输出: Paris

# 获取某个source的所有QA
qas = tracer.get_qas_by_source("src_20251030123456_0001_a3f2e8d1")
print(f"生成了 {len(qas)} 个QA")  # 输出: 生成了 3 个QA

# 统计信息
stats = tracer.get_statistics()
print(f"总共 {stats['total_sources']} 个sources")  # 输出: 总共 3 个sources
```

---

## 关键优势

### 1. ID自解释性
```
src_20251030123456_0001_a3f2e8d1_traj_0_qa_0
│   │              │    │         │      │
│   │              │    │         │      └─ 立即知道这是第0个QA
│   │              │    │         └──────── 立即知道这是第0个trajectory
│   │              │    └────────────────── 立即知道内容hash
│   │              └─────────────────────── 立即知道这是第1个seed
│   └────────────────────────────────────── 立即知道生成时间
└────────────────────────────────────────── 立即知道这是source数据
```

### 2. 快速过滤
```python
# 按时间过滤
morning_qas = [qa for qa in qas if "20251030" in qa['qa_id'] and int(qa['qa_id'].split('_')[1][8:14]) < 120000]

# 按source过滤
source_1_qas = [qa for qa in qas if qa['source_id'].endswith('_0001_a3f2e8d1')]
```

### 3. 数据完整性验证
```python
# 验证每个QA都能追溯到trajectory
for qa in qas:
    traj = tracer.find_trajectory_by_id(qa['trajectory_id'])
    assert traj is not None, f"QA {qa['qa_id']} 无法追溯到trajectory"
    assert traj['source_id'] == qa['source_id'], f"Source ID不匹配"
```

这个追溯系统让数据血统一目了然，极大提升了数据质量管理和问题追踪的效率！

