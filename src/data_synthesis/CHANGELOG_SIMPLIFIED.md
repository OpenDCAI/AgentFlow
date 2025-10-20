# 变更日志 - Seed处理简化

## 📅 2025-10-19 - 重大简化

### 🎯 目标

将seed处理简化到极致：
- ✅ Seed文件就是字符串列表
- ✅ 配置只需要 `seed_description`
- ✅ 删除 `seed_type` 概念

---

## 🔄 主要变更

### 1. Seed文件格式

#### 之前
```json
{
  "seeds": ["seed1", "seed2"],
  "entities": ["entity1", "entity2"],
  ...多种可能的key
}
```

#### 现在
```json
["seed1", "seed2", "seed3"]
```

**就这么简单！** 只支持字符串列表。

---

### 2. 配置文件变更

#### 删除的字段

```json
{
  "seed_type": "entity"  // ❌ 删除，不再需要
}
```

#### 保留的字段

```json
{
  "seed_description": "实体名称"  // ✅ 保留并简化
}
```

---

### 3. 代码变更

#### synthesis_config.py

```python
# ❌ 删除
seed_type: str = "entity"

# ✅ 简化
seed_description: str = ""  # 对seed的描述
```

#### synthesis_pipeline.py

```python
# ❌ 之前：复杂的seed文件解析
possible_keys = ["seeds", "entities", "problems", ...]
for key in possible_keys:
    if key in data:
        seeds = data[key]
        break

# ✅ 现在：直接读取列表
seeds = json.load(f)
if not isinstance(seeds, list):
    raise ValueError("必须是字符串列表")
```

#### trajectory_sampler.py

```python
# ❌ 之前：根据seed_type生成不同prompt
if seed_type == "entity":
    prompt = f"探索实体{seed_entity}..."
elif seed_type == "problem":
    prompt = f"解决问题{seed_entity}..."
...

# ✅ 现在：统一的prompt模板
prompt = f"""
【起点信息】
内容: {seed_data}
"""
if self.config.seed_description:
    prompt += f"说明: {self.config.seed_description}"
```

#### qa_synthesizer.py

```python
# ❌ 之前：metadata包含seed_type
metadata = {
    "seed_data": trajectory.seed_data,
    "seed_type": self.config.seed_type,
    ...
}

# ✅ 现在：metadata包含seed_description
metadata = {
    "seed_data": trajectory.seed_data,
    "seed_description": self.config.seed_description,
    ...
}
```

---

### 4. 配置文件更新

所有预设配置文件都已更新：

#### web_config.json
```json
{
  "seed_description": "实体名称（公司、人物、产品、事件等）"
  // 删除了 "seed_type": "entity"
}
```

#### math_config.json
```json
{
  "seed_description": "数学主题或概念（如几何图形、代数方程、数论等）"
  // 删除了 "seed_type": "problem"
}
```

#### python_config.json
```json
{
  "seed_description": "编程问题或算法主题"
  // 添加了 seed_description
}
```

#### rag_config.json
```json
{
  "seed_description": "文本、主题或概念，作为知识库检索的起点"
  // 删除了 "seed_type": "text"
}
```

---

### 5. 示例文件更新

所有示例seed文件都已简化：

#### example_seed_entities.json
```json
[
  "圣塔菲研究所",
  "神经形态计算",
  "OpenAI"
]
```

#### example_seed_problems.json
```json
[
  "计算圆形和正方形的面积关系",
  "二次方程求解",
  ...
]
```

#### example_seed_texts.json
```json
[
  "人工智能在医疗领域的应用",
  "区块链技术的工作原理",
  ...
]
```

---

## 📋 迁移检查清单

### 对于配置文件

- [ ] 删除 `seed_type` 字段
- [ ] 保留/添加 `seed_description` 字段
- [ ] 确保 `seed_description` 清晰描述seed含义

### 对于Seed文件

- [ ] 将格式改为简单的字符串列表 `["seed1", "seed2"]`
- [ ] 移除所有key（如 `"entities"`, `"seeds"` 等）
- [ ] 确保所有元素都是字符串

### 对于Python代码

- [ ] 更新调用 API 的代码（参数名依然是 `seeds`）
- [ ] 如果读取metadata，注意 `seed_type` 改为 `seed_description`

---

## ✅ 向后兼容性

### ❌ 不兼容的变更

1. **Seed文件格式**
   - 旧格式：`{"entities": [...]}` ❌ 不再支持
   - 新格式：`[...]` ✅ 唯一支持格式

2. **配置字段**
   - `seed_type` ❌ 不再识别
   - `seed_description` ✅ 必须使用（可选但推荐）

3. **Metadata字段**
   - `seed_type` ❌ 不再包含
   - `seed_description` ✅ 新增

### ✅ 兼容的部分

1. **命令行参数** - 保持不变
   ```bash
   python synthesis_pipeline.py --config xxx --seeds xxx
   ```

2. **配置文件其他字段** - 完全兼容

3. **输出格式** - 基本兼容（metadata略有变化）

---

## 💡 设计理由

### 为什么删除 seed_type？

1. **过度设计**: seed_type 创造了不必要的分类
2. **缺乏灵活性**: 强制分类限制了seed的使用方式
3. **维护负担**: 需要为每种type编写特定代码
4. **实际上不需要**: seed_description 就足够了

### 为什么只支持字符串列表？

1. **极简**: 不需要记住任何key名称
2. **直观**: 文件内容一目了然
3. **通用**: 适用于所有场景
4. **易于生成**: 程序生成seed文件更简单

### seed_description 的作用

1. **解释性**: 告诉模型seed是什么
2. **灵活性**: 同一份seed可以有不同解释
3. **可选性**: 不强制，但推荐使用
4. **动态性**: 可以随时调整描述

---

## 📊 影响范围

### 修改的文件

| 文件 | 变更内容 |
|------|---------|
| `synthesis_config.py` | 删除seed_type，简化seed_description |
| `synthesis_pipeline.py` | 简化seed文件读取逻辑 |
| `trajectory_sampler.py` | 简化prompt生成，删除seed_type相关代码 |
| `qa_synthesizer.py` | 更新metadata，简化prompt |
| `configs/*.json` | 删除seed_type，更新seed_description |
| `example_seed_*.json` | 改为简单列表格式 |

### 新增的文档

| 文件 | 说明 |
|------|------|
| `README_SIMPLE.md` | 简化后的使用指南 |
| `CHANGELOG_SIMPLIFIED.md` | 本变更日志 |

---

## 🚀 升级指南

### 步骤1: 更新配置文件

```bash
# 打开你的配置文件
vim my_config.json

# 删除这一行
- "seed_type": "entity",

# 确保有这一行（可选但推荐）
+ "seed_description": "你的seed描述",
```

### 步骤2: 更新Seed文件

```bash
# 旧格式
{
  "entities": ["seed1", "seed2"]
}

# 改为新格式
["seed1", "seed2"]
```

### 步骤3: 测试运行

```bash
python synthesis_pipeline.py \
    --config my_config.json \
    --seeds my_seeds.json \
    --output-dir test_results
```

### 步骤4: 验证输出

检查生成的QA对metadata是否包含 `seed_description`。

---

## 🎓 最佳实践

### 1. Seed文件组织

```
seeds/
├── web_seeds.json        # ["OpenAI", "Google", ...]
├── math_seeds.json       # ["圆的面积", "二次方程", ...]
└── programming_seeds.json # ["排序算法", "搜索算法", ...]
```

### 2. 配置文件组织

```
configs/
├── web_entities.json     # seed_description: "公司或组织"
├── web_topics.json       # seed_description: "技术主题"
├── math_concepts.json    # seed_description: "数学概念"
└── custom.json           # seed_description: "自定义描述"
```

### 3. Seed Description 编写

**好的例子** ✅:
- "公司名称"
- "数学概念"
- "编程问题"
- "需要检索的主题"

**不好的例子** ❌:
- "seed" （太笼统）
- "OpenAI公司的实体名称" （太具体）
- "类型为entity的实体" （冗余）

---

## 📚 参考资源

- **README_SIMPLE.md** - 详细使用指南
- **QUICKSTART.md** - 快速开始
- **configs/** - 预设配置示例
- **example_seed_*.json** - Seed文件示例

---

## 🐛 已知问题

目前没有已知问题。

---

## 📞 问题反馈

如果遇到问题：
1. 检查seed文件是否是纯字符串列表
2. 检查配置中是否删除了seed_type
3. 查看 README_SIMPLE.md 获取详细说明

---

**变更日期**: 2025-10-19  
**版本**: v2.0 - Simplified  
**影响**: 重大变更，需要手动迁移

