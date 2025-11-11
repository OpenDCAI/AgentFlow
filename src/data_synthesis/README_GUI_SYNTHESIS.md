# GUI Agent 数据合成指南

本文档介绍如何使用数据合成系统为GUI Agent（基于OSWorld环境）生成训练数据。

## 概述

GUI Agent数据合成通过以下三个步骤实现：

1. **Trajectory Sampling（轨迹采样）**: 从给定的任务描述出发，通过与GUI环境交互，探索不同的操作路径，构建操作轨迹树
2. **Trajectory Selection（轨迹选择）**: 从轨迹树中选择质量高、信息丰富的轨迹作为合成基础
3. **QA Synthesis（问答合成）**: 基于选中的轨迹，生成复杂的推理问答对

## 环境要求

### 硬件要求
- 支持虚拟机的系统（VMware、VirtualBox等）
- 足够的内存和存储空间运行VM
- 推荐：16GB+ RAM，50GB+ 可用磁盘空间

### 软件要求
- Python 3.8+
- VMware Workstation/Fusion 或 VirtualBox
- Ubuntu VM镜像（或其他支持的OS）
- 所需Python依赖（见requirements.txt）

### 配置文件

GUI Agent需要配置VM相关参数。参考配置文件：`configs/osworld_config.json`

**关键配置项说明：**

```json
{
  "environment_mode": "osworld",  // 环境模式：osworld 或 gui
  "environment_kwargs": {
    // === 必需参数 ===
    "path_to_vm": "/path/to/your/vm.vmx",  // VM镜像路径（必填）
    
    // === 可选参数（有默认值）===
    "provider_name": "vmware",              // VM提供商：vmware, virtualbox
    "action_space": "computer_13",          // 动作空间：computer_13 或 pyautogui
    "observation_type": "screenshot_a11y_tree",  // 观察类型
    "screen_width": 1920,                   // 屏幕宽度
    "screen_height": 1080,                  // 屏幕高度
    "headless": false,                      // 是否无头模式
    "client_password": "password",          // VM客户端密码
    "sleep_after_execution": 2.0            // 每次操作后的等待时间（秒）
  },
  
  // === 工具配置 ===
  "available_tools": [
    "mouse_move",           // 鼠标移动
    "mouse_click",          // 左键单击
    "mouse_right_click",    // 右键单击
    "mouse_double_click",   // 双击
    "mouse_button",         // 鼠标按下/释放
    "mouse_drag",           // 鼠标拖拽
    "scroll",               // 滚动
    "type",                 // 键盘输入
    "key_press",            // 按键
    "key_hold",             // 按住/释放键
    "hotkey",               // 组合键
    "control"               // 控制信号（WAIT, DONE, FAIL）
  ],
  
  // === QA示例（引导合成方向）===
  "qa_examples": [
    {
      "question": "示例问题描述...",
      "answer": "示例答案"
    }
  ],
  
  // === 采样和合成策略 ===
  "sampling_tips": "轨迹探索策略说明...",
  "synthesis_tips": "QA合成指南...",
  "seed_description": "GUI操作任务描述",
  
  // === 模型和采样参数 ===
  "model_name": "gpt-4.1-mini-2025-04-14",
  "max_depth": 8,              // 最大探索深度
  "branching_factor": 2,       // 分支因子
  "depth_threshold": 2,        // 深度阈值
  "max_trajectories": 3,       // 最大轨迹数
  "min_depth": 6,              // 最小深度
  "max_selected_traj": 3,      // 每次选择的轨迹数上限
  "max_retries": 3,            // 最大重试次数
  
  // === 并行处理配置 ===
  "max_workers": 1,            // 并行worker数量（OSWorld建议使用1，因为VM资源限制）
  "number_of_seed": 100        // 处理的seed数量限制
}
```

## 动作空间说明

### computer_13 (推荐)
结构化的桌面操作工具，包含13个具体的操作工具：
- **鼠标操作**：移动、单击、右键、双击、拖拽等
- **键盘操作**：输入、按键、组合键等
- **滚动操作**：页面滚动
- **控制信号**：WAIT（等待）、DONE（完成）、FAIL（失败）

**优势**：操作粒度细，易于分析和理解，适合数据合成

### pyautogui
Python脚本执行模式，直接执行pyautogui代码。

**优势**：灵活度高，可以执行复杂操作
**劣势**：需要生成Python代码，分析难度较大

## 快速开始

### 1. 准备VM环境

```bash
# 安装并配置VMware或VirtualBox
# 创建Ubuntu VM并记录路径
VM_PATH="/path/to/ubuntu.vmx"
```

### 2. 准备Seed数据

创建一个包含GUI任务描述的JSON文件（参考 `example_seed_gui_tasks.json`）：

```json
[
  "打开文本编辑器，创建一个新文档，输入标题和三段内容，然后保存到桌面",
  "在文件浏览器中找到Downloads文件夹，创建一个名为'新项目'的子文件夹",
  "打开系统设置，进入网络设置界面，检查当前WiFi连接状态"
]
```

### 3. 修改配置文件

编辑 `configs/osworld_config.json`，设置你的VM路径：

```json
{
  "environment_kwargs": {
    "path_to_vm": "/path/to/your/vm.vmx"
  }
}
```

### 4. 运行数据合成

**串行处理模式（推荐）：**

```bash
cd /home/a1/sdb/tzw/AgentFlow/src/data_synthesis

python synthesis_pipeline_multi.py \
  --config configs/osworld_config.json \
  --seeds example_seed_gui_tasks.json \
  --output-dir synthesis_results/gui
```

**或使用单文件模式（不支持并行）：**

```bash
python synthesis_pipeline.py \
  --config configs/osworld_config.json \
  --seeds example_seed_gui_tasks.json \
  --output-dir synthesis_results/gui
```

### 5. 查看结果

合成完成后，输出目录包含：

```
synthesis_results/gui/
├── synthesized_qa_osworld.jsonl       # 生成的QA对
├── trajectories_osworld.jsonl         # 选中的轨迹
└── (可选) 其他分析文件
```

**QA数据格式示例：**

```json
{
  "question": "在文本编辑器中打开第3个最近文件，在第2段插入表格，然后保存。需要多少次鼠标点击？",
  "answer": "7",
  "trajectory_id": "traj_0001",
  "source_id": "src_0001_a3b5c7d9",
  "qa_id": "qa_0001_0",
  "reasoning_steps": [
    {"step": 1, "action": "mouse_click", "reasoning": "点击文件菜单"},
    {"step": 2, "action": "mouse_click", "reasoning": "选择最近文件列表"},
    ...
  ],
  "metadata": {}
}
```

## 高级配置

### 观察类型 (observation_type)

- `"screenshot"`: 仅截图
- `"a11y_tree"`: 仅可访问性树
- `"screenshot_a11y_tree"`: 截图 + 可访问性树（推荐）
- `"som"`: Set-of-Mark标注模式

### 轨迹采样参数调优

```json
{
  "max_depth": 8,              // 增加以探索更深的操作序列
  "branching_factor": 2,       // 增加以探索更多分支（会增加计算量）
  "depth_threshold": 2,        // 超过此深度后减少分支
  "min_depth": 6,              // 过滤太浅的轨迹
  "max_selected_traj": 3       // 每个seed选择的轨迹数量
}
```

**调优建议：**
- 简单任务：`max_depth=5-6`, `branching_factor=2`
- 复杂任务：`max_depth=8-10`, `branching_factor=3`
- 资源受限：降低 `branching_factor` 和 `max_depth`

### 并行处理配置

**重要提示：** OSWorld环境由于VM资源限制，建议使用 `max_workers=1`（串行处理）。

如果你有多个独立的VM实例，可以尝试增加workers数量：

```json
{
  "max_workers": 2  // 谨慎使用，确保有足够的VM实例和资源
}
```

### 断点续传

系统自动支持断点续传。如果中途中断，重新运行相同命令会：
- 自动加载已处理的seed
- 跳过已完成的任务
- 继续处理剩余的seed

## 常见问题

### Q1: VM连接失败

**错误信息：** `Failed to initialize DesktopEnv`

**解决方案：**
1. 检查VM路径是否正确
2. 确认VM能正常启动
3. 检查provider_name是否匹配（vmware/virtualbox）
4. 确认VM网络配置正确

### Q2: 操作执行缓慢

**解决方案：**
1. 增加 `sleep_after_execution` 参数（默认2秒）
2. 降低 `max_depth` 和 `branching_factor`
3. 使用 `headless=true` 模式（如果支持）

### Q3: 生成的QA质量不高

**解决方案：**
1. 调整 `sampling_tips` 和 `synthesis_tips` 提示词
2. 提供更多高质量的 `qa_examples`
3. 增加 `max_depth` 探索更深的操作序列
4. 筛选并使用更具代表性的seed任务

### Q4: 内存不足

**解决方案：**
1. 减小VM分配的内存
2. 降低 `screen_width` 和 `screen_height`
3. 减少 `max_workers`（使用串行处理）
4. 限制 `number_of_seed` 批量处理

### Q5: 如何自定义工具集

编辑配置文件的 `available_tools` 列表，只保留需要的工具：

```json
{
  "available_tools": [
    "mouse_click",
    "type",
    "key_press",
    "control"
  ]
}
```

## 与run_osworld.py的区别

| 特性 | run_osworld.py | 数据合成 (synthesis_pipeline) |
|------|----------------|------------------------------|
| **目的** | 运行单个GUI任务 | 批量生成训练数据 |
| **输入** | 单个任务配置 | 任务描述列表（seeds） |
| **输出** | 任务执行结果、轨迹 | QA对 + 轨迹树 |
| **轨迹** | 单条线性轨迹 | 多条探索性轨迹树 |
| **并行** | 支持多任务并行 | 建议串行（VM限制） |
| **评估** | 内置任务评估 | 生成推理问答对 |

## 最佳实践

1. **Seed设计**
   - 任务描述应清晰、具体
   - 包含可执行的操作步骤
   - 避免过于简单或过于复杂的任务

2. **资源管理**
   - 使用串行处理（`max_workers=1`）
   - 监控VM性能和资源使用
   - 定期清理VM快照

3. **质量控制**
   - 定期检查生成的QA质量
   - 根据结果调整采样策略
   - 使用高质量的QA示例引导生成

4. **增量处理**
   - 利用断点续传功能
   - 分批处理大量seeds
   - 定期备份生成的数据

## 相关文件

- `synthesis_pipeline_multi.py` - 支持并行的主pipeline（推荐）
- `synthesis_pipeline.py` - 单线程版本的pipeline
- `trajectory_sampler.py` - 轨迹采样器
- `trajectory_selector.py` - 轨迹选择器
- `qa_synthesizer.py` - QA合成器
- `configs/osworld_config.json` - OSWorld配置模板
- `example_seed_gui_tasks.json` - 示例seed数据

## 技术架构

```
Seed (任务描述)
    ↓
[Trajectory Sampling]
  - 创建OSWorldEnvironment
  - 使用computer_13工具集
  - BFS探索操作空间
  - 构建轨迹树
    ↓
[Trajectory Selection]
  - 基于深度、多样性选择
  - 过滤低质量轨迹
    ↓
[QA Synthesis]
  - 基于轨迹生成推理问答
  - 混淆实体和操作
  - 创建多跳推理链
    ↓
QA对 + 完整轨迹
```

## 参考资源

- OSWorld论文：[OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972)
- AgentFlow文档：`../README.md`
- 数据合成框架：`README_DECOUPLING.md`

## 贡献与反馈

如有问题或建议，欢迎提Issue或Pull Request。

