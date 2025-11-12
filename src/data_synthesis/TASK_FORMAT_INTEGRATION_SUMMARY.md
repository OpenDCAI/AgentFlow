# OSWorld任务格式集成总结

## 🎯 完成的工作

根据您提供的OSWorld任务数据示例，我们已成功实现对**任务格式**（带evaluator的可执行任务）的支持。

### 数据格式对比

**您提供的示例：**
```json
{
  "id": "demo-spotify-001",
  "question": "I want to install Spotify on my current system. Could you please help me?",
  "answer": 1,
  "config": [...],
  "evaluator": {
    "func": "check_include_exclude",
    "result": {"type": "vm_command_line", "command": "which spotify"},
    "expected": {"type": "rule", "rules": {"include": ["spotify"], "exclude": ["not found"]}}
  }
}
```

**现在系统可以生成：** ✅ 完全相同的格式！

## 📝 核心修改

### 1. 新增数据模型 (`models.py`)

```python
@dataclass
class SynthesizedTask:
    """合成的OSWorld格式任务（可执行+可评估）"""
    id: str                       # 任务ID
    question: str                 # 任务指令
    config: List[Dict[str, Any]]  # 初始化配置
    evaluator: Dict[str, Any]     # 评估器配置
    trajectory_id: str            # 关联的轨迹ID
    source_id: str               # 原始seed标识
    answer: Optional[float]      # 预期评估得分
    metadata: Dict[str, Any]     # 元数据
```

### 2. 新增任务合成器 (`task_synthesizer.py`)

**功能：** 基于GUI探索轨迹生成OSWorld格式的任务

**关键能力：**
- ✅ 分析轨迹提取关键操作
- ✅ 生成清晰的任务指令
- ✅ 自动推断evaluator类型
- ✅ 支持多种验证方式（命令行、文件内容、文件存在性）

### 3. 配置扩展 (`synthesis_config.py`)

新增 `output_format` 字段：

```python
output_format: str = "qa"  # "qa": 问答对, "task": OSWorld任务
```

### 4. Pipeline集成 (`synthesis_pipeline_multi.py`)

**支持双模式：**
- `output_format="qa"` → 使用 `GenericQASynthesizer` → 生成QA对
- `output_format="task"` → 使用 `OSWorldTaskSynthesizer` → 生成任务

**智能文件命名：**
- QA模式: `synthesized_qa_osworld.jsonl`
- 任务模式: `synthesized_tasks_osworld.jsonl`

### 5. 配置文件更新 (`configs/osworld_config.json`)

```json
{
  "environment_mode": "osworld",
  "output_format": "task",  // ← 新增字段
  "qa_examples": [
    {
      "question": "I want to install Spotify...",
      "evaluator": {...}  // ← 包含evaluator示例
    }
  ]
}
```

## 📚 新增文档

| 文档 | 内容 |
|------|------|
| `README_OSWORLD_TASK_FORMAT.md` | 任务格式完整指南（约300行） |
| `QUICKSTART_OSWORLD_TASK.md` | 快速开始（约200行） |
| `TASK_FORMAT_INTEGRATION_SUMMARY.md` | 本文档（总结） |

## 🚀 使用方法

### 快速开始

```bash
# 1. 设置配置文件
vim configs/osworld_config.json
# 修改: "output_format": "task"
# 修改: "path_to_vm": "/your/vm/path"

# 2. 运行数据合成
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds example_seed_gui_tasks.json \
  --output-dir synthesis_results/tasks

# 3. 查看生成的任务
cat synthesis_results/tasks/synthesized_tasks_osworld.jsonl | jq .

# 4. 使用run_osworld.py执行
python ../run_osworld.py \
  --mode osworld \
  --data synthesis_results/tasks/synthesized_tasks_osworld.jsonl \
  --path-to-vm /your/vm/path
```

### 输出示例

```json
{
  "id": "src_0001_a3b5_task_0",
  "question": "I want to install Spotify on my current system. Could you please help me?",
  "config": [],
  "evaluator": {
    "func": "check_include_exclude",
    "result": {
      "type": "vm_command_line",
      "command": "which spotify"
    },
    "expected": {
      "type": "rule",
      "rules": {
        "include": ["spotify"],
        "exclude": ["not found"]
      }
    }
  },
  "answer": 1.0,
  "metadata": {
    "seed_data": "安装Spotify",
    "trajectory_depth": 5,
    "num_actions": 4,
    "environment_mode": "osworld"
  }
}
```

## 🎭 两种格式对比

| 维度 | QA格式 | 任务格式 |
|------|--------|---------|
| **配置** | `"output_format": "qa"` | `"output_format": "task"` |
| **合成器** | GenericQASynthesizer | OSWorldTaskSynthesizer |
| **输出文件** | synthesized_qa_*.jsonl | synthesized_tasks_*.jsonl |
| **问题类型** | 推理问题 | 任务指令 |
| **答案类型** | 推理结果（字符串） | 评估得分（数字） |
| **包含evaluator** | ❌ | ✅ |
| **可自动评估** | ❌ | ✅ |
| **兼容run_osworld.py** | ❌ | ✅ |
| **用途** | 推理能力训练 | 任务执行+评估 |

## 🔧 Evaluator类型

系统支持自动生成以下类型的evaluator：

### 1. 命令行输出检查 (vm_command_line)

```json
{
  "func": "check_include_exclude",
  "result": {"type": "vm_command_line", "command": "which spotify"},
  "expected": {"type": "rule", "rules": {"include": ["spotify"], "exclude": []}}
}
```

**用途：** 软件安装验证、文件存在性检查

### 2. 文件内容检查 (vm_file_content)

```json
{
  "func": "check_include_exclude",
  "result": {"type": "vm_file_content", "path": "~/test.txt"},
  "expected": {"type": "rule", "rules": {"include": ["Hello World"], "exclude": []}}
}
```

**用途：** 文件内容验证、配置文件检查

### 3. 目录/文件列表检查

```json
{
  "func": "check_include_exclude",
  "result": {"type": "vm_command_line", "command": "ls ~/Desktop/"},
  "expected": {"type": "rule", "rules": {"include": ["MyProjects"], "exclude": []}}
}
```

**用途：** 文件夹创建验证、文件移动验证

## 📊 工作流程

```
Seeds (任务描述)
    ↓
配置: output_format = "task"
    ↓
GenericTrajectorySampler
    ├─ 使用computer_13工具
    ├─ 探索GUI操作序列
    └─ 构建轨迹树
    ↓
GenericTrajectorySelector
    └─ 选择高质量轨迹
    ↓
OSWorldTaskSynthesizer  ← 新增
    ├─ 分析操作序列
    ├─ 提取任务意图
    ├─ 生成任务指令
    └─ 推断evaluator
    ↓
synthesized_tasks_osworld.jsonl
    ├─ 完全兼容OSWorld格式
    ├─ 可直接用于run_osworld.py
    └─ 支持自动评估
```

## ✅ 关键特性

1. **完全兼容OSWorld格式** 
   - 生成的任务可直接用于run_osworld.py
   - 支持OSWorld的evaluator系统
   
2. **智能evaluator推断**
   - 根据轨迹自动选择验证方式
   - 支持多种验证类型
   
3. **双模式支持**
   - QA格式：推理能力训练
   - 任务格式：执行能力+自动评估
   
4. **向后兼容**
   - 不影响现有QA格式功能
   - 通过配置文件轻松切换

## 📁 文件清单

### 修改的文件（4个）

| 文件 | 修改内容 |
|------|---------|
| `models.py` | 添加 `SynthesizedTask` 类 |
| `synthesis_config.py` | 添加 `output_format` 字段 |
| `synthesis_pipeline_multi.py` | 支持双模式合成 |
| `configs/osworld_config.json` | 添加任务示例 |

### 新增的文件（3个）

| 文件 | 功能 |
|------|------|
| `task_synthesizer.py` | OSWorld任务合成器（约300行） |
| `README_OSWORLD_TASK_FORMAT.md` | 完整指南 |
| `QUICKSTART_OSWORLD_TASK.md` | 快速开始 |

## 🧪 测试验证

### 单元测试

```bash
# 测试配置加载
python -c "
from synthesis_config import SynthesisConfig
config = SynthesisConfig.from_json('configs/osworld_config.json')
print(f'Output format: {config.output_format}')
assert config.output_format == 'task'
print('✅ 配置加载正常')
"

# 测试数据模型
python -c "
from models import SynthesizedTask
task = SynthesizedTask(
    id='test-001',
    question='Test task',
    config=[],
    evaluator={'func': 'check_include_exclude'},
    trajectory_id='traj_001',
    source_id='src_001'
)
print(task.to_dict())
print('✅ 数据模型正常')
"
```

### 集成测试

```bash
# 测试完整流程（需要VM）
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds example_seed_gui_tasks.json \
  --output-dir test_output

# 验证输出格式
python -c "
import json
with open('test_output/synthesized_tasks_osworld.jsonl') as f:
    task = json.loads(f.readline())
    assert 'id' in task
    assert 'question' in task
    assert 'evaluator' in task
    assert 'func' in task['evaluator']
    print('✅ 输出格式正确')
"
```

## 🎓 使用场景

### 场景1: 生成OSWorld基准数据

```bash
# 准备大量seeds
# seeds: ["Install X", "Create Y", "Configure Z", ...]

python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds large_seed_list.json \
  --output-dir osworld_benchmark_data
  
# 输出可直接用于OSWorld评估
```

### 场景2: 训练GUI Agent

```bash
# 1. 生成训练数据
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds training_seeds.json \
  --output-dir training_data

# 2. 使用数据训练模型
# train_model.py --data training_data/synthesized_tasks_osworld.jsonl

# 3. 使用run_osworld.py评估
python ../run_osworld.py \
  --mode osworld \
  --data training_data/synthesized_tasks_osworld.jsonl \
  --model trained_model
```

### 场景3: 数据增强

```bash
# 从少量seed生成大量变体任务
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds small_seed_set.json \
  --output-dir augmented_data

# 通过增加 max_depth 和 branching_factor 获得更多变体
```

## 💡 最佳实践

1. **Evaluator设计**
   - 确保evaluator明确可验证
   - 使用确定性验证方式
   - 避免依赖时序的验证

2. **Seeds质量**
   - 提供清晰的任务描述
   - 覆盖不同类型的操作
   - 包含可验证的结果

3. **配置优化**
   - 在qa_examples中提供高质量的evaluator示例
   - 在synthesis_tips中明确evaluator要求
   - 适当调整max_depth以捕获完整操作序列

4. **质量控制**
   - 手动检查生成的evaluator
   - 使用run_osworld.py验证任务
   - 迭代改进配置

## 🐛 已知限制

1. **Evaluator推断限制**
   - 当前主要支持3种验证类型
   - 复杂验证逻辑需要手动调整

2. **Config字段**
   - 通常为空，特殊初始化需求需手动设置

3. **并行处理**
   - 建议使用max_workers=1（VM资源限制）

## 🔮 未来改进

- [ ] 支持更多evaluator类型
- [ ] 自动生成config初始化步骤
- [ ] 添加evaluator质量评分
- [ ] 支持多步骤验证链
- [ ] 添加任务难度评估

## 📞 获取帮助

- **快速开始**: `QUICKSTART_OSWORLD_TASK.md`
- **详细文档**: `README_OSWORLD_TASK_FORMAT.md`
- **完整指南**: `README_GUI_SYNTHESIS.md`
- **配置示例**: `configs/osworld_config.json`

## 🎉 总结

✅ **成功实现了OSWorld任务格式支持**

您提供的数据格式：
```json
{"id": "...", "question": "...", "config": [...], "evaluator": {...}}
```

现在系统可以生成 ✅ 完全相同的格式！

**核心价值：**
1. 生成可执行的GUI任务
2. 包含自动评估逻辑
3. 完全兼容run_osworld.py
4. 支持大规模数据生成

**开始使用：**
```bash
vim configs/osworld_config.json  # 设置 output_format="task"
python synthesis_pipeline_multi.py --config configs/osworld_config.json --seeds example_seed_gui_tasks.json
```

---

**更新时间：** 2025-11-10
**版本：** v1.1.0
**状态：** ✅ 已完成并测试

