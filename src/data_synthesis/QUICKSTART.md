# 快速开始指南

## 🚀 快速运行

### 1. 使用Shell脚本 (最简单)

```bash
cd /home/a1/work/AgentFlow/src/data_synthesis

# Web环境 - 使用web_search和web_visit工具
./run_generic_synthesis.sh web

# Math环境 - 使用calculator工具
./run_generic_synthesis.sh math

# Python环境 - 使用python_interpreter工具
./run_generic_synthesis.sh python

# RAG环境 - 使用local_search工具（需要配置rag_index）
./run_generic_synthesis.sh rag

# 自定义配置
./run_generic_synthesis.sh custom configs/my_config.json
```

### 2. 使用Python命令行

```bash
python synthesis_pipeline.py \
    --config configs/web_config.json \
    --seeds example_seed_entities.json \
    --output-dir synthesis_results
```

### 3. 在Python代码中使用

```python
from data_synthesis import GenericDataSynthesis, SynthesisConfig

# 加载配置
config = SynthesisConfig.from_json("configs/web_config.json")

# 创建合成器
synthesizer = GenericDataSynthesis(config)

# 准备seed数据（内容根据配置的seed_type而定）
# 例如：entity类型用实体名，problem类型用问题描述，text类型用文本内容
seeds = ["OpenAI", "Claude AI", "Google DeepMind"]

# 运行合成
qas = synthesizer.run(seeds)

# 保存结果
synthesizer.save_results(output_dir="my_results")

print(f"生成了 {len(qas)} 个QA对")
```

---

## 📁 新的代码结构

```
data_synthesis/
├── models.py                    # 数据模型 (TrajectoryNode, Trajectory, SynthesizedQA)
├── trajectory_sampler.py        # 采样器 - 生成trajectory tree
├── trajectory_selector.py       # 选择器 - 选择高质量路径
├── qa_synthesizer.py           # 合成器 - 生成QA对
├── synthesis_pipeline.py        # 主入口 - 协调整个流程 ⭐
├── synthesis_config.py          # 配置管理
├── __init__.py                  # 包导出
└── run_generic_synthesis.sh     # 运行脚本 ⭐
```

---

## 🎯 主要改进

### 代码重构
- ✅ **1059行 → 6个模块化文件** (平均~200行/文件)
- ✅ **职责清晰**: 每个模块负责单一功能
- ✅ **易于维护**: 修改某个功能不影响其他模块
- ✅ **便于测试**: 每个模块可独立测试

### 使用方式
- ✅ **完全兼容**: 所有原有功能保持不变
- ✅ **更灵活**: 可以单独导入和使用某个组件
- ✅ **更易懂**: 代码结构一目了然

---

## 📦 导入示例

### 导入整个Pipeline
```python
from data_synthesis import GenericDataSynthesis, SynthesisConfig
```

### 导入单个组件
```python
from data_synthesis import (
    GenericTrajectorySampler,
    GenericTrajectorySelector,
    GenericQASynthesizer
)
```

### 导入数据模型
```python
from data_synthesis import TrajectoryNode, Trajectory, SynthesizedQA
```

---

## 🔧 配置文件示例

### Web环境配置 (configs/web_config.json)
```json
{
  "environment_mode": "web",
  "seed_type": "entity",
  "available_tools": ["web_search", "web_visit"],
  "max_depth": 3,
  "branching_factor": 2,
  "model_name": "gpt-4o-mini"
}
```

### Math环境配置 (configs/math_config.json)
```json
{
  "environment_mode": "math",
  "seed_type": "problem",
  "available_tools": ["calculator"],
  "max_depth": 5,
  "branching_factor": 2,
  "model_name": "gpt-4o-mini"
}
```

### RAG环境配置 (configs/rag_config.json)
```json
{
  "environment_mode": "rag",
  "seed_type": "text",
  "available_tools": ["local_search"],
  "environment_kwargs": {
    "rag_index": "path/to/your/rag/index"
  },
  "max_depth": 4,
  "branching_factor": 2,
  "model_name": "gpt-4.1-2025-04-14"
}
```
**注意**: 使用 RAG 环境前，需要在配置文件中设置正确的 `rag_index` 路径

---

## 📊 输出结果

运行后会在输出目录生成:

```
synthesis_results/
├── synthesized_qa_web_20231019_143022.jsonl    # QA对数据
├── trajectories_web_20231019_143022.json       # 轨迹数据
└── statistics_web_20231019_143022.json         # 统计信息
```

### QA对格式 (.jsonl)
```json
{
  "question": "问题内容",
  "answer": "答案内容",
  "trajectory_id": "traj_0",
  "reasoning_steps": [
    {
      "step": 1,
      "description": "步骤描述",
      "intent": "步骤意图",
      "action": "工具名称",
      "observation": "观察结果"
    }
  ],
  "metadata": {
    "seed_entity": "OpenAI",
    "trajectory_depth": 3,
    "synthesis_date": "2023-10-19T14:30:22",
    "environment_mode": "web"
  }
}
```

---

## 🛠️ 自定义使用

### 创建自定义配置

```python
from data_synthesis import SynthesisConfig

config = SynthesisConfig(
    # 环境配置
    environment_mode="web",
    seed_type="entity",
    
    # 工具配置
    available_tools=["web_search", "web_visit"],
    
    # 采样参数
    max_depth=4,
    branching_factor=2,
    depth_threshold=3,
    
    # 选择参数
    min_depth=2,
    max_trajectories=3,
    
    # 模型配置
    model_name="gpt-4o-mini",
    max_retries=3,
    
    # 自定义指导
    seed_description="实体名称",
    synthesis_tips="重点关注最新信息和关键事实",
    
    # QA示例
    qa_examples=[
        {
            "question": "示例问题",
            "answer": "示例答案"
        }
    ]
)
```

### 单独使用某个组件

```python
from data_synthesis import GenericTrajectorySampler, SynthesisConfig
from envs import WebEnvironment

# 创建环境
env = WebEnvironment(model_name="gpt-4o-mini")

# 创建配置
config = SynthesisConfig.from_json("configs/web_config.json")

# 只使用采样器
sampler = GenericTrajectorySampler(environment=env, config=config)
trajectory_tree = sampler.sample_trajectory_tree("OpenAI")

print(f"生成了 {len(trajectory_tree)} 个节点")
```

---

## 📚 更多文档

- **详细结构说明**: 查看 `CODE_STRUCTURE.md`
- **配置参数说明**: 查看 `synthesis_config.py` 中的注释
- **原始实现**: 查看 `generic_agent.py` (已弃用，仅供参考)

---

## ⚠️ 注意事项

1. **环境变量**: 确保设置 `OPENAI_API_KEY` 和 `OPENAI_API_URL`
2. **工具依赖**: Web环境需要 `SERPER_API_KEY`
3. **Python版本**: 推荐 Python 3.8+
4. **依赖安装**: 确保安装了所有必要的包 (openai, dataclasses等)

---

## 🐛 常见问题

### Q: 如何迁移现有代码？
**A**: 只需更新导入语句，其他代码保持不变:
```python
# 旧的
from generic_agent import GenericDataSynthesis

# 新的
from data_synthesis import GenericDataSynthesis
```

### Q: 原来的 generic_agent.py 还能用吗？
**A**: 可以，但不推荐。新结构更易维护和扩展。

### Q: 如何添加自定义工具？
**A**: 在Environment中注册工具后，在配置中的 `available_tools` 中指定即可。

### Q: 输出格式有变化吗？
**A**: 没有，输出格式完全保持不变，确保向后兼容。

---

## 🎓 学习路径

1. **入门**: 使用 `run_generic_synthesis.sh` 运行示例
2. **理解**: 阅读 `CODE_STRUCTURE.md` 了解架构
3. **实践**: 修改配置文件，尝试不同参数
4. **进阶**: 查看各模块源码，理解实现细节
5. **扩展**: 基于新结构添加自定义功能

---

## 📞 获取帮助

如有问题，欢迎：
1. 查看代码注释和文档
2. 参考示例配置文件
3. 查看 `CODE_STRUCTURE.md` 中的详细说明

