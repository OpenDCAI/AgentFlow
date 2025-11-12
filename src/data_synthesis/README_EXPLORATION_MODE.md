# GUI探索式数据合成 - 使用指南

## 核心理念

**探索式流程** vs **目标导向流程**

### 目标导向（原有流程）

```
具体任务seed → 为完成任务采样轨迹 → 选择 → 生成QA/Task
例如："安装Spotify" → 执行安装步骤 → 生成任务
```

**问题：** 预设了任务目标，限制了探索空间

### 探索式（新流程）⭐

```
抽象探索方向 → 自由探索+发现 → 选择有价值轨迹 → 总结出任务/QA
例如："探索文本编辑器" → 发现各种功能 → 总结出多个任务
```

**优势：**
- ✅ 从探索中发现多样化的任务
- ✅ 不预设目标，探索空间更大
- ✅ 能发现意想不到的操作序列
- ✅ 保存丰富的探索过程

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│ 步骤1: 探索式Trajectory Sampling                             │
│                                                             │
│ 输入: 抽象探索方向（例如："探索文本编辑器"）                  │
│   ↓                                                         │
│ GUIExplorationSampler:                                     │
│ - 在VM中自由探索界面                                         │
│ - 发现功能、菜单、选项                                       │
│ - 避免重复（状态指纹去重）                                   │
│ - 保存完整observation（截图+a11y树）                        │
│   ↓                                                         │
│ 输出: 探索树（多分支，包含所有探索过程）                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤2: Trajectory Selection                                 │
│                                                             │
│ 从探索树中选择：                                             │
│ - 有价值的操作序列                                           │
│ - 深度足够的路径                                             │
│ - 包含有意义操作的轨迹                                       │
│   ↓                                                         │
│ 输出: 精选的探索轨迹列表                                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤3: 探索总结（发现+提炼）                                 │
│                                                             │
│ ExplorationSummarizer:                                     │
│ - 分析探索轨迹                                               │
│ - **发现**隐含的任务                                         │
│ - **提炼**出任务指令                                         │
│ - 生成对应的evaluator                                       │
│   ↓                                                         │
│ 输出: Task或QA数据                                          │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 准备探索方向Seeds

创建 `example_seed_exploration.json`：

```json
[
  "探索桌面环境的文件管理功能",
  "探索文本编辑器应用的各种功能和选项",
  "探索系统设置面板的配置项",
  "探索网络浏览器的界面和功能"
]
```

**关键：** Seeds应该是**抽象的探索方向**，而非具体任务！

### 2. 配置文件

使用专门的探索式配置：`configs/osworld_exploration_config.json`

**关键配置：**
```json
{
  "environment_mode": "osworld",
  "output_format": "task",  // 或 "qa"
  "max_depth": 8,            // 探索深度
  "branching_factor": 2,     // 每步分支数
  "sampling_tips": "强调探索和发现的提示词..."
}
```

### 3. 运行探索式合成

```bash
cd /home/a1/sdb/tzw/AgentFlow/src/data_synthesis

python exploration_pipeline.py \
  --config configs/osworld_exploration_config.json \
  --seeds example_seed_exploration.json \
  --output-dir exploration_results
```

### 4. 查看输出

```bash
# 生成的任务/QA
cat exploration_results/exploration_tasks.jsonl | jq .

# 探索树（完整的探索过程）
cat exploration_results/tree_explore_0001_*.json | jq .
```

## 输出文件

### 主输出文件

| 文件 | 内容 |
|------|------|
| `exploration_tasks.jsonl` | 从探索中总结出的任务（output_format="task"） |
| `exploration_qa.jsonl` | 从探索中总结出的QA（output_format="qa"） |

### 探索树文件

| 文件 | 内容 |
|------|------|
| `tree_explore_XXXX_XXXXXX.json` | 完整的探索树（每个seed一个） |

**探索树格式：**
```json
{
  "exploration_seed": "探索文本编辑器",
  "timestamp": "2025-11-10T...",
  "total_nodes": 25,
  "total_unique_states": 18,
  "action_statistics": {
    "mouse_click": 12,
    "type": 5,
    "key_press": 3
  },
  "tree_structure": {
    "root_id": "explore_d0_t0",
    "nodes": {
      "explore_d0_t0": {
        "node_id": "explore_d0_t0",
        "depth": 0,
        "parent_id": null,
        "children_ids": ["explore_d1_t1_b0", "explore_d1_t2_b1"],
        "intent": "开始探索: 探索文本编辑器",
        "action": null,
        "observation": "[Screenshot] + [Accessibility Tree]"
      },
      ...
    }
  }
}
```

## 与目标导向的对比

| 维度 | 目标导向 | 探索式 |
|------|---------|--------|
| **Seeds类型** | 具体任务 | 抽象方向 |
| **采样器** | GenericTrajectorySampler | GUIExplorationSampler |
| **采样目标** | 完成特定任务 | 自由探索发现 |
| **状态追踪** | 无 | 状态指纹去重 |
| **轨迹保存** | 简化版 | 完整版（截图+a11y树） |
| **合成器** | QASynthesizer/TaskSynthesizer | ExplorationSummarizer |
| **合成方式** | 基于轨迹生成 | 从探索中发现+总结 |
| **数据多样性** | 较低（局限于seed） | 较高（一次探索多个发现） |
| **配置文件** | osworld_config.json | osworld_exploration_config.json |
| **入口脚本** | synthesis_pipeline_multi.py | exploration_pipeline.py |

## 核心组件

### 1. GUIExplorationSampler

**特点：**
- 探索导向：不预设任务目标
- 状态感知：记录访问过的状态，避免重复
- 丰富记录：每步保存截图和a11y树
- 价值发现：识别有价值的操作序列

**关键方法：**
```python
sample_exploration_tree(exploration_seed) 
  → 返回完整探索树

save_exploration_tree(output_path, exploration_seed)
  → 保存丰富的探索数据
```

**状态去重机制：**
```python
# 计算状态指纹（基于a11y树）
state_fingerprint = compute_state_fingerprint(observation)

# 检查是否访问过
if state_fingerprint in visited_states:
    skip  # 避免重复探索
```

### 2. ExplorationSummarizer

**特点：**
- 发现式：从探索中"发现"任务
- 提炼式：提炼出清晰的任务指令
- 智能evaluator：根据操作类型推断验证方式

**关键方法：**
```python
summarize_to_task(trajectory, task_index)
  → 从探索轨迹中总结出任务

summarize_to_qa(trajectory, qa_index)
  → 从探索轨迹中总结出QA
```

### 3. ExplorationDataSynthesis

**工作流程：**
1. 初始化OSWorld环境
2. 对每个exploration_seed:
   - 重置VM状态
   - 执行探索采样
   - 保存探索树
   - 选择有价值轨迹
   - 总结出任务/QA
3. 关闭环境

## 配置调优

### 探索深度控制

```json
{
  "max_depth": 8,           // 最大探索深度
  "branching_factor": 2,    // 每步分支数
  "depth_threshold": 5      // 超过此深度减少分支
}
```

**建议：**
- 简单应用：`max_depth=6`
- 复杂应用：`max_depth=8-10`
- 快速测试：`max_depth=4`

### 探索策略提示

在 `sampling_tips` 中强调：
```
1. 好奇心驱动 - 探索新功能
2. 新颖性优先 - 避免重复
3. 多样性探索 - 尝试不同操作
4. 价值发现 - 关注有用功能
```

### 总结策略提示

在 `synthesis_tips` 中强调：
```
1. 基于事实 - 不要添加轨迹外内容
2. 提炼价值 - 识别有意义的序列
3. 清晰表达 - 自然的任务指令
4. 可验证性 - 明确的evaluator
```

## 示例输出

### 探索方向
```
"探索文本编辑器应用的各种功能和选项"
```

### 探索过程（简化）
```
步骤1: 打开文本编辑器
步骤2: 点击"文件"菜单 → 发现：新建、打开、保存等选项
步骤3: 选择"新建" → 创建新文档
步骤4: 输入文本 → 可以编辑内容
步骤5: 点击"格式"菜单 → 发现：字体、大小等选项
步骤6: 点击"文件" → "保存" → 保存对话框
步骤7: 选择保存位置和文件名
步骤8: 确认保存
```

### 总结出的任务

**任务1：**
```json
{
  "id": "explore_0001_task_0",
  "question": "Please create a new text document, add some content, and save it to the Desktop",
  "evaluator": {
    "func": "check_include_exclude",
    "result": {"type": "vm_command_line", "command": "ls ~/Desktop/"},
    "expected": {"type": "rule", "rules": {"include": [".txt"], "exclude": []}}
  }
}
```

**任务2：**
```json
{
  "id": "explore_0001_task_1",
  "question": "Open the text editor and explore the Format menu to change text properties",
  "evaluator": {
    "func": "check_include_exclude",
    "result": {"type": "vm_command_line", "command": "ps aux | grep gedit"},
    "expected": {"type": "rule", "rules": {"include": ["gedit"], "exclude": []}}
  }
}
```

## 最佳实践

### 1. Seeds设计

✅ **好的探索方向：**
- "探索文件管理器的功能"
- "探索图片编辑工具的选项"
- "探索系统设置的各个面板"

❌ **不好的（太具体）：**
- "打开文件管理器并创建文件夹"
- "安装GIMP图片编辑器"
- "修改系统壁纸设置"

### 2. 避免无效探索

系统自动处理：
- 状态指纹去重（避免重复访问）
- 动作计数限制（避免重复操作）
- 深度控制（避免无限深入）

### 3. 探索树分析

查看探索统计：
```python
import json

with open('exploration_results/tree_explore_0001.json') as f:
    tree = json.load(f)
    
print(f"总节点数: {tree['total_nodes']}")
print(f"唯一状态数: {tree['total_unique_states']}")
print(f"动作统计: {tree['action_statistics']}")
```

### 4. 质量控制

检查生成的任务：
- 任务指令是否基于实际探索？
- Evaluator是否可验证？
- 任务是否有实用价值？

## 故障排除

### 问题1: 探索重复度高

**现象：** 大量节点访问相同状态

**解决：**
- 降低 `branching_factor`
- 增强 `sampling_tips` 中的新颖性提示
- 检查状态指纹计算是否有效

### 问题2: 探索深度不够

**现象：** 轨迹太浅，无法总结出有价值任务

**解决：**
- 增加 `max_depth`
- 增加 `depth_threshold`
- 在提示词中强调深入探索

### 问题3: 总结的任务质量差

**现象：** 生成的任务不基于轨迹

**解决：**
- 改进 `synthesis_tips`
- 提供更好的 `qa_examples`
- 增加轨迹的深度和丰富度

### 问题4: VM性能问题

**现象：** 探索速度很慢

**解决：**
- 减小 `screen_width/height`
- 增加 `sleep_after_execution`
- 使用更快的VM

## 性能考虑

- **单次探索时间：** 10-30分钟（取决于max_depth）
- **10个探索方向：** 2-5小时
- **推荐配置：** `max_workers=1`（VM限制）

## 下一步

1. ✅ 理解探索式流程
2. ✅ 准备探索方向seeds
3. ✅ 配置VM路径
4. ✅ 运行第一次探索
5. 📊 分析探索树
6. 📝 检查总结质量
7. 🔄 迭代改进配置

## 相关文件

- `exploration_sampler.py` - 探索式采样器
- `exploration_summarizer.py` - 探索总结器
- `exploration_pipeline.py` - 探索式pipeline
- `example_seed_exploration.json` - 探索方向示例
- `configs/osworld_exploration_config.json` - 探索式配置

---

**探索式流程版本：** v2.0.0
**更新日期：** 2025-11-10
**状态：** ✅ 已实现

