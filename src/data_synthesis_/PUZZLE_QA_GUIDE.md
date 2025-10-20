# Multi-hop推理谜题式问答对生成指南 (Multi-hop Reasoning Puzzle QA Guide)

## 概述

本系统专门设计用于生成**需要multi-hop推理的谜题式问答对**，这类问答对的特点是：
1. 问题使用间接的、模糊的描述
2. 需要通过**多个推理跳跃（hops）**才能得到答案
3. 包含相互关联的约束条件，形成推理链
4. 答案简短，通常只是实体名称

## 设计理念

### 什么是Multi-hop推理？

**Multi-hop推理**指需要通过多个逻辑跳跃（hops）才能得到答案的推理过程，每一步都基于前一步的结果。

**单跳推理（Single-hop）示例**：
```
Q: "What company founded by Sam Altman released ChatGPT?"
A: "OpenAI"
推理: Sam Altman创立 → OpenAI （1步直接推理）
```

**多跳推理（Multi-hop）示例**：
```
Q: "Please identify the AI organization co-founded by the entrepreneur who previously 
    co-founded the online payment company that merged with Confinity."
A: "OpenAI"
推理链:
  Hop 1: payment company merged with Confinity → PayPal → co-founder → Elon Musk
  Hop 2: Elon Musk co-founded AI organization → OpenAI
```

### 为什么使用Multi-hop推理问答？

1. **显著提高难度**: 需要多步推理，不能直接从问题推导答案
2. **测试深度推理能力**: 要求模型建立推理链，而非简单匹配
3. **更接近真实场景**: 复杂问题往往需要多步骤思考
4. **避免记忆依赖**: 需要理解关系和逻辑，而非直接记忆
5. **评估知识整合能力**: 需要综合不同来源的信息

### 与传统问答的对比

**传统问答:**
```
Q: "OpenAI公司是什么时候成立的？它的主要产品有哪些？"
A: "OpenAI成立于2015年12月，总部位于旧金山。主要产品包括GPT系列大语言模型（GPT-3、GPT-4）、
    ChatGPT对话系统、DALL-E图像生成系统等。公司由Sam Altman等人创立..."
```

**谜题式问答:**
```
Q: "Please identify the AI research organization founded in the mid-2010s in San Francisco, 
    known for developing a viral conversational AI tool in late 2022, and backed by a major 
    tech company starting with 'M'."
A: "OpenAI"
```

## Multi-hop推理问题设计策略

### 核心策略类型

#### 策略A：关系链推理（Relationship Chain）

通过中间实体建立连接，是最常用的multi-hop策略。

**结构**: 实体A的关系 → 中间实体B → 中间实体B的关系 → 目标实体C

**示例1**:
```
Question: "Please identify the organization co-founded by the entrepreneur who also 
founded Tesla and SpaceX, which released a viral AI chatbot in late 2022."
Answer: "OpenAI"

推理链:
- Hop 1: "founded Tesla and SpaceX" → 识别出Elon Musk
- Hop 2: "Elon Musk co-founded" + "AI chatbot late 2022" → OpenAI
```

**示例2**:
```
Question: "What is the company started by the person who previously led Y Combinator, 
located in the city home to the Golden Gate Bridge?"
Answer: "OpenAI"

推理链:
- Hop 1: "led Y Combinator" → Sam Altman
- Hop 2: "Sam Altman started" + "Golden Gate Bridge city (SF)" → OpenAI
```

#### 策略B：属性推理链（Attribute Chain）

通过属性组合逐步缩小范围。

**结构**: 属性1 → 中间结论1 → 属性2 → 中间结论2 → 最终答案

**示例**:
```
Question: "What technology emerged from a non-profit founded in the mid-2010s, which 
later transitioned to a capped-profit model, and developed a system that reached 
100 million users faster than any previous platform?"
Answer: "OpenAI"

推理链:
- Hop 1: "non-profit mid-2010s" → 筛选出若干组织
- Hop 2: "transitioned to capped-profit" → 进一步缩小范围
- Hop 3: "100M users fastest" → 确定为OpenAI/ChatGPT
```

#### 策略C：时间序列推理（Temporal Chain）

通过时间顺序的事件链建立联系。

**结构**: 早期事件 → 中期转变 → 近期结果

**示例**:
```
Question: "Please identify the entity that started as a research initiative in 2015, 
underwent a structural change around 2019 to enable profit distribution, and subsequently 
released products that dominated tech headlines in 2022-2023."
Answer: "OpenAI"

推理链:
- Hop 1: "2015 research initiative" → OpenAI成立
- Hop 2: "2019 structural change" → 转变为capped-profit
- Hop 3: "2022-2023 products" → ChatGPT等产品
```

#### 策略D：因果推理链（Causal Chain）

通过因果关系连接各个元素。

**结构**: 原因/动机 → 行动 → 结果/影响

**示例**:
```
Question: "What organization was founded due to concerns about AI safety from tech 
leaders, which led to establishing a research lab in San Francisco, that later developed 
technology powering a system used by hundreds of millions?"
Answer: "OpenAI"

推理链:
- Hop 1: "AI safety concerns" → 动机 → OpenAI成立
- Hop 2: "SF research lab" → OpenAI的形式
- Hop 3: "system used by hundreds of millions" → ChatGPT
```

#### 策略E：交叉验证推理（Cross-validation Chain）

需要同时满足来自不同维度的多个条件。

**结构**: 维度1约束 ∩ 维度2约束 ∩ 维度3约束

**示例**:
```
Question: "Please identify the company that: was founded by someone who previously 
led a major startup accelerator, is backed by the world's largest software company, 
operates in the same city as Salesforce's headquarters, and launched a product in 
November 2022 that gained unprecedented user adoption rates."
Answer: "OpenAI"

推理链:
- Hop 1: "led startup accelerator" → Sam Altman
- Hop 2: "backed by largest software company" → Microsoft
- Hop 3: "same city as Salesforce (SF)" + "November 2022 product" → OpenAI/ChatGPT
```

## 问题生成技巧

### 1. 信息模糊化技巧

#### 时间模糊化
```
具体信息                    -> 模糊化描述
"2015年12月"                -> "mid-2010s" / "21世纪第二个十年"
"2022年11月30日"            -> "late 2022" / "2022年底"
"1960-1980年代"             -> "between the 1960s and 1980s"
"持续了3年"                 -> "spanning approximately three years"
```

#### 数量模糊化
```
具体信息                    -> 模糊化描述
"48集"                      -> "fewer than 50 episodes"
"超过1000名员工"            -> "employs over a thousand people"
"市值100亿美元"             -> "valued in the tens of billions"
"3个主要产品"               -> "has released multiple flagship products"
```

#### 地理位置模糊化
```
具体信息                    -> 模糊化描述
"旧金山"                    -> "Bay Area" / "Northern California"
"硅谷"                      -> "tech hub in California"
"美国"                      -> "North American country"
```

#### 名称模糊化
```
具体信息                    -> 模糊化描述
"微软(Microsoft)"           -> "major tech company starting with 'M'"
"Sam Altman"                -> "a former president of a startup accelerator"
"ChatGPT"                   -> "a viral conversational AI tool"
```

#### 类别/特征模糊化
```
具体信息                    -> 模糊化描述
"人工智能研究公司"          -> "an organization focused on AI safety"
"打破第四面墙"              -> "occasionally breaks the fourth wall"
"幽默风格"                  -> "is known for his humor"
```

### 2. Multi-hop约束条件设计

对于multi-hop问题，约束条件不是独立的，而是**形成推理链**。每个问题应包含 **3-5个相互关联的约束条件**。

#### 约束条件的维度

1. **时间约束**: 成立时间、活跃时期、重要事件时间
2. **地理约束**: 位置、起源地、总部所在地
3. **规模约束**: 员工数、产品数、收入规模
4. **关系约束**: 创始人、合作伙伴、投资方
5. **产品/作品约束**: 代表性产品、重要项目
6. **特征约束**: 独特特点、标志性元素、风格
7. **历史事件约束**: 重要里程碑、转折点
8. **领域约束**: 所属行业、细分领域

#### 示例：设计Multi-hop约束条件

**实体**: OpenAI

**收集的具体信息（强调关系链）**:
- 成立于2015年12月
- 创始人之一：Elon Musk（也创立了Tesla、SpaceX）
- 创始人之一：Sam Altman（曾任Y Combinator总裁）
- 总部在旧金山（金门大桥所在城市）
- 2022年11月发布ChatGPT（2个月内达到1亿用户）
- 微软是主要投资方（全球最大软件公司）
- 从非营利转变为capped-profit模式

**设计Multi-hop推理链**:

**方案1 - 关系链（2-hop）**:
```
约束设计:
1. "co-founded by the entrepreneur who also founded Tesla and SpaceX" 
   → Hop 1: 识别Elon Musk
2. "released a viral AI chatbot in late 2022"
   → Hop 2: Elon Musk co-founded + chatbot → OpenAI

最终问题:
"Please identify the AI organization co-founded by the entrepreneur who also 
founded Tesla and SpaceX, which released a viral AI chatbot in late 2022."
```

**方案2 - 多重关系链（3-hop）**:
```
约束设计:
1. "founded in the city home to the Golden Gate Bridge"
   → Hop 1: 识别旧金山
2. "by someone who previously led a prominent startup accelerator"
   → Hop 2: 旧金山 + YC总裁 → Sam Altman
3. "developed technology that gained 100 million users in record time"
   → Hop 3: Sam Altman创立 + 1亿用户记录 → OpenAI

最终问题:
"What company was founded in the city home to the Golden Gate Bridge by someone 
who previously led a prominent startup accelerator, and developed technology that 
gained 100 million users in record time?"
```

**方案3 - 时间序列链（3-hop）**:
```
约束设计:
1. "started as a non-profit in the mid-2010s"
   → Hop 1: 2015年非营利AI组织
2. "transitioned to a capped-profit model"
   → Hop 2: 结构转变
3. "launched a product that broke user growth records in early 2023"
   → Hop 3: 2023年产品增长记录 → ChatGPT/OpenAI

最终问题:
"Please identify the entity that started as a non-profit in the mid-2010s, 
transitioned to a capped-profit model, and launched a product that broke 
user growth records in early 2023."
```

### 3. 问题模板

#### 模板1: "Please identify..."
```
Please identify the [类别] that/who [约束1], [约束2], [约束3], and [约束4].
```

示例:
```
Please identify the fictional character who breaks the fourth wall, has a humorous 
personality, appeared in a TV show during the 1970s, and has a backstory involving 
transformation.
```

#### 模板2: "What is..."
```
What is the [类别] that [约束1], [约束2], and is known for [约束3]?
```

示例:
```
What is the technology company that was founded by a serial entrepreneur in South Africa, 
operates in the space industry, and successfully landed reusable rockets?
```

#### 模板3: "Which [类别]..."
```
Which [类别] [约束1], [约束2], while also [约束3]?
```

示例:
```
Which quantum computing concept describes particles in multiple states simultaneously, 
was proposed in the early 20th century, and is often illustrated using a famous thought 
experiment involving a feline?
```

## 答案生成策略

### 答案要求

1. **简短**: 只写实体名称
2. **准确**: 与seed entity一致
3. **无解释**: 不添加任何额外信息

### 正确的答案格式

✅ **正确**:
```
"OpenAI"
"Elon Musk"
"Quantum Computing"
"Plastic Man"
"ChatGPT"
```

❌ **错误**（太详细）:
```
"OpenAI is an AI research company..."
"OpenAI (founded in 2015)"
"The answer is OpenAI"
```

## 质量控制

### 好的谜题式问答特征

1. **唯一性**: 约束条件组合应该指向唯一答案
2. **可验证性**: 所有线索都基于真实信息
3. **适度难度**: 不太简单也不过于困难
4. **多样性**: 使用不同维度的约束
5. **自然性**: 问题读起来流畅自然

### 质量检查清单

- [ ] 问题不直接包含答案实体名称？
- [ ] 包含3-5个独立的约束条件？
- [ ] 所有约束条件都是模糊化的（不是具体数字/名称）？
- [ ] 答案只是实体名称（无额外解释）？
- [ ] 约束条件基于轨迹中的真实信息？
- [ ] 约束条件组合能唯一确定答案？

### 常见问题和改进

#### 问题1: 问题太简单
```
❌ "What company makes ChatGPT?"
✅ "Please identify the AI research organization founded in the mid-2010s that released 
    a viral conversational AI tool in late 2022."
```

#### 问题2: 答案太详细
```
❌ "OpenAI is an AI research company founded in 2015..."
✅ "OpenAI"
```

#### 问题3: 约束条件太具体
```
❌ "founded on December 11, 2015"
✅ "founded in the mid-2010s"
```

#### 问题4: 直接提及答案
```
❌ "When was OpenAI founded?"
✅ "Please identify the organization that..."
```

## 示例集

### 示例1: 人物类

**实体**: Elon Musk

**问题**:
```
Please identify the entrepreneur who was born in South Africa, co-founded an online 
payment platform that became widely used in the late 1990s, leads multiple companies 
in the electric vehicle and space industries, and is known for his active presence on 
social media.
```

**答案**: `Elon Musk`

### 示例2: 概念类

**实体**: Quantum Computing

**问题**:
```
What is the computing paradigm that leverages principles from quantum mechanics, 
uses qubits instead of classical bits, promises exponential speedup for certain 
problems, and is currently being developed by major tech companies with systems 
reaching dozens of qubits?
```

**答案**: `Quantum Computing`

### 示例3: 产品类

**实体**: ChatGPT

**问题**:
```
Please identify the AI tool that was released in late 2022, reached over 100 million 
users in record time, is based on a large language model from the GPT family, and 
sparked widespread discussion about AI's impact on various industries.
```

**答案**: `ChatGPT`

### 示例4: 公司类

**实体**: SpaceX

**问题**:
```
Which aerospace company was founded in the early 2000s by a tech entrepreneur, 
successfully developed reusable rocket technology, has contracts with NASA, and 
aims to enable human settlement on Mars?
```

**答案**: `SpaceX`

## 实现要点

### Trajectory采样阶段

- 收集**多维度**的具体信息
- 关注**可量化**的数据（时间、地点、数量）
- 记录**关系信息**（人物、公司、产品）
- 获取**独特特征**（标志性元素、重要事件）

### QA合成阶段

- 分析轨迹中的所有信息
- 选择3-5个最具区分性的特征
- 将每个特征模糊化
- 组合成自然流畅的问题
- 确保答案简洁

## 参考资料

- 主实现代码: `web_agent.py` 的 `QASynthesizer.synthesize_qa()`
- Trajectory采样: `TrajectorySampler._generate_next_action()`
- 示例数据: `example_seed_entities.json`
- 主文档: `README.md`

