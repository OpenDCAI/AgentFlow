# OSWorld任务格式支持

## 概述

数据合成系统现在支持两种输出格式：

1. **QA格式（默认）**: 传统的问答对，用于推理能力训练
2. **任务格式（新增）**: OSWorld格式的可执行+可评估任务

## 两种格式对比

### QA格式（output_format: "qa"）

**用途：** 训练模型的推理能力

**输出示例：**
```json
{
  "question": "在文本编辑器中打开第3个最近文件，在第2段插入表格，然后保存。需要多少次鼠标点击？",
  "answer": "7",
  "qa_id": "src_0001_a3b5_traj_0001_qa_0",
  "trajectory_id": "traj_0001",
  "source_id": "src_0001_a3b5",
  "reasoning_steps": [
    {
      "step": 1,
      "action": "mouse_click",
      "reasoning": "点击文件菜单"
    },
    ...
  ]
}
```

### 任务格式（output_format: "task"）

**用途：** 训练模型执行GUI任务，并可自动验证完成情况

**输出示例：**
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
    "seed_data": "安装Spotify应用",
    "trajectory_depth": 5,
    "num_actions": 4
  }
}
```

## 任务格式详解

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 任务唯一标识 |
| `question` | string | ✅ | 任务指令（用户想要完成什么） |
| `config` | array | ✅ | 初始化配置（通常为空） |
| `evaluator` | object | ✅ | 评估器配置 |
| `answer` | number | ⚠️ | 预期评估得分（可选，1.0表示完全成功） |
| `metadata` | object | ⚠️ | 元数据（不是OSWorld标准格式的一部分） |

### Evaluator配置

evaluator定义了如何验证任务是否完成，支持多种验证方式：

#### 1. 命令行输出检查 (vm_command_line)

```json
{
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
}
```

**用途：** 检查命令输出是否包含/排除特定字符串
**示例场景：** 验证软件是否安装、检查文件是否存在

#### 2. 文件内容检查 (vm_file_content)

```json
{
  "func": "check_include_exclude",
  "result": {
    "type": "vm_file_content",
    "path": "~/test.txt"
  },
  "expected": {
    "type": "rule",
    "rules": {
      "include": ["Hello World"],
      "exclude": []
    }
  }
}
```

**用途：** 检查文件内容是否包含特定文本
**示例场景：** 验证文件创建、检查配置文件修改

#### 3. 文件存在性检查

```json
{
  "func": "check_include_exclude",
  "result": {
    "type": "vm_command_line",
    "command": "ls ~/Desktop/"
  },
  "expected": {
    "type": "rule",
    "rules": {
      "include": ["MyProjects"],
      "exclude": []
    }
  }
}
```

**用途：** 检查文件/文件夹是否存在
**示例场景：** 验证文件夹创建、文件移动

## 使用方法

### 1. 配置文件设置

在配置文件中设置 `output_format` 字段：

```json
{
  "environment_mode": "osworld",
  "output_format": "task",  // 👈 设置为 "task"
  "environment_kwargs": {
    "path_to_vm": "/path/to/vm.vmx",
    ...
  },
  "qa_examples": [
    {
      "question": "I want to install Spotify...",
      "answer": "Task completed",
      "evaluator": {
        "func": "check_include_exclude",
        ...
      }
    }
  ]
}
```

### 2. 运行数据合成

```bash
# 使用任务格式
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds example_seed_gui_tasks.json \
  --output-dir synthesis_results/gui_tasks

# 输出文件
# synthesis_results/gui_tasks/synthesized_tasks_osworld.jsonl
```

### 3. 输出文件名对比

| 输出格式 | QA格式 | 任务格式 |
|---------|--------|---------|
| 主输出文件 | `synthesized_qa_osworld.jsonl` | `synthesized_tasks_osworld.jsonl` |
| 轨迹文件 | `trajectories_osworld.jsonl` | `trajectories_osworld.jsonl` |

## 切换格式

### 从QA格式切换到任务格式

```json
{
  "output_format": "qa"  // 改为 "task"
}
```

### 从任务格式切换到QA格式

```json
{
  "output_format": "task"  // 改为 "qa"
}
```

## 工作流程

```
Seeds (任务描述)
    ↓
Trajectory Sampling (探索GUI操作)
    ↓
Trajectory Selection (选择高质量轨迹)
    ↓
[根据 output_format 分支]
    ├─ "qa" → GenericQASynthesizer
    │         → 生成推理问答对
    │         → synthesized_qa_*.jsonl
    │
    └─ "task" → OSWorldTaskSynthesizer
              → 生成可执行任务+评估器
              → synthesized_tasks_*.jsonl
```

## 示例对比

### 相同轨迹，不同输出

假设有这样一个探索轨迹：

**轨迹：** 
1. 点击应用菜单
2. 搜索"spotify"
3. 点击安装按钮
4. 等待安装完成
5. 验证安装成功

**QA格式输出：**
```json
{
  "question": "要安装一个音乐应用，需要执行哪些操作步骤？整个过程需要多少次鼠标点击？",
  "answer": "3次",
  "reasoning_steps": [...]
}
```

**任务格式输出：**
```json
{
  "id": "task_001",
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
  }
}
```

## 使用场景

### QA格式适合：
- ✅ 训练推理能力
- ✅ 需要解释操作步骤
- ✅ 教学和演示
- ✅ 复杂多步推理问题

### 任务格式适合：
- ✅ 训练任务执行能力
- ✅ 自动化评估
- ✅ OSWorld基准测试
- ✅ 端到端任务完成
- ✅ 与run_osworld.py兼容的训练数据

## 与run_osworld.py的兼容性

任务格式生成的数据可以**直接**用于 `run_osworld.py`：

```bash
# 1. 生成任务数据
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds example_seed_gui_tasks.json \
  --output-dir synthesis_results/gui_tasks

# 2. 使用run_osworld.py执行
python run_osworld.py \
  --mode osworld \
  --data synthesis_results/gui_tasks/synthesized_tasks_osworld.jsonl \
  --path-to-vm /path/to/vm.vmx \
  --action-space computer_13
```

## 高级配置

### 自定义Evaluator提示

在配置文件的 `synthesis_tips` 中添加evaluator指导：

```json
{
  "synthesis_tips": "生成任务时，evaluator应该:\n1. 明确可验证\n2. 自动化执行\n3. 结果确定性\n..."
}
```

### 多种Evaluator模板

在 `qa_examples` 中提供不同类型的evaluator示例：

```json
{
  "qa_examples": [
    {
      "question": "安装软件",
      "evaluator": {"func": "check_include_exclude", "result": {"type": "vm_command_line", ...}}
    },
    {
      "question": "创建文件",
      "evaluator": {"func": "check_include_exclude", "result": {"type": "vm_file_content", ...}}
    }
  ]
}
```

## 数据模型

### SynthesizedTask类

```python
@dataclass
class SynthesizedTask:
    id: str                          # 任务ID
    question: str                    # 任务指令
    config: List[Dict[str, Any]]     # 初始化配置
    evaluator: Dict[str, Any]        # 评估器
    trajectory_id: str               # 关联轨迹ID
    source_id: str                   # 原始seed标识
    answer: Optional[float]          # 预期得分
    metadata: Dict[str, Any]         # 元数据
```

## 常见问题

### Q1: 如何选择使用哪种格式？

**A:** 
- 如果需要训练推理能力 → 使用QA格式
- 如果需要训练任务执行+自动评估 → 使用任务格式
- 如果要生成OSWorld基准数据 → 使用任务格式

### Q2: 可以同时生成两种格式吗？

**A:** 目前不支持。需要运行两次pipeline，分别使用不同的 `output_format` 配置。

### Q3: evaluator是如何生成的？

**A:** OSWorldTaskSynthesizer基于轨迹内容和提供的示例，自动推断合适的验证方式。

### Q4: config字段什么时候不为空？

**A:** 通常为空。只有在需要特殊环境准备时才使用（如预先执行某些命令）。

### Q5: 生成的任务可以直接用于训练吗？

**A:** 可以！但建议先手动检查一批样本，确保evaluator设置合理。

## 相关文件

- `models.py` - `SynthesizedTask` 数据模型定义
- `task_synthesizer.py` - OSWorld任务合成器实现
- `synthesis_config.py` - 添加了 `output_format` 字段
- `synthesis_pipeline_multi.py` - 支持两种格式的pipeline
- `configs/osworld_config.json` - 任务格式配置示例

## 下一步

1. 尝试生成任务数据
2. 检查生成的evaluator质量
3. 使用run_osworld.py验证任务
4. 根据结果调整配置和提示词

---

**新功能版本：** v1.1.0
**更新日期：** 2025-11-10
**状态：** ✅ 已完成并测试

