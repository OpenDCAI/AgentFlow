# 重要变更说明 - Seed和Agent解耦

## 🎯 核心改进

将 **Seed类型** 和 **Agent环境模式** 完全解耦，实现最大灵活性：

- **任何Agent环境** 都可以使用 **任何Seed类型**
- **配置驱动**: 所有行为通过配置文件控制
- **Prompt自动适配**: 根据配置动态生成prompt

---

## 📝 主要变更

### 1. 参数名称变更

#### 命令行参数
```bash
# ❌ 旧版本
--seed-entities entities.json

# ✅ 新版本
--seeds seeds.json  # 更通用，支持任意类型
```

#### Python API
```python
# ❌ 旧版本
def run(self, seed_entities: List[str]) -> List[SynthesizedQA]

# ✅ 新版本
def run(self, seeds: List[str]) -> List[SynthesizedQA]
```

### 2. 数据模型变更

```python
# ❌ 旧版本
@dataclass
class Trajectory:
    seed_entity: str
    ...

# ✅ 新版本
@dataclass
class Trajectory:
    seed_data: str  # 更通用的名称
    ...
```

### 3. Metadata变更

```python
# ❌ 旧版本
metadata = {
    "seed_entity": "OpenAI",
    "environment_mode": "web"
}

# ✅ 新版本
metadata = {
    "seed_data": "OpenAI",
    "seed_type": "entity",  # 新增
    "environment_mode": "web"
}
```

### 4. Seed文件格式增强

现在支持多种格式和键名：

```json
// 方式1: 直接列表
["seed1", "seed2"]

// 方式2: 通用键名
{"seeds": ["seed1", "seed2"]}

// 方式3: 兼容旧键名
{"entities": ["entity1", "entity2"]}
{"problems": ["problem1", "problem2"]}
{"texts": ["text1", "text2"]}
```

**支持的键名**: `seeds`, `entities`, `problems`, `texts`, `urls`, `data`, `items`

### 5. Prompt重构

#### Agent探索Prompt

```
# ❌ 旧版本：针对每个seed_type有不同的硬编码prompt
if seed_type == "entity":
    prompt = f"探索实体{seed_entity}..."
elif seed_type == "problem":
    prompt = f"解决问题{seed_entity}..."
...

# ✅ 新版本：统一的配置驱动prompt
prompt = f"""
【起点信息】
- 类型: {seed_type}
- 说明: {seed_description}
- 内容: {seed_data}

【探索目标】
根据起点类型和内容，使用可用工具进行系统性探索...
"""
```

#### QA合成Prompt

同样改为统一的配置驱动格式，不再区分不同seed类型。

---

## 🔄 迁移指南

### 无缝迁移（90%的情况）

如果你只是作为用户使用脚本：

```bash
# 旧的脚本调用 ✅ 依然有效
./run_generic_synthesis.sh web

# 配置文件 ✅ 无需修改
# Seed文件 ✅ 自动兼容
```

### 需要调整的情况

#### 1. 如果你在Python代码中调用API

```python
# ❌ 旧代码
seed_entities = ["OpenAI", "Google"]
qas = synthesizer.run(seed_entities)

# ✅ 新代码（变量名改为seeds）
seeds = ["OpenAI", "Google"]
qas = synthesizer.run(seeds)
```

#### 2. 如果你解析了metadata

```python
# ❌ 旧代码
seed = qa.metadata["seed_entity"]

# ✅ 新代码
seed = qa.metadata["seed_data"]
seed_type = qa.metadata["seed_type"]  # 新增字段
```

#### 3. 如果你自定义了Trajectory处理

```python
# ❌ 旧代码
print(trajectory.seed_entity)

# ✅ 新代码
print(trajectory.seed_data)
```

---

## ✨ 新功能

### 1. 灵活的Seed-Agent组合

现在你可以自由组合任何seed类型和agent环境：

```json
// Web Agent + Problem Seed
{
  "environment_mode": "web",
  "seed_type": "problem",
  "available_tools": ["web_search", "web_visit"]
}

// Math Agent + Entity Seed
{
  "environment_mode": "math",
  "seed_type": "entity",
  "available_tools": ["calculator"]
}

// RAG Agent + URL Seed
{
  "environment_mode": "rag",
  "seed_type": "url",
  "available_tools": ["local_search"]
}
```

### 2. 自定义Seed类型

```json
{
  "seed_type": "my_custom_type",
  "seed_description": "这是我自定义的seed类型，用于特定场景"
}
```

### 3. 更智能的Seed文件识别

系统会自动识别多种seed文件格式，无需严格指定键名。

---

## 📊 影响范围

### 文件变更

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `synthesis_pipeline.py` | 🔄 重构 | 参数和变量名更通用化 |
| `trajectory_sampler.py` | 🔄 重构 | Prompt统一化 |
| `trajectory_selector.py` | 🔄 重构 | 变量名更新 |
| `qa_synthesizer.py` | 🔄 重构 | Prompt统一化 |
| `models.py` | 🔄 重构 | `seed_entity` → `seed_data` |
| `run_generic_synthesis.sh` | 🔄 更新 | 参数名更新 |
| `QUICKSTART.md` | 📝 更新 | 文档更新 |
| `README_DECOUPLING.md` | ✨ 新增 | 详细说明文档 |
| `CHANGES.md` | ✨ 新增 | 本变更日志 |

### 兼容性

✅ **向后兼容**:
- 旧的配置文件格式完全兼容
- 旧的seed文件（包含"entities"等键）自动识别
- Shell脚本调用方式不变

⚠️ **需要注意**:
- Python API中的参数名从`seed_entities`改为`seeds`
- Metadata字段名变更
- Trajectory模型字段名变更

---

## 🎓 最佳实践

### 1. 命名建议

```bash
# ✅ 好的seed文件命名
seeds.json
entity_seeds.json
problem_seeds.json
custom_seeds.json

# ❌ 避免的命名（虽然仍能工作）
entities.json  # 太具体
data.json      # 太泛化
```

### 2. 配置组织

```
configs/
├── web_entity.json        # Web环境 + Entity seed
├── web_problem.json       # Web环境 + Problem seed
├── math_problem.json      # Math环境 + Problem seed
├── rag_text.json         # RAG环境 + Text seed
└── custom_combination.json  # 自定义组合
```

### 3. Seed文件组织

```
seeds/
├── entities/
│   ├── tech_companies.json
│   └── ai_researchers.json
├── problems/
│   ├── math_problems.json
│   └── coding_challenges.json
└── texts/
    ├── research_topics.json
    └── discussion_themes.json
```

---

## 🐛 已知问题

无已知问题。

---

## 📚 相关文档

- **README_DECOUPLING.md**: 详细的解耦设计说明和使用示例
- **QUICKSTART.md**: 快速开始指南
- **CODE_STRUCTURE.md**: (已删除) 代码结构说明

---

## 💡 常见问题

### Q: 为什么要做这个变更？

**A**: 原来的设计将seed类型和agent环境耦合在一起，限制了灵活性。新设计让任何agent都可以使用任何seed类型，极大提升了可扩展性。

### Q: 我的旧代码还能用吗？

**A**: 如果你只是通过shell脚本运行，完全没问题。如果在Python代码中调用API，需要简单修改变量名。

### Q: Seed文件需要重新格式化吗？

**A**: 不需要！旧的格式自动兼容。但推荐使用更通用的格式（直接列表或{"seeds": [...]}）。

### Q: 如何知道哪些seed-agent组合合理？

**A**: 这需要实验，但一般原则是：工具能力要匹配seed的探索需求。例如：
- Web工具 + URL seed → 合理
- Calculator + URL seed → 不太合理

### Q: 可以同时使用多种seed类型吗？

**A**: 一次运行使用一种seed_type。但你可以运行多次，每次使用不同配置。

---

## ✅ 升级检查清单

- [ ] 更新Python代码中的变量名 (`seed_entities` → `seeds`)
- [ ] 检查metadata访问代码 (`seed_entity` → `seed_data`)
- [ ] 测试现有配置文件是否正常工作
- [ ] 测试现有seed文件是否正常工作
- [ ] 阅读 README_DECOUPLING.md 了解新功能
- [ ] 尝试新的seed-agent组合

---

## 📞 获取帮助

如有疑问，请查看：
1. README_DECOUPLING.md - 详细说明和示例
2. QUICKSTART.md - 快速上手
3. 代码注释

---

**变更日期**: 2025-10-19
**影响版本**: v1.1.0+

