# OSWorld任务格式 - 快速开始

## 1分钟了解

OSWorld任务格式是一种**可执行+可评估**的GUI任务数据格式，包含：

- **question**: 用户想要完成什么（任务指令）
- **config**: 环境初始化步骤（通常为空）
- **evaluator**: 如何验证任务完成（自动化评估）

**示例：**
```json
{
  "id": "demo-spotify-001",
  "question": "I want to install Spotify on my current system. Could you please help me?",
  "config": [],
  "evaluator": {
    "func": "check_include_exclude",
    "result": {"type": "vm_command_line", "command": "which spotify"},
    "expected": {"type": "rule", "rules": {"include": ["spotify"], "exclude": ["not found"]}}
  }
}
```

## 快速开始

### 步骤1: 修改配置

编辑 `configs/osworld_config.json`，设置 `output_format` 为 `"task"`：

```json
{
  "environment_mode": "osworld",
  "output_format": "task",  // 👈 关键：设置为 "task"
  "environment_kwargs": {
    "path_to_vm": "/home/a1/sdb/zhy/GUIAgent/OSWorld/vmware_vm_data/Ubuntu0/Ubuntu.vmx"
  }
}
```

### 步骤2: 运行数据合成

```bash
cd /home/a1/sdb/tzw/AgentFlow/src/data_synthesis

# 方式1: 使用现有seeds
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds example_seed_gui_tasks.json \
  --output-dir synthesis_results/gui_tasks

# 方式2: 使用自定义seeds
python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds my_custom_tasks.json \
  --output-dir my_output
```

### 步骤3: 查看输出

```bash
# 生成的任务文件
cat synthesis_results/gui_tasks/synthesized_tasks_osworld.jsonl | jq .

# 每个任务包含：
# - id: 任务标识
# - question: 任务指令
# - config: 初始化配置
# - evaluator: 验证逻辑
```

### 步骤4: 使用任务数据

生成的任务可以直接用于 `run_osworld.py`：

```bash
python ../run_osworld.py \
  --mode osworld \
  --data synthesis_results/gui_tasks/synthesized_tasks_osworld.jsonl \
  --path-to-vm /home/a1/sdb/zhy/GUIAgent/OSWorld/vmware_vm_data/Ubuntu0/Ubuntu.vmx \
  --action-space computer_13
```

## 对比：QA格式 vs 任务格式

| 特性 | QA格式 | 任务格式 |
|------|--------|---------|
| **配置** | `"output_format": "qa"` | `"output_format": "task"` |
| **输出文件** | `synthesized_qa_*.jsonl` | `synthesized_tasks_*.jsonl` |
| **问题类型** | 推理问答 | 任务指令 |
| **答案类型** | 推理结果 | 评估得分 |
| **是否可执行** | ❌ | ✅ |
| **是否可评估** | ❌ | ✅ (自动) |
| **兼容run_osworld.py** | ❌ | ✅ |

## Evaluator类型速查

### 1. 命令行检查

```json
{
  "func": "check_include_exclude",
  "result": {"type": "vm_command_line", "command": "which spotify"},
  "expected": {"type": "rule", "rules": {"include": ["spotify"], "exclude": []}}
}
```
**用途：** 验证软件安装、文件存在

### 2. 文件内容检查

```json
{
  "func": "check_include_exclude",
  "result": {"type": "vm_file_content", "path": "~/test.txt"},
  "expected": {"type": "rule", "rules": {"include": ["Hello World"], "exclude": []}}
}
```
**用途：** 验证文件内容、配置修改

### 3. 目录检查

```json
{
  "func": "check_include_exclude",
  "result": {"type": "vm_command_line", "command": "ls ~/Desktop/"},
  "expected": {"type": "rule", "rules": {"include": ["MyProjects"], "exclude": []}}
}
```
**用途：** 验证文件夹创建、文件移动

## 完整配置示例

```json
{
  "environment_mode": "osworld",
  "output_format": "task",
  "environment_kwargs": {
    "path_to_vm": "/path/to/vm.vmx",
    "provider_name": "vmware",
    "action_space": "computer_13",
    "observation_type": "screenshot_a11y_tree"
  },
  "available_tools": [
    "mouse_click", "type", "key_press", "control"
  ],
  "qa_examples": [
    {
      "question": "Install Spotify",
      "answer": "Task completed",
      "evaluator": {
        "func": "check_include_exclude",
        "result": {"type": "vm_command_line", "command": "which spotify"},
        "expected": {"type": "rule", "rules": {"include": ["spotify"], "exclude": ["not found"]}}
      }
    }
  ],
  "max_depth": 6,
  "branching_factor": 2,
  "max_workers": 1,
  "number_of_seed": 10
}
```

## 自定义Seeds

创建 `my_tasks.json`：

```json
[
  "Install Google Chrome browser",
  "Create a text file named 'notes.txt' on Desktop with content 'Hello'",
  "Open system settings and check network status",
  "Take a screenshot and save it as 'screenshot.png'"
]
```

## 验证输出

检查生成的任务是否有效：

```python
import json

# 读取生成的任务
with open('synthesis_results/gui_tasks/synthesized_tasks_osworld.jsonl') as f:
    for line in f:
        task = json.loads(line)
        
        print(f"Task ID: {task['id']}")
        print(f"Question: {task['question']}")
        print(f"Evaluator Type: {task['evaluator']['func']}")
        print(f"Verification: {task['evaluator']['result']['type']}")
        print("-" * 50)
```

## 常见用例

### 用例1: 生成软件安装任务

**Seeds:**
```json
["Install VLC", "Install GIMP", "Install Firefox"]
```

**生成的任务包含：**
- 安装指令
- 验证软件是否安装的evaluator

### 用例2: 生成文件操作任务

**Seeds:**
```json
[
  "Create folder 'Projects' on Desktop",
  "Move 3 files from Downloads to Documents",
  "Rename file 'old.txt' to 'new.txt'"
]
```

**生成的任务包含：**
- 文件操作指令
- 验证文件/文件夹状态的evaluator

### 用例3: 生成配置任务

**Seeds:**
```json
[
  "Change wallpaper",
  "Enable dark mode",
  "Set default browser to Firefox"
]
```

**生成的任务包含：**
- 配置修改指令
- 验证配置状态的evaluator

## 工作流程图

```
Seeds (任务描述)
    ↓
配置: output_format="task"
    ↓
Trajectory Sampling
    ↓
Trajectory Selection
    ↓
OSWorldTaskSynthesizer
    ├─ 分析轨迹
    ├─ 提取关键操作
    ├─ 生成任务指令
    └─ 推断evaluator
    ↓
synthesized_tasks_osworld.jsonl
    ├─ id
    ├─ question
    ├─ config
    └─ evaluator
    ↓
可直接用于 run_osworld.py
```

## 性能提示

- **推荐配置：**
  - `max_depth`: 6-8
  - `branching_factor`: 2
  - `max_workers`: 1（VM限制）
  - `number_of_seed`: 10-100

- **处理时间：**
  - 单个seed: 5-15分钟
  - 10个seeds: 1-2小时
  - 100个seeds: 8-25小时

## 故障排除

### 问题1: 生成的evaluator不合理

**解决：**
- 在配置中添加更多高质量的 `qa_examples`
- 调整 `synthesis_tips` 提示词
- 检查轨迹质量（增加 `max_depth`）

### 问题2: 输出文件名错误

**检查：**
- 确认 `output_format` 设置为 `"task"`
- 文件应该是 `synthesized_tasks_*.jsonl`，不是 `synthesized_qa_*.jsonl`

### 问题3: 任务无法在run_osworld.py中执行

**检查：**
- evaluator格式是否正确
- VM路径配置是否一致
- 任务指令是否明确可执行

## 下一步

1. ✅ 修改配置文件
2. ✅ 运行数据合成
3. ✅ 检查生成的任务
4. ✅ 使用run_osworld.py验证
5. 📊 分析评估结果
6. 🔄 迭代改进配置

## 更多资源

- **详细文档**: `README_OSWORLD_TASK_FORMAT.md`
- **完整指南**: `README_GUI_SYNTHESIS.md`
- **配置文件**: `configs/osworld_config.json`
- **示例seeds**: `example_seed_gui_tasks.json`

---

**快速开始完成！** 🎉

现在你可以生成OSWorld格式的可执行任务数据了。

