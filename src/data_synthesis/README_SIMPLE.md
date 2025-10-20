# 简化的Seed使用指南

## 🎯 核心理念

**极致简化**：Seed文件就是一个字符串列表，配置只需要 `seed_description` 来说明seed的含义。

---

## 📝 Seed文件格式

### 唯一格式：字符串列表

```json
[
  "seed1",
  "seed2",
  "seed3"
]
```

**就这么简单！** 不需要任何key，不需要复杂结构。

---

## ⚙️ 配置说明

### 最小配置

```json
{
  "environment_mode": "web",
  "available_tools": ["web_search", "web_visit"],
  "model_name": "gpt-4o-mini"
}
```

### 添加seed说明（推荐）

```json
{
  "environment_mode": "web",
  "available_tools": ["web_search", "web_visit"],
  "seed_description": "实体名称",
  "model_name": "gpt-4o-mini"
}
```

`seed_description` 的作用：
- 在prompt中告诉模型seed是什么
- 帮助模型更好地理解如何使用seed
- 完全可选，但推荐添加

---

## 💡 使用示例

### 示例1: Web搜索实体

**配置** (`config.json`):
```json
{
  "environment_mode": "web",
  "available_tools": ["web_search", "web_visit"],
  "seed_description": "公司或组织名称",
  "model_name": "gpt-4o-mini",
  "max_depth": 3
}
```

**Seeds** (`seeds.json`):
```json
[
  "OpenAI",
  "Google DeepMind",
  "Anthropic"
]
```

**运行**:
```bash
python synthesis_pipeline.py \
    --config config.json \
    --seeds seeds.json \
    --output-dir results
```

---

### 示例2: 数学问题

**配置**:
```json
{
  "environment_mode": "math",
  "available_tools": ["calculator"],
  "seed_description": "数学概念或主题",
  "model_name": "gpt-4o-mini",
  "max_depth": 4
}
```

**Seeds**:
```json
[
  "圆的面积",
  "二次方程",
  "质数",
  "三角形"
]
```

---

### 示例3: Python编程

**配置**:
```json
{
  "environment_mode": "python",
  "available_tools": ["python_interpreter"],
  "seed_description": "编程问题或算法",
  "model_name": "gpt-4o-mini"
}
```

**Seeds**:
```json
[
  "斐波那契数列",
  "快速排序",
  "素数筛选"
]
```

---

### 示例4: RAG检索

**配置**:
```json
{
  "environment_mode": "rag",
  "available_tools": ["local_search"],
  "seed_description": "需要在知识库中检索的主题",
  "environment_kwargs": {
    "rag_index": "path/to/index"
  },
  "model_name": "gpt-4o-mini"
}
```

**Seeds**:
```json
[
  "Transformer架构",
  "注意力机制",
  "BERT模型"
]
```

---

## 🚀 快速开始

### 1. 准备Seed文件

创建 `my_seeds.json`:
```json
[
  "你的seed1",
  "你的seed2",
  "你的seed3"
]
```

### 2. 选择或创建配置

使用预设配置：
```bash
./run_generic_synthesis.sh web
./run_generic_synthesis.sh math
./run_generic_synthesis.sh python
./run_generic_synthesis.sh rag
```

或创建自定义配置 `my_config.json`:
```json
{
  "environment_mode": "web",
  "available_tools": ["web_search", "web_visit"],
  "seed_description": "描述你的seed是什么",
  "model_name": "gpt-4o-mini",
  "max_depth": 3,
  "branching_factor": 2
}
```

### 3. 运行

```bash
python synthesis_pipeline.py \
    --config my_config.json \
    --seeds my_seeds.json \
    --output-dir results
```

---

## 📋 完整配置参数

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `environment_mode` | 环境类型 | `"web"`, `"math"`, `"python"`, `"rag"` |
| `available_tools` | 可用工具列表 | `["web_search", "web_visit"]` |
| `model_name` | 使用的模型 | `"gpt-4o-mini"` |

### 可选参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `seed_description` | Seed的描述 | `""` | `"实体名称"` |
| `synthesis_tips` | 探索策略提示 | `""` | `"重点关注..."` |
| `qa_examples` | QA示例 | `[]` | 见配置示例 |
| `max_depth` | 最大深度 | `5` | `3` |
| `branching_factor` | 分支因子 | `2` | `2` |
| `max_trajectories` | 最多轨迹数 | `5` | `3` |
| `min_depth` | 最小深度 | `2` | `2` |

---

## 🎨 Seed Description 示例

好的seed_description能帮助模型更好地理解和使用seed：

| 场景 | seed_description | 说明 |
|------|------------------|------|
| Web搜索 | `"公司或组织名称"` | 明确seed是什么类型的实体 |
| 数学 | `"数学概念或公式"` | 告诉模型从数学角度理解 |
| 编程 | `"编程问题或算法名称"` | 引导生成编程相关内容 |
| RAG | `"需要检索的主题或问题"` | 说明检索方向 |
| 通用 | `"探索起点"` | 保持灵活性 |

---

## ✅ 规则和约束

### 1. Seed文件格式

✅ **正确**:
```json
[
  "seed1",
  "seed2"
]
```

❌ **错误**:
```json
{
  "seeds": ["seed1", "seed2"]
}
```

❌ **错误**:
```json
["seed1", 123, true]  // 必须全是字符串
```

### 2. Seed内容

- ✅ 所有seed必须是字符串
- ✅ 可以是任何内容（实体名、问题、文本、URL等）
- ✅ 根据你的agent环境选择合适的seed内容
- ⚠️ Seed的含义通过`seed_description`在配置中说明

---

## 🔄 从旧版本迁移

### 变更1: Seed文件格式

**旧格式**（不再支持）:
```json
{
  "entities": ["seed1", "seed2"]
}
```

**新格式**:
```json
["seed1", "seed2"]
```

### 变更2: 配置文件

**删除的字段**:
- ❌ `seed_type` - 不再需要

**保留的字段**:
- ✅ `seed_description` - 用于描述seed

**迁移步骤**:
1. 从配置中删除 `seed_type` 字段
2. 确保 `seed_description` 清晰描述seed含义
3. 将seed文件改为简单的字符串列表

---

## 🎯 设计哲学

### 为什么这样设计？

1. **简单**: 不需要记住各种key名称
2. **灵活**: seed的含义由description说明，而不是类型约束
3. **通用**: 同一个seed列表可以用于不同的agent环境
4. **清晰**: seed就是数据，description就是解释

### 核心原则

```
Seed = 纯数据（字符串列表）
Description = 对数据的解释
Environment + Tools = 如何使用这些数据
```

---

## 📊 示例输出

运行后会生成：

```
synthesis_results/
├── synthesized_qa_web_20231019_143022.jsonl
├── trajectories_web_20231019_143022.json
└── statistics_web_20231019_143022.json
```

QA对格式：
```json
{
  "question": "问题",
  "answer": "答案",
  "reasoning_steps": [...],
  "metadata": {
    "seed_data": "OpenAI",
    "seed_description": "公司名称",
    "environment_mode": "web",
    ...
  }
}
```

---

## 💡 最佳实践

### 1. Seed内容

- 根据agent环境选择合适的seed
- Web环境: 实体名、URL、主题
- Math环境: 数学概念、公式主题
- Python环境: 算法名、编程问题
- RAG环境: 主题、问题、关键词

### 2. Seed Description

- 简短清晰
- 说明seed的性质和用途
- 不要太具体，保持灵活性

### 3. 数量

- 开始时用少量seed测试（2-3个）
- 确认效果后再增加数量
- 建议每批10-50个seed

---

## ❓ 常见问题

### Q: 如果不提供seed_description会怎样？

**A**: 也可以工作，但模型可能不太理解seed的含义。建议总是提供description。

### Q: 可以在seed列表中混合不同类型的内容吗？

**A**: 可以，但不推荐。最好一次运行使用同质的seed，用seed_description统一描述。

### Q: 如何决定seed_description的内容？

**A**: 问自己：这些seed是什么？用一句话描述它们的共同特征。

### Q: Seed可以是多行文本吗？

**A**: 可以，JSON字符串支持换行符。

```json
[
  "单行seed",
  "多行seed\n第二行\n第三行"
]
```

---

## 📚 相关文档

- `QUICKSTART.md` - 快速开始
- `configs/` - 预设配置示例
- 代码注释 - 详细实现说明

---

## 🎉 总结

**记住三点**:

1. **Seed文件** = 字符串列表 `["seed1", "seed2"]`
2. **配置中** = `seed_description` 描述seed含义
3. **就这么简单！** 🚀

