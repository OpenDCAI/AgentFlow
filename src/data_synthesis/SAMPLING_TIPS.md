# Sampling Tips 功能说明

## 🎯 新增功能

在配置中新增了 `sampling_tips` 字段，用于在 **Trajectory采样阶段** 引导Agent的探索策略。

---

## 📋 两种Tips的区别

### 1. sampling_tips - Trajectory采样提示

**作用阶段**: 步骤1 - Trajectory Sampling  
**作用对象**: Agent在探索时的行为  
**目的**: 引导Agent如何使用工具，采用什么策略探索

**示例**:
```json
{
  "sampling_tips": "探索策略：\n- 先搜索基础信息，再深入细节\n- 关注实体之间的关系链\n- 每次搜索应基于前一步结果"
}
```

### 2. synthesis_tips - QA合成提示

**作用阶段**: 步骤3 - QA Synthesis  
**作用对象**: 基于trajectory生成问答对  
**目的**: 引导如何从trajectory中合成高质量的问答对

**示例**:
```json
{
  "synthesis_tips": "QA合成要点：\n- 生成需要multi-hop推理的问题\n- 问题应该模糊化具体信息"
}
```

---

## 🔄 数据流程

```
Seed → [Step 1] Trajectory Sampling (使用 sampling_tips)
      ↓
      Trajectory Tree
      ↓
      [Step 2] Trajectory Selection
      ↓
      Selected Trajectories
      ↓
      [Step 3] QA Synthesis (使用 synthesis_tips)
      ↓
      QA Pairs
```

---

## 📝 配置示例

### Web环境配置

```json
{
  "environment_mode": "web",
  "available_tools": ["web_search", "web_visit"],
  
  "sampling_tips": "探索策略：\n- 先搜索基础信息，再深入细节\n- 关注实体之间的关系链（创始人、合作伙伴、前身等）\n- 寻找时间线信息（成立时间、重要事件、发展历程）\n- 探索相关领域和竞争对手\n- 每次搜索应基于前一步结果，逐步深入",
  
  "synthesis_tips": "QA合成要点：\n- 生成需要multi-hop推理的问题\n- 通过中间实体建立连接（关系链推理）\n- 问题应该模糊化具体信息，需要多步探索才能得到答案\n- 优先基于探索到的关系链信息生成问题",
  
  "seed_description": "实体名称",
  "model_name": "gpt-4o-mini"
}
```

### Math环境配置

```json
{
  "environment_mode": "math",
  "available_tools": ["calculator"],
  
  "sampling_tips": "探索策略：\n- 从基本概念出发，逐步深入\n- 尝试不同的计算方法和公式\n- 验证中间结果的合理性\n- 探索相关的数学性质和定理\n- 建立不同概念之间的联系",
  
  "synthesis_tips": "QA合成要点：\n- 生成需要多步骤计算的问题\n- 每一步计算都依赖前一步的结果\n- 问题描述应该自然，避免直接给出公式\n- 可以包含单位转换、比例关系等中间步骤",
  
  "seed_description": "数学概念",
  "model_name": "gpt-4o-mini"
}
```

### Python环境配置

```json
{
  "environment_mode": "python",
  "available_tools": ["python_interpreter"],
  
  "sampling_tips": "探索策略：\n- 先实现基础功能，再组合复杂逻辑\n- 测试边界情况和特殊输入\n- 逐步验证每个中间步骤的结果\n- 探索不同的实现方法和优化\n- 将复杂问题分解为可管理的子问题",
  
  "synthesis_tips": "QA合成要点：\n- 生成需要多步骤编程的问题\n- 问题应该需要逐步分解和实现\n- 可以组合多个编程概念（循环、条件、函数等）\n- 每一步都是为了获取下一步所需的信息",
  
  "seed_description": "编程问题或算法",
  "model_name": "gpt-4o-mini"
}
```

### RAG环境配置

```json
{
  "environment_mode": "rag",
  "available_tools": ["local_search"],
  "environment_kwargs": {
    "rag_index": "path/to/index"
  },
  
  "sampling_tips": "探索策略：\n- 先检索概述性信息，再查找具体细节\n- 关注文档之间的关联和引用\n- 对比不同来源的信息\n- 探索相关概念和扩展主题\n- 每次检索应该有明确的意图，逐步逼近目标",
  
  "synthesis_tips": "QA合成要点：\n- 生成需要多次检索的问题\n- 需要综合多个文档片段的信息\n- 涉及比较、总结、归纳等高阶推理\n- 问题应该基于知识库的实际内容，而不是常识\n- 可以包含概念关联、因果推理、时间序列等复杂关系",
  
  "seed_description": "检索主题",
  "model_name": "gpt-4o-mini"
}
```

---

## 💡 如何编写好的Tips

### sampling_tips 编写要点

1. **明确探索策略**: 告诉Agent应该如何使用工具
2. **指导探索顺序**: 先做什么，后做什么
3. **强调关键点**: 重点关注哪些信息
4. **建议组合方式**: 如何结合前后步骤的信息

**好的例子** ✅:
```
- 先搜索基础信息，再深入细节
- 关注实体之间的关系链
- 每次搜索应基于前一步结果
```

**不好的例子** ❌:
```
- 搜索信息（太笼统）
- 做好探索（没有指导意义）
```

### synthesis_tips 编写要点

1. **明确问题类型**: 生成什么样的问题
2. **指导问题难度**: 需要多少步推理
3. **强调信息来源**: 问题应基于什么信息
4. **建议问题风格**: 如何表达问题

**好的例子** ✅:
```
- 生成需要multi-hop推理的问题
- 问题应该模糊化具体信息
- 基于探索到的关系链信息生成问题
```

**不好的例子** ❌:
```
- 生成好问题（没有具体指导）
- 问题要难（太主观）
```

---

## 🎨 Prompt中的呈现

### Trajectory Sampling阶段的Prompt

```
你是一个智能Agent，正在使用可用工具进行探索和推理。

【起点信息】
内容: OpenAI
说明: 实体名称

【探索目标】
根据起点内容和可用工具，进行系统性探索，收集和推理出有价值的信息。

【探索策略和重点】
- 先搜索基础信息，再深入细节
- 关注实体之间的关系链（创始人、合作伙伴、前身等）
- 寻找时间线信息（成立时间、重要事件、发展历程）
- 探索相关领域和竞争对手
- 每次搜索应基于前一步结果，逐步深入

当前历史轨迹:
...

可用工具:
...
```

### QA Synthesis阶段的Prompt

```
你是一个数据合成专家。基于以下Agent的探索轨迹，合成一个高质量的问答对。

【起点信息】
内容: OpenAI
说明: 实体名称

【完整探索轨迹】
...

数据合成指导:
- 生成需要multi-hop推理的问题
- 通过中间实体建立连接（关系链推理）
- 问题应该模糊化具体信息，需要多步探索才能得到答案
- 优先基于探索到的关系链信息生成问题

请基于轨迹合成一个问答对:
...
```

---

## 🔧 配置字段总结

| 字段 | 作用阶段 | 必需 | 说明 |
|------|---------|------|------|
| `seed_description` | 全局 | 推荐 | 描述seed的含义 |
| `sampling_tips` | Step 1 | 可选 | 引导trajectory采样策略 |
| `synthesis_tips` | Step 3 | 可选 | 引导QA合成方向 |
| `qa_examples` | Step 3 | 可选 | 提供QA示例 |

---

## ✅ 最佳实践

### 1. 两个Tips应该配合使用

`sampling_tips` 引导Agent探索特定方向的信息，`synthesis_tips` 则基于这些信息生成相应类型的问题。

**示例**:
```json
{
  "sampling_tips": "关注实体之间的关系链",
  "synthesis_tips": "生成multi-hop推理问题"
}
```

### 2. 根据环境定制Tips

不同环境的探索方式和目标不同，Tips应该针对性地设计。

- **Web**: 关注搜索策略、信息关联
- **Math**: 关注计算步骤、公式应用
- **Python**: 关注代码实现、测试验证
- **RAG**: 关注检索策略、信息整合

### 3. Tips应该具体可执行

避免空泛的指导，给出具体可操作的建议。

### 4. 可以逐步优化Tips

根据生成的trajectory和QA质量，不断调整和优化tips内容。

---

## 📊 效果对比

### 无Tips

**Trajectory**: 随机探索，没有明确方向  
**QA**: 问题简单，缺乏深度

### 有sampling_tips但无synthesis_tips

**Trajectory**: 探索有方向性，收集到关键信息  
**QA**: 可能无法充分利用收集的信息

### 有synthesis_tips但无sampling_tips

**Trajectory**: 探索可能遗漏关键信息  
**QA**: 想生成复杂问题但缺乏必要信息支撑

### 两者都有

**Trajectory**: 目标明确，信息完整  
**QA**: 充分利用trajectory，生成高质量问答

---

## 🎯 使用建议

1. **起步阶段**: 使用预设配置中的tips
2. **调整阶段**: 根据输出质量微调tips
3. **生产阶段**: 为不同场景准备专门的tips配置

---

## 📝 修改记录

- **2025-10-19**: 新增 `sampling_tips` 配置项
- 更新了所有预设配置文件
- 在trajectory_sampler.py中集成sampling_tips到prompt

---

## 📚 相关文档

- **README_SIMPLE.md** - 基础使用指南
- **配置文件** - `configs/` 目录中的示例
- **synthesis_config.py** - 配置类定义

