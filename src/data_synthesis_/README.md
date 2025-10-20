# Web Agent 数据合成系统

这个模块实现了一个完整的基于 Web Agent 的数据合成 Pipeline，用于生成高质量的训练数据。

## 核心方法

数据合成分为三个主要步骤：

### 1. Trajectory Sampling (轨迹采样)

从一个 seed 实体开始，通过迭代生成动作和观察，形成 trajectory tree。

**过程:**
- 从 seed 实体创建根节点（实体可以是人名、地名、公司、概念等）
- 对每个节点，使用 LLM 围绕该实体生成下一步的探索动作(Action)和意图(Intent)
- 执行动作获取观察结果(Observation)
- 支持多分支采样(branching factor)，形成树状结构
- **深度自适应分支**: 当深度超过 `depth_threshold` 时，分支因子自动降为1，避免树过于庞大

**公式:**
```
(O_{n-1}, I_{1}, ..., I_{n-1}) => A_{n} => (O_{n}, I_{n})
```

其中：
- `A`: Action (动作，如 web_search, web_visit)
- `I`: Intent (意图)
- `O`: Observation (观察结果)

### 2. Trajectory Selection (轨迹选择)

从 trajectory tree 中选择高质量的完整链路。

**选择标准:**
- 深度：trajectory 的步骤数
- 信息量：每步观察的内容丰富度
- 多样性：使用不同工具的多样性

**输出:**
```
(O_{1}, A_{1}, I_{1}, O_{2}, A_{2}, I_{2}, ..., O_{n}, A_{n}, I_{n})
```

### 3. QA Synthesis (问答合成)

基于选中的 trajectory，使用 LLM 合成**谜题式问答对**。

**输出:**
```
Trajectory => (Q, A)
```

其中：
- `Q`: 模糊化的多约束问题（谜题式）
- `A`: 简短的实体名称答案

**特点:**
1. **Multi-hop推理**: 需要通过多个逻辑跳跃才能得到答案
2. **问题模糊化**: 不直接提及实体名称，使用间接描述
3. **推理链设计**: 包含3-5个相互关联的约束条件，形成推理链
4. **简短答案**: 只输出实体名称本身

**Multi-hop示例:**
```
Question: "Please identify the AI organization co-founded by the entrepreneur who 
previously co-founded the online payment company that merged with Confinity, and 
which released a conversational AI tool that gained over 100 million users within 
two months."
Answer: "OpenAI"

推理链:
- Hop 1: payment company merged with Confinity → PayPal → co-founder → Elon Musk
- Hop 2: Elon Musk co-founded AI org + 100M users tool → OpenAI
```

## 系统架构

### 核心类

1. **TrajectoryNode**: 表示轨迹树中的单个节点
   - `observation`: 当前观察
   - `intent`: 产生该节点的意图
   - `action`: 产生该节点的动作
   - `parent_id`, `children_ids`: 树结构关系

2. **TrajectorySampler**: 负责采样 trajectory tree
   - `sample_trajectory_tree()`: 从 seed 任务开始采样
   - `_expand_tree()`: 递归扩展树结构
   - `_generate_next_action()`: 使用 LLM 生成下一步动作

3. **TrajectorySelector**: 负责选择高质量轨迹
   - `select_trajectories()`: 从树中选择最佳路径
   - `_score_path()`: 为路径打分

4. **QASynthesizer**: 负责合成问答对
   - `synthesize_qa()`: 基于轨迹生成 QA 对

5. **WebAgentDataSynthesis**: 主类，整合所有步骤
   - `run()`: 运行完整 pipeline
   - `save_results()`: 保存所有结果

## 使用方法

### 基本使用

```bash
# 1. 设置环境变量
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_URL="your-api-url"
export SERPER_API_KEY="your-serper-key"

# 2. 准备 seed 实体文件 (JSON 格式)
# example_seed_entities.json

# 3. 运行数据合成
python web_agent.py \
    --seed-entities example_seed_entities.json \
    --model gpt-4.1-2025-04-14 \
    --max-depth 5 \
    --branching-factor 2 \
    --max-trajectories 5 \
    --depth-threshold 3 \
    --output-dir synthesis_results
```

### 高级配置

```bash
python web_agent.py \
    --seed-entities my_entities.json \
    --model gpt-4.1-2025-04-14 \
    --max-depth 7 \              # 增加探索深度
    --branching-factor 3 \       # 增加分支因子
    --max-trajectories 10 \      # 选择更多轨迹
    --min-depth 3 \              # 最小深度要求
    --depth-threshold 4 \        # 深度阈值
    --web-search-top-k 5 \       # 搜索返回更多结果
    --output-dir results
```

### 编程方式使用

```python
from data_synthesis.web_agent import WebAgentDataSynthesis

# 创建数据合成系统
synthesizer = WebAgentDataSynthesis(
    model_name="gpt-4.1-2025-04-14",
    max_depth=5,
    branching_factor=2,
    max_trajectories=5,
    min_depth=2,
    depth_threshold=3,
    web_search_top_k=3
)

# 定义 seed 实体
seed_entities = [
    "OpenAI",
    "量子计算",
    "ChatGPT",
    "SpaceX"
]

# 运行合成 pipeline
qas = synthesizer.run(seed_entities)

# 保存结果
synthesizer.save_results(output_dir="my_results")

# 访问生成的数据
for qa in qas:
    print(f"问题: {qa.question}")
    print(f"答案: {qa.answer}")
    print(f"推理步骤数: {len(qa.reasoning_steps)}")
```

## Seed 实体格式

### JSON 列表格式

```json
[
  "实体名称 1",
  "实体名称 2",
  "实体名称 3"
]
```

### JSON 对象格式

```json
{
  "entities": [
    "OpenAI",
    "量子计算",
    "ChatGPT",
    "埃隆·马斯克",
    "区块链技术"
  ]
}
```

### 实体类型示例

适合作为 seed 实体的类型：
- **公司/组织**: OpenAI, SpaceX, Tesla, Google
- **人物**: 埃隆·马斯克, 比尔·盖茨, 李开复
- **技术/概念**: 量子计算, 人工智能, 深度学习, 区块链
- **产品**: ChatGPT, iPhone, Starlink
- **地点**: 硅谷, 中关村, 火星
- **事件**: 世界杯, 奥运会, COP28气候峰会

## 输出格式

### 1. 合成的 QA 对 (`synthesized_qa_*.jsonl`)

```jsonl
{"question": "Please identify the...", "answer": "Entity Name", "trajectory_id": "...", "reasoning_steps": [...], "metadata": {...}}
```

每条记录包含：
- `question`: 合成的谜题式问题（需要multi-hop推理）
  - 格式: "Please identify..." 或 "What is..."
  - 包含3-5个相互关联的约束条件，形成推理链
  - 不直接提及实体名称
  - 需要至少2个推理跳跃（hops）
- `answer`: **简短答案**（仅实体名称）
  - 例如: "OpenAI", "Elon Musk", "ChatGPT"
- `trajectory_id`: 对应的轨迹ID
- `reasoning_steps`: 推理步骤列表
  - `step`: 步骤编号
  - `intent`: 意图
  - `action`: 动作
  - `observation`: 观察摘要
- `metadata`: 元数据
  - `seed_entity`: 原始种子实体
  - `trajectory_depth`: 轨迹深度
  - `synthesis_date`: 合成时间

**示例:**
```json
{
  "question": "Please identify the AI organization co-founded by the entrepreneur who previously co-founded the online payment company that merged with Confinity, and which released a conversational AI tool that gained over 100 million users within two months.",
  "answer": "OpenAI",
  "trajectory_id": "traj_5",
  "reasoning_steps": [
    {
      "step": 1,
      "hop": "Hop 1: Identify Elon Musk from PayPal/Confinity",
      "intent": "找到符合'payment company merged with Confinity'的创始人",
      "action": "web_search",
      "observation": "PayPal与Confinity合并，联合创始人包括Elon Musk..."
    },
    {
      "step": 2,
      "hop": "Hop 2: Find AI org co-founded by Elon Musk with viral tool",
      "intent": "查找Elon Musk联合创立的AI组织",
      "action": "web_search",
      "observation": "OpenAI由Elon Musk等人联合创立，ChatGPT达到1亿用户..."
    }
  ],
  "metadata": {...}
}
```

### 2. Trajectories (`trajectories_*.json`)

```json
[
  {
    "trajectory_id": "traj_0",
    "seed_entity": "OpenAI",
    "total_depth": 5,
    "nodes": [
      {
        "node_id": "node_1_0",
        "observation": "...",
        "intent": "...",
        "action": {...},
        "parent_id": "node_0_0",
        "children_ids": [],
        "depth": 1
      },
      ...
    ]
  },
  ...
]
```

### 3. 统计信息 (`statistics_*.json`)

```json
{
  "total_qas": 25,
  "total_trajectories": 25,
  "total_nodes": 150,
  "avg_trajectory_depth": 4.5,
  "model_name": "gpt-4.1-2025-04-14",
  "timestamp": "20250418_123456"
}
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--seed-entities` | Seed 实体文件路径 | 必需 |
| `--model` | LLM 模型名称 | gpt-4.1-2025-04-14 |
| `--max-depth` | Trajectory 最大深度 | 5 |
| `--branching-factor` | 每个节点的分支数（浅层） | 2 |
| `--depth-threshold` | 深度阈值，超过后分支因子降为1 | 3 |
| `--max-trajectories` | 每个 seed 实体最多选择的轨迹数 | 5 |
| `--min-depth` | Trajectory 最小深度 | 2 |
| `--output-dir` | 输出目录 | synthesis_results |
| `--web-search-top-k` | Web 搜索返回结果数 | 3 |

## 工作流程示例

```
Seed Entity: "OpenAI"
           |
           v
    [Trajectory Sampling]
    围绕"OpenAI"进行多角度探索
           |
    +------+------+
    |             |
   Node 1       Node 2
   (搜索基本信息)  (搜索最新动态)
   |             |
   +------+      +------+
   |      |      |      |
  N3     N4     N5     N6
  (访问官网) (搜索产品) (访问新闻) (搜索研究)
  |      |      |      |
  ...   ...    ...    ...
  
           |
           v
  [Trajectory Selection]
  - 选择高质量路径
  - 评分排序
           |
           v
  Selected Trajectories:
  1. Root -> N1(基本信息) -> N3(官网) -> N7(产品详情)
  2. Root -> N2(最新动态) -> N5(新闻) -> N8(深度报道)
  ...
           |
           v
  [QA Synthesis]
  - 为每条轨迹生成 QA
           |
           v
  Output (Multi-hop谜题式问答):
  - Q: "Please identify the organization co-founded by the entrepreneur who previously co-founded PayPal, located in the city home to the Golden Gate Bridge, and released a chatbot in 2022."
  - A: "OpenAI"
  - Hops: PayPal founder → Elon Musk → Elon's AI org in SF → OpenAI
```

## 注意事项

1. **API 密钥**: 确保设置了正确的环境变量
   - `OPENAI_API_KEY`
   - `OPENAI_API_URL` 或 `OPENAI_API_BASE`
   - `SERPER_API_KEY`

2. **成本考虑**: 
   - 每个 seed 实体会生成一个 trajectory tree
   - API 调用次数与树的复杂度相关
   - 使用 `depth_threshold` 可以有效控制成本
   - 建议从小规模开始测试（例如先测试2-3个实体）

3. **质量 vs 数量**:
   - 增加 `max_depth` 和 `branching_factor` 可以生成更丰富的轨迹
   - 但也会增加成本和时间
   - `depth_threshold` 可以在保证前期充分探索的同时减少后期分支
   - 推荐配置: `max_depth=5, branching_factor=2, depth_threshold=3`

4. **深度阈值机制**:
   - 前期（深度 < threshold）: 使用完整的 `branching_factor`，广泛探索
   - 后期（深度 >= threshold）: 分支因子降为1，深入单一路径
   - 例如: `branching_factor=2, depth_threshold=3` 表示：
     - 深度0-2: 每个节点2个分支
     - 深度3+: 每个节点1个分支
   - 这样可以在保证探索广度的同时控制树的大小

5. **网络要求**:
   - 需要稳定的网络连接访问 OpenAI API 和 Serper API
   - Web 访问需要能够爬取网页内容

## 示例输出

查看 `example_seed_entities.json` 获取示例 seed 实体。

运行后会在 `synthesis_results/` 目录下生成：
- `synthesized_qa_*.jsonl`: 合成的问答对
- `trajectories_*.json`: 完整的轨迹数据
- `statistics_*.json`: 统计信息

## 故障排查

### 问题: "SERPER_API_KEY not configured"
**解决**: 设置环境变量 `export SERPER_API_KEY="your-key"`

### 问题: "生成动作失败"
**原因**: LLM 输出格式不正确
**解决**: 系统会自动重试，增加温度参数

### 问题: "No trajectories selected"
**原因**: 生成的轨迹深度不足
**解决**: 减小 `--min-depth` 参数或增加 `--max-depth`

### 问题: 运行时间过长
**原因**: `max_depth` 和 `branching_factor` 设置过大
**解决**: 减小这两个参数，或者减少 seed 实体数量

## 扩展和定制

### 自定义评分函数

修改 `TrajectorySelector._score_path()` 方法来实现自定义的轨迹评分逻辑。

### 添加新的 Action 类型

如果 WebEnvironment 支持更多工具，系统会自动识别并使用。

### 自定义 QA 合成 Prompt

修改 `QASynthesizer.synthesize_qa()` 中的 prompt 来控制生成的 QA 格式和风格。

## 参考文档

- **[PUZZLE_QA_GUIDE.md](PUZZLE_QA_GUIDE.md)**: Multi-hop推理谜题式问答对生成详细指南
  - Multi-hop推理概念和重要性
  - 5种核心推理策略（关系链、属性链、时间序列、因果链、交叉验证）
  - 信息模糊化技巧
  - 约束条件设计策略
  - 问题模板和示例
  - 质量控制清单

- **[DEPTH_THRESHOLD.md](DEPTH_THRESHOLD.md)**: 深度阈值机制详解
  - 工作原理和优势
  - 配置建议
  - 成本分析

## 方法论

基于以下核心方法实现：
- **Trajectory Sampling with Relationship-Aware Exploration**: 
  - 优先收集关系链信息（人物、组织、因果关系）
  - 动态分支控制（depth threshold）
  
- **Multi-criteria Trajectory Selection**: 
  - 基于深度、信息量和多样性的评分
  
- **Multi-hop Reasoning QA Synthesis**: 
  - 需要至少2个推理跳跃
  - 使用模糊化和推理链设计
  - 5种推理策略（关系链、属性链、时间序列、因果链、交叉验证）

## 许可

与主项目 AgentFlow 保持一致。

