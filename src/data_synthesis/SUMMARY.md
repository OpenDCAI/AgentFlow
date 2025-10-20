# 项目总结

## ✨ 最新状态（2025-10-19）

### 🎯 核心特性：极致简化

**Seed处理**：最简单的方式
```json
["seed1", "seed2", "seed3"]
```

**配置说明**：一个字段搞定
```json
{
  "seed_description": "描述你的seed是什么"
}
```

---

## 📁 项目结构

```
data_synthesis/
├── 核心代码 (模块化)
│   ├── models.py                    # 数据模型
│   ├── trajectory_sampler.py        # 轨迹采样
│   ├── trajectory_selector.py       # 轨迹选择
│   ├── qa_synthesizer.py           # QA合成
│   ├── synthesis_pipeline.py        # 主流程
│   └── synthesis_config.py          # 配置管理
│
├── 配置文件
│   └── configs/
│       ├── web_config.json         # Web环境
│       ├── math_config.json        # Math环境
│       ├── python_config.json      # Python环境
│       └── rag_config.json         # RAG环境
│
├── Seed示例
│   ├── example_seed_entities.json
│   ├── example_seed_problems.json
│   ├── example_seed_texts.json
│   └── example_seeds.json
│
├── 运行脚本
│   └── run_generic_synthesis.sh    # 快速运行脚本
│
└── 文档
    ├── README_SIMPLE.md            # ⭐ 简化使用指南
    ├── QUICKSTART.md               # 快速开始
    ├── CHANGELOG_SIMPLIFIED.md     # 简化变更日志
    ├── CHANGES.md                  # 完整变更历史
    ├── README_DECOUPLING.md        # 解耦设计说明
    └── SUMMARY.md                  # 本文档
```

---

## 🚀 快速使用

### 方式1: 使用脚本（最简单）

```bash
cd /home/a1/work/AgentFlow/src/data_synthesis

# Web环境
./run_generic_synthesis.sh web

# Math环境  
./run_generic_synthesis.sh math

# Python环境
./run_generic_synthesis.sh python

# RAG环境
./run_generic_synthesis.sh rag
```

### 方式2: 自定义运行

1. **创建seed文件** `seeds.json`:
```json
[
  "OpenAI",
  "Google DeepMind",
  "Anthropic"
]
```

2. **选择配置** 或创建 `config.json`:
```json
{
  "environment_mode": "web",
  "available_tools": ["web_search", "web_visit"],
  "seed_description": "AI公司名称",
  "model_name": "gpt-4o-mini",
  "max_depth": 3
}
```

3. **运行**:
```bash
python synthesis_pipeline.py \
    --config config.json \
    --seeds seeds.json \
    --output-dir results
```

---

## 📚 核心概念

### 1. Seed（种子）

**定义**: 探索的起点，可以是任何字符串

**格式**: 简单的JSON字符串列表
```json
["起点1", "起点2", "起点3"]
```

**用途**: 
- Web环境: 实体名、URL、主题
- Math环境: 数学概念、问题
- Python环境: 算法名、编程问题
- RAG环境: 检索主题、关键词

### 2. Seed Description（种子描述）

**定义**: 在配置中说明seed的含义

**示例**:
- `"公司名称"`
- `"数学概念"`
- `"编程问题"`
- `"检索主题"`

**作用**: 帮助模型理解如何使用seed

### 3. Environment（环境）

**定义**: Agent使用的工具集合

**类型**:
- `web`: 网络搜索工具
- `math`: 计算器工具
- `python`: Python解释器
- `rag`: 本地检索工具

### 4. Trajectory（轨迹）

**定义**: Agent从seed出发，使用工具探索的完整路径

**包含**:
- 每一步的动作（使用什么工具）
- 每一步的观察（工具返回什么）
- 每一步的意图（为什么这样做）

### 5. QA Pair（问答对）

**定义**: 基于trajectory合成的问题和答案

**包含**:
- 问题：需要多步推理的复杂问题
- 答案：基于trajectory得出的答案
- 推理步骤：从问题到答案的过程

---

## 🔑 关键设计

### 1. 模块化架构

- **models.py**: 数据结构定义
- **trajectory_sampler.py**: 生成探索轨迹
- **trajectory_selector.py**: 选择高质量轨迹
- **qa_synthesizer.py**: 生成问答对
- **synthesis_pipeline.py**: 协调整个流程

### 2. 配置驱动

所有行为通过配置文件控制：
- 使用什么环境和工具
- Seed如何被理解
- 探索的深度和广度
- 合成的策略和风格

### 3. 极简Seed

- 只支持字符串列表
- 通过description说明含义
- 不需要复杂的类型系统

---

## 📊 数据流程

```
1. 读取Seeds
   ["seed1", "seed2", ...]
   ↓

2. 对每个Seed采样Trajectory
   Seed → [工具调用1 → 观察1 → 工具调用2 → 观察2 → ...]
   ↓

3. 选择高质量Trajectory
   评分 → 排序 → 选择Top-K
   ↓

4. 合成QA对
   Trajectory → 问题 + 答案 + 推理步骤
   ↓

5. 保存结果
   - synthesized_qa_*.jsonl
   - trajectories_*.json
   - statistics_*.json
```

---

## 💡 使用场景

### 场景1: Multi-hop推理数据生成

**目标**: 生成需要多步推理的问答对

**配置**:
```json
{
  "environment_mode": "web",
  "seed_description": "实体名称",
  "max_depth": 5,
  "synthesis_tips": "重点关注multi-hop推理..."
}
```

**Seeds**: `["OpenAI", "Tesla", "SpaceX"]`

### 场景2: 数学问题生成

**目标**: 生成多步骤数学问题

**配置**:
```json
{
  "environment_mode": "math",
  "seed_description": "数学概念",
  "max_depth": 4
}
```

**Seeds**: `["圆的面积", "二次方程", "三角函数"]`

### 场景3: 代码推理数据

**目标**: 生成编程相关的推理问题

**配置**:
```json
{
  "environment_mode": "python",
  "seed_description": "算法主题",
  "max_depth": 4
}
```

**Seeds**: `["快速排序", "动态规划", "图遍历"]`

### 场景4: 知识库问答

**目标**: 基于私有知识库生成问答

**配置**:
```json
{
  "environment_mode": "rag",
  "seed_description": "检索主题",
  "environment_kwargs": {
    "rag_index": "path/to/index"
  }
}
```

**Seeds**: `["Transformer", "BERT", "GPT"]`

---

## 📈 优势

### 1. 极致简单
- Seed文件就是列表
- 配置只需要description
- 无需学习复杂概念

### 2. 高度灵活
- 任何环境配任何seed
- Description可以随意定义
- 完全自定义探索策略

### 3. 易于扩展
- 添加新环境：注册工具即可
- 添加新seed类型：更新description
- 自定义合成策略：修改tips

### 4. 生产就绪
- 模块化架构易维护
- 配置驱动易调整
- 完整文档易上手

---

## 🎓 学习路径

### 新手（5分钟）
1. 阅读 **README_SIMPLE.md**
2. 运行 `./run_generic_synthesis.sh web`
3. 查看输出结果

### 进阶（30分钟）
1. 修改配置文件
2. 创建自定义seed文件
3. 调整参数观察效果

### 高级（1小时）
1. 阅读代码理解实现
2. 自定义环境和工具
3. 调整合成策略

---

## 🔧 配置技巧

### 1. 控制探索深度

```json
{
  "max_depth": 3,           // 最大深度
  "branching_factor": 2,    // 每层分支数
  "depth_threshold": 2      // 深度阈值后减少分支
}
```

### 2. 控制输出质量

```json
{
  "min_depth": 2,          // 最小轨迹深度
  "max_trajectories": 5    // 选择多少条轨迹
}
```

### 3. 引导合成方向

```json
{
  "synthesis_tips": "重点关注...",
  "qa_examples": [
    {
      "question": "示例问题",
      "answer": "示例答案"
    }
  ]
}
```

---

## 🐛 故障排查

### 问题1: Seed文件格式错误

**错误**: `Seed文件格式错误：必须是字符串列表`

**解决**: 确保seed文件格式为 `["seed1", "seed2"]`

### 问题2: 配置文件错误

**错误**: `配置错误: ...`

**解决**: 检查必需字段（environment_mode, available_tools, model_name）

### 问题3: 生成结果少

**原因**: 深度不够或分支太少

**解决**: 增加 `max_depth` 和 `branching_factor`

---

## 📞 获取帮助

### 文档
- **README_SIMPLE.md** - 简化使用指南 ⭐
- **QUICKSTART.md** - 快速开始
- **CHANGELOG_SIMPLIFIED.md** - 变更日志

### 配置示例
- `configs/web_config.json`
- `configs/math_config.json`
- `configs/python_config.json`
- `configs/rag_config.json`

### Seed示例
- `example_seed_entities.json`
- `example_seed_problems.json`
- `example_seed_texts.json`

---

## ✅ 快速检查清单

开始使用前：
- [ ] 准备好seed文件（字符串列表）
- [ ] 选择或创建配置文件
- [ ] 设置环境变量（OPENAI_API_KEY等）
- [ ] 确认输出目录

运行中：
- [ ] 观察日志输出
- [ ] 检查生成的轨迹
- [ ] 验证QA对质量

完成后：
- [ ] 查看统计信息
- [ ] 分析生成数据
- [ ] 调整参数优化

---

## 🎉 项目亮点

1. **极简设计** - Seed就是列表，配置就是描述
2. **模块化** - 代码清晰，职责分明
3. **灵活配置** - 完全控制探索和合成策略
4. **生产就绪** - 完整的错误处理和日志
5. **文档齐全** - 从入门到进阶的完整文档

---

**版本**: v2.0 - Simplified  
**最后更新**: 2025-10-19  
**维护者**: AgentFlow Team

