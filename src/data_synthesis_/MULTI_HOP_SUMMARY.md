# Multi-hop推理数据合成系统 - 功能总结

## 🎯 核心目标

生成需要**多步推理（Multi-hop Reasoning）**的高质量问答对，答案简短（仅实体名称），问题模糊且需要推理链。

## ✨ 主要特性

### 1. Multi-hop推理设计

**什么是Multi-hop?**
- 需要通过2个或更多逻辑跳跃才能得到答案
- 每一步基于前一步的结果
- 不能直接从问题推导到答案

**示例对比:**

❌ **单跳问题（太简单）:**
```
Q: "What company did Sam Altman found that released ChatGPT?"
A: "OpenAI"
推理: Sam Altman创立 → OpenAI (1步)
```

✅ **多跳问题（符合要求）:**
```
Q: "Please identify the AI organization co-founded by the entrepreneur who 
    previously co-founded the online payment company that merged with Confinity."
A: "OpenAI"
推理链:
  Hop 1: payment company + Confinity → PayPal → co-founder → Elon Musk
  Hop 2: Elon Musk co-founded AI organization → OpenAI
```

### 2. 五种推理策略

#### 策略A: 关系链推理 (Relationship Chain)
通过中间实体建立连接

**模式**: A的关系 → 中间实体B → B的关系 → 目标C

**示例**:
```
Q: "Please identify the organization co-founded by the entrepreneur who 
    founded Tesla and SpaceX, which released a viral AI chatbot in 2022."
A: "OpenAI"
Hops: Tesla/SpaceX → Elon Musk → AI org + chatbot → OpenAI
```

#### 策略B: 属性推理链 (Attribute Chain)
通过属性组合逐步缩小范围

**模式**: 属性1 → 范围1 → 属性2 → 范围2 → 最终答案

**示例**:
```
Q: "What emerged from a non-profit founded in the mid-2010s, transitioned 
    to capped-profit, and gained 100M users fastest?"
A: "OpenAI"
Hops: non-profit 2010s → several orgs → capped-profit → fewer orgs → 
      100M record → OpenAI
```

#### 策略C: 时间序列推理 (Temporal Chain)
通过时间顺序的事件链

**模式**: 早期事件 → 中期转变 → 近期结果

**示例**:
```
Q: "Please identify the entity that started as a research initiative in 2015, 
    underwent structural change in 2019, and launched products dominating 
    headlines in 2022-2023."
A: "OpenAI"
Hops: 2015 initiative → 2019 change → 2022-2023 products
```

#### 策略D: 因果推理链 (Causal Chain)
通过因果关系连接

**模式**: 原因/动机 → 行动 → 结果/影响

**示例**:
```
Q: "What organization founded due to AI safety concerns, established a lab 
    in SF, that developed technology used by hundreds of millions?"
A: "OpenAI"
Hops: AI safety concerns → SF lab → popular technology
```

#### 策略E: 交叉验证推理 (Cross-validation Chain)
同时满足多个维度的条件

**模式**: 维度1 ∩ 维度2 ∩ 维度3

**示例**:
```
Q: "Please identify the company founded by a YC president, backed by 
    Microsoft, in Salesforce's city, launching in Nov 2022 with record adoption."
A: "OpenAI"
Hops: YC president → Sam Altman; SF location; Microsoft backing; 
      Nov 2022 → combine all → OpenAI
```

## 🏗️ 系统架构改进

### Trajectory Sampling (轨迹采样)

**优化重点**: 优先收集关系链信息

```python
**高优先级 - 关系链信息**:
- 人物关系: 创始人及其背景（之前创立的其他公司）
- 组织关系: 合作伙伴、投资方
- 时间关系: 前身、演变历史
- 因果关系: 成立原因、产生影响

**探索策略**:
- 寻找可以形成推理链的信息
- 收集中间实体信息（作为推理桥梁）
- 例如：创始人 → 创始人的其他公司 → 那些公司的特征
```

### QA Synthesis (问答合成)

**Multi-hop Prompt设计**:

```python
关键要求:
1. 必须包含至少2个推理跳跃（hop）
2. 约束条件应形成逻辑链（不是独立的）
3. 使用间接、模糊的描述
4. 答案必须简短（仅实体名称）

提供5种策略示例：
- 关系链
- 属性链
- 时间序列
- 因果链
- 交叉验证
```

## 📊 输出格式

### 问答对结构

```json
{
  "question": "Please identify the AI organization co-founded by the 
               entrepreneur who previously co-founded PayPal...",
  "answer": "OpenAI",
  "trajectory_id": "traj_5",
  "reasoning_steps": [
    {
      "step": 1,
      "hop": "Hop 1: PayPal co-founder → Elon Musk",
      "intent": "识别PayPal联合创始人",
      "action": "web_search",
      "observation": "PayPal由Elon Musk等人创立..."
    },
    {
      "step": 2,
      "hop": "Hop 2: Elon Musk的AI组织 → OpenAI",
      "intent": "查找Elon Musk联合创立的AI公司",
      "action": "web_search",
      "observation": "OpenAI由Elon Musk等人联合创立..."
    }
  ],
  "metadata": {
    "seed_entity": "OpenAI",
    "trajectory_depth": 4,
    "synthesis_date": "2025-01-18T..."
  }
}
```

## 🔧 关键配置

### 推荐配置

```bash
python web_agent.py \
    --seed-entities example_seed_entities.json \
    --max-depth 5 \              # 足够深度收集关系信息
    --branching-factor 2 \       # 前期充分探索
    --depth-threshold 1 \        # 早期降低分支，节省成本
    --max-trajectories 5 \       # 为每个实体生成多条轨迹
    --min-depth 2                # 保证足够推理深度
```

### 参数说明

| 参数 | 作用 | Multi-hop相关 |
|------|------|--------------|
| `depth-threshold` | 控制树的分支 | 设为1-2可节省成本，同时保证收集足够关系信息 |
| `max-depth` | 最大探索深度 | 5-7较合适，能收集多层关系 |
| `branching-factor` | 前期分支数 | 2-3即可，重点是深度而非广度 |

## 📈 质量标准

### 优质Multi-hop问答的特征

✅ **好的示例**:
```
Q: "Please identify the company founded by the person who led Y Combinator, 
    in the city with the Golden Gate Bridge, that released a tool gaining 
    100M users in 2 months."
A: "OpenAI"

特点:
- 3个推理跳跃（YC → Sam Altman; SF; 100M tool → ChatGPT/OpenAI）
- 约束条件相互关联
- 信息模糊化（YC president而非Sam Altman名字）
- 答案简短
```

❌ **不好的示例**:
```
Q: "What is OpenAI's main product?"
A: "ChatGPT"

问题:
- 0个推理跳跃（直接问答）
- 没有模糊化（直接提及OpenAI）
- 太简单
```

### 检查清单

- [ ] 需要至少2个推理跳跃？
- [ ] 约束条件形成逻辑链（不是独立的）？
- [ ] 没有直接提及答案实体名称？
- [ ] 所有线索都模糊化了？
- [ ] 答案只是实体名称（无解释）？
- [ ] 基于轨迹中的真实信息？
- [ ] 推理路径清晰？

## 🎓 使用示例

### 完整流程

```python
from data_synthesis.web_agent import WebAgentDataSynthesis

# 1. 创建系统
synthesizer = WebAgentDataSynthesis(
    max_depth=5,
    branching_factor=2,
    depth_threshold=1,  # 重要：早期降低分支
    max_trajectories=5
)

# 2. 准备实体（选择有丰富关系的实体）
seed_entities = [
    "OpenAI",           # 有创始人、投资方、产品等多重关系
    "Elon Musk",        # 创立多家公司，关系链丰富
    "ChatGPT",          # 有母公司、竞争对手、用户规模等
    "Quantum Computing" # 有发展历史、应用领域、研究者等
]

# 3. 运行合成
qas = synthesizer.run(seed_entities)

# 4. 检查结果
for qa in qas:
    print(f"Question: {qa.question}")
    print(f"Answer: {qa.answer}")
    print(f"Hops: {len([s for s in qa.reasoning_steps if 'hop' in s])}")
    print()

# 5. 保存
synthesizer.save_results()
```

## 📚 相关文档

- **[PUZZLE_QA_GUIDE.md](PUZZLE_QA_GUIDE.md)**: 详细的Multi-hop推理策略和示例
- **[DEPTH_THRESHOLD.md](DEPTH_THRESHOLD.md)**: 深度阈值机制说明
- **[README.md](README.md)**: 系统总体文档

## 🔬 技术亮点

1. **关系链优先**: Trajectory采样优先收集人物、组织、因果等关系信息
2. **5种推理策略**: 系统性地覆盖不同类型的Multi-hop推理
3. **动态分支控制**: 通过depth_threshold平衡探索和成本
4. **模糊化技术**: 系统性地将具体信息转化为间接描述
5. **推理链验证**: 在reasoning_steps中明确标注每个hop

## 💡 最佳实践

### 实体选择

**适合的实体特征**:
- 有多个创始人/领导者
- 与其他知名实体有关联
- 有清晰的发展历程
- 产生了重要影响或产品

**示例**:
```
✅ 好: OpenAI, SpaceX, Elon Musk, ChatGPT
   （关系丰富，可以构建多种推理链）

❌ 差: 小众概念，孤立实体
   （关系少，难以构建推理链）
```

### 成本优化

```bash
# 测试阶段（低成本）
--max-depth 3 --branching-factor 2 --depth-threshold 1

# 生产阶段（平衡）
--max-depth 5 --branching-factor 2 --depth-threshold 1

# 高质量阶段（追求质量）
--max-depth 7 --branching-factor 3 --depth-threshold 2
```

## 🎉 总结

本系统通过以下创新实现了高质量Multi-hop推理问答对的自动化生成：

1. **关系链优先的信息收集策略**
2. **5种系统化的Multi-hop推理策略**
3. **模糊化和推理链设计的Prompt工程**
4. **动态分支控制的成本优化**

生成的数据适用于：
- 测试AI模型的推理能力
- 训练需要多步推理的模型
- 评估知识整合和关系理解能力



